import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Importar los componentes necesarios del framework de trading
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AI Trading Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 AI Trading Agent for Financial Assets")
st.markdown("This application uses a team of AI agents to analyze the asset market and propose a trading decision. Enter your API keys and analysis parameters to get started.")

# --- Configuration Sidebar ---
with st.sidebar:
    st.header("🔑 API Configuration")
    if os.path.exists('.env'):
        load_dotenv()

    openai_api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY") or "")
    openai_api_base = st.text_input("OpenAI API Base URL", value=os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1")
    finnhub_api_key = st.text_input("Finnhub API Key", type="password", value=os.getenv("FINNHUB_API_KEY") or "")
    
    st.header("⚙️ Agent Parameters")
    
    # Asset category and selection
    asset_category = st.selectbox(
        "Asset Category", 
        ["Cryptocurrencies", "Tech Stocks", "Blue Chip Stocks", "Indices", "Custom"]
    )
    
    # Define popular assets by category
    popular_assets = {
        "Cryptocurrencies": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "MATIC-USD", "DOT-USD", "AVAX-USD", "LINK-USD"],
        "Tech Stocks": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META", "AMZN", "NFLX"],
        "Blue Chip Stocks": ["JPM", "JNJ", "KO", "PG", "WMT", "V", "MA", "DIS"],
        "Indices": ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"],
        "Custom": []
    }
    
    if asset_category == "Custom":
        ticker = st.text_input("Asset Ticker", "BTC-USD")
        analysis_mode = st.radio("Analysis Mode", ["Single Asset", "Multiple Analysis"])
        
        if analysis_mode == "Multiple Analysis":
            custom_tickers = st.text_area(
                "Tickers (comma-separated)", 
                "BTC-USD, ETH-USD, AAPL, TSLA",
                help="Example: BTC-USD, ETH-USD, AAPL, TSLA, GOOGL"
            )
            selected_tickers = [t.strip() for t in custom_tickers.split(",") if t.strip()]
        else:
            selected_tickers = [ticker]
    else:
        analysis_mode = st.radio("Analysis Mode", ["Single Asset", "Multiple Analysis"])
        
        if analysis_mode == "Multiple Analysis":
            selected_tickers = st.multiselect(
                "Select Assets to Analyze", 
                popular_assets[asset_category],
                default=[popular_assets[asset_category][0]]
            )
        else:
            ticker = st.selectbox("Asset", popular_assets[asset_category])
            selected_tickers = [ticker]
    
    analysis_date = st.date_input("Analysis Date", datetime.today())
    
    st.header("🧠 Language Model (LLM)")
    llm_provider = st.selectbox("LLM Provider", ["openai", "google", "anthropic"], index=0)
    deep_think_llm = st.text_input("Main Model (Deep Think)", "gpt-4o")
    quick_think_llm = st.text_input("Quick Model (Quick Think)", "gpt-4o")

    run_analysis = st.button(f"🚀 Analyze { 'Markets' if len(selected_tickers) > 1 else 'Market'}")

