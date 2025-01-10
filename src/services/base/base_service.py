from src.exchanges.base.base_exchange import BaseExchange
from src.exchanges.upbit_exchange import UpbitExchange
from src.exchanges.yahoo_finance_exchange import YahooFinanceExchange
from src.models.types.types import ExchangeProvider


class BaseService:
    __provider: ExchangeProvider
    __exchange: BaseExchange

    def __init__(self):
        self.__provider = ExchangeProvider.UPBIT
        self.__exchange = UpbitExchange()

    def update_exchange(self, exchange_provider: ExchangeProvider):
        if exchange_provider is None:
            raise ValueError("ExchangeProvider is a required parameter")

        self.__provider = exchange_provider

        if self.__provider is ExchangeProvider.UPBIT and not isinstance(
            self.__exchange, UpbitExchange
        ):
            self.__exchange = UpbitExchange()
        elif self.__provider is ExchangeProvider.YAHOOFINANCE and not isinstance(
            self.__exchange, YahooFinanceExchange
        ):
            self.__exchange = YahooFinanceExchange()
        else:
            pass

    @property
    def provider(self) -> ExchangeProvider:
        return self.__provider

    @property
    def exchange(self) -> BaseExchange:
        return self.__exchange
