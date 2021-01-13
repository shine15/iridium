import click
import pandas as pd
from iridium.utils.trading_calendar import DataFrequency


class TradingDateTimeParam(click.ParamType):
    name = "trading_datetime"

    def convert(self, value, param, ctx):
        try:
            pd.Timestamp(value)
            return value
        except Exception as err:
            self.fail(err, param=param, ctx=ctx)


class DataFrequencyParam(click.ParamType):
    name = "data_frequency"

    def convert(self, value, param, ctx):
        try:
            return DataFrequency[value]
        except Exception as err:
            self.fail(err, param=param, ctx=ctx)


TRADING_DATETIME = TradingDateTimeParam()
DATA_FREQUENCY = DataFrequencyParam()

