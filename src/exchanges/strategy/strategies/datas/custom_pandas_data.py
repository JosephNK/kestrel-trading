import backtrader as bt


# 커스텀 데이터 피드 클래스 정의
class CustomPandasData(bt.feeds.PandasData):
    lines = (
        "rsi",
        "macd",
        "macd_signal",
        "macd_cross",
        "sma_20",
        "ema_12",
        "stoch_k",
        "stoch_d",
        "value",
    )
    params = (
        ("datetime", None),
        ("open", "open"),
        ("high", "high"),
        ("low", "low"),
        ("close", "close"),
        ("volume", "volume"),
        ("openinterest", -1),
        ("rsi", "rsi"),
        ("macd", "macd"),
        ("macd_signal", "macd_signal"),
        ("macd_cross", "macd_cross"),
        ("sma_20", "sma_20"),
        ("ema_12", "ema_12"),
        ("stoch_k", "stoch_k"),
        ("stoch_d", "stoch_d"),
        ("value", "value"),
    )
