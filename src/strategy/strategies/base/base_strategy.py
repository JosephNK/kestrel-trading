import pandas as pd

from typing import Optional

from src.strategy.strategies.datas.data import (
    EntryPosition,
    MarketData,
    TradingAnalyzeData,
)


class BaseStrategy:
    df: pd.DataFrame
    window_size: int
    market_data: MarketData
    entry_position: Optional[EntryPosition]

    def __init__(self, df: pd.DataFrame):
        if not all(col in df.columns for col in ["close", "high", "low"]):
            raise ValueError(
                "DataFrame must contain 'close', 'high', and 'low' columns"
            )

        self.window_size = 50  # 분석에 사용할 데이터 윈도우 크기
        self.df = df

    def analyze_market(
        self,
        entry_position: Optional[EntryPosition] = None,
    ) -> TradingAnalyzeData | None:
        """
        시장 데이터 분석 및 매매 신호 생성

        Args:
            current_index: 현재 분석할 시점의 인덱스
            entry_position: 진입 포지션 설정
        """

        self.entry_position = entry_position

        # 최근 50개 데이터만 슬라이싱
        last_index = len(self.df) - 1
        start_idx = max(0, last_index - self.window_size + 1)
        end_idx = last_index + 1

        self.market_data = MarketData(
            close=self.df["close"].values[start_idx:end_idx],
            high=self.df["high"].values[start_idx:end_idx],
            low=self.df["low"].values[start_idx:end_idx],
        )
