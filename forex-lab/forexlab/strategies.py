"""Strategi yang bisa diuji, termasuk pembanding yang wajib dikalahkan.

Sebuah strategi di sini adalah fungsi yang menerima seri harga dan
mengembalikan seri sinyal berisi 1 (beli), -1 (jual), atau 0 (tidak ada
posisi), satu nilai per batang.

Aturan penting agar hasil tidak bohong: sinyal pada batang ke-i hanya boleh
memakai data sampai batang ke-i, dan eksekusinya terjadi di batang i+1.
Pergeseran satu batang itu dilakukan oleh mesin backtest, bukan di sini.
Melewatkannya adalah kesalahan paling umum yang membuat backtest tampak
jauh lebih untung daripada kenyataan.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def moving_average_crossover(
    prices: pd.DataFrame, fast: int = 20, slow: int = 50
) -> pd.Series:
    """Beli saat rata-rata cepat di atas rata-rata lambat, jual bila sebaliknya.

    Strategi pengikut tren paling klasik, dan dasar dari sebagian besar robot
    forex yang dijual di internet.
    """
    if fast >= slow:
        raise ValueError("fast harus lebih kecil dari slow")
    close = prices["close"]
    fast_ma = close.rolling(fast).mean()
    slow_ma = close.rolling(slow).mean()
    signal = pd.Series(0, index=prices.index, dtype=int)
    signal[fast_ma > slow_ma] = 1
    signal[fast_ma < slow_ma] = -1
    signal[slow_ma.isna()] = 0
    return signal


def rsi_mean_reversion(
    prices: pd.DataFrame, period: int = 14, low: float = 30.0, high: float = 70.0
) -> pd.Series:
    """Beli saat dinilai terlalu murah, jual saat dinilai terlalu mahal.

    Kebalikan dari pengikut tren: bertaruh harga kembali ke rata-rata.
    """
    close = prices["close"]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0.0, np.nan)
    rsi = 100 - 100 / (1 + rs)

    signal = pd.Series(0, index=prices.index, dtype=int)
    signal[rsi < low] = 1
    signal[rsi > high] = -1
    return signal.where(rsi.notna(), 0).astype(int)


def breakout(prices: pd.DataFrame, lookback: int = 55) -> pd.Series:
    """Beli saat harga menembus tertinggi periode, jual saat menembus terendah."""
    close = prices["close"]
    upper = close.rolling(lookback).max()
    lower = close.rolling(lookback).min()
    signal = pd.Series(0, index=prices.index, dtype=int)
    signal[close >= upper] = 1
    signal[close <= lower] = -1
    signal[upper.isna()] = 0
    return signal


def coin_flip(prices: pd.DataFrame, hold_bars: int = 5, seed: int | None = 42) -> pd.Series:
    """Pembanding wajib: arah ditentukan lemparan koin.

    Strategi apa pun yang tidak mengalahkan ini secara meyakinkan tidak punya
    keunggulan. Dipakai sebagai batas bawah dalam setiap laporan.
    """
    rng = np.random.default_rng(seed)
    values = np.zeros(len(prices), dtype=int)
    i = 0
    while i < len(values):
        direction = 1 if rng.random() < 0.5 else -1
        values[i : i + hold_bars] = direction
        i += hold_bars
    return pd.Series(values, index=prices.index, dtype=int)


def always_long(prices: pd.DataFrame) -> pd.Series:
    """Beli dan tahan. Pembanding kedua, dan pada saham biasanya sulit dikalahkan."""
    return pd.Series(1, index=prices.index, dtype=int)


REGISTRY: dict[str, object] = {
    "ma_crossover": moving_average_crossover,
    "rsi": rsi_mean_reversion,
    "breakout": breakout,
    "coin_flip": coin_flip,
    "always_long": always_long,
}
