#!/usr/bin/env python3
"""Peraga: apa yang sebenarnya terjadi pada akun berleverage tinggi.

Jalankan: python3 scripts/demo_leverage.py

Skrip ini memakai simulasi broker yang sama dengan mesin backtest, jadi
angka yang keluar bukan ilustrasi karangan, melainkan hasil perhitungan
margin yang sama dengan yang dipakai menguji strategi.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.broker import UNITS_PER_LOT, BrokerConfig, SimulatedBroker

START_PRICE = 1.1000
MODAL = 500_000.0  # rupiah, diperlakukan sebagai satuan mata uang akun


def jarak_stop_out(leverage: int, pakai_margin_penuh: bool = True) -> dict:
    """Hitung seberapa jauh harga boleh bergerak sebelum broker menutup paksa."""
    config = BrokerConfig(leverage=leverage, spread_pips=1.5, swap_per_lot_per_day=0.0)
    broker = SimulatedBroker(MODAL, config)

    units = broker.max_units(START_PRICE) if pakai_margin_penuh else MODAL / START_PRICE
    if units < UNITS_PER_LOT * 0.01:
        return {"leverage": leverage, "mungkin": False}

    broker.open_position(1, units, START_PRICE, 0)

    # Turunkan harga setahap 0,00001 sampai broker melakukan stop out.
    harga = START_PRICE
    langkah = 0.00001
    while harga > START_PRICE * 0.5:
        harga -= langkah
        if broker.margin_level(harga) < config.stop_out_level:
            break

    gerak = (START_PRICE - harga) / START_PRICE
    ekuitas_sisa = broker.equity(harga)

    return {
        "leverage": leverage,
        "mungkin": True,
        "ukuran_posisi": units * START_PRICE,
        "lot": units / UNITS_PER_LOT,
        "gerak_sampai_stop_out": gerak,
        "sisa_modal": max(ekuitas_sisa, 0.0),
        "rugi": 1.0 - max(ekuitas_sisa, 0.0) / MODAL,
    }


def main() -> None:
    print()
    print("=" * 78)
    print(f"  MODAL {MODAL:,.0f}  |  seluruh jaminan dipakai untuk satu posisi")
    print("=" * 78)
    print()
    print(f"{'Leverage':>9} {'Ukuran posisi':>18} {'Lot':>7} "
          f"{'Gerak ke stop out':>19} {'Sisa modal':>14}")
    print("-" * 78)

    for leverage in (1, 5, 10, 30, 100, 200, 500):
        baris = jarak_stop_out(leverage)
        if not baris["mungkin"]:
            print(f"{leverage:>9} {'posisi terlalu kecil untuk dibuka':>60}")
            continue
        print(
            f"{baris['leverage']:>9} "
            f"{baris['ukuran_posisi']:>18,.0f} "
            f"{baris['lot']:>7.2f} "
            f"{baris['gerak_sampai_stop_out']:>18.3%} "
            f"{baris['sisa_modal']:>14,.0f}"
        )

    print("-" * 78)
    print()
    print("Cara membacanya:")
    print("  Kolom keempat adalah seberapa jauh harga boleh bergerak melawan")
    print("  posisi sebelum broker menutupnya secara paksa. Pada leverage 500,")
    print("  pergerakan sekitar sepersepuluh persen sudah cukup. Pasangan mata")
    print("  uang besar bergerak sejauh itu beberapa kali dalam satu hari biasa,")
    print("  tanpa perlu berita apa pun.")
    print()
    print("  Leverage tidak membuat strategi jadi lebih baik. Dia hanya")
    print("  mempercepat hasil ke arah mana pun hasil itu menuju.")
    print()

    print("=" * 78)
    print("  SATU HAL LAGI: BIAYA SPREAD SAJA SUDAH MEMAKAN MODAL")
    print("=" * 78)
    print()
    print(f"{'Leverage':>9} {'Rugi seketika saat posisi dibuka':>40} {'Persen modal':>15}")
    print("-" * 78)
    for leverage in (1, 10, 100, 500):
        config = BrokerConfig(leverage=leverage, spread_pips=1.5, swap_per_lot_per_day=0.0)
        broker = SimulatedBroker(MODAL, config)
        units = broker.max_units(START_PRICE)
        if units < UNITS_PER_LOT * 0.01:
            continue
        broker.open_position(1, units, START_PRICE, 0)
        rugi_awal = MODAL - broker.equity(START_PRICE)
        print(f"{leverage:>9} {rugi_awal:>40,.0f} {rugi_awal / MODAL:>15.2%}")
    print("-" * 78)
    print()
    print("  Spread 1,5 pip terdengar kecil. Dengan leverage 500 dan jaminan")
    print("  penuh, biaya itu langsung menghapus sekitar 7 persen modal pada")
    print("  detik posisi dibuka, sebelum harga bergerak sedikit pun. Harga")
    print("  harus bergerak sejauh itu dulu hanya untuk kembali ke titik nol,")
    print("  dan biaya yang sama dibayar lagi di setiap transaksi berikutnya.")
    print()


if __name__ == "__main__":
    main()
