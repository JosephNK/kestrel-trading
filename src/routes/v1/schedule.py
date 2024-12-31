import pytz

from functools import wraps
from fastapi import status, APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Callable
from requests import Session

from src.databases.database import get_scheduler_db
from src.databases.trade_history_database import TradeHistoryDatabase
from src.models.exception.http_json_exception import HttpJsonException
from src.models.params.cron_schedule_params import CronScheduleParams
from src.models.params.interval_schedule_params import IntervalScheduleParams
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_dto import TradingDto
from src.models.trading_signal_dto import TradingSignalDto
from src.models.types.types import ExchangeProvider, StrategyType
from src.routes.dependencies.services import get_exchange_service, get_trade_service
from src.services.exchange_service import ExchangeService
from src.services.trade_service import TradeService
from src.utils.logging import Logging

# Router 생성
router = APIRouter()

# 스케줄러 인스턴스 생성
scheduler = BackgroundScheduler(timezone=pytz.UTC)


def log_job_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        Logging.info(
            f"Job Starting - ID: {kwargs.get('job_id')}, Name: {kwargs.get('job_name')}"
        )

        try:
            result = func(*args, **kwargs)
            execution_time = datetime.now() - start_time
            Logging.info(
                f"Job completed - ID: {kwargs.get('job_id')}, Execution time: {execution_time}"
            )
            return result
        except Exception as e:
            Logging.error(msg=f"Job failed - ID: {kwargs.get('job_id')}", error=e)
            raise

    return wrapper


def inject_dependencies(func: Callable):
    """스케줄 작업을 위한 의존성 주입 데코레이터"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_scheduler_db() as db:
            trade_service = get_trade_service()
            exchange_service = get_exchange_service()

            return func(
                *args,
                db=db,
                trade_service=trade_service,
                exchange_service=exchange_service,
                **kwargs,
            )

    return wrapper


@log_job_execution
@inject_dependencies
def periodic_task(
    job_id: str = None,
    job_name: str = None,
    db: Session = None,
    trade_service: TradeService = None,
    exchange_service: ExchangeService = None,
):
    Logging.info(
        f"Job executed - ID: {job_id}, Name: {job_name}, Type: Periodic Task, Time: {datetime.now()}"
    )
    if job_id is None or job_name is None:
        return


@log_job_execution
@inject_dependencies
def daily_task(
    job_id: str = None,
    job_name: str = None,
    db: Session = None,
    trade_service: TradeService = None,
    exchange_service: ExchangeService = None,
):
    Logging.info(
        f"Job executed - ID: {job_id}, Name: {job_name}, Type: Daily Task, Time: {datetime.now()}"
    )
    if job_id is None or job_name is None:
        return


# 작업 함수 저장소
job_functions = {}


def register_job_function(name: str, func):
    """작업 함수를 저장소에 등록"""
    job_functions[name] = func


def init_scheduler():
    """기본 스케줄 작업 초기화"""
    register_job_function("periodic_task", periodic_task)
    register_job_function("daily_task", daily_task)

    scheduler.add_job(
        periodic_task,
        trigger=IntervalTrigger(minutes=1),
        id="periodic_task",
        name="1 minute periodic task",
        replace_existing=True,
        kwargs={
            "job_id": None,
            "job_name": None,
        },
    )

    scheduler.add_job(
        daily_task,
        trigger=CronTrigger(hour=0, minute=0),
        id="daily_task",
        name="Daily midnight task",
        replace_existing=True,
        kwargs={
            "job_id": None,
            "job_name": None,
        },
    )


def start_scheduler():
    """스케줄러 시작"""
    Logging.info("Starting scheduler")
    if not scheduler.running:
        scheduler.start()


def shutdown_scheduler():
    """스케줄러 종료"""
    Logging.info("Shutting down scheduler")
    if scheduler.running:
        scheduler.shutdown()


# 스케줄 추가 API (Interval)
@router.post("/schedule/interval")
def add_interval_schedule(params: IntervalScheduleParams):
    if params.func_name not in job_functions:
        raise HttpJsonException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown function name",
        )

    trigger_kwargs = {}
    if params.interval_seconds:
        trigger_kwargs["seconds"] = params.interval_seconds
    if params.interval_minutes:
        trigger_kwargs["minutes"] = params.interval_minutes
    if params.interval_hours:
        trigger_kwargs["hours"] = params.interval_hours

    if not trigger_kwargs:
        raise HttpJsonException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one interval parameter is required",
        )

    try:
        scheduler.add_job(
            job_functions[params.func_name],
            trigger=IntervalTrigger(**trigger_kwargs),
            id=params.job_id,
            name=params.job_name,
            replace_existing=True,
            kwargs={
                "job_id": params.job_id,
                "job_name": params.job_name,
            },
        )
        return {"message": "Schedule added successfully"}
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# 스케줄 추가 API (Cron)
@router.post("/schedule/cron")
def add_cron_schedule(params: CronScheduleParams):
    if params.func_name not in job_functions:
        raise HttpJsonException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown function name",
        )

    trigger_kwargs = {
        k: v
        for k, v in params.model_dump().items()
        if k not in ["job_type", "func_name", "job_id", "job_name"] and v is not None
    }

    try:
        scheduler.add_job(
            job_functions[params.func_name],
            trigger=CronTrigger(**trigger_kwargs),
            id=params.job_id,
            name=params.job_name,
            replace_existing=True,
            kwargs={
                "job_id": params.job_id,
                "job_name": params.job_name,
            },
        )
        return {"message": "Schedule added successfully"}
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# 스케줄 삭제 API
@router.delete("/schedule/{job_id}")
def remove_schedule(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HttpJsonException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule not found",
        )

    scheduler.remove_job(job_id)
    return {"message": f"Schedule {job_id} removed successfully"}


# 스케줄 일시정지 API
@router.post("/schedule/{job_id}/pause")
def pause_schedule(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HttpJsonException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    scheduler.pause_job(job_id)
    return {"message": f"Schedule {job_id} paused successfully"}


# 스케줄 재개 API
@router.post("/schedule/{job_id}/resume")
def resume_schedule(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HttpJsonException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    scheduler.resume_job(job_id)
    return {"message": f"Schedule {job_id} resumed successfully"}


# 스케줄 목록 조회 API
@router.get("/scheduled-tasks")
def get_scheduled_tasks():
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time),
                "trigger": str(job.trigger),
                "func_name": job.func.__name__,
            }
        )
    return {"scheduled_tasks": jobs}


# 수동 실행 API
@router.post("/trigger-task/{task_id}")
def trigger_task(task_id: str):
    job = scheduler.get_job(task_id)
    if job:
        job.func()
        return {"message": f"Task {task_id} triggered successfully"}
    return {"error": "Task not found"}
