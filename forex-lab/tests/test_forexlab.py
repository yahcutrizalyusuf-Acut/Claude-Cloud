"""Tes untuk bagian yang kalau salah akan membuat seluruh hasil bohong.

Jalankan: python3 -m pytest tests/ -q   (atau python3 tests/test_forexlab.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forexlab.backtest import BacktestConfig, run_backtest
from forexlab.broker import UNITS_PER_LOT, BrokerConfig, SimulatedBroker
from forexlab.control import permutation_test
from forexlab.data import block_bootstrap_returns, log_returns, shuffle_returns, synthetic_gbm
from forexlab.metrics import max_drawdown, sharpe_ratio
from forexlab.risk import RiskLimits, position_size
from forexlab.strategies import REGISTRY, moving_average_crossover


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
