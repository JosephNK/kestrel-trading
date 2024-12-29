import pandas as pd
import backtrader as bt

from src.exchanges.strategy.analyzer.analyzer_result import (
    AnalyzerMixin,
    AnalyzerResult,
)
from src.exchanges.strategy.strategies.datas.custom_pandas_data import (
    CustomPandasData,
)
from src.exchanges.strategy.strategies.datas.custom_percent_sizer import (
    CustomPercentSizer,
)
from src.exchanges.strategy.strategies.profitable_strategy import (
    BackTestingProfitableStrategy,
)


class BacktestingStrategy:

    @staticmethod
    def run(df: pd.DataFrame):
        try:
            # 데이터 준비 및 전략 실행
            df.index = pd.to_datetime(df.index)
            analyzer = AnalyzerMixin()

            # Cerebro 엔진 초기화
            cerebro = bt.Cerebro()

            # 데이터 피드 추가
            data = CustomPandasData(dataname=df)
            cerebro.adddata(data)

            # 분석기 추가 - 수정된 부분
            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
            cerebro.addanalyzer(
                bt.analyzers.SharpeRatio, _name="sharpe", riskfreerate=0.03
            )
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

            # 초기 설정
            initial_cash = 100000000
            initial_commission = 0.0005
            cerebro.broker.setcash(initial_cash)
            cerebro.broker.setcommission(commission=initial_commission)

            # Percent Sizer
            cerebro.addsizer(
                CustomPercentSizer,
                buy_percent=30,
                sell_percent=50,
            )

            # 전략 추가
            cerebro.addstrategy(BackTestingProfitableStrategy)
            # cerebro.addstrategy(
            #     DCAStrategy,
            #     investment_amount=initial_cash,
            #     dca_period=30,
            # )

            # 백테스팅 결과
            analyzerResult = AnalyzerResult()
            analyzerResult.cerebro = cerebro
            analyzerResult.df = df
            analyzerResult.analyzer = analyzer
            analyzerResult.initial_cash = initial_cash
            analyzerResult.run()

            # 결과 그래프 출력
            cerebro.plot(style="candle", volume=True)

        except Exception as e:
            print("Exception occurred:", e)
