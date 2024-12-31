from dataclasses import dataclass
from typing import Optional
import backtrader as bt
import pandas as pd
import numpy as np

from src.models.types.types import TradingSignal
from src.strategy.strategies.base.base_strategy import BaseStrategy
from src.strategy.strategies.datas.data import (
    EntryPosition,
    MarketData,
    TradingAnalyzeData,
)
from src.strategy.strategies.helpers.custom_indicator import (
    CustomIndicator,
    TechnicalIndicator,
)

"""
RSI Strategy 조건
"""


@dataclass
class TradingParameters:
    rsi_period: int = 14  # RSI 계산 기간
    rsi_overbought: int = 70  # 과매수 기준값
    rsi_oversold: int = 30  # 과매도 기준값


class TradingStrategy:
    def __init__(self, params: TradingParameters, indicator: TechnicalIndicator):
        self.params = params
        self.indicator = indicator
        self.prev_rsi = None

    def analyze(
        self,
        market_data: MarketData,
        check_index: int = -1,
    ) -> TradingAnalyzeData:
        """
        RSI 기반 매매 전략
        - 매수 조건: RSI가 과매도(30) 구간에서 반등할 때
        - 매도 조건: RSI가 과매수(70) 구간에서 하락할 때
        """
        # RSI 계산
        rsi = self.indicator.calculate_rsi(market_data.close, self.params.rsi_period)
        current_rsi = rsi[check_index]

        # RSI 이전값 초기화
        if self.prev_rsi is None:
            self.prev_rsi = current_rsi
            return TradingAnalyzeData(
                signal=TradingSignal.HOLD,
                reason=f"현재 RSI: {current_rsi:.2f}",
            )

        # 매수 신호: RSI가 과매도 구간에서 상승반전
        if (
            self.prev_rsi <= self.params.rsi_oversold
            and current_rsi > self.params.rsi_oversold
        ):
            reason = f"매수 신호: RSI 과매도({self.params.rsi_oversold}) 구간 반등 (이전 RSI: {self.prev_rsi:.2f}, 현재 RSI: {current_rsi:.2f})"
            self.prev_rsi = current_rsi
            return TradingAnalyzeData(
                signal=TradingSignal.BUY,
                reason=reason,
            )

        # 매도 신호: RSI가 과매수 구간에서 하락반전
        if (
            self.prev_rsi >= self.params.rsi_overbought
            and current_rsi < self.params.rsi_overbought
        ):
            reason = f"매도 신호: RSI 과매수({self.params.rsi_overbought}) 구간 하락 (이전 RSI: {self.prev_rsi:.2f}, 현재 RSI: {current_rsi:.2f})"
            self.prev_rsi = current_rsi
            return TradingAnalyzeData(
                signal=TradingSignal.SELL,
                reason=reason,
            )

        # RSI 값 업데이트
        self.prev_rsi = current_rsi

        return TradingAnalyzeData(
            signal=TradingSignal.HOLD,
            reason=f"현재 RSI: {current_rsi:.2f}",
        )


# Backtrader에서 사용하는 전략 클래스
class BackTestingRSIStrategy(bt.Strategy):
    def __init__(self):
        self.trading_strategy = TradingStrategy(TradingParameters(), CustomIndicator())
        self.data_close = self.data.close
        self.data_high = self.data.high
        self.data_low = self.data.low
        self.order = None  # order 상태 추적을 위해 추가

    def next(self):
        if len(self.data) < 50:
            return

        market_data = MarketData(
            close=np.array(self.data_close.get(size=50)),
            high=np.array(self.data_high.get(size=50)),
            low=np.array(self.data_low.get(size=50)),
        )

        trading_analyze_data = self.trading_strategy.analyze(
            market_data,
        )

        if trading_analyze_data is None:
            return

        signal = trading_analyze_data.signal
        reason = trading_analyze_data.reason

        # 포지션이 없고 매수 신호가 발생하면 매수
        if not self.position and signal == TradingSignal.BUY:
            self.order = self.buy(
                exectype=bt.Order.Market,
            )
            self.log(reason)

        # 포지션이 있고 매도 신호가 발생하면 매도
        if self.position and signal == TradingSignal.SELL:
            self.order = self.sell(
                exectype=bt.Order.Market,
            )
            self.log(reason)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # 아직 처리 중인 주문

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"매수 체결: 가격 {order.executed.price:.2f}, 수량 {order.executed.size}"
                )
            else:
                self.log(
                    f"매도 체결: 가격 {order.executed.price:.2f}, 수량 {order.executed.size}"
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("주문 실패")

        self.order = None  # 주문 상태 초기화

    # def notify_trade(self, trade):
    #     print("---------------------------- TRADE ---------------------------------")
    #     print(f"Date: {self.data.datetime.date(0)}")
    #     print(f"Type: {'sell' if trade.long else 'buy'}")
    #     print(f"Price: {trade.price}")
    #     print(f"Size: {trade.size}")
    #     print(f"PnL: {trade.pnl}")

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"[{dt.isoformat()}] {txt}")


# 실시간 전략 클래스
class RealTimeRSIStrategy(BaseStrategy):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.trading_strategy = TradingStrategy(TradingParameters(), CustomIndicator())

    def analyze_market(
        self,
        entry_position: Optional[EntryPosition] = None,
    ) -> TradingAnalyzeData | None:
        super().analyze_market(entry_position)

        # 전략 분석
        trading_analyze_data = self.trading_strategy.analyze(
            market_data=self.market_data,
        )

        # 손절/익절 체크
        if self.entry_position:
            print("손절/익절 체크 구현 필요!")
            pass

        return trading_analyze_data
