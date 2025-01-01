import backtrader as bt
import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.models.types.types import TradingSignal
from src.strategy.strategies.base.base_strategy import BaseStrategy
from src.strategy.strategies.datas.data import (
    EntryPosition,
    MarketData,
    RiskPosition,
    TradingAnalyzeData,
)
from src.strategy.strategies.helpers.custom_indicator import (
    CustomIndicator,
    TechnicalIndicator,
)

"""
Profitable Strategy 조건

- 매수 조건
1. 스토캐스틱 20 수치 미만
2. MACD 상향 교차
3. RSI 50 수치 이상

- 매도 조건
1. 스토캐스틱 80 수치 초과
2. MACD 하향 교차
3. RSI 50 수치 미만
"""


@dataclass
class TradingParameters:
    # RSI 설정
    rsi_period: int = 14  # RSI 계산 기간 (일반적으로 14일 사용)
    rsi_threshold: int = 50  # RSI 매매 신호 기준값

    # MACD 설정
    macd_fastperiod: int = 12  # 단기 이동평균 기간 (기본값 12)
    macd_slowperiod: int = 26  # 장기 이동평균 기간 (기본값 26)
    macd_signalperiod: int = 9  # MACD 시그널 라인 기간 (기본값 9)

    # 스토캐스틱 설정
    stoch_fastk: int = 12  # Fast %K 기간
    stoch_slowk: int = 3  # Slow %K 기간
    stoch_slowd: int = 3  # Slow %D 기간
    stoch_oversold: int = 20  # 과매도 기준값
    stoch_overbought: int = 80  # 과매수 기준값

    # 손절/익절 파라미터
    stop_loss_pct: float = 3.0  # 진입가 기준 손절 비율 (%)
    take_profit_pct: float = 5.0  # 진입가 기준 익절 비율 (%)


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
        """현물 매도 조건 체크 (손절/익절)"""

        if not current_position:
            return RiskPosition(
                selling=False,
                reason="",
                price=0.0,
            )

        current_price = market_data.close[check_index]  # 현재가
        entry_price = current_position.entry_price

        # 손절 체크
        if self.params.stop_loss_pct != 0.0:
            stop_loss_price = entry_price * (1 - self.params.stop_loss_pct / 100)
            if current_price <= stop_loss_price:
                return RiskPosition(
                    selling=True,
                    reason=f"손절 매도: 가격 {current_price:.2f}, 진입가 {entry_price:.2f} 대비 {self.params.stop_loss_pct}% 하락",
                    price=stop_loss_price,
                )

        # 익절 체크
        if self.params.take_profit_pct != 0.0:
            take_profit_price = entry_price * (1 + self.params.take_profit_pct / 100)
            if current_price >= take_profit_price:
                return RiskPosition(
                    selling=True,
                    reason=f"익절 매도: 가격 {current_price:.2f}, 진입가 {entry_price:.2f} 대비 {self.params.take_profit_pct}% 상승",
                    price=take_profit_price,
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
        self.macd_prev = None
        self.macdsignal_prev = None

    def analyze(
        self,
        market_data: MarketData,
        check_index: int = -1,
    ) -> TradingAnalyzeData | None:
        # 기술적 지표 계산
        rsi = self.indicator.calculate_rsi(market_data.close, self.params.rsi_period)
        macd, macdsignal, _ = self.indicator.calculate_macd(
            market_data.close,
            self.params.macd_fastperiod,
            self.params.macd_slowperiod,
            self.params.macd_signalperiod,
        )
        slowk, slowd = self.indicator.calculate_stoch(
            market_data.high,
            market_data.low,
            market_data.close,
            self.params.stoch_fastk,
            self.params.stoch_slowk,
            self.params.stoch_slowd,
        )

        # MACD 크로스 확인
        macd_golden_cross = False
        macd_dead_cross = False

        if self.macd_prev is not None and self.macdsignal_prev is not None:
            if (
                self.macd_prev < self.macdsignal_prev
                and macd[check_index] > macdsignal[check_index]
            ):
                macd_golden_cross = True
            if (
                self.macd_prev > self.macdsignal_prev
                and macd[check_index] < macdsignal[check_index]
            ):
                macd_dead_cross = True

        self.macd_prev = macd[check_index]
        self.macdsignal_prev = macdsignal[check_index]

        # 매수/매도 조건 검사
        buy_conditions = [
            (
                slowk[check_index] < self.params.stoch_oversold,
                f"Stoch K: {slowk[check_index]:.2f} < {self.params.stoch_oversold}",
            ),
            (
                slowd[check_index] < self.params.stoch_oversold,
                f"Stoch D: {slowd[check_index]:.2f} < {self.params.stoch_oversold}",
            ),
            (macd_golden_cross, "MACD 골든크로스"),
            (
                rsi[check_index] > self.params.rsi_threshold,
                f"RSI: {rsi[check_index]:.2f} > {self.params.rsi_threshold}",
            ),
        ]

        sell_conditions = [
            (
                slowk[check_index] > self.params.stoch_overbought,
                f"Stoch K: {slowk[check_index]:.2f} > {self.params.stoch_overbought}",
            ),
            (
                slowd[check_index] > self.params.stoch_overbought,
                f"Stoch D: {slowd[check_index]:.2f} > {self.params.stoch_overbought}",
            ),
            (macd_dead_cross, "MACD 데드크로스"),
            (
                rsi[check_index] < self.params.rsi_threshold,
                f"RSI: {rsi[check_index]:.2f} < {self.params.rsi_threshold}",
            ),
        ]

        satisfied_buy_conditions = [
            msg for condition, msg in buy_conditions if condition
        ]
        satisfied_sell_conditions = [
            msg for condition, msg in sell_conditions if condition
        ]

        current_price = market_data.close[check_index]  # 현재가

        if satisfied_buy_conditions and len(satisfied_buy_conditions) >= 3:
            reason = (
                f"매수 신호 발생 (조건 {len(satisfied_buy_conditions)}개 충족, 현재가 {current_price:.2f}): "
                + ", ".join(satisfied_buy_conditions)
            )
            return TradingAnalyzeData(
                signal=TradingSignal.BUY,
                reason=reason,
            )

        if satisfied_sell_conditions and len(satisfied_sell_conditions) >= 3:
            reason = (
                f"매도 신호 발생 (조건 {len(satisfied_sell_conditions)}개 충족, 현재가 {current_price:.2f}): "
                + ", ".join(satisfied_sell_conditions)
            )
            return TradingAnalyzeData(
                signal=TradingSignal.SELL,
                reason=reason,
            )

        return TradingAnalyzeData(
            signal=TradingSignal.HOLD,
            reason=f"Unmet",
        )


# Backtrader에서 사용하는 전략 클래스
class BackTestingProfitableStrategy(bt.Strategy):
    def __init__(self):
        self.trading_strategy = TradingStrategy(TradingParameters(), CustomIndicator())
        self.order = None  # order 상태 추적을 위해 추가
        # print("\n전체 데이터 길이:", self.data0.buflen())
        # self.target_date = datetime(2023, 9, 25).date()  # 찾고자 하는 날짜

    def next(self):
        # # 특정 날짜 데이터 찾기
        # current_date = self.data0.datetime.date()
        # if current_date == self.target_date:
        #     print(f"\n찾은 날짜의 데이터:")
        #     print("Date:", current_date)
        #     print("Open:", self.data0.open[0])
        #     print("High:", self.data0.high[0])
        #     print("Low:", self.data0.low[0])
        #     print("Close:", self.data0.close[0])
        #     print("Volume:", self.data0.volume[0])
        #     print(f"\n")

        if len(self.data) < 50:
            return

        market_data = MarketData(
            open=np.array(self.data0.open.get(size=50)),
            close=np.array(self.data0.close.get(size=50)),
            high=np.array(self.data0.high.get(size=50)),
            low=np.array(self.data0.low.get(size=50)),
        )

        trading_analyze_data = self.trading_strategy.analyze(
            market_data=market_data,
        )

        if trading_analyze_data is None:
            return

        signal = trading_analyze_data.signal
        reason = trading_analyze_data.reason

        # 포지션이 있고 손절/익절 체크
        if self.position.size > 0:
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
            self.log(f"주문 실패: {order.status}")

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
class RealTimeProfitableStrategy(BaseStrategy):
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
            trading_risk = TradingRisk(TradingParameters(), CustomIndicator())
            risk_position = trading_risk.check_exit_conditions(
                current_position=self.entry_position,
                market_data=self.market_data,
            )
            if risk_position.selling:
                return TradingAnalyzeData(
                    signal=TradingSignal.SELL,
                    reason=risk_position.reason,
                )

        return trading_analyze_data
