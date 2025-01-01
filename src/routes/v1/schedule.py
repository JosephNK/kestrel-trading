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
from src.models.params.trade_params import TradeParams
from src.models.response.base_response_dto import BaseResponse
from src.models.schedule_dto import ScheduleDto, ScheduleJobDto
from src.routes.dependencies.services import get_exchange_service, get_trade_service
from src.services.exchange_service import ExchangeService
from src.services.trade_service import TradeService
from src.utils.logging import Logging


class ConbineScheduleParams(TradeParams, CronScheduleParams):
    pass


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
def run_task(
    job_id: str = None,
    job_name: str = None,
    params: ConbineScheduleParams = None,
    db: Session = None,
    trade_service: TradeService = None,
    exchange_service: ExchangeService = None,
):
    Logging.info(
        f"Job executed - ID: {job_id}, Name: {job_name}, Type: Daily Task, Time: {datetime.now()}"
    )
    print("params", params)
    if job_id is None or job_name is None or params is None:
        return


# 작업 함수 저장소
job_functions = {}


def register_job_function(name: str, func):
    """작업 함수를 저장소에 등록"""
    job_functions[name] = func


def init_scheduler():
    """기본 스케줄 작업 초기화"""
    register_job_function("run_task", run_task)

    # scheduler.add_job(
    #     run_task,
    #     trigger=CronTrigger(hour=0, minute=0),
    #     id="run_task",
    #     name="init_run_task",
    #     replace_existing=True,
    #     kwargs={
    #         "job_id": "run_task",
    #         "job_name": "init_run_task",
    #     },
    # )


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


# 스케줄 추가 API (Cron)
@router.post(
    "/schedule/cron",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[ScheduleDto],
)
def add_cron_schedule(params: ConbineScheduleParams):
    try:
        trigger_kwargs = {
            k: v
            for k, v in params.model_dump().items()
            if k
            in [
                "year",
                "month",
                "day",
                "week",
                "day_of_week",
                "hour",
                "minute",
                "second",
            ]
            and v is not None
        }

        scheduler.add_job(
            job_functions["run_task"],
            trigger=CronTrigger(**trigger_kwargs),
            id=params.job_id,
            name=params.job_name,
            replace_existing=True,
            kwargs={
                "job_id": params.job_id,
                "job_name": params.job_name,
                "params": params,
            },
        )

        return BaseResponse[ScheduleDto](
            status_code=status.HTTP_200_OK,
            item=ScheduleDto(
                message=f"Schedule {params.job_id} added successfully",
                executed_at=datetime.now(),
            ),
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# 스케줄 삭제 API
@router.delete(
    "/schedule/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[ScheduleDto],
)
def remove_schedule(job_id: str):
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise HttpJsonException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_message="Schedule not found",
            )

        scheduler.remove_job(job_id)

        return BaseResponse[ScheduleDto](
            status_code=status.HTTP_200_OK,
            item=ScheduleDto(
                message=f"Schedule {job_id} removed successfully",
                executed_at=datetime.now(),
            ),
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# 스케줄 일시정지 API
@router.post(
    "/schedule/{job_id}/pause",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[ScheduleDto],
)
def pause_schedule(job_id: str):
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise HttpJsonException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message="Schedule not found",
            )

        scheduler.pause_job(job_id)

        return BaseResponse[ScheduleDto](
            status_code=status.HTTP_200_OK,
            item=ScheduleDto(
                message=f"Schedule {job_id} paused successfully",
                executed_at=datetime.now(),
            ),
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# 스케줄 재개 API
@router.post(
    "/schedule/{job_id}/resume",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[ScheduleDto],
)
def resume_schedule(job_id: str):
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise HttpJsonException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message="Schedule not found",
            )

        scheduler.resume_job(job_id)

        return BaseResponse[ScheduleDto](
            status_code=status.HTTP_200_OK,
            item=ScheduleDto(
                message=f"Schedule {job_id} resumed successfully",
                executed_at=datetime.now(),
            ),
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# 스케줄 목록 조회 API
@router.get(
    "/scheduled-tasks",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[ScheduleJobDto],
)
def get_scheduled_tasks():
    try:
        jobs: list[str] = []
        for job in scheduler.get_jobs():
            jobs.append(job.id)

        return BaseResponse[ScheduleJobDto](
            status_code=status.HTTP_200_OK,
            item=ScheduleJobDto(
                job_id_list=jobs,
                executed_at=datetime.now(),
            ),
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# 수동 실행 API
@router.post(
    "/trigger-task/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[ScheduleDto],
)
def trigger_task(job_id: str):
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise HttpJsonException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message="Schedule not found",
            )

        job.func()

        return BaseResponse[ScheduleDto](
            status_code=status.HTTP_200_OK,
            item=ScheduleDto(
                message=f"Schedule {job_id} triggered successfully",
                executed_at=datetime.now(),
            ),
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
