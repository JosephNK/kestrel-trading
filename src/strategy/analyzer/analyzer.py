import pandas as pd
import backtrader as bt

from src.strategy.analyzer.helpers.candle_graph_chart import CandleGraphChart


class BackTestingAnalyzer:
    cerebro: bt.Cerebro
    df: pd.DataFrame
    initial_cash: int

    def __init__(self, cerebro: bt.Cerebro, df: pd.DataFrame, initial_cash: int):
        # Initialize
        self.cerebro = cerebro
        self.df = df
        self.initial_cash = initial_cash

        # 분석기 추가
        """
        PyFolio 분석기는 backtrader와 pyfolio 라이브러리를 연동하기 위한 분석기입니다
        전략의 성과 데이터를 pyfolio 형식으로 변환하여 포트폴리오 분석을 가능하게 합니다
        수익률, 포지션, 거래 기록 등 다양한 데이터를 pyfolio에서 사용할 수 있는 형태로 제공합니다
        """
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")

        """
        샤프 비율(Sharpe Ratio)을 계산하는 분석기입니다
        샤프 비율은 투자의 위험 대비 수익률을 측정하는 지표입니다
        무위험 수익률 대비 초과수익률을 변동성으로 나누어 계산합니다
        높을수록 위험 대비 수익이 좋다는 것을 의미합니다
        """
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="SharpeRatio")

        """
        전략의 수익률을 계산하는 분석기입니다
        누적 수익률, 연간 수익률 등 다양한 기간의 수익률 정보를 제공합니다
        전략의 전반적인 성과를 평가하는데 사용됩니다
        """
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name="Returns")

        """
        드로우다운(DrawDown)을 분석하는 분석기입니다
        드로우다운은 최고점(peak) 대비 하락폭을 의미합니다
        최대 드로우다운, 드로우다운 기간, 드로우다운 횟수 등을 계산합니다
        전략의 위험을 평가하는데 중요한 지표입니다
        """
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DrawDown")

        """
        거래 기록을 저장하는 분석기입니다
        모든 매수/매도 거래의 상세 정보를 저장합니다
        거래 시점의 날짜와 시간을 기록합니다
        거래 가격, 수량, 수수료 등의 정보를 포함합니다
        """
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name="Transactions")

    def run(
        self,
        save_filename: str = "backtrader_plot",
    ):
        # 백테스팅 실행
        print("\n=== 백테스팅 결과 ===")

        first_value = self.cerebro.broker.getvalue()
        print("- 초기 포트폴리오 가치: %.2f" % first_value)
        result = self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        print("- 최종 포트폴리오 가치: %.2f" % final_value)

        # For single strategy
        strat = result[0]

        """
        "sharperatio" 키를 통해 최종 계산된 샤프 비율 수치를 추출합니다
        이 값이 높을수록 위험 대비 수익률이 좋다는 것을 의미합니다
        """
        sharpe_ratio = strat.analyzers.SharpeRatio.get_analysis()["sharperatio"]

        """
        "rtot"는 'return total'의 약자로, 전체 투자 기간의 누적 수익률을 의미합니다
        예를 들어, 0.15라면 15%의 총 수익률을 의미합니다
        """
        returns = strat.analyzers.Returns.get_analysis()["rtot"]

        """
        ["max"]["drawdown"]은 전체 기간 중 가장 큰 드로우다운 수치를 의미합니다
        이 값은 백분율로 표시되며, 예를 들어 20.5라면 20.5%의 최대 하락폭을 의미합니다
        투자 위험을 평가하는 중요한 지표입니다
        """
        draw_down = strat.analyzers.DrawDown.get_analysis()["max"]["drawdown"]

        """
        모든 거래 내역을 추출합니다
        'date', 'amount', 'price', 'sid', 'symbol', 'value'
        """
        transactions = strat.analyzers.Transactions.get_analysis()

        # Sharpe Ratio가 None인 경우를 처리하기 위한 조건문 추가
        if sharpe_ratio is None:
            print(f"- Sharpe Ratio: Not Available")
        else:
            print(f"- Sharpe Ratio: {sharpe_ratio:.2f}")

        # Returns를 퍼센트로 변환 (소수점 2자리)
        print(f"- Total Returns: {returns*100:.2f}%")

        # DrawDown 출력 (소수점 2자리)
        print(f"- Maximum Drawdown: {draw_down:.2f}%")

        # ROI 출력
        roi = (final_value - first_value) / first_value * 100
        print(f"- 투자수익률: {roi:.2f}%")

        # 총 거래 횟수
        print(f"- 총 거래 횟수: {len(transactions)}건")

        # 거래 내역 출력
        self.get_transactions(transactions)

        # 결과 그래프 출력
        # self.cerebro.plot(style="candle", volume=True)
        CandleGraphChart.save_fig(
            transactions,
            df=self.df,
            filename=save_filename,
        )

        # # pyfoliozer
        # pyfoliozer = strat.analyzers.getbyname("pyfolio")
        # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
        # returns.to_csv("result/returns.csv")
        # positions.to_csv("result/positions.csv")
        # transactions.to_csv("result/transactions.csv")
        # gross_lev.to_csv("result/gross_lev.csv")

    def get_transactions(self, transactions):
        # # 거래 내역 출력
        # for date, trades in transactions.items():
        #     print("---")
        #     for trade in trades:
        #         print(f"거래일시: {date}")
        #         print(f"  - 주문수량: {trade[0]:,.2f}")  # amount
        #         print(f"  - 체결가격: {trade[1]:,.2f}")  # price
        #         print(f"  - 종목ID: {trade[2]}")  # sid
        #         print(f"  - 종목코드: {trade[3]}")  # symbol
        #         print(f"  - 거래금액: {trade[4]:,.2f}")  # value
        #         print("---")
        pass
