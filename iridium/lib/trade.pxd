from numpy cimport (
int64_t,
float64_t,
uint32_t
)
from cpython.datetime cimport datetime
from .order cimport TakeProfitOrder, StopLossOrder, TrailingStopLossOrder

cpdef enum TradeState:
    OPEN
    CLOSED

cdef class Trade:
    cdef:
        readonly str trade_id
        readonly str instrument
        readonly float64_t price
        readonly TradeState state
        readonly datetime open_time
        readonly int64_t initial_units
        readonly float64_t initial_margin
        readonly int64_t current_units
        readonly float64_t realized_profit_loss
        readonly float64_t unrealized_profit_loss
        readonly float64_t margin_used
        readonly float64_t financing
        readonly datetime close_time
        readonly TakeProfitOrder take_profit_order
        readonly StopLossOrder stop_loss_order
        readonly TrailingStopLossOrder trailing_stop_loss_order
        readonly float64_t spread
        readonly float64_t commission

    cpdef set_take_profit_order(self, TakeProfitOrder order)

    cpdef set_stop_loss_order(self, StopLossOrder order)

    cpdef set_trailing_stop_loss_order(self, TrailingStopLossOrder order)

    cpdef float64_t calculate_unrealized_profit_loss(self,
                                                     float64_t current_account_vs_quote_rate,
                                                     float64_t current_price)

    cpdef float64_t partially_close_trade(self,
                                          float64_t current_account_vs_quote_rate,
                                          float64_t current_price,
                                          int64_t units)

    cpdef float64_t close_trade(self,
                                float64_t current_account_vs_quote_rate,
                                float64_t current_price,
                                datetime close_time)

    cpdef float64_t calculate_margin_used(self,
                                          float64_t current_account_vs_base_rate,
                                          uint32_t leverage)

    cpdef adjust_stop_loss(self, float64_t price)

    cpdef adjust_take_profit(self, float64_t price)

    cpdef adjust_trailing_distance(self, float64_t distance)
