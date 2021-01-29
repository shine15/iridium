from iridium.chart.trade_chart import TradeChart

import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    df = pd.read_csv("/Users/evan/.iridium/report.csv")
    for _, transaction in df.iterrows():
        if transaction.state == 'CLOSED':
            instrument = transaction.instrument
            freq = "D"
            open_time = transaction.open_time_timestamp
            close_time = transaction.close_time_timestamp
            start_offset = 60
            end_offset = 60
            chart = TradeChart(instrument, freq, open_time, close_time, start_offset, end_offset, 1)
            open_price = round(transaction.trade_open_price, chart.pip_num)
            close_price = round(transaction.trade_close_price, chart.pip_num)
            chart.draw_candlestick_chart()
            open_time_idx = chart.date_time_index(open_time)
            chart.add_annotate(open_price, open_time_idx, open_price)
            close_time_idx = chart.date_time_index(close_time)
            chart.add_annotate(close_price, close_time_idx, close_price)
            chart.draw_ma(12, 'purple', ma_type='ema')
            chart.draw_ma(26, 'orange', ma_type='ema')
            chart.add_desc_text('hello')
            plt.show()