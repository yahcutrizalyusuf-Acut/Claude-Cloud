"""Uji di luar sampel: apakah strategi ini ditemukan, atau dipaksakan?

Uji kendali di control.py menjawab satu pertanyaan: apakah hasil sebagus ini
bisa muncul dari kebetulan? Modul ini menjawab pertanyaan kedua yang sama
berbahayanya, dan yang hampir selalu dilewatkan.

Masalahnya begini. Strategi rata-rata bergerak punya dua angka yang bisa
disetel, cepat dan lambat. Kalau dicoba 20 nilai cepat dikali 20 nilai
lambat, ada 400 kombinasi. Dari 400 percobaan pada data yang sama, pasti ada
beberapa yang hasilnya bagus, bahkan kalau datanya acak murni. Lalu kombinasi
terbaik itu dipamerkan sebagai "strategi yang sudah dioptimasi".

Yang sebenarnya terjadi: angka-angka itu dipilih agar cocok dengan kebetulan
di data masa lalu, bukan karena menangkap sesuatu yang nyata. Istilahnya
overfitting, dan cirinya khas. Hasilnya indah di data yang dipakai mencari,
lalu hancur di data yang belum pernah dilihat.

Satu-satunya obatnya adalah memisahkan data. Angka disetel pada potongan
pertama, lalu diuji pada potongan berikutnya yang belum pernah dilihat sama
sekali. Hasil di potongan kedua itulah satu-satunya angka yang berarti.

Catatan teknis yang penting. Sinyal dihitung sekali pada seluruh seri harga,
baru dipotong per jendela. Ini aman karena semua indikator di strategies.py
hanya melihat ke belakang lewat rolling(), jadi nilai pada batang ke-i tidak
pernah memakai data sesudahnya. Kalau nanti ada indikator baru yang melihat
ke depan, cara ini jadi tidak aman lagi.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
import pandas as pd

from .backtest import BacktestConfig, run_backtest

#: Fungsi yang menerima nilai setelan dan mengembalikan penghasil sinyal.
StrategyFactory = Callable[..., Callable[[pd.DataFrame], pd.Series]]


@dataclass(frozen=True)
class Window:
    """Satu pasang potongan data: untuk menyetel, dan untuk menguji."""

    train_start: int
    train_end: int
    test_start: int
    test_end: int

    @property
    def train_bars(self) -> int:
        return self.train_end - self.train_start

    @property
    def test_bars(self) -> int:
        return self.test_end - self.test_start


def walk_forward_windows(
    total_bars: int, train_bars: int, test_bars: int, step: int | None = None
) -> list[Window]:
    """Bagi data menjadi rangkaian jendela setel-lalu-uji yang bergerak maju.

    Jendela pertama menyetel pada batang 0 sampai train_bars, lalu menguji
    pada batang berikutnya sebanyak test_bars. Jendela kedua bergeser maju,
    dan seterusnya. Potongan uji tidak pernah tumpang tindih, sehingga
    hasilnya bisa dirangkai menjadi satu riwayat yang utuh.
    """
    if train_bars < 50:
        raise ValueError("train_bars minimal 50 agar indikator punya ruang terbentuk")
    if test_bars < 20:
        raise ValueError("test_bars minimal 20 agar hasilnya berarti")
    step = step or test_bars

    windows: list[Window] = []
    train_start = 0
    while train_start + train_bars + test_bars <= total_bars:
        train_end = train_start + train_bars
        windows.append(
            Window(
                train_start=train_start,
                train_end=train_end,
                test_start=train_end,
                test_end=train_end + test_bars,
            )
        )
        train_start += step

    if not windows:
        raise ValueError(
            f"Data {total_bars} batang terlalu pendek untuk train={train_bars} "
            f"dan test={test_bars}. Butuh minimal {train_bars + test_bars} batang."
        )
    return windows


def expand_grid(param_grid: dict[str, Iterable]) -> list[dict]:
    """Ubah daftar nilai per setelan menjadi daftar semua kombinasi."""
    if not param_grid:
        return [{}]
    names = list(param_grid)
    combinations = itertools.product(*(list(param_grid[name]) for name in names))
    return [dict(zip(names, values)) for values in combinations]


def _is_valid(params: dict) -> bool:
    """Buang kombinasi yang tidak masuk akal, misalnya cepat lebih besar dari lambat."""
    if "fast" in params and "slow" in params:
        return params["fast"] < params["slow"]
    return True


def parameter_sweep(
    prices: pd.DataFrame,
    factory: StrategyFactory,
    param_grid: dict[str, Iterable],
    config: BacktestConfig | None = None,
) -> pd.DataFrame:
    """Uji setiap kombinasi setelan pada seluruh data, lalu urutkan hasilnya.

    Keluaran fungsi ini adalah tabel yang menggoda dan menyesatkan. Baris
    teratasnya selalu terlihat bagus, bahkan pada data acak, karena itulah
    yang terjadi kalau cukup banyak kombinasi dicoba. Fungsi ini disediakan
    untuk memperlihatkan jebakannya, bukan untuk memilih setelan.
    """
    config = config or BacktestConfig()
    rows = []
    for params in expand_grid(param_grid):
        if not _is_valid(params):
            continue
        signals = factory(**params)(prices)
        result, _ = run_backtest(prices, signals, config, "sweep")
        rows.append(
            {
                **params,
                "total_return": result.total_return,
                "max_drawdown": result.max_drawdown,
                "trades": result.trades,
                "sharpe": result.sharpe,
            }
        )
    if not rows:
        raise ValueError("Tidak ada kombinasi setelan yang sah di param_grid")
    return pd.DataFrame(rows).sort_values("total_return", ascending=False).reset_index(drop=True)


@dataclass
class WalkForwardReport:
    strategy: str
    windows: int
    combinations_tried: int
    in_sample_mean: float
    out_of_sample_mean: float
    out_of_sample_compound: float
    out_of_sample_win_rate: float
    best_params_per_window: list[dict]
    detail: pd.DataFrame

    @property
    def degradation(self) -> float:
        """Selisih hasil di dalam sampel dan di luar sampel.

        Angka besar berarti setelan itu cocok dengan masa lalu, bukan dengan
        pasar. Nol atau mendekati nol adalah tanda yang sehat.
        """
        return self.in_sample_mean - self.out_of_sample_mean

    @property
    def survives(self) -> bool:
        """Benar hanya bila hasil di luar sampel tetap positif dan cukup konsisten."""
        return self.out_of_sample_compound > 0 and self.out_of_sample_win_rate >= 0.5

    def verdict(self) -> str:
        if self.survives:
            return "LOLOS UJI LUAR SAMPEL"
        if self.out_of_sample_compound <= 0:
            return "GAGAL DI LUAR SAMPEL, SETELAN HANYA COCOK DENGAN MASA LALU"
        return "LOLOS TIPIS, TIDAK KONSISTEN ANTAR JENDELA"

    def report_text(self) -> str:
        return "\n".join(
            [
                f"Strategi                  : {self.strategy}",
                f"Jendela setel-lalu-uji    : {self.windows}",
                f"Kombinasi setelan dicoba  : {self.combinations_tried} per jendela",
                f"Hasil rata-rata, disetel  : {self.in_sample_mean:+.2%}",
                f"Hasil rata-rata, diuji    : {self.out_of_sample_mean:+.2%}",
                f"Penurunan mutu            : {self.degradation:+.2%}",
                f"Hasil berangkai di luar   : {self.out_of_sample_compound:+.2%}",
                f"Jendela uji yang untung   : {self.out_of_sample_win_rate:.1%}",
                f"Kesimpulan                : {self.verdict()}",
            ]
        )


def walk_forward_test(
    prices: pd.DataFrame,
    factory: StrategyFactory,
    param_grid: dict[str, Iterable],
    config: BacktestConfig | None = None,
    train_bars: int = 500,
    test_bars: int = 125,
    strategy_name: str = "strategy",
) -> WalkForwardReport:
    """Setel pada data lama, uji pada data berikutnya, ulangi maju ke depan.

    Untuk setiap jendela, semua kombinasi setelan diuji pada potongan setel,
    yang terbaik dipilih, lalu setelan itu dan hanya itu yang diuji pada
    potongan berikutnya yang belum pernah dilihat.

    Satu-satunya angka yang berarti dari seluruh proses ini adalah hasil di
    potongan uji. Hasil di potongan setel selalu bagus, dan itu tidak berarti
    apa-apa.
    """
    config = config or BacktestConfig()
    windows = walk_forward_windows(len(prices), train_bars, test_bars)
    combinations = [p for p in expand_grid(param_grid) if _is_valid(p)]
    if not combinations:
        raise ValueError("Tidak ada kombinasi setelan yang sah di param_grid")

    # Sinyal dihitung sekali untuk seluruh seri, lalu dipotong per jendela.
    # Aman karena semua indikator hanya melihat ke belakang.
    signal_cache = {
        tuple(sorted(params.items())): factory(**params)(prices) for params in combinations
    }

    rows = []
    best_params_per_window: list[dict] = []

    for number, window in enumerate(windows, start=1):
        train_prices = prices.iloc[window.train_start : window.train_end]

        best_params = None
        best_train_return = -np.inf
        for params in combinations:
            key = tuple(sorted(params.items()))
            signals = signal_cache[key].iloc[window.train_start : window.train_end]
            result, _ = run_backtest(train_prices, signals, config, "train")
            if result.total_return > best_train_return:
                best_train_return = result.total_return
                best_params = params

        assert best_params is not None
        test_prices = prices.iloc[window.test_start : window.test_end]
        key = tuple(sorted(best_params.items()))
        test_signals = signal_cache[key].iloc[window.test_start : window.test_end]
        test_result, _ = run_backtest(test_prices, test_signals, config, "test")

        best_params_per_window.append(dict(best_params))
        rows.append(
            {
                "window": number,
                **{f"best_{k}": v for k, v in best_params.items()},
                "in_sample_return": best_train_return,
                "out_of_sample_return": test_result.total_return,
                "out_of_sample_drawdown": test_result.max_drawdown,
                "out_of_sample_trades": test_result.trades,
            }
        )

    detail = pd.DataFrame(rows)
    oos = detail["out_of_sample_return"].to_numpy(dtype=float)

    return WalkForwardReport(
        strategy=strategy_name,
        windows=len(windows),
        combinations_tried=len(combinations),
        in_sample_mean=float(detail["in_sample_return"].mean()),
        out_of_sample_mean=float(oos.mean()),
        out_of_sample_compound=float(np.prod(1.0 + oos) - 1.0),
        out_of_sample_win_rate=float(np.mean(oos > 0)),
        best_params_per_window=best_params_per_window,
        detail=detail,
    )
