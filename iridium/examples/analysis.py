from iridium.chart.trade_chart import TradeChart

import pandas as pd
import matplotlib.pyplot as plt


def ma_strategy_analysis():
    df = pd.read_csv("/Users/evan/.iridium/report.csv")
    for _, transaction in df.iterrows():
        if transaction.state == 'CLOSED':
            instrument = transaction.instrument
            freq = "D"
            open_time = transaction.open_time_timestamp
            close_time = transaction.close_time_timestamp
            start_offset = 90
            end_offset = 90
            rows = 2
            height_ratios = [8, 2]
            chart = TradeChart(instrument, freq, open_time, close_time, start_offset, end_offset, rows, height_ratios)
            open_price = round(transaction.trade_open_price, chart.pip_num)
            close_price = round(transaction.trade_close_price, chart.pip_num)
            chart.draw_candlestick_chart()
            open_time_idx = chart.date_time_index(open_time)
            chart.add_annotate(open_price, open_time_idx, open_price)
            close_time_idx = chart.date_time_index(close_time)
            chart.add_annotate(close_price, close_time_idx, close_price)
            chart.draw_ma(12, 'purple', ma_type='ema')
            chart.draw_ma(26, 'orange', ma_type='ema')
            chart.draw_rsi(14, 'blue', row=1)
            chart.add_desc_text(transaction.to_string())
            plt.show()


def pivot_point_analysis():
    instrument = 'EUR_USD'
    freq = "D"
    start = 1606773600
    end = 1606773600
    start_offset = 30
    end_offset = 30
    chart = TradeChart(instrument, freq, start, end, start_offset, end_offset, datetime_fmt='%Y-%m-%d %H:%M')
    chart.draw_pivot_points()
    # chart.draw_pivot_point(start)
    plt.show()


def stochastic_analysis():
    instrument = 'EUR_USD'
    freq = "D"
    start = 1606773600
    end = 1606773600
    start_offset = 120
    end_offset = 120
    height_ratios = [8, 2]
    chart = TradeChart(instrument, freq, start, end, start_offset, end_offset,
                       datetime_fmt='%Y-%m-%d', rows=2, height_ratios=height_ratios)
    chart.draw_candlestick_chart()
    # chart.draw_stochastic(row=1)
    # chart.draw_parabolic_sar(acceleration=0.02, maximum=2.0)
    chart.draw_adx(row=1)
    plt.show()


if __name__ == "__main__":
    # ma_strategy_analysis()
    # pivot_point_analysis()
    stochastic_analysis()
