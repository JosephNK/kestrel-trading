from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.models.exception.validate_exception_message import ValidateExceptionMessage
from src.routes.v1 import (
    health as health_v1,
    schedule as schedule_v1,
    strategy as strategy_v1,
    trade as trade_v1,
)
from src.models.exception.http_json_exception import HttpJsonException
from src.routes.dependencies.services import (
    get_backtesting_service,
    get_exchange_service,
    get_trade_service,
)
from src.utils.logging import Logging

project_name = "Kestrel"


# 로깅 초기화
Logging.init()

# .env 파일에서 환경변수 로드
load_dotenv()


# 스케줄러 인스턴스 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 스타트업 시 실행될 코드
    schedule_v1.init_scheduler()
    schedule_v1.start_scheduler()
    yield
    # 종료 시 실행될 코드
    schedule_v1.shutdown_scheduler()


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# CORS 미들웨어 설정 - 크로스 오리진 리소스 공유 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청 허용
    allow_credentials=True,  # 자격증명 포함 요청 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: list[ValidateExceptionMessage] = []
    for error in exc.errors():
        if error["type"] == "string_pattern_mismatch":
            loc, input_value, msg = (
                error.get("loc", ["", ""])[1] if len(error.get("loc", [])) > 1 else "",
                error.get("input", ""),
                error.get("msg", ""),
            )
            errors.append(
                ValidateExceptionMessage(
                    field=loc,
                    message=msg,
                )
            )
        else:
            errors.append(
                ValidateExceptionMessage(
                    field="",
                    message=str(error),
                )
            )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "errorMessage": "\n".join(str(error) for error in errors),
        },
    )


# 예외 처리기 설정
@app.exception_handler(HttpJsonException)
async def unicorn_exception_handler(request: Request, exc: HttpJsonException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "errorMessage": exc.error_message,
        },
    )


# 라우터 등록
app.include_router(
    health_v1.router,
    tags=["health_v1"],
)
app.include_router(
    schedule_v1.router,
    prefix="/api/v1",
    tags=["schedule_v1"],
)
app.include_router(
    strategy_v1.router,
    prefix="/api/v1",
    tags=["strategy_v1"],
    dependencies=[
        Depends(get_exchange_service),
        Depends(get_backtesting_service),
    ],
)
app.include_router(
    trade_v1.router,
    prefix="/api/v1",
    tags=["trade_v1"],
    dependencies=[
        Depends(get_exchange_service),
        Depends(get_trade_service),
    ],
)

# LangSmith Enabled
Logging.langSmith(project_name=project_name)
