---
title: "Rancangan Sistem Peta Belajar"
subtitle: "Aplikasi Android pemilih video YouTube untuk belajar apa saja"
author: "Disusun Acut2 untuk Acut"
date: "16 Oktober 2026 · Versi rancangan 1.0"
---

# Ringkasan satu halaman

**Apa ini.** Aplikasi Android yang memilihkan video YouTube gratis yang tepat sasaran untuk apa pun yang ingin dipelajari seseorang, lalu menyusunnya menjadi jalur belajar berurutan. Nama kerjanya **Peta Belajar**.

**Masalah yang diselesaikan.** Orang yang ingin belajar, misalnya membuat konten, AutoCAD, atau memakai AI, menghabiskan waktu mencari video satu per satu di YouTube. Mereka mengambang, tidak tahu harus mulai dari mana, lalu jenuh dan berhenti.

**Cara kerjanya dalam satu kalimat.** Pengguna menulis keinginannya, menjawab beberapa pertanyaan pilihan, lalu menerima jalur video berurutan dari banyak kreator, dan menontonnya di dalam aplikasi sambil mencatat, bertanya, dan menarik kesimpulan.

**Pusat tenaga.** Mesin pemilih video adalah jantung produk. Buku catatan dan menu lain hanya pendukung supaya nyaman.

**Pembeda dari aplikasi lain.**

- Jalur disusun dari banyak kreator, bukan satu video yang ditempel pengguna.
- Bahasa Indonesia didahulukan, dengan pertanyaan pilihan dan tes level.
- Jalur yang sering dipakai diperiksa manusia lalu diberi tanda **Teruji**.
- Bertanya dan merangkum memakai AI milik pengguna sendiri, jadi biaya kita hampir nol.

**Teknologi.** Aplikasi dibuat dengan Expo (React Native), server kecil memakai Supabase, video dicari lewat jalur resmi YouTube, dan pemilihan dibantu Claude. Semuanya punya jatah gratis.

**Biaya tunai.** Sekitar Rp500 untuk setiap jalur baru yang disusun mesin. Selama uji tertutup, perkiraannya Rp30 ribu sebulan, dengan batas siaga Rp75 ribu.

**Jadwal.** Versi 1 siap diuji di HP Acut pada 7 November. Uji tertutup Play Store berlangsung 9 sampai 23 November. Target tayang 1 Desember 2026, cadangan 15 Desember.

**Tiga risiko terbesar.**

1. Mutu pilihan otomatis kurang tepat, padahal itu jantung produk.
2. Jatah pencarian YouTube gratis hanya cukup untuk sekitar 12 jalur baru per hari.
3. Belum ada orang yang terbukti mau membayar.

**Yang perlu Acut putuskan.** Ada enam keputusan, dirinci di Bab 17. Yang paling mendesak adalah akun layanan dan saldo AI.

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
3. **Menerima jalur.** Dalam 10 sampai 30 detik, aplikasi menampilkan jalur berisi 6 sampai 12 langkah yang dibagi ke level Nol, Dasar, dan Lanjut. Setiap langkah punya satu video utama dan dua video cadangan.
4. **Menonton di dalam aplikasi.** Ia menekan langkah pertama. Video diputar memakai pemutar resmi YouTube di dalam aplikasi, sehingga iklan dan hak kreator tetap utuh.
5. **Mencatat sambil menonton.** Di bawah video ada tiga tombol besar: **Catat**, **Tanya**, dan **Simpulkan**. Saat salah satu ditekan, video otomatis berhenti dan menitnya tercatat sendiri.
6. **Menyimpan lalu lanjut.** Setelah menulis, ia menekan Simpan dan video lanjut dari menit yang sama.
7. **Menilai video.** Di akhir video ia memilih "Membantu" atau "Tidak sesuai". Kalau ia memilih "Tidak sesuai", video cadangan langsung tampil.
8. **Menutup langkah.** Langkah dianggap selesai kalau ia menonton minimal 70% video dan menulis satu kesimpulan. Syarat ini mencegah centang asal-asalan, pelajaran dari uji halaman Claude ketika 17 langkah bisa dicentang dalam 6 menit.

# Daftar layar

Versi 1 punya sembilan layar. Tiga layar terpenting digambar di bawah ini.

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

## 4. Menyusun jalur

