---
title: "Rancangan Sistem Peta Belajar"
subtitle: "Aplikasi Android pemilih video YouTube untuk belajar apa saja"
author: "Disusun Acut2 untuk Acut"
date: "16 Oktober 2026 · Versi rancangan 2.3 · Semua gratis untuk pengguna"
---

# Ringkasan satu halaman

**Apa ini.** Aplikasi Android yang memilihkan video YouTube gratis yang tepat sasaran untuk apa pun yang ingin dipelajari seseorang, lalu menyusunnya menjadi jalur belajar berurutan. Nama kerjanya **Peta Belajar**.

**Masalah yang diselesaikan.** Orang yang ingin belajar, misalnya membuat konten, AutoCAD, atau memakai AI, menghabiskan waktu mencari video satu per satu di YouTube. Mereka mengambang, tidak tahu harus mulai dari mana, lalu jenuh dan berhenti.

**Cara kerjanya dalam satu kalimat.** Pengguna menulis keinginannya, menjawab beberapa pertanyaan pilihan, meninjau daftar judul yang akan dipelajari dan boleh mengeditnya, lalu setelah menekan Setuju menerima video berurutan dari banyak kreator, dan menontonnya di dalam aplikasi sambil mencatat, bertanya, dan menarik kesimpulan.

**Semua gratis untuk pengguna.** Tidak ada bayaran, langganan, atau saldo di versi ini. Biaya AI ditanggung kita dan ditekan serendah mungkin. Rencana fasilitas berbayar disimpan di bab terakhir untuk tahap lanjutan.

**Pusat tenaga.** Mesin pemilih video adalah jantung produk. Buku catatan dan menu lain hanya pendukung supaya nyaman.

**Pembeda dari aplikasi lain.**

- Jalur disusun dari banyak kreator, bukan satu video yang ditempel pengguna.
- Pengguna meninjau dan boleh mengedit daftar judul sebelum video dicari.
- Bahasa Indonesia didahulukan, dengan pertanyaan pilihan dan tes level.
- Jalur yang sering dipakai diperiksa manusia lalu diberi tanda **Teruji**.
- Bertanya dan merangkum memakai AI milik pengguna sendiri, jadi biaya kita hampir nol.
- Gratis tapi tetap terarah: paling banyak 2 jalur aktif, janji jadwal belajar, dan syarat langkah selesai.

**Teknologi.** Aplikasi dibuat dengan Expo (React Native), server kecil memakai Supabase, video dicari lewat jalur resmi YouTube, dan pemilihan dibantu Claude. Semuanya punya jatah gratis.

**Biaya yang kita tanggung.** Sekitar Rp190 untuk setiap rencana baru topik kecil dan Rp640 untuk topik besar. Sebanyak 200 jalur siap pakai untuk topik populer disusun sekali dengan biaya sekitar Rp40 sampai 80 ribu. Selama November, perkiraannya Rp65 sampai 105 ribu, dengan batas siaga Rp150 ribu.

**Jadwal.** Versi 1 siap diuji di HP Acut pada 7 November. Uji tertutup Play Store berlangsung 9 sampai 23 November. Target tayang 1 Desember 2026, cadangan 15 Desember.

**Tiga risiko terbesar.**

1. Mutu pilihan otomatis kurang tepat, padahal itu jantung produk.
2. Jatah pencarian YouTube gratis terbatas. Karena video dicari bertahap per modul, jatah itu cukup untuk sekitar 15 sampai 25 rencana baru per hari.
3. Biaya AI ditanggung Acut dan belum ada pemasukan. Biaya dibatasi dengan jatah 3 rencana baru per bulan per pengguna dan batas anggaran bulanan.

**Yang perlu Acut putuskan.** Ada delapan keputusan, dirinci di bab Keputusan. Yang paling mendesak adalah akun layanan dan modal biaya AI bulanan.

# Masalah dan tujuan

## Masalah

YouTube dan TikTok menyimpan sangat banyak pelajaran berharga, dan sering kali hanya di sana pelajaran itu bisa didapat. Tetapi isinya berserakan:

- Video untuk pemula bercampur dengan video untuk yang sudah mahir.
- Satu topik dibahas ratusan kreator dengan urutan yang berbeda-beda.
- Judul sering menjanjikan lebih dari isinya.
- Orang level nol tidak tahu kata apa yang harus diketik di kolom pencarian.

Akibatnya orang menonton acak, tidak menemukan urutan yang masuk akal, lalu berhenti sebelum mendapat ilmunya.

## Tujuan utama

**Memilihkan video YouTube yang tepat sasaran supaya pengguna benar-benar mendapat ilmunya, tanpa mengambang dan tanpa jenuh mencari satu per satu.**

Semua fitur lain dinilai dari satu pertanyaan: apakah fitur ini membantu pengguna menyelesaikan jalurnya?

## Ukuran berhasil

Setiap angka punya target dan cadangan. Cadangan adalah angka paling rendah yang masih membuat kita lanjut.

| Ukuran | Target | Cadangan |
|---|---|---|
| Video pertama dinilai "Membantu" | 60% | 45% |
| Lanjut ke video kedua | 50% | 35% |
| Rencana disetujui tanpa disusun ulang | 70% | 50% |
| Pengguna yang memasang janji jadwal belajar | 50% | 30% |
| Menyelesaikan level pertama jalur | 30% | 15% |
| Penguji tetap aktif 14 hari | 20 orang | 12 orang |
| Catatan per pengguna aktif | 3 | 1 |

Kalau dua angka teratas di bawah cadangan, kita perbaiki mesin pemilih dulu sebelum menambah fitur apa pun.

# Siapa penggunanya

Versi 1 menyasar orang dewasa berumur 18 tahun ke atas. Alasannya, aturan Play Store dan PP Tunas untuk aplikasi anak jauh lebih ketat. Pelajar SMA bisa menjadi sasaran versi berikutnya.

Tiga contoh pengguna pertama di Aceh:

**Bang Rahmat, pemilik warung kopi, level nol.** Ingin membuat video promosi untuk TikTok. Hanya punya HP Android. Belum pernah mengedit video. Waktu luangnya 30 menit setelah warung tutup.

**Kak Nur, guru honorer, level dasar.** Sudah memakai ChatGPT untuk membuat soal, tapi ingin memakai AI lebih rapi untuk administrasi kelas. Punya laptop dan HP.

**Fadhil, mahasiswa teknik sipil, level lanjut.** Sudah bisa dasar AutoCAD dari kampus, tapi ingin mahir menggambar denah rumah tiga dimensi. Mau belajar satu jam sehari.

Ketiganya punya pola yang sama: tahu apa yang diinginkan, tapi tidak tahu video mana yang harus ditonton dan dalam urutan apa.

# Perjalanan pengguna

Begini perjalanan Bang Rahmat dari membuka aplikasi sampai selesai satu langkah.

<!-- VISUAL:alur -->

1. **Menulis keinginan.** Di layar Beranda ia mengetik "bikin video promosi warung kopi".
2. **Menjawab pertanyaan pilihan.** Aplikasi menanyakan empat sampai lima hal, satu per layar, cukup sekali ketuk: video untuk TikTok atau Instagram, sudah pernah mengedit atau belum, pakai HP atau laptop, bahasa video, dan waktu luang per hari.
3. **Meninjau rencana belajar.** Sebelum satu video pun dicari, aplikasi menampilkan daftar judul yang akan dipelajari, dikelompokkan dalam modul. Bang Rahmat boleh mengubah judul, menghapus, menambah, menggeser urutan, atau menandai "Sudah bisa". Kalau tidak ingin mengubah apa pun, ia cukup menekan **Setuju**.
4. **Berjanji lalu menerima video.** Saat menekan Setuju, ia memilih jadwal belajar, misalnya Senin, Rabu, dan Jumat jam 20.00. Aplikasi lalu mencarikan video untuk modul pertama dalam 10 sampai 30 detik. Setiap judul mendapat satu video utama dan dua video cadangan. Video untuk modul berikutnya dicari saat ia sudah menyelesaikan separuh modul sebelumnya.
5. **Menonton di dalam aplikasi.** Ia menekan langkah pertama. Video diputar memakai pemutar resmi YouTube di dalam aplikasi, sehingga iklan dan hak kreator tetap utuh.
6. **Mencatat sambil menonton.** Di bawah video ada tiga tombol besar: **Catat**, **Tanya**, dan **Simpulkan**. Saat salah satu ditekan, video otomatis berhenti dan menitnya tercatat sendiri.
7. **Menyimpan lalu lanjut.** Setelah menulis, ia menekan Simpan dan video lanjut dari menit yang sama.
8. **Menilai video.** Di akhir video ia memilih "Membantu" atau "Tidak sesuai". Kalau ia memilih "Tidak sesuai", video cadangan langsung tampil.
9. **Menutup langkah.** Langkah dianggap selesai kalau ia menonton minimal 70% video dan menulis satu kesimpulan. Syarat ini mencegah centang asal-asalan, pelajaran dari uji halaman Claude ketika 17 langkah bisa dicentang dalam 6 menit.

# Daftar layar

Versi 1 punya sepuluh layar. Empat layar terpenting digambar di bawah ini.

<!-- VISUAL:layar -->

<!-- ASCII-START -->

```
┌──────────────────────────────┐
│ Mau belajar apa hari ini?    │
│ ┌──────────────────────────┐ │
│ │ bikin video promosi...   │ │
│ └──────────────────────────┘ │
│ [ Susun jalur belajar ]      │
│                              │
│ Lanjutkan belajar            │
│ ▸ Video promosi · 3/9        │
│                              │
│ Jalur Teruji                 │
│ ▸ Belajar Claude dari Nol    │
│ ▸ Excel untuk Kerja          │
└──────────────────────────────┘
          Layar Beranda
```

```
┌──────────────────────────────┐
│ Rencana belajar              │
│ Belajar AI dari 0 sampai ahli│
│ 8 modul · 31 judul           │
│ Modul 1 · Kenal AI           │
│  ✎ Apa itu AI & cara kerjanya│
│  ✎ Mencoba ChatGPT & Claude  │
│  ✓ Membuat akun (Sudah bisa) │
│  + Tambah judul              │
│ Modul 2 · Menulis perintah ▸ │
│ [Susun ulang]                │
│ [ Setuju, carikan videonya ] │
└──────────────────────────────┘
        Layar Rencana belajar
```

