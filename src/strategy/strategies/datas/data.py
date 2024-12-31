import numpy as np

from dataclasses import dataclass

from src.models.types.types import TradingSignal


@dataclass
class MarketData:
    close: np.ndarray
    high: np.ndarray
    low: np.ndarray


@dataclass
class RiskParams:
    # 손절/익절 파라미터
    stop_loss_pct: float  # 진입가 기준 손절 비율 (%)
    take_profit_pct: float  # 진입가 기준 익절 비율 (%)


@dataclass
class RiskPosition:
    selling: bool
    reason: str
    price: float


@dataclass
class EntryPosition:
    entry_price: float


@dataclass
class TradingPercent:
    buy_percent: float  # 매수시 사용할 퍼센트
    sell_percent: float  # 매도시 사용할 퍼센트

    def __init__(self, buy_percent: float = 10, sell_percent: float = 20):
        self.buy_percent = buy_percent
        self.sell_percent = sell_percent


@dataclass
class TradingAnalyzeData:
    signal: TradingSignal
    reason: str
    trading_percent: TradingPercent  # 매매 비율