Layar tunggu 10 sampai 30 detik dengan keterangan yang jujur tentang apa yang sedang dikerjakan, misalnya "Mencari video berbahasa Indonesia…" lalu "Memilih video untuk pemula…". Kalau jalur yang sama pernah disusun untuk orang lain, jalur langsung tampil tanpa menunggu.

## 5. Peta jalur

Daftar langkah yang dibagi per level. Setiap langkah menampilkan judul, durasi video, dan status selesai. Di bagian atas ada tanda **Teruji** atau **Disusun otomatis**.

## 6. Layar Belajar

Layar terpenting setelah mesin pemilih.

- **HP tegak:** video di atas, tiga tombol besar di bawahnya, lalu daftar catatan langkah itu.
- **HP miring:** video mengisi sekitar tiga perempat layar, dan tombol berjajar di kolom sempit sebelah kanan.

Tombol tidak pernah diletakkan di atas video, sebab aturan YouTube melarangnya.

## 7. Panel catatan

Muncul dari bawah saat tombol Catat, Tanya, atau Simpulkan ditekan. Video berhenti otomatis, dan menit video tercatat di pojok panel.

- **Catat:** kolom tulisan bebas.
- **Tanya:** kolom pertanyaan dengan tombol "Tanyakan ke…" yang membuka AI pilihan pengguna.
- **Simpulkan:** kolom satu kalimat "Hal terpenting dari bagian ini adalah…".

Untuk menghemat ketikan, pengguna bisa menekan ikon mikrofon di papan ketik HP-nya. Fitur ini sudah ada di Android dan tidak perlu dibangun sendiri.

## 8. Buku catatan

Semua catatan, pertanyaan, jawaban, dan kesimpulan dikelompokkan per jalur dan per langkah. Setiap catatan bertanda menit dan bisa ditekan untuk membuka video tepat di menit itu. Ada pencarian, dan buku bisa dibagikan sebagai teks ke WhatsApp.

## 9. Profil dan pengaturan

Pengaturannya: AI pilihan (Claude, ChatGPT, Gemini, atau lainnya), bahasa video, pengingat belajar, kebijakan privasi, dan tombol **Hapus akun**. Tombol Hapus akun wajib ada menurut aturan Play Store.

# Mesin pemilih video

Ini jantung aplikasi. Mesin bekerja dalam enam tahap.

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

## Tahap 3. Menyusun kerangka jalur

AI menyusun 6 sampai 12 langkah belajar berurutan yang sesuai dengan jawaban pengguna. Setiap langkah punya judul, tujuan, dan kata kunci pencarian dalam bahasa Indonesia dan Inggris.

Contoh untuk Bang Rahmat:

1. Kenal aplikasi CapCut di HP
2. Merekam video yang terang dan stabil
3. Memotong dan menyusun klip
4. Menambah teks dan musik
5. Membuat 3 detik pembuka yang menarik
6. Mengunggah ke TikTok dan memilih jam tayang

## Tahap 4. Mencari kandidat video

Untuk setiap langkah, mesin mencari video lewat jalur resmi YouTube. Bahasa Indonesia dicari lebih dulu. Bahasa Inggris hanya dipakai kalau kandidat Indonesia kurang dari lima dan pengguna mengizinkan.

**Saringan wajib.** Video yang tidak lolos langsung dibuang:

- Boleh diputar di aplikasi lain.
- Durasi 3 sampai 45 menit. Video pendek boleh menjadi pelengkap, bukan inti.
- Bukan siaran langsung.
- Untuk topik teknologi, diunggah paling lama 24 bulan terakhir.
- Ditonton minimal 1.000 kali, kecuali dari kanal resmi pembuat alat.

## Tahap 5. Menilai dan memilih

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

## Tahap 6. Menyimpan, memakai ulang, dan memperbaiki

- **Dipakai ulang.** Jalur disimpan. Pengguna berikutnya dengan topik dan jawaban yang sama langsung menerima jalur itu, tanpa biaya dan tanpa menunggu.
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

## Tanya ke AI milik pengguna

1. Pengguna menulis pertanyaannya di panel Tanya.
2. Aplikasi menyusun pesan lengkap: topik, langkah, judul video, menit, catatan terakhir, dan pertanyaannya.
3. Aplikasi membuka menu **Bagikan** bawaan Android. Pengguna memilih aplikasi ChatGPT, Gemini, Claude, atau AI lain, dan pesan langsung masuk ke kolom ketiknya.
4. Setelah AI menjawab, pengguna menyalin jawabannya lalu kembali ke Peta Belajar.
5. Aplikasi menampilkan tombol **"Tempel jawaban dari AI"**. Satu ketukan menyimpan jawaban di bawah pertanyaannya.

