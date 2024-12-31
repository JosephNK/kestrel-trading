from pydantic import BaseModel
from fastapi import Query

from src.models.types.types import ExchangeProvider, StrategyType


class TradeParams(BaseModel):
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
    candle_count: int = Query(
        default=30,
        ge=1,  # greater than or equal
        le=200,  # less than or equal
        description="캔들 개수",
    )
    candle_interval: str = Query(
        default="day",
        regex="^(day|minute|week|month)$",
        description="캔들 간격",
    )
    buy_percent: float = Query(
        default=30.0,
        ge=0,
        le=100,
        description="매수 퍼센트",
    )
    sell_percent: float = Query(
        default=50.0,
        ge=0,
        le=100,
        description="매도 퍼센트",
    )
