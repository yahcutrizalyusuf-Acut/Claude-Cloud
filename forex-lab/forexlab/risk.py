"""Manajemen risiko, dikunci di kode dan tidak boleh diubah oleh model AI.

Pemisahan ini disengaja. Strategi boleh salah menebak arah sesering apa pun,
dan itu normal. Yang tidak boleh terjadi adalah satu transaksi atau satu hari
buruk menghabiskan akun. Aturan di bawah ini yang mencegahnya, dan letaknya
terpisah supaya tidak ikut berubah saat strategi diubah-ubah.
"""

from __future__ import annotations

from dataclasses import dataclass

from .broker import UNITS_PER_LOT, SimulatedBroker


@dataclass(frozen=True)
class RiskLimits:
    """Batas yang dipaksakan pada setiap transaksi.

    risk_per_trade 0.01 berarti kerugian maksimal 1 persen ekuitas per
    transaksi bila stop loss tersentuh. Angka ini, bukan leverage broker,
    yang menentukan ukuran posisi.
    """

    risk_per_trade: float = 0.01
    stop_loss_atr_multiple: float = 2.0
    take_profit_atr_multiple: float = 3.0
    max_daily_loss: float = 0.03
    max_total_drawdown: float = 0.20
    max_effective_leverage: float = 10.0

    def __post_init__(self) -> None:
        if not 0 < self.risk_per_trade <= 0.05:
            raise ValueError(
                "risk_per_trade harus di antara 0 dan 0.05. "
                "Di atas 5 persen per transaksi, kebangkrutan hanya soal waktu."
            )
        if self.stop_loss_atr_multiple <= 0:
            raise ValueError("stop_loss_atr_multiple harus positif")
        if not 0 < self.max_effective_leverage <= 50:
            raise ValueError("max_effective_leverage harus di antara 0 dan 50")


def position_size(
    broker: SimulatedBroker,
    mid_price: float,
    stop_distance: float,
    limits: RiskLimits,
) -> float:
    """Hitung ukuran posisi dari risiko yang diizinkan, bukan dari leverage.

    Jumlah unit dipilih agar kerugian saat stop loss tersentuh sama dengan
    risk_per_trade dikali ekuitas. Hasilnya lalu dibatasi lagi oleh
    max_effective_leverage dan oleh jaminan yang tersedia.
    """
    if stop_distance <= 0:
        return 0.0

    equity = broker.equity(mid_price)
    if equity <= 0:
        return 0.0

    units_by_risk = equity * limits.risk_per_trade / stop_distance
    units_by_leverage = equity * limits.max_effective_leverage / mid_price
    units_by_margin = broker.max_units(mid_price)

    units = min(units_by_risk, units_by_leverage, units_by_margin)
    # Dibulatkan ke bawah ke 0.01 lot, ukuran terkecil yang diterima broker.
    min_step = UNITS_PER_LOT * 0.01
    return (units // min_step) * min_step


def average_true_range(high, low, close, period: int = 14):
    """Rentang gerak rata-rata, dipakai untuk menempatkan stop loss.

    Stop loss yang jaraknya mengikuti gejolak pasar jauh lebih baik daripada
    jarak tetap dalam pip, karena pasar tenang dan pasar bergejolak butuh
    ruang yang berbeda.
    """
    import numpy as np
    import pandas as pd

    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    previous_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()],
        axis=1,
    ).max(axis=1)
    atr = true_range.rolling(period).mean()
    # Sebelum ATR terbentuk, pakai perkiraan kasar dari gejolak harga.
    fallback = close.pct_change().abs().rolling(period).mean() * close
    return atr.fillna(fallback).fillna(close * 0.005).replace(0.0, np.nan).ffill()
