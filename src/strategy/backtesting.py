import pandas as pd
import backtrader as bt
import yfinance as yf

from datetime import datetime

from src.models.backtesting_dto import BackTestingDto
from src.strategy.analyzer.analyzer import BackTestingAnalyzer
from src.strategy.strategies.helpers.custom_pandas_data import CustomPandasData
from src.strategy.strategies.helpers.custom_percent_sizer import CustomPercentSizer
from src.strategy.strategies.profitable_strategy import BackTestingProfitableStrategy
from src.strategy.strategies.qulla_maggie_strategy import BackTestingQullaMaggieStrategy
from src.strategy.strategies.rsi_strategy import BackTestingRSIStrategy


class Backtesting:
    cerebro: bt.Cerebro

    def __init__(self):
        self.cerebro = bt.Cerebro()

    def run_rsi_strategy(
        self,
        ticker: str = "KRW-BTC",
        df: pd.DataFrame = None,
        initial_cash: int = 100000000,
        commission: float = 0.0005,
    ) -> BackTestingDto:
        try:
            # 데이터 준비 및 전략 실행
            # df_ready.index = pd.to_datetime(df_ready.index).tz_localize(None)
            df.index = pd.to_datetime(df.index)

            # 데이터 피드 추가
            data = CustomPandasData(dataname=df)
            self.cerebro.adddata(data)

            # 전략 추가
            self.cerebro.addstrategy(BackTestingRSIStrategy)

            # 초기 설정
            initial_cash = initial_cash
            initial_commission = commission
            self.cerebro.broker.setcash(initial_cash)
            self.cerebro.broker.setcommission(commission=initial_commission)

            # Percent Sizer
            self.cerebro.addsizer(
                CustomPercentSizer,
                # buy_percent=30,
                # sell_percent=50,
            )

            # 백테스팅 결과
            backtesting_analyzer = BackTestingAnalyzer(
                cerebro=self.cerebro,
                df=df,
                initial_cash=initial_cash,
            )
            return backtesting_analyzer.run(ticker=ticker)

        except Exception as e:
            raise ValueError(f"Backtesting failed {e}")

    def run_profitable_strategy(
        self,
        ticker: str = "KRW-BTC",
        df: pd.DataFrame = None,
        initial_cash: int = 100000000,
        commission: float = 0.0005,
    ) -> BackTestingDto:
        try:
            # # 데이터 준비 및 전략 실행
            # df_ready.index = pd.to_datetime(df_ready.index).tz_localize(None)
            df.index = pd.to_datetime(df.index)

            # # 데이터 피드 추가
            data = CustomPandasData(dataname=df)

            self.cerebro.adddata(data)

            # 전략 추가
            self.cerebro.addstrategy(BackTestingProfitableStrategy)

            # 초기 설정
            initial_cash = initial_cash
            initial_commission = commission
            self.cerebro.broker.setcash(initial_cash)
            self.cerebro.broker.setcommission(commission=initial_commission)

            # Percent Sizer
            self.cerebro.addsizer(
                CustomPercentSizer,
                # buy_percent=30,
                sell_percent=100,
            )

            # 백테스팅 결과
            backtesting_analyzer = BackTestingAnalyzer(
                cerebro=self.cerebro,
                df=df,
                initial_cash=initial_cash,
            )
            return backtesting_analyzer.run(ticker=ticker)

        except Exception as e:
            raise ValueError(f"Backtesting failed {e}")

    def run_qulla_maggie_strategy(
        self,
        ticker: str = "KRW-BTC",
        df: pd.DataFrame = None,
        initial_cash: int = 100000000,
        commission: float = 0.0005,
    ) -> BackTestingDto:
        try:
            # 데이터 준비 및 전략 실행
            # df_ready.index = pd.to_datetime(df_ready.index).tz_localize(None)
            df.index = pd.to_datetime(df.index)

            # 데이터 피드 추가
            data = CustomPandasData(dataname=df)
            self.cerebro.adddata(data)

            # 전략 추가
            self.cerebro.addstrategy(BackTestingQullaMaggieStrategy)

            # 초기 설정
            initial_cash = initial_cash
            initial_commission = commission
            self.cerebro.broker.setcash(initial_cash)
            self.cerebro.broker.setcommission(commission=initial_commission)

            # Percent Sizer
            self.cerebro.addsizer(
                CustomPercentSizer,
                # buy_percent=30,
                # sell_percent=50,
            )

            # 백테스팅 결과
            backtesting_analyzer = BackTestingAnalyzer(
                cerebro=self.cerebro,
                df=df,
                initial_cash=initial_cash,
            )
            return backtesting_analyzer.run(ticker=ticker)

        except Exception as e:
            raise ValueError(f"Backtesting failed {e}")
