import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Importar los componentes necesarios del framework de trading
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="Agente de Trading con IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Agente de Trading con IA para Activos Financieros")
st.markdown("Esta aplicación utiliza un equipo de agentes de IA para analizar el mercado de Activos y proponer una decisión de trading. Introduce tus claves de API y los parámetros de análisis para comenzar.")

# --- Barra Lateral de Configuración ---
with st.sidebar:
    st.header("🔑 Configuración de APIs")
    if os.path.exists('.env'):
        load_dotenv()

    openai_api_key = st.text_input("Clave API de OpenAI", type="password", value=os.getenv("OPENAI_API_KEY") or "")
    openai_api_base = st.text_input("URL base de la API de OpenAI", value=os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1")
    finnhub_api_key = st.text_input("Clave API de Finnhub", type="password", value=os.getenv("FINNHUB_API_KEY") or "")
    
    st.header("⚙️ Parámetros del Agente")
    
    # Selección de categoría y activos
    asset_category = st.selectbox(
        "Categoría de Activos", 
        ["Criptomonedas", "Acciones Tech", "Acciones Blue Chip", "Índices", "Personalizado"]
    )
    
    # Definir activos populares por categoría
    popular_assets = {
        "Criptomonedas": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "MATIC-USD", "DOT-USD", "AVAX-USD", "LINK-USD"],
        "Acciones Tech": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META", "AMZN", "NFLX"],
        "Acciones Blue Chip": ["JPM", "JNJ", "KO", "PG", "WMT", "V", "MA", "DIS"],
        "Índices": ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"],
        "Personalizado": []
    }
    
    if asset_category == "Personalizado":
        ticker = st.text_input("Ticker del Activo", "BTC-USD")
        analysis_mode = st.radio("Modo de Análisis", ["Activo Individual", "Análisis Múltiple"])
        
        if analysis_mode == "Análisis Múltiple":
            custom_tickers = st.text_area(
                "Tickers (separados por coma)", 
                "BTC-USD, ETH-USD, AAPL, TSLA",
                help="Ejemplo: BTC-USD, ETH-USD, AAPL, TSLA, GOOGL"
            )
            selected_tickers = [t.strip() for t in custom_tickers.split(",") if t.strip()]
        else:
            selected_tickers = [ticker]
    else:
        analysis_mode = st.radio("Modo de Análisis", ["Activo Individual", "Análisis Múltiple"])
        
        if analysis_mode == "Análisis Múltiple":
            selected_tickers = st.multiselect(
                "Selecciona Activos para Analizar", 
                popular_assets[asset_category],
                default=[popular_assets[asset_category][0]]
            )
        else:
            ticker = st.selectbox("Activo", popular_assets[asset_category])
            selected_tickers = [ticker]
    
    analysis_date = st.date_input("Fecha de Análisis", datetime.today())
    
    st.header("🧠 Modelo de Lenguaje (LLM)")
    llm_provider = st.selectbox("Proveedor de LLM", ["openai", "google", "anthropic"], index=0)
    deep_think_llm = st.text_input("Modelo Principal (Deep Think)", "gpt-4o")
    quick_think_llm = st.text_input("Modelo Rápido (Quick Think)", "gpt-4o")

    run_analysis = st.button(f"🚀 Analizar {'Mercados' if len(selected_tickers) > 1 else 'Mercado'}")