Cara ini membuat biaya AI kita nol untuk fitur Tanya. Kelemahannya, cara ini kurang mulus dibanding AI bawaan. AI bawaan disiapkan untuk paket berbayar di versi berikutnya.

## Simpulkan

Pengguna menulis satu kalimat kesimpulan sendiri. Ada juga tombol "Minta AI merangkum catatanku" yang bekerja seperti fitur Tanya: catatan langkah itu dikirim ke AI pilihan pengguna lewat menu Bagikan.

## Syarat langkah selesai

Langkah selesai kalau pengguna menonton minimal 70% video **dan** menulis satu kesimpulan. Untuk Jalur Teruji ada tambahan kuis satu soal.

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
| Menyusun kerangka 6 sampai 12 langkah | Claude Sonnet 5.5 | Butuh penalaran urutan belajar yang baik |
| Menilai kecocokan kandidat video | Claude Haiku 5.5 | Banyak dan berulang, harus murah |

Kalau mutu susunan langkah ternyata kurang, susunan langkah bisa dipindah ke Claude Opus 5.5 dengan biaya sekitar dua kali lipat untuk tahap itu.

# Data yang disimpan

| Data | Isi | Siapa yang bisa melihat |
|---|---|---|
| Pengguna | Nama dari akun Google, email, tanggal daftar | Pengguna sendiri |
| Profil belajar | Jawaban pertanyaan pilihan | Pengguna sendiri |
| Topik dan jalur | Keinginan yang sudah dirapikan, susunan langkah | Semua, tanpa nama pengguna |
| Video | Nomor video YouTube, judul, kanal, durasi, nilai | Semua, disegarkan setiap 30 hari |
| Penilaian | "Membantu" atau "Tidak sesuai", persen ditonton | Hanya angka gabungan yang dipakai |
| Kemajuan | Langkah selesai, menit terakhir | Pengguna sendiri |
| Catatan | Catatan, pertanyaan, jawaban, kesimpulan | Hanya pengguna sendiri |

**Prinsip privasi.**

- **Catatan sepenuhnya milik pengguna.** Acut dan Acut2 tidak membaca isi catatan. Laporan hanya memakai jumlah.
- **Hanya data yang perlu yang disimpan.** Tidak ada nomor HP, lokasi, atau kontak.
- **Hapus akun berarti semua data pribadi dihapus,** sesuai UU Pelindungan Data Pribadi dan aturan Play Store.

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
| AI pemilih | Claude API (Haiku 5.5 dan Sonnet 5.5) | Murah untuk tugas berulang, kuat untuk menyusun urutan |
| Pembuatan berkas aplikasi | EAS Build gratis, atau dibangun di komputer | Jatah gratis 15 kali per bulan untuk Android |
| Halaman privasi dan hapus akun | Halaman web gratis | Syarat Play Store |

Kalau Jeumpa ternyata dibuat dengan teknologi lain, misalnya Flutter, pilihan ini bisa disesuaikan supaya pengaturan dan pengalaman dari Jeumpa terpakai ulang. Keputusan ini menunggu jawaban Acut.

**Catatan Supabase.** Proyek gratis berhenti sementara kalau tidak dipakai selama seminggu. Selama aplikasi dipakai setiap hari, ini tidak terjadi.

# Biaya dan hitungan uang

Semua angka rupiah memakai perkiraan kurs Rp16.500 per dolar AS.

## Biaya satu jalur baru

| Pekerjaan AI | Model | Biaya |
|---|---|---|
| Memahami keinginan, sekitar 1.500 token masuk dan 500 keluar | Haiku 5.5 | Rp7 |
| Menyusun kerangka, sekitar 2.000 token masuk dan 1.500 keluar | Sonnet 5.5 | Rp314 |
| Menilai kandidat untuk 8 langkah | Haiku 5.5 | Rp158 |
| **Jumlah** | | **sekitar Rp480** |

Jalur yang dipakai ulang tidak memakan biaya AI sama sekali. Harga yang dipakai: Haiku 5.5 US$0,10 per sejuta token masuk dan US$0,50 per sejuta token keluar; Sonnet 5.5 US$2 dan US$10.

