import pandas as pd
import matplotlib.pyplot as plt


class CandleGraphChart:
    @staticmethod
    def save_fig(
        transactions,
        df: pd.DataFrame,
        filename: str = "backtrader_plot",
    ):
        # 매수/매도 시그널 추출
        buy_signals = []
        sell_signals = []

        for date, trades in transactions.items():
            for trade in trades:
                amount = trade[0]
                price = trade[1]

                if amount > 0:
                    buy_signals.append((date, price))
                else:
                    sell_signals.append((date, price))

        # 그래프 생성
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(15, 10), gridspec_kw={"height_ratios": [3, 1]}
        )

        # 캔들차트 그리기
        candlestick_width = 0.6
        up_color = "red"
        down_color = "blue"

        for i in range(len(df)):
            open_price = df["open"].iloc[i]
            close_price = df["close"].iloc[i]
            high_price = df["high"].iloc[i]
            low_price = df["low"].iloc[i]

            color = up_color if close_price >= open_price else down_color

            # 캔들 몸통
            ax1.add_patch(
                plt.Rectangle(
                    (i - candlestick_width / 2, min(open_price, close_price)),
                    candlestick_width,
                    abs(close_price - open_price),
                    facecolor=color,
                )
            )

            # 위아래 선
            ax1.plot([i, i], [low_price, high_price], color=color)

        # 매수/매도 신호 표시
        for buy_date, buy_price in buy_signals:
            idx = df.index.get_loc(buy_date)
            ax1.plot(idx, buy_price, "^", color="green", markersize=10, label="Buy")

        for sell_date, sell_price in sell_signals:
            idx = df.index.get_loc(sell_date)
            ax1.plot(idx, sell_price, "v", color="red", markersize=10, label="Sell")

        # 중복된 레전드 제거
        handles, labels = ax1.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax1.legend(by_label.values(), by_label.keys())

        # 볼륨 바 그리기
        ax2.bar(
            range(len(df)),
            df["volume"],
            color=[
                (up_color if df["close"].iloc[i] >= df["open"].iloc[i] else down_color)
                for i in range(len(df))
            ],
        )

        # 축 설정
        ax1.set_title("Price with Buy/Sell Signals")
        ax1.grid(True)
        ax2.set_title("Volume")
        ax2.grid(True)

        # x축 날짜 표시
        date_ticks = range(0, len(df), len(df) // 10)
        ax1.set_xticks(date_ticks)
        ax1.set_xticklabels(
            [df.index[i].strftime("%Y-%m-%d") for i in date_ticks], rotation=45
        )
        ax2.set_xticks(date_ticks)
        ax2.set_xticklabels(
            [df.index[i].strftime("%Y-%m-%d") for i in date_ticks], rotation=45
        )

        # 그래프 저장
        plt.tight_layout()
        plt.savefig(f"assets/{filename}.png")
        plt.close()
