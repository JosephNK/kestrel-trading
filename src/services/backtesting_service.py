import inspect

from typing import Optional
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
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> BaseResponse[BackTestingDto]:
        try:
            self.update_exchange()

            self.exchange.ticker = ticker

            candle_df = self.exchange.get_candle(
                start_date=start_date,
                end_date=end_date,
                count=candle_count,
                interval=candle_interval,
            )

            backtesting = Backtesting()

            item: BackTestingDto = backtesting.run_strategy(
                ticker=ticker,
                df=candle_df,
                strategy_type=strategy_type,
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
