"""Ukuran hasil backtest.

Total keuntungan adalah angka yang paling menipu. Sebuah strategi bisa
mencetak keuntungan besar sambil hampir membangkrutkan akun di tengah jalan,
atau mendapatkannya dari satu transaksi keberuntungan. Kolom yang paling
penting di sini adalah penurunan terdalam, jumlah transaksi, dan harapan
keuntungan per transaksi.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


@dataclass
class Result:
    strategy: str
    bars: int
    trades: int
    starting_balance: float
    final_equity: float
    total_return: float
    annualised_return: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    expectancy: float
    sharpe: float
    total_costs: float
    costs_share_of_gross: float
    margin_calls: int
    stopped_out: bool
    blown: bool

    def as_dict(self) -> dict:
        return asdict(self)

    def summary_line(self) -> str:
        status = "AKUN HABIS" if self.blown else f"{self.total_return:+7.1%}"
        return (
            f"{self.strategy:<16} {status:>12}  "
            f"turun terdalam {self.max_drawdown:5.1%}  "
            f"transaksi {self.trades:>4}  "
            f"menang {self.win_rate:5.1%}  "
            f"biaya {self.total_costs:>10,.0f}"
        )


def max_drawdown(equity_curve: np.ndarray) -> float:
    """Penurunan terdalam dari puncak ke dasar, sebagai pecahan.

    Inilah angka yang menentukan apakah sebuah strategi bisa dijalankan oleh
    manusia. Penurunan 50 persen secara matematis bisa pulih, tapi hampir
    tidak ada orang yang sanggup menahannya tanpa berhenti.
    """
    values = np.asarray(equity_curve, dtype=float)
    if values.size == 0:
        return 0.0
    running_peak = np.maximum.accumulate(values)
    safe_peak = np.where(running_peak <= 0, np.nan, running_peak)
    drawdowns = 1.0 - values / safe_peak
    worst = np.nanmax(drawdowns) if np.any(~np.isnan(drawdowns)) else 0.0
    return float(min(max(worst, 0.0), 1.0))


def sharpe_ratio(equity_curve: np.ndarray, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    """Keuntungan dibandingkan gejolaknya, disetahunkan.

    Di bawah 1 berarti gejolaknya tidak sebanding dengan hasilnya. Nilai di
    atas 2 pada backtest hampir selalu tanda ada kesalahan metode, bukan tanda
    strategi hebat.
    """
    values = np.asarray(equity_curve, dtype=float)
    if values.size < 3:
        return 0.0
    positive = np.where(values > 0, values, np.nan)
    returns = np.diff(np.log(positive))
    returns = returns[np.isfinite(returns)]
    if returns.size < 2:
        return 0.0
    deviation = returns.std(ddof=1)
    if deviation == 0:
        return 0.0
    return float(returns.mean() / deviation * np.sqrt(periods_per_year))


def annualised_return(total_return: float, bars: int, bars_per_year: int) -> float:
    """Ubah keuntungan total menjadi laju per tahun."""
    if bars <= 0 or bars_per_year <= 0:
        return 0.0
    growth = 1.0 + total_return
    if growth <= 0:
        return -1.0
    years = bars / bars_per_year
    if years <= 0:
        return 0.0
    return float(growth ** (1.0 / years) - 1.0)


def build_result(
    strategy: str,
    broker,
    equity_curve: np.ndarray,
    bars: int,
    bars_per_year: int = TRADING_DAYS_PER_YEAR,
) -> Result:
    profits = np.array([t.profit for t in broker.trades], dtype=float)
    costs = float(np.sum([t.costs for t in broker.trades])) if broker.trades else 0.0

    wins = profits[profits > 0]
    losses = profits[profits < 0]
    gross_win = float(wins.sum())
    gross_loss = float(-losses.sum())

    final_equity = float(equity_curve[-1]) if len(equity_curve) else broker.balance
    total_return = final_equity / broker.starting_balance - 1.0
    gross_profit_abs = gross_win + gross_loss

    return Result(
        strategy=strategy,
        bars=bars,
        trades=len(profits),
        starting_balance=broker.starting_balance,
        final_equity=final_equity,
        total_return=total_return,
        annualised_return=annualised_return(total_return, bars, bars_per_year),
        max_drawdown=max_drawdown(equity_curve),
        win_rate=float(len(wins) / len(profits)) if len(profits) else 0.0,
        profit_factor=float(gross_win / gross_loss) if gross_loss > 0 else float("inf"),
        expectancy=float(profits.mean()) if len(profits) else 0.0,
        sharpe=sharpe_ratio(equity_curve, bars_per_year),
        total_costs=costs,
        costs_share_of_gross=float(costs / gross_profit_abs) if gross_profit_abs > 0 else 0.0,
        margin_calls=broker.margin_calls,
        stopped_out=broker.stopped_out,
        blown=broker.is_blown,
    )


def results_table(results: list[Result]) -> pd.DataFrame:
    return pd.DataFrame([r.as_dict() for r in results])
