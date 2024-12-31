from fastapi import Query
from pydantic import BaseModel

from src.models.types.types import ExchangeProvider, StrategyType


class StrategyParams(BaseModel):
    exchange_provider: ExchangeProvider = Query(
        default=ExchangeProvider.UPBIT,
        description="거래소 제공자",
    )
    ticker: str = Query(
        default="KRW-BTC",
        description="거래 티커",
    )
    strategy_type: StrategyType = Query(
        default=StrategyType.RSI,
        description="전략 유형",
    )
    candle_interval: str = Query(
        default="day",
        regex="^(day|minute|week|month)$",
        description="캔들 간격",
    )
