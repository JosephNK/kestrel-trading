import inspect

from enum import Enum

from fastapi import status

from src.exchanges.strategy.strategies.profitable_strategy import (
    ProfitableRealTimeStrategy,
    TradingSignal,
)
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_signal_dto import TradingSignalDto
from src.utils.logging import Logging


class StrategyType(str, Enum):
    PROFITABLE = "Profitable"


class ExchangeService:

    def get_trading_signal_with_strategy(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.PROFITABLE,
    ) -> BaseResponse[TradingSignalDto]:
        try:
            # Upbit 거래소 인스턴스 생성
            exchange = UpbitExchange()
            exchange.ticker = ticker

            day_candle_df = exchange.get_candle(count=200, interval="day")

            trading_signal = None

            # Profitable 전략
            if strategy_type == StrategyType.PROFITABLE:
                strategy = ProfitableRealTimeStrategy(df=day_candle_df)
                latest_signal = strategy.analyze_market()
                trading_signal = TradingSignal(latest_signal)

            if trading_signal is None:
                raise HttpJsonException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=str("Trading Signal Not Found"),
                )

            return BaseResponse[TradingSignalDto](
                status_code=status.HTTP_200_OK,
                item=TradingSignalDto(ticker=ticker, signal=trading_signal.value),
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
