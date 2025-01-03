from fastapi import Depends, status, APIRouter
from requests import Session

from src.databases.database import get_db
from src.databases.trade_history_database import TradeHistoryDatabase
from src.models.exception.http_json_exception import HttpJsonException
from src.models.params.trade_params import TradeParams
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_dto import TradingDto
from src.models.trading_signal_dto import TradingSignalDto
from src.models.types.types import ExchangeProvider, StrategyType
from src.routes.dependencies.services import get_exchange_service, get_trade_service
from src.routes.v1.auth import verify_token
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
    user: dict = Depends(verify_token),
    params: TradeParams = Depends(),
    trader_service: TradeService = Depends(get_trade_service),
    exchange_service: ExchangeService = Depends(get_exchange_service),
    db: Session = Depends(get_db),
):
    try:
        trading_response = trader_service.run_trade_with_strategy(
            params=params,
            exchange_service=exchange_service,
            db=db,
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
    user: dict = Depends(verify_token),
    params: TradeParams = Depends(),
    trader_service: TradeService = Depends(get_trade_service),
    exchange_service: ExchangeService = Depends(get_exchange_service),
    db: Session = Depends(get_db),
):
    try:
        trading_response = trader_service.run_trade_with_agent(
            params=params,
            exchange_service=exchange_service,
            db=db,
        )
        return trading_response
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
