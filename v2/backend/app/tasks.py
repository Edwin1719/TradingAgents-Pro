
import os
import sys
from typing import Optional
from celery import Celery

# Add the project root to the Python path
# This is necessary for Celery to find the `tradingagents` module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .celery_worker import celery_app
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def clean_state_for_json(state):
    """
    Recursively cleans a state dictionary to make it JSON serializable.
    Converts any non-serializable objects (like HumanMessage) to their string representation.
    """
    if isinstance(state, dict):
        return {k: clean_state_for_json(v) for k, v in state.items()}
    elif isinstance(state, list):
        return [clean_state_for_json(i) for i in state]
    elif hasattr(state, '__dict__'):
        # This will handle most custom objects, including HumanMessage,
        # by converting them to a string representation.
        return str(state)
    else:
        # For basic types that are already JSON serializable
        return state

@celery_app.task(bind=True)
def run_analysis_task(self, ticker: str, date: str, deep_think_llm: Optional[str] = None, quick_think_llm: Optional[str] = None):
    """
    The actual long-running analysis task, now managed by Celery.
    This task will instantiate and run the TradingAgentsGraph.
    Allows overriding LLM models at runtime.
    """
    print(f"[Celery Task] Starting analysis for {ticker} on {date}...")

    # --- Configuration Setup ---
    # In a real app, API keys should come from environment variables
    # or a secure config management system.
    config = DEFAULT_CONFIG.copy()
    config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
    config["finnhub_api_key"] = os.getenv("FINNHUB_API_KEY")
    
    # *** IMPORTANT: Apply the custom OpenAI API base URL if provided ***
    openai_api_base = os.getenv("OPENAI_API_BASE")
    if openai_api_base:
        config["backend_url"] = openai_api_base
        print(f'[Celery Task] Using custom OpenAI API base: {openai_api_base}')

    # *** IMPORTANT: Override models if provided in the request ***
    if deep_think_llm:
        config["deep_think_llm"] = deep_think_llm
        print(f'[Celery Task] Overriding deep_think_llm with: {deep_think_llm}')
    if quick_think_llm:
        config["quick_think_llm"] = quick_think_llm
        print(f'[Celery Task] Overriding quick_think_llm with: {quick_think_llm}')

    if not config["openai_api_key"] or not config["finnhub_api_key"]:
        print("[Celery Task] ERROR: API keys are not configured.")
        # You can update the task state to reflect the failure
        self.update_state(state='FAILURE', meta={'exc_type': 'ConfigurationError', 'exc_message': 'API keys missing.'})
        raise ValueError("Missing OPENAI_API_KEY or FINNHUB_API_KEY environment variables.")

    # --- Instantiate and Run the Graph ---
    try:
        # Initialize the main graph orchestrator
        trading_graph = TradingAgentsGraph(config=config)

        # Execute the analysis process
        final_state, processed_signal = trading_graph.propagate(
            company_name=ticker,
            trade_date=date
        )

        print(f"[Celery Task] Analysis for {ticker} completed.")
        
        # Clean the final_state to ensure it's JSON serializable
        cleaned_state = clean_state_for_json(final_state)
        
        # The result of the task is the cleaned final state from the graph
        return cleaned_state

    except Exception as e:
        print(f"[Celery Task] An error occurred during analysis: {e}")
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise
