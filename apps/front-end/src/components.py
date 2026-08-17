"""
Reusable UI Components for Meu Copiloto Financeiro
Sidebar, header, portfolio, news, and chat sections
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from html import escape

from .utils import format_money, format_pct, format_asset_label, get_market_data, add_indicators, assess_recommendation, forecast_prices, get_fundamentals, get_dividend_history, get_recommendation_details
from .data import CLIENTS, SECTOR_BY_TICKER, COMPANY_BY_TICKER, FAKE_NEWS


# ============================================================================
# SIDEBAR COMPONENT
# ============================================================================

def render_sidebar(selected_client: str, profile: str, portfolio_value: float, best_ticker: str, worst_ticker: str, portfolio_gain_pct: float = 0.0) -> str:
    """
    Render left sidebar with client profile and portfolio summary
    
    Args:
        selected_client: Selected client name
        profile: Client risk profile
        portfolio_value: Total portfolio value in BRL
        best_ticker: Best performing holding ticker
        worst_ticker: Worst performing holding ticker
        portfolio_gain_pct: Portfolio gain percentage
    
    Returns:
        Updated selected client name
    """
    st.sidebar.markdown(
        """
        <div style='background: linear-gradient(135deg, rgba(59,130,246,0.10), rgba(56,189,248,0.08), rgba(255,255,255,0.9)); border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 0.65rem 0.75rem; margin-bottom: 0.8rem;'>
            <div style='color:#1d4ed8; font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; font-weight:700; margin-bottom:0.2rem;'>Analytics Finance</div>
            <div style='font-size:1.15rem; font-weight:800; color:#0f172a; line-height:1.1; margin-bottom:0.3rem;'>Meu Copiloto Financeiro</div>
            <div style='color:#334155; font-size:0.68rem; line-height:1.35;'>Carteira, métricas, risco e simulações de preços para decisões mais conscientes com foco de aumento patrimonial.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.sidebar.header("🎯 Dados do investidor")
    selected_client = st.sidebar.selectbox("Cliente", list(CLIENTS.keys()), index=list(CLIENTS.keys()).index(selected_client))
    profile = CLIENTS[selected_client]["perfil"]

    st.sidebar.markdown(f"<div class='risk-badge {'buy' if profile == 'conservador' else 'neutral' if profile == 'moderado' else 'sell'}' style='color: #0f172a; font-size: 0.82rem;'>{profile.title()}</div>", unsafe_allow_html=True)

    st.sidebar.markdown(
        f"""
        <div class='sidebar-card' style='padding: 0.6rem 0.7rem;'>
            <div style='color:#64748b; font-size:0.65rem; letter-spacing:0.08em; text-transform:uppercase;'>Objetivo</div>
            <div style='margin-top:0.3rem; color:#475569; font-size:0.75rem; line-height:1.4;'>{CLIENTS[selected_client]['objetivo']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    gain_color = '#16a34a' if portfolio_gain_pct >= 0 else '#dc2626'
    st.sidebar.markdown(
        f"""
        <div class='sidebar-card' style='padding: 0.6rem 0.7rem;'>
            <div style='color:#64748b; font-size:0.65rem; letter-spacing:0.08em; text-transform:uppercase;'>Resumo Financeiro</div>
            <div style='margin-top:0.35rem; font-size:0.95rem; font-weight:800;'>{format_money(portfolio_value)}</div>
            <div style='margin-top:0.15rem; color:#475569; font-size:0.7rem;'>Valor total</div>
            <div style='margin-top:0.35rem; color:{gain_color}; font-weight:700; font-size:0.72rem;'>Ganho: {portfolio_gain_pct:+.2f}%</div>
            <div style='margin-top:0.5rem; color:#16a34a; font-weight:700; font-size:0.72rem;'>🏆 Melhor: {format_asset_label(best_ticker, COMPANY_BY_TICKER)}</div>
            <div style='margin-top:0.25rem; color:#dc2626; font-weight:700; font-size:0.72rem;'>📉 Pior: {format_asset_label(worst_ticker, COMPANY_BY_TICKER)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_client


# ============================================================================
# TOPBAR COMPONENT
# ============================================================================

# ============================================================================
# RECOMMENDATION ANALYSIS DIALOG
# ============================================================================

def create_recommendation_dialog():
    """Create a dialog factory for recommendation details"""
    def open_recommendation(symbol: str, profile: str):
        st.session_state.selected_stock = symbol
        st.session_state.show_recommendation_dialog = True
        st.rerun()

    @st.dialog("Análise da Recomendação")
    def show_recommendation_dialog(symbol: str, profile: str):
        st.markdown(f"<div style='font-size:1.4rem; font-weight:800; color:#1d4ed8; margin-bottom:0.8rem;'>{escape(format_asset_label(symbol, COMPANY_BY_TICKER))}</div>", unsafe_allow_html=True)
        
        # Get market data and analysis
        market_df = add_indicators(get_market_data(symbol, "6mo"))
        details = get_recommendation_details(market_df, profile)
        
        # Show recommendation badge
        rec = details["recommendation"]
        badge_colors = {"Compra": "#16a34a", "Venda": "#dc2626", "Neutra": "#f59e0b"}
        badge_color = badge_colors.get(rec, "#64748b")
        
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;'>
                <div style='font-size:1.1rem; font-weight:700; color:white; background:{badge_color}; padding:0.5rem 1rem; border-radius:8px;'>
                    {rec.upper()}
                </div>
                <div style='color:#475569; font-size:0.9rem;'>
                    Perfil: <strong>{profile.title()}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Show indicators
        st.markdown("#### 📊 Indicadores Técnicos")
        cols = st.columns(2)
        for idx, (indicator, data) in enumerate(details["indicators"].items()):
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div style='background:rgba(255,255,255,0.8); border:1px solid rgba(148,163,184,0.2); border-radius:12px; padding:0.8rem; margin-bottom:0.5rem;'>
                        <div style='color:#64748b; font-size:0.8rem; font-weight:600;'>{indicator}</div>
                        <div style='font-size:1.2rem; font-weight:700; color:#0f172a; margin-top:0.3rem;'>{data["status"]} {data["value"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        # Show sources/reasoning
        st.markdown("#### 🔍 Fundamentos da Análise")
        for source in details["sources"]:
            st.markdown(
                f"""
                <div style='background:rgba(59,130,246,0.08); border-left:4px solid #1d4ed8; padding:0.8rem 1rem; margin-bottom:0.6rem; border-radius:6px;'>
                    <div style='color:#0f172a; font-size:0.95rem;'>{source}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.divider()
        st.markdown("💡 **Dica:** Clique em um ticker para ver análises técnicas detalhadas (gráficos, MACD, Bollinger Bands)")

    return open_recommendation, show_recommendation_dialog


# ============================================================================
# PORTFOLIO ANALYSIS DIALOG
# ============================================================================

def create_stock_analysis_dialog():
    """Create a dialog factory for stock analysis charts"""
    def open_stock_analysis(symbol: str, view: str, portfolio: list, profile: str):
        st.session_state.selected_stock = symbol
        st.session_state.selected_view = view
        st.session_state.dialog_period = "1 ano" if view == "dy" else "6 meses"
        st.session_state.show_dialog = True
        st.rerun()

    @st.dialog("Análise de ativo")
    def show_dialog(symbol: str, view: str, portfolio: list, profile: str):
        asset_label = format_asset_label(symbol, COMPANY_BY_TICKER)
        st.markdown(f"<div style='font-size:1.3rem; font-weight:700; color:#1d4ed8; margin-bottom:0.5rem;'>{escape(asset_label)}</div>", unsafe_allow_html=True)
        
        period = "6 meses"
        dividend_years = 1
        if view == "dy":
            period = st.selectbox("Período de dividendos", ["1 ano", "3 anos", "5 anos"], index=0, key="dialog_period")
            dividend_years = {"1 ano": 1, "3 anos": 3, "5 anos": 5}[period]
        elif view != "simulacao":
            period = st.selectbox("Período", ["6 meses", "1 ano", "3 meses", "1 semana"], index=0, key="dialog_period")
        period_map = {"6 meses": "6mo", "1 ano": "1y", "3 meses": "3mo", "1 semana": "5d", "3 anos": "3y", "5 anos": "5y"}
        period_code = period_map[period]
        
        # Loading placeholder
        loading_placeholder = st.empty()
        loading_placeholder.markdown(
            """
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:400px; gap:1rem;">
                <div style="width:48px; height:48px; border:4px solid #e2e8f0; border-top:4px solid #1d4ed8; border-radius:50%; animation:spin 1s linear infinite;"></div>
                <div style="color:#475569; font-size:0.95rem;">Carregando gráfico...</div>
            </div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
            """,
            unsafe_allow_html=True,
        )
        
        stock_df = add_indicators(get_market_data(symbol, period_code))
        
        if stock_df.empty:
            loading_placeholder.empty()
            st.error("Não foi possível carregar dados para este período.")
            return

        if view == "candles":
            loading_placeholder.empty()
            fig = go.Figure(data=[go.Candlestick(x=stock_df["date"], open=stock_df["Open"], high=stock_df["High"], low=stock_df["Low"], close=stock_df["Close"], increasing_line_color="#22c55e", decreasing_line_color="#ef4444")])
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font={"color": "#0f172a"}, title=f"{asset_label} - Candlestick ({period})", xaxis_title="Data", yaxis_title="Preço", height=420)
            st.plotly_chart(fig, use_container_width=True)
        elif view == "macd":
            loading_placeholder.empty()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["Close"], name="Preço", line=dict(color="#38bdf8", width=2)))
            fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["MACD"], name="MACD", line=dict(color="#8b5cf6", width=2)))
            fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["Signal"], name="Sinal", line=dict(color="#f59e0b", width=2)))
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font={"color": "#0f172a"}, title=f"{asset_label} - MACD ({period})", height=420)
            st.plotly_chart(fig, use_container_width=True)
        elif view == "bollinger":
            loading_placeholder.empty()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["Close"], name="Fechamento", line=dict(color="#0ea5e9", width=2)))
            fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["Upper_Band"], name="Banda superior", line=dict(color="#ef4444", dash="dot")))
            fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["Lower_Band"], name="Banda inferior", line=dict(color="#f97316", dash="dot")))
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font={"color": "#0f172a"}, title=f"{asset_label} - Bollinger ({period})", height=420)
            st.plotly_chart(fig, use_container_width=True)
        elif view == "dy":
            loading_placeholder.empty()
            fund = get_fundamentals(symbol)
            div_df = get_dividend_history(symbol, dividend_years)
            current_dy = fund.get("dy")

            if current_dy is not None:
                st.markdown(f"<div style='font-size:1.3rem; font-weight:800; color:#16a34a; margin-bottom:0.5rem;'>DY Atual: {format_pct(current_dy)}</div>", unsafe_allow_html=True)
            if not div_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=div_df["date"],
                    y=div_df["dividend"],
                    name="Dividendo (R$)",
                    marker_color="#22c55e",
                    text=[f"R$ {v:.2f}" for v in div_df["dividend"]],
                    textposition="outside",
                ))
                fig.update_layout(
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    font={"color": "#0f172a"},
                    title=f"{asset_label} - Histórico de Dividendos ({period})",
                    xaxis_title="Data",
                    yaxis_title="Dividendo por ação (R$)",
                    height=300,
                    margin=dict(l=20, r=20, t=55, b=35),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de dividendos disponíveis para este ativo.")
        else:
            loading_placeholder.empty()
            forecast = forecast_prices(stock_df, profile, days=5)
            current_price = float(stock_df["Close"].iloc[-1])
            projected_price = float(forecast["price"].iloc[-1])
            projected_change = ((projected_price - current_price) / current_price) * 100
            recent_change = ((float(stock_df["Close"].iloc[-1]) - float(stock_df["Close"].iloc[-20])) / float(stock_df["Close"].iloc[-20])) * 100
            volatility = float(stock_df["Close"].pct_change().dropna().tail(20).std() * 100)
            direction = "alta" if projected_change >= 0 else "queda"
            trend = "positiva" if recent_change >= 0 else "negativa"
            justification = (
                f"A projeção indica {direction} de {abs(projected_change):.2f}% em até 1 semana. "
                f"A tendência recente foi {trend} ({recent_change:+.2f}% em 20 pregões), "
                f"com volatilidade diária estimada de {volatility:.2f}%. "
                f"O cenário considera o histórico recente e o perfil {profile}. "
                "Esta é uma simulação educacional, não uma garantia de preço futuro."
            )
            st.info(justification)
            fig = go.Figure(data=[go.Scatter(x=forecast["date"], y=forecast["price"], mode="lines+markers", line=dict(color="#22c55e", width=3))])
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font={"color": "#0f172a"}, title=f"{asset_label} - Simulação de preço (até 1 semana)", xaxis_title="Data", yaxis_title="Preço estimado", height=360, margin=dict(l=20, r=20, t=55, b=35))
            st.plotly_chart(fig, use_container_width=True)

    return open_stock_analysis, show_dialog


# ============================================================================
# CHARTS RENDERING
# ============================================================================

def render_sector_allocation(portfolio_df: pd.DataFrame):
    """Render sector allocation cards and pie chart"""
    sector_summary = portfolio_df.groupby("sector", as_index=False)["valor_total"].sum().sort_values("valor_total", ascending=False)
    
    allocation_col, allocation_chart = st.columns([1.1, 1.9])
    with allocation_col:
        st.markdown(
            """
            <div class='portfolio-card'>
                <div style='color:#94a3b8; font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.8rem;'>Alocação por setor</div>
            """,
            unsafe_allow_html=True,
        )
        for _, row in sector_summary.iterrows():
            pct = (row["valor_total"] / portfolio_df["valor_total"].sum()) * 100
            st.markdown(
                f"<div style='display:flex; justify-content:space-between; margin-bottom:0.55rem; color:#334155;'><span>{row['sector']}</span><strong>{pct:.1f}%</strong></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with allocation_chart:
        pie_fig = go.Figure(data=[go.Pie(labels=sector_summary["sector"], values=sector_summary["valor_total"], hole=0.45, marker=dict(colors=["#60a5fa", "#38bdf8", "#2dd4bf", "#34d399", "#fbbf24", "#f59e0b", "#a78bfa", "#c084fc", "#f87171", "#fb7185"]), textinfo="label+percent", insidetextorientation="radial")])
        pie_fig.update_layout(paper_bgcolor="rgba(255,255,255,0.96)", plot_bgcolor="rgba(255,255,255,0.96)", font={"color": "#0f172a"}, height=260, margin=dict(l=20, r=20, t=20, b=20), title="Mix setorial", title_x=0.02)
        st.plotly_chart(pie_fig, use_container_width=True)


def render_ranking_cards(portfolio_df: pd.DataFrame):
    """Render top 3 performing stocks ranking"""
    ranking = portfolio_df.sort_values("variacao_pct", ascending=False).reset_index(drop=True)
    rank_col1, rank_col2, rank_col3 = st.columns(3)
    
    for idx, col in enumerate([rank_col1, rank_col2, rank_col3], start=1):
        item = ranking.iloc[idx - 1]
        trend = "↗" if item["variacao_pct"] >= 0 else "↘"
        trend_color = "#16a34a" if item["variacao_pct"] >= 0 else "#dc2626"
        with col:
            st.markdown(
                f"""
                <div class='rank-card'>
                    <div class='rank-top'>
                        <span class='rank-number'>#{idx}</span>
                        <span style='color:{trend_color}; font-weight:800;'>{trend} {item['variacao_pct']:.1f}%</span>
                    </div>
                    <div class='rank-value'>{escape(format_asset_label(item['ticker'], COMPANY_BY_TICKER))}</div>
                    <div style='color:#475569; font-size:0.8rem;'>Preço atual: {format_money(item['preco_atual'])}</div>
                    <div style='margin-top:0.35rem; color:#475569; font-size:0.8rem;'>Valor: {format_money(item['valor_total'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================================
# NEWS SECTION
# ============================================================================

def render_news_section():
    """Render financial news feed"""
    st.subheader("Últimas notícias financeiras")
    for item in FAKE_NEWS:
        st.markdown(
            f"""
            <div class='news-item'>
                <div style='font-size:0.72rem; color:#64748b; text-transform:uppercase; letter-spacing:0.08em;'>{item['source']} • {item['time']}</div>
                <div class='title' style='font-size:1.02rem; font-weight:600; margin-top:0.5rem; color:#0f172a;'>{item['title']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================================
# CHAT SECTION
# ============================================================================

def render_chat_section(selected_client: str):
    """Render financial assistant chat"""
    st.subheader("Assistente financeiro")
    st.caption("Perguntas rápidas sobre a carteira, setores ou ações brasileiras.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Olá! Posso ajudar com análise de carteira, risco e ações brasileiras. Pergunte por exemplo: 'qual a melhor ação da minha carteira?', 'a carteira está balanceada?' ou 'o que você acha da PETR4?'"}
        ]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input("Faça uma pergunta sobre a sua carteira ou sobre ações brasileiras", max_chars=500)
    if user_message:
        user_message = user_message.strip()
        if not user_message:
            return
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        question = user_message.lower()

        if "carteira" in question or "perfil" in question:
            top_positions = [format_asset_label(item["ticker"], COMPANY_BY_TICKER) for item in CLIENTS[selected_client]["portfolio"][:3]]
            response = f"A carteira de {selected_client} está focada em {CLIENTS[selected_client]['perfil']} e possui {len(CLIENTS[selected_client]['portfolio'])} posições, com maior peso em {', '.join(top_positions)}. O objetivo é manter diversificação e controle de risco."
        elif "petr4" in question or "petro" in question:
            response = "PETR4 normalmente acompanha o ciclo do petróleo e pode ter sensibilidade a commodities. Em um cenário de juros estáveis e câmbio favorável, a ação tende a responder bem a melhora do ambiente macro."
        elif "vale" in question or "vale3" in question:
            response = "VALE3 costuma ter forte ligação com minério de ferro e demanda chinesa. A tendência da ação depende muito da dinâmica do preço do minério e da liquidez global."
        elif "itub" in question or "itub4" in question:
            response = "ITUB4 tende a ter foco em rentabilidade e qualidade de crédito. É uma ação que costuma reagir a cenário de juros e crescimento de crédito no Brasil."
        elif "recomend" in question or "compra" in question or "venda" in question:
            response = "A recomendação para a carteira depende do horizonte e do perfil de risco. Para um investidor conservador, foco em qualidade e disciplina de entrada; para moderado, composição equilibrada; para agressivo, maior beta e busca por upside."
        else:
            response = "Posso responder sobre carteira, indicadores e ações do Brasil. Tente perguntar por exemplo: 'qual ação da carteira tem melhor potencial?', 'como está meu perfil de risco?' ou 'o que você acha da PETR4?'"

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.chat_history = st.session_state.chat_history[-20:]
        with st.chat_message("assistant"):
            st.write(response)


# ============================================================================
# FOOTER
# ============================================================================

def render_footer():
    """Render page footer with warnings"""
    st.warning("Atenção: As respostas da IA podem conter erros. Estes conteúdos não constituem recomendação financeira, assessoria de investimento ou garantia de retorno.")
