# Brief Desain Aplikasi Peta Belajar

Lampiran: rancangan-sistem.pdf (Rancangan Sistem Peta Belajar versi 2.3). Baca lampiran itu sebagai sumber isi, alur, dan aturan.

## R · Peran

Kamu adalah desainer produk senior untuk aplikasi Android di Indonesia. Kamu menguasai Material Design 3, terbiasa merancang untuk pengguna awam yang baru mengenal teknologi, dan punya selera visual yang modern tanpa berlebihan. Kamu memikirkan ukuran, keterbacaan, dan kenyamanan jempol sama seriusnya dengan keindahan.

## C · Konteks

**Produk.** Peta Belajar (nama kerja) adalah aplikasi Android gratis yang memilihkan video YouTube yang tepat sasaran untuk apa pun yang ingin dipelajari seseorang, lalu menyusunnya menjadi jalur belajar berurutan dari banyak kreator. Video diputar di dalam aplikasi memakai pemutar resmi YouTube. Sambil menonton, pengguna bisa mencatat, bertanya ke AI miliknya sendiri, dan menarik kesimpulan.

**Pengguna.** Orang dewasa 18 tahun ke atas di Indonesia, mulai dari Aceh. Contohnya:
- Bang Rahmat, pemilik warung kopi, belum pernah mengedit video, hanya punya HP Android.
- Kak Nur, guru honorer, sudah memakai ChatGPT dan ingin lebih rapi.
- Fadhil, mahasiswa teknik sipil, ingin mahir AutoCAD.

Banyak dari mereka memakai HP Android kelas menengah ke bawah, dengan layar sekitar 360 × 800 dp. Aplikasi yang mereka buka setiap hari adalah WhatsApp, TikTok, YouTube, dan aplikasi bank atau dompet digital. Jadi rasa "akrab seperti WhatsApp" lebih penting daripada gaya yang asing.

**Alur utama.**
1. Menulis keinginan, misalnya "bikin video promosi warung kopi".
2. Menjawab 4 sampai 5 pertanyaan pilihan, satu per layar, sekali ketuk.
3. Meninjau Rencana belajar, yaitu daftar modul dan judul. Pengguna boleh mengubah, menghapus, menambah, menggeser, atau menandai "Sudah bisa", lalu menekan "Setuju, carikan videonya".
4. Memilih jadwal belajar, misalnya Senin, Rabu, dan Jumat jam 20.00.
5. Menerima jalur video per modul.
6. Menonton di Layar Belajar. Tombol Catat, Tanya, dan Simpulkan ada di bawah video. Saat ditekan, video berhenti otomatis dan menitnya tercatat.
7. Menyimpan catatan, lalu video lanjut dari menit yang sama.
8. Menilai video: "Membantu" atau "Tidak sesuai". Kalau "Tidak sesuai", video cadangan muncul.
9. Langkah selesai kalau minimal 70% video ditonton dan satu kesimpulan ditulis.

**Kepribadian merek.** Hangat, sabar, dan jelas, seperti abang atau kakak yang mengajari dengan tenang. Modern dan rapi, tapi tidak dingin. Membuat orang merasa "aku bisa".

## T · Tugas

Rancang sistem desain dan tampilan aplikasi Peta Belajar yang **modern dan inovatif**, dengan ukuran dan kenyamanan pakai setara aplikasi Android populer seperti WhatsApp.

1. **Sistem desain:** warna untuk tema terang dan gelap, huruf, jarak, sudut, bayangan, ikon, dan komponen.
2. **Layar beresolusi tinggi** untuk semua layar di daftar bawah.
3. **Prototipe yang bisa diklik** untuk alur utama: Beranda, Pertanyaan pilihan, Rencana belajar, Setuju, Jadwal, Peta jalur, Layar Belajar, Catat, lalu Simpan dan video lanjut.
4. **Logo dan ikon aplikasi:** tiga konsep, lalu satu konsep yang paling kuat dikembangkan.

