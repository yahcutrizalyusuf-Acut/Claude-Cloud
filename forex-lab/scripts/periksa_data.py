#!/usr/bin/env python3
"""Periksa berkas data harga sebelum dipakai menguji strategi.

Jalankan: python3 scripts/periksa_data.py data/BBCA.csv --market idx

Backtest paling teliti pun tidak berguna kalau datanya cacat. Jalankan ini
lebih dulu, setiap kali ada berkas baru.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.data import load_csv
from forexlab.quality import periksa, sesuaikan_pemecahan

GARIS = "=" * 76


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="Berkas CSV harga yang mau diperiksa")
    parser.add_argument(
        "--market",
        choices=("idx", "forex"),
        default="idx",
        help="Pasar asal data. Menentukan penafsiran angka seperti 7.400, "
        "yang berarti Rp 7.400 pada saham tapi 7,4 pada forex.",
    )
    parser.add_argument(
        "--perbaiki-pemecahan",
        metavar="BERKAS_KELUARAN",
        help="Tulis salinan yang harga lamanya sudah disesuaikan dengan "
        "pemecahan saham. Periksa laporannya lebih dulu dan pastikan "
        "dugaannya benar pemecahan saham, bukan kejatuhan harga sungguhan.",
    )
    args = parser.parse_args()

    try:
        prices = load_csv(args.csv, market=args.market)
    except (ValueError, FileNotFoundError) as galat:
        print(f"Berkas tidak bisa dibaca: {galat}", file=sys.stderr)
        return 1

    print()
    print(GARIS)
    print(f"  PEMERIKSAAN MUTU: {Path(args.csv).name}")
    print(GARIS)
    print()
    laporan = periksa(prices)
    print(laporan.laporan_teks())
    print()

    print("Lima baris pertama:")
    print(prices.head().to_string())
    print()
    print("Lima baris terakhir:")
    print(prices.tail().to_string())
    print()

    if laporan.dugaan_pemecahan:
        print(GARIS)
        print("  PEMECAHAN SAHAM TERDETEKSI, DATA TIDAK BOLEH DIPAKAI APA ADANYA")
        print(GARIS)
        print()
        print("Ketika satu lembar saham dipecah menjadi beberapa, harganya turun")
        print("sebanding dalam satu malam, padahal nilai kepemilikan pemegang")
        print("saham sama sekali tidak berubah. Kalau data belum disesuaikan,")
        print("backtest membaca itu sebagai kejatuhan harga yang tidak pernah")
        print("terjadi, dan seluruh hasilnya menjadi tidak berarti.")
        print()
        print("Dua pilihan:")
        print()
        print("1. Unduh ulang data yang sudah disesuaikan. Ini pilihan terbaik.")
        print("   Cari kolom bernama 'Adj Close' atau keterangan 'adjusted',")
        print("   karena sumber itu sudah memperhitungkan pemecahan dan dividen.")
        print()
        print("2. Sesuaikan berkas ini sendiri:")
        print()
        print(f"   python3 scripts/periksa_data.py {args.csv} \\")
        print(f"       --market {args.market} --perbaiki-pemecahan data/sudah_rapi.csv")
        print()
        print("   Pilihan kedua hanya menyesuaikan pemecahan saham, tidak")
        print("   dividen. Jadi pembanding beli lalu tahan akan terlihat lebih")
        print("   rendah daripada kenyataannya.")
        print()

    if args.perbaiki_pemecahan:
        if not laporan.dugaan_pemecahan:
            print("Tidak ada pemecahan saham yang perlu disesuaikan.")
            return 0
        rapi = sesuaikan_pemecahan(prices, laporan.dugaan_pemecahan)
        keluaran = Path(args.perbaiki_pemecahan)
        keluaran.parent.mkdir(parents=True, exist_ok=True)
        rapi.to_csv(keluaran)
        ulang = periksa(rapi)
        print(f"Salinan yang sudah disesuaikan ditulis ke {keluaran}")
        print(f"Dugaan pemecahan yang tersisa: {len(ulang.dugaan_pemecahan)}")
        print(f"Kesimpulan ulang: "
              f"{'LAYAK DIPAKAI' if ulang.layak_pakai else 'MASIH BELUM LAYAK'}")
        print()
        print("Periksa lima baris pertama di bawah ini. Harga lama seharusnya")
        print("kini berada pada skala yang sama dengan harga terbaru.")
        print(rapi.head().to_string())
        print()

    return 0 if laporan.layak_pakai else 2


if __name__ == "__main__":
    raise SystemExit(main())
