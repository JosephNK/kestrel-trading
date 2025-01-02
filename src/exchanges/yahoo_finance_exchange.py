import yfinance as yf
import pandas as pd

from typing import Optional
from datetime import datetime

from src.exchanges.base.base_exchange import BaseExchange
from src.models.exception.http_json_exception import HttpJsonException
from src.models.trading_dto import TradingDto
from src.models.types.types import ExchangeProvider
from src.utils.indicator import Indicator
from src.utils.logging import Logging


class YahooFinanceExchange(BaseExchange):
    def __init__(self):
        self.ticker = "AAPL"

    def get_provider(self) -> str:
        return ExchangeProvider.YAHOOFINANCE.value

    def get_current_investment_status(self) -> list:
        pass

    def get_orderbook_status(self) -> dict:
        pass

    def get_candle(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: int = 0,
        interval: str = "1d",
    ) -> pd.DataFrame:
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
                    raise ValueError(error_message)

        # yfinance로 데이터 가져오기
        yf_df = yf.Ticker(self.ticker).history(
            interval=interval,
            start=start_date_time if diff_day is not None else None,
            end=end_date_time if diff_day is not None else None,
        )

        return yf_df

    def trading(
        self,
        answer: str,
        buy_percent: float = 100,
        sell_percent: float = 100,
    ) -> TradingDto:
        pass

    def buy_market(
        self,
        decision: str,
        reason: str,
        buy_percent: float = 100,
    ) -> TradingDto:
        pass

    def sell_market(
        self,
        decision: str,
        reason: str,
        sell_percent: float = 100,
    ) -> TradingDto:
        pass

    def hold_market(
        self,
        decision: str,
        reason: str,
    ) -> TradingDto:
        pass
