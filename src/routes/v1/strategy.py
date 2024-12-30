from fastapi import status, APIRouter, Depends
from src.databases.database import get_db
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_signal_dto import TradingSignalDto
from src.models.types.types import ExchangeProvider, StrategyType
from src.routes.dependencies.services import (
    get_backtesting_service,
    get_exchange_service,
)
from src.services.backtesting_service import BacktestingService
from src.services.exchange_service import ExchangeService
from src.utils.logging import Logging

# Router 생성
router = APIRouter()


# Get Strategy API (/api/v1/strategy)
@router.get(
    "/strategy",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingSignalDto],
)
async def strategy(
    exchange_service: ExchangeService = Depends(get_exchange_service),
    exchange_provider: ExchangeProvider = ExchangeProvider.UPBIT,
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
        exchange_service.provider = exchange_provider
        return exchange_service.get_trading_signal_with_strategy(
            ticker=ticker,
            strategy_type=strategy_type,
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# Get Backtesting Strategy API (/api/v1/strategy/backtesting)
@router.get(
    "/strategy/backtesting",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[TradingSignalDto],
)
async def strategy_backtesting(
    backtesting_service: BacktestingService = Depends(get_backtesting_service),
    exchange_provider: ExchangeProvider = ExchangeProvider.UPBIT,
    ticker: str = "KRW-BTC",
    strategy_type: StrategyType = StrategyType.PROFITABLE,
):
    try:
        backtesting_service.provider = exchange_provider
        return backtesting_service.run_testing(
            ticker=ticker,
            strategy_type=strategy_type,
            candle_count=200,
            candle_interval="day",
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
