from src.services.exchange_service import ExchangeService
from src.services.trade_service import TradeService

# 서비스 인스턴스 생성
exchange_service = ExchangeService()
trader_service = TradeService()


def get_exchange_service():
    return exchange_service


def get_trade_service():
    return trader_service
