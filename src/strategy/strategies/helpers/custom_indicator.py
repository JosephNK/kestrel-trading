from dataclasses import dataclass
from typing import List, Optional, Tuple, Protocol
import numpy as np
import talib


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

    def calculate_ema(self, close: np.ndarray, period: int) -> np.ndarray: ...


class CustomIndicator(TechnicalIndicator):
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

    def calculate_ema(self, close: np.ndarray, period: int) -> np.ndarray:
        return talib.EMA(close, timeperiod=period)
