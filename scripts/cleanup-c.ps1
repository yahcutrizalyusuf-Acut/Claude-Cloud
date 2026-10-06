#Requires -Version 5.1
<#
.SYNOPSIS
    Membersihkan ruang Local Disk C: tanpa mengganggu proses yang sedang berjalan.

.DESCRIPTION
    Tiga mode:
      Report  - hanya memindai dan melaporkan, tidak menghapus apa pun.
      Safe    - hanya membersihkan hal yang aman dijalankan kapan saja, termasuk
                saat sesi Claude Code / build / container sedang bekerja.
      Full    - termasuk Safe, ditambah operasi berat (DISM, cache Gradle,
                versi lama aplikasi Claude, compact WSL). Mode ini MENOLAK jalan
                kalau ada proses claude/node/java/wsl/docker yang aktif,
                kecuali dipaksa dengan -Force.

    Semua penghapusan lewat ShouldProcess, jadi -WhatIf bekerja untuk dry-run.

.PARAMETER Mode
    Report | Safe | Full. Default: Safe.

.PARAMETER Force
    Lewati pemeriksaan proses aktif pada mode Full. Gunakan dengan sadar.

.PARAMETER DisableHibernate
    Jalankan 'powercfg /h off'. Membebaskan ruang sebesar RAM, tetapi
    mematikan Fast Startup. Perlu hak Administrator.

.PARAMETER ResetBase
    Tambahkan /ResetBase pada DISM. Ruang lebih banyak, tetapi update Windows
    yang sudah terpasang tidak bisa di-uninstall lagi. Hanya pada mode Full.

.PARAMETER CompactWsl
    Shutdown WSL lalu compact file ext4.vhdx. Mematikan semua distro WSL dan
    container Docker. Hanya pada mode Full.

.PARAMETER TempOlderThanDays
    Hanya hapus isi folder temp yang lebih tua dari N hari, supaya file kerja
    proses yang sedang jalan tidak ikut terhapus. Default: 7.

.PARAMETER KeepVersions
    Berapa versi terbaru yang dipertahankan saat membersihkan folder
    ber-versi (aplikasi Claude, puppeteer, Gradle wrapper). Default: 1.

.EXAMPLE
    .\cleanup-c.ps1 -Mode Report
    Lihat dulu apa yang memakan tempat, tanpa menghapus apa pun.

.EXAMPLE
    .\cleanup-c.ps1 -Mode Safe
    Aman dijalankan sekarang juga, walau ada task Claude yang sedang bekerja.

.EXAMPLE
    .\cleanup-c.ps1 -Mode Full -WhatIf
    Lihat persis apa yang akan dihapus mode Full, tanpa benar-benar menghapus.

.EXAMPLE
    .\cleanup-c.ps1 -Mode Full -CompactWsl -ResetBase
    Pembersihan menyeluruh. Jalankan hanya saat tidak ada pekerjaan berjalan.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Report', 'Safe', 'Full')]
    [string]$Mode = 'Safe',

    [switch]$Force,
    [switch]$DisableHibernate,
    [switch]$ResetBase,
    [switch]$CompactWsl,

    [ValidateRange(0, 365)]
    [int]$TempOlderThanDays = 7,

    [ValidateRange(1, 10)]
    [int]$KeepVersions = 1
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

$script:Ledger    = New-Object System.Collections.ArrayList
$script:DryRun    = $false
$script:IsAdmin   = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
                    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Proses yang, kalau hidup, membuat operasi berat jadi berisiko.
$script:BlockingProcesses = @(
    'claude', 'node', 'java', 'gradle', 'kotlin-daemon', 'dart', 'flutter',
    'vmmem', 'vmmemWSL', 'wsl', 'wslhost',
    'com.docker.backend', 'Docker Desktop', 'dockerd', 'studio64', 'msbuild'
)

# ---------------------------------------------------------------- output ----

function Write-Head {
    param([string]$Text)
    Write-Host ''
    Write-Host "== $Text" -ForegroundColor Cyan
}

