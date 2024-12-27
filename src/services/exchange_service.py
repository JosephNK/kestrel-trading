from enum import Enum

from src.exchanges.strategy.strategies.profitable_strategy import (
    ProfitableFixedStrategy,
)
from src.exchanges.upbit.upbit_exchange import UpbitExchange


class StrategyType(str, Enum):
    PROFITABLE = "Profitable"


class TradingSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ExchangeService:
    def get_trading_signal(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.PROFITABLE,
    ) -> TradingSignal | None:
        try:
            exchange = UpbitExchange()
            exchange.ticker = ticker
            day_candle_df = exchange.get_candle(count=200, interval="day")
            if strategy_type == StrategyType.PROFITABLE:
                strategy = ProfitableFixedStrategy(df=day_candle_df)
                latest_signal = strategy.analyze_market()
                return TradingSignal(latest_signal)
            return None
        except Exception as e:
            print("Exception occurred:", e)
            raise
