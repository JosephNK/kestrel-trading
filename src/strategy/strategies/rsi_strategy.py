import backtrader as bt
import math


class RSIStrategy(bt.Strategy):
    params = (
        ("rsi_period", 14),
        ("rsi_overbought", 70),
        ("rsi_oversold", 30),
        ("min_trade_amount", 0.0001),  # 최소 거래 단위
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.order = None
        self.trades = 0

    def next(self):
        if self.order:
            return

        cash = self.broker.get_cash()
        position_value = self.position.size * self.data.close[0] if self.position else 0
        total_value = cash + position_value

        if not self.position:
            if self.rsi[0] < self.params.rsi_oversold:
                raw_size = total_value * 0.95 / self.data.close[0]
                size = (
                    math.floor(raw_size / self.params.min_trade_amount)
                    * self.params.min_trade_amount
                )
                if size >= self.params.min_trade_amount:
                    self.order = self.buy(size=size)
                    print(f"매수 신호 (RSI: {self.rsi[0]:.2f})")

        else:
            if self.rsi[0] > self.params.rsi_overbought:
                size = (
                    math.floor(self.position.size / self.params.min_trade_amount)
                    * self.params.min_trade_amount
                )
                if size >= self.params.min_trade_amount:
                    self.order = self.sell(size=size)
                    print(f"매도 신호 (RSI: {self.rsi[0]:.2f})")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                print(
                    f"매수 체결: {order.executed.price:,.0f}원, 수량: {order.executed.size:.4f} BTC"
                )
            elif order.issell():
                print(
                    f"매도 체결: {order.executed.price:,.0f}원, 수량: {order.executed.size:.4f} BTC"
                )
            self.trades += 1

        self.order = None
