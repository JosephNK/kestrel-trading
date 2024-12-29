import pandas as pd
import numpy as np
import backtrader as bt
from typing import Tuple, Dict


class TradeAnalyzer(bt.Analyzer):
    def __init__(self):
        self.trades = []

    def notify_trade(self, trade):
        if trade.isopen:  # 포지션 진입할 때
            self.trades.append(
                {
                    "datetime": self.data.datetime.date(0),
                    "type": (
                        "buy" if trade.long else "sell"
                    ),  # long이면 매수, short이면 매도
                    "price": trade.price,
                    "size": trade.size,
                }
            )
        elif trade.isclosed:  # 포지션 청산할 때
            self.trades.append(
                {
                    "datetime": self.data.datetime.date(0),
                    "type": (
                        "sell" if trade.long else "buy"
                    ),  # long 포지션 청산은 매도, short 포지션 청산은 매수
                    "price": trade.price,
                    "size": trade.size,
                    "pnl": trade.pnl,
                    "pnlcomm": trade.pnlcomm,
                }
            )

    def get_analysis(self):
        return {"trades": self.trades}


class CalculateAnalyzer:
    def calculate_annual_roi(
        self, final_value: float, initial_cash: float, days: int
    ) -> float:
        """연간 수익률 계산"""
        total_roi = (final_value - initial_cash) / initial_cash
        years = days / 365
        annual_roi = (1 + total_roi) ** (1 / years) - 1
        return annual_roi * 100

    def calculate_max_drawdown(self, value_history: list) -> Tuple[float, int, int]:
        """최대 낙폭(MDD) 계산"""
        if not value_history or len(value_history) < 2:
            return 0.0, 0, 0

        try:
            value_series = pd.Series(value_history)
            rolling_max = value_series.expanding().max()
            drawdowns = (value_series - rolling_max) / rolling_max

            if len(drawdowns) == 0:
                return 0.0, 0, 0

            max_drawdown = drawdowns.min()

            # 최대 낙폭 기간 찾기
            end_idx = drawdowns.idxmin()
            peak_idx = rolling_max.loc[:end_idx].idxmax()

            return abs(max_drawdown) * 100, peak_idx, end_idx
        except Exception as e:
            print(f"MDD 계산 중 오류 발생: {str(e)}")
            return 0.0, 0, 0

    def calculate_sharpe_ratio(
        self, returns: pd.Series, risk_free_rate: float = 0.03
    ) -> float:
        """샤프 비율 계산"""
        excess_returns = returns - risk_free_rate / 252  # 일간 무위험수익률로 변환
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def calculate_win_rate(self, trades: list) -> Dict[str, float]:
        """승률 및 수익비율 계산"""
        if not trades:
            return {"win_rate": 0, "profit_factor": 0}

        wins = sum(1 for trade in trades if trade.pnl > 0)
        total_profit = sum(trade.pnl for trade in trades if trade.pnl > 0)
        total_loss = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))

        win_rate = (wins / len(trades)) * 100
        profit_factor = total_profit / total_loss if total_loss != 0 else float("inf")

        return {"win_rate": win_rate, "profit_factor": profit_factor}


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
        # self.cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        # self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        # self.cerebro.addanalyzer(
        #     bt.analyzers.SharpeRatio, _name="sharpe", riskfreerate=0.03
        # )
        # self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(TradeAnalyzer, _name="trade_list")

    def run(self):
        self.analyzer = CalculateAnalyzer()

        results = self.cerebro.run()
        strat = results[0]

        # 백테스팅 실행
        print("\n=== 백테스팅 결과 ===")

        print(f"초기 포트폴리오 가치: {self.initial_cash:,.0f}원")
        final_value = self.cerebro.broker.getvalue()
        print(f"최종 포트폴리오 가치: {final_value:,.0f}원")

        trades = strat.analyzers.trade_list.get_analysis()["trades"]
        print(f"총 거래 횟수: {trades}건")

        # # 1. 기본 수익률
        # roi = (final_value - self.initial_cash) / self.initial_cash * 100
        # print(f"\n1. 투자수익률: {roi:.2f}%")

        # # 2. 연간수익률
        # trading_days = len(self.df)
        # annual_roi = self.analyzer.calculate_annual_roi(
        #     final_value, self.initial_cash, trading_days
        # )
        # print(f"2. 연간수익률: {annual_roi:.2f}%")

        # # 3. 최대낙폭 (MDD) 계산
        # drawdown = strategy.analyzers.drawdown.get_analysis()
        # max_dd = drawdown.get("max", {})

        # if max_dd:
        #     max_drawdown = max_dd.get("drawdown", 0)

        #     # 포트폴리오 가치 기록 가져오기
        #     values = strategy.observers.value.get(size=trading_days)

        #     if values and len(values) > 0:
        #         value_series = pd.Series(values, index=self.df.index[-len(values) :])

        #         # 롤링 최대값 계산
        #         rolling_max = value_series.expanding().max()
        #         drawdowns = (value_series - rolling_max) / rolling_max * 100

        #         # 최대 낙폭 시점 찾기
        #         mdd_idx = drawdowns.idxmin()
        #         peak_idx = rolling_max.loc[:mdd_idx].idxmax()

        #         print(f"3. 최대낙폭(MDD): {max_drawdown:.2f}%")
        #         print(f"   - MDD 시작일: {peak_idx.strftime('%Y-%m-%d')}")
        #         print(f"   - MDD 종료일: {mdd_idx.strftime('%Y-%m-%d')}")
        #         print(f"   - MDD 지속기간: {(mdd_idx - peak_idx).days}일")
        #     else:
        #         print(f"3. 최대낙폭(MDD): {max_drawdown:.2f}%")
        #         print("   - MDD 기간: 상세 정보 없음")
        # else:
        #     print("3. 최대낙폭(MDD): 계산 불가")

        # # 4. 샤프 비율
        # try:
        #     sharpe_analysis = strategy.analyzers.sharpe.get_analysis()
        #     sharpe_ratio = sharpe_analysis.get("sharperatio", None)
        #     if sharpe_ratio is not None:
        #         print(f"4. 샤프 비율: {sharpe_ratio:.2f}%")
        #     else:
        #         print("4. 샤프 비율: 계산 불가 (충분한 데이터가 없음)")
        # except Exception as e:
        #     print("4. 샤프 비율: 계산 불가", str(e))

        # # 5. 승률 및 수익비율
        # try:
        #     # 전체 거래 수
        #     trade_analysis = strategy.analyzers.trades.get_analysis()
        #     total_trades = trade_analysis.get("total", {}).get("total", 0)

        #     if total_trades > 0:
        #         # 포트폴리오 가치 변화로 수익 계산
        #         total_profit = final_value - self.initial_cash

        #         if total_profit > 0:
        #             win_rate = 100.0  # 수익이 발생했으므로 100% 승률
        #             profit_factor = (
        #                 total_profit / self.initial_cash
        #             )  # 수익비율을 투자원금 대비 수익으로 계산

        #             print(
        #                 f"5. 승률: {win_rate:.2f}% (성공: {total_trades}건 / 전체: {total_trades}건)"
        #             )
        #             print(
        #                 f"6. 수익비율: {profit_factor:.2f}% (총수익: {total_profit:,.0f}원)"
        #             )
        #         else:
        #             print(f"5. 승률: 0.00% (성공: 0건 / 전체: {total_trades}건)")
        #             print(f"6. 수익비율: 0.00 (총손실: {abs(total_profit):,.0f}원)")
        #     else:
        #         print("5. 승률: 계산 불가 (거래 없음)")
        #         print("6. 수익비율: 계산 불가 (거래 없음)")
        # except Exception as e:
        #     print("5. 승률: 계산 중 오류 발생", str(e))
        #     print("6. 수익비율: 계산 중 오류 발생", str(e))
