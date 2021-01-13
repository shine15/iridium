import threading
import tables as tb
from iridium.data.hdf5 import FILE_PATH
import asyncio
import numpy as np
import pandas as pd
from dateutil.tz import tzlocal
import os
from collections import namedtuple
from loguru import logger


class NoDataSet(Exception):
    """
    Raised when trading price cannot be found for a currency pair.
    """
    pass


class TradingData:
    """
    Data for trading simulation
    """
    lock = threading.Lock()

    def __enter__(self):
        self.event_loop = asyncio.get_event_loop()
        self.hdf = TradingData._synchronized_open_file(FILE_PATH, mode='r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.event_loop.close()
        self._synchronized_close_file()

    async def query_instrument_data(self,
                                    instrument,
                                    trade_time,
                                    freq,
                                    semaphore):
        try:
            async with semaphore:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, self._get_instrument_data,
                                                  instrument, trade_time, freq)
        except Exception as exc:
            logger.exception(exc)
            return instrument, None
        else:
            return instrument, data

    async def query_instruments_data(self,
                                     instruments,
                                     trade_time,
                                     freq,
                                     concur_req=os.cpu_count()):
        semaphore = asyncio.Semaphore(concur_req)
        queries = [self.query_instrument_data(instrument, trade_time, freq, semaphore) for instrument in instruments]
        queries_iter = asyncio.as_completed(queries)
        results = {}
        for future in queries_iter:
            try:
                result = await future
            except Exception as exc:
                logger.exception(exc)
            else:
                name, data = result
                results[name] = None if (data is None or data.size == 0) else data[0]
        return results

    def _get_instrument_data(self, instrument, trade_time, freq):
        """

        :param instrument:
        :param trade_time:
        :param freq:
        :return:
        """
        table_name = '{}_{}'.format(instrument, freq)
        table = self.hdf.root.instruments[table_name]
        data = table.read_where('time == {}'.format(trade_time.timestamp()))
        return data

    async def query_instrument_history(self,
                                       instrument,
                                       before_trade_time,
                                       freq,
                                       numbers,
                                       semaphore):
        try:
            async with semaphore:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, self._get_instrument_history,
                                                  instrument, before_trade_time, freq, numbers)
        except Exception as exc:
            logger.exception(exc)
            return instrument, None
        else:
            return instrument, data

    async def query_instruments_history(self,
                                        instruments,
                                        before_trade_time,
                                        freq,
                                        numbers,
                                        concur_req=os.cpu_count()):
        semaphore = asyncio.Semaphore(concur_req)
        queries = [self.query_instrument_history(instrument, before_trade_time, freq, numbers, semaphore)
                   for instrument in instruments]
        queries_iter = asyncio.as_completed(queries)
        results = {}
        for future in queries_iter:
            try:
                result = await future
            except Exception as exc:
                logger.exception(exc)
            else:
                name, history_data = result
                results[name] = history_data
        return results

    def _get_instrument_history(self, instrument, before_trade_time, freq, numbers):
        """

        :param instrument:
        :param before_trade_time:
        :param freq:
        :param numbers:
        :return:
        """
        table_name = '{}_{}'.format(instrument, freq)
        table = self.hdf.root.instruments[table_name]
        data = table.read_where('time < {}'.format(before_trade_time.timestamp()))
        result = np.array([[x['time'], x['open'], x['close'], x['high'], x['low'], x['volume']]
                           for x in data])
        dates = [pd.Timestamp(x, unit='s', tz=tzlocal()) for x in result[:, 0]]
        history_data = pd.DataFrame({'open': result[:, 1],
                                     'close': result[:, 2],
                                     'high': result[:, 3],
                                     'low': result[:, 4],
                                     'volume': result[:, 5]},
                                    index=dates)
        history_data.sort_index(inplace=True, ascending=False)
        return history_data[:numbers][::-1]

    @property
    def instruments_support_simulation(self):
        instruments = [name for name in
                       self.hdf.root.instruments._v_children.keys() if name.split('_')[-1] == 'M1']
        return instruments

    def get_account_vs_currencies_for_simulation(self, account, currencies, trade_time):
        Pair = namedtuple('Pair', 'name currency reversed')
        account_vs_currency_pairs = set()
        rates = {}
        for currency in currencies:
            if currency == account:
                rates[currency] = float(1)
            else:
                pair = '{}_{}'.format(account, currency)
                reversed_pair = '{}_{}'.format(currency, account)
                if '{}_M1'.format(pair) in self.instruments_support_simulation:
                    account_vs_currency_pairs.add(Pair(name=pair, currency=currency, reversed=False))
                elif '{}_M1'.format(reversed_pair) in self.instruments_support_simulation:
                    account_vs_currency_pairs.add(Pair(name=reversed_pair, currency=currency, reversed=True))
                else:
                    raise NoDataSet()
        results = self.get_instruments_data(
            instruments=[pair.name for pair in account_vs_currency_pairs],
            trade_time=trade_time,
            freq='M1')
        for pair in account_vs_currency_pairs:
            if results[pair.name] is None:
                rates[pair.currency] = None
            else:
                if pair.reversed:
                    rates[pair.currency] = 1 / results[pair.name]['close']
                else:
                    rates[pair.currency] = results[pair.name]['close']
        return rates

    def get_instruments_data(self,
                             instruments,
                             trade_time,
                             freq,
                             concur_req=os.cpu_count()):
        coro = self.query_instruments_data(
            instruments=instruments,
            trade_time=trade_time,
            freq=freq,
            concur_req=concur_req)
        results = self.event_loop.run_until_complete(coro)
        return results

    def get_instruments_history(self,
                                instruments,
                                before_trade_time,
                                freq,
                                numbers,
                                concur_req=os.cpu_count()):
        coro = self.query_instruments_history(
            instruments=instruments,
            before_trade_time=before_trade_time,
            freq=freq,
            numbers=numbers,
            concur_req=concur_req
        )
        results = self.event_loop.run_until_complete(coro)
        return results

    @staticmethod
    def _synchronized_open_file(*args, **kwargs):
        with TradingData.lock:
            return tb.open_file(*args, **kwargs)

    def _synchronized_close_file(self):
        with TradingData.lock:
            return self.hdf.close()
