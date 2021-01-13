from tables import *
from pathlib import Path
from contextlib import closing
from iridium.utils.file import make_dirs_path_no_exist
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from iridium.utils.trading_calendar import DataFrequency, ForexCalendar
from dateutil.tz import tzlocal

FILTERS = Filters(complib='zlib', complevel=5)
DIRECTORY_PATH = str(Path.home()) + '/.iridium/data'
FILE_PATH = DIRECTORY_PATH + '/history.h5'


class HDFData(ABC):
    """
    Abstract class for HDF5 format data
    """

    def __init__(self, token, instruments, source, start, end, data_frequency):
        """
        HDFData init
        :param token: authentication token
        :param instruments: list of instrument name
        :param source: data source
        :param start: start date time, timestamp
        :param end: end date time, timestamp
        :param data_frequency: iridium.trading_calendar.DataFrequency
        """
        self._token = token
        self._instruments = instruments
        self._source = source
        self._start = start
        self._end = end
        self._data_frequency = data_frequency

    class Price(IsDescription):
        """
        HDF5 price row definition
        """
        time = UInt32Col()
        open = Float32Col()
        close = Float32Col()
        high = Float32Col()
        low = Float32Col()
        volume = UInt32Col()

    def create_hdf5_file(self):
        make_dirs_path_no_exist(DIRECTORY_PATH)
        with closing(open_file(FILE_PATH, mode='a', filters=FILTERS)) as hdf:
            if '/instruments' in hdf:
                group = hdf.get_node('/instruments')
            else:
                group = hdf.create_group("/", 'instruments', 'Forex instrument history data')
            for instrument in self._instruments:
                from_time = self._start
                to_time = self._end
                table_name = '{}_{}'.format(instrument, self._data_frequency.name)
                table_path = '/instruments/{}'.format(table_name)
                if table_path in group:
                    table = hdf.get_node(table_path)
                    if len(table) >= 1:
                        from_time = table.cols.time[0]
                else:
                    table = hdf.create_table(group, table_name, HDFData.Price, table_name)
                if from_time > to_time:
                    continue
                self.map_data(row=table.row,
                              instrument=instrument,
                              from_time=from_time,
                              to_time=to_time,
                              data_frequency=self._data_frequency)
                self._flush_table(table)

        return FILE_PATH

    @staticmethod
    def read_hdf(instrument, frequency, start, end, path=FILE_PATH):
        """
        Read instruments history data file
        :param instrument: instrument name, string
        :param frequency:
        M* - Minute, H - hour, D - day, W - Week, M - Month
        M1, M2, M4, M5, M10, M15, M30
        H1, H2, H3, H4, H6, H8, H12,
        D, W
        :param start: start date, str or datetime-like
        :param end: end date, str or datetime-like
        :param path: HDF5 file path
        :return: pandas DataFrame
        """
        with closing(open_file(path, mode='r')) as hdf:
            table_name = '{}_{}'.format(instrument, frequency)
            table = hdf.root.instruments[table_name]
            trading_sessions = ForexCalendar().trading_sessions(start, end, frequency)
            if not trading_sessions:
                return None
            start_datetime = trading_sessions[0].start
            end_datetime = trading_sessions[-1].end
            result = np.array([[x['time'], x['open'], x['close'], x['high'], x['low'], x['volume']]
                               for x in table.read_where('( time >= {}) & (time <= {})'.
                                                         format(start_datetime.timestamp(),
                                                                end_datetime.timestamp())
                                                         )])
            dates = [pd.Timestamp(x, unit='s', tz=tzlocal()) for x in result[:, 0]]
            history_data = pd.DataFrame({'open': result[:, 1],
                                         'close': result[:, 2],
                                         'high': result[:, 3],
                                         'low': result[:, 4],
                                         'volume': result[:, 5]},
                                        index=dates)
            history_data.sort_index(inplace=True)
            return history_data

    @staticmethod
    def resample(instrument, from_frequency, to_frequency, start, end, path=FILE_PATH):
        """
        Read instruments history data file
        :param instrument: instrument name, string
        :param from_frequency:
        M* - Minute, H - hour, D - day, W - Week, M - Month
        M1, M2, M4, M5, M10, M15, M30
        H1, H2, H3, H4, H6, H8, H12,
        D, W, M
        :param to_frequency: same with from_frequency
        :param start: start date, str or datetime-like
        :param end: end date, str or datetime-like
        :param path: HDF5 file path
        :return: pandas DataFrame
        """
        if DataFrequency[to_frequency] <= DataFrequency[from_frequency]:
            raise Exception('to_frequency must be greater than from_frequency')
        history = HDFData.read_hdf(
            instrument=instrument,
            start=start,
            end=end,
            frequency=from_frequency,
            path=path)

        def forex_data_resample(array_like):
            index = array_like.index
            if len(index) > 0:
                from_freq = DataFrequency[from_frequency]
                if from_freq < DataFrequency.D:
                    timedelta = (index[-1] - index[0]).seconds + DataFrequency[from_frequency].value
                    if timedelta < DataFrequency[to_frequency].value:
                        return
                if array_like.name == 'open':
                    return array_like[0]
                elif array_like.name == 'close':
                    return array_like[-1]
                elif array_like.name == 'high':
                    return array_like.max()
                elif array_like.name == 'low':
                    return array_like.min()
                elif array_like.name == 'volume':
                    return array_like.sum()

        to_freq = DataFrequency[to_frequency]
        resample_freq = to_freq.resample_desc
        if to_freq <= DataFrequency.H1:
            # hour alignment
            resample_data = history.resample(resample_freq).apply(forex_data_resample).dropna()
        else:
            # day alignment to New York timezone 17:00
            history.index = history.index.tz_convert('America/New_York')
            if to_freq <= DataFrequency.D:
                loffset = None
            elif to_freq == DataFrequency.W:
                loffset = '17h'
            resample_data = history.resample(resample_freq, base=17, loffset=loffset, label='left') \
                .apply(forex_data_resample).dropna()
            resample_data.index = resample_data.index.tz_convert(tzlocal())

        return resample_data

    @staticmethod
    def _flush_table(table):
        table.flush()
        if table.cols.time.index:
            table.cols.time.reindex()
        else:
            table.cols.time.create_index()

    @abstractmethod
    def map_data(self, row, instrument, from_time, to_time, data_frequency):
        raise NotImplementedError
