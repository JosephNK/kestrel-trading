import backtrader as bt

from src.strategy.strategies.datas.data import TradingPercent


class CustomPercentSizer(bt.Sizer):
    percent = TradingPercent(
        buy_percent=10,
        sell_percent=20,
    )

    params = (
        ("buy_percent", percent.buy_percent),  # 매수시 사용할 퍼센트
        ("sell_percent", percent.sell_percent),  # 매도시 사용할 퍼센트
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if position:
            # 매도 상황
            if not isbuy:
                size = position.size * (self.params.sell_percent / 100)
            # 이미 포지션 있는 상태에서 추가 매수
            else:
                value = cash * (self.params.buy_percent / 100)
                size = value / data[0]
        # 신규 매수
        else:
            if isbuy:
                value = cash * (self.params.buy_percent / 100)
                size = value / data[0]
            else:
                size = 0

        return size
