from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Detect if it is a cryptocurrency
        is_crypto = ticker.endswith("-USD") or ticker.endswith("-EUR") or ticker.endswith("-USDT")
        
        if is_crypto:
            # For cryptocurrencies, use adapted tools
            if toolkit.config["online_tools"]:
                tools = [toolkit.get_fundamentals_openai]  # Can search for crypto info online
            else:
                tools = []  # No specific offline tools for crypto
        else:
            # For stocks, use traditional tools
            if toolkit.config["online_tools"]:
                tools = [toolkit.get_fundamentals_openai]
            else:
                tools = [
                    toolkit.get_finnhub_company_insider_sentiment,
                    toolkit.get_finnhub_company_insider_transactions,
                    toolkit.get_simfin_balance_sheet,
                    toolkit.get_simfin_cashflow,
                    toolkit.get_simfin_income_stmt,
                ]

        # Detect if it is a cryptocurrency
        is_crypto = ticker.endswith("-USD") or ticker.endswith("-EUR") or ticker.endswith("-USDT")
        
        if is_crypto:
            system_message = (
                "IMPORTANT: Always respond in English. All analyses, reports, and decisions must be in English.\n\nYou are a researcher tasked with analyzing fundamental information about a cryptocurrency. Since cryptocurrencies do not have traditional financial statements, focus on: project fundamentals, tokenomics, network activity, adoption metrics, partnerships, development activity, governance, and market position. For crypto assets, analyze the underlying blockchain technology, use cases, total supply, circulating supply, staking rewards, and ecosystem growth. Provide detailed insights that help traders understand the long-term value proposition of this cryptocurrency."
                + " Make sure to add a Markdown table at the end of the report to organize the key points of the report, organized and easy to read."
            )
        else:
            system_message = (
                "IMPORTANT: Always respond in English. All analyses, reports, and decisions must be in English.\n\nYou are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report on the company's fundamental information such as financial documents, company profile, basic company finances, company financial history, insider sentiment, and insider transactions to get a complete view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Do not just state that trends are mixed, provide detailed and insightful analysis that can help traders make decisions."
                + " Make sure to add a Markdown table at the end of the report to organize the key points of the report, organized and easy to read."
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