function Write-Ok   { param([string]$Text) Write-Host "   [ok]   $Text" -ForegroundColor Green }
function Write-Skip { param([string]$Text) Write-Host "   [--]   $Text" -ForegroundColor DarkGray }
function Write-Note { param([string]$Text) Write-Host "   [!]    $Text" -ForegroundColor Yellow }
function Write-Info { param([string]$Text) Write-Host "   [i]    $Text" -ForegroundColor Gray }

function Format-Size {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return ('{0:N2} GB' -f ($Bytes / 1GB)) }
    if ($Bytes -ge 1MB) { return ('{0:N0} MB' -f ($Bytes / 1MB)) }
    if ($Bytes -ge 1KB) { return ('{0:N0} KB' -f ($Bytes / 1KB)) }
    return "$Bytes B"
}

# ----------------------------------------------------------------- utils ----

function Get-FreeGB {
    $d = Get-PSDrive -Name C -ErrorAction SilentlyContinue
    if ($d) { return [math]::Round($d.Free / 1GB, 2) }
    return 0
}

function Get-PathSizeBytes {
    param([string]$Path)
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) { return [long]0 }
    try {
        $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if (-not $item.PSIsContainer) { return [long]$item.Length }
        $sum = (Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
        if ($null -eq $sum) { return [long]0 }
        return [long]$sum
    }
    catch { return [long]0 }
}

function Add-Ledger {
    param([string]$Label, [long]$Bytes)
    if ($Bytes -le 0) { return }
    [void]$script:Ledger.Add([pscustomobject]@{ Label = $Label; Bytes = $Bytes })
}

function Get-RunningBlockers {
    $found = @()
    foreach ($name in $script:BlockingProcesses) {
        $p = Get-Process -Name $name -ErrorAction SilentlyContinue
        if ($p) { $found += "$name ($($p.Count))" }
    }
    return $found
}

function Test-ProcessIdle {
    <# Benar kalau tidak ada satu pun proses dari daftar yang hidup. #>
    param([string[]]$Names)
    foreach ($name in $Names) {
        if (Get-Process -Name $name -ErrorAction SilentlyContinue) { return $false }
    }
    return $true
}

function Remove-Target {
    <#
        Menghapus path (atau isinya) sambil menghitung ruang yang dibebaskan.
        Menghormati -WhatIf lewat ShouldProcess.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [string[]]$Path,
        [switch]$ContentsOnly,
        [int]$OlderThanDays = 0
    )

    $targets = @()
    foreach ($p in @($Path)) {
        if (-not $p -or -not (Test-Path -LiteralPath $p)) { continue }
        if ($ContentsOnly) {
            $kids = @(Get-ChildItem -LiteralPath $p -Force -ErrorAction SilentlyContinue)
            if ($OlderThanDays -gt 0) {
                $cutoff = (Get-Date).AddDays(-$OlderThanDays)
                $kids = @($kids | Where-Object { $_.LastWriteTime -lt $cutoff })
            }
            $targets += @($kids | ForEach-Object { $_.FullName })
        }
        else {
            $targets += $p
        }
    }

    $targets = @($targets | Where-Object { $_ })
    if ($targets.Count -eq 0) { Write-Skip "$Label : tidak ada"; return }

    [long]$bytes = 0
    foreach ($t in $targets) { $bytes += Get-PathSizeBytes $t }
    if ($bytes -le 0) { Write-Skip "$Label : kosong"; return }

    $size = Format-Size $bytes
    if (-not $PSCmdlet.ShouldProcess("$Label - $size ($($targets.Count) item)", 'Hapus')) {
        Add-Ledger -Label "$Label (dry-run)" -Bytes $bytes
        return
    }

    $failed = 0
    foreach ($t in $targets) {
        try { Remove-Item -LiteralPath $t -Recurse -Force -ErrorAction Stop }
        catch { $failed++ }
    }

    [long]$left = 0
    foreach ($t in $targets) { $left += Get-PathSizeBytes $t }
    $actual = $bytes - $left
    Add-Ledger -Label $Label -Bytes $actual

    if ($failed -gt 0) {
        Write-Note "$Label : $(Format-Size $actual) dibebaskan, $failed item terkunci (dipakai proses lain)"
    }
    else {
        Write-Ok "$Label : $(Format-Size $actual) dibebaskan"
    }
}

