#!/usr/bin/env python3
"""Peraga: berapa harga sebenarnya dari "beli murah, jual cepat saat naik".

Jalankan: python3 scripts/demo_biaya_saham.py

Rencana itu terdengar masuk akal, dan hampir semua pemula memulainya dari
sana. Yang jarang dihitung lebih dulu adalah biayanya. Satu putaran beli
lalu jual di Bursa Efek Indonesia menelan sekitar 0,4 persen dalam bentuk
komisi, ditambah selisih harga beli-jual yang besarnya mengikuti fraksi
harga saham.

Biaya itu dibayar setiap kali, menang atau kalah. Jadi makin sering
bertransaksi, makin besar bagian keuntungan yang hilang sebelum sampai ke
tangan Anda.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.backtest import BacktestConfig, benchmark_config, run_backtest
from forexlab.broker import IDX_BROKER, SimulatedBroker, idx_tick_size
from forexlab.data import synthetic_gbm
from forexlab.risk import RiskLimits
from forexlab.strategies import always_long, coin_flip, moving_average_crossover

GARIS = "=" * 76
MODAL = 10_000_000.0


def biaya_satu_putaran(harga: float) -> dict:
    """Hitung biaya nyata satu putaran beli lalu jual pada harga tertentu."""
    broker = SimulatedBroker(MODAL, IDX_BROKER)
    units = (broker.max_units(harga) // 100) * 100
    if units <= 0:
        return {"harga": harga, "mungkin": False}

    broker.open_position(1, units, harga, 0)
    broker.close_position(harga, 1, "uji")
    rugi = MODAL - broker.balance
    nilai = units * harga

    return {
        "harga": harga,
        "mungkin": True,
        "lot": units / 100,
        "nilai": nilai,
        "fraksi": idx_tick_size(harga),
        "rugi": rugi,
        "persen": rugi / nilai,
    }


def main() -> None:
    print()
    print(GARIS)
    print(f"  BIAYA SATU PUTARAN BELI LALU JUAL, MODAL Rp {MODAL:,.0f}")
    print(GARIS)
    print()
    print(f"{'Harga saham':>13} {'Fraksi':>8} {'Lot':>7} {'Biaya rupiah':>15} {'Persen':>9}")
    print("-" * 76)
    for harga in (150.0, 450.0, 1_200.0, 3_500.0, 8_000.0):
        baris = biaya_satu_putaran(harga)
        if not baris["mungkin"]:
            continue
        print(f"{baris['harga']:>13,.0f} {baris['fraksi']:>8,.0f} "
              f"{baris['lot']:>7,.0f} {baris['rugi']:>15,.0f} {baris['persen']:>8.2%}")
    print("-" * 76)
    print()
    print("Harga belum bergerak sedikit pun, tapi uang sudah berkurang.")
    print("Komisi menyumbang 0,4 persen, sisanya selisih harga beli-jual.")
    print("Saham murah justru lebih mahal diperdagangkan, karena fraksi")
    print("harga Rp 1 pada saham Rp 150 setara 0,67 persen, sementara pada")
    print("saham Rp 8.000 fraksi Rp 25 hanya setara 0,31 persen.")
    print()

    print(GARIS)
    print("  BERAPA BIAYA SETAHUN, MENURUT SEBERAPA SERING BERTRANSAKSI")
    print(GARIS)
    print()
    satu_putaran = biaya_satu_putaran(3_500.0)["persen"]
    print(f"Memakai biaya satu putaran {satu_putaran:.2%} pada saham Rp 3.500:")
    print()
    print(f"{'Gaya':<26} {'Putaran/tahun':>15} {'Biaya setahun':>16}")
    print("-" * 76)
    for gaya, putaran in (
        ("Beli lalu tahan", 1),
        ("Sekali sebulan", 12),
        ("Sekali dua minggu", 26),
        ("Sekali sepekan", 52),
        ("Dua kali sepekan", 104),
        ("Harian", 250),
    ):
        print(f"{gaya:<26} {putaran:>15} {putaran * satu_putaran:>15.1%}")
    print("-" * 76)
    print()
    print("Baris 'Harian' itu yang perlu diperhatikan. Bertransaksi setiap")
    print("hari menelan biaya lebih dari dua kali modal dalam setahun. Artinya")
    print("strategi harian harus menghasilkan keuntungan kotor di atas angka")
    print("itu hanya untuk kembali ke titik nol.")
    print()
    print("Bandingkan dengan harapan keuntungan pasar saham jangka panjang,")
    print("yang biasanya 8 sampai 12 persen setahun. Pada tiga baris terbawah,")
    print("biaya sudah melampaui seluruh harapan keuntungan itu.")
    print()

    print(GARIS)
    print("  UJI LANGSUNG: SERING BERTRANSAKSI VERSUS BELI LALU TAHAN")
    print(GARIS)
    print()
    prices = synthetic_gbm(
        2_500, start_price=3_500.0, daily_volatility=0.018, drift=0.0004, seed=18
    )
    naik_pasar = float(prices["close"].iloc[-1] / prices["close"].iloc[0] - 1)

    limits = RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0)
    # Beli lalu tahan tidak memakai stop loss; itu memang definisinya. Strategi
    # aktif memakai stop loss, karena tanpa itu satu kesalahan bisa menghapus
    # modal. Perbedaan ini disengaja dan ikut dihitung sebagai biaya masing-masing.
    dengan_stop = BacktestConfig(
        starting_balance=MODAL, broker=IDX_BROKER, limits=limits,
        long_only=True, use_stops=True,
    )
    # Pembanding beli lalu tahan dijalankan tanpa stop loss dan tanpa batas
    # penurunan, karena itu memang definisinya. Lihat benchmark_config.
    tanpa_stop = benchmark_config(dengan_stop)

    print(f"Data: saham sintetis 2.500 hari, sekitar 10 tahun bursa.")
    print(f"Harga naik {naik_pasar:+.1%} sepanjang periode, jadi pasarnya memang naik.")
    print()
    print(f"{'Strategi':<26} {'Hasil':>9} {'Transaksi':>11} {'Biaya':>14} "
          f"{'Biaya/modal':>13}")
    print("-" * 76)

    baris = [
        ("beli lalu tahan", always_long(prices), tanpa_stop),
        ("beli lalu tahan + stop", always_long(prices), dengan_stop),
        ("rata-rata bergerak 20/50", moving_average_crossover(prices, 20, 50), dengan_stop),
        ("rata-rata cepat 3/10", moving_average_crossover(prices, 3, 10), dengan_stop),
        ("lemparan koin", coin_flip(prices, hold_bars=3, seed=5), dengan_stop),
    ]
    for nama, sinyal, konfigurasi in baris:
        hasil, _ = run_backtest(prices, sinyal, konfigurasi, nama)
        print(f"{nama:<26} {hasil.total_return:>8.1%} {hasil.trades:>11} "
              f"{hasil.total_costs:>14,.0f} {hasil.total_costs / MODAL:>12.1%}")
    print("-" * 76)
    print()
    print("Baris pertama adalah satu kali beli lalu didiamkan sampai akhir.")
    print("Biayanya sekali saja, dan hasilnya mengikuti pasar.")
    print()
    print("Baris kedua strategi yang sama, tapi dengan stop loss. Stop loss")
    print("melindungi dari kerugian besar, dan harganya adalah transaksi yang")
    print("jauh lebih banyak. Perlindungan itu tidak gratis.")
    print()
    print("Tiga baris terakhir strategi aktif. Perhatikan kolom paling kanan:")
    print("makin sering bertransaksi, makin besar bagian modal yang berpindah")
    print("ke biaya, dan itu terjadi tanpa memandang benar atau salah tebakannya.")
    print()
    print("Inilah sebabnya rencana 'beli murah, jual cepat saat naik' sulit")
    print("menguntungkan di pasar yang naik. Bukan karena menebak arah itu")
    print("mustahil, tetapi karena setiap tebakan dikenai ongkos yang pasti,")
    print("sementara keuntungannya tidak pasti.")
    print()


if __name__ == "__main__":
    main()
