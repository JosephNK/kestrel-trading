import inspect
import pandas as pd

from datetime import datetime
from fastapi import status
from typing import Tuple

from src.agents.kestrel_agent import KestrelAiAgent
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_signal_dto import TradingSignalDto
from src.models.types.types import StrategyType, TradingSignal
from src.services.base.base_service import BaseService
from src.strategy.strategies.base.base_strategy import BaseStrategy
from src.strategy.strategies.profitable_strategy import (
    RealTimeProfitableStrategy,
    TradingAnalyzeData,
)
from src.strategy.strategies.qulla_maggie_strategy import RealTimeQullaMaggieStrategy
from src.strategy.strategies.rsi_strategy import RealTimeRSIStrategy
from src.utils.indicator import Indicator
from src.utils.logging import Logging


class ExchangeService(BaseService):
    def __init__(self):
        super().__init__()

    # 전략에 따른 Trading Signal 생성
    def __get_strategy_trading_signal(
        self,
        df: pd.DataFrame,
        strategy_type: StrategyType = StrategyType.PROFITABLE,
    ) -> TradingAnalyzeData | None:
        strategy: BaseStrategy = None

        if strategy_type == StrategyType.RSI:
            strategy = RealTimeRSIStrategy(df=df)

        if strategy_type == StrategyType.PROFITABLE:
            strategy = RealTimeProfitableStrategy(df=df)

        if strategy_type == StrategyType.QULLAMAGGIE:
            strategy = RealTimeQullaMaggieStrategy(df=df)

        return strategy.analyze_market()

    # 전략에 따른 Trading Signal 생성
    def get_trading_signal_with_strategy(
        self,
        ticker: str = "KRW-BTC",
        strategy_type: StrategyType = StrategyType.RSI,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> BaseResponse[TradingSignalDto]:
        try:
            self.update_exchange()

            self.exchange.ticker = ticker

            # 데이터 조회
            candle_df = self.exchange.get_candle(
                count=candle_count, interval=candle_interval
            )

            # 전략
            trading_analyze_data = self.__get_strategy_trading_signal(
                df=candle_df,
                strategy_type=strategy_type,
            )
            trading_signal = trading_analyze_data.signal
            reason = trading_analyze_data.reason

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
                    reason=reason,
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
        strategy_type: StrategyType = StrategyType.RSI,
        candle_count: int = 200,
        candle_interval: str = "day",
    ) -> Tuple[BaseResponse[TradingSignalDto], dict]:
        try:
            self.update_exchange()

            self.exchange.ticker = ticker

            # 데이터 조회
            investment_status = self.exchange.get_current_investment_status()
            orderbook_status = self.exchange.get_orderbook_status()
            candle_df = self.exchange.get_candle(
                count=candle_count, interval=candle_interval
            )

            # 전략
            trading_analyze_data = self.__get_strategy_trading_signal(
                df=candle_df,
                strategy_type=strategy_type,
            )
            trading_signal = trading_analyze_data.signal

            if trading_signal is None:
                raise HttpJsonException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=str("Trading Signal Not Found"),
                )

            # 데이터 통합 및 JSON 형식으로 변환
            analysis_data = {
                "Current Investment Status": investment_status,
                "Orderbook Status": orderbook_status,
                "OHLCV With Indicators": candle_df.to_json(),
                "Result By Trading Strategy": trading_signal.value,
            }

            # AI 매매 결정
            ai_agent = KestrelAiAgent()
            answer = ai_agent.invoke(
                analysis_data=analysis_data,
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
