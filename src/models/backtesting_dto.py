from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from datetime import datetime, timezone


# 백테스팅 거래 내역을 표현하는 DTO 클래스
class BackTestingTransactionDto(BaseModel):
    id: int | None = None  # 거래 내역 고유 식별자
    trade_signal: str | None = None  # 거래 신호
    order_quantity: float | None = None  # 주문 수량
    execution_price: float | None = None  # 체결 가격
    stock_id: str | None = None  # 주식 고유 식별자
    stock_code: str | None = None  # 주식 종목 코드
    transaction_value: float | None = None  # 거래 금액
    executed_at: datetime | None = None  # 거래 체결 시간

    class Config:
        alias_generator = to_camel  # snake_case를 camelCase로 변환
        populate_by_name = True  # 별칭과 원래 이름 모두 허용
        from_attributes = True  # ORM 모델 -> DTO 변환 허용
        json_encoders = {
            datetime: lambda v: v.astimezone(
                tz=timezone.utc
            ),  # datetime을 UTC 시간대로 변환
        }


# 백테스팅 결과를 표현하는 DTO 클래스
class BackTestingDto(BaseModel):
    id: int = 0  # 백테스팅 결과 고유 식별자
    ticker: str | None = None  # 거래 통화
    initial_portfolio_value: float | None = None  # 초기 포트폴리오 가치
    final_portfolio_value: float | None = None  # 최종 포트폴리오 가치
    sharpe_ratio: float | None = None  # 샤프 비율 (위험 대비 수익률)
    total_returns_per: float | None = None  # 총 수익
    maximum_drawdown_per: float | None = None  # 최대 손실폭
    roi_per: float | None = None  # 투자 수익률
    transactions: list[BackTestingTransactionDto] | None = None  # 거래 내역 목록
    candle_graph_chart_file_path: str | None = None  # 캔들 차트 파일 경로
    exchange_provider: str | None = None  # 거래소 제공자
    created_at: datetime | None = None  # 생성 시간
    updated_at: datetime | None = None  # 수정 시간
    deleted_at: datetime | None = None  # 삭제 시간

    class Config:
        alias_generator = to_camel  # snake_case를 camelCase로 변환
        populate_by_name = True  # 별칭과 원래 이름 모두 허용
        from_attributes = True  # ORM 모델 -> DTO 변환 허용
        json_encoders = {
            datetime: lambda v: v.astimezone(
                tz=timezone.utc
            ),  # datetime을 UTC 시간대로 변환
        }
