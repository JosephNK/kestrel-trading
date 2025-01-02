import inspect
from typing import Optional
import pandas as pd
import yfinance as yf
import backtrader as bt

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

    def run_testing_yf(
        self,
        ticker: str = "AAPL",
        strategy_type: StrategyType = StrategyType.RSI,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
    ) -> BaseResponse[BackTestingDto]:
        try:
            start_date_time = (
                datetime.strptime(start_date, "%Y-%m-%d")
                if start_date and start_date.strip()
                else None
            )
            end_date_time = (
                datetime.strptime(end_date, "%Y-%m-%d")
                if end_date and end_date.strip()
                else None
            )
            diff_day = (
                (end_date_time - start_date_time)
                if end_date_time and start_date_time
                else None
            )

            if diff_day is not None:
                days = diff_day.days

                # interval별 제한일 설정
                interval_limits = {
                    "1m": (7, "1분봉 (최근 7일 제한)"),
                    "2m": (60, "2분봉, 5분봉, 15분봉, 30분봉, 90분봉 (최근 60일 제한)"),
                    "5m": (60, "2분봉, 5분봉, 15분봉, 30분봉, 90분봉 (최근 60일 제한)"),
                    "15m": (
                        60,
                        "2분봉, 5분봉, 15분봉, 30분봉, 90분봉 (최근 60일 제한)",
                    ),
                    "30m": (
                        60,
                        "2분봉, 5분봉, 15분봉, 30분봉, 90분봉 (최근 60일 제한)",
                    ),
                    "90m": (
                        60,
                        "2분봉, 5분봉, 15분봉, 30분봉, 90분봉 (최근 60일 제한)",
                    ),
                    "60m": (730, "60분봉, 1시간봉 (최근 730일 제한)"),
                    "1h": (730, "60분봉, 1시간봉 (최근 730일 제한)"),
                }

                if interval in interval_limits:
                    limit_days, error_message = interval_limits[interval]
                    if days > limit_days:
                        raise HttpJsonException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            error_message=error_message,
                        )

            # yfinance로 데이터 가져오기
            yf_df = yf.Ticker(ticker).history(
                interval=interval,
                start=start_date_time if diff_day is not None else None,
                end=end_date_time if diff_day is not None else None,
            )

            backtesting = Backtesting()

            item: BackTestingDto = backtesting.run_strategy(
                ticker=ticker,
                df=yf_df,
                strategy_type=strategy_type,
            )

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

    def __get_yahoo_data(
        self,
        ticker: str = "AAPL",
        start: datetime = datetime(2023, 1, 1),
        end: datetime = datetime(2023, 12, 31),
    ) -> pd.DataFrame:
        # yfinance로 데이터 가져오기
        yf_df = yf.Ticker(ticker).history(
            start=start,
            end=end,
        )
        return yf_df