## Biaya bulanan

| Masa | Perkiraan | Keterangan |
|---|---|---|
| Uji tertutup, November | Rp30 ribu | 20 penguji × 3 jalur baru. Batas siaga Rp75 ribu |
| 3 bulan setelah tayang | Rp300 sampai 720 ribu | 1.000 pengguna aktif. Angka rendah kalau 60% jalur dipakai ulang |
| Supabase, YouTube API, EAS Build, Play Console | Rp0 | Masih dalam jatah gratis |

Akun Play Console memakai akun Jeumpa yang sudah ada, jadi tidak ada biaya pendaftaran baru.

**Modal tunai awal:** saldo Claude API. Saran pengisian pertama US$5, sekitar Rp83 ribu, cukup untuk sekitar 170 jalur baru. Pengisian ini perlu persetujuan Acut.

## Sumber pemasukan

YouTube tidak membagi apa pun kepada aplikasi yang menyematkan video. Pemasukan harus datang dari fitur milik kita sendiri.

1. **Paket Plus**, perkiraan Rp15 ribu per bulan. Isinya AI bawaan untuk Tanya dan Simpulkan tanpa salin-tempel, jalur baru tanpa batas, dan ekspor buku catatan ke PDF. Pengguna gratis mendapat 3 jalur baru per bulan dan semua Jalur Teruji.
2. **Lembaga**, misalnya dinas, balai pelatihan, sekolah vokasi, atau komunitas, yang memesan jalur khusus untuk anggotanya. Harganya belum diuji, perkiraan Rp1 sampai 3 juta per jalur.
3. **Afiliasi** alat dan kursus berbayar yang relevan dengan jalur.
4. **Kerja sama kreator.** Kreator ikut untung dari penonton yang kita kirim, sehingga mereka punya alasan untuk mempromosikan aplikasi ini.

## Hitungan 3 bulan setelah tayang

| | Target | Cadangan |
|---|---|---|
| Pengguna aktif per bulan | 1.000 | 400 |
| Pelanggan Plus | 3% = 30 orang | 1% = 4 orang |
| Pemasukan Plus per bulan | Rp450 ribu | Rp60 ribu |
| Biaya AI per bulan | Rp300 sampai 720 ribu | Rp120 sampai 290 ribu |

**Kesimpulan uang yang jujur.** Pada 1.000 pengguna, pemasukan dan biaya kira-kira impas. Untung yang berarti butuh sekitar 5.000 pengguna aktif, atau satu sampai dua kontrak lembaga. Modal tunai kecil, jadi balik modal tunai bisa terjadi pada bulan kedua setelah Paket Plus dibuka, dengan cadangan bulan keenam. Modal terbesar sebenarnya waktu Acut.

# Cakupan versi 1 dan versi berikutnya

## Masuk versi 1

- Masuk sebagai tamu atau dengan akun Google
- Menulis keinginan dan menjawab pertanyaan pilihan
- Mesin pemilih: jalur otomatis dan Jalur Teruji
- Layar Belajar dengan pemutar resmi, plus tombol Catat, Tanya, dan Simpulkan
- Menit video tercatat otomatis
- Tanya dan rangkum lewat AI milik pengguna
- Penilaian "Membantu" dan "Tidak sesuai", dengan video cadangan
- Buku catatan, pencarian, dan berbagi ke WhatsApp
- Kemajuan dan syarat langkah selesai
- Hapus akun dan kebijakan privasi

## Ditunda ke versi berikutnya

- **Paket Plus dan AI bawaan:** setelah ada 1.000 pengguna aktif.
- **iPhone:** setelah Android stabil. Kodenya sama, tapi ada akun dan pemeriksaan Apple.
- **Website:** setelah ada pemasukan pertama. Memakai kode dan server yang sama.
- **TikTok:** TikTok tidak menyediakan pemutar yang bisa dikendalikan seperti YouTube, jadi ditunda.
- **Tombol rekam suara khusus:** sementara memakai mikrofon di papan ketik.
- **Ruang Kurator:** halaman khusus untuk memeriksa dan mengganti video. Di versi 1, pemeriksaan memakai dasbor Supabase ditambah laporan mingguan dari Acut2.
- **Pengingat harian, lencana, dan teman belajar.**