```
┌──────────────────────────────┐
│ ▓▓▓▓▓▓ VIDEO YOUTUBE ▓▓▓▓▓▓▓ │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ Langkah 2 · Potong & susun   │
│ Kanal: (nama kreator)        │
│ ┌────────┬────────┬────────┐ │
│ │ Catat  │ Tanya  │Simpulkan││
│ └────────┴────────┴────────┘ │
│ Catatan langkah ini:         │
│ 01:17 Tahan klip, geser...   │
│ [Membantu]  [Tidak sesuai]   │
└──────────────────────────────┘
          Layar Belajar
```

<!-- ASCII-END -->

## 1. Pembuka dan masuk

Pengguna bisa langsung mencoba sebagai **tamu**. Semua catatan tersimpan di HP. Kalau ingin catatannya aman saat ganti HP, ia masuk dengan akun Google, dan catatan tamu ikut terbawa.

## 2. Beranda

Isinya kolom "Mau belajar apa hari ini?", daftar jalur yang sedang dipelajari dengan tombol Lanjutkan, dan daftar Jalur Teruji yang populer.

## 3. Pertanyaan pilihan

Empat sampai lima kartu, satu kartu per layar, setiap kartu cukup sekali ketuk. Ada tombol "Lewati" untuk pengguna yang tidak sabar. Isi pertanyaannya dijelaskan di bab Mesin Pemilih.

## 4. Rencana belajar

Layar ini usulan Acut. Isinya daftar judul yang akan dipelajari, dikelompokkan dalam modul, sebelum satu video pun dicari. Untuk topik besar seperti "belajar AI dari 0 sampai expert", modul dibagi ke empat level: Nol, Dasar, Lanjut, dan Ahli.

Yang bisa dilakukan pengguna pada setiap judul:

- **Ubah judul**, misalnya "Dasar prompt" menjadi "Cara memberi perintah ke ChatGPT".
- **Hapus** judul yang tidak dibutuhkan.
- **Tambah** judul sendiri di modul mana pun.
- **Geser** urutan dengan menahan lalu menarik judul.
- **Tandai "Sudah bisa"**, sehingga judul dilewati tanpa dihapus.

Di bawah daftar ada dua tombol: **Setuju, carikan videonya** dan **Susun ulang**. Tombol Setuju dibuat paling besar, sebab orang level nol biasanya belum tahu apa yang perlu diubah. Mengedit adalah pilihan, bukan kewajiban. Setelah Setuju, muncul pilihan jadwal belajar yang dijelaskan di bab Supaya Gratis Tetap Terarah.

Setelah pengguna mengedit, AI memeriksa urutannya sekali. Kalau ada yang janggal, muncul peringatan lembut, misalnya: "Judul *Membuat agen AI* butuh dasar *Menulis perintah yang baik* yang tadi dihapus. Tetap lanjut?" Keputusan tetap di tangan pengguna.

## 5. Menyusun jalur

Layar tunggu muncul dua kali: sekitar 10 detik saat rencana disusun, lalu 10 sampai 30 detik setelah Setuju saat video dicari. Keterangannya jujur tentang apa yang sedang dikerjakan, misalnya "Mencari video berbahasa Indonesia…" lalu "Memilih video untuk pemula…". Kalau jalur yang sama pernah disusun untuk orang lain, jalur langsung tampil tanpa menunggu.

## 6. Peta jalur

Daftar modul dan judul yang dibagi per level. Setiap judul menampilkan durasi video dan status selesai. Di bagian atas ada tanda **Teruji** atau **Disusun otomatis**, dan tombol **Ubah rencana**. Kalau rencana diubah di tengah jalan, video hanya dicari ulang untuk judul yang berubah.

## 7. Layar Belajar

Layar terpenting setelah mesin pemilih.

- **HP tegak:** video di atas, tiga tombol besar di bawahnya, lalu daftar catatan langkah itu.
- **HP miring, Mode Layar Lebar:** video mengisi sekitar 90% layar. Di tepi kanan ada jalur tipis berisi satu tombol bulat yang bisa digeser naik-turun. Rinciannya ada di bab Layar Belajar dan buku catatan.

Tombol tidak pernah diletakkan di atas video, sebab aturan YouTube melarangnya.

## 8. Panel catatan

Muncul dari bawah saat tombol Catat, Tanya, atau Simpulkan ditekan. Video berhenti otomatis, dan menit video tercatat di pojok panel.

- **Catat:** kolom tulisan bebas.
- **Tanya:** kolom pertanyaan dengan tombol "Tanyakan ke…" yang membuka AI pilihan pengguna.
- **Simpulkan:** kolom satu kalimat "Hal terpenting dari bagian ini adalah…".

Untuk menghemat ketikan, pengguna bisa menekan ikon mikrofon di papan ketik HP-nya. Fitur ini sudah ada di Android dan tidak perlu dibangun sendiri.

## 9. Buku catatan

Semua catatan, pertanyaan, jawaban, dan kesimpulan dikelompokkan per jalur dan per langkah. Setiap catatan bertanda menit dan bisa ditekan untuk membuka video tepat di menit itu. Ada pencarian, dan buku bisa dibagikan sebagai teks ke WhatsApp.

## 10. Profil dan pengaturan

Pengaturannya: AI pilihan (Claude, ChatGPT, Gemini, atau lainnya), bahasa video, pengingat belajar, kebijakan privasi, tombol **Unduh dataku**, dan tombol **Hapus akun**. Tombol Hapus akun wajib ada menurut aturan Play Store, dan Unduh dataku memenuhi hak pengguna menurut UU Pelindungan Data Pribadi.

# Mesin pemilih video

Ini jantung aplikasi. Mesin bekerja dalam tujuh tahap. Tahap 4 adalah giliran pengguna.

<!-- VISUAL:mesin -->

## Tahap 1. Memahami keinginan

Ketikan bebas pengguna, misalnya "bikin video promosi warung kopi", dibaca AI untuk menentukan topik, perkiraan tujuan, dan pilihan jawaban untuk pertanyaan pertama.

## Tahap 2. Pertanyaan pilihan

Paling banyak lima pertanyaan. Empat pertanyaan tetap, satu atau dua disesuaikan dengan topik.

| Pertanyaan | Contoh pilihan |
|---|---|
| Tujuanmu yang paling dekat? | Video jualan TikTok · Vlog YouTube · Poster Instagram · Lainnya |
| Sudah sampai mana? | Belum pernah sama sekali · Pernah coba sedikit · Sudah bisa dasar |
| Belajar pakai apa? | HP Android · Laptop Windows · iPhone · MacBook |
| Bahasa video? | Indonesia saja · Indonesia dulu, Inggris boleh · Bebas |
| Waktu belajar per hari? | 15 menit · 30 menit · 1 jam atau lebih |

Pertanyaan pertama dibuat AI dari ketikan pengguna. Pertanyaan lain memakai daftar tetap, sehingga murah dan cepat.

## Tahap 3. Menyusun rencana belajar

AI menyusun rencana berupa **modul** (judul besar) yang berisi **judul-judul** (langkah belajar) berurutan, sesuai jawaban pengguna. Setiap judul menyimpan tujuan dan kata kunci pencarian dalam bahasa Indonesia dan Inggris, tapi pengguna hanya melihat judulnya.

- **Topik kecil**, seperti video promosi warung, cukup 1 sampai 2 modul dengan 6 sampai 12 judul.
- **Topik besar**, seperti AI dari 0 sampai ahli, bisa sampai 10 modul dengan 3 sampai 6 judul per modul.

Contoh rencana untuk "belajar AI dari 0 sampai expert":

| Level | Modul |
|---|---|
| Nol | 1. Kenal AI dan cara kerjanya · 2. Menulis perintah yang baik |
| Dasar | 3. AI untuk kerja harian · 4. Membuat gambar dan video dengan AI |
| Lanjut | 5. Projects, Skills, dan Connectors · 6. Otomatisasi dan agen AI |
| Ahli | 7. Membangun aplikasi AI sendiri · 8. Dasar pembelajaran mesin, etika, dan keamanan |

Contoh untuk Bang Rahmat, satu modul:

1. Kenal aplikasi CapCut di HP
2. Merekam video yang terang dan stabil
3. Memotong dan menyusun klip
4. Menambah teks dan musik
5. Membuat 3 detik pembuka yang menarik
6. Mengunggah ke TikTok dan memilih jam tayang

## Tahap 4. Pengguna mengedit dan menyetujui

Pengguna meninjau rencana di layar Rencana belajar: mengubah, menghapus, menambah, menggeser, atau menandai "Sudah bisa". Kalau ada yang diedit, AI memeriksa urutannya sekali dan memberi peringatan lembut bila ada dasar yang hilang. Video baru dicari setelah pengguna menekan **Setuju**.

Tahap ini punya tiga manfaat:

- **Lebih tepat sasaran,** sebab pengguna sendiri yang memastikan judulnya sesuai kebutuhan.
- **Lebih hemat,** sebab tidak ada jatah YouTube yang terpakai untuk judul yang akhirnya dihapus.
- **Bahan belajar bagi kita.** Judul yang sering ditambah atau dihapus orang menjadi masukan untuk memperbaiki rencana bawaan.

## Tahap 5. Mencari kandidat video

Video dicari **bertahap per modul**. Setelah Setuju, hanya modul pertama yang dicarikan. Modul berikutnya dicari saat pengguna sudah menyelesaikan separuh modul sebelumnya. Alasannya, banyak orang berhenti sebelum modul terakhir, dan video untuk modul yang masih jauh bisa basi sebelum ditonton.

Untuk setiap judul, mesin mencari video lewat jalur resmi YouTube. Bahasa Indonesia dicari lebih dulu. Bahasa Inggris hanya dipakai kalau kandidat Indonesia kurang dari lima dan pengguna mengizinkan.

**Saringan wajib.** Video yang tidak lolos langsung dibuang:

