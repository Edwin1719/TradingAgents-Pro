# TradingAgents/graph/trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.interface import set_config

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
        log_callback: Optional[callable] = None,
        language: str = "zh",
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
            log_callback: Optional callable for logging updates.
            language: Language for the log messages ('en' or 'zh').
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG
        self.log_callback = log_callback
        self.language = language

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatOpenAI(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"])
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"])
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.config,  # Pass config to GraphSetup
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict
        self.log_step_mapping = {
            'zh': {
                "company_of_interest": "🎯 锁定目标: {company_of_interest}",
                "trade_date": "🗓️ 设定行动日期: {trade_date}",
                "market_report": "📈 市场部: 宏观趋势分析完毕。",
                "sentiment_report": "👥 情绪分析部: 市场情绪评估完成。",
                "news_report": "📰 新闻部: 关键情报汇总完毕。",
                "fundamentals_report": "🏦 基本面部: 公司价值评估出炉。",
                "investment_debate_state": "🐂⚔️🐻 多空对决: 策略辩论结束，初步共识已形成。",
                "trader_investment_plan": "✍️ 交易策略师: 初步交易草案已拟定。",
                "risk_debate_state": "🛡️ 风控部: 风险评估通过，计划已加固。",
                "investment_plan": "📝 作战室: 最终交易计划已敲定。",
                "final_trade_decision": "🚀 交易执行: 指令已发出！",
                "fallback": "✅ {step_name}: 操作完成。",
                "start_analysis": "🔍 开始分析: {company_name} on {trade_date}...",
            },
            'en': {
                "company_of_interest": "🎯 Target Locked: {company_of_interest}",
                "trade_date": "🗓️ Action Date Set: {trade_date}",
                "market_report": "📈 Market Desk: Macro trend analysis complete.",
                "sentiment_report": "👥 Sentiment Desk: Market sentiment assessed.",
                "news_report": "📰 News Desk: Key intelligence compiled.",
                "fundamentals_report": "🏦 Fundamentals Desk: Company valuation is ready.",
                "investment_debate_state": "🐂⚔️🐻 Bull vs. Bear: Strategy debate concluded. Initial consensus reached.",
                "trader_investment_plan": "✍️ Trading Strategist: Draft trade plan formulated.",
                "risk_debate_state": "🛡️ Risk Desk: Risk assessment passed. Plan fortified.",
                "investment_plan": "📝 War Room: Final trading plan locked in.",
                "final_trade_decision": "🚀 Trade Execution: Order has been sent!",
                "fallback": "✅ {step_name}: Operation complete.",
                "start_analysis": "🔍 Starting Analysis: {company_name} on {trade_date}...",
            }
        }

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources."""
        return {
            "market": ToolNode(
                [
                    # online tools
                    self.toolkit.get_YFin_data_online,
                    self.toolkit.get_stockstats_indicators_report_online,
                    # offline tools
                    self.toolkit.get_YFin_data,
                    self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # online tools
                    self.toolkit.get_stock_news_openai,
                    # offline tools
                    self.toolkit.get_reddit_stock_info,
                ]
            ),
            "news": ToolNode(
                [
                    # online tools
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    # offline tools
                    self.toolkit.get_finnhub_news,
                    self.toolkit.get_reddit_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # online tools
                    self.toolkit.get_fundamentals_openai,
                    # offline tools
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""

        self.ticker = company_name

        # Add a starting message to the log
        lang_templates = self.log_step_mapping.get(self.language, self.log_step_mapping['en'])
        start_message = lang_templates.get("start_analysis", "Starting analysis for {company_name} on {trade_date}...").format(
            company_name=company_name, 
            trade_date=trade_date
        )
        if self.log_callback:
            self.log_callback(start_message)

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        # Replace invoke with stream to get real-time updates
        final_state = None
        for chunk in self.graph.stream(init_agent_state, **args):
            if self.log_callback:
                for key, value in chunk.items():
                    if value:
                        # Select the language template
                        lang_templates = self.log_step_mapping.get(self.language, self.log_step_mapping['en'])
                        step_template = lang_templates.get(key, lang_templates["fallback"])

                        # Prepare context for formatting
                        format_context = {
                            "company_of_interest": init_agent_state.get("company_of_interest"),
                            "trade_date": init_agent_state.get("trade_date"),
                            "step_name": key,
                        }

                        if isinstance(value, dict):
                            format_context.update(value)
                        else:
                            format_context[key] = value
                        
                        # Format the message with robust error handling
                        try:
                            step_message = step_template.format(**format_context)
                        except KeyError:
                            # Fallback for any missing keys in the template
                            fallback_template = lang_templates["fallback"]
                            step_message = fallback_template.format(step_name=key)

                        self.log_callback(step_message)

            final_state = chunk

        if self.log_callback:
            self.log_callback("Analysis complete. Processing final decision...")

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)
