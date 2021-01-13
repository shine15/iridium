from iridium.utils.trading_calendar import ForexCalendar
from iridium.data.hdf5 import HDFData
import pandas as pd
import numpy as np
import warnings
from dateutil.tz import tzlocal
from ..resources import SAMPLE_DATA_PATH

start = pd.Timestamp(year=2014,
                     month=1,
                     day=1,
                     tz=tzlocal())
end = pd.Timestamp(year=2019,
                   month=1,
                   day=1,
                   tz=tzlocal())


def test_trading_calendar():
    test_freqs = ['H4', 'H8', 'H12', 'D', 'W']
    for freq in test_freqs:
        history_start_time = HDFData.read_hdf(instrument='EUR_USD',
                                              frequency=freq,
                                              start=start,
                                              end=end,
                                              path=SAMPLE_DATA_PATH).index
        trading_start_time = pd.DatetimeIndex([session.start for session in
                                               ForexCalendar().trading_sessions(start=start, end=end, frequency=freq)])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert np.array_equal(trading_start_time, history_start_time)
