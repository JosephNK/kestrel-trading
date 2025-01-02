from typing import Optional
import pandas as pd

from abc import ABC, abstractmethod

from src.models.trading_dto import TradingDto


class BaseExchange(ABC):
    ticker: str  # 거래 대상 티커 (예: "KRW-BTC")
    fee: float  # 거래 수수료 (0.05%)
    min_trade_amount: int  # 최소 거래 금액 (5000원)

    def __init__(self):
        pass

    @abstractmethod
    def get_provider(self) -> str:
        pass

    @abstractmethod
    def get_current_investment_status(self) -> list:
        pass

    @abstractmethod
    def get_orderbook_status(self) -> dict:
        pass

    @abstractmethod
    def get_candle(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: int = 24,
        interval: str = "day",
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def trading(
        self,
        answer: str,
        buy_percent: float = 100,
        sell_percent: float = 100,
    ) -> TradingDto:
        pass

    @abstractmethod
    def buy_market(
        self,
        decision: str,
        reason: str,
        buy_percent: float = 100,
    ) -> TradingDto:
        pass

    @abstractmethod
    def sell_market(
        self,
        decision: str,
        reason: str,
        sell_percent: float = 100,
    ) -> TradingDto:
        pass

    @abstractmethod
    def hold_market(
        self,
        decision: str,
        reason: str,
    ) -> TradingDto:
        pass
