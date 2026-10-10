"""Simulasi broker forex dengan mekanika margin yang sebenarnya.

Modul ini meniru hal-hal yang membuat akun forex nyata habis, dan yang
hampir selalu hilang dari backtest buatan sendiri:

  * spread, yaitu selisih harga beli dan harga jual, dibayar setiap transaksi
  * margin, yaitu jaminan yang ditahan broker untuk tiap posisi
  * margin call dan stop out, yaitu penutupan paksa oleh broker
  * biaya menginap (swap) untuk posisi yang dibawa lewat malam
  * saldo negatif ketika harga melompat melewati titik stop out

Asumsi yang disederhanakan, dan konsekuensinya:
  * Mata uang akun sama dengan mata uang kedua pasangan (contoh: akun USD
    untuk EURUSD). Untuk pasangan lain, laba-rugi perlu dikonversi dan
    angkanya akan bergeser.
  * Eksekusi terjadi pada harga penutupan batang berikutnya, tanpa slippage
    di luar spread. Pada pasar nyata slippage memperburuk hasil, jadi angka
    di sini adalah batas optimis.
"""

from __future__ import annotations

from dataclasses import dataclass, field

UNITS_PER_LOT = 100_000


@dataclass(frozen=True)
class BrokerConfig:
    """Ketentuan broker. Nilai bawaan meniru broker retail leverage tinggi."""

    leverage: int = 100
    spread_pips: float = 1.5
    pip_size: float = 0.0001
    commission_per_lot: float = 0.0
    swap_per_lot_per_day: float = -2.0
    margin_call_level: float = 1.0
    stop_out_level: float = 0.5
    negative_balance_protection: bool = True

    def __post_init__(self) -> None:
        if self.leverage < 1:
            raise ValueError("leverage minimal 1")
        if self.spread_pips < 0 or self.pip_size <= 0:
            raise ValueError("spread_pips tidak boleh negatif dan pip_size harus positif")
        if not 0 <= self.stop_out_level <= self.margin_call_level:
            raise ValueError("stop_out_level harus di antara 0 dan margin_call_level")

    @property
    def half_spread(self) -> float:
        """Jarak harga dari harga tengah ke harga beli atau harga jual."""
        return self.spread_pips * self.pip_size / 2.0


@dataclass
class Position:
    direction: int
    units: float
    entry_price: float
    entry_index: int
    margin: float
    stop_loss: float | None = None
    take_profit: float | None = None

    @property
    def lots(self) -> float:
        return self.units / UNITS_PER_LOT


@dataclass
class Trade:
    direction: int
    units: float
    entry_price: float
    exit_price: float
    entry_index: int
    exit_index: int
    profit: float
    costs: float
    reason: str

    @property
    def lots(self) -> float:
        return self.units / UNITS_PER_LOT


class StopOut(Exception):
    """Broker menutup posisi secara paksa karena jaminan tidak cukup."""


