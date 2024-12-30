import pandas as pd
import numpy as np
import backtrader as bt
from typing import Tuple, Dict


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
