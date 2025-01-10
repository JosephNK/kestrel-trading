from pydantic import BaseModel
from fastapi import Query

from src.models.types.types import ExchangeProvider, StrategyType


class InfoParams(BaseModel):
    exchange_provider: ExchangeProvider = Query(
        default=ExchangeProvider.UPBIT,
        description="거래소 제공자",
    )