- Boleh diputar di aplikasi lain.
- Durasi 3 sampai 45 menit. Video pendek boleh menjadi pelengkap, bukan inti.
- Bukan siaran langsung.
- Untuk topik teknologi, diunggah paling lama 24 bulan terakhir.
- Ditonton minimal 1.000 kali, kecuali dari kanal resmi pembuat alat.

## Tahap 6. Menilai dan memilih

Setiap kandidat diberi nilai dari lima sumber:

| Sumber nilai | Bobot |
|---|---|
| Kecocokan isi dengan langkah dan level, dinilai AI dari judul, deskripsi, dan daftar bab | 40% |
| Mutu: rasio suka per tonton dan jumlah tonton per hari sejak diunggah | 20% |
| Penilaian pengguna kita: "Membantu", ditonton sampai habis | 15% |
| Kesegaran video | 15% |
| Bahasa sesuai pilihan pengguna | 10% |

Ada dua aturan tambahan:

- **Bonus seri.** Kalau satu kreator punya seri berurutan yang cocok untuk beberapa langkah, seri itu diutamakan, sebab gaya dan istilahnya sama.
- **Batas satu kreator.** Paling banyak setengah jalur dari satu kreator, kecuali seri yang memang lengkap.

Setiap langkah mendapat satu video utama dan dua cadangan. Di jalur baru, penilaian pengguna belum ada, jadi bobotnya dibagi ke sumber lain.

**Batas yang perlu diketahui.** Isi video orang lain tidak bisa dibaca lewat jalur resmi YouTube. Mesin hanya membaca judul, deskripsi, dan daftar bab. Kekurangan ini ditutup oleh tombol "Membantu" dan "Tidak sesuai" dari pengguna.

## Tahap 7. Menyimpan, memakai ulang, dan memperbaiki

- **Dipakai ulang per rencana.** Rencana bawaan disimpan. Pengguna berikutnya dengan topik dan jawaban yang sama langsung menerimanya, tanpa biaya dan tanpa menunggu.
- **Dipakai ulang per judul.** Pilihan video juga disimpan per judul, bersama level, bahasa, dan perangkatnya. Jadi rencana yang sudah diedit tetap bisa memakai pilihan video dari orang lain untuk judul yang sama.
- **Diperbaiki sendiri.** Video yang sering dinilai "Tidak sesuai" turun nilainya dan diganti cadangan.
- **Naik menjadi Teruji.** Jalur yang dipakai minimal 20 orang dengan nilai "Membantu" minimal 60% masuk daftar periksa. Setelah Acut atau Acut2 memeriksanya, jalur diberi tanda **Teruji**.
- **Disegarkan setiap 30 hari.** Data dari YouTube wajib diperbarui atau dihapus setiap 30 hari. Video yang hilang atau dikunci otomatis diganti.

## Dua jenis jalur

| | Jalur Teruji | Jalur Otomatis |
|---|---|---|
| Disusun oleh | Mesin, lalu diperiksa manusia | Mesin saja |
| Cek paham | Kuis buatan pemeriksa | Kesimpulan dari pengguna |
| Tanda di aplikasi | Teruji | Disusun otomatis |
| Contoh pertama | Belajar Claude dari Nol | Topik apa saja |

Jalur teruji pertama adalah "Belajar Claude dari Nol" yang sudah dibuat sebagai halaman uji, ditambah tiga topik yang dipilih Acut.

# Layar Belajar dan buku catatan

## Pemutar resmi YouTube

Video diputar memakai pemutar resmi YouTube yang disematkan di aplikasi. Dengan cara ini aplikasi bisa:

- menjeda dan melanjutkan video,
- membaca menit yang sedang diputar,
- membaca durasi video untuk menghitung berapa persen yang sudah ditonton.

Semua ini tanpa izin khusus, dan cara yang sama nanti jalan di iPhone dan website.

Batasan dari YouTube:

- Tidak boleh ada tombol atau apa pun di atas video, termasuk saat layar penuh.
- Ukuran pemutar minimal 200 × 200 piksel.
- Video tidak boleh diputar saat layar mati atau diunduh.
- Kalau pengguna menekan tombol layar penuh milik YouTube, tombol kita tidak terlihat sampai ia keluar dari layar penuh.

Pelanggaran aturan ini berisiko besar. YouTube bisa mencabut kunci akses aplikasi, sehingga pencarian video dan pemutar sama-sama mati.

## Mode Layar Lebar

Mode ini usulan Acut, supaya pengguna bisa menonton hampir layar penuh sambil tetap punya tombol catatan seperti tombol bulat di iPhone. Mode Layar Lebar aktif otomatis saat HP dimiringkan.

<!-- VISUAL:lebar -->

<!-- ASCII-START -->

```
Saat menonton:
┌─────────────────────────┬──┐
│                         │  │
│      VIDEO (±90%)       │ ◉│
│                         │  │
└─────────────────────────┴──┘

Saat tombol ◉ ditekan:
┌──────────────┬─────────────┐
│ VIDEO kecil  │ Beri catatan│
│ berhenti di  │ Isi tanya   │
│ 01:17        │ Simpulkan   │
│              │ [Simpan]    │
└──────────────┴─────────────┘
```

<!-- ASCII-END -->

Cara kerjanya:

1. **Saat menonton,** video mengisi sekitar 90% layar. Tombol bulat berada di jalur tipis di tepi kanan, di samping video, bukan di atasnya. Tombol bisa digeser naik-turun sepanjang jalur itu supaya tidak mengganggu.
2. **Saat tombol ditekan,** video berhenti otomatis dan menitnya tercatat. Video mengecil ke kiri, lalu menu muncul di kanan: **Beri catatan**, **Isi pertanyaan**, dan **Tarik 1 kesimpulan**. Menu tidak menutupi video, sebab video bergeser memberi tempat.
3. **Saat Simpan ditekan,** menu tertutup, video kembali melebar, dan lanjut dari menit yang sama.

Mode ini tetap mematuhi aturan YouTube, sebab tidak ada apa pun di atas video. Kelemahannya, layar tidak 100% penuh karena jalur tombol di tepi kanan selalu tersisa.

## Jalan pintas tanpa tombol

Dua jalan pintas ini tidak menaruh apa pun di atas video, sehingga bisa dipakai juga saat pengguna memakai layar penuh milik YouTube. Keduanya **wajib diuji dulu di HP sungguhan** sebelum masuk versi 1.

| Jalan pintas | Cara | Yang perlu diuji |
|---|---|---|
| Tombol volume | Tekan tombol volume bawah dua kali dengan cepat: video berhenti, layar penuh tertutup, menu catatan terbuka | Apakah aplikasi bisa membaca tombol volume saat layar penuh YouTube aktif, dan apakah suara tetap bisa diatur normal |
| Goyang HP | Goyangkan HP dua kali: video berhenti dan menu catatan terbuka | Seberapa sering terpicu tanpa sengaja saat HP dipegang sambil berbaring atau di kendaraan |

Kalau hasil uji bagus, kedua jalan pintas tersedia di pengaturan dan bisa dimatikan. Kalau tidak andal, keduanya ditunda dan Mode Layar Lebar tetap menjadi cara utama.

## Tanya ke AI milik pengguna

1. Pengguna menulis pertanyaannya di panel Tanya.
2. Aplikasi menyusun pesan lengkap: topik, langkah, judul video, menit, catatan terakhir, dan pertanyaannya.
3. Aplikasi membuka menu **Bagikan** bawaan Android. Pengguna memilih aplikasi ChatGPT, Gemini, Claude, atau AI lain, dan pesan langsung masuk ke kolom ketiknya.
4. Setelah AI menjawab, pengguna menyalin jawabannya lalu kembali ke Peta Belajar.
5. Aplikasi menampilkan tombol **"Tempel jawaban dari AI"**. Satu ketukan menyimpan jawaban di bawah pertanyaannya.

Cara ini membuat biaya AI kita nol untuk fitur Tanya. Kelemahannya, cara ini kurang mulus dibanding AI bawaan. AI bawaan masuk daftar fasilitas berbayar di bab terakhir.

## Simpulkan

Pengguna menulis satu kalimat kesimpulan sendiri. Ada juga tombol "Minta AI merangkum catatanku" yang bekerja seperti fitur Tanya: catatan langkah itu dikirim ke AI pilihan pengguna lewat menu Bagikan.

## Syarat langkah selesai

Langkah selesai kalau pengguna menonton minimal 70% video **dan** menulis satu kesimpulan. Untuk Jalur Teruji ada tambahan kuis satu soal.

# Supaya gratis tetap terarah

Kekhawatiran Acut: aplikasi gratis bisa membuat orang bingung, nyasar, dan berputar-putar tanpa berkembang. Yang membuat orang nyasar biasanya bukan soal gratis atau bayar, melainkan tidak adanya arahan dan komitmen. Karena itu versi gratis memasang tujuh pagar berikut.

1. **Paling banyak 2 jalur aktif.** Untuk mulai jalur ketiga, pengguna harus menyelesaikan atau menjeda salah satu jalur. Berpindah-pindah topik adalah penyebab utama orang berputar di tempat.
2. **Janji jadwal belajar.** Saat menekan Setuju, pengguna memilih hari dan jam belajar, serta target menyelesaikan modul pertama. Pengingat dikirim oleh HP sendiri, tanpa server dan tanpa biaya.
3. **Satu tombol Lanjutkan.** Beranda selalu menunjuk tepat ke langkah berikutnya, bukan puluhan pilihan.
4. **Syarat langkah selesai.** Minimal 70% video ditonton ditambah satu kesimpulan. Jalur Teruji juga punya kuis satu soal.
5. **Ringkasan mingguan.** Setiap Minggu malam, aplikasi menampilkan kemajuan minggu itu, misalnya "3 langkah, 5 catatan, 2 kesimpulan", beserta kesimpulan yang ditulis pengguna sendiri. Kemajuan yang terlihat membuat orang mau lanjut.
6. **Jatah 3 rencana baru per bulan.** Jatah ini mencegah orang terus membuat rencana tanpa belajar, sekaligus menjaga biaya. Jalur Teruji dan rencana yang sudah pernah disusun tidak memakan jatah.
7. **Rencana baru perlu akun Google.** Pengguna tamu tetap bisa memakai semua Jalur Teruji dan rencana yang sudah ada. Aturan ini mencegah penyalahgunaan oleh mesin otomatis.

