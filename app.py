import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Importar los componentes necesarios del framework de trading
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# --- Translation Dictionary ---
translations = {
    "en": {
        "page_title": "AI Trading Agent",
        "title": "🤖 AI Trading Agent for Financial Assets",
        "description": "This application uses a team of AI agents to analyze the asset market and propose a trading decision. Enter your API keys and analysis parameters to get started.",
        "api_config_header": "🔑 API Configuration",
        "openai_api_key": "OpenAI API Key",
        "openai_api_base": "OpenAI API Base URL",
        "finnhub_api_key": "Finnhub API Key",
        "agent_params_header": "⚙️ Agent Parameters",
        "asset_category": "Asset Category",
        "categories": ["Cryptocurrencies", "Tech Stocks", "Blue Chip Stocks", "Indices", "Custom"],
        "asset_ticker": "Asset Ticker",
        "analysis_mode": "Analysis Mode",
        "single_asset": "Single Asset",
        "multiple_analysis": "Multiple Analysis",
        "tickers_comma_separated": "Tickers (comma-separated)",
        "tickers_help": "Example: BTC-USD, ETH-USD, AAPL, TSLA, GOOGL",
        "select_assets": "Select Assets to Analyze",
        "asset": "Asset",
        "analysis_date": "Analysis Date",
        "llm_header": "🧠 Language Model (LLM)",
        "llm_provider": "LLM Provider",
        "main_model": "Main Model (Deep Think)",
        "quick_model": "Quick Model (Quick Think)",
        "analyze_market": "Analyze Market",
        "analyze_markets": "Analyze Markets",
        "error_api_keys": "Please enter your OpenAI and Finnhub API keys in the sidebar.",
        "spinner_analyzing": "The agent team is analyzing {ticker} ({asset_type})... This may take a few minutes.",
        "analysis_completed": "Analysis completed for {ticker} ({asset_type}).",
        "debug_output": "🐞 Debug Output",
        "raw_state": "**Raw State (`state`):**",
        "raw_decision": "**Raw Decision (`decision`):**",
        "final_decision": "📈 Final Decision for {ticker}:",
        "no_decision": "The agent did not produce a final decision.",
        "detailed_reports": "📄 Detailed Agent Reports:",
        "market_analysis": "🔍 Market Technical Analysis",
        "social_analysis": "📱 Social Sentiment Analysis",
        "news_analysis": "📰 News Analysis",
        "fundamentals_analysis": "📊 Fundamental Analysis",
        "whale_order_analysis": "🐳 Whale Order Analysis",
        "fundamentals_na": "Not available for cryptocurrencies.",
        "researcher_debate": "⚖️ Researcher Debate (Bull vs Bear)",
        "trader_proposal": "💼 Trader's Proposal",
        "risk_evaluation": "🛡️ Risk Management Evaluation",
        "no_results": "No results found.",
        "error_analysis": "An error occurred during the analysis: {e}",
        "multiple_analysis_header": "🔄 Multiple Analysis of {num_assets} Assets",
        "status_analyzing": "Analyzing {ticker} ({asset_type})... {i}/{total}",
        "multiple_analysis_completed": "Multiple analysis completed!",
        "decision_summary": "📊 Decision Summary",
        "summary_asset": "Asset",
        "summary_type": "Type",
        "summary_action": "Action",
        "summary_confidence": "Confidence",
        "summary_status": "Status",
        "summary_successful": "✅ Successful",
        "summary_error": "❌ Error",
        "detailed_analysis_by_asset": "📄 Detailed Analysis by Asset",
        "agent_reports": "**Agent Reports:**",
        "analyst_team_analysis": "🔍 Analyst Team Analysis",
        "researcher_team_debate": "⚖️ Researcher Team Debate",
        "trader_agent_proposal": "💼 Trader Agent Proposal",
        "risk_management_team_evaluation": "🛡️ Risk Management Team Evaluation",
        "error_analyzing_ticker": "Error analyzing {ticker}: {error}"
    },
    "zh": {
        "page_title": "AI 交易代理",
        "title": "🤖 AI 金融资产交易代理",
        "description": "本应用程序使用一组 AI 代理来分析资产市场并提出交易决策。请输入您的 API 密钥和分析参数以开始。",
        "api_config_header": "🔑 API 配置",
        "openai_api_key": "OpenAI API 密钥",
        "openai_api_base": "OpenAI API 基础 URL",
        "finnhub_api_key": "Finnhub API 密钥",
        "agent_params_header": "⚙️ 代理参数",
        "asset_category": "资产类别",
        "categories": ["加密货币", "科技股", "蓝筹股", "指数", "自定义"],
        "asset_ticker": "资产代码",
        "analysis_mode": "分析模式",
        "single_asset": "单个资产",
        "multiple_analysis": "多个资产",
        "tickers_comma_separated": "代码（以逗号分隔）",
        "tickers_help": "例如：BTC-USD, ETH-USD, AAPL, TSLA, GOOGL",
        "select_assets": "选择要分析的资产",
        "asset": "资产",
        "analysis_date": "分析日期",
        "llm_header": "🧠 语言模型 (LLM)",
        "llm_provider": "LLM 提供商",
        "main_model": "主模型 (深度思考)",
        "quick_model": "快速模型 (快速思考)",
        "analyze_market": "分析市场",
        "analyze_markets": "分析多个市场",
        "error_api_keys": "请在侧边栏输入您的 OpenAI 和 Finnhub API 密钥。",
        "spinner_analyzing": "代理团队正在分析 {ticker} ({asset_type})... 这可能需要几分钟。",
        "analysis_completed": "已完成对 {ticker} ({asset_type}) 的分析。",
        "debug_output": "🐞 调试输出",
        "raw_state": "**原始状态 (`state`):**",
        "raw_decision": "**原始决策 (`decision`):**",
        "final_decision": "📈 {ticker} 的最终决策：",
        "no_decision": "代理未能做出最终决策。",
        "detailed_reports": "📄 详细代理报告：",
        "market_analysis": "🔍 市场技术分析",
        "social_analysis": "📱 社交情绪分析",
        "news_analysis": "📰 新闻分析",
        "fundamentals_analysis": "📊 基本面分析",
        "whale_order_analysis": "🐳 巨鲸订单分析",
        "fundamentals_na": "不适用于加密货币。",
        "researcher_debate": "⚖️ 研究员辩论 (牛市 vs 熊市)",
        "trader_proposal": "💼 交易员提案",
        "risk_evaluation": "🛡️ 风险管理评估",
        "no_results": "未找到结果。",
        "error_analysis": "分析过程中发生错误: {e}",
        "multiple_analysis_header": "🔄 对 {num_assets} 个资产进行多重分析",
        "status_analyzing": "正在分析 {ticker} ({asset_type})... {i}/{total}",
        "multiple_analysis_completed": "多重分析已完成！",
        "decision_summary": "📊 决策摘要",
        "summary_asset": "资产",
        "summary_type": "类型",
        "summary_action": "操作",
        "summary_confidence": "置信度",
        "summary_status": "状态",
        "summary_successful": "✅ 成功",
        "summary_error": "❌ 错误",
        "detailed_analysis_by_asset": "📄 按资产分的详细分析",
        "agent_reports": "**代理报告:**",
        "analyst_team_analysis": "🔍 分析师团队分析",
        "researcher_team_debate": "⚖️ 研究员团队辩论",
        "trader_agent_proposal": "💼 交易代理提案",
        "risk_management_team_evaluation": "🛡️ 风险管理团队评估",
        "error_analyzing_ticker": "分析 {ticker} 时出错: {error}"
    }
}

