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


# Get Health API
@app.get("/", status_code=status.HTTP_200_OK, response_model=HealthResponseDto)
async def health():
    """서버 상태 확인
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
async def strategy(ticker: str = "KRW-BTC", strategy_type=StrategyType.PROFITABLE):
    """시장 데이터 분석 및 매매 신호 생성
    Args:
        ticker (str): 티커 (default: "KRW-BTC")
        strategy_type (StrategyType): 전략 타입 (default: StrategyType.PROFITABLE)
    Returns:
        BaseResponse[TradingSignalDto]
    """

    try:
        return exchange_service.get_trading_signal(
            ticker=ticker, strategy_type=strategy_type
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# Get Test API
@app.get(
    "/v1/test",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingDto],
)
async def test(db: Session = Depends(get_db)):
    try:
        # Upbit 거래소 인스턴스 생성 및 티커 설정
        exchange = UpbitExchange()
        exchange.ticker = "KRW-BTC"
        # Kestrel AI 에이전트 인스턴스 생성
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
    except HttpJsonException as e:
        raise e
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
