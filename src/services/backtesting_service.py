import inspect


from datetime import datetime
from fastapi import status


from src.models.backtesting_dto import BackTestingDto
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.types.types import StrategyType
from src.services.base.base_service import BaseService
from src.strategy.backtesting import Backtesting
from src.utils.logging import Logging


class BacktestingService(BaseService):
    def __init__(self):
        super().__init__()

    def run_testing(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.RSI,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> BaseResponse[BackTestingDto]:
        try:
            self.update_exchange()

            self.exchange.ticker = ticker

            candle_df = self.exchange.get_candle(
                count=candle_count, interval=candle_interval
            )

            backtesting = Backtesting()

            item: BackTestingDto = None

            if strategy_type == StrategyType.RSI:
                item = backtesting.run_rsi_strategy(
                    ticker=ticker,
                    df=candle_df,
                )
                item.exchange_provider = self.exchange.get_provider()

            if strategy_type == StrategyType.PROFITABLE:
                item = backtesting.run_profitable_strategy(
                    ticker=ticker,
                    df=candle_df,
                )
                item.exchange_provider = self.exchange.get_provider()

            if strategy_type == StrategyType.QULLAMAGGIE:
                item = backtesting.run_qulla_maggie_strategy(
                    ticker=ticker,
                    df=candle_df,
                )
                item.exchange_provider = self.exchange.get_provider()

            if item is None:
                raise HttpJsonException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=str("BackTesting Result Not Found"),
                )

            return BaseResponse[BackTestingDto](
                status_code=status.HTTP_200_OK,
                item=item,
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
