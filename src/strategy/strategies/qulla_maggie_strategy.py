from dataclasses import dataclass
from typing import List, Optional, Tuple, Protocol
import backtrader as bt
import pandas as pd
import numpy as np
import talib

from src.models.types.types import TradingSignal
from src.strategy.strategies.base.base_strategy import BaseStrategy
from src.strategy.strategies.datas.data import (
    EntryPosition,
    MarketData,
    RiskPosition,
    TradingAnalyzeData,
    TradingPercent,
)
from src.strategy.strategies.helpers.custom_indicator import (
    CustomIndicator,
    TechnicalIndicator,
)

"""
Qulla maggie Strategy 조건

"""


@dataclass
class TradingParameters:
    # EMA 설정
    ema_fast_period: int = 10
    ema_mid_period: int = 20
    ema_slow_period: int = 50

    # 교차 판단 설정
    cross_threshold: float = 0.1  # EMA 간 교차 판단 임계값 (%)


class TradingRisk:
    def __init__(self, params: TradingParameters, indicator: TechnicalIndicator):
        self.params = params
        self.indicator = indicator

    def check_exit_conditions(
        self,
        market_data: MarketData,
        current_position: Optional[EntryPosition],
        check_index: int = -1,
    ) -> RiskPosition:
        """익절 조건 확인: 가격이 10일선 아래로 진입"""

        if not current_position:
            return RiskPosition(
                selling=False,
                reason="",
                price=0.0,
            )

        current_price = market_data.close[check_index]
        entry_price = current_position.entry_price

        ema_fast = self.indicator.calculate_ema(
            market_data.close, self.params.ema_fast_period
        )[check_index]
        print("current_price", current_price, ema_fast)

        if current_price < ema_fast:
            return RiskPosition(
                selling=True,
                reason=f"익절 매도: 가격 {current_price:.2f}이 10일선({ema_fast:.2f}) 아래로 진입",
                price=0.0,
            )

        return RiskPosition(
            selling=False,
            reason="",
            price=0.0,
        )


class TradingStrategy:
    def __init__(self, params: TradingParameters, indicator: TechnicalIndicator):
        self.params = params
        self.indicator = indicator

    def check_ema_cross(self, ema1: np.ndarray, ema2: np.ndarray, index: int) -> bool:
        """두 EMA가 교차(겹침) 상태인지 확인"""
        diff_percent = abs(
            (ema1[index] - ema2[index]) / ema1[index] * 100
        )  # 두 EMA의 차이를 백분율로 계산
        return diff_percent <= self.params.cross_threshold

    def check_ema_conditions(
        self,
        ema_fast: np.ndarray,
        ema_mid: np.ndarray,
        ema_slow: np.ndarray,
        index: int,
    ) -> Tuple[bool, str]:
        """
        EMA 조건 확인:
        1. 10일선과 20일선이 겹침
        2. 50일선은 겹치지 않음
        """
        # 10일선과 20일선의 교차 여부
        is_fast_mid_cross = self.check_ema_cross(ema_fast, ema_mid, index)

        # 10일선과 50일선, 20일선과 50일선의 교차 여부 확인
        is_fast_slow_cross = self.check_ema_cross(ema_fast, ema_slow, index)
        is_mid_slow_cross = self.check_ema_cross(ema_mid, ema_slow, index)

        # 50일선이 겹치지 않아야 함
        is_slow_separate = not (is_fast_slow_cross or is_mid_slow_cross)

        # 모든 조건 충족 여부
        conditions_met = is_fast_mid_cross and is_slow_separate

        # 상세 이유 메시지 생성
        reason_parts = []
        if is_fast_mid_cross:
            reason_parts.append(
                f"10일선({ema_fast[index]:.2f})과 20일선({ema_mid[index]:.2f})이 겹침"
            )
        else:
            reason_parts.append(
                f"10일선({ema_fast[index]:.2f})과 20일선({ema_mid[index]:.2f})이 겹치지 않음"
            )

        if is_slow_separate:
            reason_parts.append(
                f"50일선({ema_slow[index]:.2f})이 다른 선들과 충분히 분리됨"
            )
        else:
            reason_parts.append(f"50일선({ema_slow[index]:.2f})이 다른 선들과 겹침")

        return conditions_met, " / ".join(reason_parts)

    def analyze(
        self,
        market_data: MarketData,
        check_index: int = -1,
        trading_percent: Optional[TradingPercent] = None,
    ) -> TradingAnalyzeData:
        # EMA 계산
        ema_fast = self.indicator.calculate_ema(
            market_data.close, self.params.ema_fast_period
        )
        ema_mid = self.indicator.calculate_ema(
            market_data.close, self.params.ema_mid_period
        )
        ema_slow = self.indicator.calculate_ema(
            market_data.close, self.params.ema_slow_period
        )

        # EMA 조건 검사
        conditions_met, reason = self.check_ema_conditions(
            ema_fast, ema_mid, ema_slow, check_index
        )

        # 매수 신호 생성
        if conditions_met:
            return TradingAnalyzeData(
                signal=TradingSignal.BUY,
                reason=f"매수 신호 발생: {reason}",
                trading_percent=trading_percent,
            )

        # 매수 조건 불충족
        return TradingAnalyzeData(
            signal=TradingSignal.HOLD,
            reason=reason,
            trading_percent=trading_percent,
        )


# Backtrader에서 사용하는 전략 클래스
class BackTestingQullaMaggieStrategy(bt.Strategy):
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
            trading_percent=None,
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

        # 손절/익절 체크
        if self.position:
            trading_risk = TradingRisk(TradingParameters(), CustomIndicator())
            risk_position = trading_risk.check_exit_conditions(
                current_position=EntryPosition(
                    entry_price=self.position.price,
                ),
                market_data=market_data,
            )
            if risk_position.selling:
                self.order = self.sell(
                    exectype=bt.Order.Market,
                )
                self.log(risk_position.reason)
                return

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
class RealTimeQullaMaggieStrategy(BaseStrategy):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.trading_strategy = TradingStrategy(TradingParameters(), CustomIndicator())

    def analyze_market(
        self,
        current_index: Optional[int] = None,
        trading_percent: Optional[TradingPercent] = None,
        entry_position: Optional[EntryPosition] = None,
    ) -> TradingAnalyzeData | None:
        super().analyze_market(current_index, trading_percent, entry_position)

        trading_analyze_data = self.trading_strategy.analyze(
            self.market_data,
            trading_percent=self.trading_percent,
        )

        # 손절/익절 체크
        if self.entry_position:
            trading_risk = TradingRisk(TradingParameters(), CustomIndicator())
            risk_position = trading_risk.check_exit_conditions(
                current_position=self.entry_position,
                market_data=self.market_data,
            )
            if risk_position.selling:
                self.trading_percent.sell_percent = risk_position.price
                return TradingAnalyzeData(
                    signal=TradingSignal.SELL,
                    reason=risk_position.reason,
                    trading_percent=self.trading_percent,
                )

        return trading_analyze_data
