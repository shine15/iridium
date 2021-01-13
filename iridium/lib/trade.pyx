import uuid
from numpy cimport (
float64_t,
int64_t,
uint32_t
)
from libc.stdlib cimport abs
from .forex cimport calculate_gains_losses, calculate_margin_used
from .instrument import Instrument
from cpython.datetime cimport datetime

cdef class Trade:
    def __init__(self,
                 instrument,
                 price,
                 open_time,
                 initial_units,
                 initial_margin,
                 take_profit_order,
                 stop_loss_order,
                 trailing_stop_loss_order,
                 spread,
                 commission):
        self.trade_id = str(uuid.uuid4())
        self.instrument = instrument
        self.price = price
        self.state = TradeState.OPEN
        self.open_time = open_time
        self.initial_units = initial_units
        self.initial_margin = initial_margin
        self.current_units = initial_units
        self.margin_used = initial_margin
        self.realized_profit_loss = 0.00
        self.unrealized_profit_loss = 0.00
        #TODO: The financing paid/collected for this Trade
        self.financing = 0.00
        self.close_time = None
        self.take_profit_order = take_profit_order
        self.stop_loss_order = stop_loss_order
        self.trailing_stop_loss_order = trailing_stop_loss_order
        self.spread = spread
        self.commission = commission

    cpdef set_take_profit_order(self, TakeProfitOrder order):
        self.take_profit_order = order

    cpdef set_stop_loss_order(self, StopLossOrder order):
        self.stop_loss_order = order

    cpdef set_trailing_stop_loss_order(self, TrailingStopLossOrder order):
        self.trailing_stop_loss_order = order

    cpdef float64_t calculate_unrealized_profit_loss(self,
                                                     float64_t current_account_vs_quote_rate,
                                                     float64_t current_price):
        cdef float64_t trading_cost = calculate_gains_losses(
            self.spread / 2,
            abs(self.current_units),
            current_account_vs_quote_rate,
            Instrument(self.instrument).pip_decimal_number) + self.commission
        cdef float64_t price_change_profit_loss = (current_price - self.price) * \
                                                  (1 / current_account_vs_quote_rate) * \
                                                  self.current_units
        cdef unrealized_profit_loss = price_change_profit_loss - trading_cost
        self.unrealized_profit_loss = unrealized_profit_loss
        return unrealized_profit_loss

    cpdef float64_t partially_close_trade(self,
                                          float64_t current_account_vs_quote_rate,
                                          float64_t current_price,
                                          int64_t units):
        cdef float64_t trading_cost = calculate_gains_losses(
            self.spread,
            abs(units),
            current_account_vs_quote_rate,
            Instrument(self.instrument).pip_decimal_number) + self.commission
        cdef float64_t price_change_profit_loss = (current_price - self.price) * \
                                                  (1 / current_account_vs_quote_rate) * \
                                                  units
        cdef float64_t profit_loss = price_change_profit_loss - trading_cost
        self.current_units += -units
        self.realized_profit_loss += profit_loss
        self.margin_used += -(units / self.initial_units) * self.initial_margin
        return profit_loss

    cpdef float64_t close_trade(self,
                                float64_t current_account_vs_quote_rate,
                                float64_t current_price,
                                datetime close_time
                                ):
        cdef float64_t profit_loss = self.partially_close_trade(current_account_vs_quote_rate,
                                                                current_price,
                                                                self.current_units)
        self.close_time = close_time
        self.take_profit_order = None
        self.stop_loss_order = None
        self.trailing_stop_loss_order = None
        self.state = TradeState.CLOSED
        return profit_loss

    cpdef float64_t calculate_margin_used(self,
                                          float64_t current_account_vs_base_rate,
                                          uint32_t leverage):
        return calculate_margin_used(abs(self.current_units),
                                     current_account_vs_base_rate,
                                     leverage)

    cpdef adjust_stop_loss(self, float64_t price):
        if self.stop_loss_order is not None:
            self.stop_loss_order.adjust_price(price)

    cpdef adjust_take_profit(self, float64_t price):
        if self.take_profit_order is not None:
            self.take_profit_order.adjust_price(price)

    cpdef adjust_trailing_distance(self, float64_t distance):
        if self.trailing_stop_loss_order is not None:
            self.trailing_stop_loss_order.adjust_distance(distance)