function Remove-OldVersions {
    <#
        Menyisakan $KeepVersions entri terbaru dalam sebuah folder,
        sisanya dihapus. Dipakai untuk folder ber-versi.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Root,
        [string]$Filter = '*',
        [switch]$Files,
        [switch]$VersionSort
    )

    if (-not (Test-Path -LiteralPath $Root)) { Write-Skip "$Label : folder tidak ada"; return }

    $items = @(Get-ChildItem -LiteralPath $Root -Filter $Filter -Force -ErrorAction SilentlyContinue |
               Where-Object { if ($Files) { -not $_.PSIsContainer } else { $_.PSIsContainer } })

    if ($VersionSort) {
        # Urutkan berdasarkan nomor versi di nama (app-0.14.3, Claude-0.14.3-full.nupkg),
        # bukan tanggal file, supaya build yang terpasang tidak pernah ikut terhapus.
        $items = @($items | Sort-Object -Property @{
            Expression = {
                $m = [regex]::Match($_.Name, '(\d+(?:\.\d+){1,3})')
                if ($m.Success) {
                    try { [version]$m.Groups[1].Value } catch { [version]'0.0.0' }
                }
                else { [version]'0.0.0' }
            }
        }, LastWriteTime -Descending)
    }
    else {
        $items = @($items | Sort-Object LastWriteTime -Descending)
    }

    if ($items.Count -le $KeepVersions) {
        Write-Skip "$Label : hanya $($items.Count) entri, tidak ada yang lama"
        return
    }

    $stale = @($items | Select-Object -Skip $KeepVersions)
    $keep  = @($items | Select-Object -First $KeepVersions | ForEach-Object { $_.Name })
    Write-Info "$Label : mempertahankan $($keep -join ', ')"
    Remove-Target -Label $Label -Path @($stale | ForEach-Object { $_.FullName })
}

function Find-ClaudeDesktopRoot {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'AnthropicClaude'),
        (Join-Path $env:LOCALAPPDATA 'Claude'),
        (Join-Path $env:LOCALAPPDATA 'Programs\claude')
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c)) { return $c }
    }
    return $null
}

