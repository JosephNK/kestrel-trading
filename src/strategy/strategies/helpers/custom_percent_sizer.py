import backtrader as bt


class CustomPercentSizer(bt.Sizer):
    params = (
        ("buy_percent", 30),  # 매수시 사용할 퍼센트
        ("sell_percent", 50),  # 매도시 사용할 퍼센트
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        # comminfo를 통해 수수료 정보 가져오기
        commission_rate = comminfo.p.commission

        # 현재 포지션 정보 가져오기
        position = self.broker.getposition(data)

        # 수수료를 고려한 최대 주문 가능 금액 계산
        # 현재 사용 가능한 현금에서 수수료를 제외한 실제 투자 가능 금액
        max_order_cash = cash / (1 + commission_rate)

        value = 0
        size = 0

        if position:
            # 매도 상황
            if not isbuy:
                size = position.size * (self.params.sell_percent / 100)
            # 이미 포지션 있는 상태에서 추가 매수
            else:
                value = max_order_cash * (self.params.buy_percent / 100)
                size = value / data[0]
        # 신규 매수
        else:
            if isbuy:
                value = max_order_cash * (self.params.buy_percent / 100)
                size = value / data[0]
            else:
                size = 0

        return size