# Cara kerja di balik layar

Sistem terdiri dari tiga bagian.

<!-- VISUAL:arsitektur -->

**1. Aplikasi di HP.** Dibuat dengan Expo (React Native). Aplikasi menampilkan layar, memutar video lewat pemutar resmi YouTube, dan menyimpan catatan di HP lebih dulu, supaya tetap bisa mencatat walau sinyal hilang.

**2. Server kecil di Supabase.** Isinya tiga hal:

- **Login:** tamu atau akun Google.
- **Database:** jalur, video, penilaian, kemajuan, dan catatan.
- **Fungsi server:** potongan program yang memanggil YouTube dan Claude. Kunci rahasia layanan disimpan di sini, tidak pernah di dalam aplikasi, sehingga tidak bisa dicuri dari HP.

**3. Layanan luar.**

- **YouTube Data API:** mencari video dan membaca judul, deskripsi, durasi, dan angka tonton.
- **Claude API:** memahami keinginan, menyusun kerangka langkah, dan menilai kecocokan kandidat.
- **Pemutar resmi YouTube:** memutar video langsung dari YouTube ke HP pengguna.
- **AI milik pengguna:** dibuka lewat menu Bagikan, di luar sistem kita.

## Pembagian tugas AI

| Tugas | Model | Alasan |
|---|---|---|
| Memahami ketikan dan membuat pertanyaan pertama | Claude Haiku 5.5 | Tugas pendek, paling murah |
| Menyusun rencana: modul dan judul | Claude Haiku 5.5, cadangan Sonnet 5.5 | Paling murah. Sonnet dipakai hanya kalau uji manual menunjukkan mutu Haiku kurang |
| Memeriksa urutan rencana setelah diedit | Claude Haiku 5.5 | Pendek dan murah |
| Menilai kecocokan kandidat video | Claude Haiku 5.5 | Banyak dan berulang, harus murah |
| Menyusun 200 jalur siap pakai sekaligus | Claude Haiku 5.5 lewat layanan Batch | Separuh harga, hasilnya keluar dalam beberapa jam |

Layanan Batch adalah cara mengirim banyak pekerjaan AI sekaligus untuk dikerjakan tanpa terburu-buru, dengan harga separuh.

# Data yang disimpan

| Data | Isi | Siapa yang bisa melihat |
|---|---|---|
| Pengguna | Nama dari akun Google, email, tanggal daftar | Pengguna sendiri |
| Profil belajar | Jawaban pertanyaan pilihan | Pengguna sendiri |
| Topik dan rencana bawaan | Keinginan yang sudah dirapikan, modul dan judul | Semua, tanpa nama pengguna |
| Rencana pribadi | Judul hasil edit pengguna | Pengguna sendiri. Perubahan judul dipakai tanpa nama untuk memperbaiki rencana bawaan |
| Video | Nomor video YouTube, judul, kanal, durasi, nilai | Semua, disegarkan setiap 30 hari |
| Penilaian | "Membantu" atau "Tidak sesuai", persen ditonton | Hanya angka gabungan yang dipakai |
| Kemajuan | Langkah selesai, menit terakhir | Pengguna sendiri |
| Catatan | Catatan, pertanyaan, jawaban, kesimpulan | Hanya pengguna sendiri |

**Prinsip privasi.**

- **Catatan sepenuhnya milik pengguna.** Acut dan Acut2 tidak membaca isi catatan. Laporan hanya memakai jumlah.
- **Hanya data yang perlu yang disimpan.** Tidak ada nomor HP, lokasi, atau kontak.
- **Hapus akun berarti semua data pribadi dihapus,** sesuai UU Pelindungan Data Pribadi dan aturan Play Store.

# Siapa memegang data

## Tempat data tersimpan

| Tempat | Data | Siapa yang bisa melihat |
|---|---|---|
| HP pengguna | Catatan yang belum terkirim, dan semua data pengguna tamu | Hanya pengguna itu. Data tamu tidak pernah sampai ke kita |
| Database Supabase di akun Acut | Akun, jawaban pertanyaan pilihan, rencana, kemajuan, penilaian video, catatan, pertanyaan, jawaban, kesimpulan | Acut sebagai pemilik akun, dan orang yang Acut beri akses |
| Google | Nama dan email saat masuk, angka unduhan, laporan aplikasi macet | Acut, lewat Play Console |
| Anthropic, pembuat Claude | Teks keinginan dan susunan rencana yang dikirim untuk diolah | Disimpan sementara sesuai kebijakan Anthropic, dan secara bawaan tidak dipakai melatih AI |
| YouTube | Data bahwa video ditonton lewat pemutarnya | YouTube. Catatan pengguna tidak pernah sampai ke YouTube |
| AI milik pengguna | Pertanyaan yang dikirim lewat menu Bagikan | Urusan pengguna dengan AI-nya, di luar sistem kita |

**Lokasi server.** Database ditempatkan di Singapura, lokasi terdekat yang tersedia di Supabase. Server Jakarta belum terlihat di daftar resmi mereka dan dicek ulang saat akun dibuka. Menurut UU Pelindungan Data Pribadi, data boleh disimpan di luar negeri kalau negara tujuannya punya pelindungan yang setara, dan hal ini harus disebut jelas di kebijakan privasi.

## Siapa yang bisa melihat

- **Acut,** sebagai pemilik akun Supabase, Play Console, dan Claude. Semua akun dijaga dengan verifikasi dua langkah.
- **Acut2,** hanya kalau Acut memberi akses untuk tugas tertentu.
- **Pengguna,** untuk datanya sendiri.
- **Tidak ada pihak lain.**

## Aturan catatan pribadi

Keputusan Acut: catatan pribadi dijaga dengan aturan dan akses terbatas.

- **Isi catatan, pertanyaan, jawaban, dan kesimpulan tidak dibuka.** Laporan hanya memakai angka gabungan.
- **Pengecualian:** pengguna sendiri meminta bantuan dan mengizinkan, misalnya saat melaporkan masalah.
- **Setiap pembukaan data pribadi oleh pengelola dicatat:** siapa, kapan, dan apa alasannya.
- **Jujur kepada diri sendiri:** secara teknis pemilik database tetap bisa membuka isi catatan. Karena itu akses dijaga ketat. Pilihan mengunci catatan di HP pengguna disimpan untuk versi berikutnya.

## Hak pengguna

- **Unduh dataku:** satu file berisi akun, rencana, kemajuan, dan semua catatan. UU Pelindungan Data Pribadi meminta akses diberikan paling lambat 3 × 24 jam, dan tombol ini memenuhinya seketika.
- **Memperbaiki data, menarik persetujuan, dan menghapus akun,** dari dalam aplikasi maupun lewat halaman web.
- **Akun yang tidak aktif 24 bulan** diberi tahu lewat email, lalu dihapus kalau tidak ada tanggapan.

## Cadangan dan kebocoran

- **Cadangan otomatis mingguan** ke Google Drive Acut, tanpa biaya, sebab cadangan di paket gratis Supabase terbatas.
- **Kalau terjadi kebocoran,** pengguna dan lembaga pengawas wajib diberi tahu secara tertulis paling lambat 3 × 24 jam, sesuai Pasal 46 UU Pelindungan Data Pribadi. Acut2 menyiapkan langkah tanggap dan contoh surat pemberitahuan sebelum aplikasi tayang.

# Pemanfaatan data

## Boleh, dan disebut di kebijakan privasi

| Pemanfaatan | Contoh | Syarat |
|---|---|---|
| Menjalankan layanan | Menyusun rencana, menyimpan kemajuan, mengirim pengingat | Tidak ada |
| Memperbaiki mesin pemilih | Video yang sering dinilai "Tidak sesuai" diganti, judul yang sering diedit dirapikan | Tanpa nama |
| Menyusun Jalur Teruji dan jalur siap pakai | Dari topik yang paling banyak dicari | Tanpa nama |
| Laporan untuk lembaga, sponsor, dan kreator | "1.200 orang belajar Excel bulan ini, 64% merasa terbantu" | Angka gabungan, minimal 20 orang per angka supaya tidak bisa ditebak, dan hanya data milik kita |
| Bahan ide usaha baru di Bank Ide | Topik yang banyak dicari tapi videonya sedikit adalah peluang membuat konten atau kelas | Hanya untuk kita, angka gabungan |
| Menghubungi pengguna soal layanan | Pengingat, pembaruan aplikasi, survei kepuasan | Bisa dimatikan pengguna |

## Boleh hanya dengan persetujuan khusus

Persetujuan ini ditanyakan terpisah, satu per satu, dan pengguna boleh menolak tanpa kehilangan fasilitas apa pun.

- Kabar promosi atau tawaran, termasuk dari sponsor.
- Testimoni atau kisah berhasil yang memakai nama atau foto pengguna.
- Laporan kemajuan perorangan untuk lembaga yang memesan jalur.
- Menghubungkan pengguna dengan pelatihan, lowongan kerja, atau kreator.

## Tidak boleh

- **Menjual, menyewakan, atau menukar data pribadi,** seperti nama, email, catatan, dan riwayat belajar. Ini dilarang aturan Google Play dan UU Pelindungan Data Pribadi.
- **Membuka isi catatan pribadi** tanpa izin pengguna.
- **Memakai data untuk tujuan baru** yang tidak disebut di kebijakan privasi, tanpa meminta persetujuan baru.
- **Mengirim catatan pengguna ke pihak lain** untuk melatih AI.
- **Mengumpulkan lalu menjual atau menerbitkan statistik YouTube,** misalnya angka tonton atau peringkat kanal. Aturan YouTube melarang data dari jalur resminya dikumpulkan untuk pihak lain. Laporan kita memakai penilaian pengguna kita sendiri.
- **Menyimpan data YouTube lebih dari 30 hari** tanpa diperbarui.

Batasan hukumnya, termasuk ancaman denda dan pidana, dirinci di bab berikut.

# Batasan hukum data pribadi

