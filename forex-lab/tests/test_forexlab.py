"""Tes untuk bagian yang kalau salah akan membuat seluruh hasil bohong.

Jalankan: python3 -m pytest tests/ -q   (atau python3 tests/test_forexlab.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.backtest import BacktestConfig, benchmark_config, run_backtest
from forexlab.broker import (
    IDX_BROKER,
    UNITS_PER_LOT,
    BrokerConfig,
    SimulatedBroker,
    idx_tick_size,
)
from forexlab.control import permutation_test
from forexlab.data import (
    bersihkan_angka,
    bersihkan_kolom,
    block_bootstrap_returns,
    load_csv,
    log_returns,
    shuffle_returns,
    synthetic_gbm,
)
from forexlab.quality import deteksi_pemecahan, periksa, sesuaikan_pemecahan
from forexlab.metrics import max_drawdown, sharpe_ratio
from forexlab.risk import RiskLimits, position_size
from forexlab.strategies import REGISTRY, moving_average_crossover
from forexlab.validation import (
    expand_grid,
    parameter_sweep,
    walk_forward_test,
    walk_forward_windows,
)


# --- spread selalu merugikan pedagang ------------------------------------

def test_spread_dibayar_di_kedua_arah():
    broker = SimulatedBroker(10_000, BrokerConfig(leverage=10, spread_pips=2.0))
    assert broker.ask(1.1000) > 1.1000 > broker.bid(1.1000)


def test_posisi_langsung_rugi_sebesar_spread():
    """Posisi yang baru dibuka harus langsung merugi, bukan nol."""
    config = BrokerConfig(leverage=10, spread_pips=2.0, swap_per_lot_per_day=0.0)
    broker = SimulatedBroker(100_000, config)
    broker.open_position(1, UNITS_PER_LOT, 1.1000, 0)
    assert broker.floating_profit(1.1000) < 0
    expected = -UNITS_PER_LOT * config.spread_pips * config.pip_size
    assert np.isclose(broker.floating_profit(1.1000), expected)


def test_posisi_jual_juga_membayar_spread():
    config = BrokerConfig(leverage=10, spread_pips=2.0, swap_per_lot_per_day=0.0)
    broker = SimulatedBroker(100_000, config)
    broker.open_position(-1, UNITS_PER_LOT, 1.1000, 0)
    assert broker.floating_profit(1.1000) < 0


# --- margin dan stop out --------------------------------------------------

def test_margin_sebanding_dengan_ukuran_dibagi_leverage():
    broker = SimulatedBroker(100_000, BrokerConfig(leverage=100, spread_pips=0.0))
    position = broker.open_position(1, UNITS_PER_LOT, 1.1000, 0)
    assert np.isclose(position.margin, UNITS_PER_LOT * 1.1000 / 100)


def test_leverage_lebih_tinggi_berarti_stop_out_lebih_dekat():
    """Inti pelajarannya: leverage memperpendek jarak ke penutupan paksa."""
    jarak = {}
    for leverage in (10, 100, 500):
        config = BrokerConfig(leverage=leverage, spread_pips=0.0, swap_per_lot_per_day=0.0)
        broker = SimulatedBroker(500_000, config)
        broker.open_position(1, broker.max_units(1.1000), 1.1000, 0)
        harga = 1.1000
        while harga > 0.5 and broker.margin_level(harga) >= config.stop_out_level:
            harga -= 0.00001
        jarak[leverage] = 1.1000 - harga
    assert jarak[10] > jarak[100] > jarak[500]


def test_stop_out_menutup_posisi_dan_menandai_akun():
    config = BrokerConfig(leverage=500, spread_pips=0.0, swap_per_lot_per_day=0.0)
    broker = SimulatedBroker(500_000, config)
    broker.open_position(1, broker.max_units(1.1000), 1.1000, 0)
    broker.enforce_margin(1.0950, 1)
    assert broker.stopped_out
    assert broker.position is None
    assert len(broker.trades) == 1
    assert broker.trades[0].reason == "stop_out"


def test_perlindungan_saldo_negatif():
    """Dengan perlindungan aktif, saldo tidak boleh minus."""
    config = BrokerConfig(leverage=500, spread_pips=0.0, swap_per_lot_per_day=0.0,
                          negative_balance_protection=True)
    broker = SimulatedBroker(500_000, config)
    broker.open_position(1, broker.max_units(1.1000), 1.1000, 0)
    broker.enforce_margin(0.9000, 1)  # harga melompat jauh, seperti gap akhir pekan
    assert broker.balance >= 0.0


def test_tanpa_perlindungan_saldo_bisa_minus():
    config = BrokerConfig(leverage=500, spread_pips=0.0, swap_per_lot_per_day=0.0,
                          negative_balance_protection=False)
    broker = SimulatedBroker(500_000, config)
    broker.open_position(1, broker.max_units(1.1000), 1.1000, 0)
    broker.enforce_margin(0.9000, 1)
    assert broker.balance < 0.0


def test_ukuran_posisi_dibatasi_jaminan():
    """Permintaan yang lebih besar dari jaminan harus dipotong, bukan diterima.

    Kapasitas diukur sebelum posisi dibuka. Sesudah dibuka, jaminan sudah
    terpakai sehingga kapasitas tersisa mendekati nol.
    """
    broker = SimulatedBroker(1_000, BrokerConfig(leverage=10, spread_pips=0.0))
    kapasitas = broker.max_units(1.1000)
    position = broker.open_position(1, 100 * UNITS_PER_LOT, 1.1000, 0)
    assert position.units <= kapasitas + 1e-6
    assert position.units < 100 * UNITS_PER_LOT
    assert broker.free_margin(1.1000) < kapasitas * 1.1000 / 10


# --- manajemen risiko ----------------------------------------------------

def test_ukuran_posisi_menghormati_risiko_per_transaksi():
    broker = SimulatedBroker(1_000_000, BrokerConfig(leverage=100, spread_pips=0.0))
    limits = RiskLimits(risk_per_trade=0.01, max_effective_leverage=50)
    units = position_size(broker, 1.1000, 0.0050, limits)
    kerugian_saat_stop = units * 0.0050
    assert kerugian_saat_stop <= 1_000_000 * 0.01 * 1.001


def test_risiko_per_transaksi_berlebihan_ditolak():
    for nilai in (0.0, 0.10, -0.01):
        try:
            RiskLimits(risk_per_trade=nilai)
        except ValueError:
            continue
        raise AssertionError(f"risk_per_trade={nilai} seharusnya ditolak")


def test_leverage_efektif_dibatasi():
    broker = SimulatedBroker(1_000_000, BrokerConfig(leverage=500, spread_pips=0.0))
    limits = RiskLimits(risk_per_trade=0.05, max_effective_leverage=5)
    units = position_size(broker, 1.1000, 0.0001, limits)
    assert units * 1.1000 <= 1_000_000 * 5 * 1.001


# --- mesin backtest tidak boleh melihat masa depan -----------------------

def _seri_lompatan(bars: int, bar_lompatan: int, besar: float = 0.01):
    """Harga datar, lalu melompat sekali pada batang tertentu.

    Bentuk ini membuat waktu eksekusi bisa diuji secara pasti: entah posisi
    terbuka sebelum lompatan dan menangkapnya, atau sesudah dan tidak.
    """
    index = pd.date_range("2020-01-01", periods=bars, freq="D")
    closes = np.full(bars, 1.1000)
    closes[bar_lompatan:] += besar
    return pd.DataFrame({"close": closes}, index=index)


def _config_tanpa_stop():
    return BacktestConfig(
        starting_balance=1_000_000,
        broker=BrokerConfig(leverage=10, spread_pips=1.0, swap_per_lot_per_day=0.0),
        limits=RiskLimits(risk_per_trade=0.01, max_effective_leverage=10),
        use_stops=False,
    )


def test_sinyal_tidak_dieksekusi_pada_batang_yang_menghasilkannya():
    """Sinyal di batang 4 tidak boleh menangkap lompatan di batang 5.

    Mesin mengeksekusi sinyal batang 4 pada harga penutupan batang 5, yaitu
    SESUDAH lompatan terjadi. Jadi keuntungannya harus nol, hanya dikurangi
    spread. Kalau tes ini menunjukkan keuntungan, mesin mengeksekusi di
    batang yang sama dengan sinyalnya, dan itu kebocoran data masa depan.
    """
    prices = _seri_lompatan(bars=40, bar_lompatan=5)
    signals = pd.Series(0, index=prices.index, dtype=int)
    signals.iloc[4] = 1

    result, _ = run_backtest(prices, signals, _config_tanpa_stop(), "uji_geser")
    assert result.total_return <= 0.0, (
        f"keuntungan {result.total_return:+.4%} seharusnya tidak ada; "
        "mesin menangkap lompatan yang belum terjadi saat sinyal muncul"
    )


def test_sinyal_dieksekusi_tepat_satu_batang_kemudian():
    """Sinyal di batang 4 harus menangkap lompatan di batang 6.

    Pasangan dari tes sebelumnya. Bersama-sama keduanya memaku jarak
    eksekusi tepat satu batang: tidak nol, dan tidak dua.
    """
    prices = _seri_lompatan(bars=40, bar_lompatan=6)
    signals = pd.Series(0, index=prices.index, dtype=int)
    signals.iloc[4] = 1

    result, _ = run_backtest(prices, signals, _config_tanpa_stop(), "uji_geser")
    assert result.total_return > 0.0, (
        f"keuntungan {result.total_return:+.4%}; posisi seharusnya sudah "
        "terbuka sebelum lompatan di batang 6"
    )


def test_peramal_tidak_untung_pada_data_acak():
    """Sinyal yang tahu arah batang berikutnya tetap tidak untung di data acak.

    Karena mesin menggeser eksekusi satu batang, pengetahuan masa depan itu
    hilang seluruhnya. Pada data acak tidak ada momentum yang bisa
    menggantikannya, jadi hasilnya harus di sekitar nol atau merugi.
    """
    prices = synthetic_gbm(1200, seed=21)
    closes = prices["close"].to_numpy()
    arah_berikutnya = np.sign(np.diff(closes, append=closes[-1])).astype(int)
    signals = pd.Series(arah_berikutnya, index=prices.index)

    result, _ = run_backtest(prices, signals, _config_tanpa_stop(), "peramal")
    assert result.total_return < 0.25, (
        f"keuntungan {result.total_return:+.1%} terlalu tinggi untuk data acak; "
        "mesin mungkin membocorkan data masa depan"
    )


def test_batas_penurunan_menghentikan_perdagangan():
    """Setelah batas penurunan tersentuh, ekuitas harus berhenti bergerak."""
    prices = synthetic_gbm(800, daily_volatility=0.02, drift=-0.01, seed=3)
    config = BacktestConfig(
        starting_balance=1_000_000,
        broker=BrokerConfig(leverage=100),
        limits=RiskLimits(max_total_drawdown=0.10),
    )
    result, equity = run_backtest(prices, REGISTRY["always_long"](prices), config, "uji")
    assert result.max_drawdown <= 0.35
    assert equity.iloc[-1] == equity.iloc[-50:].iloc[0] or result.max_drawdown < 0.10


def test_kurva_ekuitas_sepanjang_data():
    prices = synthetic_gbm(300, seed=4)
    result, equity = run_backtest(
        prices, moving_average_crossover(prices), BacktestConfig(), "ma"
    )
    assert len(equity) == len(prices)
    assert result.bars == len(prices)


def test_semua_strategi_jalan_tanpa_galat():
    prices = synthetic_gbm(500, seed=5)
    for name, fungsi in REGISTRY.items():
        result, _ = run_backtest(prices, fungsi(prices), BacktestConfig(), name)
        assert np.isfinite(result.total_return), name


# --- data dan uji kendali ------------------------------------------------

def test_pengacakan_mempertahankan_sebaran_return():
    prices = synthetic_gbm(600, seed=6)
    asli = log_returns(prices["close"])
    diacak = log_returns(shuffle_returns(prices, seed=1)["close"])
    assert np.isclose(np.sort(asli), np.sort(diacak)).all()


def test_bootstrap_blok_menjaga_panjang_data():
    prices = synthetic_gbm(600, seed=7)
    assert len(block_bootstrap_returns(prices, block_size=20, seed=2)) == len(prices)


def test_uji_kendali_menolak_strategi_tanpa_keunggulan():
    """Pada data acak murni, tidak ada strategi yang boleh dinyatakan unggul."""
    prices = synthetic_gbm(900, seed=8)
    laporan = permutation_test(
        prices,
        moving_average_crossover,
        BacktestConfig(broker=BrokerConfig(leverage=100)),
        runs=40,
        seed=9,
        strategy_name="ma_crossover",
    )
    assert not laporan.has_edge
    assert 0.0 < laporan.p_value <= 1.0


# --- metrik ---------------------------------------------------------------

def test_penurunan_terdalam():
    assert np.isclose(max_drawdown(np.array([100.0, 150.0, 75.0, 120.0])), 0.5)
    assert max_drawdown(np.array([100.0, 101.0, 102.0])) == 0.0
    assert 0.0 <= max_drawdown(np.array([100.0, 0.0])) <= 1.0


def test_sharpe_aman_untuk_masukan_aneh():
    assert sharpe_ratio(np.array([100.0])) == 0.0
    assert sharpe_ratio(np.array([100.0, 100.0, 100.0])) == 0.0
    assert np.isfinite(sharpe_ratio(np.array([100.0, 0.0, 50.0, 60.0])))


# --- uji di luar sampel ---------------------------------------------------

def _pabrik_ma(fast: int, slow: int):
    return lambda prices: moving_average_crossover(prices, fast=fast, slow=slow)


def test_jendela_uji_tidak_tumpang_tindih():
    """Potongan uji harus benar-benar terpisah, atau hasilnya dihitung ganda."""
    windows = walk_forward_windows(2000, train_bars=500, test_bars=125)
    for lebih_awal, berikutnya in zip(windows, windows[1:]):
        assert lebih_awal.test_end <= berikutnya.test_start


def test_potongan_uji_selalu_sesudah_potongan_setel():
    """Menguji pada data yang dipakai menyetel akan membuat hasilnya bohong."""
    for window in walk_forward_windows(1500, train_bars=400, test_bars=100):
        assert window.test_start >= window.train_end
        assert window.train_start < window.train_end


def test_data_terlalu_pendek_ditolak():
    try:
        walk_forward_windows(300, train_bars=500, test_bars=125)
    except ValueError:
        return
    raise AssertionError("data yang terlalu pendek seharusnya ditolak")


def test_jendela_terlalu_kecil_ditolak():
    for kwargs in ({"train_bars": 10, "test_bars": 100}, {"train_bars": 500, "test_bars": 5}):
        try:
            walk_forward_windows(2000, **kwargs)
        except ValueError:
            continue
        raise AssertionError(f"{kwargs} seharusnya ditolak")


def test_kombinasi_setelan_tidak_masuk_akal_dibuang():
    """Rata-rata cepat tidak boleh lebih panjang dari rata-rata lambat."""
    prices = synthetic_gbm(400, seed=31)
    tabel = parameter_sweep(
        prices, _pabrik_ma, {"fast": [10, 60], "slow": [50]}, BacktestConfig()
    )
    assert (tabel["fast"] < tabel["slow"]).all()
    assert len(tabel) == 1


def test_sapuan_setelan_menemukan_pemenang_di_data_acak():
    """Pada data acak, mencoba banyak setelan tetap memunculkan yang 'bagus'.

    Inilah inti masalah overfitting. Tes ini memastikan peraganya memang
    memperlihatkan hal itu, bukan kebetulan sekali jalan.
    """
    prices = synthetic_gbm(1200, seed=77)
    tabel = parameter_sweep(
        prices,
        _pabrik_ma,
        {"fast": [5, 10, 20, 30], "slow": [50, 100, 150, 200]},
        BacktestConfig(broker=BrokerConfig(leverage=100)),
    )
    assert len(tabel) >= 10
    # Hasil terbaik harus jauh lebih tinggi dari rata-rata, murni dari seleksi.
    assert tabel["total_return"].iloc[0] > tabel["total_return"].mean()
    assert tabel["total_return"].is_monotonic_decreasing


def test_mutu_menurun_di_luar_sampel_pada_data_acak():
    """Pada data acak, hasil saat disetel harus lebih baik dari saat diuji.

    Selisih itu bukan kelemahan alat, melainkan besarnya overfitting yang
    berhasil diukur. Kalau selisihnya nol pada data acak, berarti ada yang
    salah pada pemisahan datanya.
    """
    prices = synthetic_gbm(2000, seed=99)
    laporan = walk_forward_test(
        prices,
        _pabrik_ma,
        {"fast": [5, 10, 20, 30], "slow": [50, 100, 150, 200]},
        BacktestConfig(broker=BrokerConfig(leverage=100)),
        train_bars=500,
        test_bars=125,
        strategy_name="ma",
    )
    assert laporan.windows >= 5
    assert laporan.in_sample_mean > laporan.out_of_sample_mean
    assert laporan.degradation > 0


def test_tidak_ada_strategi_lolos_di_data_acak():
    """Alat ini tidak boleh menyatakan strategi lolos pada data tanpa pola."""
    prices = synthetic_gbm(1800, seed=123)
    laporan = walk_forward_test(
        prices,
        _pabrik_ma,
        {"fast": [5, 15, 30], "slow": [60, 120, 200]},
        BacktestConfig(broker=BrokerConfig(leverage=100)),
        train_bars=500,
        test_bars=125,
    )
    assert not laporan.survives, (
        f"alat menyatakan lolos di data acak: {laporan.out_of_sample_compound:+.2%}, "
        f"menang {laporan.out_of_sample_win_rate:.0%}"
    )


def test_rincian_jendela_lengkap():
    prices = synthetic_gbm(1400, seed=55)
    laporan = walk_forward_test(
        prices, _pabrik_ma, {"fast": [10], "slow": [50]},
        BacktestConfig(), train_bars=500, test_bars=125,
    )
    assert len(laporan.detail) == laporan.windows
    assert len(laporan.best_params_per_window) == laporan.windows
    assert laporan.combinations_tried == 1
    # Dengan satu kombinasi, tidak ada yang bisa dipilih, jadi tidak ada seleksi.
    assert set(laporan.detail["best_fast"]) == {10}


def test_expand_grid_kosong():
    assert expand_grid({}) == [{}]
    assert len(expand_grid({"a": [1, 2], "b": [3, 4, 5]})) == 6


# --- saham Indonesia ------------------------------------------------------

def test_fraksi_harga_mengikuti_rentang():
    """Fraksi harga di bursa Indonesia berbeda menurut harga sahamnya."""
    assert idx_tick_size(150) == 1.0
    assert idx_tick_size(199) == 1.0
    assert idx_tick_size(200) == 2.0
    assert idx_tick_size(499) == 2.0
    assert idx_tick_size(500) == 5.0
    assert idx_tick_size(1_999) == 5.0
    assert idx_tick_size(2_000) == 10.0
    assert idx_tick_size(4_999) == 10.0
    assert idx_tick_size(5_000) == 25.0
    assert idx_tick_size(50_000) == 25.0


def test_biaya_jual_lebih_besar_dari_biaya_beli():
    """Pajak penghasilan final hanya dikenakan saat menjual, bukan saat beli."""
    nilai = 10_000_000.0
    beli = IDX_BROKER.commission(nilai, 2_000, is_buy=True)
    jual = IDX_BROKER.commission(nilai, 2_000, is_buy=False)
    assert jual > beli
    assert np.isclose(beli, nilai * 0.0015)
    assert np.isclose(jual, nilai * 0.0025)


def test_satu_putaran_beli_jual_menelan_sekitar_empat_persepuluh_persen():
    """Komisi satu putaran harus mendekati 0,4 persen, di luar selisih harga."""
    nilai = 10_000_000.0
    total = (
        IDX_BROKER.commission(nilai, 2_000, is_buy=True)
        + IDX_BROKER.commission(nilai, 2_000, is_buy=False)
    )
    assert 0.0035 < total / nilai < 0.0045


def test_selisih_beli_jual_saham_ikut_harga():
    """Saham Rp 5.000 punya fraksi harga lebih besar dari saham Rp 500."""
    assert IDX_BROKER.half_spread(5_000) > IDX_BROKER.half_spread(500)
    assert np.isclose(IDX_BROKER.half_spread(5_000), 12.5)
    assert np.isclose(IDX_BROKER.half_spread(1_000), 2.5)


def test_ukuran_posisi_saham_selalu_lot_utuh():
    """Bursa Indonesia tidak menerima pecahan lot. Satu lot adalah 100 lembar."""
    broker = SimulatedBroker(10_000_000, IDX_BROKER)
    limits = RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0)
    for harga, jarak_stop in ((5_000.0, 250.0), (1_250.0, 60.0), (315.0, 15.0)):
        units = position_size(broker, harga, jarak_stop, limits)
        assert units % 100 == 0, f"harga {harga} memberi {units} lembar, bukan lot utuh"


def test_saham_tidak_bisa_melebihi_modal():
    """Tanpa leverage, nilai posisi tidak boleh lebih besar dari modal."""
    broker = SimulatedBroker(10_000_000, IDX_BROKER)
    position = broker.open_position(1, 1_000_000, 5_000.0, 0)
    assert position.units * position.entry_price <= 10_000_000 * 1.001


def test_saham_tanpa_leverage_tidak_terkena_stop_out():
    """Pada leverage 1, broker tidak punya alasan menutup paksa.

    Modal pemodal menanggung seluruh nilai posisi, jadi tidak ada uang broker
    yang perlu dilindungi. Harga boleh turun jauh tanpa penutupan paksa.
    """
    broker = SimulatedBroker(10_000_000, IDX_BROKER)
    broker.open_position(1, broker.max_units(5_000.0), 5_000.0, 0)
    broker.enforce_margin(3_500.0, 1)  # turun 30 persen
    assert not broker.stopped_out
    assert broker.position is not None


def test_tanpa_biaya_menginap_di_saham():
    broker = SimulatedBroker(10_000_000, IDX_BROKER)
    broker.open_position(1, 1_000, 5_000.0, 0)
    saldo_sebelum = broker.balance
    broker.accrue_swap(30.0)
    assert broker.balance == saldo_sebelum


def test_long_only_memblokir_jual_kosong():
    """Dengan long_only, sinyal jual harus berarti keluar ke tunai."""
    prices = synthetic_gbm(600, start_price=5_000.0, daily_volatility=0.018, seed=41)
    config = BacktestConfig(
        starting_balance=10_000_000,
        broker=IDX_BROKER,
        limits=RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0),
        long_only=True,
    )
    signals = pd.Series(-1, index=prices.index, dtype=int)
    result, _ = run_backtest(prices, signals, config, "semua_jual")
    assert result.trades == 0, "sinyal jual terus seharusnya tidak membuka posisi apa pun"

    campur = REGISTRY["ma_crossover"](prices)
    hasil, _ = run_backtest(prices, campur, config, "ma_long_only")
    broker_trades = hasil.trades
    assert broker_trades >= 0


def test_pasar_tidak_dikenal_ditolak():
    try:
        BrokerConfig(market="nyse")
    except ValueError:
        return
    raise AssertionError("market yang tidak dikenal seharusnya ditolak")


def test_tarif_komisi_tidak_masuk_akal_ditolak():
    for kwargs in (
        {"commission_rate_buy": 0.5},
        {"commission_rate_sell": -0.01},
        {"units_per_lot": 0},
    ):
        try:
            BrokerConfig(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"{kwargs} seharusnya ditolak")


def test_biaya_saham_tercatat_di_hasil():
    """Biaya harus muncul di laporan, bukan hilang diam-diam."""
    prices = synthetic_gbm(800, start_price=2_500.0, daily_volatility=0.02, seed=62)
    config = BacktestConfig(
        starting_balance=10_000_000,
        broker=IDX_BROKER,
        limits=RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0),
        long_only=True,
    )
    result, _ = run_backtest(prices, REGISTRY["ma_crossover"](prices), config, "ma")
    if result.trades > 0:
        assert result.total_costs > 0, "transaksi terjadi tapi biayanya nol"


# --- keadilan pembanding --------------------------------------------------

def test_pembanding_tidak_dilumpuhkan_batas_penurunan():
    """Beli lalu tahan di pasar naik harus menangkap sebagian besar kenaikan.

    Ini tes pelindung untuk cacat nyata yang pernah terjadi. Batas penurunan
    20 persen di manajemen risiko ikut menghentikan pembanding beli lalu
    tahan, sehingga pada saham yang naik 84 persen pembandingnya hanya
    mencatat +2,1 persen. Akibatnya setiap strategi aktif terlihat jauh lebih
    baik daripada kenyataannya.
    """
    prices = synthetic_gbm(
        2_500, start_price=3_500.0, daily_volatility=0.018, drift=0.0004, seed=18
    )
    naik_pasar = float(prices["close"].iloc[-1] / prices["close"].iloc[0] - 1)
    assert naik_pasar > 0.5, "data uji ini seharusnya pasar naik"

    base = BacktestConfig(
        starting_balance=10_000_000,
        broker=IDX_BROKER,
        limits=RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0),
        long_only=True,
    )
    hasil, _ = run_backtest(
        prices, REGISTRY["always_long"](prices), benchmark_config(base), "beli_tahan"
    )
    # Pembanding harus menangkap minimal tiga perempat kenaikan pasarnya.
    assert hasil.total_return > naik_pasar * 0.75, (
        f"pembanding hanya {hasil.total_return:+.1%} padahal pasar naik "
        f"{naik_pasar:+.1%}; batas risiko kemungkinan melumpuhkannya lagi"
    )


def test_benchmark_config_mematikan_stop_dan_batas():
    base = BacktestConfig(
        limits=RiskLimits(max_total_drawdown=0.20, max_daily_loss=0.03),
        use_stops=True,
    )
    pembanding = benchmark_config(base)
    assert pembanding.use_stops is False
    assert pembanding.limits.max_total_drawdown > 0.9
    assert pembanding.limits.max_daily_loss > 0.9
    # Konfigurasi asalnya tidak boleh ikut berubah.
    assert base.use_stops is True
    assert base.limits.max_total_drawdown == 0.20


def test_biaya_posisi_terbuka_ikut_dilaporkan():
    """Strategi yang berakhir dengan posisi terbuka tetap sudah bayar biaya masuk."""
    prices = synthetic_gbm(500, start_price=3_500.0, daily_volatility=0.01, seed=73)
    base = BacktestConfig(
        starting_balance=10_000_000,
        broker=IDX_BROKER,
        limits=RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0),
        long_only=True,
    )
    hasil, _ = run_backtest(
        prices, REGISTRY["always_long"](prices), benchmark_config(base), "beli_tahan"
    )
    assert hasil.trades == 0, "beli lalu tahan seharusnya tidak menutup posisi"
    assert hasil.total_costs > 0, "biaya beli awal seharusnya tetap tercatat"


def test_stop_loss_menambah_jumlah_transaksi_dan_biaya():
    """Stop loss itu perlindungan, dan perlindungan itu berbiaya."""
    prices = synthetic_gbm(
        1_500, start_price=3_500.0, daily_volatility=0.018, drift=0.0004, seed=18
    )
    base = BacktestConfig(
        starting_balance=10_000_000,
        broker=IDX_BROKER,
        limits=RiskLimits(risk_per_trade=0.02, max_effective_leverage=1.0),
        long_only=True,
        use_stops=True,
    )
    signals = REGISTRY["always_long"](prices)
    dengan, _ = run_backtest(prices, signals, base, "dengan_stop")
    tanpa, _ = run_backtest(prices, signals, benchmark_config(base), "tanpa_stop")
    assert dengan.trades > tanpa.trades
    assert dengan.total_costs > tanpa.total_costs


# --- membaca berkas dari berbagai penyedia data ---------------------------

def _tulis(nama: str, isi: str) -> str:
    import tempfile

    folder = Path(tempfile.mkdtemp())
    berkas = folder / nama
    berkas.write_text(isi)
    return str(berkas)


def test_angka_pemisah_ribuan_koma():
    assert bersihkan_angka("7,350") == 7350.0
    assert bersihkan_angka("1,234.56") == 1234.56
    assert bersihkan_angka("26,000") == 26_000.0


def test_angka_akhiran_ribuan():
    assert bersihkan_angka("12.5M") == 12_500_000.0
    assert bersihkan_angka("45K") == 45_000.0


def test_angka_tidak_terbaca_menjadi_nan():
    for nilai in ("-", "", "n/a", "abc", None):
        assert np.isnan(bersihkan_angka(nilai))


def test_petunjuk_pasar_tidak_merusak_angka_desimal():
    """Petunjuk pasar hanya menengahi susunan yang memang bisa dibaca dua cara.

    Ini tes pelindung untuk bug nyata. Memaksa titik sebagai pemisah ribuan
    untuk pasar saham sempat mengubah "5306.2" menjadi 53062, sepuluh kali
    lipat dari seharusnya, sehingga seluruh ukuran posisi jadi nol dan tidak
    ada satu pun transaksi terjadi.
    """
    assert bersihkan_angka("5306.2", titik_ribuan=True) == 5306.2
    assert bersihkan_angka("0.25", titik_ribuan=True) == 0.25
    assert bersihkan_angka("7.400", titik_ribuan=True) == 7_400.0
    assert bersihkan_angka("1.234.567", titik_ribuan=True) == 1_234_567.0


def test_petunjuk_forex_menjaga_titik_sebagai_desimal():
    assert bersihkan_angka("1.105", titik_ribuan=False) == 1.105
    assert bersihkan_angka("1.10523", titik_ribuan=False) == 1.10523


def test_kolom_memutuskan_konvensi_sekali_untuk_semua():
    """Satu nilai tidak cukup; seluruh kolom hampir selalu cukup."""
    gaya_forex = bersihkan_kolom(pd.Series(["1.1050", "1.1123", "1.0987"]))
    assert gaya_forex.max() < 2.0
    gaya_saham = bersihkan_kolom(pd.Series(["7.350", "26.000", "1.234.567"]))
    assert gaya_saham.min() >= 7_000.0


def test_baca_berkas_gaya_indonesia():
    path = _tulis(
        "idx.csv",
        "Tanggal,Penutupan,Tertinggi,Terendah,Volume\n"
        "01/09/2026,7.350,7.400,7.300,45200000\n"
        "02/09/2026,7.400,7.450,7.325,38100000\n",
    )
    frame = load_csv(path, market="idx")
    assert list(frame.columns) == ["high", "low", "close", "volume"]
    assert float(frame["close"].iloc[0]) == 7_350.0
    assert frame.index[0] < frame.index[1]


def test_baca_berkas_gaya_investing():
    path = _tulis(
        "investing.csv",
        'Tanggal,Terakhir,Pembukaan,Tertinggi,Terendah,Vol.,Perubahan%\n'
        '10/10/2026,"9,875","9,800","9,900","9,775","45.2M","0.76%"\n'
        '09/10/2026,"9,800","9,850","9,875","9,775","38.1M","-0.51%"\n',
    )
    frame = load_csv(path, market="idx")
    assert float(frame["close"].iloc[-1]) == 9_875.0
    assert float(frame["volume"].iloc[-1]) == 45_200_000.0


def test_tanggal_iso_tidak_dibalik():
    """Tanggal 2026-09-01 adalah 1 September, bukan 9 Januari.

    Tes pelindung untuk bug nyata: dayfirst=True membalik bulan dan hari pada
    berkas gaya Yahoo Finance, sehingga urutan waktunya jadi kacau.
    """
    path = _tulis(
        "yahoo.csv",
        "Date,Open,High,Low,Close,Adj Close,Volume\n"
        "2026-09-01,7350,7400,7300,7375,7375,45200000\n"
        "2026-09-02,7375,7450,7325,7400,7400,38100000\n",
    )
    frame = load_csv(path, market="idx")
    assert frame.index[0].month == 9
    assert frame.index[0].day == 1


def test_berkas_tanpa_kolom_harga_ditolak():
    path = _tulis("tanpa_harga.csv", "Tanggal,Volume\n01/09/2026,100\n")
    try:
        load_csv(path, market="idx")
    except ValueError:
        return
    raise AssertionError("berkas tanpa kolom harga penutupan seharusnya ditolak")


def test_pasar_tidak_dikenal_di_load_csv_ditolak():
    path = _tulis("x.csv", "Tanggal,Penutupan\n01/09/2026,7.350\n")
    try:
        load_csv(path, market="nasdaq")
    except ValueError:
        return
    raise AssertionError("market yang tidak dikenal seharusnya ditolak")


# --- pemeriksaan mutu data ------------------------------------------------

def _seri_dengan_pemecahan(rasio: float, pada: int = 700, baris: int = 1_200):
    index = pd.date_range("2019-01-02", periods=baris, freq="B")
    harga = np.linspace(26_000.0, 36_000.0, baris)
    harga[pada:] /= rasio
    return pd.DataFrame({"close": harga}, index=index)


def test_pemecahan_saham_terdeteksi():
    """Pemecahan yang belum disesuaikan harus ditemukan, apa pun rasionya."""
    for rasio in (2.0, 5.0, 10.0):
        frame = _seri_dengan_pemecahan(rasio)
        dugaan = deteksi_pemecahan(frame)
        assert len(dugaan) == 1, f"rasio {rasio} tidak terdeteksi"
        assert np.isclose(dugaan[0].rasio_terdekat, rasio)


def test_data_bersih_tidak_dituduh_pemecahan():
    """Pergerakan pasar biasa tidak boleh dikira pemecahan saham."""
    frame = synthetic_gbm(1_500, start_price=7_000.0, daily_volatility=0.02, seed=88)
    assert deteksi_pemecahan(frame) == []


def test_penyesuaian_pemecahan_menyatukan_skala_harga():
    frame = _seri_dengan_pemecahan(5.0)
    laporan = periksa(frame)
    assert not laporan.layak_pakai
    rapi = sesuaikan_pemecahan(frame, laporan.dugaan_pemecahan)
    assert deteksi_pemecahan(rapi) == []
    # Harga lama kini sebanding dengan harga terbaru, bukan lima kali lipat.
    assert float(rapi["close"].iloc[0]) < float(rapi["close"].iloc[-1]) * 1.5


def test_harga_nol_ditandai_tidak_sah():
    index = pd.date_range("2020-01-01", periods=100, freq="B")
    harga = np.full(100, 5_000.0)
    harga[50] = 0.0
    laporan = periksa(pd.DataFrame({"close": harga}, index=index))
    assert laporan.harga_tidak_sah == 1
    assert not laporan.layak_pakai


def test_data_terlalu_pendek_ditandai():
    frame = synthetic_gbm(100, start_price=5_000.0, seed=4)
    laporan = periksa(frame)
    assert laporan.tahun_data < 2.0
    assert not laporan.layak_pakai


def test_data_bagus_dinyatakan_layak():
    frame = synthetic_gbm(
        1_000, start_price=7_000.0, daily_volatility=0.015, seed=7, freq="B"
    )
    laporan = periksa(frame)
    assert laporan.layak_pakai, laporan.laporan_teks()


def test_penyesuaian_tanpa_dugaan_tidak_mengubah_apa_pun():
    frame = synthetic_gbm(500, start_price=5_000.0, seed=11)
    assert sesuaikan_pemecahan(frame, []).equals(frame)


# --- pengunduh data -------------------------------------------------------

def test_kode_saham_indonesia_diberi_akhiran_bursa():
    """Kode Indonesia butuh akhiran .JK, kode asing tidak boleh diubah."""
    import importlib.util

    jalur = Path(__file__).resolve().parents[1] / "scripts" / "unduh_data.py"
    spec = importlib.util.spec_from_file_location("unduh_data", jalur)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)

    assert modul.kode_lengkap("BBCA") == "BBCA.JK"
    assert modul.kode_lengkap("bbri") == "BBRI.JK"
    assert modul.kode_lengkap(" tlkm ") == "TLKM.JK"
    assert modul.kode_lengkap("BBCA.JK") == "BBCA.JK"
    assert modul.kode_lengkap("EURUSD=X") == "EURUSD=X"
    assert modul.kode_lengkap("^JKSE") == "^JKSE.JK"


def _jalankan_semua() -> int:
    gagal = 0
    tes = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    for nama, fungsi in tes:
        try:
            fungsi()
            print(f"  lulus  {nama}")
        except Exception as error:  # noqa: BLE001
            gagal += 1
            print(f"  GAGAL  {nama}: {error}")
    print(f"\n{len(tes) - gagal} lulus, {gagal} gagal, dari {len(tes)} tes")
    return 1 if gagal else 0


if __name__ == "__main__":
    raise SystemExit(_jalankan_semua())
