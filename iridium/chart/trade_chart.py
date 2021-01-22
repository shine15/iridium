import os
from datetime import datetime
from sys import platform as sys_pf
import numpy as np
import pandas as pd
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from mpl_finance import candlestick2_ohlc
import matplotlib.dates as mdates
from matplotlib.ticker import Formatter, MaxNLocator
from ..data.hdf5 import HDFData, FILE_PATH
from ..utils.trading_calendar import DataFrequency


class TradeDateFormatter(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        """Return the label for time x at position pos"""
        ind = int(np.round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''
        return mdates.num2date(self.dates[ind]).strftime(self.fmt)


def _chart_data(instrument, frequency, start, end, start_offset=0, end_offset=0, file_path=FILE_PATH):
    chart_start = pd.Timestamp(start, unit='s') - pd.Timedelta(start_offset * DataFrequency[frequency].value, unit='s')
    chart_end = pd.Timestamp(end, unit='s') + pd.Timedelta(end_offset * DataFrequency[frequency].value, unit='s')
    return HDFData.read_hdf(instrument, frequency, chart_start, chart_end, file_path)


def draw_candlestick_chart(instrument, frequency, start, end, start_offset=0, end_offset=0, file_path=FILE_PATH):
    """
    Prepare data for chart
    :param instrument: instrument name, string
    :param frequency:
    M* - Minute, H - hour, D - day, W - Week, M - Month
    M1, M2, M4, M5, M10, M15, M30
    H1, H2, H3, H4, H6, H8, H12,
    D, W
    :param start: timestamp
    :param end: timestamp
    :param start_offset: int
    :param end_offset: int
    :param file_path: HDF5 file path
    :return: pandas DataFrame
    """
    df = _chart_data(instrument, frequency, start, end, start_offset, end_offset, file_path)
    fig, ax = plt.subplots(1, 1, sharex=True, figsize=(10, 5))
    line_width = 0.6
    date_list = [mdates.date2num(datetime.fromtimestamp(date.timestamp())) for date in df.index]
    open_list = df.open.values
    close_list = df.close.values
    high_list = df.high.values
    low_list = df.low.values
    candlestick2_ohlc(
        ax=ax,
        opens=open_list,
        highs=high_list,
        lows=low_list,
        closes=close_list,
        width=line_width,
        colorup='green',
        colordown='red',
        alpha=1.0)
    formatter = TradeDateFormatter(date_list)
    ax.xaxis.set_major_formatter(formatter)
