#!/usr/bin/env python3
"""Unduh data harga saham langsung, tanpa perlu mencari berkas sendiri.

Contoh pemakaian:

  python3 scripts/unduh_data.py BBCA
  python3 scripts/unduh_data.py BBRI TLKM ASII --tahun 10
  python3 scripts/unduh_data.py BBCA --keluaran data/BBCA.csv

Kode saham Indonesia otomatis diberi akhiran .JK, yang dipakai penyedia data
untuk menandai Bursa Efek Indonesia. Kode asing bisa ditulis apa adanya.

Harga yang diambil adalah harga yang sudah disesuaikan dengan pemecahan
saham dan dividen. Itu penting: harga mentah BBCA memuat pemecahan saham
yang akan terbaca sebagai kejatuhan 80 persen yang tidak pernah terjadi.

CATATAN: skrip ini butuh akses jaringan ke penyedia data. Bila lingkungan
kerja memblokirnya, skrip akan berhenti dengan keterangan yang jelas, bukan
diam-diam gagal.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import requests

SUMBER = "https://query1.finance.yahoo.com/v8/finance/chart"
PENGENAL_PERAMBAH = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
BATAS_WAKTU_DETIK = 30


def kode_lengkap(kode: str) -> str:
    """Lengkapi kode saham Indonesia dengan akhiran bursanya.

    Kode saham di Bursa Efek Indonesia selalu empat huruf, seperti BBCA dan
    TLKM, sehingga hanya bentuk itu yang diberi akhiran .JK. Kode lain
    dibiarkan apa adanya, karena EURUSD=X dan ^JKSE bukan saham Indonesia dan
    akan rusak kalau diberi akhiran.

    Satu kasus memang ikut terkena: saham asing yang kodenya juga empat
    huruf, misalnya AAPL, akan menjadi AAPL.JK. Untuk kode seperti itu,
    tulis akhiran bursanya sendiri, misalnya AAPL.US.
    """
    kode = kode.strip().upper()
    if "." in kode:
        return kode
    if len(kode) == 4 and kode.isascii() and kode.isalpha():
        return f"{kode}.JK"
    return kode


def unduh(kode: str, tahun: int = 10) -> pd.DataFrame:
    """Ambil harga harian satu saham, sudah disesuaikan pemecahan dan dividen."""
    simbol = kode_lengkap(kode)
    alamat = f"{SUMBER}/{simbol}"
    parameter = {"range": f"{tahun}y", "interval": "1d", "events": "div,split"}

    tanggapan = requests.get(
        alamat,
        params=parameter,
        headers={"User-Agent": PENGENAL_PERAMBAH},
        timeout=BATAS_WAKTU_DETIK,
    )
    tanggapan.raise_for_status()
    isi = tanggapan.json()

    hasil = (isi.get("chart") or {}).get("result")
    if not hasil:
        galat = ((isi.get("chart") or {}).get("error") or {}).get("description")
        raise ValueError(f"{simbol}: penyedia data tidak mengembalikan harga. {galat or ''}")

    satu = hasil[0]
    waktu = satu.get("timestamp")
    if not waktu:
        raise ValueError(f"{simbol}: tidak ada data harga pada rentang ini.")

    petunjuk = satu["indicators"]
    kutipan = petunjuk["quote"][0]
    # Harga yang sudah disesuaikan dipakai bila tersedia. Tanpa itu,
    # pemecahan saham akan terbaca sebagai kejatuhan harga.
    disesuaikan = (petunjuk.get("adjclose") or [{}])[0].get("adjclose")

    frame = pd.DataFrame(
        {
            "open": kutipan.get("open"),
            "high": kutipan.get("high"),
            "low": kutipan.get("low"),
            "close": disesuaikan if disesuaikan else kutipan.get("close"),
            "volume": kutipan.get("volume"),
        },
        index=pd.to_datetime(waktu, unit="s").tz_localize(None).normalize(),
    )
    frame.index.name = "datetime"
    return frame.dropna(subset=["close"]).sort_index()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("kode", nargs="+", help="Kode saham, misalnya BBCA BBRI TLKM")
    parser.add_argument("--tahun", type=int, default=10, help="Panjang riwayat harga")
    parser.add_argument(
        "--keluaran",
        help="Nama berkas keluaran. Hanya berlaku bila satu kode saja; "
        "untuk beberapa kode, berkasnya dinamai data/KODE.csv",
    )
    args = parser.parse_args()

    if args.keluaran and len(args.kode) > 1:
        print("--keluaran hanya berlaku untuk satu kode saham.", file=sys.stderr)
        return 2

    folder = Path(__file__).resolve().parents[1] / "data"
    folder.mkdir(parents=True, exist_ok=True)
    gagal = 0

    for kode in args.kode:
        try:
            frame = unduh(kode, args.tahun)
        except requests.exceptions.RequestException as galat:
            gagal += 1
            print(f"{kode}: tidak bisa menghubungi penyedia data.", file=sys.stderr)
            print(f"  Sebabnya: {type(galat).__name__}", file=sys.stderr)
            print(
                "  Kemungkinan besar jaringan lingkungan kerja ini memblokir "
                "query1.finance.yahoo.com.",
                file=sys.stderr,
            )
            print(
                "  Buka menu cloud environment di judul sesi, pilih Edit, lalu "
                "tambahkan host itu di Allowed domains.",
                file=sys.stderr,
            )
            continue
        except (ValueError, KeyError, IndexError) as galat:
            gagal += 1
            print(f"{kode}: {galat}", file=sys.stderr)
            continue

        tujuan = Path(args.keluaran) if args.keluaran else folder / f"{kode.upper()}.csv"
        tujuan.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(tujuan)

        print(
            f"{kode.upper():<8} {len(frame):>5} baris  "
            f"{frame.index[0].date()} sampai {frame.index[-1].date()}  "
            f"harga {frame['close'].iloc[0]:,.0f} ke {frame['close'].iloc[-1]:,.0f}  "
            f"-> {tujuan}"
        )

    if gagal:
        return 1

    print()
    print("Langkah berikutnya:")
    print(f"  python3 scripts/periksa_data.py data/{args.kode[0].upper()}.csv --market idx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
