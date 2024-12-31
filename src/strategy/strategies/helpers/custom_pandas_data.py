import backtrader as bt


# 커스텀 데이터 피드 클래스 정의
class CustomPandasData(bt.feeds.PandasData):
    # lines = (
    #     "rsi",
    #     "macd",
    #     "macd_signal",
    #     "macd_cross",
    #     "sma_20",
    #     "ema_12",
    #     "stoch_k",
    #     "stoch_d",
    #     "value",
    # )
    params = (
        ("datetime", None),
        ("open", -1),
        ("high", -1),
        ("low", -1),
        ("close", -1),
        ("volume", -1),
        ("openinterest", -1),
    )
