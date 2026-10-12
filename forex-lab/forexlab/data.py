"""Sumber data harga untuk forex-lab.

Dua sumber:
  1. CSV asli yang diunduh pengguna (load_csv)
  2. Data buatan untuk uji kendali (synthetic_*), dipakai untuk membuktikan
     apakah sebuah strategi punya keunggulan nyata atau cuma kebetulan.

Semua fungsi mengembalikan pandas.DataFrame dengan indeks waktu dan
minimal satu kolom: "close". Kolom open/high/low diisi bila tersedia.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

REQUIRED_COLUMN = "close"

#: Nama kolom yang dipakai berbagai penyedia data, dipetakan ke nama baku.
#: Sumber Indonesia memakai istilah bahasa Indonesia, sumber asing memakai
#: bahasa Inggris, dan investing.com memakai "Terakhir" untuk harga penutupan.
#: Nama kolom harga penutupan yang sudah disesuaikan dengan aksi korporasi.
#: Kolom ini memuat pengaruh dividen dan pemecahan saham, sehingga
#: mencerminkan hasil yang benar-benar diterima pemegang saham.
ALIAS_HARGA_DISESUAIKAN: frozenset[str] = frozenset(
    {"adj close", "adj. close", "adjusted close", "close adjusted"}
)

ALIAS_KOLOM: dict[str, str] = {
    "close": "close",
    "close price": "close",
    "closing price": "close",
    "adj close": "close",
    "adj. close": "close",
    "adjusted close": "close",
    "last": "close",
    "terakhir": "close",
    "penutupan": "close",
    "harga penutupan": "close",
    "tutup": "close",
    "open": "open",
    "pembukaan": "open",
    "buka": "open",
    "high": "high",
    "tertinggi": "high",
    "low": "low",
    "terendah": "low",
    "volume": "volume",
    "vol": "volume",
    "vol.": "volume",
    "volume saham": "volume",
}

_CANDIDATE_TIME_COLUMNS = (
    "datetime",
    "date",
    "tanggal",
    "time",
    "waktu",
    "timestamp",
    "gmt time",
)

#: Susunan angka yang memakai titik sebagai pemisah ribuan, misalnya
#: "7.350" atau "1.234.567". Setiap kelompok sesudah titik tepat tiga angka.
_POLA_RIBUAN_TITIK = re.compile(r"^\d{1,3}(\.\d{3})+$")

#: Akhiran ribuan yang dipakai investing.com di kolom volume.
_PENGALI_AKHIRAN: dict[str, float] = {"k": 1e3, "m": 1e6, "b": 1e9, "t": 1e12}


def bersihkan_angka(nilai, titik_ribuan: bool | None = None) -> float:
    """Ubah teks angka dari berbagai format penyedia data menjadi bilangan.

    Yang ditangani: pemisah ribuan koma seperti "7,350", pemisah ribuan titik
    gaya Indonesia seperti "7.350", akhiran ribuan seperti "12.5M", tanda
    persen, dan kurung untuk bilangan negatif.

    Format Indonesia dan format Inggris saling bertabrakan: "7.350" berarti
    tujuh ribu tiga ratus lima puluh di Indonesia, tetapi tujuh koma tiga
    lima nol di Inggris. Aturan yang dipakai: titik dianggap pemisah ribuan
    hanya bila kelompok terakhirnya tepat tiga angka dan tidak ada koma di
    dalam teksnya. Harga saham Indonesia selalu bilangan bulat rupiah,
    sehingga aturan ini aman untuk data harga.

    Argumen titik_ribuan memaksa penafsiran, dan itulah yang dipakai oleh
    bersihkan_kolom setelah memeriksa seluruh kolom. Memutuskan dari satu
    nilai saja tidak selalu bisa benar.
    """
    if isinstance(nilai, bool):
        return float("nan")
    if isinstance(nilai, (int, float)):
        return float(nilai)

    teks = str(nilai).strip()
    if not teks or teks.lower() in ("-", "nan", "none", "null", "n/a", "#n/a"):
        return float("nan")

    negatif = teks.startswith("(") and teks.endswith(")")
    teks = teks.strip("()").replace("%", "").replace(" ", "").replace("\xa0", "")

    pengali = 1.0
    if teks and teks[-1].lower() in _PENGALI_AKHIRAN:
        pengali = _PENGALI_AKHIRAN[teks[-1].lower()]
        teks = teks[:-1]

    if "," in teks:
        # Ada koma: koma adalah pemisah ribuan, titik adalah titik desimal.
        teks = teks.replace(",", "")
    elif teks.count(".") >= 1:
        # Titik hanya boleh dibuang bila susunannya benar-benar pola ribuan,
        # yaitu setiap kelompok sesudah titik tepat tiga angka. Petunjuk pasar
        # memutuskan kasus yang susunannya memang bisa dibaca dua cara,
        # seperti "7.400"; ia tidak boleh memaksa pada "5306.2", yang hanya
        # punya satu angka di kelompok terakhir dan sudah pasti desimal.
        pola_ribuan = bool(_POLA_RIBUAN_TITIK.match(teks))
        if titik_ribuan is None:
            titik_ribuan = pola_ribuan
        if titik_ribuan and pola_ribuan:
            teks = teks.replace(".", "")

    try:
        hasil = float(teks) * pengali
    except ValueError:
        return float("nan")
    return -hasil if negatif else hasil



def _titik_adalah_pemisah_ribuan(nilai_teks: list[str]) -> bool:
    """Tentukan sekali untuk seluruh kolom: titik itu ribuan atau desimal?

    Keputusan ini tidak bisa diambil per nilai. Teks "7.350" berarti tujuh
    ribu tiga ratus lima puluh pada data saham Indonesia, tetapi tujuh koma
    tiga lima nol pada data forex. Satu nilai saja tidak cukup untuk
    membedakannya, sementara seluruh kolom hampir selalu cukup.

    Aturannya berurutan:

    1. Ada koma di kolom ini berarti gaya Inggris: koma pemisah ribuan, titik
       pemisah desimal. Selesai.
    2. Ada nilai bertitik yang kelompok terakhirnya bukan tiga angka, seperti
       "1.1050", berarti titiknya pemisah desimal. Pola ribuan tidak pernah
       menghasilkan kelompok selain tiga.
    3. Sisanya pemisah ribuan.

    Satu kasus tetap tidak bisa dipastikan dari isi kolomnya: "7.400" bisa
    berarti Rp 7.400 pada saham Indonesia, atau 7,4 pada pasangan mata uang.
    Keduanya identik susunannya. Untuk kasus itu, pasarnya harus disebutkan
    lewat argumen market di load_csv, dan fungsi ini tidak dipakai menebak.
    """
    bertitik = [t for t in nilai_teks if "." in t]
    if not bertitik:
        return False
    if any("," in t for t in nilai_teks):
        return False
    if not all(_POLA_RIBUAN_TITIK.match(t) for t in bertitik):
        return False
    return True


def bersihkan_kolom(kolom: pd.Series, titik_ribuan: bool | None = None) -> pd.Series:
    """Bersihkan satu kolom angka dengan satu keputusan untuk seluruh kolom.

    Bila titik_ribuan diberikan, nilai itu dipakai apa adanya. Bila tidak,
    konvensinya ditebak dari seluruh isi kolom.
    """
    if pd.api.types.is_numeric_dtype(kolom):
        return kolom.astype(float)

    # Nilai kosong harus diubah menjadi teks kosong lebih dulu. Pada berkas
    # Yahoo Finance, baris dividen punya kolom lebih sedikit daripada
    # judulnya, sehingga sel yang hilang terisi nilai kosong, bukan teks,
    # dan pemrosesan teks akan gagal di situ.
    teks = kolom.fillna("").astype(str).str.strip()
    kandidat = [
        t.strip("()").replace("%", "").replace(" ", "").replace("\xa0", "").rstrip("kKmMbBtT")
        for t in teks
        if t and t.lower() not in ("-", "nan", "none", "null", "n/a", "#n/a")
    ]
    ribuan = (
        titik_ribuan
        if titik_ribuan is not None
        else _titik_adalah_pemisah_ribuan(kandidat)
    )
    return teks.map(lambda nilai: bersihkan_angka(nilai, titik_ribuan=ribuan)).astype(float)


def load_csv(
    path: str,
    time_column: str | None = None,
    market: str | None = None,
    prefer_adjusted: bool = True,
) -> pd.DataFrame:
    """Baca CSV harga dari penyedia data mana pun.

    Nama kolom dinormalkan lewat ALIAS_KOLOM, sehingga berkas dari sumber
    Indonesia maupun asing bisa dibaca tanpa diubah lebih dulu. Angkanya
    dibersihkan lewat bersihkan_angka, yang menangani pemisah ribuan dan
    akhiran ribuan.

    Sebutkan market "idx" untuk saham Indonesia, atau "forex" untuk pasangan
    mata uang. Ini penting pada berkas seperti "7.400", yang berarti Rp 7.400
    pada saham Indonesia tetapi 7,4 pada forex. Tanpa market, konvensinya
    ditebak dari isi kolom, dan tebakan itu bisa salah pada kasus tersebut.

    Bila berkas punya kolom harga yang sudah disesuaikan, seperti "Adj Close"
    milik Yahoo Finance, kolom itulah yang dipakai secara bawaan. Kolom itu
    memuat pengaruh dividen dan pemecahan saham, sehingga mencerminkan hasil
    yang benar-benar diterima pemegang saham. Tanpa itu, pembanding beli lalu
    tahan akan terlihat lebih rendah daripada kenyataannya, karena dividen
    yang dibagikan selama bertahun-tahun hilang dari perhitungan. Setel
    prefer_adjusted=False untuk memakai harga mentah.

    Baris dengan tanggal atau harga yang tidak terbaca dibuang. Itu termasuk
    baris dividen yang disisipkan Yahoo Finance di tengah data harga, yang
    kolomnya lebih sedikit daripada judulnya. Jumlahnya tidak disembunyikan:
    periksa jumlah baris lewat quality.periksa untuk memastikan tidak ada
    yang hilang diam-diam.
    """
    if market not in (None, "idx", "forex"):
        raise ValueError("market harus None, 'idx', atau 'forex'")
    titik_ribuan = {"idx": True, "forex": False}.get(market) if market else None
    # dtype=str penting: tanpa ini pandas sudah menafsirkan "7.350" sebagai
    # 7,35 sebelum bersihkan_kolom sempat memutuskan konvensi titiknya.
    frame = pd.read_csv(path, dtype=str)
    frame.columns = [str(c).strip().lower() for c in frame.columns]

    if time_column is None:
        for candidate in _CANDIDATE_TIME_COLUMNS:
            if candidate in frame.columns:
                time_column = candidate
                break
    if time_column is None:
        raise ValueError(
            f"Kolom waktu tidak ditemukan di {path}. "
            f"Kolom yang ada: {list(frame.columns)}. "
            "Sebutkan lewat argumen time_column."
        )

    # Tanggal gaya ISO seperti 2026-09-01 harus dibaca lebih dulu tanpa
    # dayfirst, karena dayfirst membalik bulan dan harinya menjadi 9 Januari.
    # Sumber Indonesia dan Eropa menulis hari lebih dulu, jadi di luar ISO
    # dayfirst memang yang benar.
    mentah = frame[time_column].astype(str).str.strip()
    pola_iso = mentah.str.match(r"^\d{4}-\d{1,2}-\d{1,2}")
    gaya_iso = bool(pola_iso.fillna(False).mean() > 0.9)
    frame[time_column] = pd.to_datetime(
        mentah, errors="coerce", format="mixed", dayfirst=not gaya_iso
    )
    frame = frame.dropna(subset=[time_column]).set_index(time_column).sort_index()
    frame.index.name = "datetime"

    # Petakan nama kolom ke nama baku. Bila dua kolom memetakan ke nama yang
    # sama, yang pertama dipakai agar tidak ada kolom ganda.
    terpakai: dict[str, str] = {}
    for asli in frame.columns:
        baku = ALIAS_KOLOM.get(asli)
        if baku is not None and baku not in terpakai:
            terpakai[baku] = asli

    # Harga yang sudah disesuaikan menang atas harga mentah bila keduanya ada.
    # Urutan kolom di berkas menaruh "Close" sebelum "Adj Close", jadi tanpa
    # langkah ini harga mentah yang terpilih dan dividen ikut hilang.
    kolom_disesuaikan = None
    if prefer_adjusted:
        for asli in frame.columns:
            if asli in ALIAS_HARGA_DISESUAIKAN:
                kolom_disesuaikan = asli
                break

    if REQUIRED_COLUMN not in terpakai:
        raise ValueError(
            f"Kolom harga penutupan tidak ditemukan di {path}. "
            f"Kolom yang ada: {list(frame.columns)}. "
            f"Nama yang dikenali: {sorted(n for n, b in ALIAS_KOLOM.items() if b == 'close')}"
        )

    bersih = pd.DataFrame(index=frame.index)
    for baku in ("open", "high", "low", "close", "volume"):
        if baku in terpakai:
            # Volume tidak pernah memakai titik sebagai desimal, jadi
            # konvensinya dibiarkan ditebak dari kolomnya sendiri.
            paksa = titik_ribuan if baku != "volume" else None
            bersih[baku] = bersihkan_kolom(frame[terpakai[baku]], paksa)

    if kolom_disesuaikan is not None:
        # Seluruh harga harus berada pada satu skala. Memakai penutupan yang
        # sudah disesuaikan sementara tertinggi dan terendahnya masih mentah
        # menghasilkan keadaan mustahil, misalnya penutupan di bawah harga
        # terendah hari itu, dan itu merusak pengujian stop loss sepenuhnya.
        # Karena itu pembukaan, tertinggi, dan terendah dikalikan rasio
        # penyesuaian hari yang sama.
        disesuaikan = bersihkan_kolom(frame[kolom_disesuaikan], titik_ribuan)
        mentah = bersih[REQUIRED_COLUMN]
        rasio = (disesuaikan / mentah.where(mentah > 0)).reindex(bersih.index)
        for baku in ("open", "high", "low"):
            if baku in bersih.columns:
                bersih[baku] = bersih[baku] * rasio
        bersih[REQUIRED_COLUMN] = disesuaikan

    return bersih.dropna(subset=[REQUIRED_COLUMN])


def log_returns(prices: pd.Series) -> np.ndarray:
    """Return logaritmik dari seri harga, panjangnya len(prices) - 1."""
    values = np.asarray(prices, dtype=float)
    return np.diff(np.log(values))


def _frame_from_closes(closes: np.ndarray, index: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"close": closes}, index=index)


def synthetic_gbm(
    bars: int,
    start_price: float = 1.1000,
    daily_volatility: float = 0.006,
    drift: float = 0.0,
    seed: int | None = None,
    start: str = "2015-01-01",
    freq: str = "D",
) -> pd.DataFrame:
    """Harga acak murni (geometric Brownian motion).

    Tidak ada pola apa pun di dalamnya. Strategi yang tampak untung di sini
    sedang menunjukkan kebetulan, bukan keunggulan.
    """
    rng = np.random.default_rng(seed)
    steps = rng.normal(loc=drift, scale=daily_volatility, size=bars)
    closes = start_price * np.exp(np.cumsum(steps))
    index = pd.date_range(start=start, periods=bars, freq=freq, name="datetime")
    return _frame_from_closes(closes, index)


def shuffle_returns(prices: pd.DataFrame, seed: int | None = None) -> pd.DataFrame:
    """Acak urutan return harga asli.

    Besaran dan sebaran pergerakan harian dipertahankan persis, tapi urutan
    waktunya dihancurkan. Pola yang bisa diprediksi ikut hilang, sementara
    "watak" pasarnya tetap. Ini pembanding paling jujur untuk strategi
    berbasis pola harga.
    """
    rng = np.random.default_rng(seed)
    returns = log_returns(prices["close"])
    rng.shuffle(returns)
    start_price = float(prices["close"].iloc[0])
    closes = np.concatenate([[start_price], start_price * np.exp(np.cumsum(returns))])
    return _frame_from_closes(closes, prices.index[: len(closes)])


def block_bootstrap_returns(
    prices: pd.DataFrame, block_size: int = 20, seed: int | None = None
) -> pd.DataFrame:
    """Susun ulang return harga asli dalam potongan (blok).

    Lebih ketat daripada shuffle_returns: pengelompokan volatilitas, yaitu
    kecenderungan hari bergejolak datang berurutan, tetap terjaga di dalam
    blok. Pola lintas blok tetap hancur.
    """
    rng = np.random.default_rng(seed)
    returns = log_returns(prices["close"])
    if len(returns) == 0:
        raise ValueError("Seri harga terlalu pendek untuk bootstrap.")
    block_size = max(1, min(block_size, len(returns)))

    pieces: list[np.ndarray] = []
    collected = 0
    while collected < len(returns):
        start = int(rng.integers(0, len(returns) - block_size + 1))
        block = returns[start : start + block_size]
        pieces.append(block)
        collected += len(block)

    resampled = np.concatenate(pieces)[: len(returns)]
    start_price = float(prices["close"].iloc[0])
    closes = np.concatenate([[start_price], start_price * np.exp(np.cumsum(resampled))])
    return _frame_from_closes(closes, prices.index[: len(closes)])
