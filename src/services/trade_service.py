import inspect

from fastapi import status
from requests import Session

from src.databases.trade_history_database import TradeHistoryDatabase
from src.models.exception.http_json_exception import HttpJsonException
from src.models.params.trade_params import TradeParams
from src.models.response.base_response_dto import BaseResponse
from src.models.trading_dto import TradingDto
from src.models.trading_signal_dto import TradingSignalDto
from src.models.types.types import TradingSignal
from src.services.base.base_service import BaseService
from src.services.exchange_service import ExchangeService
from src.utils.logging import Logging


class TradeService(BaseService):
    def __init__(self):
        super().__init__()

    def run_trade_with_strategy(
        self,
        params: TradeParams,
        exchange_service: ExchangeService,
        db: Session,
    ) -> BaseResponse[TradingDto]:
        try:
            self.provider = params.exchange_provider

            exchange_service.provider = params.exchange_provider
            trading_signal_response = exchange_service.get_trading_signal_with_strategy(
                ticker=params.ticker,
                strategy_type=params.strategy_type,
                candle_count=params.candle_count,
                candle_interval=params.candle_interval,
            )

            trading_signal_dto = trading_signal_response.item

            # 매매 실행
            trading_response = self.run_trade(
                # dto=trading_signal_dto,
                dto=TradingSignalDto(
                    ticker=params.ticker,
                    decision="HOLD",
                    reason="임시 테스트 중입니다. (실거래를 원하시면 decision 값을 BUY 또는 SELL로 변경해주세요.)",
                    connect_live=False,
                ),
                buy_percent=params.buy_percent,
                sell_percent=params.sell_percent,
            )

            # 거래 내역 저장
            try:
                if db is not None:
                    TradeHistoryDatabase().create(db, dto=trading_response.item)
            except Exception as e:
                Logging.error(msg="Failed to save trade history", error=e)

            return trading_response
        except:
            raise

    def run_trade_with_agent(
        self,
        params: TradeParams,
        exchange_service: ExchangeService,
        db: Session,
    ) -> BaseResponse[TradingDto]:
        try:
            self.provider = params.exchange_provider

            exchange_service.provider = params.exchange_provider
            trading_signal_response, answer = (
                exchange_service.get_trading_signal_with_agent(
                    ticker=params.ticker,
                    strategy_type=params.strategy_type,
                    candle_count=params.candle_count,
                    candle_interval=params.candle_interval,
                )
            )

            trading_signal_dto = trading_signal_response.item

            total_tokens = answer["total_tokens"]
            prompt_tokens = answer["prompt_tokens"]
            completion_tokens = answer["completion_tokens"]
            total_cost = answer["total_cost"]

            # 매매 실행
            trading_response = self.run_trade(
                # dto=trading_signal_dto,
                dto=TradingSignalDto(
                    ticker=params.ticker,
                    decision="HOLD",
                    reason="임시 테스트 중입니다. (실거래를 원하시면 decision 값을 BUY 또는 SELL로 변경해주세요.)",
                    connect_live=False,
                ),
                buy_percent=params.buy_percent,
                sell_percent=params.sell_percent,
            )

            trading_response.item.total_tokens = total_tokens
            trading_response.item.prompt_tokens = prompt_tokens
            trading_response.item.completion_tokens = completion_tokens
            trading_response.item.total_token_cost = total_cost

            # 거래 내역 저장
            try:
                if db is not None:
                    TradeHistoryDatabase().create(db, dto=trading_response.item)
            except Exception as e:
                Logging.error(msg="Failed to save trade history", error=e)

            return trading_response
        except:
            raise

    def run_trade(
        self,
        dto: TradingSignalDto,
        buy_percent: float = 30,
        sell_percent: float = 50,
    ) -> BaseResponse[TradingDto]:
        try:
            self.update_exchange()

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
