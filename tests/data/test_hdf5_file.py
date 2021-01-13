from iridium.data.sources.oanda import HDF5DataOanda
from iridium.data.hdf5 import FILE_PATH, HDFData
import pandas as pd
import pytest
from ..resources import SAMPLE_DATA_PATH
from dateutil.tz import tzlocal


@pytest.fixture(scope="module")
def h5_file():
    token = 'token'
    instruments = ['EUR_USD']
    source = 'oanda'
    start = pd.Timestamp(2019, 10, 1).timestamp()
    end = pd.Timestamp(2019, 11, 1).timestamp()
    data_frequency = 'daily'
    h5 = HDF5DataOanda(token=token,
                       instruments=instruments,
                       source=source,
                       start=start,
                       end=end,
                       data_frequency=data_frequency)
    return h5


def test_create_hdf5_file(monkeypatch, h5_file):
    def mock_create_hdf5_file(self):
        return FILE_PATH

    monkeypatch.setattr(HDFData, "create_hdf5_file", mock_create_hdf5_file)
    h5_file_path = h5_file.create_hdf5_file()
    assert h5_file_path == FILE_PATH


def test_resample():
    # 1 week sample data
    start = pd.Timestamp(year=2019,
                         month=9,
                         day=30,
                         hour=7,
                         tz=tzlocal())
    end = pd.Timestamp(year=2019,
                       month=10,
                       day=5,
                       hour=7,
                       tz=tzlocal())
    to_freq = 'D'
    df_day = HDFData.read_hdf(instrument='EUR_USD',
                              start=start,
                              end=end,
                              frequency=to_freq,
                              path=SAMPLE_DATA_PATH)
    for from_freq in ['M15', 'M30', 'H1', 'H4', 'H8', 'H12']:
        resample_data = HDFData.resample(instrument='EUR_USD',
                                         from_frequency=from_freq,
                                         to_frequency=to_freq,
                                         start=start,
                                         end=end,
                                         path=SAMPLE_DATA_PATH)
        assert df_day.equals(resample_data)