Bab ini merangkum UU Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi, yang berlaku penuh sejak 17 Oktober 2024, beserta Putusan MK Nomor 151/PUU-XXII/2024. **Bab ini bukan nasihat hukum.** Nomor pasal dan tenggatnya wajib dicek ulang oleh ahli hukum sebelum tayang.

## Kedudukan kita

| Peran menurut UU | Siapa | Artinya |
|---|---|---|
| Pengendali Data Pribadi | Acut, atau usaha Acut | Menentukan tujuan dan cara data diolah, dan menanggung kewajiban utama |
| Prosesor Data Pribadi | Supabase (Singapura), Anthropic (Amerika Serikat), Google | Mengolah data atas perintah kita |
| Subjek Data Pribadi | Pengguna | Pemilik data, dengan hak yang dilindungi undang-undang |

## Dasar pemrosesan

Pasal 20 mewajibkan setiap pengolahan data punya dasar yang sah. Ada enam dasar, antara lain persetujuan yang sah secara eksplisit, pelaksanaan perjanjian, dan kewajiban hukum. Pembagian untuk aplikasi kita:

| Data dan tujuannya | Dasar | Catatan |
|---|---|---|
| Akun: nama dan email dari Google | Perjanjian | Syarat layanan disetujui saat mendaftar |
| Rencana, kemajuan, catatan, pengingat | Perjanjian | Inilah layanan yang diminta pengguna |
| Teks keinginan yang dikirim ke Claude di Amerika Serikat | Perjanjian, ditambah pemberitahuan transfer ke luar negeri | Pasal 56: negara tujuan harus punya pelindungan setara, dan ini disebut jelas di kebijakan privasi |
| Penilaian video dan topik untuk memperbaiki mesin | Persetujuan eksplisit | Dicentang sendiri oleh pengguna, terpisah dari syarat layanan |
| Promosi, sponsor, testimoni, laporan untuk lembaga | Persetujuan eksplisit | Satu persetujuan untuk setiap tujuan |

Data yang benar-benar tanpa nama dan tidak bisa dikaitkan kembali ke seseorang bukan lagi data pribadi. Tapi selama data masih tersimpan bersama nomor akun, data itu tetap data pribadi.

## Syarat persetujuan yang sah

Menurut Pasal 22, persetujuan yang tidak memenuhi syarat **batal demi hukum**. Karena itu setiap persetujuan di aplikasi wajib:

- **Tertulis atau terekam.** Centang atau tombol di aplikasi sah, asalkan tercatat waktunya dan versi teks yang disetujui.
- **Terpisah untuk setiap tujuan,** dengan bahasa yang jelas dan sederhana. Persetujuan tidak boleh disembunyikan di dalam syarat yang panjang.
- **Tidak tercentang otomatis.** Pengguna sendiri yang mencentang.
- **Bisa ditarik kapan saja.** Setelah ditarik, pengolahan untuk tujuan itu dihentikan.

## Informasi yang wajib disampaikan

Pasal 21 mewajibkan kita menyampaikan informasi berikut sebelum meminta persetujuan. Semuanya dimuat di kebijakan privasi berbahasa Indonesia sederhana:

- Dasar hukum dan tujuan pengolahan.
- Jenis data dan alasan data itu dibutuhkan.
- Berapa lama data disimpan.
- Pihak yang ikut mengolah data, yaitu Supabase, Anthropic, dan Google, beserta negaranya.
- Hak-hak pengguna dan cara memakainya.

## Data pribadi spesifik

Pasal 4 menggolongkan data kesehatan, biometrik, genetika, catatan kejahatan, data anak, dan data keuangan pribadi sebagai **data spesifik** yang perlindungannya lebih ketat.

- **Kita tidak pernah meminta data spesifik.**
- **Risikonya:** pengguna bisa menulisnya sendiri di catatan atau topik, misalnya belajar mengelola diabetes atau melunasi utang.
- **Penangkalnya:** isi catatan tidak dianalisis dan tidak dibuka, topik hanya dipakai dalam angka gabungan, dan di kolom catatan ada pengingat: "Jangan menulis data kesehatan, keuangan, atau data pribadi orang lain di sini."

## Batas umur

Data anak termasuk data spesifik, dan Pasal 25 mewajibkan persetujuan orang tua atau wali. Karena itu versi 1 hanya untuk umur 18 tahun ke atas:

- Saat mendaftar, pengguna mencentang "Saya berumur 18 tahun atau lebih".
- Sasaran umur di Play Store diatur 18 tahun ke atas.
- Akun yang ketahuan milik anak dihapus.

## Hak pengguna dan tenggatnya

Permintaan akses, perbaikan, penghapusan, penarikan persetujuan, dan pembatasan pengolahan dipenuhi **paling lambat 3 × 24 jam** sejak permintaan diterima. Tombol di aplikasi memenuhinya seketika. Untuk permintaan lewat email, tenggat ini dihitung sejak email masuk.

## Masa simpan dan penghapusan

| Data | Masa simpan |
|---|---|
| Akun aktif dan catatannya | Selama akun aktif |
| Akun yang dihapus pengguna | Dihapus dari database seketika. Salinan di cadangan mingguan ikut hilang paling lama 30 hari, sebab cadangan lama dihapus bergilir |
| Akun tidak aktif | Diberi tahu pada bulan ke-23, lalu dihapus pada bulan ke-24 |
| Bukti persetujuan | Selama akun ada, ditambah waktu yang dibutuhkan untuk pembuktian hukum, sesuai saran ahli hukum |
| Data YouTube | Disegarkan atau dihapus setiap 30 hari |

## Keamanan

UU mewajibkan pengendali menjaga keamanan data. Langkah minimal kita:

- Verifikasi dua langkah di semua akun pengelola.
- Data dienkripsi saat dikirim dan saat disimpan.
- Akses database hanya untuk orang yang tercatat namanya.
- Setiap pembukaan data pribadi dicatat.
- Data pengguna tidak pernah disalin ke HP pribadi, WhatsApp, atau berkas lepas.

## Kebocoran data

Pasal 46 mewajibkan pemberitahuan tertulis **paling lambat 3 × 24 jam** kepada pengguna yang terdampak dan kepada lembaga pengawas. Isi pemberitahuannya: data apa yang terungkap, kapan dan bagaimana kejadiannya, dan apa yang sudah dilakukan. Dalam kasus tertentu, kita juga wajib mengumumkannya kepada masyarakat.

Menurut satu sumber per Agustus 2026, lembaga pengawas PDP belum terbentuk. Ahli hukum perlu menetapkan ke mana laporan dikirim selama lembaga itu belum ada.

## Penilaian dampak

Pengolahan berisiko tinggi, misalnya pemantauan yang sistematis atau berskala besar, wajib didahului penilaian dampak pelindungan data. Aplikasi kita memantau kemajuan belajar pengguna. Karena itu Acut2 menyusun penilaian dampak sederhana sebelum tayang. Biayanya nol, dan penilaian ini menjadi bukti bahwa kita berhati-hati.

## Pejabat Pelindungan Data

Pasal 53, setelah Putusan MK 151/PUU-XXII/2024, mewajibkan penunjukan pejabat pelindungan data kalau salah satu keadaan berikut terpenuhi:

- Pengolahan untuk pelayanan publik.
- Kegiatan inti yang memerlukan pemantauan teratur dan sistematis berskala besar.
- Pengolahan berskala besar atas data spesifik.

Ukuran "skala besar" belum dirinci peraturan pelaksana. Usulnya, Acut ditunjuk sebagai penanggung jawab data sejak awal, dengan email kontak yang tercantum di kebijakan privasi. Penunjukan pejabat resmi ditinjau ulang saat pengguna melewati 10.000 orang.

## Ancaman sanksi

| Pelanggaran | Ancaman |
|---|---|
| Sanksi administratif, Pasal 57 | Peringatan tertulis, penghentian sementara pengolahan, penghapusan data, dan denda sampai 2% dari pendapatan tahunan |
| Memperoleh atau mengumpulkan data orang lain secara melawan hukum, Pasal 67 ayat 1 | Penjara sampai 5 tahun dan/atau denda sampai Rp5 miliar |
| Mengungkapkan data orang lain secara melawan hukum, Pasal 67 ayat 2 | Penjara sampai 4 tahun dan/atau denda sampai Rp4 miliar |
| Menggunakan data orang lain secara melawan hukum, Pasal 67 ayat 3 | Penjara sampai 5 tahun dan/atau denda sampai Rp5 miliar |
| Dilakukan oleh badan usaha, Pasal 70 | Denda sampai 10 kali lipat, ditambah perampasan keuntungan, pembekuan usaha, pencabutan izin, atau pembubaran. Pengurus dan pemberi perintah juga bisa dipidana |

Menurut satu sumber per Agustus 2026, lembaga pengawas dan peraturan pelaksana tentang denda administratif belum terbit. Tapi **ketentuan pidana sudah bisa ditegakkan** oleh polisi dan jaksa, jadi kita tidak boleh menunggu.

## Garis merah

Sepuluh hal yang tidak pernah boleh dilakukan:

1. Menjual, menyewakan, atau menukar data pribadi.
2. Membuka isi catatan pengguna tanpa izinnya.
3. Memakai data untuk tujuan yang tidak disebut di kebijakan privasi.
4. Mengirim data pribadi ke pihak lain tanpa dasar yang sah.
5. Membuat kotak persetujuan yang tercentang otomatis.
6. Menerima pengguna di bawah 18 tahun.
7. Menyimpan data lebih lama dari masa simpannya.
8. Menunda pemberitahuan kebocoran lebih dari 3 × 24 jam.
9. Menyalin data pengguna ke HP pribadi, WhatsApp, atau berkas lepas.
10. Memberi akses akun pengelola kepada orang lain tanpa tercatat.

## Daftar periksa sebelum tayang

