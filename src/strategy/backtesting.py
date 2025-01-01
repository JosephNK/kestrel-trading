import pandas as pd
import backtrader as bt
import yfinance as yf

from datetime import datetime

from src.models.backtesting_dto import BackTestingDto
from src.models.types.types import StrategyType
from src.strategy.analyzer.analyzer import BackTestingAnalyzer
from src.strategy.strategies.helpers.custom_pandas_data import CustomPandasData
from src.strategy.strategies.helpers.custom_percent_sizer import CustomPercentSizer
from src.strategy.strategies.profitable_strategy import BackTestingProfitableStrategy
from src.strategy.strategies.qulla_maggie_strategy import BackTestingQullaMaggieStrategy
from src.strategy.strategies.rsi_strategy import BackTestingRSIStrategy


class BaseBacktesting:
    cerebro: bt.Cerebro

    def __init__(self):
        self.cerebro = bt.Cerebro()

    def init_setup(
        self,
        df: pd.DataFrame = None,
        initial_cash: int = 100000000,
        commission: float = 0.0005,
    ):
        # 데이터 준비 및 전략 실행
        # df_ready.index = pd.to_datetime(df_ready.index).tz_localize(None)
        df.index = pd.to_datetime(df.index)

        # 데이터 피드 추가
        data = CustomPandasData(dataname=df)
        self.cerebro.adddata(data)

        # 초기 설정
        initial_cash = initial_cash
        initial_commission = commission
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=initial_commission)

    def run_testing_analyzer(
        self,
        ticker: str = "KRW-BTC",
        df: pd.DataFrame = None,
    ) -> BackTestingDto:
        # 백테스팅 결과
        backtesting_analyzer = BackTestingAnalyzer(
            cerebro=self.cerebro,
            df=df,
        )
        return backtesting_analyzer.run(ticker=ticker)


class Backtesting(BaseBacktesting):
    def run_strategy(
        self,
        ticker: str = "KRW-BTC",
        df: pd.DataFrame = None,
        strategy_type: StrategyType = StrategyType.RSI,
        initial_cash: int = 100000000,
        commission: float = 0.0005,
    ) -> BackTestingDto:
        try:
            # 초기 설정
            self.init_setup(
                df=df,
                initial_cash=initial_cash,
                commission=commission,
            )

            # 전략 추가
            if strategy_type == StrategyType.RSI:
                self.cerebro.addstrategy(BackTestingRSIStrategy)

            if strategy_type == StrategyType.PROFITABLE:
                self.cerebro.addstrategy(BackTestingProfitableStrategy)

            if strategy_type == StrategyType.QULLAMAGGIE:
                self.cerebro.addstrategy(BackTestingQullaMaggieStrategy)

            # Percent Sizer
            self.cerebro.addsizer(
                CustomPercentSizer,
                buy_percent=90,
                sell_percent=100,
            )

            # 실행
            return self.run_testing_analyzer(ticker=ticker, df=df)

        except Exception as e:
            raise ValueError(f"Backtesting failed {e}")
