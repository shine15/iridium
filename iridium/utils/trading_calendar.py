from dateutil.tz import tzlocal
from enum import IntEnum
from collections import namedtuple
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday

from datetime import timedelta
import pytz
import pandas as pd


class DataFrequency(IntEnum):
    M1 = 60
    M2 = 2 * M1
    M4 = 4 * M1
    M5 = 5 * M1
    M10 = 10 * M1
    M15 = 15 * M1
    M30 = 30 * M1
    H1 = 60 * M1
    H2 = 2 * H1
    H3 = 3 * H1
    H4 = 4 * H1
    H6 = 6 * H1
    H8 = 8 * H1
    H12 = 12 * H1
    D = 24 * H1
    W = 5 * D

    @property
    def resample_desc(self):
        if self == DataFrequency.M1:
            return '1min'
        elif self == DataFrequency.M2:
            return '2min'
        elif self == DataFrequency.M4:
            return '4min'
        elif self == DataFrequency.M5:
            return '5min'
        elif self == DataFrequency.M10:
            return '10min'
        elif self == DataFrequency.M15:
            return '15min'
        elif self == DataFrequency.M30:
            return '30min'
        elif self == DataFrequency.H1:
            return '1h'
        elif self == DataFrequency.H2:
            return '2h'
        elif self == DataFrequency.H4:
            return '4h'
        elif self == DataFrequency.H8:
            return '8h'
        elif self == DataFrequency.H12:
            return '12h'
        elif self == DataFrequency.D:
            return '24h'
        elif self == DataFrequency.W:
            return 'W-FRI'


def following_monday(dt):
    """
    If holiday falls on Saturday or Sunday, use the following Monday instead;
    """
    if dt.weekday() == 5:
        return dt + timedelta(2)
    elif dt.weekday() == 6:
        return dt + timedelta(1)
    return dt


class ForexCalendar(AbstractHolidayCalendar):
    """
    Forex Calendar based on the Forex history data from Oanda
    """
    rules = [
        Holiday("New Years Day", month=1, day=1, observance=following_monday),
        Holiday("Christmas", month=12, day=25, observance=following_monday)
    ]

    TradingSession = namedtuple('TradingSession', 'start end')

    def trading_sessions(self, start, end, frequency='D'):
        """
        Returns trading sessions between start_date and end_date
        :param start: starting date, str or datetime-like
        :param end: ending date, str or datetime-like
        :param frequency: str
        M* - Minute, H - hour, D - day, W - Week, M - Month
        M1, M2, M4, M5, M10, M15, M30
        H1, H2, H3, H4, H6, H8, H12,
        D, W
        :return: List of tuple TradingSession, local timezone
        """
        # Forex trading starts from Sydney session & ends in New York session
        # More details https://www.babypips.com/learn/forex/forex-trading-sessions
        new_york_tz = 'America/New_York'
        # type validation & timezone conversion
        if type(start) == str:
            start_datetime = pd.Timestamp(start, tz=new_york_tz)
        elif type(start) == pd.Timestamp:
            start_datetime = start.tz_localize(pytz.utc).tz_convert(new_york_tz) \
                if not start.tzname() else start.tz_convert(new_york_tz)
        else:
            raise TypeError('only support str or datetime-like format')
        if type(end) == str:
            end_datetime = pd.Timestamp(end, tz=new_york_tz)
        elif type(end) == pd.Timestamp:
            end_datetime = end.tz_localize(pytz.utc).tz_convert(new_york_tz) \
                if not end.tzname() else end.tz_convert(new_york_tz)
        else:
            raise TypeError('only support str or datetime-like format')
        data_frequency = DataFrequency[frequency]
        weekdays = pd.bdate_range(start=start_datetime, end=end_datetime)
        holidays = self.holidays(start=start_datetime, end=end_datetime)
        trading_days = [day for day in weekdays if day not in holidays]
        trading_sessions = []
        for date in trading_days:
            trading_end = pd.Timestamp(year=date.year,
                                       month=date.month,
                                       day=date.day,
                                       hour=17,
                                       tzinfo=pytz.timezone(new_york_tz)).astimezone(tzlocal())
            trading_start = trading_end - pd.tseries.offsets.DateOffset(hours=24)
            session = ForexCalendar.TradingSession(trading_start,
                                                   trading_end - pd.tseries.offsets.DateOffset(seconds=1))
            trading_sessions.append(session)
        if not trading_sessions:
            return None
        if data_frequency == DataFrequency.D:
            return trading_sessions
        elif data_frequency not in (DataFrequency.D, DataFrequency.W):
            all_sessions = []
            for session in trading_sessions:
                session_start = session.start
                session_end = session.end
                session_opens = pd.date_range(start=session_start, end=session_end,
                                              freq='{}S'.format(data_frequency.value))
                session_closes = [session_open + pd.tseries.offsets.DateOffset(seconds=data_frequency.value - 1)
                                  for session_open in session_opens]
                sessions = [ForexCalendar.TradingSession(start, end)
                            for start, end in zip(session_opens, session_closes)
                            if start >= start_datetime and end <= end_datetime]
                all_sessions.extend(sessions)
            return all_sessions
        elif data_frequency == DataFrequency.W:
            session_closes = pd.DatetimeIndex([session.start.tz_convert(new_york_tz)
                                               for session in trading_sessions]) \
                .to_series(keep_tz=True) \
                .resample(data_frequency.resample_desc, loffset='17h') \
                .last() \
                .index
            session_opens = []
            for session_close in session_closes:
                session_open = session_close - pd.tseries.offsets.DateOffset(days=7)
                if session_open.dst().days == 0 and session_close.dst().days == 1:
                    session_open = session_open + pd.tseries.offsets.DateOffset(hours=1)
                elif session_open.dst().days == 1 and session_close.dst().days == 0:
                    session_open = session_open - pd.tseries.offsets.DateOffset(hours=1)
                session_opens.append(session_open)
            sessions = [ForexCalendar.TradingSession(start.tz_convert(tzlocal()),
                                                     (end - pd.tseries.offsets.DateOffset(seconds=1))
                                                     .tz_convert(tzlocal()))
                        for start, end in zip(session_opens, session_closes)
                        if start >= start_datetime and end <= end_datetime]
            return sessions