| No | Yang harus beres | Bukti |
|---|---|---|
| 1 | Kebijakan privasi dan syarat layanan dalam bahasa Indonesia sederhana, diperiksa ahli hukum | Berkas yang sudah diperiksa |
| 2 | Layar persetujuan terpisah, tidak tercentang otomatis, dan bukti persetujuan tersimpan | Tangkapan layar dan isi tabel bukti |
| 3 | Konfirmasi umur 18 tahun ke atas | Tangkapan layar pendaftaran |
| 4 | Pengingat di kolom catatan | Tangkapan layar |
| 5 | Tombol Unduh dataku, Perbaiki data, Tarik persetujuan, dan Hapus akun, plus halaman web untuk hapus akun | Uji coba setiap tombol |
| 6 | Perjanjian pemrosesan data dengan Supabase dan Anthropic disetujui | Salinan perjanjian |
| 7 | Verifikasi dua langkah di semua akun, dan daftar orang yang punya akses | Daftar akses |
| 8 | Catatan pembukaan data pribadi berjalan | Contoh catatan |
| 9 | Penilaian dampak pelindungan data | Berkas penilaian |
| 10 | Langkah tanggap kebocoran dan contoh surat pemberitahuan | Berkas langkah tanggap |
| 11 | Formulir Keamanan Data di Play Store sesuai kenyataan | Tangkapan layar Play Console |
| 12 | Penanggung jawab data dan email kontak tercantum | Kebijakan privasi |
| 13 | Aturan data dipasang di Supabase dan 22 uji aturan lulus di sana | Hasil uji di Supabase |

# Aturan data di dalam sistem

Batasan hukum di bab sebelumnya tidak hanya ditulis, tapi **dikunci di dalam database**. Kodenya ada di folder `aturan-data`, bersama penjelasan berbahasa mudah di `aturan-data/README.md`.

## Enam kunci

1. **Kunci baris.** Setiap baris data pribadi hanya bisa dibaca dan diubah oleh pemiliknya. Kunci ini juga berlaku untuk pemilik tabel.
2. **Pengelola tanpa akses langsung.** Peran pengelola laporan, kurator, dan bantuan tidak diberi hak apa pun pada tabel data pribadi. Mereka hanya bisa memakai tampilan angka gabungan dan fungsi resmi.
3. **Angka gabungan minimal 20 orang.** Laporan hanya menampilkan angka yang mewakili minimal 20 pengguna, dan hanya dari pengguna yang masih setuju. Kalau seseorang menarik persetujuan, datanya langsung keluar dari laporan.
4. **Catatan dibuka hanya dengan izin pengguna.** Pengguna memberi izin dari aplikasi untuk satu tiket bantuan, paling lama 72 jam. Izin untuk satu tiket tidak berlaku untuk tiket lain atau pengguna lain.
5. **Catatan akses yang tidak bisa dihapus.** Setiap pembukaan data lewat fungsi resmi dicatat, termasuk percobaan yang ditolak. Catatan ini tidak bisa diubah atau dihapus, bahkan oleh pemilik database.
6. **Masa simpan otomatis.** Akun yang tidak aktif 23 bulan diberi tahu, lalu dihapus pada bulan ke-24. Izin bantuan kedaluwarsa dihapus, dan data YouTube yang lebih dari 30 hari dibersihkan.

Satu kunci tambahan ada di fungsi server: **penyensor** menghapus email, nomor HP, NIK, dan nomor rekening dari teks keinginan sebelum dikirim ke Claude. Teks juga dipotong paling panjang 300 huruf.

## Siapa boleh apa

| Peran | Boleh | Tidak boleh |
|---|---|---|
| Pengguna | Data sendiri: lihat, ubah, unduh, hapus, tarik persetujuan, beri izin bantuan | Data orang lain dan catatan akses |
| Tamu | Jalur, judul, dan video publik | Data pribadi apa pun |
| Pengelola laporan | Angka gabungan minimal 20 orang | Tabel data pribadi dan email |
| Pengelola kurator | Jalur, judul, video, dan nilai video gabungan | Penilaian perorangan |
| Pengelola bantuan | Catatan seorang pengguna dengan izinnya, untuk satu tiket | Membuka tabel catatan langsung |
| Fungsi server | Email dari yang setuju menerima promosi, dan pekerjaan masa simpan | Pemakaian lain |

## Hasil uji

Aturan ini diuji di Postgres 16 pada 16 Oktober 2026, dengan tiruan bagian Supabase yang dibutuhkan:

| Uji | Hasil |
|---|---|
| Aturan database, misalnya pengguna tidak bisa membaca catatan orang lain, pengelola tidak bisa membuka tabel pribadi, dan catatan akses tidak bisa dihapus | 22 dari 22 lulus |
| Penyensor, misalnya email dan nomor HP disensor tapi "AutoCAD 2026 rumah tipe 36" tidak | 5 dari 5 lulus |

## Batas yang jujur

- **Pemilik proyek Supabase tetap bisa melewati semua kunci.** Peran pemilik dan kunci server punya hak di atas aturan. Karena itu keduanya hanya dipakai untuk pemeliharaan, dijaga verifikasi dua langkah, dan setiap perintahnya dicatat oleh pgaudit.
- **Log pgaudit di paket gratis hanya disimpan sebentar,** jadi log diekspor rutin bersama cadangan mingguan.
- **Penyensor tidak menangkap nama orang atau alamat rumah,** sebab polanya tidak jelas. Kolom keinginan diberi pengingat supaya tidak diisi data pribadi.
- **Uji perlu diulang di Supabase sungguhan** setelah aturan dipasang.

## Aturan pemakaian akun pemilik

- Hanya Acut yang memegang akun pemilik Supabase.
- Akun pemilik dipakai untuk pemeliharaan, bukan untuk melihat data pengguna.
- Setiap bulan Acut2 menyusun laporan dari log pgaudit dan catatan akses: siapa membuka apa, dan kapan.
- Pembukaan data pribadi tanpa alasan sah diperlakukan sebagai kebocoran, sehingga langkah tanggap 3 × 24 jam berlaku.

# Aturan yang wajib dipatuhi

## Aturan YouTube

- Video hanya diputar lewat pemutar resmi, tanpa tombol atau gambar di atasnya.
- Tidak boleh memungut bayaran untuk menonton video.
- Tidak boleh memberi hadiah karena menonton, misalnya poin yang bisa ditukar.
- Tidak boleh mengunduh video atau memutarnya saat layar mati.
- Data dari YouTube disegarkan atau dihapus setiap 30 hari.
- Judul video dan nama kanal ditampilkan, dengan tautan ke kanalnya.
- Jatah gratis harian berlaku. Tambahan jatah bisa diminta gratis lewat formulir dan pemeriksaan YouTube.

## Aturan Play Store

- Uji tertutup minimal 12 penguji selama 14 hari berturut-turut sebelum boleh tayang untuk umum.
- Tombol Hapus akun di dalam aplikasi, ditambah halaman web untuk meminta penghapusan.
- Kebijakan privasi di halaman web yang bisa dibuka umum.
- Formulir Keamanan Data diisi jujur.
- Tidak memakai izin khusus. Rancangan ini memang tidak membutuhkannya.

## Aturan lain

- **UU Pelindungan Data Pribadi:** persetujuan pengguna, data seperlunya, dan hak menghapus.
- **Umur:** versi 1 untuk 18 tahun ke atas.
- **Hak cipta:** kita tidak menyalin isi video. Ringkasan langkah ditulis sendiri.

# Teknologi dan alasannya

| Bagian | Pilihan | Alasan |
|---|---|---|
| Aplikasi HP | Expo (React Native, TypeScript) | Satu kode untuk Android, iPhone, dan website nanti |
| Pemutar video | react-native-youtube-iframe | Membungkus pemutar resmi YouTube, bisa jeda dan baca menit |
| Server, login, database | Supabase | Gratis untuk 50 ribu pengguna aktif per bulan |
| Fungsi server | Supabase Edge Functions | Gratis 500 ribu panggilan per bulan |
| Cari video | YouTube Data API | Resmi dan gratis dengan jatah harian |
| AI pemilih | Claude API (Haiku 5.5, cadangan Sonnet 5.5) | Paling murah untuk tugas berulang, dengan cadangan untuk mutu |
| Pembuatan berkas aplikasi | EAS Build gratis, atau dibangun di komputer | Jatah gratis 15 kali per bulan untuk Android |
| Halaman privasi dan hapus akun | Halaman web gratis | Syarat Play Store |

Kalau Jeumpa ternyata dibuat dengan teknologi lain, misalnya Flutter, pilihan ini bisa disesuaikan supaya pengaturan dan pengalaman dari Jeumpa terpakai ulang. Keputusan ini menunggu jawaban Acut.

**Catatan Supabase.** Proyek gratis berhenti sementara kalau tidak dipakai selama seminggu. Selama aplikasi dipakai setiap hari, ini tidak terjadi.

# Biaya dan siapa yang menanggung

Pengguna tidak membayar apa pun. Semua biaya di bawah ini ditanggung kita. Angka rupiah memakai perkiraan kurs Rp16.500 per dolar AS.

## Biaya satu rencana baru

| Pekerjaan AI | Model | Biaya |
|---|---|---|
| Memahami keinginan, sekitar 1.500 token masuk dan 500 keluar | Haiku 5.5 | Rp7 |
| Menyusun rencana, sekitar 2.000 token masuk dan 1.500 keluar | Haiku 5.5 | Rp16 |
| Memeriksa rencana yang diedit | Haiku 5.5 | Rp7 |
| Menilai kandidat untuk 8 judul | Haiku 5.5 | Rp158 |
| **Jumlah untuk topik kecil** | | **sekitar Rp190** |

Untuk topik besar seperti AI dari 0 sampai ahli, dengan sekitar 30 judul, biayanya sekitar Rp640. Biaya ini keluar bertahap per modul, dan berhenti kalau pengguna berhenti. Kalau rencana ternyata perlu disusun dengan Sonnet 5.5, biayanya naik menjadi sekitar Rp490 untuk topik kecil dan Rp1.170 untuk topik besar.

Harga yang dipakai: Haiku 5.5 US$0,10 per sejuta token masuk dan US$0,50 per sejuta token keluar; Sonnet 5.5 US$2 dan US$10.

## Tiga cara menekan biaya