# --- Área Principal de la Aplicación ---
if run_analysis:
    if not openai_api_key or not finnhub_api_key:
        st.error("Please enter your OpenAI and Finnhub API keys in the sidebar.")
    else:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_API_BASE"] = openai_api_base
        os.environ["FINNHUB_API_KEY"] = finnhub_api_key
        
        # Function to detect asset type
        def detect_asset_type(ticker):
            if ticker.endswith("-USD") or ticker.endswith("-EUR") or ticker.endswith("-USDT"):
                return "crypto"
            elif ticker in ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"]:
                return "index"
            else:
                return "stock"
        
        # Function to get analysts for asset type
        def get_analysts_for_asset(asset_type):
            if asset_type == "crypto":
                return ["market", "social", "news"]  # No fundamentals for crypto
            elif asset_type == "index":
                return ["market", "news"]  # Indices don't need social or fundamentals
            else:
                return ["market", "social", "news", "fundamentals"]  # Complete for stocks
        
        if len(selected_tickers) == 1:
            # Single analysis
            ticker = selected_tickers[0]
            asset_type = detect_asset_type(ticker)
            
            with st.spinner(f"The agent team is analyzing {ticker} ({asset_type})... This may take a few minutes."):
                try:
                    config = DEFAULT_CONFIG.copy()
                    config["llm_provider"] = llm_provider
                    config["backend_url"] = openai_api_base
                    config["deep_think_llm"] = deep_think_llm
                    config["quick_think_llm"] = quick_think_llm
                    config["online_tools"] = True
                    config["max_debate_rounds"] = 2
                    config["language"] = "english"
                    config["language_instruction"] = "IMPORTANT: Always respond in English. All analyses, reports, and decisions must be in English."

                    # Seleccionar analistas según tipo de activo
                    selected_analysts = get_analysts_for_asset(asset_type)
                    ta = TradingAgentsGraph(debug=False, config=config, selected_analysts=selected_analysts)
                    formatted_date = analysis_date.strftime("%Y-%m-%d")
                    
                    state, decision = ta.propagate(ticker, formatted_date)

                    st.success(f"Analysis completed for {ticker} ({asset_type}).")

                    # --- DEBUG SECTION ---
                    with st.expander("🐞 Debug Output"):
                        st.markdown("**Raw State (`state`):**")
                        st.write(state)
                        st.markdown("**Raw Decision (`decision`):**")
                        st.write(decision)
                    # --- END OF DEBUG SECTION ---

                    st.subheader(f"📈 Final Decision for {ticker}:")
                    if decision:
                        # If the decision is just a string (BUY, SELL, HOLD), display it directly
                        if isinstance(decision, str):
                            decision_color = {
                                "BUY": "green",
                                "SELL": "red", 
                                "HOLD": "orange"
                            }.get(decision.upper(), "blue")
                            st.markdown(f"### :{decision_color}[{decision.upper()}]")
                        else:
                            st.json(decision)
                    else:
                        st.warning("The agent did not produce a final decision.")

                    st.subheader("📄 Detailed Agent Reports:")
                    
                    with st.expander("🔍 Market Technical Analysis"):
                        st.write(state.get("market_report", "No results found."))
                    
                    with st.expander("📱 Social Sentiment Analysis"):
                        st.write(state.get("sentiment_report", "No results found."))
                    
                    with st.expander("📰 News Analysis"):
                        st.write(state.get("news_report", "No results found."))
                    
                    if state.get("fundamentals_report"):
                        with st.expander("📊 Fundamental Analysis"):
                            st.write(state.get("fundamentals_report", "Not available for cryptocurrencies."))

                    with st.expander("⚖️ Researcher Debate (Bull vs Bear)"):
                        investment_debate = state.get("investment_debate_state", {})
                        if investment_debate.get("judge_decision"):
                            st.write(investment_debate["judge_decision"])
                        else:
                            st.write("No debate results found.")
                    
                    with st.expander("💼 Trader's Proposal"):
                         st.write(state.get("trader_investment_plan", "No results found."))

                    with st.expander("🛡️ Risk Management Evaluation"):
                        risk_debate = state.get("risk_debate_state", {})
                        if risk_debate.get("judge_decision"):
                            st.write(risk_debate["judge_decision"])
                        else:
                            st.write("No risk analysis results found.")

                except Exception as e:
                    st.error(f"An error occurred during the analysis: {e}")
        
        else:
            # Multiple analysis
            st.subheader(f"🔄 Multiple Analysis of {len(selected_tickers)} Assets")
            
            results = {}
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(selected_tickers):
                asset_type = detect_asset_type(ticker)
                status_text.text(f"Analyzing {ticker} ({asset_type})... {i+1}/{len(selected_tickers)}")
                
                try:
                    config = DEFAULT_CONFIG.copy()
                    config["llm_provider"] = llm_provider
                    config["backend_url"] = openai_api_base
                    config["deep_think_llm"] = deep_think_llm
                    config["quick_think_llm"] = quick_think_llm
                    config["online_tools"] = True
                    config["max_debate_rounds"] = 1  # Reduce rounds for multiple analysis
                    config["language"] = "english"
                    config["language_instruction"] = "IMPORTANT: Always respond in English. All analyses, reports, and decisions must be in English."

                    # Seleccionar analistas según tipo de activo
                    selected_analysts = get_analysts_for_asset(asset_type)
                    ta = TradingAgentsGraph(debug=False, config=config, selected_analysts=selected_analysts)
                    formatted_date = analysis_date.strftime("%Y-%m-%d")
                    
                    state, decision = ta.propagate(ticker, formatted_date)
                    results[ticker] = {
                        "asset_type": asset_type,
                        "state": state,
                        "decision": decision,
                        "status": "success"
                    }
                    
                except Exception as e:
                    results[ticker] = {
                        "asset_type": asset_type,
                        "error": str(e),
                        "status": "error"
                    }
                
                progress_bar.progress((i + 1) / len(selected_tickers))
            
            status_text.text("Multiple analysis completed!")
            
            # Show summary of results
            st.subheader("📊 Decision Summary")
            
            summary_data = []
            for ticker, result in results.items():
                if result["status"] == "success":
                    decision = result["decision"]
                    if decision and isinstance(decision, dict):
                        action = decision.get("action", "N/A")
                        confidence = decision.get("confidence", "N/A")
                    else:
                        action = "N/A"
                        confidence = "N/A"
                    
                    summary_data.append({
                        "Asset": ticker,
                        "Type": result["asset_type"],
                        "Action": action,
                        "Confidence": confidence,
                        "Status": "✅ Successful"
                    })
                else:
                    summary_data.append({
                        "Asset": ticker,
                        "Type": result["asset_type"],
                        "Action": "Error",
                        "Confidence": "N/A",
                        "Status": "❌ Error"
                    })
            
            st.dataframe(summary_data)
            
            # Show detailed analysis by asset
            st.subheader("📄 Detailed Analysis by Asset")
            
            for ticker, result in results.items():
                with st.expander(f"📈 {ticker} ({result['asset_type']})"):
                    if result["status"] == "success":
                        st.json(result["decision"])
                        
                        st.markdown("**Agent Reports:**")
                        state = result["state"]
                        
                        with st.expander("🔍 Analyst Team Analysis"):
                            st.write(state.get("analyst_team_results", "No results found."))

                        with st.expander("⚖️ Researcher Team Debate"):
                            st.write(state.get("researcher_team_results", "No results found."))
                        
                        with st.expander("💼 Trader Agent Proposal"):
                             st.write(state.get("trader_results", "No results found."))

                        with st.expander("🛡️ Risk Management Team Evaluation"):
                            st.write(state.get("risk_management_results", "No results found."))
                    else:
                        st.error(f"Error analyzing {ticker}: {result['error']}")