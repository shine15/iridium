from random import random
from sys import platform as sys_pf
from mpl_finance import candlestick2_ohlc
from matplotlib.ticker import AutoLocator, AutoMinorLocator, FormatStrFormatter
from iridium.data.hdf5 import HDFData, FILE_PATH
from iridium.utils.trading_calendar import DataFrequency
from iridium.utils.alg import binary_search_left
from iridium.utils.pivot_point import standard_pivot_pts

import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


class TradeChart:
    def __init__(self,
                 instrument,
                 freq,
                 start,
                 end,
                 start_offset=0,
                 end_offset=0,
                 rows=1,
                 height_ratios=None,
                 file_path=FILE_PATH,
                 datetime_fmt='%Y-%m-%d'):
        """
        TradeChart init
        :param instrument: instrument name, string
        :param freq:
        M* - Minute, H - hour, D - day, W - Week, M - Month
        M1, M2, M4, M5, M10, M15, M30
        H1, H2, H3, H4, H6, H8, H12,
        D, W
        :param start: timestamp
        :param end: timestamp
        :param start_offset: int
        :param end_offset: int
        :param rows: number of sub plots
        :param height_ratios: different row height ratios
        :param file_path: HDF5 file path
        :param datetime_fmt
        """
        chart_start = pd.Timestamp(start, unit='s') - pd.Timedelta(start_offset * DataFrequency[freq].value,
                                                                   unit='s')
        chart_end = pd.Timestamp(end, unit='s') + pd.Timedelta(end_offset * DataFrequency[freq].value, unit='s')
        self._df = HDFData.read_hdf(instrument, freq, chart_start, chart_end, file_path)
        self._rows = rows
        self._height_ratios = height_ratios
        self._axes = None
        self._fig = None
        self._datetime_fmt = datetime_fmt
        self.pip_num = 2 if instrument.split('_')[1] == 'JPY' else 4
        self._freq = DataFrequency[freq]
        self._instrument = instrument
        self._file_path = file_path

    def draw_candlestick_chart(self):
        if self._rows > 1:
            self._fig, self._axes = plt.subplots(self._rows, 1, sharex=True, figsize=(20, 10),
                                                 gridspec_kw={'height_ratios': self._height_ratios})
        elif self._rows == 1:
            self._fig, ax = plt.subplots(self._rows, 1, sharex=True, figsize=(20, 10))
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
        max_n_ticks = 48
        step = len(date_list) // max_n_ticks
        if step < 1:
            step = 1
        ax.set_xticks(range(0, len(date_list), step))
        ax.set_xticklabels(date_list[::step])
        ax.yaxis.set_major_locator(AutoLocator())
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.{}f'.format(self.pip_num)))
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        for _ax in self._axes:
            _ax.tick_params(axis='both', labelsize=6)
        self._fig.autofmt_xdate()
        self._fig.tight_layout()
        plt.subplots_adjust(hspace=0)

    def add_annotate(self, message, x, y, row=0, x_offset=20, y_offset=20):
        self._axes[row].annotate(
            message,
            xy=(x, y),
            xytext=(x_offset, y_offset),
            fontsize=10,
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
        ax = self._axes[row]
        ax.axhline(y=value, color=color)
        y_min, y_max = ax.get_ylim()
        y = (value - y_min) / (y_max - y_min)
        ax.text(1.0, y, label,
                verticalalignment='bottom',
                horizontalalignment='right',
                transform=ax.transAxes,
                fontsize=10,
                color=color)

    def draw_ma(self, period, color, ma_type='sma', row=0):
        """
        draw moving average line
        :param period
        :param color:
        :param ma_type: sma or ema
        :param row:
        :return:
        """
        ax = self._axes[row]
        if ma_type == 'ema':
            ma = talib.EMA(self._df.close.values, period)
        else:
            ma = talib.SMA(self._df.close.values, period)
        ax.plot(ma, label="{} {}".format(ma_type.upper(), period), color=color)
        ax.legend(loc='upper left')

    def draw_rsi(self, period, color, row):
        """
        draw relative strength index
        :param period:
        :param color:
        :param row:
        :return:
        """
        ax = self._axes[row]
        rsi = talib.RSI(self._df.close.values, period)
        ax.plot(rsi, label="RSI", color=color)
        ax.legend(loc='upper left')

    def draw_pivot_point(self, date_time):
        if self._freq != DataFrequency.D:
            raise Exception('To draw pivot point, freq must be set to D')
        date_time_idx = self.date_time_index(date_time)
        day_start__time = self._df.index[date_time_idx]
        day_end_time = day_start__time + pd.tseries.offsets.DateOffset(seconds=DataFrequency.D.value - 1)
        last_day_close = self._df.close.values[date_time_idx - 1]
        last_day_low = self._df.low.values[date_time_idx - 1]
        last_day_high = self._df.high.values[date_time_idx - 1]
        self._df = HDFData.read_hdf(self._instrument, 'M15', day_start__time, day_end_time, self._file_path)
        self.draw_candlestick_chart()
        pivot_pts = standard_pivot_pts(close=last_day_close, high=last_day_high, low=last_day_low)
        self._draw_pivot_pt_line(pivot_pts.s3, 'S3')
        self._draw_pivot_pt_line(pivot_pts.r3, 'R3')
        self._draw_pivot_pt_line(pivot_pts.s2, 'S2')
        self._draw_pivot_pt_line(pivot_pts.r2, 'R2')
        self._draw_pivot_pt_line(pivot_pts.s1, 'S1')
        self._draw_pivot_pt_line(pivot_pts.r1, 'R1')
        self._draw_pivot_pt_line(pivot_pts.pp, 'PP')

    def _draw_pivot_pt_line(self, value, label):
        color = random(), random(), random()
        self.draw_horizontal_line(value, color, '{} {} '.format(label, round(value, self.pip_num)))

    def add_desc_text(self, desc, row=0):
        ax = self._axes[row]
        ax.text(0.8, 0.98, desc,
                fontsize=8,
                transform=ax.transAxes,
                horizontalalignment='left',
                verticalalignment='top')
