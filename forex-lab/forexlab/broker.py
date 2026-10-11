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

#: Fraksi harga di Bursa Efek Indonesia, berbeda menurut rentang harga saham.
#: Satu fraksi adalah langkah harga terkecil yang bisa terjadi, dan setengah
#: fraksi itulah selisih beli-jual terbaik yang mungkin didapat.
IDX_TICK_BANDS: tuple[tuple[float, float], ...] = (
    (200.0, 1.0),
    (500.0, 2.0),
    (2_000.0, 5.0),
    (5_000.0, 10.0),
    (float("inf"), 25.0),
)


def idx_tick_size(price: float) -> float:
    """Fraksi harga yang berlaku untuk saham pada harga tertentu."""
    for batas, fraksi in IDX_TICK_BANDS:
        if price < batas:
            return fraksi
    return IDX_TICK_BANDS[-1][1]


@dataclass(frozen=True)
class BrokerConfig:
    """Ketentuan broker.

    Satu kelas ini melayani dua pasar yang mekanika biayanya sangat berbeda:

    forex: biaya utamanya spread dalam pip, ada leverage, ada biaya menginap,
    dan posisi bisa ditutup paksa lewat stop out.

    idx: saham Indonesia. Tidak ada leverage bagi pemodal biasa, tidak ada
    biaya menginap, dan biayanya berupa persentase dari nilai transaksi yang
    berbeda antara beli dan jual. Selisih beli-jual mengikuti fraksi harga
    yang berubah menurut rentang harga saham.

    Nilai bawaan meniru broker forex retail berleverage tinggi. Untuk saham
    Indonesia, pakai IDX_BROKER di bawah.
    """

    market: str = "forex"
    leverage: int = 100
    units_per_lot: int = UNITS_PER_LOT
    spread_pips: float = 1.5
    pip_size: float = 0.0001
    spread_ticks: float = 1.0
    commission_per_lot: float = 0.0
    commission_rate_buy: float = 0.0
    commission_rate_sell: float = 0.0
    swap_per_lot_per_day: float = -2.0
    margin_call_level: float = 1.0
    stop_out_level: float = 0.5
    negative_balance_protection: bool = True

    def __post_init__(self) -> None:
        if self.market not in ("forex", "idx"):
            raise ValueError("market harus 'forex' atau 'idx'")
        if self.leverage < 1:
            raise ValueError("leverage minimal 1")
        if self.units_per_lot < 1:
            raise ValueError("units_per_lot minimal 1")
        if self.spread_pips < 0 or self.pip_size <= 0:
            raise ValueError("spread_pips tidak boleh negatif dan pip_size harus positif")
        if self.spread_ticks < 0:
            raise ValueError("spread_ticks tidak boleh negatif")
        for nama, nilai in (
            ("commission_rate_buy", self.commission_rate_buy),
            ("commission_rate_sell", self.commission_rate_sell),
        ):
            if not 0 <= nilai < 0.05:
                raise ValueError(f"{nama} harus di antara 0 dan 0.05")
        if not 0 <= self.stop_out_level <= self.margin_call_level:
            raise ValueError("stop_out_level harus di antara 0 dan margin_call_level")

    def half_spread(self, price: float) -> float:
        """Jarak harga dari harga tengah ke harga beli atau harga jual.

        Pada forex jaraknya tetap, karena spread dihitung dalam pip. Pada
        saham Indonesia jaraknya ikut harga, karena fraksi harga saham Rp 500
        berbeda dari saham Rp 5.000.
        """
        if self.market == "idx":
            return self.spread_ticks * idx_tick_size(price) / 2.0
        return self.spread_pips * self.pip_size / 2.0

    def commission(self, notional: float, units: float, is_buy: bool) -> float:
        """Biaya satu kali transaksi, selalu positif.

        Pada saham Indonesia, biaya jual lebih besar dari biaya beli karena
        memuat pajak penghasilan final atas penjualan saham. Itu sebabnya
        tarifnya dipisah, bukan disamakan.
        """
        rate = self.commission_rate_buy if is_buy else self.commission_rate_sell
        per_lot = self.commission_per_lot * units / self.units_per_lot
        return abs(notional) * rate + per_lot


