from typing import Optional
from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from datetime import datetime, timezone

from src.models.session_dto import SessionDto


# UserDto: 사용자 정보 DTO
class UserDto(BaseModel):
    id: Optional[str] = ""  # 사용자 ID
    provider: Optional[str] = ""  # 제공자
    email: Optional[str] = ""  # 이메일
    email_verified: bool = False  # 이메일 인증 여부
    session: Optional[SessionDto] = None
    created_at: datetime | None = None  # 생성 시간
    updated_at: datetime | None = None  # 수정 시간
    deleted_at: datetime | None = None  # 삭제 시간

    class Config:
        alias_generator = to_camel  # snake_case를 camelCase로 변환
        populate_by_name = True  # 별칭과 원래 이름 모두 허용
        from_attributes = True  # ORM 모델 -> DTO 변환 허용
        json_encoders = {
            datetime: lambda v: v.astimezone(
                tz=timezone.utc
            ),  # datetime을 UTC 시간대로 변환
        }