1. **200 jalur siap pakai.** Topik yang paling banyak dicari, misalnya membuat konten, Excel, Canva, AI, dan menjahit, disusun sekali sebelum tayang lewat layanan Batch. Biayanya sekitar Rp40 ribu dengan Haiku, atau Rp80 ribu kalau perlu Sonnet. Setelah itu ribuan pengguna memakainya tanpa biaya AI.
2. **Dipakai ulang per rencana dan per judul.** Rencana yang sama, atau judul yang sama dengan level, bahasa, dan perangkat yang sama, tidak disusun dan dinilai ulang.
3. **Batas anggaran bulanan.** Kalau biaya AI bulan itu mencapai batas, rencana baru masuk antrean dan disusun lewat Batch pada malam hari dengan harga separuh. Pengguna diberi tahu: "Rencanamu siap besok pagi. Sambil menunggu, coba Jalur Teruji ini."

## Biaya bulanan

| Masa | Target | Cadangan | Keterangan |
|---|---|---|---|
| November, uji tertutup | Rp65 ribu | Rp105 ribu | 200 jalur siap pakai ditambah 20 penguji × 3 rencana baru. Batas siaga Rp150 ribu |
| 3 bulan setelah tayang | Rp160 ribu | Rp720 ribu | 1.000 pengguna aktif. Target kalau 60% permintaan terpenuhi jalur siap pakai. Batas anggaran Rp300 ribu |
| Supabase, YouTube API, EAS Build, Play Console | Rp0 | Rp0 | Masih dalam jatah gratis |

Biaya terburuk per pengguna dibatasi oleh jatah 3 rencana baru per bulan, yaitu sekitar Rp1.900. Rata-ratanya jauh lebih kecil, sekitar Rp160 per pengguna aktif per bulan.

Akun Play Console memakai akun Jeumpa yang sudah ada, jadi tidak ada biaya pendaftaran baru.

## Modal dan pemasukan

| | Target | Cadangan |
|---|---|---|
| Modal tunai sampai tayang | Rp100 ribu | Rp150 ribu |
| Modal tunai per bulan setelah tayang | Rp160 ribu | Rp300 ribu, sesuai batas anggaran |
| Pemasukan versi gratis | Rp0 | Rp0 |

**Kesimpulan uang yang jujur.** Versi ini tidak menghasilkan uang, dan memang tidak dimaksudkan begitu. Tujuannya membuktikan bahwa jalur kita benar-benar membantu orang belajar. Bukti itu, berupa jumlah pengguna, nilai "Membantu", dan jumlah yang menyelesaikan jalur, menjadi bahan untuk membuka fasilitas berbayar, mengajak lembaga, dan mencari sponsor. Modal tunainya kecil. Modal terbesar adalah waktu Acut.

# Cakupan versi 1 dan versi berikutnya

## Masuk versi 1

- Masuk sebagai tamu atau dengan akun Google
- Menulis keinginan dan menjawab pertanyaan pilihan
- Rencana belajar yang bisa diedit, lalu disetujui sebelum video dicari
- Mesin pemilih: jalur otomatis dan Jalur Teruji
- Layar Belajar dengan pemutar resmi, plus tombol Catat, Tanya, dan Simpulkan
- Mode Layar Lebar saat HP dimiringkan, dengan tombol bulat di tepi kanan
- Jalan pintas tombol volume dan goyang HP, kalau lolos uji
- Menit video tercatat otomatis
- Tanya dan rangkum lewat AI milik pengguna
- Penilaian "Membantu" dan "Tidak sesuai", dengan video cadangan
- Buku catatan, pencarian, dan berbagi ke WhatsApp
- Kemajuan dan syarat langkah selesai
- Pagar supaya terarah: paling banyak 2 jalur aktif, janji jadwal, pengingat, ringkasan mingguan, jatah 3 rencana baru per bulan
- 200 jalur siap pakai untuk topik populer
- Hapus akun, Unduh dataku, dan kebijakan privasi
- Cadangan otomatis mingguan ke Google Drive Acut

## Ditunda ke versi berikutnya

- **Semua fasilitas berbayar:** disimpan di bab terakhir, dibuka setelah syaratnya terpenuhi.
- **iPhone:** setelah Android stabil. Kodenya sama, tapi ada akun dan pemeriksaan Apple.
- **Website:** setelah ada 1.000 pengguna aktif. Memakai kode dan server yang sama.
- **TikTok:** TikTok tidak menyediakan pemutar yang bisa dikendalikan seperti YouTube, jadi ditunda.
- **Tombol rekam suara khusus:** sementara memakai mikrofon di papan ketik.
- **Ruang Kurator:** halaman khusus untuk memeriksa dan mengganti video. Di versi 1, pemeriksaan memakai dasbor Supabase ditambah laporan mingguan dari Acut2.
- **Lencana dan teman belajar.**

# Jadwal

| Kegiatan | Siapa | Kapan | Bukti selesai |
|---|---|---|---|
| Ngobrol dengan 1 sampai 2 orang yang membutuhkan, memakai 4 pertanyaan dari Acut2 | Acut | Paling lambat 22 Okt | Jawaban mereka, berupa tangkapan layar WA atau catatan |
| Uji mesin pemilih secara manual untuk 3 topik, membandingkan rencana dari Haiku dan Sonnet | Acut2 menyusun, Acut menilai | 19 sampai 22 Okt | 3 jalur, nilai tepat sasaran dari Acut, dan pilihan model |
| Uji pemutar resmi di HP Acut: putar, jeda, baca menit, Mode Layar Lebar, jalan pintas tombol volume dan goyang HP | Acut2 membuat, Acut mencoba | 21 sampai 23 Okt | Rekaman layar dari Acut dan catatan hasil tiap jalan pintas |
| Membuka akun Supabase dan Google Cloud, mengisi saldo Claude API sekitar Rp100 ribu | Acut, dipandu Acut2 | 24 sampai 25 Okt | Tangkapan layar ketiga akun |
| Merekrut penguji, target 20, cadangan 12 | Acut | 25 sampai 31 Okt | Daftar nama dan email Google |
| Membangun versi 1 | Acut2 | 26 Okt sampai 6 Nov | Berkas aplikasi untuk diuji |
| Menyusun 200 jalur siap pakai lewat layanan Batch | Acut2, daftar topik disetujui Acut | 1 sampai 6 Nov | Daftar topik dan jumlah jalur yang tersimpan |
| Menyusun kebijakan privasi, syarat layanan, penilaian dampak, dan langkah tanggap kebocoran, lalu diperiksa ahli hukum | Acut2 menyusun, Acut mencari pemeriksa | 1 sampai 7 Nov | Berkas yang sudah diperiksa, dan 12 butir daftar periksa terpenuhi |
| Uji internal di HP Acut dan perbaikan | Acut, Acut2 | 7 sampai 8 Nov | Daftar temuan yang sudah diperbaiki |
| Uji tertutup 14 hari | Penguji | 9 sampai 23 Nov | Jumlah penguji aktif di Play Console |
| Mengajukan akses produksi | Acut | 24 Nov | Tangkapan layar pengajuan |
| Tayang di Play Store | Google | Target 1 Des, cadangan 15 Des | Tautan Play Store |

Selama uji tertutup, Acut2 mengirim laporan mingguan berisi angka-angka di bab Ukuran Berhasil.

# Risiko dan penangkalnya

| Risiko | Penangkal |
|---|---|
| Pilihan otomatis kurang tepat sasaran | Uji manual 3 topik sebelum membangun, tombol "Tidak sesuai" dengan cadangan, dan Jalur Teruji |
| Jatah pencarian YouTube hanya cukup sekitar 15 sampai 25 rencana baru per hari | Cari video bertahap per modul, pakai ulang per judul, susun topik populer di malam hari, minta tambahan jatah setelah tayang |
| Pengguna mengedit rencana sampai urutannya kacau | AI memeriksa urutan dan memberi peringatan lembut, keputusan tetap di pengguna |
| Penguji kurang dari 12 selama 14 hari | Rekrut 20, kirim pengingat lewat WhatsApp, dan siapkan tugas kecil harian |
| Penguji berebut dengan Jeumpa | Satu orang boleh menguji dua aplikasi. Ajak penguji yang sama untuk keduanya, dan geser jadwal supaya tidak bersamaan |
| Kreator mematikan izin pemutaran di aplikasi lain | Saring sejak awal, dan otomatis ganti dengan cadangan |
| Tombol atau menu tidak sengaja menutupi video, sehingga melanggar aturan YouTube | Mode Layar Lebar menggeser video, tidak menutupinya. Setiap tampilan diperiksa sebelum tayang |
| Pemeriksa Play Store menolak | Tanpa izin khusus, kebijakan privasi lengkap, dan tombol hapus akun |
| Biaya AI ditanggung Acut tanpa pemasukan | Jalur siap pakai, jatah 3 rencana per bulan, batas anggaran Rp300 ribu per bulan, dan antrean malam |
| Penyalahgunaan oleh mesin otomatis yang membuat rencana terus-menerus | Rencana baru wajib akun Google, dengan jatah per akun |
| Gratis membuat pengguna nyasar dan tidak berkembang | Tujuh pagar di bab Supaya Gratis Tetap Terarah |
| Akun Acut dibobol sehingga catatan pengguna terbuka | Verifikasi dua langkah, akses terbatas, catatan pembukaan data, dan langkah tanggap 3 × 24 jam |
| Mesin memakai angka tonton YouTube untuk menilai video, padahal YouTube membatasi pembuatan angka turunan | Angka hanya dipakai di dalam sistem, tidak ditampilkan atau dijual. Kalau tetap dilarang, bobotnya dipindah ke penilaian pengguna dan kecocokan AI |
| Video cepat basi, terutama topik AI | Saring video lama dan segarkan data setiap 30 hari |
| Bersaing dengan Curator AI dan aplikasi asing | Bahasa Indonesia, pertanyaan pilihan, Jalur Teruji, dan penilaian pelajar Indonesia |

# Website nanti

Website dibuat setelah ada 1.000 pengguna aktif per bulan. Karena aplikasi memakai Expo, sebagian besar kode bisa dipakai ulang untuk website, dengan server dan database yang sama. Yang perlu dibeli saat itu hanya domain, sekitar Rp150 sampai 200 ribu per tahun.

