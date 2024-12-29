import inspect

from fastapi import status

from src.exchanges.strategy.strategies.profitable_strategy import TradingSignal
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_dto import TradingDto
from src.models.trading_signal_dto import TradingSignalDto
from src.utils.logging import Logging


class TradeService:
    exchange: UpbitExchange

    def __init__(self):
        Logging.info("Creating an instance of TradeService!")
        self.exchange = UpbitExchange()

    def run_trade(
        self,
        dto: TradingSignalDto,
        buy_percent: float = 30,
        sell_percent: float = 50,
    ) -> BaseResponse[TradingDto]:
        try:
            self.exchange.ticker = dto.ticker

            # 거래소 매매 실행
            trading_dto = self.exchange.trading(
                answer={
                    "decision": TradingSignal(dto.decision.upper()).value,
                    "reason": dto.reason,
                },
                buy_percent=buy_percent,
                sell_percent=sell_percent,
            )
            trading_dto.connect_live = dto.connect_live

            return BaseResponse[TradingDto](
                status_code=status.HTTP_200_OK,
                item=trading_dto,
            )
        except HttpJsonException as e:
            raise e
        except Exception as e:
            calling_function = inspect.currentframe().f_code.co_name
            Logging.error(
                msg=f"Exception occurred in [{calling_function}]:",
                error=e,
            )
            raise HttpJsonException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
            )