# --- Área Principal de la Aplicación ---
if run_analysis:
    if not openai_api_key or not finnhub_api_key:
        st.error("Por favor, introduce tus claves de API de OpenAI y Finnhub en la barra lateral.")
    else:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_API_BASE"] = openai_api_base
        os.environ["FINNHUB_API_KEY"] = finnhub_api_key
        
        # Función para detectar tipo de activo
        def detect_asset_type(ticker):
            if ticker.endswith("-USD") or ticker.endswith("-EUR") or ticker.endswith("-USDT"):
                return "crypto"
            elif ticker in ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"]:
                return "index"
            else:
                return "stock"
        
        # Función para obtener analistas según tipo de activo
        def get_analysts_for_asset(asset_type):
            if asset_type == "crypto":
                return ["market", "social", "news"]  # Sin fundamentals para crypto
            elif asset_type == "index":
                return ["market", "news"]  # Índices no necesitan social ni fundamentals
            else:
                return ["market", "social", "news", "fundamentals"]  # Completo para acciones
        
        if len(selected_tickers) == 1:
            # Análisis individual
            ticker = selected_tickers[0]
            asset_type = detect_asset_type(ticker)
            
            with st.spinner(f"El equipo de agentes está analizando {ticker} ({asset_type})... Esto puede tardar unos minutos."):
                try:
                    config = DEFAULT_CONFIG.copy()
                    config["llm_provider"] = llm_provider
                    config["backend_url"] = openai_api_base
                    config["deep_think_llm"] = deep_think_llm
                    config["quick_think_llm"] = quick_think_llm
                    config["online_tools"] = True
                    config["max_debate_rounds"] = 2
                    config["language"] = "spanish"
                    config["language_instruction"] = "IMPORTANTE: Responde SIEMPRE en español. Todos los análisis, reportes y decisiones deben estar en español."

                    # Seleccionar analistas según tipo de activo
                    selected_analysts = get_analysts_for_asset(asset_type)
                    ta = TradingAgentsGraph(debug=False, config=config, selected_analysts=selected_analysts)
                    formatted_date = analysis_date.strftime("%Y-%m-%d")
                    
                    state, decision = ta.propagate(ticker, formatted_date)

                    st.success(f"Análisis completado para {ticker} ({asset_type}).")

                    # --- SECCIÓN DE DEPURACIÓN ---
                    with st.expander("🐞 Salida de Depuración"):
                        st.markdown("**Estado Crudo (`state`):**")
                        st.write(state)
                        st.markdown("**Decisión Cruda (`decision`):**")
                        st.write(decision)
                    # --- FIN DE LA SECCIÓN DE DEPURACIÓN ---

                    st.subheader(f"📈 Decisión Final para {ticker}:")
                    if decision:
                        # Si la decisión es solo un string (BUY, SELL, HOLD), mostrarla directamente
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
                        st.warning("El agente no produjo una decisión final.")

                    st.subheader("📄 Informes Detallados de los Agentes:")
                    
                    with st.expander("🔍 Análisis Técnico de Mercado"):
                        st.write(state.get("market_report", "No se encontraron resultados."))
                    
                    with st.expander("📱 Análisis de Sentimiento Social"):
                        st.write(state.get("sentiment_report", "No se encontraron resultados."))
                    
                    with st.expander("📰 Análisis de Noticias"):
                        st.write(state.get("news_report", "No se encontraron resultados."))
                    
                    if state.get("fundamentals_report"):
                        with st.expander("📊 Análisis Fundamental"):
                            st.write(state.get("fundamentals_report", "No disponible para criptomonedas."))

                    with st.expander("⚖️ Debate de Investigadores (Bull vs Bear)"):
                        investment_debate = state.get("investment_debate_state", {})
                        if investment_debate.get("judge_decision"):
                            st.write(investment_debate["judge_decision"])
                        else:
                            st.write("No se encontraron resultados del debate.")
                    
                    with st.expander("💼 Propuesta del Trader"):
                         st.write(state.get("trader_investment_plan", "No se encontraron resultados."))

                    with st.expander("🛡️ Evaluación de Gestión de Riesgos"):
                        risk_debate = state.get("risk_debate_state", {})
                        if risk_debate.get("judge_decision"):
                            st.write(risk_debate["judge_decision"])
                        else:
                            st.write("No se encontraron resultados del análisis de riesgos.")

                except Exception as e:
                    st.error(f"Ha ocurrido un error durante el análisis: {e}")
        
        else:
            # Análisis múltiple
            st.subheader(f"🔄 Análisis Múltiple de {len(selected_tickers)} Activos")
            
            results = {}
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(selected_tickers):
                asset_type = detect_asset_type(ticker)
                status_text.text(f"Analizando {ticker} ({asset_type})... {i+1}/{len(selected_tickers)}")
                
                try:
                    config = DEFAULT_CONFIG.copy()
                    config["llm_provider"] = llm_provider
                    config["backend_url"] = openai_api_base
                    config["deep_think_llm"] = deep_think_llm
                    config["quick_think_llm"] = quick_think_llm
                    config["online_tools"] = True
                    config["max_debate_rounds"] = 1  # Reducir rounds para análisis múltiple
                    config["language"] = "spanish"
                    config["language_instruction"] = "IMPORTANTE: Responde SIEMPRE en español. Todos los análisis, reportes y decisiones deben estar en español."

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
            
            status_text.text("¡Análisis múltiple completado!")
            
            # Mostrar resumen de resultados
            st.subheader("📊 Resumen de Decisiones")
            
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
                        "Activo": ticker,
                        "Tipo": result["asset_type"],
                        "Acción": action,
                        "Confianza": confidence,
                        "Estado": "✅ Exitoso"
                    })
                else:
                    summary_data.append({
                        "Activo": ticker,
                        "Tipo": result["asset_type"],
                        "Acción": "Error",
                        "Confianza": "N/A",
                        "Estado": "❌ Error"
                    })
            
            st.dataframe(summary_data)
            
            # Mostrar análisis detallado por activo
            st.subheader("📄 Análisis Detallado por Activo")
            
            for ticker, result in results.items():
                with st.expander(f"📈 {ticker} ({result['asset_type']})"):
                    if result["status"] == "success":
                        st.json(result["decision"])
                        
                        st.markdown("**Informes de Agentes:**")
                        state = result["state"]
                        
                        with st.expander("🔍 Análisis del Equipo de Analistas"):
                            st.write(state.get("analyst_team_results", "No se encontraron resultados."))

                        with st.expander("⚖️ Debate del Equipo de Investigadores"):
                            st.write(state.get("researcher_team_results", "No se encontraron resultados."))
                        
                        with st.expander("💼 Propuesta del Agente Trader"):
                             st.write(state.get("trader_results", "No se encontraron resultados."))

                        with st.expander("🛡️ Evaluación del Equipo de Gestión de Riesgos"):
                            st.write(state.get("risk_management_results", "No se encontraron resultados."))
                    else:
                        st.error(f"Error al analizar {ticker}: {result['error']}")