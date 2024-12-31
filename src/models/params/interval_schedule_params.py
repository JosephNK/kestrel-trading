from fastapi import Query
from pydantic import BaseModel, create_model
from typing import Optional, Literal


class IntervalScheduleParams(BaseModel):
    job_type: Literal["interval"] = Query(
        default="interval",
        description="작업 유형 (간격 기반 스케줄링)",
    )
    func_name: str = Query(
        description="실행할 함수 이름",
    )
    interval_seconds: Optional[int] = Query(
        default=None,
        ge=0,
        description="실행 간격 (초)",
    )
    interval_minutes: Optional[int] = Query(
        default=None,
        ge=0,
        description="실행 간격 (분)",
    )
    interval_hours: Optional[int] = Query(
        default=None,
        ge=0,
        description="실행 간격 (시간)",
    )
    job_id: str = Query(
        description="작업 고유 식별자",
    )
    job_name: str = Query(
        description="작업 표시 이름",
    )
