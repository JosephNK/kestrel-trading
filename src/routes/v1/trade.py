from fastapi import Depends, status, APIRouter
from requests import Session

from src.databases.database import get_db
from src.models.exception.http_json_exception import HttpJsonException
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


# Get Strategy Trade API (/api/v1/trade/strategy)
@router.get(
    "/trade/strategy",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingDto],
)
async def trade_strategy(
    trader_service: TradeService = Depends(get_trade_service),
    exchange_service: ExchangeService = Depends(get_exchange_service),
    exchange_provider: ExchangeProvider = ExchangeProvider.UPBIT,
    ticker: str = "KRW-BTC",
    strategy_type: StrategyType = StrategyType.RSI,
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
        exchange_service.provider = exchange_provider
        trading_signal_response = exchange_service.get_trading_signal_with_strategy(
            ticker=ticker,
            strategy_type=strategy_type,
        )

        trading_signal_dto = trading_signal_response.item

        # 매매 실행
        trader_service.provider = exchange_provider
        trading_response = trader_service.run_trade(
            # dto=trading_signal_dto,
            dto=TradingSignalDto(
                ticker=ticker,
                decision="HOLD",
                reason="임시 테스트 중입니다. (실거래를 원하시면 decision 값을 BUY 또는 SELL로 변경해주세요.)",
                connect_live=False,
            ),
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


# Get Trade Agent API (/api/v1/trade/agent)
@router.get(
    "/trade/agent",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingDto],
)
async def trade_agent(
    trader_service: TradeService = Depends(get_trade_service),
    exchange_service: ExchangeService = Depends(get_exchange_service),
    exchange_provider: ExchangeProvider = ExchangeProvider.UPBIT,
    db: Session = Depends(get_db),
    ticker: str = "KRW-BTC",
    strategy_type: StrategyType = StrategyType.RSI,
    buy_percent: float = 30,
    sell_percent: float = 50,
):
    try:
        exchange_service.provider = exchange_provider
        trading_signal_response, answer = (
            exchange_service.get_trading_signal_with_agent(
                ticker=ticker,
                strategy_type=strategy_type,
                candle_count=30,
                candle_interval="day",
            )
        )

        trading_signal_dto = trading_signal_response.item

        total_tokens = answer["total_tokens"]
        prompt_tokens = answer["prompt_tokens"]
        completion_tokens = answer["completion_tokens"]
        total_cost = answer["total_cost"]

        # 매매 실행
        trader_service.provider = exchange_provider
        trading_response = trader_service.run_trade(
            # dto=trading_signal_dto,
            dto=TradingSignalDto(
                ticker=ticker,
                decision="HOLD",
                reason="임시 테스트 중입니다. (실거래를 원하시면 decision 값을 BUY 또는 SELL로 변경해주세요.)",
                connect_live=False,
            ),
            buy_percent=buy_percent,
            sell_percent=sell_percent,
        )

        trading_response.item.total_tokens = total_tokens
        trading_response.item.prompt_tokens = prompt_tokens
        trading_response.item.completion_tokens = completion_tokens
        trading_response.item.total_token_cost = total_cost

        return trading_response
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
