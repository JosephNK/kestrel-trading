import re
from fastapi import Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from src.models.exception.http_json_exception import HttpJsonException
from src.models.exception.validate_exception_message import ValidateExceptionMessage
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
    start_date: str = Query(
        default="",
        description="시작일 (2024-01-01)",
    )
    end_date: str = Query(
        default="",
        description="종료일 (2024-12-31)",
    )
    candle_interval: str = Query(
        default="",
        description="캔들 간격",
    )

    @field_validator("candle_interval")
    def validate_interval(cls, v, info):
        if not v or v.strip() == "":
            error_message = ValidateExceptionMessage(
                field="candle_interval",
                message="시간 간격은 필수 값입니다.",
            )
            raise HttpJsonException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_message=str(error_message),
            )

        exchange = info.data.get("exchange_provider")

        pattern = ""
        if exchange == ExchangeProvider.UPBIT:
            pattern = r"^(day|minute1|minute3|minute5|minute10|minute15|minute30|minute60|minute240|week|month)$"
        else:
            pattern = r"^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$"

        if not re.match(pattern, v):
            result = re.search(r"\((.*?)\)", pattern).group(1)
            error_message = ValidateExceptionMessage(
                field="candle_interval",
                message=f"올바르지 않은 시간 간격입니다. ({result})",
            )
            raise HttpJsonException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_message=str(error_message),
            )

        return v
