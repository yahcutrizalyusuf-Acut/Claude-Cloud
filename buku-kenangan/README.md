# Buku Kenangan Bersama (purwarupa tahap 1)

Website PWA untuk mengumpulkan ucapan, doa, foto, dan suara dari banyak orang untuk satu orang istimewa (pensiun, perpisahan guru, rekan pindah tugas, lepas haji, pernikahan). Penulis cukup membuka satu tautan dari grup WA: tidak perlu daftar, tidak perlu memasang aplikasi, dan bisa dari iPhone maupun Android.

## Cara pakai

```bash
cd buku-kenangan
cp .env.example .env   # ANTHROPIC_API_KEY boleh kosong; fitur bantu tulis AI jadi nonaktif
npm install
npm run dev            # development, http://localhost:3000
npm test               # build + tes alur
npm run build && npm start   # production
```

## Halaman

| Alamat | Untuk | Isi |
|---|---|---|
| `/` | Pembuat | Buat buku baru |
| `/kelola/:id` | Pembuat | Dasbor: jumlah ucapan, sebar ke WA, sembunyikan ucapan, kunci, buka buku |
| `/b/:id` | Penulis | Tulis ucapan, foto (maks. 3), suara (maks. 60 detik), bantu tulis AI |
| `/buku/:id` | Penerima | Momen buka buku dan halaman buku yang bisa digeser |

## API

| Method | Endpoint | Keterangan |
|---|---|---|
| POST | `/api/buku` | Buat buku, balas `{ id, kunciAdmin }` |
| GET | `/api/buku/:id` | Info buku. Isi ucapan hanya muncul kalau mode rahasia mati atau buku sudah dibuka |
| POST | `/api/buku/:id/ucapan` | Kirim ucapan (foto dan suara dalam bentuk data URL) |
| POST | `/api/buku/:id/draf` | Draf ucapan dari Claude (maks. 15 per jam per alamat IP) |
| GET | `/api/kelola/:id` | Semua ucapan (header `X-Kunci`) |
| PATCH | `/api/kelola/:id/ucapan/:uid` | Sembunyikan/tampilkan ucapan (header `X-Kunci`) |
| POST | `/api/kelola/:id/status` | `terbuka` / `dikunci` / `dibuka` (header `X-Kunci`) |

## Batasan purwarupa

- **Masuk akun pembuat** masih memakai *tautan kelola rahasia* (`/kelola/:id#k=…`), belum akun Google/email. Login Google perlu mendaftarkan aplikasi atas nama Acut.
- **Data** disimpan di satu file JSON dan folder `data/media`. Cukup untuk uji coba beberapa acara; perlu basis data dan penyimpanan file sungguhan sebelum dipakai luas. Kalau dipasang di layanan yang disknya hilang setiap kali deploy, pasang volume tetap untuk `DATA_DIR`.
- **Kode QR suara, patungan, dan cetak** termasuk tahap 2.
