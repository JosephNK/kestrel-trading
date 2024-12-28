from enum import Enum


class StrategyType(str, Enum):
    PROFITABLE = "Profitable"


class TradingSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