# --- Language Selection ---
st.sidebar.image("assets/logo.png", use_container_width=True)
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

lang_options = {'en': 'English', 'zh': '中文'}
selected_lang = st.sidebar.selectbox(
    "Language / 语言",
    options=list(lang_options.keys()),
    format_func=lambda x: lang_options[x],
    index=list(lang_options.keys()).index(st.session_state.lang)
)
st.session_state.lang = selected_lang
T = translations[st.session_state.lang]

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title=T["page_title"],
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加 CSS 样式来限制 Analysis Log 的高度
st.markdown("""
<style>
/* 限制 Analysis Log 的最大高度为页面一半 */
div[data-testid="stExpander"] > details > div {
    max-height: 50vh !important;
    overflow-y: auto !important;
    scroll-behavior: smooth !important;
}

/* 隐藏自动滚动iframe的容器 */
.scroll-trigger {
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# 创建一个全局的自动滚动控制占位符，用于存放iframe
if 'scroll_placeholder' not in st.session_state:
    st.session_state.scroll_placeholder = st.empty()


# 添加自动滚动组件（每次都生成新的iframe）
def update_auto_scroll():
    import time
    # 生成时间戳，确保每次更新iframe都是唯一的
    timestamp = int(time.time() * 1000)

    # 使用session_state中的占位符更新自动滚动脚本
    st.session_state.scroll_placeholder.markdown(
        f"""
        <div class="scroll-trigger">
        <iframe srcdoc="
        <script>
            // 使用时间戳：{timestamp}，确保脚本每次都执行
            console.log('Auto-scroll triggered at {timestamp}');
            // 等待父窗口中的元素加载完成
            setTimeout(function() {{
                // 查找所有Analysis Log容器并滚动到底部
                var expanders = window.parent.document.querySelectorAll('div[data-testid=\\'stExpander\\'] > details > div');
                for (var i = 0; i < expanders.length; i++) {{
                    expanders[i].scrollTop = expanders[i].scrollHeight;
                    console.log('Scrolling container ' + i + ' to ' + expanders[i].scrollHeight);
                }}
            }}, 200);
        </script>
        " height="0" width="0" frameborder="0"></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )


# 添加函数：将Yahoo Finance格式的加密货币符号转换为Binance格式
def convert_crypto_symbol(symbol):
    """
    将Yahoo Finance格式的加密货币符号转换为Binance格式
    例如: BTC-USD -> BTC/USDT
    """
    if symbol.endswith('-USD'):
        base_currency = symbol[:-4]  # 移除'-USD'后缀
        return f"{base_currency}/USDT"
    return symbol


# 从环境变量获取默认的最小订单金额阈值，默认为100000
DEFAULT_MIN_AMOUNT = int(os.getenv('BINANCE_MIN_ORDER_AMOUNT', 100000))


# 添加函数：为加密货币启动后台追踪线程
def start_crypto_tracking_threads(crypto_assets, min_amount=DEFAULT_MIN_AMOUNT, interval=60):
    """
    为加密货币资产启动后台追踪线程
    
    Args:
        crypto_assets (list): 加密货币资产列表，如 ['BTC-USD', 'ETH-USD']
        min_amount (int): 最小订单金额阈值
        interval (int): 检查间隔（秒）
    """
    from tradingagents.dataflows.binance_utils import start_tracker_thread

    # 使用st.session_state跟踪已启动的线程，避免重复启动
    if 'tracking_threads' not in st.session_state:
        st.session_state.tracking_threads = set()

    for asset in crypto_assets:
        # 转换符号格式
        binance_symbol = convert_crypto_symbol(asset)

        # 检查是否已经为该资产启动了线程
        if binance_symbol not in st.session_state.tracking_threads:
            # 启动追踪线程
            start_tracker_thread(binance_symbol, min_amount, interval)
            st.session_state.tracking_threads.add(binance_symbol)
            # st.info(f"已为 {asset} ({binance_symbol}) 启动后台数据收集线程")


@st.cache_resource
def start_crypto_tracking_once(crypto_assets):
    """
    使用 st.cache_resource 确保追踪线程只启动一次。
    """
    start_crypto_tracking_threads(crypto_assets)
    return True


st.title(T["title"])
st.markdown(T["description"])

# --- Configuration Sidebar ---
with st.sidebar:
    st.header(T["api_config_header"])
    if os.path.exists('.env'):
        load_dotenv()

    openai_api_key = st.text_input(T["openai_api_key"], type="password", value=os.getenv("OPENAI_API_KEY") or "")
    openai_api_base = st.text_input(T["openai_api_base"],
                                    value=os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1")
    finnhub_api_key = st.text_input(T["finnhub_api_key"], type="password", value=os.getenv("FINNHUB_API_KEY") or "")

    st.header(T["agent_params_header"])

    # Asset category and selection
    asset_category = st.selectbox(
        T["asset_category"],
        T["categories"]
    )

    # Define popular assets by category
    popular_assets = {
        "Cryptocurrencies": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "MATIC-USD", "DOT-USD", "AVAX-USD",
                             "LINK-USD"],
        "Tech Stocks": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META", "AMZN", "NFLX"],
        "Blue Chip Stocks": ["JPM", "JNJ", "KO", "PG", "WMT", "V", "MA", "DIS"],
        "Indices": ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"],
        "Custom": []
    }

    # Map categories for display
    category_map = {
        "Cryptocurrencies": "Cryptocurrencies",
        "Tech Stocks": "Tech Stocks",
        "Blue Chip Stocks": "Blue Chip Stocks",
        "Indices": "Indices",
        "Custom": "Custom"
    }
    if st.session_state.lang == 'zh':
        category_map = {
            "加密货币": "Cryptocurrencies",
            "科技股": "Tech Stocks",
            "蓝筹股": "Blue Chip Stocks",
            "指数": "Indices",
            "自定义": "Custom"
        }

    internal_category = category_map[asset_category]

    # 如果是加密货币类别，为所有popular_assets中的加密货币启动追踪线程
    # 使用 st.cache_resource 确保只在应用启动时启动一次
    if internal_category == "Cryptocurrencies":
        start_crypto_tracking_once(popular_assets[internal_category])

    if internal_category == "Custom":
        ticker = st.text_input(T["asset_ticker"], "BTC-USD")
        analysis_mode = st.radio(T["analysis_mode"], [T["single_asset"], T["multiple_analysis"]])

        if analysis_mode == T["multiple_analysis"]:
            custom_tickers = st.text_area(
                T["tickers_comma_separated"],
                "BTC-USD, ETH-USD, AAPL, TSLA",
                help=T["tickers_help"]
            )
            selected_tickers = [t.strip() for t in custom_tickers.split(",") if t.strip()]
        else:
            selected_tickers = [ticker]
    else:
        analysis_mode = st.radio(T["analysis_mode"], [T["single_asset"], T["multiple_analysis"]])

        if analysis_mode == T["multiple_analysis"]:
            selected_tickers = st.multiselect(
                T["select_assets"],
                popular_assets[internal_category],
                default=[popular_assets[internal_category][0]]
            )
        else:
            ticker = st.selectbox(T["asset"], popular_assets[internal_category])
            selected_tickers = [ticker]

    analysis_date = st.date_input(T["analysis_date"], datetime.today())

    st.header(T["llm_header"])
    llm_provider = st.selectbox(T["llm_provider"], ["openai", "google", "anthropic"], index=0)
    deep_think_llm = st.text_input(T["main_model"], "gpt-4o")
    quick_think_llm = st.text_input(T["quick_model"], "gpt-4o")

    button_text = f"🚀 {T['analyze_markets'] if len(selected_tickers) > 1 else T['analyze_market']}"
    run_analysis = st.button(button_text)

# --- Main Application Area ---
if run_analysis:
    if not openai_api_key or not finnhub_api_key:
        st.error(T["error_api_keys"])
    else:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_API_BASE"] = openai_api_base
        os.environ["FINNHUB_API_KEY"] = finnhub_api_key


        def detect_asset_type(ticker):
            if ticker.endswith("-USD") or ticker.endswith("-EUR") or ticker.endswith("-USDT"):
                return "crypto"
            elif ticker in ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"]:
                return "index"
            else:
                return "stock"


        def get_analysts_for_asset(asset_type):
            if asset_type == "crypto":
                return ["whale", "market", "social", "news"]
            elif asset_type == "index":
                return ["market", "news"]
            else:
                return ["market", "social", "news", "fundamentals"]


        # Setup config based on language
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = llm_provider
        config["backend_url"] = openai_api_base
        config["deep_think_llm"] = deep_think_llm
        config["quick_think_llm"] = quick_think_llm
        config["online_tools"] = True

        if st.session_state.lang == 'zh':
            config["language"] = "chinese"
            config["language_instruction"] = "重要：请始终使用中文回答。所有分析、报告和决策都必须是中文。"
        else:
            config["language"] = "english"
            config[
                "language_instruction"] = "IMPORTANT: Always respond in English. All analyses, reports, and decisions must be in English."

        if len(selected_tickers) == 1:
            ticker = selected_tickers[0]
            asset_type = detect_asset_type(ticker)

            st.subheader(f"{T['analyze_market']}: {ticker} ({asset_type})")

            # 创建一个占位符用于放置日志expander
            log_placeholder = st.empty()
            log_expander = log_placeholder.expander("Analysis Log", expanded=True)

            # 用于存储日志消息的列表
            if 'log_messages' not in st.session_state:
                st.session_state.log_messages = []


            def log_to_streamlit(message):
                # 添加消息到列表
                st.session_state.log_messages.append(message)
                # 清空expander并重新添加所有消息
                log_expander.empty()
                for msg in st.session_state.log_messages:
                    log_expander.markdown(msg, unsafe_allow_html=True)
                # 触发自动滚动（使用全局占位符，但每次都生成新iframe）
                update_auto_scroll()


            spinner_text = T["spinner_analyzing"].format(ticker=ticker, asset_type=asset_type)
            with st.spinner(spinner_text):
                try:
                    single_analysis_config = config.copy()
                    single_analysis_config["max_debate_rounds"] = 2

                    selected_analysts = get_analysts_for_asset(asset_type)
                    ta = TradingAgentsGraph(
                        debug=False,
                        config=single_analysis_config,
                        selected_analysts=selected_analysts,
                        log_callback=log_to_streamlit,
                        language=st.session_state.lang
                    )
                    formatted_date = analysis_date.strftime("%Y-%m-%d")

                    state, decision = ta.propagate(ticker, formatted_date)

                    # 分析完成后，重新创建日志expander，但默认收起
                    # 替换占位符中的expander为收起状态
                    log_placeholder.empty()
                    log_expander = log_placeholder.expander("Analysis Log", expanded=False)
                    for msg in st.session_state.log_messages:
                        log_expander.write(msg)
                    # 触发一次自动滚动，确保日志显示在底部
                    update_auto_scroll()

                    st.success(T["analysis_completed"].format(ticker=ticker, asset_type=asset_type))

                    with st.expander(T["debug_output"]):
                        st.markdown(T["raw_state"])
                        st.write(state)
                        st.markdown(T["raw_decision"])
                        st.write(decision)

                    st.subheader(T["final_decision"].format(ticker=ticker))
                    if decision:
                        if isinstance(decision, str):
                            decision_color = {"BUY": "green", "SELL": "red", "HOLD": "orange"}.get(decision.upper(),
                                                                                                   "blue")
                            st.markdown(f"### :{decision_color}[{decision.upper()}]")
                        else:
                            st.json(decision)
                    else:
                        st.warning(T["no_decision"])

                    st.subheader(T["detailed_reports"])

                    with st.expander(T["market_analysis"]):
                        st.write(state.get("market_report", T["no_results"]))

                    with st.expander(T["social_analysis"]):
                        st.write(state.get("sentiment_report", T["no_results"]))

                    with st.expander(T["news_analysis"]):
                        st.write(state.get("news_report", T["no_results"]))

                    if state.get("fundamentals_report"):
                        with st.expander(T["fundamentals_analysis"]):
                            st.write(state.get("fundamentals_report", T["fundamentals_na"]))

                    if state.get("whale_report"):
                        with st.expander("🐳 Whale Order Analysis"):
                            st.markdown(state.get("whale_report"), unsafe_allow_html=True)

                    with st.expander(T["researcher_debate"]):
                        investment_debate = state.get("investment_debate_state", {})
                        st.write(investment_debate.get("judge_decision", T["no_results"]))

                    with st.expander(T["trader_proposal"]):
                        st.write(state.get("trader_investment_plan", T["no_results"]))

                    with st.expander(T["risk_evaluation"]):
                        risk_debate = state.get("risk_debate_state", {})
                        st.write(risk_debate.get("judge_decision", T["no_results"]))
                except Exception as e:
                    st.error(T["error_analysis"].format(e=e))

        else:
            st.subheader(T["multiple_analysis_header"].format(num_assets=len(selected_tickers)))

            results = {}
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 创建一个占位符用于放置日志expander
            log_placeholder = st.empty()
            log_expander = log_placeholder.expander("Analysis Log", expanded=True)

            # 重置日志消息列表
            st.session_state.log_messages = []


            def log_to_streamlit(message):
                # 添加消息到列表
                st.session_state.log_messages.append(message)
                # 清空expander并重新添加所有消息
                log_expander.empty()
                for msg in st.session_state.log_messages:
                    log_expander.markdown(msg, unsafe_allow_html=True)
                # 触发自动滚动（使用全局占位符，但每次都生成新iframe）
                update_auto_scroll()


            multi_analysis_config = config.copy()
            multi_analysis_config["max_debate_rounds"] = 1

            for i, ticker in enumerate(selected_tickers):
                asset_type = detect_asset_type(ticker)
                status_text.info(T["status_analyzing"].format(ticker=ticker, asset_type=asset_type, i=i + 1,
                                                              total=len(selected_tickers)))
                log_expander.write(f"--- Starting analysis for {ticker} ---")

                try:
                    selected_analysts = get_analysts_for_asset(asset_type)
                    ta = TradingAgentsGraph(
                        debug=False,
                        config=multi_analysis_config,
                        selected_analysts=selected_analysts,
                        log_callback=log_to_streamlit,
                        language=st.session_state.lang
                    )
                    formatted_date = analysis_date.strftime("%Y-%m-%d")

                    state, decision = ta.propagate(ticker, formatted_date)
                    results[ticker] = {"asset_type": asset_type, "state": state, "decision": decision,
                                       "status": "success"}
                    log_expander.write(f"--- Finished analysis for {ticker} ---")

                except Exception as e:
                    results[ticker] = {"asset_type": asset_type, "error": str(e), "status": "error"}
                    log_expander.write(f"--- Error analyzing {ticker} ---")

                progress_bar.progress((i + 1) / len(selected_tickers))

            # 多资产分析完成后，重新创建日志expander，但默认收起
            # 替换占位符中的expander为收起状态
            log_placeholder.empty()
            log_expander = log_placeholder.expander("Analysis Log", expanded=False)
            for msg in st.session_state.log_messages:
                log_expander.write(msg)
            # 触发一次自动滚动，确保日志显示在底部
            update_auto_scroll()

            status_text.empty()
            st.success(T["multiple_analysis_completed"])

            st.subheader(T["decision_summary"])

            summary_data = []
            for ticker, result in results.items():
                if result["status"] == "success":
                    decision = result["decision"]
                    action = decision.get("action", "N/A") if isinstance(decision, dict) else "N/A"
                    confidence = decision.get("confidence", "N/A") if isinstance(decision, dict) else "N/A"
                    summary_data.append({
                        T["summary_asset"]: ticker, T["summary_type"]: result["asset_type"],
                        T["summary_action"]: action, T["summary_confidence"]: confidence,
                        T["summary_status"]: T["summary_successful"]
                    })
                else:
                    summary_data.append({
                        T["summary_asset"]: ticker, T["summary_type"]: result["asset_type"],
                        T["summary_action"]: "Error", T["summary_confidence"]: "N/A",
                        T["summary_status"]: T["summary_error"]
                    })

            st.dataframe(summary_data)

            st.subheader(T["detailed_analysis_by_asset"])

            for ticker, result in results.items():
                with st.expander(f"📈 {ticker} ({result.get('asset_type', 'N/A')})"):
                    if result.get("status") == "success":
                        decision = result.get("decision")
                        state = result.get("state", {})

                        # Display final decision (similar to single asset mode)
                        st.subheader(T["final_decision"].format(ticker=ticker))
                        if decision:
                            if isinstance(decision, str):
                                decision_color = {"BUY": "green", "SELL": "red", "HOLD": "orange"}.get(decision.upper(),
                                                                                                       "blue")
                                st.markdown(f"### :{decision_color}[{decision.upper()}]")
                            elif isinstance(decision, dict):
                                st.json(decision)
                            else:
                                st.write(decision)
                        else:
                            st.warning(T["no_decision"])

                        # Display detailed reports (similar to single asset mode)
                        st.subheader(T["detailed_reports"])

                        with st.expander(T["market_analysis"]):
                            st.write(state.get("market_report", T["no_results"]))

                        with st.expander(T["social_analysis"]):
                            st.write(state.get("sentiment_report", T["no_results"]))

                        with st.expander(T["news_analysis"]):
                            st.write(state.get("news_report", T["no_results"]))

                        if state.get("fundamentals_report"):
                            with st.expander(T["fundamentals_analysis"]):
                                st.write(state.get("fundamentals_report", T["fundamentals_na"]))

                        if state.get("whale_report"):
                            with st.expander("🐳 Whale Order Analysis"):
                                st.markdown(state.get("whale_report"), unsafe_allow_html=True)

                        with st.expander(T["researcher_debate"]):
                            investment_debate = state.get("investment_debate_state", {})
                            st.write(investment_debate.get("judge_decision", T["no_results"]))

                        with st.expander(T["trader_proposal"]):
                            st.write(state.get("trader_investment_plan", T["no_results"]))

                        with st.expander(T["risk_evaluation"]):
                            risk_debate = state.get("risk_debate_state", {})
                            st.write(risk_debate.get("judge_decision", T["no_results"]))
                    else:
                        st.error(T["error_analyzing_ticker"].format(ticker=ticker,
                                                                    error=result.get('error', 'Unknown error')))
