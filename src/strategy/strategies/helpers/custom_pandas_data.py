import backtrader as bt


# 커스텀 데이터 피드 클래스 정의
class CustomPandasData(bt.feeds.PandasData):
    params = (
        # ("datetime", None),
        ("open", "Open"),  # DataFrame의 'Open' 컬럼과 매핑
        ("high", "High"),  # DataFrame의 'High' 컬럼과 매핑
        ("low", "Low"),  # DataFrame의 'Low' 컬럼과 매핑
        ("close", "Close"),  # DataFrame의 'Close' 컬럼과 매핑
        ("volume", "Volume"),  # DataFrame의 'Volume' 컬럼과 매핑
        ("openinterest", -1),  # -1은 해당 컬럼을 사용하지 않음을 의미
    )
