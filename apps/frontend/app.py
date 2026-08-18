"""
Meu Copiloto Financeiro - Financial Portfolio Dashboard
Main application entry point with clean modular architecture

Modular structure:
- src/styles.py: CSS theming
- src/data.py: Client and market data
- src/utils.py: Technical indicators and formatting
- src/components.py: Reusable UI components
- src/portfolio.py: Portfolio table component
"""

import streamlit as st
import pandas as pd

# Import modular components
from src.styles import inject_theme
from src.data import CLIENTS, SECTOR_BY_TICKER
from src.utils import get_market_data, add_indicators, assess_recommendation, format_money, get_fundamentals
from src.components import (
    render_sidebar,
    create_stock_analysis_dialog,
    create_recommendation_dialog,
    render_sector_allocation,
    render_ranking_cards,
    render_news_section,
    render_chat_section,
    render_footer,
)
from src.portfolio import render_portfolio_table


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(page_title="Meu Copiloto Financeiro", page_icon="📈", layout="wide")
inject_theme()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "selected_client" not in st.session_state:
    st.session_state.selected_client = "Marcio"
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "PETR4.SA"
if "selected_view" not in st.session_state:
    st.session_state.selected_view = "candles"
if "show_dialog" not in st.session_state:
    st.session_state.show_dialog = False
if "show_recommendation_dialog" not in st.session_state:
    st.session_state.show_recommendation_dialog = False
# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_portfolio_value(client_name: str) -> float:
    """Calculate total portfolio value in BRL"""
    portfolio = CLIENTS[client_name]["portfolio"]
    portfolio_value = 0.0
    for item in portfolio:
        market = get_market_data(item["ticker"], "6mo")
        last_price = float(market["Close"].iloc[-1])
        portfolio_value += last_price * item["quantidade"]
    return portfolio_value


