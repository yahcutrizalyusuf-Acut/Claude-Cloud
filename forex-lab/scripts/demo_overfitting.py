#!/usr/bin/env python3
"""Peraga: bagaimana mencoba banyak setelan menghasilkan robot palsu.

Jalankan: python3 scripts/demo_overfitting.py

Seluruh peraga ini berjalan pada data harga ACAK MURNI, yang dipastikan
tidak punya pola apa pun. Jadi tidak ada satu pun setelan yang pantas
untung. Kalau tetap ada yang untung, itu sepenuhnya kebetulan, dan di situlah
pelajarannya.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.backtest import BacktestConfig
from forexlab.broker import BrokerConfig
from forexlab.data import synthetic_gbm
from forexlab.strategies import moving_average_crossover
from forexlab.validation import parameter_sweep, walk_forward_test

GARIS = "=" * 76


def pabrik_ma(fast: int, slow: int):
    """Hasilkan penghasil sinyal rata-rata bergerak dengan setelan tertentu."""
    return lambda prices: moving_average_crossover(prices, fast=fast, slow=slow)


def main() -> None:
    prices = synthetic_gbm(2500, seed=4242)
    config = BacktestConfig(
        starting_balance=1_000_000,
        broker=BrokerConfig(leverage=100, spread_pips=1.5),
    )
    grid = {
        "fast": [3, 5, 8, 10, 13, 15, 20, 25, 30, 40],
        "slow": [40, 50, 60, 80, 100, 120, 150, 180, 200, 250],
    }

    print()
    print(GARIS)
    print("  DATA: HARGA ACAK MURNI, 2500 HARI, TANPA POLA SAMA SEKALI")
    print(GARIS)
    print()

    tabel = parameter_sweep(prices, pabrik_ma, grid, config)

    print(f"Dicoba {len(tabel)} kombinasi setelan pada data yang sama.")
    print()
    print("LIMA SETELAN TERBAIK, cara orang memamerkan robotnya:")
    print("-" * 76)
    print(f"{'cepat':>7} {'lambat':>8} {'keuntungan':>13} {'turun terdalam':>16} {'transaksi':>11}")
    print("-" * 76)
    for _, baris in tabel.head(5).iterrows():
        print(f"{int(baris['fast']):>7} {int(baris['slow']):>8} "
              f"{baris['total_return']:>12.1%} {baris['max_drawdown']:>15.1%} "
              f"{int(baris['trades']):>11}")
    print("-" * 76)
    print()
    print("LIMA SETELAN TERBURUK, dari percobaan yang sama:")
    print("-" * 76)
    for _, baris in tabel.tail(5).iterrows():
        print(f"{int(baris['fast']):>7} {int(baris['slow']):>8} "
              f"{baris['total_return']:>12.1%} {baris['max_drawdown']:>15.1%} "
              f"{int(baris['trades']):>11}")
    print("-" * 76)
    print()
    print(f"Rata-rata seluruh {len(tabel)} kombinasi : "
          f"{tabel['total_return'].mean():+.1%}")
    print(f"Kombinasi yang untung             : "
          f"{(tabel['total_return'] > 0).mean():.1%}")
    print()
    print("Inilah jebakannya. Setelan terbaik di tabel atas akan terlihat")
    print("meyakinkan di tangkapan layar mana pun, lengkap dengan grafik yang")
    print("menanjak. Padahal datanya acak, jadi angka itu tidak mengandung")
    print("informasi apa pun. Yang terjadi hanya satu: dari seratus percobaan,")
    print("selalu ada yang kebetulan bagus.")
    print()

    print(GARIS)
    print("  UJI YANG SEBENARNYA: SETEL DI DATA LAMA, UJI DI DATA BARU")
    print(GARIS)
    print()

    laporan = walk_forward_test(
        prices, pabrik_ma, grid, config,
        train_bars=500, test_bars=125, strategy_name="ma_crossover",
    )
    print(laporan.report_text())
    print()
    print("Rincian per jendela:")
    print("-" * 76)
    print(f"{'jendela':>8} {'cepat':>7} {'lambat':>8} {'saat disetel':>14} {'saat diuji':>13}")
    print("-" * 76)
    for _, baris in laporan.detail.iterrows():
        print(f"{int(baris['window']):>8} {int(baris['best_fast']):>7} "
              f"{int(baris['best_slow']):>8} {baris['in_sample_return']:>13.1%} "
              f"{baris['out_of_sample_return']:>12.1%}")
    print("-" * 76)
    print()
    print("Perhatikan dua hal.")
    print()
    print("Pertama, kolom 'saat disetel' hampir selalu positif, dan kolom")
    print("'saat diuji' naik turun tanpa pola. Itu tanda khas setelan yang")
    print("cocok dengan masa lalu, bukan dengan pasar.")
    print()
    print("Kedua, kolom cepat dan lambat berubah-ubah dari jendela ke jendela.")
    print("Kalau setelan itu benar-benar menangkap sesuatu yang nyata, nilainya")
    print("akan cenderung stabil. Yang berpindah-pindah setiap kali data baru")
    print("masuk sedang mengejar kebetulan, bukan menemukan aturan.")
    print()
    print("Aturan yang dipakai di proyek ini: hanya kolom 'saat diuji' yang")
    print("dihitung. Hasil di potongan setel dibuang, seberapa pun indahnya.")
    print()


if __name__ == "__main__":
    main()
