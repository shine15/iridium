import pandas as pd
from iridium.lib.validation import expect_types
from iridium.utils.type import Singleton

DEFAULT_CAPITAL_BASE = 1e5
DEFAULT_LEVERAGE = 50
DEFAULT_ACCOUNT_CURRENCY = 'USD'
DEFAULT_DATA_FREQUENCY = 'D'
DEFAULT_COMMISSION = 0.0
DEFAULT_HISTORY_DATA_NUMBER = 60


class SimulationParameters(metaclass=Singleton):
    @expect_types(start=pd.Timestamp,
                  end=pd.Timestamp)
    def __init__(self,
                 start,
                 end,
                 instruments,
                 spread,
                 commission=DEFAULT_COMMISSION,
                 account_currency=DEFAULT_ACCOUNT_CURRENCY,
                 leverage=DEFAULT_LEVERAGE,
                 capital_base=DEFAULT_CAPITAL_BASE,
                 data_frequency=DEFAULT_DATA_FREQUENCY,
                 hist_data_num=DEFAULT_HISTORY_DATA_NUMBER):
        self._start = start
        self._end = end
        self._instruments = instruments
        self._spread = spread
        self._commission = commission
        self._account_currency = account_currency
        self._leverage = leverage
        self._balance = capital_base
        self._data_frequency = data_frequency
        self._hist_data_num = hist_data_num

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def instruments(self):
        return self._instruments

    @property
    def account_currency(self):
        return self._account_currency

    @property
    def spread(self):
        return self._spread

    @property
    def commission(self):
        return self._commission

    @property
    def leverage(self):
        return self._leverage

    @property
    def balance(self):
        return self._balance

    @property
    def data_frequency(self):
        return self._data_frequency

    @property
    def hist_data_num(self):
        return self._hist_data_num

    def __repr__(self):
        return """
        {class_name}(
        start={start},
        end={end},
        instruments={instruments},
        account_currency={account_currency},
        spread={spread},
        commission={commission},
        leverage={leverage},
        balance={balance},
        data_frequency={data_frequency},
        hist_data_num={hist_data_num}
    )\
    """.format(class_name=self.__class__.__name__,
               start=self.start,
               end=self.end,
               instruments=self.instruments,
               account_currency=self.account_currency,
               spread=self.spread,
               commission=self.commission,
               leverage=self.leverage,
               balance=self.balance,
               data_frequency=self.data_frequency.name,
               hist_data_num=self.hist_data_num)
