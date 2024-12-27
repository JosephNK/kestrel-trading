from pydantic import BaseModel, BeforeValidator
from pydantic.alias_generators import to_camel
from datetime import date, datetime, timedelta, timezone


class TradingSignalDto(BaseModel):
    id: int = 0
    ticker: str | None = None
    signal: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.astimezone(tz=timezone.utc),
        }