function Find-Vhdx {
    $roots = @(
        (Join-Path $env:LOCALAPPDATA 'Packages'),
        (Join-Path $env:LOCALAPPDATA 'wsl'),
        (Join-Path $env:LOCALAPPDATA 'Docker')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

    $found = @()
    foreach ($r in $roots) {
        $found += @(Get-ChildItem -LiteralPath $r -Filter '*.vhdx' -Recurse -Depth 4 -Force -ErrorAction SilentlyContinue)
    }
    return $found
}

# ------------------------------------------------------------- pemindaian ---

function Invoke-Report {
    Write-Head 'Pemakaian ruang di titik-titik panas'

    $spots = [ordered]@{
        'Aplikasi Claude (desktop)'   = Find-ClaudeDesktopRoot
        'Claude Code (data)'          = Join-Path $env:USERPROFILE '.claude'
        'Cache Gradle'                = Join-Path $env:USERPROFILE '.gradle'
        'Cache puppeteer'             = Join-Path $env:USERPROFILE '.cache\puppeteer'
        'Cache npm'                   = Join-Path $env:APPDATA 'npm-cache'
        'Cache pub (Dart/Flutter)'    = Join-Path $env:LOCALAPPDATA 'Pub\Cache'
        'Docker Desktop (data)'       = Join-Path $env:LOCALAPPDATA 'Docker'
        'Temp pengguna'               = $env:TEMP
        'Temp Windows'                = 'C:\Windows\Temp'
        'Windows Update (unduhan)'    = 'C:\Windows\SoftwareDistribution\Download'
        'Crash dump kernel'           = 'C:\Windows\LiveKernelReports'
        'Laporan error Windows'       = 'C:\ProgramData\Microsoft\Windows\WER'
        'Unduhan updater Edge'        = 'C:\Program Files (x86)\Microsoft\EdgeUpdate\Download'
        'Instalasi Windows lama'      = 'C:\Windows.old'
        'File hibernasi'              = 'C:\hiberfil.sys'
    }

    $rows = @()
    foreach ($k in $spots.Keys) {
        $path = $spots[$k]
        if (-not $path -or -not (Test-Path -LiteralPath $path)) { continue }
        $b = Get-PathSizeBytes $path
        if ($b -le 0) { continue }
        $rows += [pscustomobject]@{
            Lokasi = $k
            Ukuran = Format-Size $b
            Bytes  = $b
            Path   = $path
        }
    }

    $rows | Sort-Object Bytes -Descending |
        Format-Table Lokasi, Ukuran, Path -AutoSize | Out-Host

    $vhdx = Find-Vhdx
    if ($vhdx) {
        Write-Head 'Disk virtual WSL / Docker'
        $vhdx | Sort-Object Length -Descending | ForEach-Object {
            Write-Info ("{0,-10} {1}" -f (Format-Size $_.Length), $_.FullName)
        }
        Write-Note 'File vhdx tidak mengecil sendiri. Pakai -Mode Full -CompactWsl untuk memadatkannya.'
    }
}

# ------------------------------------------------------------- mode Safe ----

function Invoke-SafeCleanup {
    Write-Head 'Recycle Bin'
    try {
        if ($PSCmdlet.ShouldProcess('Recycle Bin', 'Kosongkan')) {
            Clear-RecycleBin -DriveLetter C -Force -ErrorAction Stop
            Write-Ok 'Recycle Bin dikosongkan'
        }
    }
    catch { Write-Skip 'Recycle Bin sudah kosong' }

    Write-Head "File temp lebih tua dari $TempOlderThanDays hari"
    Write-Info 'Batas usia melindungi file kerja proses yang sedang berjalan.'
    Remove-Target -Label 'Temp pengguna'  -Path $env:TEMP        -ContentsOnly -OlderThanDays $TempOlderThanDays
    Remove-Target -Label 'Temp Windows'   -Path 'C:\Windows\Temp' -ContentsOnly -OlderThanDays $TempOlderThanDays

    Write-Head 'Crash dump dan laporan error'
    Remove-Target -Label 'Crash dump aplikasi' -Path (Join-Path $env:LOCALAPPDATA 'CrashDumps') -ContentsOnly
    Remove-Target -Label 'WER ReportArchive'   -Path 'C:\ProgramData\Microsoft\Windows\WER\ReportArchive' -ContentsOnly
    Remove-Target -Label 'WER ReportQueue'     -Path 'C:\ProgramData\Microsoft\Windows\WER\ReportQueue'   -ContentsOnly
    if ($script:IsAdmin) {
        Remove-Target -Label 'LiveKernelReports' -Path 'C:\Windows\LiveKernelReports' -ContentsOnly
        Remove-Target -Label 'Minidump'          -Path 'C:\Windows\Minidump'          -ContentsOnly
        Remove-Target -Label 'MEMORY.DMP'        -Path 'C:\Windows\MEMORY.DMP'
    }
    else {
        Write-Skip 'Dump sistem dilewati (perlu Administrator)'
    }

    Write-Head 'Sisa unduhan updater'
    Remove-Target -Label 'EdgeUpdate Download'   -Path 'C:\Program Files (x86)\Microsoft\EdgeUpdate\Download' -ContentsOnly
    Remove-Target -Label 'Google Update Download' -Path 'C:\Program Files (x86)\Google\Update\Download'       -ContentsOnly

    Write-Head 'Cache Delivery Optimization'
    if (Get-Command Delete-DeliveryOptimizationCache -ErrorAction SilentlyContinue) {
        if ($PSCmdlet.ShouldProcess('Cache Delivery Optimization', 'Hapus')) {
            try {
                Delete-DeliveryOptimizationCache -Force -ErrorAction Stop
                Write-Ok 'Cache Delivery Optimization dihapus'
            }
            catch { Write-Note "Gagal: $($_.Exception.Message)" }
        }
    }
    else { Write-Skip 'Cmdlet Delivery Optimization tidak tersedia' }

    Write-Head 'Data lama Claude Code'
    $claudeData = Join-Path $env:USERPROFILE '.claude'
    # shell-snapshots murni artefak sesi; transkrip di projects/ TIDAK disentuh.
    Remove-Target -Label 'Claude Code shell-snapshots' -Path (Join-Path $claudeData 'shell-snapshots') -ContentsOnly -OlderThanDays 7

    if (Test-Path -LiteralPath 'C:\hiberfil.sys') {
        Write-Head 'File hibernasi'
        if ($DisableHibernate) {
            if (-not $script:IsAdmin) {
                Write-Note 'Perlu Administrator untuk mematikan hibernasi.'
            }
            elseif ($PSCmdlet.ShouldProcess('hiberfil.sys', 'Matikan hibernasi')) {
                $before = Get-PathSizeBytes 'C:\hiberfil.sys'
                & powercfg.exe /h off
                Add-Ledger -Label 'Hibernasi dimatikan' -Bytes $before
                Write-Ok "Hibernasi dimatikan, $(Format-Size $before) dibebaskan (Fast Startup ikut mati)"
            }
        }
        else {
            $sz = Format-Size (Get-PathSizeBytes 'C:\hiberfil.sys')
            Write-Info "hiberfil.sys = $sz. Tambahkan -DisableHibernate untuk membebaskannya."
        }
    }
}

# ------------------------------------------------------------- mode Full ----

function Invoke-FullCleanup {
    Write-Head 'Versi lama aplikasi Claude desktop'
    $claudeRoot = Find-ClaudeDesktopRoot
    if (-not $claudeRoot) {
        Write-Skip 'Instalasi Claude desktop tidak ditemukan'
    }
    elseif (-not (Test-ProcessIdle -Names @('claude'))) {
        Write-Note 'Claude desktop sedang berjalan. Tutup dulu, lalu ulangi. Dilewati.'
    }
    else {
        Write-Info "Root: $claudeRoot ($(Format-Size (Get-PathSizeBytes $claudeRoot)))"
        # Installer Squirrel menyimpan setiap versi sebagai app-x.y.z plus paket .nupkg.
        Remove-OldVersions -Label 'Versi lama app-*'      -Root $claudeRoot -Filter 'app-*' -VersionSort
        Remove-OldVersions -Label 'Paket installer .nupkg' -Root (Join-Path $claudeRoot 'packages') -Filter '*.nupkg' -Files -VersionSort
        Remove-Target      -Label 'SquirrelTemp'          -Path (Join-Path $claudeRoot 'packages\SquirrelTemp') -ContentsOnly
    }

    Write-Head 'Cache Gradle'
    if (-not (Test-ProcessIdle -Names @('java', 'gradle', 'kotlin-daemon', 'studio64'))) {
        Write-Note 'Ada JVM/Gradle/Android Studio berjalan. Dilewati.'
    }
    else {
        $gradle = Join-Path $env:USERPROFILE '.gradle'
        Remove-Target      -Label 'Gradle daemon logs' -Path (Join-Path $gradle 'daemon')            -ContentsOnly
        Remove-Target      -Label 'Gradle build-cache' -Path (Join-Path $gradle 'caches\build-cache-1') -ContentsOnly
        Remove-OldVersions -Label 'Gradle wrapper lama' -Root (Join-Path $gradle 'wrapper\dists')
    }

    Write-Head 'Cache browser headless (puppeteer)'
    $pptr = Join-Path $env:USERPROFILE '.cache\puppeteer'
    if (Test-Path -LiteralPath $pptr) {
        foreach ($browser in Get-ChildItem -LiteralPath $pptr -Directory -ErrorAction SilentlyContinue) {
            Remove-OldVersions -Label "puppeteer/$($browser.Name)" -Root $browser.FullName
        }
    }
    else { Write-Skip 'Cache puppeteer tidak ada' }

    Write-Head 'Cache package manager'
    foreach ($tool in @(
            @{ Name = 'npm'; Cmd = 'npm'; Args = @('cache', 'clean', '--force') },
            @{ Name = 'pip'; Cmd = 'pip'; Args = @('cache', 'purge') },
            @{ Name = 'yarn'; Cmd = 'yarn'; Args = @('cache', 'clean') })) {
        if (-not (Get-Command $tool.Cmd -ErrorAction SilentlyContinue)) {
            Write-Skip "$($tool.Name) tidak terpasang"
            continue
        }
        if ($PSCmdlet.ShouldProcess("cache $($tool.Name)", 'Bersihkan')) {
            $exe  = $tool.Cmd
            $argv = $tool.Args
            & $exe $argv 2>&1 | Out-Null
            Write-Ok "Cache $($tool.Name) dibersihkan"
        }
    }

    Write-Head 'Unduhan Windows Update'
    if (-not $script:IsAdmin) {
        Write-Skip 'Perlu Administrator'
    }
    elseif ($PSCmdlet.ShouldProcess('C:\Windows\SoftwareDistribution\Download', 'Hapus isi')) {
        Stop-Service -Name wuauserv, bits -Force -ErrorAction SilentlyContinue
        Remove-Target -Label 'SoftwareDistribution\Download' -Path 'C:\Windows\SoftwareDistribution\Download' -ContentsOnly
        Start-Service -Name wuauserv, bits -ErrorAction SilentlyContinue
    }

    Write-Head 'Component store Windows (DISM)'
    if (-not $script:IsAdmin) {
        Write-Skip 'Perlu Administrator'
    }
    else {
        $dismArgs = @('/Online', '/Cleanup-Image', '/StartComponentCleanup')
        if ($ResetBase) { $dismArgs += '/ResetBase' }
        $label = 'DISM ' + ($dismArgs -join ' ')
        if ($PSCmdlet.ShouldProcess($label, 'Jalankan')) {
            Write-Info 'Butuh 10-30 menit dan memakai CPU + disk cukup berat.'
            $before = Get-FreeGB
            & dism.exe @dismArgs | Out-Null
            $gained = [math]::Max(0, (Get-FreeGB) - $before)
            Add-Ledger -Label 'DISM component cleanup' -Bytes ([long]($gained * 1GB))
            Write-Ok ("DISM selesai, sekitar {0:N2} GB dibebaskan" -f $gained)
        }
    }

    if ($CompactWsl) {
        Write-Head 'Compact disk virtual WSL / Docker'
        $vhdx = Find-Vhdx
        if (-not $vhdx) {
            Write-Skip 'Tidak ada file vhdx ditemukan'
        }
        elseif (-not $script:IsAdmin) {
            Write-Note 'Compact vhdx perlu Administrator. Dilewati.'
        }
        elseif ($PSCmdlet.ShouldProcess('WSL + Docker', 'Shutdown lalu compact vhdx')) {
            Write-Note 'Mematikan semua distro WSL dan container Docker sekarang.'
            & wsl.exe --shutdown 2>&1 | Out-Null
            Start-Sleep -Seconds 8

            foreach ($v in $vhdx) {
                $before = $v.Length
                $done   = $false

                if (Get-Command Optimize-VHD -ErrorAction SilentlyContinue) {
                    try {
                        Optimize-VHD -Path $v.FullName -Mode Full -ErrorAction Stop
                        $done = $true
                    }
                    catch { Write-Info "Optimize-VHD gagal, beralih ke diskpart: $($_.Exception.Message)" }
                }

                if (-not $done) {
                    $dpScript = Join-Path $env:TEMP ('compact-' + [guid]::NewGuid().ToString('N') + '.txt')
                    $dpLines  = @(
                        ('select vdisk file="' + $v.FullName + '"'),
                        'attach vdisk readonly',
                        'compact vdisk',
                        'detach vdisk',
                        'exit'
                    )
                    Set-Content -LiteralPath $dpScript -Value $dpLines -Encoding ASCII
                    & diskpart.exe /s $dpScript 2>&1 | Out-Null
                    Remove-Item -LiteralPath $dpScript -Force -ErrorAction SilentlyContinue
                }

                $after  = (Get-Item -LiteralPath $v.FullName -ErrorAction SilentlyContinue).Length
                $gained = $before - $after
                if ($gained -gt 0) {
                    Add-Ledger -Label "Compact $($v.Name)" -Bytes $gained
                    Write-Ok "$($v.Name) : $(Format-Size $gained) dibebaskan"
                }
                else {
                    Write-Skip "$($v.Name) : sudah padat"
                }
            }
        }
    }
    else {
        $vhdx = Find-Vhdx
        if ($vhdx) {
            $total = ($vhdx | Measure-Object -Property Length -Sum).Sum
            Write-Head 'Disk virtual WSL / Docker'
            Write-Info "Total $(Format-Size $total). Tambahkan -CompactWsl untuk memadatkannya."
        }
    }

    Write-Head 'Docker (hanya laporan)'
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Info 'Image dan volume tidak dihapus otomatis karena bisa berisi data penting.'
        Write-Info 'Jalankan sendiri bila perlu: docker system prune -a --volumes'
    }
    else { Write-Skip 'Docker CLI tidak ada di PATH' }
}

