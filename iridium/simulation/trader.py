from iridium.simulation.data import TradingData, NoDataSet
from iridium.simulation.simulation_parameters import SimulationParameters
from iridium.lib.trade import TradeState
from iridium.lib.order import \
    OrderState, OrderPositionFill, TimeInForce, OrderTriggerCondition, \
    MarketOrder, TakeProfitOrder, StopLossOrder, TrailingStopLossOrder
from iridium.lib.validation import expect_types
from iridium.lib.instrument import Instrument
import pandas as pd


class Trader:
    def __init__(self, sim_params, trading_data):
        assert type(sim_params) == SimulationParameters
        assert type(trading_data) == TradingData
        self.trades = []
        self.orders = []
        self.sim_params = sim_params
        self.trading_data = trading_data

    @property
    def open_trades(self):
        return [trade for trade in self.trades if trade.state == TradeState.OPEN]

    @property
    def pending_orders(self):
        return [order for order in self.orders if order.state == OrderState.PENDING]

    def create_market_order(self,
                            instrument,
                            units,
                            market_price,
                            create_time,
                            take_profit=None,
                            stop_loss=None,
                            trailing_stop_loss=None,
                            price_bound=0.00,
                            order_position_fill=OrderPositionFill.REDUCE_FIRST,
                            time_in_force=TimeInForce.GTC):
        market_order = MarketOrder(instrument, units, market_price, create_time, take_profit, stop_loss,
                                   trailing_stop_loss, price_bound, order_position_fill, time_in_force)
        self.orders.append(market_order)

    def create_take_profit_order(self,
                                 trade,
                                 price,
                                 create_time,
                                 time_in_force=TimeInForce.GTC,
                                 gtd_time=None,
                                 trigger=OrderTriggerCondition.DEFAULT):
        take_profit_order = TakeProfitOrder(trade.trade_id, price, create_time, time_in_force, gtd_time, trigger)
        self.orders.append(take_profit_order)
        trade.set_take_profit_order(take_profit_order)

    def create_stop_loss_order(self,
                               trade,
                               price,
                               create_time,
                               time_in_force=TimeInForce.GTC,
                               gtd_time=None,
                               trigger=OrderTriggerCondition.DEFAULT
                               ):
        stop_loss_order = StopLossOrder(trade.trade_id, price, create_time, time_in_force, gtd_time, trigger)
        self.orders.append(stop_loss_order)
        trade.set_stop_loss_order(stop_loss_order)

    def create_trailing_stop_loss_order(self,
                                        trade,
                                        distance,
                                        create_time,
                                        time_in_force=TimeInForce.GTC,
                                        gtd_time=None,
                                        trigger=OrderTriggerCondition.DEFAULT
                                        ):
        stop_loss = trade.price - distance
        trailing_stop_loss_order = TrailingStopLossOrder(trade.trade_id, distance, stop_loss, create_time,
                                                         time_in_force, gtd_time, trigger)
        self.orders.append(trailing_stop_loss_order)
        trade.set_trailing_stop_loss_order(trailing_stop_loss_order)

    def update_stop_loss_order(self, trade, price, time):
        if trade.stop_loss_order is None:
            self.create_stop_loss_order(trade, price, time)
        else:
            trade.adjust_stop_loss(price)

    def update_take_profit_order(self, trade, price, time):
        if trade.take_profit_order is None:
            self.create_take_profit_order(trade, price, time)
        else:
            trade.adjust_take_profit(price)

    def update_trailing_stop_order(self, trade, distance, time):
        """
        :param trade:
        :param distance: trade price - stop loss price
        :param time:
        :return:
        """
        if trade.take_profit_order is None:
            self.create_trailing_stop_loss_order(trade, distance, time)
        else:
            trade.adjust_trailing_distance(distance)

    @expect_types(close_time=pd.Timestamp)
    def close_trade(self, trade, close_time):
        instrument = trade.instrument
        quote = Instrument(instrument).quote
        account_vs_quote_rates = self.trading_data.get_account_vs_currencies_for_simulation(
            account=self.sim_params.account_currency,
            currencies=[quote],
            trade_time=close_time)
        current_instrument_prices = self.trading_data.get_instruments_data(
            instruments=[instrument],
            trade_time=close_time,
            freq='M1')
        if (account_vs_quote_rates[quote] is None) or (current_instrument_prices[trade.instrument] is None):
            raise NoDataSet()
        profit_loss = trade.close_trade(current_account_vs_quote_rate=account_vs_quote_rates[quote],
                                        current_price=current_instrument_prices[instrument]['close'],
                                        close_time=close_time
                                        )
        self.sim_params.balance += profit_loss

    @expect_types(partially_close_time=pd.Timestamp)
    def _partially_close_trade(self, trade, partially_close_time):
        instrument = trade.instrument
        quote = Instrument(instrument).quote
        account_vs_quote_rates = self.trading_data.get_account_vs_currencies_for_simulation(
            account=self.sim_params.account_currency,
            currencies=[quote],
            trade_time=partially_close_time)
        current_instrument_prices = self.trading_data.get_instruments_data(
            instruments=[instrument],
            trade_time=partially_close_time,
            freq='M1')
        if (account_vs_quote_rates[quote] is None) or (current_instrument_prices[trade.instrument] is None):
            raise NoDataSet()
        profit_loss = trade.partially_close_trade(current_account_vs_quote_rate=account_vs_quote_rates[quote],
                                                  current_price=current_instrument_prices[instrument]['close']
                                                  )
        self.sim_params.balance += profit_loss

    @expect_types(trade_time=pd.Timestamp)
    def net_asset_value(self, trade_time):
        instruments = [trade.instrument for trade in self.open_trades]
        quotes = [Instrument(name).quote for name in instruments]
        account_vs_quote_rates = self.trading_data.get_account_vs_currencies_for_simulation(
            account=self.sim_params.account_currency,
            currencies=quotes,
            trade_time=trade_time)
        current_instrument_prices = self.trading_data.get_instruments_data(
            instruments=instruments,
            trade_time=trade_time,
            freq='M1')
        asset_value = self.sim_params.balance
        for trade in self.open_trades:
            quote = Instrument(trade.instrument).quote
            if (account_vs_quote_rates[quote] is None) or (current_instrument_prices[trade.instrument] is None):
                raise NoDataSet()
            unrealized_profit_loss = trade.calculate_unrealized_profit_loss(
                current_account_vs_quote_rate=account_vs_quote_rates[quote],
                current_price=current_instrument_prices[trade.instrument]['close'])
            asset_value += unrealized_profit_loss
        return asset_value

    @expect_types(trade_time=pd.Timestamp)
    def calculate_margin_used(self, trade_time):
        instruments = [trade.instrument for trade in self.open_trades]
        bases = [Instrument(name).base for name in instruments]
        account_vs_base_rates = self.trading_data.get_account_vs_currencies_for_simulation(
            account=self.sim_params.account_currency,
            currencies=bases,
            trade_time=trade_time)
        margin_used = 0.0
        for trade in self.open_trades:
            base = Instrument(trade.instrument).base
            if account_vs_base_rates[base] is None:
                raise NoDataSet()
            margin_used += trade.calculate_margin_used(account_vs_base_rates[base],
                                                       self.sim_params.leverage)
        return margin_used
