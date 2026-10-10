#!/usr/bin/env python3
"""Jalankan backtest dan uji kendali dari baris perintah.

Contoh pemakaian:

  # Semua strategi pada data simulasi, leverage 100
  python3 scripts/run_backtest.py --synthetic 2000 --leverage 100

  # Satu strategi pada data CSV milik sendiri, lengkap dengan uji kendali
  python3 scripts/run_backtest.py --csv data/EURUSD_daily.csv \
      --strategy ma_crossover --control 200

  # Bandingkan pengaruh leverage pada strategi yang sama
  python3 scripts/run_backtest.py --synthetic 2000 --strategy ma_crossover \
      --leverage-sweep
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.backtest import BacktestConfig, run_backtest
from forexlab.broker import BrokerConfig
from forexlab.control import permutation_test
from forexlab.data import load_csv, synthetic_gbm
from forexlab.risk import RiskLimits
from forexlab.strategies import REGISTRY


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Backtest strategi forex dengan mekanika margin yang sebenarnya.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sumber = parser.add_mutually_exclusive_group(required=True)
    sumber.add_argument("--csv", help="Berkas CSV harga, wajib punya kolom close")
    sumber.add_argument(
        "--synthetic",
        type=int,
        metavar="BATANG",
        help="Pakai data acak sepanjang N batang, untuk menguji mesinnya sendiri",
    )

    parser.add_argument(
        "--strategy",
        choices=sorted(REGISTRY),
        help="Satu strategi saja. Bila tidak disebut, semua strategi dijalankan.",
    )
    parser.add_argument("--balance", type=float, default=1_000_000.0, help="Modal awal")
    parser.add_argument("--leverage", type=int, default=100, help="Leverage broker")
    parser.add_argument("--spread-pips", type=float, default=1.5, help="Spread dalam pip")
    parser.add_argument(
        "--risk-per-trade",
        type=float,
        default=0.01,
        help="Kerugian maksimal per transaksi sebagai pecahan ekuitas",
    )
    parser.add_argument(
        "--control",
        type=int,
        default=0,
        metavar="N",
        help="Jalankan uji kendali dengan N percobaan acak. 200 adalah angka yang layak.",
    )
    parser.add_argument(
        "--leverage-sweep",
        action="store_true",
        help="Ulangi strategi yang sama pada beberapa tingkat leverage",
    )
    parser.add_argument("--seed", type=int, default=7, help="Benih angka acak")
    return parser


BENCHMARKS = ("coin_flip", "always_long")


def _ordered_strategies() -> list[str]:
    """Strategi sungguhan lebih dulu, pembanding selalu di baris terakhir."""
    real = sorted(name for name in REGISTRY if name not in BENCHMARKS)
    return real + [name for name in BENCHMARKS if name in REGISTRY]


def load_prices(args: argparse.Namespace):
    if args.csv:
        prices = load_csv(args.csv)
        label = Path(args.csv).name
    else:
        prices = synthetic_gbm(args.synthetic, seed=args.seed)
        label = f"data acak ({args.synthetic} batang)"
    return prices, label


def make_config(args: argparse.Namespace, leverage: int | None = None) -> BacktestConfig:
    return BacktestConfig(
        starting_balance=args.balance,
        broker=BrokerConfig(
            leverage=leverage if leverage is not None else args.leverage,
            spread_pips=args.spread_pips,
        ),
        limits=RiskLimits(risk_per_trade=args.risk_per_trade),
    )


def main() -> int:
    args = build_parser().parse_args()
    prices, label = load_prices(args)

    if len(prices) < 100:
        print(f"Peringatan: hanya {len(prices)} batang. Hasil di bawah 100 batang "
              f"tidak berarti apa-apa.", file=sys.stderr)

    chosen = [args.strategy] if args.strategy else _ordered_strategies()

    print()
    print(f"Sumber data : {label}")
    print(f"Rentang     : {prices.index[0].date()} sampai {prices.index[-1].date()} "
          f"({len(prices)} batang)")
    print(f"Modal awal  : {args.balance:,.0f}")
    print(f"Leverage    : 1:{args.leverage}   spread {args.spread_pips} pip   "
          f"risiko {args.risk_per_trade:.1%} per transaksi")
    print()

    if args.leverage_sweep:
        if not args.strategy:
            print("--leverage-sweep butuh --strategy", file=sys.stderr)
            return 2
        print(f"PENGARUH LEVERAGE PADA STRATEGI {args.strategy}")
        print("-" * 78)
        for leverage in (1, 5, 10, 30, 100, 500):
            result, _ = run_backtest(
                prices,
                REGISTRY[args.strategy](prices),
                make_config(args, leverage),
                f"1:{leverage}",
            )
            print(result.summary_line())
        print("-" * 78)
        print()
        print("Manajemen risiko di risk.py membatasi ukuran posisi berdasarkan")
        print("risiko per transaksi, bukan leverage broker. Karena itu menaikkan")
        print("leverage di atas kebutuhan tidak menambah keuntungan, hanya")
        print("menambah peluang tertutup paksa oleh broker.")
        print()
        return 0

    print("HASIL BACKTEST")
    print("-" * 78)
    for name in chosen:
        result, _ = run_backtest(prices, REGISTRY[name](prices), make_config(args), name)
        print(result.summary_line())
    print("-" * 78)
    print()
    if all(name in chosen for name in BENCHMARKS):
        print("Dua baris terakhir adalah pembanding wajib. coin_flip adalah lemparan")
        print("koin dan always_long adalah beli lalu diam. Strategi yang tidak")
        print("mengalahkan keduanya tidak layak dipakai.")
    else:
        print("Pembanding wajib tidak ikut dijalankan. Jalankan tanpa --strategy")
        print("untuk membandingkannya dengan lemparan koin dan beli-lalu-diam.")
    print()

    if args.control:
        for name in chosen:
            if name in BENCHMARKS:
                continue
            print("=" * 78)
            report = permutation_test(
                prices,
                REGISTRY[name],
                make_config(args),
                runs=args.control,
                seed=args.seed,
                strategy_name=name,
            )
            print(report.report_text())
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
