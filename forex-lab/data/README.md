# Tempat berkas data harga

Letakkan berkas CSV harga yang diunduh sendiri di folder ini, lalu jalankan:

```bash
python3 scripts/run_backtest.py --csv data/NAMA_BERKAS.csv --control 200
```

Syarat berkas: satu kolom waktu (`date`, `datetime`, `time`, `timestamp`,
atau `Gmt time`) dan satu kolom `close`. Kolom `open`, `high`, `low`
bersifat pilihan tetapi sangat dianjurkan, karena membuat pengujian stop
loss jauh lebih akurat.

Berkas CSV tidak disertakan ke dalam repositori ini.
