import pandas as pd
import backtrader as bt

from src.exchanges.strategy.analyzer.analyzer import (
    BackTestingAnalyzer,
    TradeAnalyzer,
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


class Backtesting:
    cerebro: bt.Cerebro

    def __init__(self):
        self.cerebro = bt.Cerebro()

    def run_profitable_strategy(
        self,
        df: pd.DataFrame,
        initial_cash: int = 100000000,
        commission: float = 0.0005,
    ):
        try:
            # 데이터 준비 및 전략 실행
            df.index = pd.to_datetime(df.index)

            # 데이터 피드 추가
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
                buy_percent=30,
                sell_percent=50,
            )

            # 거래량 관련 설정 추가
            self.cerebro.broker.set_checksubmit(False)  # 주문 검증 비활성화

            # cerebro.addstrategy(
            #     DCAStrategy,
            #     investment_amount=initial_cash,
            #     dca_period=30,
            # )

            # 백테스팅 결과
            backtesting_analyzer = BackTestingAnalyzer(
                cerebro=self.cerebro,
                df=df,
                initial_cash=initial_cash,
            )
            backtesting_analyzer.run()

            # 결과 그래프 출력
            # self.cerebro.plot(style="candle", volume=True)
            ## figure = cerebro.plot(style="candle", volume=True)[0][0]
            ## figure.savefig("backtest_result.png")

        except Exception as e:
            print("Exception occurred:", e)
