from pydantic import BaseModel, BeforeValidator
from pydantic.alias_generators import to_camel
from datetime import date, datetime, timedelta, timezone


# TradingDto: Trading 관련 데이터 전송 객체 (Data Transfer Object)
class TradingDto(BaseModel):
    id: int = 0  # Trading ID
    decision: str | None = None  # 거래 결정 (매수/매도 등)
    confidence: str | None = None  # 신뢰도
    ratio: str | None = None  # 비율
    reason: str | None = None  # 결정 이유
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