**Daftar layar.**
1. Pembuka: tiga layar perkenalan singkat, tombol "Masuk dengan Google", dan tombol "Coba sebagai tamu".
2. Persetujuan: centang umur 18 tahun, syarat layanan, dan persetujuan tambahan yang terpisah, misalnya "Bantu memperbaiki jalur tanpa nama" dan "Terima kabar promosi". Semuanya tidak tercentang otomatis.
3. Beranda: kolom "Mau belajar apa hari ini?", kartu Lanjutkan belajar, dan Jalur Teruji yang populer.
4. Pertanyaan pilihan: satu pertanyaan per layar, misalnya "Sudah sampai mana?", dengan tombol Lewati.
5. Rencana belajar: contoh "Belajar AI dari 0 sampai ahli", 8 modul dalam level Nol, Dasar, Lanjut, dan Ahli. Tampilkan juga peringatan lembut saat pengguna menghapus judul yang menjadi dasar judul lain.
6. Janji jadwal belajar: pilih hari, jam, dan target modul pertama.
7. Menyusun jalur: layar tunggu dengan keterangan jujur, misalnya "Mencari video berbahasa Indonesia…".
8. Peta jalur: modul dan judul per level, status selesai, tanda "Teruji" atau "Disusun otomatis", dan tombol Ubah rencana.
9. Layar Belajar, HP tegak.
10. Panel catatan: lembar dari bawah dengan tab Catat, Tanya, dan Simpulkan, menit tercatat otomatis, serta tombol Batal dan Simpan & lanjutkan.
11. Mode Layar Lebar, HP miring, dalam dua keadaan. Saat menonton, video mengisi sekitar 90% layar dan jalur tipis di kanan berisi satu tombol bulat yang bisa digeser naik-turun. Saat tombol ditekan, video mengecil ke kiri dan berhenti, lalu menu muncul di kanan.
12. Tanya ke AI: pilih Claude, ChatGPT, Gemini, atau AI lain, lalu menu Bagikan Android. Saat kembali ke aplikasi, muncul tombol "Tempel jawaban dari AI".
13. Buku catatan: semua catatan per jalur dan langkah, bertanda menit, dengan pencarian dan berbagi ke WhatsApp.
14. Ringkasan mingguan: kartu kemajuan yang enak dibagikan ke status WhatsApp.
15. Profil dan pengaturan: AI pilihan, bahasa video, pengingat, daftar persetujuan yang bisa ditarik, Izin bantuan 72 jam, Unduh dataku, dan Hapus akun.
16. Keadaan khusus: daftar kosong, sedang memuat, galat, tanpa internet, dan jatah 3 rencana baru per bulan habis dengan pesan "Rencanamu siap besok pagi. Sambil menunggu, coba Jalur Teruji ini."

**Bagian yang harus inovatif.**
- **Rute bertitik sebagai ciri khas.** Jadikan "peta" sebagai identitas visual: kemajuan belajar digambar sebagai jalan bertitik dengan halte untuk setiap judul, warna berbeda untuk tiap level, dan penanda "Kamu di sini". Pakai ciri ini secara konsisten, misalnya di Peta jalur, bilah kemajuan, dan ikon aplikasi.
- **Rencana belajar yang terasa ringan untuk diedit:** geser ke samping untuk Hapus atau Sudah bisa, mirip geser untuk membalas di WhatsApp, ditambah tahan lalu seret untuk menggeser urutan.
- **Panel catatan yang cepat:** sekali ketuk, video berhenti, papan ketik langsung terbuka, dan ikon mikrofon papan ketik terlihat jelas.
- **Gerak kecil yang bermakna:** getar halus saat langkah selesai, dan halte yang terisi saat kemajuan bertambah. Jangan memakai animasi yang hanya hiasan.

## O · Hasil yang diminta

1. **Halaman sistem desain:** token warna terang dan gelap dengan kode hex, skala huruf, jarak, sudut, bayangan, dan ikon.
2. **Pustaka komponen:** tombol utama, sekunder, dan teks; kolom isian; kartu; baris daftar; chip; kartu pilihan; lembar bawah; navigasi bawah; bilah atas; tombol aksi mengambang; tanda level; bilah kemajuan rute; dan dialog. Sertakan keadaan biasa, ditekan, nonaktif, dan galat.
3. **Layar resolusi tinggi** di ukuran 360 × 800 dp. Layar 3, 5, 8, 9, 10, 11, dan 14 dibuat dalam tema terang dan gelap.
4. **Prototipe alur utama** yang bisa diklik.
5. **Logo:** tiga konsep dengan alasan singkat, lalu satu konsep terpilih dalam versi warna dan putih polos. Sertakan ikon aplikasi adaptif Android dan contoh ikon di layar HP.
6. **Catatan keputusan:** satu sampai dua kalimat untuk setiap keputusan penting, misalnya alasan memilih warna utama.

## R · Aturan

**Patokan ukuran.** Ukuran mengikuti Material Design 3, standar yang juga menjadi dasar aplikasi Android populer seperti WhatsApp. Angka bertanda "sekitar" adalah patokan pengamatan dari aplikasi populer, bukan ukuran resmi WhatsApp.

