from sys import platform as sys_pf
from mpl_finance import candlestick2_ohlc
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from iridium.data.hdf5 import HDFData, FILE_PATH
from iridium.utils.trading_calendar import DataFrequency
from iridium.utils.alg import binary_search_left

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


class TradeChart:
    def __init__(self,
                 instrument,
                 frequency,
                 start,
                 end,
                 start_offset=0,
                 end_offset=0,
                 rows=1,
                 file_path=FILE_PATH,
                 datetime_fmt='%Y-%m-%d'):
        """
        TradeChart init
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
        :param rows: number of sub plots
        :param file_path: HDF5 file path
        :param datetime_fmt
        """
        chart_start = pd.Timestamp(start, unit='s') - pd.Timedelta(start_offset * DataFrequency[frequency].value,
                                                                   unit='s')
        chart_end = pd.Timestamp(end, unit='s') + pd.Timedelta(end_offset * DataFrequency[frequency].value, unit='s')
        self._df = HDFData.read_hdf(instrument, frequency, chart_start, chart_end, file_path)
        self._rows = rows
        self._axes = None
        self._fig = None
        self._datetime_fmt = datetime_fmt

    def draw_candlestick_chart(self):
        if self._rows > 1:
            self._fig, self._axes = plt.subplots(self._rows, 1, sharex=True, figsize=(20, 10 * self._rows))
        elif self._rows == 1:
            self._fig, ax = plt.subplots(self._rows, 1, sharex=True, figsize=(20, 10 * self._rows))
            self._axes = np.array([ax])
        ax = self._axes[0]
        line_width = 0.6
        date_list = [date.strftime(self._datetime_fmt) for date in self._df.index]
        open_list = self._df.open.values
        close_list = self._df.close.values
        high_list = self._df.high.values
        low_list = self._df.low.values
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
        max_n_ticks = 12
        step = len(date_list) // max_n_ticks
        if step < 1:
            step = 1
        ax.set_xticks(range(0, len(date_list), step))
        ax.set_xticklabels(date_list[::step])
        ax.yaxis.set_major_locator(MultipleLocator(0.0005))
        ax.yaxis.set_minor_locator(MultipleLocator(0.0001))
        self._fig.autofmt_xdate()

    def add_annotate(self, row, message, x, y, x_offset=15, y_offset=15):
        self._axes[row].annotate(
            message,
            xy=(x, y),
            xytext=(x_offset, y_offset),
            textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
            color="black"
        )

    def date_time_index(self, date_time):
        """
        find time index for chart
        :param date_time: timestamp
        :return: time index
        """
        dt = pd.Timestamp(date_time, unit='s')
        idx = binary_search_left(self._df.index.asi8, dt.value)
        return idx

    def draw_horizontal_line(self, value, color, label, row=0):
        ax = self._axes[0]
        ax.axhline(y=value, color=color)
        y_min, y_max = ax.get_ylim()
        y = (value - y_min) / (y_max - y_min)
        ax.text(1.0, y, label,
                verticalalignment='center',
                horizontalalignment='left',
                transform=ax.transAxes,
                color=color)


if __name__ == "__main__":
    instrument = "EUR_USD"
    freq = "D"
    start = 1548108060
    end = 1548339840
    start_offset = 0
    end_offset = 0
    chart = TradeChart(instrument, freq, start, end, start_offset, end_offset, 1)
    chart.draw_candlestick_chart()
    trade_time_idx = chart.date_time_index(1548108060)
    chart.add_annotate(0, chart._df.close[trade_time_idx], trade_time_idx, chart._df.close[trade_time_idx])
    chart.draw_horizontal_line(chart._df.close[trade_time_idx], color='purple', label='{} {}'.format(' PP', 1.223))
    plt.show()
