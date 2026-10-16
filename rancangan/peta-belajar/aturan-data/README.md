# Aturan Data Peta Belajar

Folder ini berisi aturan data pribadi yang **dikunci di dalam database**, bukan hanya ditulis di dokumen. Dasarnya UU Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi. Rangkumannya ada di bab Batasan Hukum Data Pribadi dalam `../rancangan-sistem.md`.

## Isi folder

| Berkas | Isi |
|---|---|
| `supabase/migrations/20261016000001_aturan_data.sql` | Peran, skema, kunci baris, fungsi resmi, catatan akses, laporan gabungan, dan masa simpan |
| `supabase/migrations/20261016000002_jadwal_dan_pgaudit.sql` | Khusus Supabase: jadwal otomatis dan pencatatan semua perintah pemilik proyek |
| `supabase/functions/_shared/sensor.ts` | Penyensor email, nomor HP, NIK, dan nomor rekening sebelum teks dikirim ke Claude |
| `uji/uji_aturan.sql` | 22 uji aturan database |
| `uji/sensor.test.ts` | 5 uji penyensor |
| `uji/jalankan.sh` | Menjalankan uji database di Postgres sementara |

## Siapa boleh apa

| Peran | Boleh | Tidak boleh |
|---|---|---|
| Pengguna | Melihat, mengubah, mengunduh, dan menghapus datanya sendiri; menarik persetujuan; memberi izin bantuan 72 jam | Melihat data orang lain, membaca catatan akses |
| Tamu | Membaca jalur, judul, dan video publik | Menyentuh data pribadi apa pun |
| Pengelola laporan | Membaca angka gabungan, minimal 20 orang per angka | Membuka tabel data pribadi, mengambil email |
| Pengelola kurator | Mengelola jalur, judul, dan video; membaca nilai video gabungan | Membaca penilaian perorangan |
| Pengelola bantuan | Membaca catatan seorang pengguna, hanya dengan izin pengguna itu untuk satu tiket, paling lama 72 jam | Membuka tabel catatan secara langsung |
| Fungsi server | Mengambil email hanya dari yang setuju menerima promosi, menjalankan masa simpan | Tidak ada pengecualian lain |

Setiap pembukaan data lewat fungsi resmi dicatat di `audit.akses_data`, **termasuk percobaan yang ditolak**. Catatan itu tidak bisa diubah atau dihapus, bahkan oleh pemilik database.

## Hasil uji

Diuji di Postgres 16 pada 16 Oktober 2026:

- **22 dari 22 uji aturan database lulus.**
- **5 dari 5 uji penyensor lulus.**

Cara menjalankan ulang:

```bash
PGHOST=/tmp PGPORT=54329 PGUSER=postgres bash uji/jalankan.sh
node --experimental-strip-types --test uji/sensor.test.ts
```

## Batas yang jujur

1. **Pemilik proyek Supabase tetap bisa melewati semua kunci.** Peran `postgres` dan kunci `service_role` punya hak di atas aturan. Karena itu keduanya hanya dipakai untuk pemeliharaan, dijaga verifikasi dua langkah, dan setiap perintahnya dicatat oleh pgaudit.
2. **Log pgaudit di paket gratis Supabase hanya disimpan sebentar.** Log perlu diekspor rutin bersama cadangan mingguan.
3. **Penyensor hanya menangkap pola yang jelas,** yaitu email, nomor HP, NIK, dan deretan angka panjang. Nama orang atau alamat rumah tidak tertangkap. Karena itu kolom keinginan dibatasi 300 huruf dan diberi pengingat.
4. **Uji dijalankan di Postgres biasa dengan tiruan bagian Supabase.** Setelah dipasang di Supabase sungguhan, uji yang sama wajib dijalankan ulang.

## Aturan pemakaian akun pemilik

- Hanya Acut yang memegang akun pemilik Supabase.
- Akun pemilik dipakai untuk pemeliharaan, bukan untuk melihat data pengguna.
- Setiap bulan Acut2 menyusun laporan dari log pgaudit dan `audit.akses_data`: siapa membuka apa dan kapan.
- Kalau ada pembukaan data pribadi tanpa alasan yang sah, perlakukan sebagai kebocoran: langkah tanggap 3 × 24 jam berlaku.
