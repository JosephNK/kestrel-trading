import inspect
import pandas as pd

from datetime import datetime
from fastapi import status
from typing import Tuple

from src.agents.kestrel_agent import KestrelAiAgent
from src.agents.prompts.prompt import KestrelPrompt
from src.exchanges.strategy.strategies.datas.types import StrategyType, TradingSignal
from src.exchanges.strategy.strategies.profitable_strategy import (
    RealTimeProfitableStrategy,
)
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_signal_dto import TradingSignalDto
from src.utils.logging import Logging


class ExchangeService:
    exchange: UpbitExchange

    def __init__(self):
        Logging.info("Creating an instance of ExchangeService!")
        self.exchange = UpbitExchange()

    # Profitable 전략에 따른 Trading Signal 생성
    def get_profitable_strategy_trading_signal(
        self, df: pd.DataFrame
    ) -> Tuple[TradingSignal, str]:
        strategy = RealTimeProfitableStrategy(df=df)
        return strategy.analyze_market()

    # 전략에 따른 Trading Signal 생성
    def get_trading_signal_with_strategy(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.PROFITABLE,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> BaseResponse[TradingSignalDto]:
        try:
            self.exchange.ticker = ticker

            # 데이터 조회
            candle_df = self.exchange.get_candle(
                count=candle_count, interval=candle_interval
            )

            trading_signal: TradingSignal | None = None
            signal_condition: str | None = None

            if strategy_type == StrategyType.PROFITABLE:
                # Profitable 전략
                trading_signal, signal_condition = (
                    self.get_profitable_strategy_trading_signal(df=candle_df)
                )

            if trading_signal is None:
                raise HttpJsonException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=str("Trading Signal Not Found"),
                )

            return BaseResponse[TradingSignalDto](
                status_code=status.HTTP_200_OK,
                item=TradingSignalDto(
                    ticker=ticker,
                    decision=trading_signal.value,
                    reason=signal_condition,
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

    # AI 에이전트를 사용하여 Trading Signal 생성
    def get_trading_signal_with_agent(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.PROFITABLE,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> Tuple[BaseResponse[TradingSignalDto], dict]:
        try:
            self.exchange.ticker = ticker

            # 데이터 조회
            candle_df = self.exchange.get_candle(
                count=candle_count, interval=candle_interval
            )
            investment_status = self.exchange.get_current_investment_status()
            orderbook_status = self.exchange.get_orderbook_status()

            trading_signal: TradingSignal | None = None

            if strategy_type == StrategyType.PROFITABLE:
                # Profitable 전략
                trading_signal, _ = self.get_profitable_strategy_trading_signal(
                    df=candle_df
                )

            if trading_signal is None:
                raise HttpJsonException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=str("Trading Signal Not Found"),
                )

            # 데이터 통합 및 JSON 형식으로 변환
            analysis_data = {
                "Current Investment Status": investment_status,
                "OHLCV With Indicators": candle_df.to_json(),
                "Orderbook Status": orderbook_status,
                "Result By Trading Strategy": trading_signal.value,
            }

            # AI 매매 결정
            ai_agent = KestrelAiAgent()
            answer = ai_agent.invoke(
                analysis_data=analysis_data,
                strategy_type=strategy_type,
            )

            return (
                BaseResponse[TradingSignalDto](
                    status_code=status.HTTP_200_OK,
                    item=TradingSignalDto(
                        ticker=ticker,
                        decision=answer["decision"],
                        reason=answer["reason"],
                        created_at=datetime.now(),
                    ),
                ),
                answer,
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

    def get_candle_df(
        self,
        ticker: str = "KRW-BTC",
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> pd.DataFrame:
        self.exchange.ticker = ticker
        candle_df = self.exchange.get_candle(
            count=candle_count, interval=candle_interval
        )
        return candle_df
