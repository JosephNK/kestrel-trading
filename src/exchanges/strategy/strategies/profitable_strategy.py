from enum import Enum

from dataclasses import dataclass
from typing import List, Tuple, Protocol
import backtrader as bt
import pandas as pd
import numpy as np
import talib


class TradingSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


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


@dataclass
class MarketData:
    close: np.ndarray
    high: np.ndarray
    low: np.ndarray


# 기술적 지표 계산을 위한 프로토콜
class TechnicalIndicator(Protocol):
    def calculate_rsi(self, close: np.ndarray, period: int) -> np.ndarray: ...
    def calculate_macd(
        self, close: np.ndarray, fast_period: int, slow_period: int, signal_period: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def calculate_stoch(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        fastk_period: int,
        slowk_period: int,
        slowd_period: int,
    ) -> Tuple[np.ndarray, np.ndarray]: ...


# TA-Lib 라이브러리를 사용한 기술적 지표 계산
class TALibIndicator(TechnicalIndicator):
    def calculate_rsi(self, close: np.ndarray, period: int) -> np.ndarray:
        return talib.RSI(close, timeperiod=period)

    def calculate_macd(
        self, close: np.ndarray, fast_period: int, slow_period: int, signal_period: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return talib.MACD(
            close,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period,
        )

    def calculate_stoch(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        fastk_period: int,
        slowk_period: int,
        slowd_period: int,
    ) -> Tuple[np.ndarray, np.ndarray]:
        return talib.STOCH(
            high,
            low,
            close,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,
            slowd_period=slowd_period,
            slowd_matype=0,
        )


class TradingStrategy:
    def __init__(self, params: TradingParameters, indicator: TechnicalIndicator):
        self.params = params
        self.indicator = indicator
        self.macd_prev = None
        self.macdsignal_prev = None

    def analyze(self, market_data: MarketData) -> Tuple[List[str], List[str]]:
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
            if self.macd_prev < self.macdsignal_prev and macd[-1] > macdsignal[-1]:
                macd_golden_cross = True
            if self.macd_prev > self.macdsignal_prev and macd[-1] < macdsignal[-1]:
                macd_dead_cross = True

        self.macd_prev = macd[-1]
        self.macdsignal_prev = macdsignal[-1]

        # 매수/매도 조건 검사
        buy_conditions = [
            (
                slowk[-1] < self.params.stoch_oversold,
                f"Stoch K: {slowk[-1]:.2f} < {self.params.stoch_oversold}",
            ),
            (
                slowd[-1] < self.params.stoch_oversold,
                f"Stoch D: {slowd[-1]:.2f} < {self.params.stoch_oversold}",
            ),
            (macd_golden_cross, "MACD 골든크로스"),
            (
                rsi[-1] > self.params.rsi_threshold,
                f"RSI: {rsi[-1]:.2f} > {self.params.rsi_threshold}",
            ),
        ]

        sell_conditions = [
            (
                slowk[-1] > self.params.stoch_overbought,
                f"Stoch K: {slowk[-1]:.2f} > {self.params.stoch_overbought}",
            ),
            (
                slowd[-1] > self.params.stoch_overbought,
                f"Stoch D: {slowd[-1]:.2f} > {self.params.stoch_overbought}",
            ),
            (macd_dead_cross, "MACD 데드크로스"),
            (
                rsi[-1] < self.params.rsi_threshold,
                f"RSI: {rsi[-1]:.2f} < {self.params.rsi_threshold}",
            ),
        ]

        satisfied_buy_conditions = [
            msg for condition, msg in buy_conditions if condition
        ]
        satisfied_sell_conditions = [
            msg for condition, msg in sell_conditions if condition
        ]

        return satisfied_buy_conditions, satisfied_sell_conditions


# Backtrader에서 사용하는 전략 클래스
class ProfitableStrategy(bt.Strategy):
    def __init__(self):
        self.trading_strategy = TradingStrategy(TradingParameters(), TALibIndicator())
        self.data_close = self.data.close
        self.data_high = self.data.high
        self.data_low = self.data.low

    def next(self):
        if len(self.data) < 50:
            return

        market_data = MarketData(
            close=np.array(self.data_close.get(size=50)),
            high=np.array(self.data_high.get(size=50)),
            low=np.array(self.data_low.get(size=50)),
        )

        buy_signals, sell_signals = self.trading_strategy.analyze(market_data)

        if not self.position and len(buy_signals) >= 3:
            self.buy()
            self.log(
                f"매수 신호 발생 (조건 {len(buy_signals)}개 충족): "
                + ", ".join(buy_signals)
            )
        elif self.position and len(sell_signals) >= 3:
            self.sell()
            self.log(
                f"매도 신호 발생 (조건 {len(sell_signals)}개 충족): "
                + ", ".join(sell_signals)
            )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"[{dt.isoformat()}] {txt}")


# 실시간 전략 클래스
class ProfitableRealTimeStrategy:
    def __init__(self, df: pd.DataFrame):
        if not all(col in df.columns for col in ["close", "high", "low"]):
            raise ValueError(
                "DataFrame must contain 'close', 'high', and 'low' columns"
            )

        self.df = df
        self.trading_strategy = TradingStrategy(TradingParameters(), TALibIndicator())
        self.window_size = 50  # 분석에 사용할 데이터 윈도우 크기

    def analyze_market(self, current_index: int = None) -> TradingSignal:
        """
        시장 데이터 분석 및 매매 신호 생성

        Args:
            current_index: 현재 분석할 시점의 인덱스
        """
        if current_index is None:
            current_index = len(self.df) - 1

        # 최근 50개 데이터만 슬라이싱
        start_idx = max(0, current_index - self.window_size + 1)
        end_idx = current_index + 1

        market_data = MarketData(
            close=self.df["close"].values[start_idx:end_idx],
            high=self.df["high"].values[start_idx:end_idx],
            low=self.df["low"].values[start_idx:end_idx],
        )

        buy_signals, sell_signals = self.trading_strategy.analyze(market_data)

        if len(buy_signals) >= 3:
            print(
                f"매수 신호 발생 (조건 {len(buy_signals)}개 충족): "
                + ", ".join(buy_signals)
            )
            return TradingSignal.BUY
        elif len(sell_signals) >= 3:
            print(
                f"매도 신호 발생 (조건 {len(sell_signals)}개 충족): "
                + ", ".join(sell_signals)
            )
            return TradingSignal.SELL

        return TradingSignal.HOLD
