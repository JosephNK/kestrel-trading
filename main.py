from typing import List
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from requests import Session

from src.agents.kestrel_agent import KestrelAiAgent
from src.databases.database import get_db
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.response.health_response_dto import HealthResponseDto
from src.models.trading_dto import TradingDto
from src.models.trading_signal_dto import TradingSignalDto
from src.services.exchange_service import ExchangeService, StrategyType
from src.utils.logging import Logging

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangSmith Enabled
Logging.logging_langSmith(project_name="Kestrel")


""" HttpJsonException
"""


@app.exception_handler(HttpJsonException)
async def unicorn_exception_handler(request: Request, exc: HttpJsonException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "errorMessage": exc.error_message,
        },
    )


### Health API
### This is Health API List

""" [GET] /
    Args:
        None
    Returns:
        HealthResponseDto
"""


@app.get("/", status_code=status.HTTP_200_OK, response_model=HealthResponseDto)
async def health():
    try:
        return HealthResponseDto(status="OK")
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


@app.get(
    "/v1/strategy",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingSignalDto],
)
async def strategy(ticker: str = "KRW-BTC"):
    """시장 데이터 분석 및 매매 신호 생성
    Response:
        {
            ...
            "item": {
                ...
                "ticker": "KRW-BTC",
                "signal": "HOLD",
                ...
            }
            ...
        }
    """

    try:
        service = ExchangeService()

        trading_signal = service.get_trading_signal(
            ticker=ticker, strategy_type=StrategyType.PROFITABLE
        )

        if trading_signal is None:
            raise HttpJsonException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message=str("Trading Signal Not Found"),
            )

        return BaseResponse[TradingSignalDto](
            status_code=status.HTTP_200_OK,
            item=TradingSignalDto(ticker=ticker, signal=trading_signal.value),
        )
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


@app.get(
    "/v1/test",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingDto],
)
async def test(db: Session = Depends(get_db)):
    try:
        exchange = UpbitExchange()
        exchange.ticker = "KRW-BTC"
        ai_agent = KestrelAiAgent()

        # 분석용 데이터 준비
        analysis_data = exchange.prepare_analysis_data()

        print("analysis_data", analysis_data)

        # AI 매매 결정
        answer = ai_agent.invoke(source_data=analysis_data, is_pass=True)

        # 매매 실행
        exchange.trading(answer=answer)

        return BaseResponse[TradingDto](
            status_code=status.HTTP_200_OK,
            item=TradingDto(
                decision=answer["decision"],
                # confidence=answer["confidence"],
                # ratio=answer["ratio"],
                reason=answer["reason"],
            ),
        )
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
