"""Pemeriksa mutu data harga sebelum dipakai menguji strategi.

Backtest yang paling teliti pun tidak berguna kalau datanya cacat, dan data
harga saham Indonesia yang diunduh dari berbagai tempat sering cacat dengan
cara yang tidak kelihatan. Modul ini memeriksanya lebih dulu.

Tiga cacat yang paling berbahaya, berurutan dari yang paling sering:

1. Pemecahan saham yang belum disesuaikan. Ketika satu lembar saham dipecah
   menjadi lima, harganya turun menjadi seperlima dalam satu malam, padahal
   nilai kepemilikan pemegang saham sama sekali tidak berubah. Kalau data
   belum disesuaikan, backtest membaca itu sebagai kejatuhan 80 persen yang
   tidak pernah terjadi. BBCA pernah mengalami ini.

2. Harga nol, kosong, atau negatif. Biasanya berasal dari hari bursa tutup
   yang tetap ikut terunduh. Satu nilai nol saja bisa membuat perhitungan
   return menjadi tak terhingga.

3. Tanggal ganda atau urutan terbalik. Membuat satu hari dihitung dua kali,
   atau membuat strategi seolah melihat masa depan.

Pemeriksaan ini tidak memperbaiki data secara diam-diam. Cacat yang
ditemukan dilaporkan, dan keputusan memperbaikinya diserahkan kepada
pengguna, karena memperbaiki diam-diam adalah cara lain backtest berbohong.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

#: Rasio pemecahan saham yang lazim di bursa. Nilai 5.0 berarti satu lembar
#: dipecah menjadi lima, sehingga harga menjadi seperlima.
RASIO_PEMECAHAN_LAZIM: tuple[float, ...] = (2.0, 2.5, 4.0, 5.0, 8.0, 10.0, 20.0, 50.0)

#: Pergerakan harian di luar rentang ini dianggap mencurigakan untuk saham
#: likuid. Batas auto reject di Bursa Efek Indonesia umumnya di bawah 35
#: persen, jadi lompatan di luar rentang ini hampir pasti cacat data, bukan
#: pergerakan pasar.
BATAS_GERAK_WAJAR = 0.40


@dataclass
class DugaanPemecahan:
    tanggal: pd.Timestamp
    harga_sebelum: float
    harga_sesudah: float
    rasio: float
    rasio_terdekat: float

    def keterangan(self) -> str:
        arah = "pemecahan" if self.rasio > 1 else "penggabungan"
        return (
            f"{self.tanggal.date()}: harga {self.harga_sebelum:,.0f} menjadi "
            f"{self.harga_sesudah:,.0f}, rasio 1:{self.rasio_terdekat:,.0f} "
            f"({arah} saham)"
        )


@dataclass
class LaporanMutu:
    baris: int
    tanggal_awal: pd.Timestamp | None
    tanggal_akhir: pd.Timestamp | None
    kolom: list[str]
    harga_tidak_sah: int
    tanggal_ganda: int
    urutan_terbalik: bool
    hari_bursa_per_tahun: float
    lompatan_mencurigakan: int
    dugaan_pemecahan: list[DugaanPemecahan] = field(default_factory=list)
    catatan: list[str] = field(default_factory=list)

    @property
    def tahun_data(self) -> float:
        if self.tanggal_awal is None or self.tanggal_akhir is None:
            return 0.0
        return (self.tanggal_akhir - self.tanggal_awal).days / 365.25

    @property
    def layak_pakai(self) -> bool:
        """Benar hanya bila tidak ada cacat yang membuat hasil backtest bohong."""
        return (
            self.harga_tidak_sah == 0
            and self.tanggal_ganda == 0
            and not self.urutan_terbalik
            and not self.dugaan_pemecahan
            and self.tahun_data >= 2.0
        )

    def laporan_teks(self) -> str:
        baris = [
            f"Jumlah baris        : {self.baris:,}",
            f"Rentang tanggal     : "
            + (
                f"{self.tanggal_awal.date()} sampai {self.tanggal_akhir.date()} "
                f"({self.tahun_data:.1f} tahun)"
                if self.tanggal_awal is not None
                else "tidak terbaca"
            ),
            f"Kolom tersedia      : {', '.join(self.kolom)}",
            f"Hari bursa per tahun: {self.hari_bursa_per_tahun:.0f} "
            f"(normalnya sekitar 240)",
            "",
            f"Harga tidak sah     : {self.harga_tidak_sah}"
            + ("" if self.harga_tidak_sah == 0 else "  <-- MASALAH"),
            f"Tanggal ganda       : {self.tanggal_ganda}"
            + ("" if self.tanggal_ganda == 0 else "  <-- MASALAH"),
            f"Urutan terbalik     : {'ya  <-- MASALAH' if self.urutan_terbalik else 'tidak'}",
            f"Lompatan di luar {BATAS_GERAK_WAJAR:.0%}: {self.lompatan_mencurigakan}",
            f"Dugaan pemecahan    : {len(self.dugaan_pemecahan)}"
            + ("" if not self.dugaan_pemecahan else "  <-- MASALAH SERIUS"),
        ]
        for dugaan in self.dugaan_pemecahan:
            baris.append(f"    {dugaan.keterangan()}")
        if self.catatan:
            baris.append("")
            for catatan in self.catatan:
                baris.append(f"Catatan: {catatan}")
        baris.append("")
        baris.append(
            "Kesimpulan          : "
            + ("DATA LAYAK DIPAKAI" if self.layak_pakai else "DATA BELUM LAYAK DIPAKAI")
        )
        return "\n".join(baris)


def _rasio_terdekat(rasio: float) -> float | None:
    """Cari rasio pemecahan lazim yang paling mendekati, bila ada."""
    kandidat = rasio if rasio > 1 else 1.0 / rasio
    for lazim in RASIO_PEMECAHAN_LAZIM:
        # Toleransi 6 persen: harga pada hari pemecahan tetap bergerak sedikit.
        if abs(kandidat - lazim) / lazim < 0.06:
            return lazim
    return None


def deteksi_pemecahan(prices: pd.DataFrame) -> list[DugaanPemecahan]:
    """Cari lompatan harga satu malam yang bentuknya seperti pemecahan saham.

    Pemecahan saham meninggalkan jejak yang khas: harga berubah mendekati
    pecahan bulat seperti setengah, seperlima, atau sepersepuluh, dalam satu
    malam. Pergerakan pasar biasa tidak pernah sedekat itu dengan pecahan
    bulat, dan di Bursa Efek Indonesia juga dibatasi auto reject.
    """
    close = prices["close"].to_numpy(dtype=float)
    if len(close) < 2:
        return []

    hasil: list[DugaanPemecahan] = []
    for i in range(1, len(close)):
        sebelum, sesudah = close[i - 1], close[i]
        if sebelum <= 0 or sesudah <= 0:
            continue
        rasio = sebelum / sesudah
        if 1 / (1 + BATAS_GERAK_WAJAR) < rasio < 1 + BATAS_GERAK_WAJAR:
            continue
        terdekat = _rasio_terdekat(rasio)
        if terdekat is None:
            continue
        hasil.append(
            DugaanPemecahan(
                tanggal=prices.index[i],
                harga_sebelum=sebelum,
                harga_sesudah=sesudah,
                rasio=rasio,
                rasio_terdekat=terdekat,
            )
        )
    return hasil


def periksa(prices: pd.DataFrame) -> LaporanMutu:
    """Periksa seluruh berkas harga dan laporkan setiap cacat yang ditemukan."""
    catatan: list[str] = []
    close = prices["close"]

    harga_tidak_sah = int((~np.isfinite(close)).sum() + (close <= 0).sum())
    tanggal_ganda = int(prices.index.duplicated().sum())
    urutan_terbalik = not prices.index.is_monotonic_increasing

    if len(prices) >= 2:
        rentang_hari = (prices.index[-1] - prices.index[0]).days
        hari_per_tahun = len(prices) / (rentang_hari / 365.25) if rentang_hari > 0 else 0.0
    else:
        hari_per_tahun = 0.0

    gerak = close.pct_change().abs()
    lompatan = int((gerak > BATAS_GERAK_WAJAR).sum())
    dugaan = deteksi_pemecahan(prices) if harga_tidak_sah == 0 else []

    if hari_per_tahun > 300:
        catatan.append(
            "Lebih dari 300 baris per tahun. Kemungkinan akhir pekan atau hari "
            "libur bursa ikut terunduh, atau datanya bukan harian."
        )
    elif 0 < hari_per_tahun < 200:
        catatan.append(
            "Kurang dari 200 baris per tahun. Kemungkinan ada hari bursa yang "
            "hilang dari berkas."
        )

    if "high" not in prices.columns or "low" not in prices.columns:
        catatan.append(
            "Kolom tertinggi dan terendah tidak ada. Stop loss masih bisa diuji, "
            "tapi hasilnya kurang akurat karena rentang harga harian diperkirakan."
        )

    if len(prices) >= 2 and (prices.index[-1] - prices.index[0]).days < 730:
        catatan.append(
            "Data kurang dari 2 tahun. Jumlah transaksinya akan terlalu sedikit "
            "untuk menyimpulkan apa pun."
        )

    if lompatan > 0 and not dugaan:
        catatan.append(
            f"Ada {lompatan} lompatan harga di luar {BATAS_GERAK_WAJAR:.0%} yang "
            "bentuknya bukan pemecahan saham. Periksa tanggal-tanggal itu secara "
            "manual sebelum melanjutkan."
        )

    return LaporanMutu(
        baris=len(prices),
        tanggal_awal=prices.index[0] if len(prices) else None,
        tanggal_akhir=prices.index[-1] if len(prices) else None,
        kolom=list(prices.columns),
        harga_tidak_sah=harga_tidak_sah,
        tanggal_ganda=tanggal_ganda,
        urutan_terbalik=urutan_terbalik,
        hari_bursa_per_tahun=hari_per_tahun,
        lompatan_mencurigakan=lompatan,
        dugaan_pemecahan=dugaan,
        catatan=catatan,
    )


def sesuaikan_pemecahan(
    prices: pd.DataFrame, dugaan: list[DugaanPemecahan]
) -> pd.DataFrame:
    """Sesuaikan harga lama agar setara dengan harga sesudah pemecahan.

    Harga sebelum tanggal pemecahan dibagi rasionya, sehingga seluruh seri
    berada pada skala yang sama. Volume tidak disesuaikan, karena tidak
    dipakai dalam perhitungan apa pun di proyek ini.

    Fungsi ini tidak pernah dipanggil sendiri oleh pemeriksa. Pengguna yang
    memutuskan memakainya, setelah membaca laporan dan memastikan dugaannya
    benar-benar pemecahan saham, bukan kejatuhan harga yang sungguhan.
    """
    if not dugaan:
        return prices.copy()

    hasil = prices.copy()
    kolom_harga = [k for k in ("open", "high", "low", "close") if k in hasil.columns]

    for satu in dugaan:
        sebelum = hasil.index < satu.tanggal
        hasil.loc[sebelum, kolom_harga] = (
            hasil.loc[sebelum, kolom_harga] / satu.rasio_terdekat
        )
    return hasil
