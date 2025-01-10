from fastapi import Depends, status, APIRouter
from src.models.exception.http_json_exception import HttpJsonException
from src.models.exchange_dto import ExchangeDto
from src.models.params.info_params import InfoParams
from src.models.response.base_response_dto import BaseListResponse, BaseResponse
from src.models.response.health_response_dto import HealthResponseDto
from src.models.symbol_dto import SymbolDto
from src.routes.dependencies.services import get_exchange_service
from src.services.exchange_service import ExchangeService
from src.utils.logging import Logging

# Router 생성
router = APIRouter()


@router.get(
    "/info/exchanges",
    status_code=status.HTTP_200_OK,
    response_model=BaseListResponse[ExchangeDto],
)
async def exchanges(
    exchange_service: ExchangeService = Depends(get_exchange_service),
):
    try:
        exchange_response = exchange_service.get_exchanges()
        return exchange_response
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


@router.get(
    "/info/symbols",
    status_code=status.HTTP_200_OK,
    response_model=BaseListResponse[SymbolDto],
)
async def symbols(
    params: InfoParams = Depends(),
    exchange_service: ExchangeService = Depends(get_exchange_service),
):
    try:
        exchange_service.provider = params.exchange_provider
        exchange_response = exchange_service.get_symbols(
            params=params,
        )
        return exchange_response
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
