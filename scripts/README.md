# scripts/

Utilitas pendukung yang tidak termasuk kode API.

## `cleanup-c.ps1`

Pembersih ruang Local Disk `C:` untuk Windows, dirancang agar aman dijalankan
walau ada sesi Claude Code, build Gradle, atau container Docker yang sedang bekerja.

### Kenapa ada guard-nya

Perintah pembersihan yang lazim beredar (`Remove-Item $env:TEMP\*`,
`wsl --shutdown`, `Dism /ResetBase`) bisa menggagalkan pekerjaan yang sedang
berjalan: proses menulis file kerja di `%TEMP%`, dan WSL yang dimatikan membawa
serta semua container. Script ini memisahkan operasi berdasarkan risikonya.

| Mode     | Isi                                                                    | Kapan |
|----------|------------------------------------------------------------------------|-------|
| `Report` | Hanya memindai titik-titik panas dan melaporkan ukurannya              | Kapan saja |
| `Safe`   | Recycle Bin, temp **lebih tua dari N hari**, crash dump, sisa updater, cache Delivery Optimization | Kapan saja, termasuk saat ada task berjalan |
| `Full`   | Semua isi `Safe` + versi lama aplikasi Claude, cache Gradle & puppeteer, cache npm/pip/yarn, DISM, (opsional) compact WSL | Hanya saat idle |

Mode `Full` memeriksa proses `claude`, `node`, `java`, `gradle`, `dart`,
`flutter`, `vmmem*`, `wsl`, `docker`, dan **membatalkan diri** (exit code `2`)
kalau ada yang aktif. Lewati pemeriksaan itu dengan `-Force` hanya bila kamu
yakin tidak ada pekerjaan yang sedang jalan.

Batas usia file temp (`-TempOlderThanDays`, default `7`) adalah alasan utama
mode `Safe` aman: file kerja proses yang sedang berjalan selalu lebih baru dari
batas itu, jadi tidak pernah ikut terhapus.

### Pemakaian

```powershell
# Lihat dulu apa yang memakan tempat, tanpa menghapus apa pun
.\cleanup-c.ps1 -Mode Report

# Aman dijalankan sekarang juga
.\cleanup-c.ps1 -Mode Safe

# Lihat persis apa yang akan dihapus mode Full, tanpa menghapus
.\cleanup-c.ps1 -Mode Full -WhatIf

# Pembersihan menyeluruh, saat tidak ada pekerjaan berjalan
.\cleanup-c.ps1 -Mode Full -CompactWsl -ResetBase
```

Jalankan dari PowerShell **sebagai Administrator** agar langkah yang menyentuh
file sistem (dump kernel, Windows Update, DISM, compact `vhdx`) tidak dilewati.
Tanpa Administrator script tetap jalan, hanya melaporkan langkah mana yang
dilewati.

Kalau PowerShell menolak menjalankan file script:

```powershell
powershell -ExecutionPolicy Bypass -File .\cleanup-c.ps1 -Mode Report
```

### Yang sengaja TIDAK dilakukan

- **Transkrip Claude Code** (`~/.claude/projects/`) tidak disentuh — hanya
  `shell-snapshots` lebih tua dari 7 hari yang dihapus.
- **Image dan volume Docker** hanya dilaporkan. `docker system prune` bisa
  menghapus data yang tidak tergantikan, jadi keputusannya diserahkan ke kamu.
- **Cache pub (Dart/Flutter)** hanya dilaporkan, karena menghapusnya memaksa
  unduh ulang seluruh dependensi.
- **Hibernasi** hanya dimatikan bila kamu menambahkan `-DisableHibernate`,
  karena itu juga mematikan Fast Startup.

### Opsi

| Opsi | Arti |
|------|------|
| `-Mode <Report\|Safe\|Full>` | Default `Safe` |
| `-WhatIf` | Dry-run; tampilkan apa yang akan dihapus |
| `-Force` | Lewati pemeriksaan proses aktif pada mode `Full` |
| `-DisableHibernate` | Jalankan `powercfg /h off` (membebaskan ruang sebesar RAM) |
| `-ResetBase` | Tambahkan `/ResetBase` ke DISM; update lama tak bisa di-uninstall lagi |
| `-CompactWsl` | Shutdown WSL lalu compact `ext4.vhdx` |
| `-TempOlderThanDays <n>` | Ambang usia file temp, default `7` |
| `-KeepVersions <n>` | Jumlah versi terbaru yang dipertahankan, default `1` |
