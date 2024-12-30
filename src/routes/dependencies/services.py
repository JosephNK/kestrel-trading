from src.services.backtesting_service import BacktestingService
from src.services.exchange_service import ExchangeService
from src.services.trade_service import TradeService


def get_exchange_service():
    return ExchangeService()


def get_trade_service():
    return TradeService()


def get_backtesting_service():
    return BacktestingService()