class SimulatedBroker:
    """Akun forex satu posisi sekaligus, dengan penegakan margin."""

    def __init__(self, starting_balance: float, config: BrokerConfig | None = None) -> None:
        if starting_balance <= 0:
            raise ValueError("starting_balance harus positif")
        self.config = config or BrokerConfig()
        self.starting_balance = float(starting_balance)
        self.balance = float(starting_balance)
        self.position: Position | None = None
        self.trades: list[Trade] = []
        self.margin_calls = 0
        self.stopped_out = False
        self._accrued_costs = 0.0

    # --- harga ---------------------------------------------------------

    def ask(self, mid_price: float) -> float:
        """Harga beli, selalu di atas harga tengah."""
        return mid_price + self.config.half_spread

    def bid(self, mid_price: float) -> float:
        """Harga jual, selalu di bawah harga tengah."""
        return mid_price - self.config.half_spread

    # --- keadaan akun --------------------------------------------------

    def floating_profit(self, mid_price: float) -> float:
        """Laba-rugi posisi terbuka bila ditutup pada harga saat ini."""
        if self.position is None:
            return 0.0
        exit_price = self.bid(mid_price) if self.position.direction > 0 else self.ask(mid_price)
        return self.position.direction * self.position.units * (
            exit_price - self.position.entry_price
        )

    def equity(self, mid_price: float) -> float:
        """Saldo ditambah laba-rugi posisi terbuka. Ini angka yang sebenarnya."""
        return self.balance + self.floating_profit(mid_price)

    @property
    def used_margin(self) -> float:
        return 0.0 if self.position is None else self.position.margin

    def margin_level(self, mid_price: float) -> float:
        """Rasio ekuitas terhadap jaminan terpakai.

        Tak terhingga bila tidak ada posisi terbuka. Broker memberi margin
        call di bawah 1.0 dan stop out di bawah 0.5 pada pengaturan bawaan.
        """
        if self.used_margin <= 0:
            return float("inf")
        return self.equity(mid_price) / self.used_margin

    def free_margin(self, mid_price: float) -> float:
        return self.equity(mid_price) - self.used_margin

    def max_units(self, mid_price: float) -> float:
        """Ukuran posisi terbesar yang masih sanggup dijaminkan."""
        price = self.ask(mid_price)
        if price <= 0:
            return 0.0
        return max(0.0, self.free_margin(mid_price) * self.config.leverage / price)

    # --- transaksi -----------------------------------------------------

    def open_position(
        self,
        direction: int,
        units: float,
        mid_price: float,
        bar_index: int,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> Position:
        if direction not in (1, -1):
            raise ValueError("direction harus 1 (beli) atau -1 (jual)")
        if self.position is not None:
            raise RuntimeError("Sudah ada posisi terbuka")
        if units <= 0:
            raise ValueError("units harus positif")

        allowed = self.max_units(mid_price)
        if units > allowed:
            units = allowed
        if units <= 0:
            raise StopOut("Jaminan tidak cukup untuk membuka posisi")

        entry_price = self.ask(mid_price) if direction > 0 else self.bid(mid_price)
        margin = units * entry_price / self.config.leverage

        commission = self.config.commission_per_lot * units / UNITS_PER_LOT
        self.balance -= commission
        self._accrued_costs = commission

        self.position = Position(
            direction=direction,
            units=units,
            entry_price=entry_price,
            entry_index=bar_index,
            margin=margin,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        return self.position

    def close_position(self, mid_price: float, bar_index: int, reason: str = "signal") -> Trade:
        if self.position is None:
            raise RuntimeError("Tidak ada posisi untuk ditutup")

        position = self.position
        exit_price = self.bid(mid_price) if position.direction > 0 else self.ask(mid_price)
        gross = position.direction * position.units * (exit_price - position.entry_price)
        commission = self.config.commission_per_lot * position.units / UNITS_PER_LOT

        self.balance += gross - commission
        costs = self._accrued_costs + commission

        trade = Trade(
            direction=position.direction,
            units=position.units,
            entry_price=position.entry_price,
            exit_price=exit_price,
            entry_index=position.entry_index,
            exit_index=bar_index,
            profit=gross - commission,
            costs=costs,
            reason=reason,
        )
        self.trades.append(trade)
        self.position = None
        self._accrued_costs = 0.0
        return trade

    # --- pemeliharaan per batang --------------------------------------

    def accrue_swap(self, days: float = 1.0) -> None:
        """Bebankan biaya menginap untuk posisi yang dibawa lewat malam."""
        if self.position is None or days <= 0:
            return
        cost = self.config.swap_per_lot_per_day * self.position.lots * days
        self.balance += cost
        self._accrued_costs -= cost

    def check_exits(self, high: float, low: float, bar_index: int) -> Trade | None:
        """Periksa stop loss dan take profit terhadap rentang harga batang.

        Bila keduanya tersentuh di batang yang sama, stop loss dimenangkan.
        Urutan sebenarnya tidak terlihat dari data harian, dan memilih yang
        merugikan menjaga backtest tetap jujur.
        """
        position = self.position
        if position is None:
            return None

        if position.direction > 0:
            if position.stop_loss is not None and self.bid(low) <= position.stop_loss:
                return self.close_position(position.stop_loss + self.config.half_spread,
                                           bar_index, "stop_loss")
            if position.take_profit is not None and self.bid(high) >= position.take_profit:
                return self.close_position(position.take_profit + self.config.half_spread,
                                           bar_index, "take_profit")
        else:
            if position.stop_loss is not None and self.ask(high) >= position.stop_loss:
                return self.close_position(position.stop_loss - self.config.half_spread,
                                           bar_index, "stop_loss")
            if position.take_profit is not None and self.ask(low) <= position.take_profit:
                return self.close_position(position.take_profit - self.config.half_spread,
                                           bar_index, "take_profit")
        return None

    def enforce_margin(self, mid_price: float, bar_index: int) -> Trade | None:
        """Jalankan margin call dan stop out seperti broker sungguhan.

        Inilah mekanisme yang menghabiskan akun berleverage tinggi. Tidak ada
        yang bertanya lebih dulu; posisi ditutup paksa.
        """
        if self.position is None:
            return None

        level = self.margin_level(mid_price)
        if level < self.config.margin_call_level:
            self.margin_calls += 1
        if level >= self.config.stop_out_level:
            return None

        trade = self.close_position(mid_price, bar_index, "stop_out")
        self.stopped_out = True
        if self.balance < 0 and self.config.negative_balance_protection:
            self.balance = 0.0
        return trade

    @property
    def is_blown(self) -> bool:
        """Akun tidak lagi bisa membuka posisi berarti."""
        return self.balance <= self.starting_balance * 0.02
