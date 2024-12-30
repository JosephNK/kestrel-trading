from enum import Enum


class ExchangeProvider(str, Enum):
    UPBIT = "Upbit"


class StrategyType(str, Enum):
    PROFITABLE = "Profitable"


class TradingSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
