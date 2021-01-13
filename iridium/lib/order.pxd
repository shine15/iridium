from cpython.datetime cimport datetime
from numpy cimport (
int64_t,
float64_t
)

cpdef enum OrderState:
    PENDING
    FILLED
    TRIGGERED
    CANCELLED

cpdef enum TimeInForce:
    GTC
    GTD
    GFD
    FOK
    IOC

cpdef enum OrderPositionFill:
    OPEN_ONLY
    REDUCE_FIRST
    REDUCE_ONLY

cpdef enum OrderTriggerCondition:
    DEFAULT
    INVERSE
    BID
    ASK
    MID

cdef class TakeProfitDetails:
    cdef:
        readonly float64_t price
        readonly TimeInForce time_in_force
        readonly datetime gtd_time

cdef class StopLossDetails:
    cdef:
        readonly float64_t price
        readonly TimeInForce time_in_force
        readonly datetime gtd_time

cdef class TrailingStopLossDetails:
    cdef:
        readonly float64_t distance
        readonly TimeInForce time_in_force
        readonly datetime gtd_time

cdef class Order:
    cdef:
        readonly str order_id
        readonly OrderState state
        readonly datetime create_time
    cpdef set_state(self, OrderState state)

cdef class MarketOrder(Order):
    cdef:
        readonly str instrument
        readonly int64_t units
        readonly float64_t market_price
        readonly TakeProfitDetails take_profit
        readonly StopLossDetails stop_loss
        readonly TrailingStopLossDetails trailing_stop_loss
        readonly float64_t price_bound
        readonly OrderPositionFill order_position_fill
        readonly TimeInForce time_in_force

cdef class TakeProfitOrder(Order):
    cdef:
        readonly str trade_id
        readonly float64_t price
        readonly TimeInForce time_in_force
        readonly datetime gtd_time
        readonly OrderTriggerCondition trigger

    cpdef adjust_price(self, float64_t price)

cdef class StopLossOrder(Order):
    cdef:
        readonly str trade_id
        readonly float64_t price
        readonly TimeInForce time_in_force
        readonly datetime gtd_time
        readonly OrderTriggerCondition trigger

    cpdef adjust_price(self, float64_t price)

cdef class TrailingStopLossOrder(Order):
    cdef:
        readonly str trade_id
        readonly float64_t distance
        readonly float64_t price
        readonly TimeInForce time_in_force
        readonly datetime gtd_time
        readonly OrderTriggerCondition trigger

    cpdef adjust_distance(self, float64_t distance)

    cpdef adjust_price(self, float64_t price)