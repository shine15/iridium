from datetime import datetime
import bisect
from sys import platform as sys_pf
import numpy as np
import pandas as pd


if sys_pf == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc
import matplotlib.dates as mdates
from matplotlib.ticker import Formatter, MaxNLocator
from iridium.data.hdf5 import HDFData, FILE_PATH
from iridium.utils.trading_calendar import DataFrequency


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


def draw_candlestick_chart(df):
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
    return fig, ax


def add_annotate(ax, message, x, y, x_offset=15, y_offset=15):
    ax.annotate(
        message,
        xy=(x, y),
        xytext=(x_offset, y_offset),
        textcoords='offset points',
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
        color="black"
    )


def chart_data(instrument, frequency, start, end, start_offset=0, end_offset=0, file_path=FILE_PATH):
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
    chart_start = pd.Timestamp(start, unit='s') - pd.Timedelta(start_offset * DataFrequency[frequency].value, unit='s')
    chart_end = pd.Timestamp(end, unit='s') + pd.Timedelta(end_offset * DataFrequency[frequency].value, unit='s')
    return HDFData.read_hdf(instrument, frequency, chart_start, chart_end, file_path)


def date_time_index(df, date_time):
    """
    find time index for chart
    :param df: pandas data frame
    :param date_time: timestamp
    :return: time index
    """
    dt = pd.Timestamp(date_time, unit='s')
    idx = np.searchsorted(df.index.asi8, dt.value, side="left")
    return idx


if __name__ == "__main__":
    instrument = "EUR_USD"
    freq = "D"
    start = 1548108060
    end = 1548339840
    start_offset = 0
    end_offset = 0
    df = chart_data(instrument, freq, start, end, start_offset, end_offset)
    fig, ax = draw_candlestick_chart(df)
    x1 = date_time_index(df, start)
    y1 = df.close[x1]
    add_annotate(ax, y1, x1, y1)

    plt.show()
