"""Sumber data harga untuk forex-lab.

Dua sumber:
  1. CSV asli yang diunduh pengguna (load_csv)
  2. Data buatan untuk uji kendali (synthetic_*), dipakai untuk membuktikan
     apakah sebuah strategi punya keunggulan nyata atau cuma kebetulan.

Semua fungsi mengembalikan pandas.DataFrame dengan indeks waktu dan
minimal satu kolom: "close". Kolom open/high/low diisi bila tersedia.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_COLUMN = "close"
_CANDIDATE_TIME_COLUMNS = ("datetime", "date", "time", "timestamp", "gmt time")


def load_csv(path: str, time_column: str | None = None) -> pd.DataFrame:
    """Baca CSV harga dari penyedia data mana pun.

    Nama kolom dinormalkan ke huruf kecil, lalu kolom waktu dipakai sebagai
    indeks. Penyedia yang berbeda memakai nama berbeda (Date, Gmt time,
    timestamp), jadi kolom waktu dideteksi otomatis bila tidak disebutkan.
    """
    frame = pd.read_csv(path)
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

    frame[time_column] = pd.to_datetime(frame[time_column], errors="coerce", format="mixed")
    frame = frame.dropna(subset=[time_column]).set_index(time_column).sort_index()
    frame.index.name = "datetime"

    if REQUIRED_COLUMN not in frame.columns:
        raise ValueError(
            f"Kolom 'close' wajib ada di {path}. Kolom yang ada: {list(frame.columns)}"
        )

    keep = [c for c in ("open", "high", "low", "close", "volume") if c in frame.columns]
    frame = frame[keep].astype(float)
    return frame.dropna(subset=[REQUIRED_COLUMN])


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
