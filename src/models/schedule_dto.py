from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from datetime import datetime, timezone


class ScheduleDto(BaseModel):
    id: int | None = None
    message: str | None = None
    executed_at: datetime | None = None

    class Config:
        alias_generator = to_camel  # snake_case를 camelCase로 변환
        populate_by_name = True  # 별칭과 원래 이름 모두 허용
        from_attributes = True  # ORM 모델 -> DTO 변환 허용
        json_encoders = {
            datetime: lambda v: v.astimezone(
                tz=timezone.utc
            ),  # datetime을 UTC 시간대로 변환
        }


class ScheduleJobDto(BaseModel):
    id: int | None = None
    job_id_list: list[str] | None = None
    executed_at: datetime | None = None

    class Config:
        alias_generator = to_camel  # snake_case를 camelCase로 변환
        populate_by_name = True  # 별칭과 원래 이름 모두 허용
        from_attributes = True  # ORM 모델 -> DTO 변환 허용
        json_encoders = {
            datetime: lambda v: v.astimezone(
                tz=timezone.utc
            ),  # datetime을 UTC 시간대로 변환
        }
