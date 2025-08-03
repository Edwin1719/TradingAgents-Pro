from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory, config):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Get language instruction from config
        lang_instruction = config.get("language_instruction", "IMPORTANT: Always respond in English.")

        task_prompt = f"""You are a Bullish Analyst advocating for investing in the stock. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company's market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong brand, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bearish Counterpoints: Critically analyze the bearish argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bullish outlook has stronger merit.
- Engagement: Present your argument in a conversational style, directly engaging with the bearish analyst's points and debating effectively rather than just listing data.

Available resources:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Debate conversation history: {history}
Latest bearish argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bullish argument, rebut bearish concerns, and engage in a dynamic debate that demonstrates the strengths of the bullish position. You should also address reflections and learn from lessons and mistakes you made in the past.
"""

        prompt = f"{lang_instruction}\n{task_prompt}"

        response = llm.invoke(prompt)

        argument = f"Analista Optimista: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
