import uuid

cdef class TakeProfitDetails:
    def __init__(self, price, time_in_force=TimeInForce.GTC, gtd_time=None):
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time

cdef class StopLossDetails:
    def __init__(self, price, time_in_force=TimeInForce.GTC, gtd_time=None):
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time

cdef class TrailingStopLossDetails:
    def __init__(self, distance, time_in_force=TimeInForce.GTC, gtd_time=None):
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time

cdef class Order:
    def __init__(self, create_time):
        self.order_id = str(uuid.uuid4())
        self.state = OrderState.PENDING
        self.create_time = create_time

    cpdef set_state(self, OrderState state):
        self.state = state


cdef class MarketOrder(Order):
    def __init__(self,
                 instrument,
                 units,
                 market_price,
                 create_time,
                 take_profit=None,
                 stop_loss=None,
                 trailing_stop_loss=None,
                 price_bound=0.00,
                 order_position_fill=OrderPositionFill.REDUCE_FIRST,
                 time_in_force=TimeInForce.GTC):
        self.instrument = instrument
        self.units = units
        self.market_price = market_price
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.trailing_stop_loss = trailing_stop_loss
        self.price_bound = price_bound
        self.order_position_fill = order_position_fill
        self.time_in_force = time_in_force
        super().__init__(create_time)


cdef class TakeProfitOrder(Order):
    def __init__(self,
                 trade_id,
                 price,
                 create_time,
                 time_in_force=TimeInForce.GTC,
                 gtd_time=None,
                 trigger=OrderTriggerCondition.DEFAULT):
        self.trade_id = trade_id
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger = trigger
        super().__init__(create_time)

    cpdef adjust_price(self, float64_t price):
        self.price = price

cdef class StopLossOrder(Order):
    def __init__(self,
                 trade_id,
                 price,
                 create_time,
                 time_in_force=TimeInForce.GTC,
                 gtd_time=None,
                 trigger=OrderTriggerCondition.DEFAULT):
        self.trade_id = trade_id
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger = trigger
        super().__init__(create_time)

    cpdef adjust_price(self, float64_t price):
        self.price = price

cdef class TrailingStopLossOrder(Order):
    def __init__(self,
                 trade_id,
                 distance,
                 price,
                 create_time,
                 time_in_force=TimeInForce.GTC,
                 gtd_time=None,
                 trigger=OrderTriggerCondition.DEFAULT):
        self.trade_id = trade_id
        self.distance = distance
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger = trigger
        super().__init__(create_time)

    cpdef adjust_distance(self, float64_t distance):
        self.distance = distance

    cpdef adjust_price(self, float64_t price):
        self.price = price