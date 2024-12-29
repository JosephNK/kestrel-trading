from dotenv import load_dotenv
from src.agents.kestrel_agent import KestrelAiAgent
from src.exchanges.strategy.strategies.profitable_strategy import (
    ProfitableRealTimeStrategy,
)
from src.exchanges.strategy.strategy import BacktestingStrategy
from src.exchanges.upbit.upbit_exchange import UpbitExchange
from src.utils.whale_etherscan import EtherscanWhaleTransaction

load_dotenv()


def main1():
    try:
        exchange = UpbitExchange()
        exchange.ticker = "KRW-BORA"
        day_candle_df = exchange.get_candle(count=200, interval="day")
        BacktestingStrategy.run(day_candle_df)
    except Exception as e:
        print(e)


def main2():
    try:
        exchange = UpbitExchange()
        day_candle_df = exchange.get_candle(count=200, interval="day")
        strategy = ProfitableRealTimeStrategy(df=day_candle_df)
        # 전체 데이터에 대해 순차적으로 분석
        for i in range(50, len(day_candle_df)):
            signal = strategy.analyze_market(current_index=i)
            print(f"Time {i}: Signal = {signal}")
        # latest_signal = strategy.analyze_market()
    except Exception as e:
        print(e)


def main3():
    try:
        exchange = UpbitExchange()
        exchange.sell_market()
    except Exception as e:
        print(e)


def main4():
    try:
        exchange = UpbitExchange()
        exchange.ticker = "KRW-BTC"
        ai_agent = KestrelAiAgent()

        # 분석용 데이터 준비
        analysis_data = exchange.prepare_analysis_data()
        # print("analysis_data", analysis_data)

        # # AI 매매 결정
        # answer = ai_agent.invoke(source_data=analysis_data, is_pass=False)
        # print("answer", answer)

        # # 매매 실행
        # exchange.trading(answer=answer)
    except Exception as e:
        print(e)


def main5():
    try:
        whale = EtherscanWhaleTransaction()
        transactions = whale.get_historical_wbtc_transactions(
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        whale.print_transaction_summary(transactions)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main5()