def prepare_portfolio_dataframe(portfolio: list) -> pd.DataFrame:
    """Prepare and enrich portfolio data with market information"""
    portfolio_rows = []
    
    # Get current profile for recommendations
    profile = CLIENTS[st.session_state.selected_client]["perfil"]
    
    for item in portfolio:
        item_symbol = item["ticker"]
        item_market = add_indicators(get_market_data(item_symbol, "6mo"))
        item_price = float(item_market["Close"].iloc[-1])

        variation = ((item_price - item["preco_medio"]) / item["preco_medio"]) * 100
        rec, badge = assess_recommendation(item_market, profile)
        fund = get_fundamentals(item_symbol)

        portfolio_rows.append({
            "ticker": item_symbol,
            "quantidade": item["quantidade"],
            "preco_medio": item["preco_medio"],
            "preco_teto": item["preco_teto"],
            "preco_atual": item_price,
            "valor_total": item_price * item["quantidade"],
            "variacao_pct": variation,
            "recomendacao": rec,
            "badge": badge,
            "p_vp": fund["p_vp"],
            "dy": fund["dy"],
        })

    portfolio_df = pd.DataFrame(portfolio_rows).sort_values("valor_total", ascending=False)
    portfolio_df["sector"] = portfolio_df["ticker"].map(SECTOR_BY_TICKER)
    return portfolio_df


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application logic"""
    
    # Load client data
    portfolio = CLIENTS[st.session_state.selected_client]["portfolio"]
    profile = CLIENTS[st.session_state.selected_client]["perfil"]
    portfolio_value = calculate_portfolio_value(st.session_state.selected_client)
    
    # Prepare portfolio data BEFORE sidebar to get best/worst
    portfolio_df = prepare_portfolio_dataframe(portfolio)
    best_ticker = portfolio_df.loc[portfolio_df["variacao_pct"].idxmax(), "ticker"]
    worst_ticker = portfolio_df.loc[portfolio_df["variacao_pct"].idxmin(), "ticker"]
    portfolio_gain_pct = portfolio_df["variacao_pct"].mean()
    
    # Render sidebar with best/worst holdings and gain percentage
    selected_client = render_sidebar(
        st.session_state.selected_client,
        CLIENTS[st.session_state.selected_client]["perfil"],
        portfolio_value,
        best_ticker,
        worst_ticker,
        portfolio_gain_pct
    )
    if selected_client != st.session_state.selected_client:
        st.session_state.selected_client = selected_client
        st.session_state.selected_stock = CLIENTS[selected_client]["portfolio"][0]["ticker"]
        st.rerun()
    st.session_state.selected_client = selected_client
    
    # Add branding to top right
    _, branding_col = st.columns([2, 1.5])
    with branding_col:
        st.markdown(
            """
            <div style="text-align:right; white-space:nowrap; font-size:0.9rem; padding-right:1rem;">
                <span style="font-weight:700; color:#1d4ed8;">Data Master</span>
                <span style="font-weight:600; color:#0f172a; margin:0 0.3rem;">Eng IA</span>
                <span style="color:#94a3b8;">•</span>
                <span style="font-weight:600; color:#334155; margin:0 0.3rem;">Marcio de Lima</span>
                <span style="color:#94a3b8;">©</span>
                <span style="color:#94a3b8;">2026</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Update portfolio and profile if client changed
    portfolio = CLIENTS[selected_client]["portfolio"]
    profile = CLIENTS[selected_client]["perfil"]
    portfolio_value = calculate_portfolio_value(selected_client)
    portfolio_df = prepare_portfolio_dataframe(portfolio)
    best_ticker = portfolio_df.loc[portfolio_df["variacao_pct"].idxmax(), "ticker"]
    worst_ticker = portfolio_df.loc[portfolio_df["variacao_pct"].idxmin(), "ticker"]
    
    # Render topbar removed - tabs now include Risco and Simulação
    
    # Create dialog functions
    open_stock_analysis, show_dialog = create_stock_analysis_dialog()
    open_recommendation, show_recommendation = create_recommendation_dialog()
    
    # Handle dialogs trigger
    if st.session_state.get("show_dialog"):
        show_dialog(st.session_state.selected_stock, st.session_state.selected_view, portfolio, profile)
        st.session_state.show_dialog = False
    
    if st.session_state.get("show_recommendation_dialog"):
        show_recommendation(st.session_state.selected_stock, profile)
        st.session_state.show_recommendation_dialog = False
    
    # Main content tabs
    portfolio_tab, sector_tab, risk_tab, sim_tab, portfolio_suggest_tab, news_tab, chat_tab = st.tabs(["📊 Carteira", "🎯 Setor", "⚠️ Risco", "🧪 Simulação", "📊 Carteira x Risco", "📰 Notícias", "💬 Chat"])
    
    with portfolio_tab:
        render_portfolio_table(
            portfolio_df,
            best_ticker,
            worst_ticker,
            lambda ticker, view: open_stock_analysis(ticker, view, portfolio, profile),
            open_recommendation,
            profile
        )

    with sector_tab:
        render_sector_allocation(portfolio_df)
    
    with risk_tab:
        st.subheader("Análise de Risco da Carteira")
        render_ranking_cards(portfolio_df)
    
    with sim_tab:
        st.subheader("Simulação de Cenários")
        st.info("📊 Simule diferentes cenários de mercado e veja o impacto na sua carteira. Selecione uma ação na tabela para visualizar a simulação de preço.")
    
    with portfolio_suggest_tab: 
        st.subheader("Carteira Recomendada (RetornoxRisco)")
        st.info("📊 Baseado no retorno financeiro desejado e do risco a ser assumido, segue uma carteira com 5 ações.")
        
    with news_tab:
        render_news_section()
    
    with chat_tab:
        render_chat_section(selected_client)
    
    # Add branding footer with Data Master Eng IA
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        render_footer()


if __name__ == "__main__":
    main()
