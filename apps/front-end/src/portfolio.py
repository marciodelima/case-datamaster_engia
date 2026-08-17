"""
Portfolio Table Component for Meu Copiloto Financeiro
CRM-style table with hover effects and action buttons
"""

import streamlit as st
import pandas as pd
from html import escape

from .utils import format_money, format_ticker


def render_portfolio_table(portfolio_df: pd.DataFrame, best_ticker: str, worst_ticker: str, open_stock_analysis_fn, open_recommendation_fn, profile: str):
    """Render a compact osne-row-per-asset portfolio table."""
    st.subheader("Minha Carteira")

    header_cols = st.columns([1.3, 0.8, 1.2, 1.2, 1.2, 0.8, 0.8, 0.9, 1.4, 1.3])
    labels = ["Ticker", "Qtd", "Médio", "Teto", "Atual", "P/VP", "DY", "Var.%", "Sugestão", "Ações"]
    for col, label in zip(header_cols, labels):
        with col:
            st.markdown(f"<div class='crm-header-cell'>{escape(label)}</div>", unsafe_allow_html=True)

    for item in portfolio_df.to_dict("records"):
        rec_badge = 'buy' if item['ticker'] == best_ticker else 'sell' if item['ticker'] == worst_ticker else 'neutral'
        is_selected = st.session_state.get("selected_stock") == item["ticker"]

        cols = st.columns([1.3, 0.8, 1.2, 1.2, 1.2, 0.8, 0.8, 0.9, 1.4, 1.3])

        with cols[0]:
            if st.button(
                format_ticker(item["ticker"]),
                key=f"select_{item['ticker']}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                open_recommendation_fn(item['ticker'], profile)
        with cols[1]:
            st.markdown(f"<div class='crm-cell'>{item['quantidade']}</div>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<div class='crm-cell'>{format_money(item['preco_medio'])}</div>", unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f"<div class='crm-cell'>{format_money(item['preco_teto'])}</div>", unsafe_allow_html=True)
        with cols[4]:
            st.markdown(f"<div class='crm-cell'><strong>{format_money(item['preco_atual'])}</strong></div>", unsafe_allow_html=True)
        with cols[5]:
            p_vp = item.get('p_vp')
            p_vp_val = f"{p_vp:.2f}" if p_vp and p_vp > 0 else "—"
            st.markdown(f"<div class='crm-cell'>{p_vp_val}</div>", unsafe_allow_html=True)
        with cols[6]:
            dy = item.get('dy')
            dy_val = f"{dy:.2f}%" if dy and dy > 0 else "—"
            st.markdown(f"<div class='crm-cell' style='color:#16a34a; font-weight:600;'>{dy_val}</div>", unsafe_allow_html=True)
        with cols[7]:
            st.markdown(f"<div class='crm-cell' style='color:{'#16a34a' if item['variacao_pct'] >= 0 else '#dc2626'}; font-weight:700;'>{item['variacao_pct']:.1f}%</div>", unsafe_allow_html=True)
        with cols[8]:
            st.markdown(f"<div class='crm-cell'><span class='risk-badge {escape(rec_badge)}'>{escape(str(item['recomendacao']))}</span></div>", unsafe_allow_html=True)
        with cols[9]:
            action_cols = st.columns([1, 1, 1, 1, 1], gap="small")
            with action_cols[0]:
                if st.button("📈", key=f"candles_{item['ticker']}", help=f"Candles de {format_ticker(item['ticker'])}", use_container_width=True):
                    open_stock_analysis_fn(item['ticker'], "candles")
            with action_cols[1]:
                if st.button("📉", key=f"macd_{item['ticker']}", help=f"MACD de {format_ticker(item['ticker'])}", use_container_width=True):
                    open_stock_analysis_fn(item['ticker'], "macd")
            with action_cols[2]:
                if st.button("📊", key=f"bollinger_{item['ticker']}", help=f"Bollinger de {format_ticker(item['ticker'])}", use_container_width=True):
                    open_stock_analysis_fn(item['ticker'], "bollinger")
            with action_cols[3]:
                if st.button("💰", key=f"dy_{item['ticker']}", help=f"Dividend Yield de {format_ticker(item['ticker'])}", use_container_width=True):
                    open_stock_analysis_fn(item['ticker'], "dy")
            with action_cols[4]:
                if st.button("🧪", key=f"sim_{item['ticker']}", help=f"Simulação de {format_ticker(item['ticker'])}", use_container_width=True):
                    open_stock_analysis_fn(item['ticker'], "simulacao")

        st.markdown("<div style='height:0.15rem;'></div>", unsafe_allow_html=True)
