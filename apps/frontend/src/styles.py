"""
Streamlit CSS Styles for Meu Copiloto Financeiro
Complete theme and component styling
"""

ATLAS_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #f8fbff 0%, #edf4ff 35%, #f5f7fb 100%);
    color: #0f172a;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

.main {
    background: transparent;
}

.stAppHeader {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.9);
    border-right: 1px solid rgba(148, 163, 184, 0.25);
    color: #0f172a;
    height: 100vh;
    min-height: 100vh;
    overflow: hidden;
    padding: 0.75rem 0.55rem 0.5rem;
}

[data-testid="stSidebar"] > div {
    height: 100%;
    overflow: hidden;
}

[data-testid="stSidebar"] .stSidebarContent {
    gap: 0.3rem;
}

[data-testid="stSidebar"] .element-container {
    margin-bottom: 0.2rem;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 0.2rem;
    padding-bottom: 0.1rem;
}

.metric-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 18px;
    padding: 0.8rem 1rem;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.mini-stat {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 18px;
    padding: 0.8rem 0.9rem;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.04);
}

.topbar {
    background: linear-gradient(135deg, rgba(59,130,246,0.10), rgba(56,189,248,0.08), rgba(255,255,255,0.9));
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 22px;
    padding: 0.9rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 20px 50px rgba(37, 99, 235, 0.08);
}

.topbar-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.18);
    color: #bfdbfe;
    border: 1px solid rgba(96, 165, 250, 0.3);
    border-radius: 999px;
    padding: 0.35rem 0.72rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.header-kicker {
    color: #1d4ed8;
    font-size: 0.74rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    font-weight: 700;
}

.header-title {
    font-size: clamp(1.7rem, 2.2vw, 2.5rem);
    font-weight: 800;
    line-height: 1.08;
    margin: 0;
    color: #0f172a;
}

.header-subtitle {
    margin-top: 0.45rem;
    color: #334155;
    font-size: 0.96rem;
}

.header-actions {
    display: flex;
    gap: 0.55rem;
    flex-wrap: wrap;
}

.tool-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 999px;
    padding: 0.45rem 0.8rem;
    color: #0f172a;
    font-size: 0.78rem;
    font-weight: 600;
}

.glass {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 1rem 1.1rem;
    backdrop-filter: blur(8px);
}

.sidebar-card {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 18px;
    padding: 0.7rem 0.75rem;
    margin-bottom: 0.45rem;
}

.sidebar-brand {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0f172a;
}

.sidebar-tag {
    display: inline-block;
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.2);
    color: #bae6fd;
    border-radius: 999px;
    padding: 0.32rem 0.6rem;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.ticker-pill {
    display: inline-block;
    background: linear-gradient(135deg, #1d4ed8, #38bdf8);
    color: white;
    border-radius: 999px;
    padding: 0.35rem 0.75rem;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.06em;
}

.risk-badge {
    display: inline-block;
    padding: 0.38rem 0.8rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
}

.buy { background: rgba(34, 197, 94, 0.18); color: #86efac; }
.neutral { background: rgba(245, 158, 11, 0.18); color: #fbbf24; }
.sell { background: rgba(239, 68, 68, 0.18); color: #fca5a5; }

.news-item {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 12px 25px rgba(15, 23, 42, 0.04);
}

.news-item .title {
    color: #0f172a !important;
}

.rank-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 0.7rem 0.8rem;
    min-height: 110px;
}

.rank-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.45rem;
}

.rank-number {
    color: #93c5fd;
    font-weight: 800;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.rank-value {
    font-size: 1.35rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.portfolio-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 0.8rem 0.9rem 0.7rem;
    height: 100%;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
    color: #0f172a;
}

.performance-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 18px;
    padding: 0.9rem 0.9rem 0.8rem;
    min-height: 170px;
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
    color: #0f172a;
}

.performance-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.65rem;
}

.performance-price {
    font-size: 1.35rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.performance-meta {
    color: #334155;
    font-size: 0.8rem;
    margin-bottom: 0.2rem;
}

div[role="tablist"] {
    gap: 0.7rem;
    margin-bottom: 1.2rem;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 16px;
    padding: 0.5rem;
    backdrop-filter: blur(8px);
}

div[role="tab"] {
    background: rgba(255, 255, 255, 0.85);
    border: 1.5px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
    color: #334155;
    padding: 0.55rem 1rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

div[role="tab"]:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(96, 165, 250, 0.3);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

div[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(59,130,246,0.16), rgba(14,165,233,0.14));
    border: 1.5px solid rgba(59, 130, 246, 0.6);
    color: #0f172a;
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
    font-weight: 700;
}

div.stButton > button {
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: #0f172a;
    font-weight: 700;
    min-width: 42px;
    min-height: 36px;
    transition: all 0.2s ease;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
}

div.stButton > button:hover {
    border-color: rgba(96, 165, 250, 0.5);
    background: rgba(219, 234, 254, 0.8);
    color: #0f172a;
    transform: translateY(-1px);
}

.crm-table-shell {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 20px;
    padding: 0;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    overflow: hidden;
}

.crm-header-cell {
    color: #334155;
    font-weight: 800;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    min-height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.crm-cell {
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    color: #0f172a;
    white-space: nowrap;
}

.crm-cell strong {
    font-size: 0.8rem;
}

.crm-table-row {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 12px;
    padding: 0.3rem 0.45rem;
    margin-bottom: 0.25rem;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    color: #0f172a;
    min-height: 52px;
}

.crm-table-row:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.06), rgba(14,165,233,0.04));
    border-color: rgba(96, 165, 250, 0.25);
    transform: translateX(2px);
    box-shadow: inset 3px 0 0 rgba(59, 130, 246, 0.4);
}

/* Give chart dialogs enough room while preserving mobile margins. */
[data-testid="stDialog"] > div,
div[role="dialog"] {
    width: min(94vw, 1180px) !important;
    max-width: 1180px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stDialog"] [data-testid="stDialogContent"],
div[role="dialog"] > div {
    max-height: 88vh;
}

/* Global loading spinner */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(4px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    gap: 1rem;
}

.loading-spinner {
    width: 56px;
    height: 56px;
    border: 4px solid #e2e8f0;
    border-top: 4px solid #1d4ed8;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.loading-text {
    color: #475569;
    font-size: 1rem;
    font-weight: 600;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
"""


def inject_theme():
    """Inject theme CSS into Streamlit app"""
    import streamlit as st
    st.markdown(ATLAS_THEME, unsafe_allow_html=True)
