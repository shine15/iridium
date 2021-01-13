from ...lib.requests import request, HttpMethod
from ..hdf5 import HDFData
from iridium.utils.trading_calendar import DataFrequency

TRADE_ENDPOINT = "https://api-fxtrade.oanda.com"
PRACTICE_ENDPOINT = "https://api-fxpractice.oanda.com"


class HDF5DataOanda(HDFData):

    def map_data(self, row, instrument, from_time, to_time, data_frequency):
        while True:
            resp = self._oanda_history_data(instrument, from_time, to_time)
            if resp["candles"]:
                candles = sorted([candle for candle in resp['candles'] if candle['complete']],
                                 key=lambda data: data['time'],
                                 reverse=True)
                for candle in candles:
                    volume = candle['volume']
                    if volume < 3 and self._data_frequency >= DataFrequency.H1:
                        continue
                    row['time'] = int(float(candle['time']))
                    row['open'] = float(candle['mid']['o'])
                    row['close'] = float(candle['mid']['c'])
                    row['high'] = float(candle['mid']['h'])
                    row['low'] = float(candle['mid']['l'])
                    row['volume'] = volume
                    row.append()
                to_time = int(float(candles[-1]['time']))
                if to_time < from_time:
                    break
            else:
                break

    @staticmethod
    def auth_request_default(
            url,
            access_token,
            method,
            datetime_format,
            params=None,
            data=None):
        """

        :param url:
        :param access_token:
        :param method:
        :param datetime_format:
        :param params:
        :param data:
        :return:
        """
        headers = {
            "Content-Type": "application/json",
            "Accept-Datetime-Format": datetime_format,
            "Authorization": "Bearer {}".format(access_token)
        }
        return request(
            url=url,
            method=method,
            headers=headers,
            params=params,
            data=data)

    @staticmethod
    def candlestick_data(
            access_token,
            instrument,
            granularity,
            price="M",
            count=None,
            from_time=None,
            to_time=None,
            is_trade_env=False,
            datetime_format='UNIX'):
        """
        https://developer.oanda.com/rest-live-v20/instrument-ep/
        :param access_token:
        :param instrument:
        :param price:
        :param granularity:
        :param count:
        :param from_time:
        :param to_time:
        :param is_trade_env:
        :param datetime_format: UNIX, RFC3339
        :return:
        """
        host = TRADE_ENDPOINT if is_trade_env else PRACTICE_ENDPOINT
        path = "/v3/instruments/{}/candles".format(instrument)
        url = "{}{}".format(host, path)
        params = {'price': price,
                  'granularity': granularity,
                  'to': to_time}
        if count is None:
            params['from'] = from_time
        else:
            params['count'] = count
        return HDF5DataOanda.auth_request_default(
            url=url,
            access_token=access_token,
            method=HttpMethod.GET,
            datetime_format=datetime_format,
            params=params)

    def _oanda_history_data(self, instrument, from_time, to_time):
        count = None
        if self._data_frequency < DataFrequency.D:
            count = 5000
        return self.candlestick_data(
            access_token=self._token,
            instrument=instrument,
            granularity=self._data_frequency.name,
            datetime_format='UNIX',
            from_time=from_time,
            to_time=to_time,
            count=count
        )

