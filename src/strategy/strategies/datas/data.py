import numpy as np

from dataclasses import dataclass

from src.models.types.types import TradingSignal


@dataclass
class MarketData:
    close: np.ndarray
    high: np.ndarray
    low: np.ndarray


@dataclass
class RiskPosition:
    selling: bool
    reason: str
    price: float


@dataclass
class EntryPosition:
    entry_price: float


@dataclass
class TradingAnalyzeData:
    signal: TradingSignal
    reason: str
