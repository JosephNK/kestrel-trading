import backtrader as bt
from datetime import datetime, timedelta


class DCAStrategy(bt.Strategy):
    params = (
        ("investment_amount", 1000000),  # 기본 투자금액
        ("dca_period", 30),  # DCA 주기 (일)
    )

    def __init__(self):
        # 기본 데이터 피드에 대한 참조 저장
        self.dataclose = self.datas[0].close

        # 마지막 투자일 초기화
        self.last_investment = None
        self.order = None
        self.total_invested = 0
        self.entry_prices = []  # 매수 가격 기록

        # 포지션 트래킹을 위한 변수
        self.position_size = 0
        self.buy_price_history = []

        # 매월 투자할 금액을 초기 자본에서 할당
        self.monthly_budget = self.broker.getvalue() * 0.02  # 예: 초기 자본의 2%
        self.params.investment_amount = self.monthly_budget  # 투자 금액 업데이트

        # 최대 투자 한도 설정
        self.max_investment = (
            self.broker.getvalue() * 0.98
        )  # 초기 자본의 98%까지만 투자

    def next(self):
        if self.order:
            return

        current_date = self.data.datetime.date(0)
        current_price = self.dataclose[0]

        # 매도 조건 체크 (예: 수익률이 특정 퍼센트 이상일 때)
        if self.position and len(self.entry_prices) > 0:
            avg_entry_price = sum(self.entry_prices) / len(self.entry_prices)
            current_return = (current_price - avg_entry_price) / avg_entry_price * 100

            # 예: 50% 이상 수익 시 보유 수량의 20% 매도
            if current_return >= 50:
                sell_size = self.position.size * 0.2
                self.order = self.sell(size=sell_size)
                self.log(
                    f"매도 주문: 가격 {current_price:.2f}, 수량 {sell_size:.4f}, 수익률 {current_return:.2f}%"
                )
                return

        # 기존 매수 로직
        should_invest = (
            self.last_investment is None
            or (current_date - self.last_investment).days >= self.params.dca_period
        )

        if should_invest and self.broker.getcash() >= self.params.investment_amount:
            size = self.params.investment_amount / current_price
            self.order = self.buy(size=size)
            self.log(f"매수 주문: 가격 {current_price:.2f}, 수량 {size:.4f}")
            if self.order:
                self.last_investment = current_date
                self.total_invested += self.params.investment_amount
                self.buy_price_history.append(current_price)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.position_size += order.executed.size
                self.entry_prices.append(order.executed.price)
                self.log(
                    f"매수 체결: 가격 {order.executed.price:.2f}, "
                    f"수량 {order.executed.size:.4f}, "
                    f"수수료 {order.executed.comm:.2f}, "
                    f"현금 잔고 {self.broker.getcash():.2f}"
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"주문 취소/거부: {order.status}")
            # 주문이 실패한 경우 투자 기록 롤백
            if self.last_investment == self.data.datetime.date(0):
                self.last_investment = None
                self.total_invested -= self.params.investment_amount
                if self.buy_price_history:
                    self.buy_price_history.pop()

        self.order = None

    def stop(self):
        # 전략 종료 시 최종 성과 출력
        self.total_value = self.broker.getvalue()
        # 투자가 있었을 경우에만 ROI 계산
        roi = (
            ((self.total_value - self.total_invested) / self.total_invested * 100)
            if self.total_invested > 0 and len(self.entry_prices) > 0
            else 0
        )
        avg_entry = (
            sum(self.entry_prices) / len(self.entry_prices) if self.entry_prices else 0
        )

        self.log("===== 전략 실행 결과 =====")
        self.log(f"총 투자 횟수: {len(self.entry_prices)}회")
        self.log(f"평균 매수가: {avg_entry:,.0f}원")
        self.log(f"총 투자금액: {self.total_invested:,.0f}원")
        self.log(f"최종 포트폴리오 가치: {self.total_value:,.0f}원")
        self.log(f"최종 ROI: {roi:,.0f}%")
        self.log("========================")

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print(f"[{dt.isoformat()}] {txt}")
