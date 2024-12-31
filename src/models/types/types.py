from enum import Enum


class ExchangeProvider(str, Enum):
    UPBIT = "Upbit"


class StrategyType(str, Enum):
    RSI = "RSI"
    PROFITABLE = "Profitable"
    QULLAMAGGIE = "QullaMaggie"


class TradingSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
