from iridium.simulation.data import TradingData, NoDataSet
from iridium.utils.trading_calendar import ForexCalendar
import pandas as pd
import numpy as np
from loguru import logger
from iridium.lib.forex import check_margin_call, calculate_margin_available, calculate_margin_used
from .trader import Trader
from iridium.lib.order import MarketOrder, StopLossOrder, TakeProfitOrder, TrailingStopLossOrder, OrderState
from iridium.lib.trade import Trade
from iridium.lib.instrument import Instrument
import sys


class TradeSimulation:
    def __init__(self, file, output):
        script = file.read()
        namespace = {}
        file_name = getattr(file, 'name')
        code = compile(script, file_name, 'exec')
        exec(code, namespace)
        if 'handle_data' in namespace and \
                callable(namespace['handle_data']):
            self.handle_data = namespace.get('handle_data', None)
        else:
            assert (), 'handle_data function must be implemented'

        self.output = output
        self.trader = None

    def start_simulate(self, sim_params):
        perfs = []
        with TradingData() as trading_data:
            self.trader = Trader(sim_params, trading_data)
            trading_sessions = ForexCalendar().trading_sessions(sim_params.start,
                                                                sim_params.end,
                                                                sim_params.data_frequency)
            for session in trading_sessions:
                hist_results = trading_data.get_instruments_history(
                    instruments=sim_params.instruments,
                    before_trade_time=session.start,
                    freq=sim_params.data_frequency,
                    numbers=sim_params.hist_data_num
                )
                # check history data number
                break_loop = False
                for instrument, data in hist_results.items():
                    if data.size < sim_params.hist_data_num:
                        break_loop = True
                        break
                if break_loop:
                    continue
                # minutely data
                minutes = pd.date_range(start=session.start,
                                        end=session.end,
                                        freq='T')
                for idx, minute in enumerate(minutes):
                    sim_data = {}
                    results = trading_data.get_instruments_data(
                        instruments=sim_params.instruments,
                        trade_time=minute,
                        freq='M1')
                    for instrument in sim_params.instruments:
                        price = results[instrument]
                        if price is None:
                            # handle no trading data this time
                            row = pd.DataFrame({
                                'open': [np.nan],
                                'close': [np.nan],
                                'high': [np.nan],
                                'low': [np.nan],
                                'volume': [np.nan]
                            }, index=[minute])
                        else:
                            row = pd.DataFrame({
                                'open': [price['open']],
                                'close': [price['close']],
                                'high': [price['high']],
                                'low': [price['low']],
                                'volume': [price['volume']]
                            }, index=[minute])
                        sim_data[instrument] = hist_results[instrument].append(row)
                    self.handle_data(self.trader, sim_data, minute)
                    try:
                        self._process_orders(minute, results, sim_params)
                        self.user_asset_state(minute)
                    except NoDataSet:
                        logger.warning('time: {}, No enough data to calculate NAV'.format(minute))
                    # except Exception as exc:
                    #     logger.exception(exc)
                    if idx == minutes.size - 1:
                        logger.info('calculate metrics')
            dts = pd.DatetimeIndex(
                [p['time'] for p in perfs]
            )
            stats = pd.DataFrame(perfs, index=dts)
            stats.to_pickle(self.output)

    def user_asset_state(self, trade_time):
        nav = self.trader.net_asset_value(trade_time=trade_time)
        margin_used = self.trader.calculate_margin_used(trade_time=trade_time)
        margin_available = calculate_margin_available(nav, margin_used)
        margin_call = check_margin_call(nav, margin_used)
        logger.info('time: {}, NAV: {:.2f}, margin used: {:.2f}, margin available: {:.2f},'
                    ' margin call: {}'.
                    format(trade_time, nav, margin_used, margin_available, margin_call))
        if margin_call:
            sys.exit()
        return margin_available

    def _process_orders(self, time, data, sim_params):
        open_trades = self.trader.open_trades
        for order in self.trader.pending_orders:
            current_price = data[order.instrument]['close']
            if isinstance(order, MarketOrder):
                existing_trades = [trade for trade in open_trades if trade.instrument == order.instrument]
                order_units = order.units
                existing_units = sum([trade.current_units for trade in existing_trades])
                if order_units * existing_units < 0:
                    for trade in open_trades:
                        if abs(order_units) > 0:
                            if abs(order_units) >= abs(trade.current_units):
                                self.trader.close_trade(trade, time)
                                order_units += trade.current_units
                            else:
                                self.trader._partially_close_trade(trade, time)
                                order_units = 0
                if abs(order_units) == 0:
                    order.set_state(OrderState.FILLED)
                    continue
                base = Instrument(order.instrument).base
                account_vs_base_rates = self.trader.trading_data.get_account_vs_currencies_for_simulation(
                    account=sim_params.account_currency,
                    currencies=[base],
                    trade_time=time)
                if account_vs_base_rates[base] is None:
                    raise NoDataSet()
                initial_margin = calculate_margin_used(abs(order.units),
                                                       account_vs_base_rates[base],
                                                       sim_params.leverage)
                if initial_margin > self.user_asset_state(time):
                    order.set_state(OrderState.CANCELLED)
                    continue
                trade = Trade(instrument=order.instrument,
                              price=order.market_price,
                              open_time=time,
                              initial_units=order_units,
                              initial_margin=initial_margin,
                              take_profit_order=None,
                              stop_loss_order=None,
                              trailing_stop_loss_order=None,
                              spread=sim_params.spread,
                              commission=sim_params.commission)
                self.trader.trades.append(trade)
                if order.take_profit is not None:
                    self.trader.create_take_profit_order(trade,
                                                         order.take_profit.price,
                                                         time)

                if order.stop_loss is not None:
                    self.trader.create_stop_loss_order(trade,
                                                       order.stop_loss.price,
                                                       time)

                if order.trailing_stop_loss is not None:
                    self.trader.create_trailing_stop_loss_order(trade,
                                                                order.trailing_stop_loss.distance,
                                                                time)

                order.set_state(OrderState.FILLED)

            elif isinstance(order, StopLossOrder):
                trade = [trade for trade in self.trader.open_trades if trade.trade_id == order.trade_id][0]
                if (trade.current_units < 0 and current_price >= order.price) and \
                        (trade.current_units > 0 and current_price <= order.price):
                    self.trader.close_trade(trade, time)
                    order.set_state(OrderState.TRIGGERED)
            elif isinstance(order, TakeProfitOrder):
                trade = [trade for trade in self.trader.open_trades if trade.trade_id == order.trade_id][0]
                if (trade.current_units < 0 and current_price <= order.price) and \
                        (trade.current_units > 0 and current_price >= order.price):
                    self.trader.close_trade(trade, time)
                    order.set_state(OrderState.TRIGGERED)
            elif isinstance(order, TrailingStopLossOrder):
                trade = [trade for trade in self.trader.open_trades if trade.trade_id == order.trade_id][0]
                stop_loss = order.price
                if (trade.current_units < 0 and current_price >= stop_loss) and \
                        (trade.current_units > 0 and current_price <= stop_loss):
                    self.trader.close_trade(trade, time)
                    order.set_state(OrderState.TRIGGERED)
                if abs(current_price - stop_loss) > abs(order.distance):
                    order.adjust_price(current_price - order.distance)
            else:
                logger.error("No support order type: {}".format(order))
