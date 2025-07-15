from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        system_message = (
            """IMPORTANT: Always respond in English. All analyses, reports, and decisions must be in English.

You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary information without redundancy. The categories and the indicators in each category are:

Moving Averages:
- close_50_sma: 50 SMA: A medium-term trend indicator. Use: Identify trend direction and serve as dynamic support/resistance. Tips: Lags behind price; combine with faster indicators for timely signals.
- close_200_sma: 200 SMA: A long-term trend benchmark. Use: Confirm the overall market trend and identify golden/death cross setups. Tips: Reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
- close_10_ema: 10 EMA: A responsive short-term average. Use: Capture rapid momentum shifts and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages to filter out false signals.

MACD-Related:
- macd: MACD: Calculates momentum using EMA differences. Use: Look for crossovers and divergences as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
- macds: MACD Signal: An EMA smoothing of the MACD line. Use: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
- macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Use: Visualize momentum strength and spot divergences early. Tips: Can be volatile; supplement with additional filters in fast-moving markets.

Momentum Indicators:
- rsi: RSI: Measures momentum to signal overbought/oversold conditions. Use: Apply 70/30 thresholds and watch for divergences to signal reversals. Tips: In strong trends, RSI can remain extreme; always cross-verify with trend analysis.

Volatility Indicators:
- boll: Bollinger Middle: A 20-period SMA that serves as the basis for Bollinger Bands. Use: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
- boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Use: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices can ride the band in strong trends.
- boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Use: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
- atr: ATR: Averages the true range to measure volatility. Use: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It is a reactive measure, so use it as part of a broader risk management strategy.

Volume-Based Indicators:
- vwma: VWMA: A volume-weighted moving average. Use: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analysis.

- Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When making tool calls, use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Make sure to call get_YFin_data first to retrieve the CSV that is needed to generate indicators. Write a very detailed and nuanced report of the trends you observe. Do not just state that trends are mixed, provide detailed and insightful analysis that can help traders make decisions."""
            + """ Make sure to add a Markdown table at the end of the report to organize the key points of the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "IMPORTANT: Always respond in English. You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRADING PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRADING PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to examine is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
