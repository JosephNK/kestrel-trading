from src.exchanges.base.base_exchange import BaseExchange
from src.exchanges.upbit_exchange import UpbitExchange
from src.models.types.types import ExchangeProvider


class BaseService:
    exchange: BaseExchange
    provider: ExchangeProvider

    def __init__(self):
        self.provider = ExchangeProvider.UPBIT
        self.exchange = UpbitExchange()

    def update_exchange(self):
        if self.provider is ExchangeProvider.UPBIT and not isinstance(
            self.exchange, UpbitExchange
        ):
            self.exchange = UpbitExchange()
        else:
            pass