Website juga membuka jalan untuk pemakaian di laptop, yang lebih nyaman untuk belajar AutoCAD, Excel, atau topik lain yang dipraktikkan di komputer.

# Keputusan yang perlu dari Acut

1. **Nama aplikasi.** Nama kerjanya Peta Belajar. Nama resmi dibutuhkan sebelum 9 November untuk halaman Play Store.
2. **Teknologi.** Setuju Expo dan Supabase, atau samakan dengan Jeumpa? Mohon kabari Jeumpa dibuat dengan apa dan kodenya disimpan di mana.
3. **Akun layanan.** Setuju membuka akun Supabase dan Google Cloud memakai email Acut. Acut2 tidak boleh masuk ke akun Acut tanpa izin.
4. **Modal biaya AI.** Setuju menanggung biaya AI: sekitar Rp100 ribu sampai tayang (batas Rp150 ribu), lalu paling banyak Rp300 ribu per bulan.
5. **Tiga topik Jalur Teruji pertama.** Usulan Acut2: "membuat konten", "AutoCAD", dan "Excel untuk kerja".
6. **Daftar penguji.** 20 orang dengan akun Google, paling lambat 31 Oktober.
7. **Pemeriksa kebijakan privasi.** Siapa ahli hukum yang bisa memeriksa kebijakan privasi sebelum 7 November?
8. **Penanggung jawab data.** Setuju Acut ditunjuk sebagai penanggung jawab data, dengan email kontak khusus?

# Riwayat ganti arah

| Tanggal | Perubahan | Alasan |
|---|---|---|
| 16 Okt | Topik pertama: Belajar Claude dari Nol | Acut bisa menilai sendiri |
| 16 Okt | Centang langkah dikunci sampai cek paham benar | 17 langkah bisa dicentang dalam 6 menit tanpa menonton |
| 16 Okt | Ditambah buku catatan per langkah | Permintaan Acut |
| 16 Okt | Bentuk: aplikasi Android, bukan website dulu | Keputusan Acut; akun Play sudah ada |
| 16 Okt | Video diputar di dalam aplikasi, bukan tombol mengambang di atas YouTube | Tanpa izin khusus, jalan juga di iPhone, menit tercatat otomatis |
| 16 Okt | Tujuan utama ditegaskan: pemilih video tepat sasaran | Penegasan Acut; fitur lain hanya pendukung |
| 16 Okt | Cara memilih: gabungan jalur teruji dan jalur otomatis | Pengguna boleh mengetik topik apa saja |
| 16 Okt | Ditambah layar Rencana belajar: judul bisa diedit, video dicari setelah Setuju, bertahap per modul | Usulan Acut; pengguna ikut menentukan isi, dan jatah YouTube lebih hemat |
| 16 Okt | Ditambah Mode Layar Lebar dan jalan pintas tombol volume dan goyang HP | Usulan Acut: menonton hampir layar penuh dengan tombol seperti iPhone, tanpa melanggar larangan YouTube menutupi video |
| 16 Okt | Model bayar per pemakaian dibahas lalu ditolak: biaya AI + 50%, kemudian + 20% | Penilaian Acut: tetap terasa mahal, dan pengguna tidak punya alasan kuat membayar |
| 16 Okt | Versi 2.0: semua fasilitas gratis untuk pengguna; rencana berbayar disimpan di bab terakhir | Keputusan Acut: manfaat dibuktikan dulu |
| 16 Okt | Ditambah tujuh pagar supaya gratis tetap terarah, dan rencana disusun dengan Haiku | Kekhawatiran Acut bahwa gratis membuat orang nyasar; biaya harus serendah mungkin |
| 16 Okt | Versi 2.1: bab Siapa Memegang Data dan Pemanfaatan Data, tombol Unduh dataku, cadangan mingguan | Pertanyaan Acut soal tempat dan pemakaian data; Acut memilih catatan dijaga dengan aturan dan akses terbatas |
| 16 Okt | Versi 2.2: bab Batasan Hukum Data Pribadi, berisi dasar pemrosesan, syarat persetujuan, data spesifik, batas umur, tenggat, sanksi, garis merah, dan daftar periksa | Permintaan Acut: pelanggaran UU PDP bisa berujung pidana, jadi batasannya harus akurat |
| 16 Okt | Versi 2.3: aturan data dikunci di database (folder aturan-data), dengan 22 uji database dan 5 uji penyensor yang lulus | Permintaan Acut: sistem tidak boleh mengizinkan akses data yang melawan hukum |

# Fasilitas berbayar untuk tahap lanjutan

Bab ini **disimpan, belum dibangun.** Isinya bahan untuk peningkatan aplikasi setelah versi gratis terbukti membantu.

## Syarat dibuka

- Minimal 1.000 pengguna aktif per bulan, dua bulan berturut-turut.
- Minimal 60% video pertama dinilai "Membantu".
- Ada permintaan nyata dari pengguna, misalnya mereka meminta AI bawaan atau rencana tambahan.

**Janji kepada pengguna:** semua yang gratis di versi 1 tetap gratis. Fasilitas berbayar hanya menambah, tidak mengambil.

## Pelajaran dari diskusi 16 Oktober

Pengguna tidak mau membayar untuk "dicarikan video", sebab mencari sendiri itu gratis. Yang mungkin mau dibayar adalah **hasil**: pendampingan sampai bisa, kemudahan, dan pengakuan. Jadi setiap fasilitas berbayar harus menjual hasil, bukan akses ke video.

## Calon fasilitas berbayar

| Fasilitas | Isi | Perkiraan harga |
|---|---|---|
| Pendampingan sampai bisa | AI bawaan untuk Tanya dan Simpulkan tanpa salin-tempel, rencana baru tanpa batas, laporan kemajuan, pengingat pintar, ekspor buku catatan ke PDF | Rp15 ribu per bulan |
| Saldo isi ulang | Untuk pengguna yang butuh rencana baru di atas jatah gratis | Rp10 ribu untuk sekitar 30 rencana topik kecil, atau 12 kalau memakai Sonnet |
| Sertifikat | Tes akhir buatan kita untuk Jalur Teruji, dengan sertifikat yang bisa dibagikan | Rp10 sampai 25 ribu per sertifikat, belum diuji |
| Jalur untuk lembaga | Dinas, balai pelatihan, sekolah vokasi, atau komunitas memesan jalur khusus dan laporan kemajuan anggotanya | Rp1 sampai 3 juta per jalur |
| Sponsor dan afiliasi | Iklan atau tautan alat yang relevan, misalnya aplikasi edit video atau toko laptop, di luar pemutar video | Sesuai kesepakatan |
| Kerja sama kreator | Kreator mempromosikan aplikasi, sebab mereka ikut untung dari penonton yang kita kirim | Bagi hasil atau promosi bersama |

## Hitungan saldo isi ulang

Hitungan dari diskusi 16 Oktober, dengan bagian sistem 20%:

| Urutan | Potongan | Sisa |
|---|---|---|
| Pengguna membayar | | Rp10.000 |
| PPN 12%, sudah termasuk harga dan dipungut Google | Rp1.071 | Rp8.929 |
| Layanan Google 15% | Rp1.339 | Rp7.589 |
| Sistem 20% | Rp1.518 | Rp6.071 untuk AI |

Dengan Haiku untuk menyusun rencana, Rp6.071 cukup untuk sekitar 30 rencana topik kecil. Dengan Sonnet, cukup untuk sekitar 12.

## Perkiraan pemasukan setelah dibuka

| | Target | Cadangan |
|---|---|---|
| Pengguna aktif per bulan | 1.000 | 400 |
| Pelanggan Pendampingan | 3% = 30 orang | 1% = 4 orang |
| Pemasukan Pendampingan per bulan, sebelum potongan | Rp450 ribu | Rp60 ribu |
| Kontrak lembaga dalam 6 bulan | 1 kontrak, Rp1 sampai 3 juta | Belum ada |

## Aturan yang wajib diingat

- **Pembayaran di aplikasi wajib lewat Google Play Billing.** Ada PPN dan potongan Google 15%, sehingga kita menerima sekitar 76% dari harga.
- **Harga minimum produk di Play Store Indonesia sekitar Rp3.000.** Angka ini dari data 2015 dan perlu dicek ulang. Akibatnya, bayar per sekali pakai yang sangat kecil tidak bisa dilakukan.
- **YouTube melarang memungut bayaran untuk menonton** dan melarang memberi hadiah karena menonton. Yang dijual harus fasilitas milik kita sendiri.
- **Langganan dan saldo perlu cara berhenti dan pengembalian dana yang jelas,** sebab keluhan tagihan adalah keluhan terbanyak di aplikasi pesaing seperti Coursiv.

# Sumber

- Halaman uji "Belajar Claude dari Nol": https://claude.ai/artifact/StYmmDuKUWzRKeuoT2rTer
- Aturan fungsi minimum pemutar YouTube: https://developers.google.com/youtube/terms/required-minimum-functionality
- Aturan pengembang YouTube API: https://developers.google.com/youtube/terms/developer-policies
- Panduan kepatuhan aturan YouTube, termasuk aturan 30 hari: https://developers.google.com/youtube/terms/developer-policies-guide
- Jatah harian YouTube Data API: https://developers.google.com/youtube/v3/getting-started
- Iklan di video sematan: https://support.google.com/youtube/answer/132596
- Syarat uji tertutup Play Console: https://support.google.com/googleplay/android-developer/answer/14151465
- Aturan hapus akun Play Store: https://9to5google.com/2023/04/05/google-play-delete-account-data/
- Jatah gratis Supabase: https://uibakery.io/blog/supabase-pricing
- Jatah gratis EAS Build: https://cadrant.ai/blog/eas-build
- Pembungkus pemutar YouTube untuk React Native: https://github.com/LonelyCpp/react-native-youtube-iframe
- Pesaing: Curator AI https://play.google.com/store/apps/details?id=in.devity.cc, DashLearn https://play.google.com/store/apps/details?id=dashlearn.ai, YouLearn https://play.google.com/store/apps/details?id=com.youlearn.main, Coursiv https://play.google.com/store/apps/details?id=io.zimran.coursiv, Pelajarin AI https://play.google.com/store/apps/details?id=com.triputra.pelajarin_ai
