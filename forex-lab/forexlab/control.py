"""Uji kendali: apakah strategi ini punya keunggulan, atau sedang beruntung?

Ini bagian terpenting di seluruh proyek, dan yang hampir selalu hilang dari
robot forex yang dijual orang.

Masalahnya begini. Kalau kita menguji cukup banyak strategi pada satu seri
harga, beberapa di antaranya pasti terlihat untung, sama seperti beberapa
orang di ruangan pasti menang saat semuanya melempar koin. Keuntungan di
backtest karena itu bukan bukti apa pun dengan sendirinya.

Caranya memeriksa: jalankan strategi yang sama pada ratusan seri harga
buatan yang sudah dipastikan tidak punya pola, lalu lihat di mana hasil pada
data asli berdiri di antara hasil-hasil acak itu. Kalau hasil asli berada di
tengah kerumunan, strategi itu tidak menemukan apa pun. Keunggulan nyata
berarti hasil asli berdiri di luar hampir semua hasil acak.

Metodenya disebut uji permutasi. Dipakai luas di statistik, dan tidak
bergantung pada asumsi apa pun tentang bentuk sebaran keuntungan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from .backtest import BacktestConfig, run_backtest
from .data import block_bootstrap_returns, shuffle_returns

SignalFunction = Callable[[pd.DataFrame], pd.Series]

#: Ambang bukti. 0.05 berarti hasil asli harus mengalahkan 95 persen hasil
#: acak sebelum strategi dianggap punya keunggulan. Dibuat ketat dengan
#: sengaja, karena biaya salah menyimpulkan di sini dibayar dengan uang.
SIGNIFICANCE = 0.05


@dataclass
class ControlReport:
    strategy: str
    real_return: float
    real_drawdown: float
    random_runs: int
    random_mean_return: float
    random_median_return: float
    random_best_return: float
    beaten_fraction: float
    p_value: float
    method: str

    @property
    def has_edge(self) -> bool:
        """Benar hanya bila hasil asli berdiri di luar sebaran acak."""
        return self.p_value < SIGNIFICANCE and self.real_return > 0

    def verdict(self) -> str:
        if self.has_edge:
            return "ADA TANDA KEUNGGULAN"
        if self.real_return <= 0:
            return "TIDAK UNTUNG SEJAK AWAL"
        return "KEUNTUNGAN TIDAK TERBUKTI, MASIH DALAM WILAYAH KEBETULAN"

    def report_text(self) -> str:
        return "\n".join(
            [
                f"Strategi            : {self.strategy}",
                f"Metode pembanding   : {self.method}",
                f"Hasil data asli     : {self.real_return:+.2%} "
                f"(turun terdalam {self.real_drawdown:.1%})",
                f"Hasil data acak     : rata-rata {self.random_mean_return:+.2%}, "
                f"median {self.random_median_return:+.2%}, "
                f"terbaik {self.random_best_return:+.2%}",
                f"Mengalahkan          : {self.beaten_fraction:.1%} dari "
                f"{self.random_runs} percobaan acak",
                f"Nilai p             : {self.p_value:.3f} "
                f"(ambang {SIGNIFICANCE})",
                f"Kesimpulan          : {self.verdict()}",
            ]
        )


def permutation_test(
    prices: pd.DataFrame,
    signal_function: SignalFunction,
    config: BacktestConfig | None = None,
    runs: int = 200,
    method: str = "block",
    block_size: int = 20,
    seed: int = 0,
    strategy_name: str = "strategy",
) -> ControlReport:
    """Bandingkan hasil pada data asli dengan hasil pada data yang diacak.

    method "block" menyusun ulang return dalam potongan, sehingga
    pengelompokan volatilitas tetap terjaga. Ini pembanding yang lebih ketat
    dan yang sebaiknya dipakai. method "shuffle" mengacak satu per satu.

    Nilai p adalah peluang mendapat hasil sebagus itu dari kebetulan saja.
    Nilai 0.30 berarti tiga dari sepuluh rangkaian harga acak memberi hasil
    yang sama bagusnya, jadi tidak ada yang istimewa dari hasil tersebut.
    """
    if runs < 20:
        raise ValueError("runs minimal 20 agar nilai p berarti")
    if method not in ("block", "shuffle"):
        raise ValueError("method harus 'block' atau 'shuffle'")

    config = config or BacktestConfig()
    real_result, _ = run_backtest(prices, signal_function(prices), config, strategy_name)

    random_returns = np.empty(runs, dtype=float)
    for i in range(runs):
        if method == "block":
            fake = block_bootstrap_returns(prices, block_size=block_size, seed=seed + i)
        else:
            fake = shuffle_returns(prices, seed=seed + i)
        fake_result, _ = run_backtest(fake, signal_function(fake), config, strategy_name)
        random_returns[i] = fake_result.total_return

    beaten = int(np.sum(random_returns < real_result.total_return))
    # Koreksi +1 di pembilang dan penyebut: hasil asli dihitung sebagai satu
    # kemungkinan susunan, sehingga nilai p tidak pernah tepat nol.
    p_value = float((runs - beaten + 1) / (runs + 1))

    return ControlReport(
        strategy=strategy_name,
        real_return=real_result.total_return,
        real_drawdown=real_result.max_drawdown,
        random_runs=runs,
        random_mean_return=float(random_returns.mean()),
        random_median_return=float(np.median(random_returns)),
        random_best_return=float(random_returns.max()),
        beaten_fraction=beaten / runs,
        p_value=p_value,
        method=method,
    )
