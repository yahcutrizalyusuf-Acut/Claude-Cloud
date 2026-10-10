"""Mesin backtest berbasis batang (bar) untuk strategi forex.

Urutan kejadian di setiap batang dibuat mengikuti kenyataan, bukan yang
paling menguntungkan:

  1. biaya menginap dibebankan untuk posisi yang dibawa dari batang sebelumnya
  2. stop loss dan take profit diperiksa terhadap rentang harga batang ini
  3. margin diperiksa, dan broker boleh menutup paksa
  4. sinyal dari batang SEBELUMNYA dieksekusi pada harga penutupan batang ini
  5. ekuitas dicatat

Langkah 4 adalah yang paling sering salah di backtest buatan sendiri. Sinyal
yang dihitung dari harga penutupan sebuah batang tidak mungkin dieksekusi
pada harga penutupan batang yang sama, karena saat harga itu diketahui, batang
tersebut sudah berakhir. Mengeksekusinya di sana membuat strategi tampak bisa
melihat masa depan, dan itu sumber utama backtest yang terlalu indah.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .broker import BrokerConfig, SimulatedBroker, StopOut
from .metrics import TRADING_DAYS_PER_YEAR, Result, build_result
from .risk import RiskLimits, average_true_range, position_size


@dataclass
class BacktestConfig:
    starting_balance: float = 1_000_000.0
    broker: BrokerConfig | None = None
    limits: RiskLimits | None = None
    use_stops: bool = True
    bars_per_year: int = TRADING_DAYS_PER_YEAR
    swap_days_per_bar: float = 1.0

    def __post_init__(self) -> None:
        self.broker = self.broker or BrokerConfig()
        self.limits = self.limits or RiskLimits()


def _bar_range(prices: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Rentang tertinggi dan terendah per batang.

    Bila data hanya punya harga penutupan, rentangnya diperkirakan dari
    gejolak harga agar stop loss tetap bisa diuji. Perkiraan ini membuat
    hasil stop loss kurang tepat, jadi data dengan high dan low selalu lebih
    baik.
    """
    close = prices["close"].to_numpy(dtype=float)
    if "high" in prices.columns and "low" in prices.columns:
        return prices["high"].to_numpy(dtype=float), prices["low"].to_numpy(dtype=float)
    typical_move = pd.Series(close).pct_change().abs().rolling(14).mean().bfill().fillna(0.003)
    half = close * typical_move.to_numpy(dtype=float) / 2.0
    return close + half, close - half


def run_backtest(
    prices: pd.DataFrame,
    signals: pd.Series,
    config: BacktestConfig | None = None,
    strategy_name: str = "strategy",
) -> tuple[Result, pd.Series]:
    """Jalankan satu strategi pada satu seri harga.

    Mengembalikan ringkasan hasil dan kurva ekuitas. Kurva ekuitas, bukan
    angka keuntungan akhir, yang memperlihatkan apakah strategi ini layak
    dijalankan.
    """
    config = config or BacktestConfig()
    if len(prices) != len(signals):
        raise ValueError("panjang signals harus sama dengan panjang prices")
    if len(prices) < 3:
        raise ValueError("data terlalu pendek untuk backtest")

    broker = SimulatedBroker(config.starting_balance, config.broker)
    limits = config.limits

    close = prices["close"].to_numpy(dtype=float)
    high, low = _bar_range(prices)
    signal_values = signals.to_numpy(dtype=int)
    atr = average_true_range(high, low, close).to_numpy(dtype=float)

    equity_curve = np.empty(len(close), dtype=float)
    peak_equity = config.starting_balance
    day_start_equity = config.starting_balance
    current_day = prices.index[0].date() if hasattr(prices.index[0], "date") else None
    halted = False

    for i in range(len(close)):
        price = close[i]

        if i > 0:
            broker.accrue_swap(config.swap_days_per_bar)
            broker.check_exits(high[i], low[i], i)
            broker.enforce_margin(price, i)

        equity = broker.equity(price)
        peak_equity = max(peak_equity, equity)

        # Batas kerugian harian: dihitung ulang setiap kali tanggal berganti.
        bar_day = prices.index[i].date() if hasattr(prices.index[i], "date") else None
        if bar_day != current_day:
            current_day = bar_day
            day_start_equity = equity

        daily_loss = 1.0 - equity / day_start_equity if day_start_equity > 0 else 1.0
        total_drawdown = 1.0 - equity / peak_equity if peak_equity > 0 else 1.0
        breached = (
            daily_loss >= limits.max_daily_loss
            or total_drawdown >= limits.max_total_drawdown
        )

        if breached and not halted:
            # Batas risiko tersentuh: tutup posisi dan berhenti berdagang.
            # Robot nyata berhenti di sini dan menunggu diperiksa manusia.
            if broker.position is not None:
                broker.close_position(price, i, "risk_halt")
            halted = total_drawdown >= limits.max_total_drawdown
            equity = broker.equity(price)

        equity_curve[i] = equity

        if broker.is_blown or halted:
            equity_curve[i:] = equity
            break

        # Eksekusi sinyal batang sebelumnya pada harga penutupan batang ini.
        if i == 0:
            continue
        desired = int(signal_values[i - 1])
        current = broker.position.direction if broker.position else 0

        if desired == current:
            continue

        if broker.position is not None:
            broker.close_position(price, i, "signal")

        if desired == 0:
            continue

        stop_distance = atr[i] * limits.stop_loss_atr_multiple if config.use_stops else price * 0.02
        if not np.isfinite(stop_distance) or stop_distance <= 0:
            continue

        units = position_size(broker, price, stop_distance, limits)
        if units <= 0:
            continue

        if config.use_stops:
            stop_loss = price - desired * stop_distance
            take_profit = price + desired * atr[i] * limits.take_profit_atr_multiple
        else:
            stop_loss = take_profit = None

        try:
            broker.open_position(desired, units, price, i, stop_loss, take_profit)
        except StopOut:
            continue

    result = build_result(
        strategy=strategy_name,
        broker=broker,
        equity_curve=equity_curve,
        bars=len(close),
        bars_per_year=config.bars_per_year,
    )
    return result, pd.Series(equity_curve, index=prices.index, name="equity")
