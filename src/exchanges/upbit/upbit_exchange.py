import json
import os
import pyupbit

import pandas as pd
import backtrader as bt

from src.exchanges.strategy.strategies.datas.custom_pandas_data import (
    CustomPandasData,
)
from src.exchanges.strategy.strategies.ma_cross_strategy import MACrossStrategy
from src.models.exception.exchange_exception import ExchangeException
from src.utils.fng import Fng
from src.utils.indicator import Indicator
from src.utils.news import News


class UpbitExchange:
    """
    업비트 거래소와의 상호작용을 담당하는 클래스
    - 시장 데이터 조회
    - 투자 상태 모니터링
    - 주문 실행
    을 처리합니다.
    """

    ticker: str  # 거래 대상 티커 (예: "KRW-BTC")
    fee: float  # 거래 수수료 (0.05%)
    min_trade_amount: int  # 최소 거래 금액 (5000원)
    access_key: str  # 업비트 API 접근 키
    secret_key: str  # 업비트 API 비밀 키
    upbit: pyupbit.Upbit  # 업비트 API 클라이언트 인스턴스

    def __init__(self):
        """
        UpbitExchange 클래스 초기화
        환경 변수에서 API 키를 가져와 업비트 API 클라이언트를 생성합니다.
        """
        self.ticker = "KRW-BTC"  # 기본값으로 비트코인 설정
        self.fee = 0.0005  # 0.05% 수수료
        self.min_trade_amount = 5000  # 최소 거래 금액
        self.access_key = os.environ.get("UPBIT_ACCESS_KEY")
        self.secret_key = os.environ.get("UPBIT_SECRET_KEY")
        self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)

    def prepare_analysis_data(self) -> str:
        """
        투자 분석에 필요한 모든 데이터를 수집하여 JSON 형태의 문자열로 반환하는 함수

        Returns:
            str: JSON 형식의 데이터 문자열
                - investment_status: 현재 투자 상태 정보 (잔고, 수익률 등)
                - day_candle_data: 일간의 일봉 데이터 (OHLCV)
                - hour_candle_data: 시간의 시간봉 데이터 (OHLCV)
                - orderbook_status: 현재 호가 데이터 (매수/매도 주문)
        """
        try:
            ticker_currency = self.ticker.split("-")[1]

            # 각종 데이터 수집
            investment_status = self.get_current_investment_status()
            day_candle_data = self.get_candle(count=30, interval="day").to_json()
            hour_candle_data = self.get_candle(count=24, interval="minute60").to_json()
            orderbook_status = self.get_orderbook_status()
            # fear_greed_index = Fng.get_fear_and_greed_index()
            # news_headlines = News.get_google_news(query=ticker_currency)

            # 데이터 통합 및 JSON 형식으로 변환
            analysis_data = {
                "Current Investment Status": investment_status,
                "Daily OHLCV with indicators": day_candle_data,
                "Hourly OHLCV with indicators": hour_candle_data,
                "Orderbook Status": orderbook_status,
            }

            # if news_headlines is not None:
            #     analysis_data["Recent news headlines"] = news_headlines

            # if fear_greed_index is not None:
            #     analysis_data["Fear and Greed Index"] = fear_greed_index

            return json.dumps(analysis_data, indent=2)

        except Exception as e:
            raise

    def get_current_investment_status(self):
        try:
            # 현재가 조회
            current_price = pyupbit.get_current_price(self.ticker)

            # 전체 계좌 조회
            balances = self.upbit.get_balances()
            filtered_balances = [
                balance
                for balance in balances
                if balance["currency"] in [self.ticker.split("-")[1], "KRW"]
            ]
            result_balances = []
            for balance in filtered_balances:
                coin_ticker = balance["unit_currency"] + "-" + balance["currency"]

                if coin_ticker == "KRW-KRW":
                    current_price = 0
                else:
                    current_price = pyupbit.get_current_price(coin_ticker)

                if float(balance["avg_buy_price"]) != 0:
                    profit_loss_percent = (
                        (current_price - float(balance["avg_buy_price"]))
                        / float(balance["avg_buy_price"])
                        * 100.0
                    )
                else:
                    profit_loss_percent = 0  # 매수 평균가가 0인 경우

                invested_amount = round(
                    float(balance["avg_buy_price"]) * float(balance["balance"])
                )

                result_balances.append(
                    {
                        "currency": balance["currency"],
                        "balance": balance["balance"],
                        "avg_buy_price": balance["avg_buy_price"],
                        "invested_amount": invested_amount,
                        "current_price": current_price,
                        "profit_loss_percent": profit_loss_percent,
                    }
                )

            return result_balances
        except Exception as e:
            raise ExchangeException(f"Exception in Get Current Investment Status : {e}")

    def get_orderbook_status(self):
        """
        현재 시장의 호가창(orderbook) 데이터를 조회하고 분석하는 함수
        매수/매도 호가의 물량과 가격을 단계별로 조회하여 시장 동향을 파악할 수 있음

        Returns:
            dict: 호가 데이터 분석 결과
                - timestamp: 호가 데이터 생성 시간
                - total_ask_size: 총 매도 주문량
                - total_bid_size: 총 매수 주문량
                - ask_bid_ratio: 매도/매수 물량 비율
                - orderbook_units: 호가 단계별 상세 데이터
        """
        try:
            # 업비트 API를 통해 호가 데이터 조회
            orderbook_data = pyupbit.get_orderbook(self.ticker)

            if not orderbook_data:
                return None

            # orderbook 데이터 타입 체크 및 처리
            if isinstance(orderbook_data, list):
                orderbook = orderbook_data[0]  # 리스트인 경우 첫 번째 요소 사용
            elif isinstance(orderbook_data, dict):
                orderbook = orderbook_data  # 딕셔너리인 경우 그대로 사용
            else:
                raise ExchangeException(
                    f"Unexpected orderbook data type: {type(orderbook_data)}"
                )

            # 호가 데이터 분석 결과를 저장할 딕셔너리
            status = {
                # 호가 데이터의 생성 시간 (timestamp)
                "timestamp": orderbook["timestamp"],
                # 매도 호가의 총 물량 (ask: 매도 주문)
                "total_ask_size": orderbook["total_ask_size"],
                # 매수 호가의 총 물량 (bid: 매수 주문)
                "total_bid_size": orderbook["total_bid_size"],
                # 매도/매수 물량 비율
                # 1보다 크면 매도 물량이 많다는 의미 (매도 우세)
                # 1보다 작으면 매수 물량이 많다는 의미 (매수 우세)
                "ask_bid_ratio": (
                    orderbook["total_ask_size"] / orderbook["total_bid_size"]
                    if orderbook["total_bid_size"] > 0
                    else 0
                ),
                # 각 호가 단계별 상세 데이터를 저장할 리스트
                "orderbook_units": [],
                "level": orderbook["level"],
            }

            # 호가 단계별 데이터 분석 (기본적으로 최대 15단계)
            # orderbook_units는 가격이 유리한 순서대로 정렬되어 있음
            for unit in orderbook["orderbook_units"]:
                status["orderbook_units"].append(
                    {
                        # 매도 호가 (매도 주문이 걸려있는 가격)
                        # 예: 50000000 -> 5천만원에 매도 주문
                        "ask_price": unit["ask_price"],
                        # 매수 호가 (매수 주문이 걸려있는 가격)
                        # 예: 49990000 -> 4,999만원에 매수 주문
                        "bid_price": unit["bid_price"],
                        # 해당 매도 호가의 코인 수량
                        # 예: 0.1 -> 해당 가격에 0.1 BTC만큼 매도 주문이 있음
                        "ask_size": unit["ask_size"],
                        # 해당 매수 호가의 코인 수량
                        # 예: 0.15 -> 해당 가격에 0.15 BTC만큼 매수 주문이 있음
                        "bid_size": unit["bid_size"],
                    }
                )

            return status
        except Exception as e:
            raise ExchangeException(f"Exception in Get Orderbook Status : {e}")

    def get_candle(self, count: int = 24, interval: str = "day") -> pd.DataFrame:
        """
        최근 X시간의 시간봉 데이터를 조회합니다.

        Returns:
            str: 시간봉 데이터의 JSON 문자열
                포함 정보:
                - open: 시가
                - high: 고가
                - low: 저가
                - close: 종가
                - volume: 거래량
                - value: 거래금액
        """
        try:
            df: pd.DataFrame = pyupbit.get_ohlcv(
                self.ticker, count=count, interval=interval
            )
            if df is None:
                return ""
            df = Indicator.add_sub_indicators(df)
            return df
        except Exception as e:
            raise ExchangeException(f"Exception in Get Hour Candle : {e}")

    def trading(self, answer: str) -> bool:
        """
        AI 모델의 결정에 따라 실제 매매를 실행합니다.

        Args:
            answer (dict): AI 모델의 매매 결정 정보
                - decision: 'buy', 'sell', 또는 'hold'
                - reason: 매매 결정의 이유

        주의사항:
        - 최소 거래금액은 5000원
        - 매수 시 수수료 0.05% 고려 (0.9995)
        """
        try:
            decision = answer["decision"].lower()
            reason = answer["reason"]
            if decision == "buy":
                # Buy
                print("Buy Reason: ", reason)
                self.buy_market()
            elif decision == "sell":
                # Sell
                print("Sell Reason: ", reason)
                self.sell_market()
            elif decision == "hold":
                # Hold
                print("Hold Reason: ", reason)
                return False
            else:
                return False
        except ExchangeException:
            raise
        except Exception as e:
            raise ExchangeException(f"Exception in trading : {e}")

    def buy_market(self):
        my_krw = self.upbit.get_balance("KRW")
        calc_my_krw_price = my_krw - (my_krw * self.fee)
        print("buy_market", my_krw, calc_my_krw_price)
        if calc_my_krw_price > self.min_trade_amount:
            print("Buy Order Executed")
            # buy_result = self.upbit.buy_market_order(
            #     ticker=self.ticker, price=my_krw_amount
            # )
            # if buy_result is None:
            #     raise ExchangeException("An error with the buy order")
        else:
            print("Buy Order Faild Below 5000 Won")

    def sell_market(self):
        my_coin = self.upbit.get_balance(self.ticker)
        current_coin_price = pyupbit.get_orderbook(ticker=self.ticker)[
            "orderbook_units"
        ][0]["ask_price"]
        calc_coin_price = my_coin * current_coin_price
        print("sell_market", my_coin, current_coin_price, calc_coin_price)
        if calc_coin_price > self.min_trade_amount:
            print("Sell Order Executed")
            # sell_result = self.upbit.sell_market_order(ticker=self.ticker, volume=my_coin)
            # if sell_result is None:
            #     raise ExchangeException("An error with the sell order")
        else:
            print("Sell Order Faild Below 5000 Won")