# Jadwal

| Kegiatan | Siapa | Kapan | Bukti selesai |
|---|---|---|---|
| Uji mesin pemilih secara manual untuk 3 topik | Acut2 menyusun, Acut menilai | 19 sampai 22 Okt | 3 jalur dan nilai tepat sasaran dari Acut |
| Uji pemutar resmi di HP Acut: putar, jeda, baca menit | Acut2 membuat, Acut mencoba | 21 sampai 23 Okt | Rekaman layar dari Acut |
| Membuka akun Supabase dan Google Cloud, mengisi saldo Claude API | Acut, dipandu Acut2 | 24 sampai 25 Okt | Tangkapan layar ketiga akun |
| Merekrut penguji, target 20, cadangan 12 | Acut | 25 sampai 31 Okt | Daftar nama dan email Google |
| Membangun versi 1 | Acut2 | 26 Okt sampai 6 Nov | Berkas aplikasi untuk diuji |
| Uji internal di HP Acut dan perbaikan | Acut, Acut2 | 7 sampai 8 Nov | Daftar temuan yang sudah diperbaiki |
| Uji tertutup 14 hari | Penguji | 9 sampai 23 Nov | Jumlah penguji aktif di Play Console |
| Mengajukan akses produksi | Acut | 24 Nov | Tangkapan layar pengajuan |
| Tayang di Play Store | Google | Target 1 Des, cadangan 15 Des | Tautan Play Store |

Selama uji tertutup, Acut2 mengirim laporan mingguan berisi angka-angka di bab Ukuran Berhasil.

# Risiko dan penangkalnya

| Risiko | Penangkal |
|---|---|
| Pilihan otomatis kurang tepat sasaran | Uji manual 3 topik sebelum membangun, tombol "Tidak sesuai" dengan cadangan, dan Jalur Teruji |
| Jatah pencarian YouTube hanya cukup sekitar 12 jalur baru per hari | Pakai ulang jalur, susun topik populer di malam hari, minta tambahan jatah setelah tayang |
| Penguji kurang dari 12 selama 14 hari | Rekrut 20, kirim pengingat lewat WhatsApp, dan siapkan tugas kecil harian |
| Kreator mematikan izin pemutaran di aplikasi lain | Saring sejak awal, dan otomatis ganti dengan cadangan |
| Pemeriksa Play Store menolak | Tanpa izin khusus, kebijakan privasi lengkap, dan tombol hapus akun |
| Belum ada yang mau membayar | Versi 1 gratis untuk membuktikan manfaat, lalu uji Paket Plus dan tawaran ke satu lembaga |
| Video cepat basi, terutama topik AI | Saring video lama dan segarkan data setiap 30 hari |
| Bersaing dengan Curator AI dan aplikasi asing | Bahasa Indonesia, pertanyaan pilihan, Jalur Teruji, dan penilaian pelajar Indonesia |

# Website nanti

Website dibuat setelah dua syarat terpenuhi: ada 1.000 pengguna aktif dan ada pemasukan pertama. Karena aplikasi memakai Expo, sebagian besar kode bisa dipakai ulang untuk website, dengan server dan database yang sama. Yang perlu dibeli saat itu hanya domain, sekitar Rp150 sampai 200 ribu per tahun.

Website juga membuka jalan untuk pemakaian di laptop, yang lebih nyaman untuk belajar AutoCAD, Excel, atau topik lain yang dipraktikkan di komputer.

# Keputusan yang perlu dari Acut

1. **Nama aplikasi.** Nama kerjanya Peta Belajar. Nama resmi dibutuhkan sebelum 9 November untuk halaman Play Store.
2. **Teknologi.** Setuju Expo dan Supabase, atau samakan dengan Jeumpa? Mohon kabari Jeumpa dibuat dengan apa dan kodenya disimpan di mana.
3. **Akun layanan.** Setuju membuka akun Supabase dan Google Cloud memakai email Acut. Acut2 tidak boleh masuk ke akun Acut tanpa izin.
4. **Saldo AI.** Setuju mengisi saldo Claude API sekitar US$5 sebagai modal awal.
5. **Tiga topik Jalur Teruji pertama.** Usulan Acut2: "membuat konten", "AutoCAD", dan "Excel untuk kerja".
6. **Daftar penguji.** 20 orang dengan akun Google, paling lambat 31 Oktober.

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
