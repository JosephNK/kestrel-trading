from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class KestrelAiAgent:
    llm: ChatOpenAI
    prompt: ChatPromptTemplate
    parser: JsonOutputParser

    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,  # 일관성을 위해 temperature 설정
        )

        self.parser = JsonOutputParser()

    def create_prompt(self):
        system_template = """
        You are an expert in cryptocurrency coin investing. Your role is to analyze market data and make precise trading decisions based on the following criteria.

        Market Data:
        - Current balance, position size, and P/L (Profit/Loss)
        - Current price and buy price
        - Technical indicators:
          - RSI(14)
          - MACD(2,19,7) with signal and difference
          - Bollinger Bands (middle, upper, lower)
          - Moving averages (SMA20, EMA12)

        Trading Rules:
        1. Buy Condition (all required):
          - The Relative Strength Index (RSI) with a length of 14 crosses above the 30 threshold.
          - The Moving Average Convergence Divergence (MACD) indicator has the following settings: fast length of 2, slow length of 19, signal line of 7, and crosses above the zero line.
          - The Provide a percentage (1-100) of available KRW
        2. Sell Strategy:
          - Sell 50% of the position when the price increases by 10% from the buy price.
          - Sell the remaining 50% when the price further increases by 20%.

        Response Example:
        {{\"decision\": \"buy\", \"percentage\": \"10%\", \"reason\": \"Strong buying pressure in orderbook with 30-day upward trend\"}}
        {{\"decision\": \"sell\", \"percentage\": \"50%\" \"reason\": \"High ask/bid ratio indicating selling pressure, take profit at 5%\"}}
        {{\"decision\": \"hold\", \"percentage\": \"0%\" \"reason\": \"Market in consolidation phase, wait for clear direction\"}}
        """

        # system_template = """
        # You are an expert in cryptocurrency coin investing. Your role is to analyze market data and make precise trading decisions based on the following criteria.

        # MARKET DATA:
        # - **Investment Status**:
        #     - Current balance, position, and P/L
        # - **Technical Analysis**:
        #   - Bollinger Bands (bb_bbm, bb_bbh, bb_bbl)
        #   - RSI (rsi)
        #   - MACD (macd, macd_signal, macd_diff)
        #   - Moving Averages (sma_20, ema_12)

        # TRADING DECISION:
        # - **Buy Condition**: Execute a buy order when both of the following conditions are met:
        #   - The Relative Strength Index (RSI) with a length of 14 crosses above the 30 threshold.
        #   - The Moving Average Convergence Divergence (MACD) indicator has the following settings: fast length of 2, slow length of 19, signal line of 7, and crosses above the zero line.

        # - **Sell Strategy**:
        #   1. Sell 50% of the position when the price increases by 10% from the buy price.
        #   2. Sell the remaining 50% when the price further increases by 20%.

        # Response Example:
        # {{\"decision\": \"buy\", \"reason\": \"Strong buying pressure in orderbook with 30-day upward trend\"}}
        # {{\"decision\": \"sell\", \"reason\": \"High ask/bid ratio indicating selling pressure, take profit at 5%\"}}
        # {{\"decision\": \"hold\", \"reason\": \"Market in consolidation phase, wait for clear direction\"}}
        # """

        # system_template = """
        # You are an expert in cryptocurrency coin investing.
        # Analyze market data and make trading decisions based on the following information:

        # MARKET DATA:
        # 1. Investment Status
        # - Current balance, position, and P/L
        # - Minimum trade: 5000 KRW
        # - Risk limit: 50% of available funds
        # - Buy ratio: 10-50% of available KRW balance
        # - Sell ratio: 10-50% of current coin position
        # - Hold ratio: 0% (no new position changes)

        # 2. Technical Analysis
        # - 30-day daily candles
        # - 24-hour hourly candles
        # - Key indicators: RSI, MACD
        # - Support/resistance levels

        # 3. Market Depth
        # - Current orderbook (15 levels)
        # - Ask/bid volume ratio
        # - Price pressure analysis

        # 4. Market Sentiment
        # - Fear & Greed Index (0-100):
        #   * Extreme Fear (0-25): Strong buy signal
        #   * Fear (26-45): Moderate buy signal
        #   * Neutral (46-55): Hold signal
        #   * Greed (56-75): Moderate sell signal
        #   * Extreme Greed (76-100): Strong sell signal
        # - News Sentiment Analysis:
        #   * Recent news headlines
        #   * Key topics monitoring:
        #     - Regulatory news
        #     - Market adoption news
        #     - Technical developments
        #     - Major institutional moves

        # TRADING DECISION FRAMEWORK:
        # 1. BUY DECISION (Confidence & Ratio):
        # Very Strong (90-100% Confidence, 40-50% Ratio):
        # - Multiple indicators confirm uptrend
        # - Strong volume support
        # - RSI below 30
        # - Price near strong support level
        # - Very strong bid pressure
        # - Fear & Greed Index: Extreme Fear (0-25)

        # Strong (80-89% Confidence, 30-39% Ratio):
        # - Clear uptrend
        # - Good volume support
        # - RSI below 35
        # - Price approaching support
        # - Strong bid pressure
        # - Fear & Greed Index: Fear (26-45)

        # Moderate (70-79% Confidence, 20-29% Ratio):
        # - Uptrend with some uncertainty
        # - Decent volume
        # - RSI below 40
        # - Moderate bid pressure
        # - Fear & Greed Index: Near Fear levels

        # 2. SELL DECISION (Confidence & Ratio):
        # Very Strong (90-100% Confidence, 40-50% Ratio):
        # - Multiple indicators confirm downtrend
        # - Heavy selling pressure
        # - RSI above 70
        # - Price hit +5% profit target
        # - Fear & Greed Index: Extreme Greed (76-100)

        # Strong (80-89% Confidence, 30-39% Ratio):
        # - Clear downtrend
        # - Strong selling pressure
        # - RSI above 65
        # - Price approaching -3% stop loss
        # - Fear & Greed Index: Greed (56-75)

        # Moderate (70-79% Confidence, 20-29% Ratio):
        # - Downtrend with some uncertainty
        # - Moderate selling pressure
        # - RSI above 60
        # - Price movement against position

        # 3. HOLD DECISION:
        # - Confidence: 60-75%
        # - Ratio: 0% (maintain current position)
        # Conditions:
        # - Sideways movement/No clear trend
        # - Balanced orderbook
        # - RSI between 40-60
        # - P/L within -2% to +4%
        # - Fear & Greed Index: Neutral (46-55)

        # Not Recommended (Below 60% Confidence):
        # - Conflicting signals
        # - High uncertainty
        # - No clear trend
        # - Ratio: 0% (no new positions)

        # Response Example:
        # {{\"decision\": \"buy\", \"confidence\": \"85%\", \"ratio\": \"30%\", \"reason\": \"Strong buying pressure in orderbook with 30-day upward trend\"}}
        # {{\"decision\": \"sell\", \"confidence\": \"92%\", \"ratio\": \"40%\", \"reason\": \"High ask/bid ratio indicating selling pressure, take profit at 5%\"}}
        # {{\"decision\": \"hold\", \"confidence\": \"75%\", \"ratio\": \"0%\", \"reason\": \"Market in consolidation phase, wait for clear direction\"}}
        # """

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", "{source}"),
            ]
        )

    def invoke(self, source_data: str, is_pass: bool = False) -> dict:
        """
        AI 모델에 데이터를 전달하고 매매 결정을 받아오는 함수

        Args:
            source_data (str): JSON 형식의 분석 데이터 문자열 (캔들 데이터, 호가 데이터 포함)

        Returns:
            dict: 매매 결정 딕셔너리
                - decision: 'buy', 'sell', 또는 'hold'
                - reason: 결정에 대한 이유
        """

        if is_pass is True:
            return {"decision": "hold", "reason": "This is test reason"}

        self.create_prompt()
        self.prompt = self.prompt.partial(
            format_instructions=self.parser.get_format_instructions()
        )
        chain = self.prompt | self.llm | self.parser
        answer = chain.invoke({"source": source_data})
        return answer
