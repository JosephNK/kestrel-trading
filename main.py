from dotenv import load_dotenv

from fastapi import Depends, FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from requests import Session

from src.agents.kestrel_agent import KestrelAiAgent
from src.databases.database import get_db
from src.exchanges.strategy.strategies.datas.types import StrategyType
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.response.health_response_dto import HealthResponseDto
from src.models.trading_dto import TradingDto
from src.models.trading_signal_dto import TradingSignalDto
from src.services.exchange_service import ExchangeService
from src.services.trade_service import TradeService
from src.utils.logging import Logging

# 로깅 초기화
Logging.init()

# .env 파일에서 환경변수 로드
load_dotenv()

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# CORS 미들웨어 설정 - 크로스 오리진 리소스 공유 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청 허용
    allow_credentials=True,  # 자격증명 포함 요청 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# LangSmith Enabled
Logging.langSmith(project_name="Kestrel")


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


# 서비스 인스턴스 생성
exchange_service = ExchangeService()
trader_service = TradeService()


# Get Health API
@app.get("/", status_code=status.HTTP_200_OK, response_model=HealthResponseDto)
async def health():
    """
    서버 상태 확인

    Args:
        None
    Returns:
        HealthResponseDto
    """
    try:
        return HealthResponseDto(status="OK")
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# Get Strategy API
@app.get(
    "/v1/strategy",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingSignalDto],
)
async def strategy(
    ticker: str = "KRW-BTC",
    strategy_type: StrategyType = StrategyType.PROFITABLE,
):
    """
    트레이딩 전략 사용하여 매매 신호 생성

    Args:
        ticker (str): 거래할 암호화폐 티커 (default: "KRW-BTC")
        strategy_type (StrategyType): 트레이딩 전략 유형 (default: PROFITABLE)
    Returns:
        BaseResponse[TradingSignalDto]
    """

    try:
        return exchange_service.get_trading_signal_with_strategy(
            ticker=ticker, strategy_type=strategy_type
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# Get Strategy Trade API
@app.get(
    "/v1/trade/strategy",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingDto],
)
async def trade_strategy(
    ticker: str = "KRW-BTC",
    strategy_type: StrategyType = StrategyType.PROFITABLE,
    buy_percent: float = 30,
    sell_percent: float = 50,
):
    """
    트레이딩 전략 사용하여 매매 실행

    Args:
       ticker (str): 거래할 암호화폐 티커 (default: "KRW-BTC")
       strategy_type (StrategyType): 트레이딩 전략 유형 (default: PROFITABLE)
       buy_percent (float): 매수 비율 % (default: 30%)
       sell_percent (float): 매도 비율 % (default: 50%)

    Returns:
       BaseResponse[TradingDto]
    """

    try:
        trading_signal_response = exchange_service.get_trading_signal_with_strategy(
            ticker=ticker,
            strategy_type=strategy_type,
            interval="day",
        )

        trading_signal_dto = trading_signal_response.item

        trading_response = trader_service.run_trade(
            dto=trading_signal_dto,
            # dto=TradingSignalDto(
            #     ticker=ticker,
            #     signal="BUY",
            # ),
            buy_percent=buy_percent,
            sell_percent=sell_percent,
        )

        return trading_response
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# Get Trade Agent API
@app.get(
    "/v1/trade/agent",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingDto],
)
async def trade_agent(
    db: Session = Depends(get_db),
    ticker: str = "KRW-BTC",
    strategy_type: StrategyType = StrategyType.PROFITABLE,
    buy_percent: float = 30,
    sell_percent: float = 50,
):
    try:
        trading_signal_response, answer = (
            exchange_service.get_trading_signal_with_agent(
                ticker=ticker,
                strategy_type=strategy_type,
                interval="day",
                candle_count=30,
            )
        )

        trading_signal_dto = trading_signal_response.item

        total_tokens = answer["total_tokens"]
        prompt_tokens = answer["prompt_tokens"]
        completion_tokens = answer["completion_tokens"]
        total_cost = answer["total_cost"]

        trading_response = trader_service.run_trade(
            dto=trading_signal_dto,
            buy_percent=buy_percent,
            sell_percent=sell_percent,
        )

        trading_response.item.total_tokens = total_tokens
        trading_response.item.prompt_tokens = prompt_tokens
        trading_response.item.completion_tokens = completion_tokens
        trading_response.item.total_cost = total_cost

        return trading_response
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