#: Broker saham Indonesia dengan biaya yang lazim berlaku.
#:
#: Tarif 0,15 persen saat beli dan 0,25 persen saat jual adalah angka umum
#: yang sudah memuat komisi broker, biaya transaksi bursa, biaya kliring,
#: pajak pertambahan nilai atas komisi, dan pajak penghasilan final 0,1
#: persen yang hanya dikenakan saat menjual. Jadi satu putaran beli lalu jual
#: menelan sekitar 0,4 persen.
#:
#: Tarif ini berbeda antar sekuritas, kadang cukup jauh. Periksa tarif
#: sekuritas Anda sendiri dan ganti angkanya, karena pada strategi yang
#: sering bertransaksi, selisih kecil di sini menentukan untung atau rugi.
IDX_BROKER = BrokerConfig(
    market="idx",
    leverage=1,
    units_per_lot=100,
    spread_ticks=1.0,
    commission_rate_buy=0.0015,
    commission_rate_sell=0.0025,
    commission_per_lot=0.0,
    swap_per_lot_per_day=0.0,
)


@dataclass
class Position:
    direction: int
    units: float
    entry_price: float
    entry_index: int
    margin: float
    stop_loss: float | None = None
    take_profit: float | None = None
    units_per_lot: float = UNITS_PER_LOT

    @property
    def lots(self) -> float:
        return self.units / self.units_per_lot


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
    units_per_lot: float = UNITS_PER_LOT

    @property
    def lots(self) -> float:
        return self.units / self.units_per_lot


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
        return mid_price + self.config.half_spread(mid_price)

    def bid(self, mid_price: float) -> float:
        """Harga jual, selalu di bawah harga tengah."""
        return mid_price - self.config.half_spread(mid_price)

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

        # Membuka posisi beli berarti transaksi beli; membuka posisi jual
        # berarti transaksi jual. Tarifnya berbeda pada saham Indonesia.
        commission = self.config.commission(
            units * entry_price, units, is_buy=direction > 0
        )
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
            units_per_lot=self.config.units_per_lot,
        )
        return self.position

    def close_position(self, mid_price: float, bar_index: int, reason: str = "signal") -> Trade:
        if self.position is None:
            raise RuntimeError("Tidak ada posisi untuk ditutup")

        position = self.position
        exit_price = self.bid(mid_price) if position.direction > 0 else self.ask(mid_price)
        gross = position.direction * position.units * (exit_price - position.entry_price)
        # Menutup posisi beli berarti transaksi jual, dan sebaliknya.
        commission = self.config.commission(
            position.units * exit_price, position.units, is_buy=position.direction < 0
        )

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
            units_per_lot=self.config.units_per_lot,
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
                return self.close_position(position.stop_loss + self.config.half_spread(position.stop_loss),
                                           bar_index, "stop_loss")
            if position.take_profit is not None and self.bid(high) >= position.take_profit:
                return self.close_position(position.take_profit + self.config.half_spread(position.take_profit),
                                           bar_index, "take_profit")
        else:
            if position.stop_loss is not None and self.ask(high) >= position.stop_loss:
                return self.close_position(position.stop_loss - self.config.half_spread(position.stop_loss),
                                           bar_index, "stop_loss")
            if position.take_profit is not None and self.ask(low) <= position.take_profit:
                return self.close_position(position.take_profit - self.config.half_spread(position.take_profit),
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
    def open_position_costs(self) -> float:
        """Biaya yang sudah dibayar untuk posisi yang masih terbuka.

        Tanpa ini, strategi yang mengakhiri periode dengan posisi terbuka,
        seperti beli lalu tahan, akan terlihat tidak berbiaya sama sekali.
        """
        return 0.0 if self.position is None else max(self._accrued_costs, 0.0)

    @property
    def is_blown(self) -> bool:
        """Akun tidak lagi bisa membuka posisi berarti."""
        return self.balance <= self.starting_balance * 0.02
