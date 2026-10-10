# forex-lab

Alat untuk menguji apakah sebuah strategi forex punya keunggulan nyata, atau
cuma kebetulan. Dibuat untuk dijalankan **sebelum** uang sungguhan terlibat.

Paket ini sengaja tidak bisa menghubungkan diri ke broker dan tidak bisa
mengirim order. Yang bisa dilakukannya hanya satu: menguji dengan jujur.

## Mengapa ini ada

Membangun robot forex itu mudah. Membangun robot yang untung itu sulit, dan
yang paling sulit adalah **mengetahui perbedaannya**. Sebagian besar robot
yang dijual orang didukung grafik backtest yang menanjak indah, dan grafik
seperti itu bisa dibuat untuk strategi yang sama sekali tidak punya
keunggulan. Dua cara paling umum backtest berbohong:

1. **Melihat masa depan.** Sinyal dihitung dari harga penutupan sebuah
   batang, lalu dieksekusi pada harga penutupan batang yang sama. Padahal
   saat harga itu diketahui, kesempatan membelinya sudah lewat.
2. **Mengabaikan biaya.** Spread, komisi, dan biaya menginap terlihat kecil
   per transaksi, tetapi pada strategi yang sering bertransaksi, biaya ini
   yang menentukan untung atau rugi.

Keduanya dicegah di sini. Yang pertama oleh mesin backtest, yang menggeser
eksekusi satu batang dan dikunci oleh tes otomatis. Yang kedua oleh simulasi
broker, yang membebankan semua biaya itu.

Masalah ketiga lebih halus dan paling sering terlewat: **uji cukup banyak
strategi, dan beberapa pasti terlihat untung karena kebetulan.** Untuk itulah
`forexlab/control.py` ada, dan itu bagian terpenting dari seluruh paket ini.

## Cara pakai

```bash
cd forex-lab
pip install -r requirements.txt

# 1. Lihat apa yang sebenarnya dilakukan leverage pada modal kecil
python3 scripts/demo_leverage.py

# 2. Uji semua strategi pada data simulasi, untuk memastikan alatnya jalan
python3 scripts/run_backtest.py --synthetic 2000 --leverage 100

# 3. Uji pada data harga sungguhan milik sendiri
python3 scripts/run_backtest.py --csv data/EURUSD_daily.csv --control 200

# 4. Lihat pengaruh leverage pada satu strategi
python3 scripts/run_backtest.py --synthetic 2000 --strategy ma_crossover --leverage-sweep

# 5. Lihat bagaimana mencoba banyak setelan menghasilkan robot palsu
python3 scripts/demo_overfitting.py

# 6. Uji di luar sampel: setel di data lama, uji di data baru
python3 scripts/run_backtest.py --synthetic 2500 --walk-forward

# Jalankan tes
python3 tests/test_forexlab.py
```

## Cara membaca hasil

Setiap laporan memuat dua pembanding yang wajib dikalahkan:

| Pembanding | Arti |
|---|---|
| `coin_flip` | Arah ditentukan lemparan koin |
| `always_long` | Beli lalu diam saja |

Strategi yang tidak mengalahkan keduanya tidak layak dipakai, apa pun
tampilan grafiknya. Dari pengujian pada data acak, `coin_flip` cukup sering
menang, dan itu memang intinya.

Kolom yang paling penting bukan keuntungan total, melainkan:

- **turun terdalam**: penurunan dari puncak ke dasar. Angka 50 persen secara
  matematis bisa pulih, tetapi hampir tidak ada orang yang sanggup
  menahannya tanpa berhenti di tengah jalan.
- **transaksi**: di bawah 30 transaksi, hasilnya belum berarti apa-apa.
- **biaya**: bandingkan dengan keuntungan kotor. Pada strategi yang sering
  bertransaksi, biaya sering lebih besar dari seluruh keuntungannya.

## Uji kendali, bagian terpenting

```bash
python3 scripts/run_backtest.py --csv data/EURUSD_daily.csv \
    --strategy ma_crossover --control 200
```

Perintah ini menjalankan strategi yang sama pada 200 rangkaian harga buatan
yang sudah dipastikan tidak punya pola, lalu melihat di mana hasil pada data
asli berdiri di antara hasil-hasil acak itu.

```
Hasil data asli     : +5.46% (turun terdalam 7.0%)
Hasil data acak     : rata-rata -0.00%, median -0.31%, terbaik +16.11%
Mengalahkan          : 81.7% dari 60 percobaan acak
Nilai p             : 0.197 (ambang 0.05)
Kesimpulan          : KEUNTUNGAN TIDAK TERBUKTI, MASIH DALAM WILAYAH KEBETULAN
```

Contoh di atas nyata, diambil dari pengujian pada data acak murni. Strategi
itu mencetak keuntungan 5,46 persen dari sesuatu yang dipastikan tidak punya
pola sama sekali. Nilai p 0,197 berarti dua dari sepuluh rangkaian harga acak
memberi hasil yang sama bagusnya, jadi tidak ada yang istimewa dari
keuntungan tersebut.

**Aturannya satu: strategi dengan nilai p di atas 0,05 tidak boleh diberi
uang sungguhan.**

## Lubang kedua: overfitting

Uji kendali menjawab "apakah ini kebetulan". Ia tidak menjawab pertanyaan
kedua yang sama berbahayanya: **apakah saya menemukan strategi ini, atau
memaksakannya dengan mencoba ratusan setelan sampai ada yang kelihatan bagus?**

```bash
python3 scripts/demo_overfitting.py
```

