import backtrader as bt


class MACrossStrategy(bt.Strategy):
    params = (
        ("fast_period", 3),
        ("slow_period", 10),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trades = 0

        # 이동평균선
        self.sma_fast = bt.indicators.SMA(
            self.dataclose, period=self.params.fast_period
        )
        self.sma_slow = bt.indicators.SMA(
            self.dataclose, period=self.params.slow_period
        )

    def next(self):
        if self.order:
            return

        # 포지션이 없을 때
        if not self.position:
            # 골든크로스
            if (
                self.sma_fast[-1] < self.sma_slow[-1]
                and self.sma_fast[0] > self.sma_slow[0]
            ):
                available_cash = self.broker.getcash()
                stock_price = self.dataclose[0]

                # 최소 0.0001 BTC 단위로 매수 가능하도록 설정
                size = round(available_cash * 0.95 / stock_price, 4)
                if size > 0.0001:  # 최소 거래 수량 설정
                    print(f"매수 신호! 가격: {stock_price:,.0f}, 수량: {size:.4f}")
                    self.order = self.buy(size=size)

        # 포지션이 있을 때
        else:
            # 데드크로스
            if (
                self.sma_fast[-1] > self.sma_slow[-1]
                and self.sma_fast[0] < self.sma_slow[0]
            ):
                print(f"매도 신호! 현재 보유수량: {self.position.size:.4f}")
                self.order = self.sell(size=self.position.size)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                print(
                    f"매수 체결: 가격: {order.executed.price:,.0f}, 수량: {order.executed.size:.4f}, 비용: {order.executed.value:,.0f}"
                )
            else:
                print(
                    f"매도 체결: 가격: {order.executed.price:,.0f}, 수량: {order.executed.size:.4f}, 수익: {order.executed.pnl:,.0f}"
                )
            self.trades += 1

        self.order = None
