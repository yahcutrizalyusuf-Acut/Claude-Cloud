"""forex-lab: alat uji strategi forex yang jujur.

Tujuan paket ini bukan mencari strategi yang untung, melainkan menolak
strategi yang tidak untung sebelum uang sungguhan terlibat. Karena itu
bagian terpentingnya adalah control.permutation_test, bukan mesin
backtestnya.
"""

__version__ = "0.1.0"

from .backtest import BacktestConfig, run_backtest
from .broker import BrokerConfig, SimulatedBroker
from .control import ControlReport, permutation_test
from .data import load_csv, synthetic_gbm
from .metrics import Result
from .risk import RiskLimits
from .validation import (
    WalkForwardReport,
    parameter_sweep,
    walk_forward_test,
)

__all__ = [
    "BacktestConfig",
    "BrokerConfig",
    "ControlReport",
    "Result",
    "RiskLimits",
    "SimulatedBroker",
    "WalkForwardReport",
    "load_csv",
    "parameter_sweep",
    "permutation_test",
    "run_backtest",
    "synthetic_gbm",
    "walk_forward_test",
]
