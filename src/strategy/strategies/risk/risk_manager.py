from typing import Optional
from src.strategy.strategies.datas.data import (
    EntryPosition,
    MarketData,
    RiskParams,
    RiskPosition,
)


class RiskManager:
    risk_params: RiskParams

    def __init__(self, risk_params: RiskParams):
        self.risk_params = risk_params

    def check_exit_conditions(
        self,
        market_data: MarketData,
        current_position: Optional[EntryPosition],
    ) -> RiskPosition:
        """현물 매도 조건 체크 (손절/익절)"""

        if not current_position:
            return RiskPosition(
                selling=False,
                reason="",
                price=0.0,
            )

        current_price = market_data.close[0]  # 현재 봉의 데이터
        entry_price = current_position.entry_price

        # 손절 체크
        if self.risk_params.stop_loss_pct != 0.0:
            stop_loss_price = entry_price * (1 - self.risk_params.stop_loss_pct / 100)
            if current_price <= stop_loss_price:
                return RiskPosition(
                    selling=True,
                    reason=f"손절 매도: 가격 {current_price:.2f}, 진입가 {entry_price:.2f} 대비 {self.risk_params.stop_loss_pct}% 하락",
                    price=stop_loss_price,
                )

        # 익절 체크
        if self.risk_params.take_profit_pct != 0.0:
            take_profit_price = entry_price * (
                1 + self.risk_params.take_profit_pct / 100
            )
            if current_price >= take_profit_price:
                return RiskPosition(
                    selling=True,
                    reason=f"익절 매도: 가격 {current_price:.2f}, 진입가 {entry_price:.2f} 대비 {self.risk_params.take_profit_pct}% 상승",
                    price=take_profit_price,
                )

        return RiskPosition(
            selling=False,
            reason="",
            price=0.0,
        )
