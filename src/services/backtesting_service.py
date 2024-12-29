import inspect


from datetime import datetime
from fastapi import status


from src.exchanges.strategy.strategies.datas.types import StrategyType
from src.exchanges.strategy.backtesting import Backtesting
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.models.backtesting_dto import BackTestingDto
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.utils.logging import Logging


class BacktestingService:
    exchange: UpbitExchange

    def __init__(self):
        Logging.info("Creating an instance of BacktestingService!")
        self.exchange = UpbitExchange()

    def run_testing(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.PROFITABLE,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> BaseResponse[BackTestingDto]:
        try:
            self.exchange.ticker = ticker

            candle_df = self.exchange.get_candle(
                count=candle_count, interval=candle_interval
            )

            backtesting = Backtesting()

            if strategy_type == StrategyType.PROFITABLE:
                backtesting.run_profitable_strategy(candle_df)

            return BaseResponse[BackTestingDto](
                status_code=status.HTTP_200_OK,
                item=BackTestingDto(
                    ticker=ticker,
                    exchange_provider=self.exchange.get_provider(),
                    created_at=datetime.now(),
                ),
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