| Bagian | Ukuran |
|---|---|
| Layar acuan | 360 × 800 dp, juga diperiksa di 412 × 915 dp |
| Kisi dan jarak | Kelipatan 4 dp. Margin tepi layar 16 dp. Jarak antar elemen 8, 12, 16, atau 24 dp |
| Bilah atas | Tinggi 64 dp, judul 22 sp |
| Navigasi bawah | Tinggi 80 dp, 4 tab (Beranda, Jalurku, Buku Catatan, Profil), ikon 24 dp, label 12 sp, seperti navigasi bawah WhatsApp versi baru |
| Baris daftar | Tinggi sekitar 72 dp seperti daftar chat WhatsApp, ikon atau gambar bulat 48 dp, judul 16 sp tebal, keterangan 14 sp |
| Tombol utama | Tinggi 48 sampai 52 dp, bentuk pil, teks 16 sp tebal |
| Tombol sekunder | Tinggi 48 dp, bergaris tepi |
| Target sentuh minimum | 48 × 48 dp untuk semua yang bisa ditekan |
| Tombol aksi mengambang | 56 dp, seperti tombol chat baru WhatsApp, dipakai untuk "Mau belajar apa?" |
| Kolom isian | Tinggi 56 dp, sudut 12 dp. Kolom keinginan dibuat membulat seperti kolom ketik chat WhatsApp |
| Kartu | Sudut 16 dp, isi 16 dp |
| Kartu pilihan jawaban | Tinggi minimal 56 dp, satu ketukan |
| Chip | Tinggi 32 sampai 40 dp |
| Lembar bawah | Sudut atas 28 dp, pegangan 32 × 4 dp |
| Pemutar video, HP tegak | Lebar penuh, rasio 16:9, sekitar 203 dp di layar 360 dp |
| Mode Layar Lebar | Jalur tombol di kanan 56 dp, tombol bulat 48 dp |
| Ikon | Material Symbols Rounded, 24 dp |
| Ikon aplikasi | Adaptif 108 dp dengan area aman 66 dp, berkas Play Store 512 × 512 piksel |

**Skala huruf.**

| Peran | Ukuran | Ketebalan |
|---|---|---|
| Judul layar | 22 sp | Tebal |
| Judul bagian | 18 sp | Tebal |
| Isi | 16 sp | Biasa |
| Keterangan | 14 sp | Biasa |
| Label kecil | 12 sp, tidak boleh lebih kecil | Sedang |

Tinggi baris 1,4 sampai 1,5 kali ukuran huruf. Huruf yang disarankan: **Plus Jakarta Sans**, huruf buatan Indonesia yang tersedia gratis di Google Fonts, dengan cadangan Roboto. Angka menit dan kemajuan memakai angka berlebar sama supaya tidak bergoyang.

**Warna.**
- Warna utama milik sendiri. **Jangan memakai hijau WhatsApp** seperti #25D366 atau #008069, supaya aplikasi tidak dikira milik WhatsApp. Arah yang disarankan: biru tinta yang tenang, dengan aksen kuning kunyit yang hangat. Kamu boleh mengusulkan yang lebih baik, dengan alasannya.
- Warna level tetap dan konsisten: Nol hijau daun, Dasar biru, Lanjut ungu, Ahli kuning keemasan.
- Tema gelap wajib ada dan dirancang sama seriusnya, bukan sekadar dibalik.

**Aturan YouTube, wajib dipatuhi.**
- Tidak boleh ada tombol, gambar, atau apa pun di atas video, termasuk saat layar penuh dan saat video berhenti.
- Ukuran pemutar minimal 200 × 200 piksel.
- Judul video dan nama kanal selalu tampil di dekat pemutar.
- Tombol layar penuh dan merek YouTube di pemutar tidak boleh disembunyikan atau ditiru.
- Jangan memakai segitiga play merah sebagai logo kita, sebab itu ciri khas YouTube.

**Kemudahan untuk semua orang.**
- Kontras teks minimal 4,5:1 terhadap latar.
- Tampilan tetap rapi saat ukuran huruf HP diperbesar sampai 200%.
- Status tidak boleh hanya dibedakan dengan warna. Selalu ada ikon atau tulisan.
- Setiap ikon navigasi punya label tulisan.
- Bahasa Indonesia sederhana, tanpa istilah Inggris kecuali nama merek seperti Google, YouTube, atau ChatGPT.

**Privasi yang terlihat.**
- Setiap persetujuan punya centang sendiri, tidak tercentang otomatis, dan bisa ditarik dari Profil.
- Kolom catatan menampilkan pengingat kecil: "Jangan menulis data kesehatan, keuangan, atau data pribadi orang lain di sini."
- Tombol Unduh dataku dan Hapus akun mudah ditemukan. Hapus akun memakai konfirmasi di dalam layar, bukan dialog yang membingungkan.

**Larangan lain.**
- Jangan meniru logo, gelembung chat, atau tata letak yang membuat orang mengira ini aplikasi WhatsApp atau Meta. WhatsApp hanya patokan ukuran dan rasa akrab.
- Jangan ada fitur bayar, harga, atau langganan di desain versi ini. Semua fasilitas gratis.
- Jangan memakai lorem ipsum. Pakai isi nyata dari rancangan, misalnya "bikin video promosi warung kopi", "Belajar AI dari 0 sampai ahli", dan "Memotong dan menyusun klip".
- Jangan memakai emoji sebagai ikon.
- Hindari efek berat seperti bayangan berlapis, blur besar, atau gambar latar besar, sebab banyak pengguna memakai HP murah.

**Logo.** Nama kerja: Peta Belajar. Konsep yang disarankan: jalan bertitik dengan tiga halte berwarna level, yang bisa membentuk huruf P atau jalan menuju satu titik tujuan. Logo harus tetap terbaca di ukuran 24 dp untuk notifikasi dalam versi satu warna, dan indah di ukuran 512 piksel.
