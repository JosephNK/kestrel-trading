from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.callbacks import get_openai_callback

# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from src.exchanges.strategy.strategies.datas.types import StrategyType
from pydantic import BaseModel, Field
from typing import Literal


class TradingDecision(BaseModel):
    decision: Literal["buy", "sell", "hold"] = Field(
        description="Trading decision: buy, sell, or hold",
    )
    reason: str = Field(
        description="Reasoning behind the trading decision",
    )
    # percentage: str = Field(description="Percentage for the trading action")


class KestrelAiAgent:
    llm: ChatOpenAI
    prompt_template: ChatPromptTemplate

    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.7,
        )

    def invoke(
        self,
        analysis_data: str,
        strategy_type: StrategyType = StrategyType.PROFITABLE,
    ) -> dict:
        """
        AI 모델에 데이터를 전달하고 매매 결정을 받아오는 함수

        Args:
            source_data (str): JSON 형식의 분석 데이터 문자열 (캔들 데이터, 호가 데이터 포함)

        Returns:
            dict: 매매 결정 딕셔너리
                - decision: 'buy', 'sell', 또는 'hold'
                - reason: 결정에 대한 이유
        """

        # 전략 메시지 설정
        strategy_message: str = ""
        if strategy_type is StrategyType.PROFITABLE:
            strategy_message = "Profitable Strategy"

        # JsonOutputParser 설정
        json_parser = JsonOutputParser(pydantic_object=TradingDecision)

        # 시스템 템플릿 정의
        system_template = """
        You are a cryptocurrency trading expert who provides clear market analysis and trading decisions.

        Market Data:
        - Current Investment Status
        - OHLCV With Indicators
        - Orderbook Status
        - Trading Strategy is {strategy_message}

        TRADING RULES:
        - Reflect the results of trading strategy as much as possible.
        """

        # 인간 프롬프트 템플릿 정의
        human_template = """
        Please analyze the following market data and make a trading decision:
        {analysis_data}
        """

        # AI Prompt 생성
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", human_template),
                ("system", "{format_instructions}"),
            ]
        )

        # Format Instructions 설정
        format_instructions = json_parser.get_format_instructions()

        # 필요한 변수들을 딕셔너리로 전달
        variables = {
            "strategy_message": strategy_message,
            "analysis_data": analysis_data,
            "format_instructions": format_instructions,
        }

        # Chain 생성
        chain = prompt_template | self.llm | json_parser

        # 토큰 추적 함수
        def track_tokens():
            with get_openai_callback() as cb:
                response = chain.invoke(variables)

                response["total_tokens"] = cb.total_tokens  # 총 토큰
                response["prompt_tokens"] = cb.prompt_tokens  # 프롬프트 토큰
                response["completion_tokens"] = cb.completion_tokens  # 완성 토큰
                response["total_cost"] = cb.total_cost  # 총 비용 $USD

                return response

        # AI 실행
        answer = track_tokens()

        print(answer)

        return answer
