from fastapi import Query
from pydantic import BaseModel
from typing import Optional, Literal


class CronScheduleParams(BaseModel):
    year: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 년도 (Cron 표현식)",
    )
    month: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 월 (Cron 표현식)",
    )
    day: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 일 (Cron 표현식)",
    )
    week: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 주 (Cron 표현식)",
    )
    day_of_week: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 요일 (Cron 표현식)",
    )
    hour: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 시간 (Cron 표현식)",
    )
    minute: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 분 (Cron 표현식)",
    )
    second: Optional[str] = Query(
        default=None,
        regex="^[0-9*/,-]+$",
        description="실행 초 (Cron 표현식)",
    )
    job_id: str = Query(
        description="작업 고유 식별자",
    )
    job_name: str = Query(
        description="작업 표시 이름",
    )
