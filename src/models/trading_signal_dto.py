from pydantic import BaseModel, BeforeValidator
from pydantic.alias_generators import to_camel
from datetime import date, datetime, timedelta, timezone


# TradingSignalDto: 트레이딩 신호 데이터 전송 객체
class TradingSignalDto(BaseModel):
    id: int = 0  # 신호 ID
    ticker: str | None = None  # 거래 대상 티커 (예: "KRW-BTC")
    signal: str | None = None  # 거래 신호 (BUY/SELL/HOLD)
    reason: str | None = None  # 거래 신호 이유
    created_at: datetime | None = None  # 생성 시간
    updated_at: datetime | None = None  # 수정 시간

    class Config:
        alias_generator = to_camel  # snake_case를 camelCase로 변환
        populate_by_name = True  # 별칭과 원래 이름 모두 허용
        from_attributes = True  # ORM 모델 -> DTO 변환 허용
        json_encoders = {
            datetime: lambda v: v.astimezone(
                tz=timezone.utc
            ),  # datetime을 UTC 시간대로 변환
        }
