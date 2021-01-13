from loguru import logger
from talib.abstract import EMA


FAST_PERIOD = 12
SLOW_PERIOD = 26


def handle_data(trader, sim_data, time):
    for instrument, data in sim_data.items():
        # skip if the current price unavailable
        if data.iloc[-1].isnull().values.any():
            continue
        current_price = data.iloc[-1]['close']
        fast_ema = EMA(data, timeperiod=FAST_PERIOD, price='close')
        slow_ema = EMA(data, timeperiod=SLOW_PERIOD, price='close')
        # moving average trigger condition
        long_or_short = None
        if fast_ema[-1] > slow_ema[-1] and \
                fast_ema[-2] < slow_ema[-2]:
            long_or_short = True
        if fast_ema[-1] < slow_ema[-1] and \
                fast_ema[-2] > slow_ema[-2]:
            long_or_short = False
        if long_or_short is not None:
            logger.info("trade time: {}".format(time))