# ------------------------------------------------------------------ main ----

$startFree = Get-FreeGB

Write-Host ''
Write-Host '  cleanup-c.ps1' -ForegroundColor White
Write-Host "  Mode: $Mode   Admin: $script:IsAdmin   Ruang bebas C: $startFree GB" -ForegroundColor White
if ($WhatIfPreference) { Write-Host '  DRY-RUN: tidak ada yang benar-benar dihapus.' -ForegroundColor Magenta }

$blockers = Get-RunningBlockers
if ($blockers.Count -gt 0) {
    Write-Host ''
    Write-Note "Proses aktif terdeteksi: $($blockers -join ', ')"
}

switch ($Mode) {
    'Report' {
        Invoke-Report
    }
    'Safe' {
        Invoke-SafeCleanup
    }
    'Full' {
        if ($blockers.Count -gt 0 -and -not $Force) {
            Write-Host ''
            Write-Host '  Mode Full dibatalkan.' -ForegroundColor Red
            Write-Host '  Ada pekerjaan yang sedang berjalan dan operasi berat bisa merusaknya.' -ForegroundColor Red
            Write-Host '  Pilihan: tunggu selesai, jalankan -Mode Safe, atau paksa dengan -Force.' -ForegroundColor Red
            Write-Host ''
            exit 2
        }
        Invoke-SafeCleanup
        Invoke-FullCleanup
    }
}

if ($Mode -ne 'Report') {
    $endFree = Get-FreeGB
    Write-Head 'Ringkasan'
    if ($script:Ledger.Count -gt 0) {
        $script:Ledger | Sort-Object Bytes -Descending | ForEach-Object {
            Write-Host ("   {0,-12} {1}" -f (Format-Size $_.Bytes), $_.Label)
        }
        $total = ($script:Ledger | Measure-Object -Property Bytes -Sum).Sum
        Write-Host ''
        Write-Host ("   Total      : {0}" -f (Format-Size $total)) -ForegroundColor Green
    }
    else {
        Write-Host '   Tidak ada yang dibersihkan.' -ForegroundColor DarkGray
    }
    Write-Host ("   Sebelum    : {0} GB bebas" -f $startFree)
    Write-Host ("   Sesudah    : {0} GB bebas" -f $endFree) -ForegroundColor Green
    Write-Host ''
}
