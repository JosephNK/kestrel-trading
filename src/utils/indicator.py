import pandas as pd
import numpy as np
import talib


class Indicator:
    """
    Ta-Lib를 사용하여 기술적 분석 지표들을 계산하고 데이터프레임에 추가하는 클래스
    """

    @staticmethod
    def add_sub_indicators(df):
        """
        주어진 데이터프레임에 여러 기술적 지표들을 계산하여 추가하는 메서드

        Parameters:
            df (pandas.DataFrame): 주가 데이터가 포함된 데이터프레임
                                 필수 컬럼: 'close' (종가), 'high' (고가), 'low' (저가)

        Returns:
            pandas.DataFrame: 기술적 지표들이 추가된 데이터프레임
        """

        # 결측치 처리
        df = df.dropna()

        # 볼린저 밴드 계산 (20일, 2 표준편차)
        df["bb_bbm"], df["bb_bbh"], df["bb_bbl"] = talib.BBANDS(
            df["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.SMA
        )

        # RSI 계산 (14일)
        df["rsi"] = talib.RSI(df["close"], timeperiod=14)

        # 이동평균선 계산
        df["sma_20"] = talib.SMA(df["close"], timeperiod=20)  # 20일 단순이동평균
        df["ema_12"] = talib.EMA(df["close"], timeperiod=12)  # 12일 지수이동평균

        # MACD 계산
        df["macd"], df["macd_signal"], df["macd_hist"] = talib.MACD(
            df["close"], fastperiod=12, slowperiod=26, signalperiod=9
        )

        # MACD 교차 계산 (골든크로스/데드크로스)
        df["macd_cross"] = np.select(
            [
                # 골든크로스
                (df["macd"].shift(1) < df["macd_signal"].shift(1))
                & (df["macd"] > df["macd_signal"]),
                # 데드크로스
                (df["macd"].shift(1) > df["macd_signal"].shift(1))
                & (df["macd"] < df["macd_signal"]),
            ],
            [1, -1],
            default=0,
        )

        # 스토캐스틱 계산
        df["stoch_k"], df["stoch_d"] = talib.STOCH(
            df["high"],
            df["low"],
            df["close"],
            fastk_period=3,  # %K 기간
            slowk_period=3,  # %K 스무딩 기간
            slowk_matype=0,  # 단순이동평균 사용
            slowd_period=12,  # %D 기간
            slowd_matype=0,  # 단순이동평균 사용
        )

        # # 결과 확인
        # print(df[["macd", "macd_signal", "macd_cross"]].tail())

        # # 교차 발생한 날짜만 확인
        # cross_days = df[df["macd_cross"] != 0]
        # print("\n교차 발생일:", cross_days[["macd", "macd_signal", "macd_cross"]])

        return df
