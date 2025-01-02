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
        regex="^(day|minute1|minute3|minute5|minute10|minute15|minute30|minute60|minute240|week|month)$",
        description="캔들 간격",
    )


class StrategyDateParams(BaseModel):
    ticker: str = Query(
        default="BTC-USD",
        description="거래 티커",
    )
    strategy_type: StrategyType = Query(
        default=StrategyType.RSI,
        description="전략 유형",
    )
    start_date: str = Query(
        default="",
        description="시작일 (2024-01-01)",
    )
    end_date: str = Query(
        default="",
        description="종료일 (2024-12-31)",
    )
    interval: str = Query(
        default="1d",
        regex="^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$",
        description="Interval",
    )
