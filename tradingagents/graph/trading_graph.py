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
from tradingagents.agents.analysts.arkham_analyst import ArkhamAnalyst
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
        self.arkham_analyst = ArkhamAnalyst(
            api_key=self.config.get("ARKHAM_API_KEY"),
            api_secret=self.config.get("ARKHAM_API_SECRET")
        )

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
            self.arkham_analyst, # Pass arkham analyst
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
                "company_of_interest": "---\n### 🎯 **交易员指令已确认**\n- **分析目标:** {company_of_interest}",
                "trade_date": "- **分析日期:** {trade_date}\n---",
                "market_report": "### 📈 **阶段1: 分析师团队启动**\n- **市场分析师** 已完成宏观趋势评估。",
                "sentiment_report": "- **情绪分析师** 已完成市场情绪评估。",
                "news_report": "- **新闻分析师** 已完成关键情报汇总。",
                "fundamentals_report": "- **基本面分析师** 已完成公司价值评估。",
                "whale_tracking_report": "- **巨鲸追踪分析师** 已完成链上大额异动监控。",
                "investment_debate_state": "### ⚖️ **阶段2: 多空策略辩论**\n- **仲裁法官** 判定最终共识为: \n> {judge_decision}",
                "trader_investment_plan": "### ✍️ **阶段3: 交易策略与风险评估**\n- **交易策略师** 已拟定初步交易草案。",
                "risk_debate_state": "- **风险管理官** 已完成风险评估。",
                "investment_plan": "### 📝 **阶段4: 生成最终计划**\n- **作战室** 已敲定最终交易计划。",
                "final_trade_decision": "### 🚀 **阶段5: 输出最终决策**\n- **交易指令:** {action} (置信度: {confidence})"
            },
            'en': {
                "company_of_interest": "---\n### 🎯 **Trader's Directive Confirmed**\n- **Analysis Target:** {company_of_interest}",
                "trade_date": "- **Analysis Date:** {trade_date}\n---",
                "market_report": "### 📈 **Phase 1: Analyst Team Kick-off**\n- **Market Analyst** has completed the macro trend assessment.",
                "sentiment_report": "- **Sentiment Analyst** has completed the market sentiment assessment.",
                "news_report": "- **News Analyst** has compiled key intelligence.",
                "fundamentals_report": "- **Fundamentals Analyst** has completed the company valuation.",
                "whale_tracking_report": "- **Whale Tracking Analyst** has completed on-chain large transaction monitoring.",
                "investment_debate_state": "### ⚖️ **Phase 2: Strategy Debate**\n- **The Judge** has determined the final consensus: \n> {judge_decision}",
                "trader_investment_plan": "### ✍️ **Phase 3: Trading Strategy & Risk Assessment**\n- **Trading Strategist** has drafted a preliminary trade plan.",
                "risk_debate_state": "- **Risk Management Officer** has completed the risk assessment.",
                "investment_plan": "### 📝 **Phase 4: Final Plan Generation**\n- **War Room** has locked in the final trading plan.",
                "final_trade_decision": "### 🚀 **Phase 5: Final Decision Output**\n- **Trade Order:** {action} (Confidence: {confidence})"
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
            "whale_tracking": ToolNode([self.arkham_analyst.analyze]),
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
        logged_keys = set()
        # Define a blacklist of keys to ignore in logging
        log_blacklist = {"messages", "sender"}

        for chunk in self.graph.stream(init_agent_state, **args):
            if self.log_callback:
                for key, value in chunk.items():
                    # Condition to log:
                    # 1. Key has a value
                    # 2. Key has not been logged before
                    # 3. Key is not in the blacklist
                    if value and key not in logged_keys and key not in log_blacklist:
                        
                        # Add "patience" for complex states: wait for the final piece of info
                        if key == "investment_debate_state" and "judge_decision" not in value:
                            continue
                        if key == "risk_debate_state" and "judge_decision" not in value:
                            continue
                        if key == "final_trade_decision" and "action" not in value:
                            continue

                        logged_keys.add(key)
                        
                        # Select the language template
                        lang_templates = self.log_step_mapping.get(self.language, self.log_step_mapping['en'])
                        step_template = lang_templates.get(key)

                        # If no specific template, skip logging
                        if not step_template:
                            continue

                        # Prepare context for formatting, starting with the initial state
                        format_context = init_agent_state.copy()
                        
                        # If the value is a dictionary, update the context with it
                        if isinstance(value, dict):
                            format_context.update(value)
                        # Otherwise, add the value directly to the context
                        else:
                            format_context[key] = value
                        
                        # Format the message with robust error handling
                        try:
                            # Use a dictionary comprehension to filter only the keys needed for the template
                            # This avoids KeyErrors for templates that don't need all context variables
                            template_keys = [k[1] for k in __import__('string').Formatter().parse(step_template) if k[1] is not None]
                            filtered_context = {k: format_context.get(k, f'{{{k}}}') for k in template_keys}
                            step_message = step_template.format(**filtered_context)
                            self.log_callback(step_message)
                        except KeyError as e:
                            # This fallback is less likely to be needed now, but good to have
                            print(f"[Log Formatting Error] Key {e} not found for template: {step_template}")


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
            "whale_tracking_report": final_state.get("whale_tracking_report"),
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