Peraga ini mencoba 99 kombinasi setelan rata-rata bergerak pada data harga
**acak murni**, yang dipastikan tidak punya pola apa pun.

```
LIMA SETELAN TERBAIK, cara orang memamerkan robotnya:
  cepat   lambat    keuntungan   turun terdalam   transaksi
     40       60        10.4%           14.0%         227
     40       50         2.5%           17.4%         252
      8       40         1.7%           20.3%         155

Rata-rata seluruh 99 kombinasi : -8.4%
Kombinasi yang untung          : 6.1%
```

Setelan teratas itu akan terlihat meyakinkan di tangkapan layar mana pun.
Padahal datanya acak, jadi angka itu tidak mengandung informasi apa pun.
Dari 99 percobaan, selalu ada yang kebetulan bagus.

Obatnya memisahkan data. Setelan dicari pada potongan pertama, lalu diuji
pada potongan berikutnya yang belum pernah dilihat:

```bash
python3 scripts/run_backtest.py --csv data/EURUSD_daily.csv --walk-forward
```

```
Hasil rata-rata, disetel  : +7.22%
Hasil rata-rata, diuji    : -1.32%
Penurunan mutu            : +8.54%
Hasil berangkai di luar   : -20.72%
Jendela uji yang untung   : 37.5%
Kesimpulan                : GAGAL DI LUAR SAMPEL
```

Selisih 8,54 persen antara "saat disetel" dan "saat diuji" itu bukan
kelemahan alat. Itu besarnya overfitting yang berhasil diukur.

Ada satu tanda lain yang perlu diperhatikan di rincian per jendela: kalau
nilai setelan terbaik **berpindah-pindah** setiap kali data baru masuk,
strategi itu sedang mengejar kebetulan. Setelan yang menangkap sesuatu yang
nyata cenderung stabil.

## Dua pintu yang harus dilewati

Sebelum sebuah strategi boleh diberi uang sungguhan, keduanya wajib lolos:

| Pintu | Pertanyaan | Alat | Syarat lolos |
|---|---|---|---|
| 1 | Apakah hasilnya kebetulan? | `control.py` | nilai p di bawah 0,05 |
| 2 | Apakah setelannya dipaksakan? | `validation.py` | untung di luar sampel, dan lebih dari separuh jendela untung |

Gagal di salah satunya berarti tidak lolos. Tidak ada nilai tengah di sini.

## Dari mana data harga

Jaringan di lingkungan ini memblokir penyedia data keuangan, jadi berkas CSV
perlu diunduh sendiri lalu diletakkan di `data/`. Sumber gratis yang biasa
dipakai antara lain Dukascopy, HistData, dan ekspor dari platform MetaTrader
milik broker sendiri.

Syarat berkasnya ringan: satu kolom waktu dengan nama apa pun yang lazim
(`date`, `datetime`, `time`, `timestamp`, atau `Gmt time`), dan satu kolom
`close`. Kolom `open`, `high`, dan `low` bersifat pilihan, tetapi membuat
pengujian stop loss jauh lebih akurat, jadi sebaiknya disertakan.

Minimal 2 tahun data harian. Di bawah itu, jumlah transaksinya terlalu
sedikit untuk disimpulkan apa pun.

## Isi paket

| Berkas | Isi |
|---|---|
| `forexlab/broker.py` | Simulasi broker: spread, margin, margin call, stop out, swap |
| `forexlab/risk.py` | Batas risiko yang dikunci di kode, menentukan ukuran posisi |
| `forexlab/backtest.py` | Mesin backtest, dengan pergeseran eksekusi satu batang |
| `forexlab/strategies.py` | Strategi dan pembanding wajib |
| `forexlab/control.py` | Uji permutasi, pintu pertama |
| `forexlab/validation.py` | Uji di luar sampel dan deteksi overfitting, pintu kedua |
| `forexlab/metrics.py` | Penurunan terdalam, harapan keuntungan, Sharpe |
| `forexlab/data.py` | Pembaca CSV dan pembuat data acak |
| `tests/` | 33 tes, termasuk dua yang memaku jarak eksekusi tepat satu batang |

## Batas kemampuan alat ini

Perlu disebutkan terus terang:

- Mata uang akun dianggap sama dengan mata uang kedua pasangan, misalnya
  akun dolar untuk EURUSD. Untuk pasangan lain, laba-rugi perlu dikonversi
  dan angkanya akan bergeser.
- Slippage di luar spread tidak dimodelkan, dan pada pasar nyata slippage
  selalu memperburuk hasil. Jadi angka di sini adalah **batas optimis**.
- Lompatan harga akhir pekan tidak ada di data harian, padahal itu salah satu
  cara akun berleverage tinggi berakhir dengan saldo minus.
- Hanya satu posisi terbuka sekaligus.

Semua batasan di atas mengarah ke satu arah yang sama: **hasil sungguhan akan
lebih buruk dari hasil di sini, tidak pernah lebih baik.**

## Peran API Claude di sini

Belum ada, dan itu disengaja. Keputusan beli dan jual di paket ini
sepenuhnya ditentukan aturan yang bisa diuji ulang dan memberi hasil sama
setiap kali dijalankan. Model bahasa tidak bisa memberi sifat itu, dan tanpa
sifat itu tidak ada yang bisa diuji.

Tempat API Claude benar-benar berguna, nanti, adalah pekerjaan yang memang
bahasa: merangkum berita dan rilis data ekonomi, mengkritik strategi,
mencari kesalahan di kode, dan menulis laporan mingguan dari catatan
transaksi. Semua itu di luar jalur keputusan, dan karena itu tidak merusak
sifat dapat diujinya.
