"""
Utility functions for Meu Copiloto Financeiro
Market data fetching, technical indicators, and formatting
"""

import numpy as np
import pandas as pd
import streamlit as st
import re

try:
    import yfinance as yf
except ImportError:
    yf = None


# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

TICKER_PATTERN = re.compile(r"^[A-Z]{4}[0-9]{1,2}\.SA$")


def is_valid_ticker(symbol: str) -> bool:
    """Allow only Brazilian B3 ticker symbols before external lookups."""
    return isinstance(symbol, str) and bool(TICKER_PATTERN.fullmatch(symbol))

def format_money(value: float) -> str:
    """Format value as Brazilian currency (BRL)"""
    return f"R$ {value:,.2f}"


def format_pct(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"


def format_ticker(symbol: str) -> str:
    """Format an internal B3 ticker for user-facing displays."""
    return symbol.removesuffix(".SA") if isinstance(symbol, str) else str(symbol)


def format_asset_label(symbol: str, company_names: dict[str, str]) -> str:
    """Build a user-facing label without changing the internal ticker."""
    ticker = format_ticker(symbol)
    company = company_names.get(symbol, "Empresa não cadastrada")
    return f"{ticker} - {company}"


# ============================================================================
# FUNDAMENTAL DATA
# ============================================================================

@st.cache_data
def get_fundamentals(symbol: str) -> dict:
    """
    Fetch P/VP and Dividend Yield from Yahoo Finance

    Args:
        symbol: Stock ticker (e.g., 'PETR4.SA')

    Returns:
        Dict with 'p_vp' and 'dy' keys (floats or None)
        'dy' is returned as a percentage (e.g. 5.32 for 5.32%)
    """
    try:
        if yf is None or not is_valid_ticker(symbol):
            return {"p_vp": None, "dy": None}
        info = yf.Ticker(symbol).info
        raw_dy = info.get("dividendYield")
        p_vp = info.get("priceToBook")

        # dividendYield comes as decimal (0.0532 = 5.32%)
        dy = round(raw_dy * 1, 2) if raw_dy and raw_dy > 0 else None
        p_vp = round(p_vp, 2) if p_vp and p_vp > 0 else None

        return {"p_vp": p_vp, "dy": dy}
    except Exception:
        return {"p_vp": None, "dy": None}


@st.cache_data
def get_dividend_history(symbol: str, years: int = 1) -> pd.DataFrame:
    """
    Fetch dividend payment history from Yahoo Finance

    Args:
        symbol: Stock ticker (e.g., 'PETR4.SA')

    Returns:
        DataFrame with 'date' and 'dividend' columns for the selected period
    """
    try:
        if yf is None or not is_valid_ticker(symbol):
            raise ValueError("Invalid or unavailable ticker")
        ticker = yf.Ticker(symbol)
        divs = ticker.dividends
        if divs.empty:
            raise ValueError("No dividends")
        df = divs.reset_index()
        df.columns = ["date", "dividend"]
        df["date"] = pd.to_datetime(df["date"])
        years = max(1, min(int(years), 5))
        cutoff = pd.Timestamp.today() - pd.Timedelta(days=365 * years)
        df = df[df["date"] >= cutoff].sort_values("date")
        return df
    except Exception:
        return _generate_synthetic_dividends(symbol, years)


def _generate_synthetic_dividends(symbol: str, years: int = 1) -> pd.DataFrame:
    """Generate synthetic dividend data for demo purposes"""
    rng = np.random.default_rng(sum(ord(ch) for ch in symbol))
    years = max(1, min(int(years), 5))
    dates = pd.date_range(end=pd.Timestamp.today(), periods=years * 4, freq="QE")
    base_div = 0.3 + (sum(ord(ch) for ch in symbol) % 10) * 0.05
    dividends = np.abs(rng.normal(base_div, base_div * 0.3, len(dates)))
    return pd.DataFrame({"date": dates, "dividend": dividends})


# ============================================================================
# MARKET DATA UTILITIES
# ============================================================================

@st.cache_data
def get_market_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """
    Fetch market data from Yahoo Finance with synthetic fallback
    
    Args:
        symbol: Stock ticker (e.g., 'PETR4.SA')
        period: Period for data retrieval (default: '6mo')
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        if yf is None or not is_valid_ticker(symbol):
            raise ValueError("Invalid or unavailable ticker")
        df = yf.download(symbol, period=period, interval="1d", auto_adjust=True, progress=False, actions=False)
        if df.empty:
            raise ValueError("No data available")
        df = df.reset_index()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [column[0] for column in df.columns]
        df = df.loc[:, ~df.columns.duplicated(keep="first")]
        return df.rename(columns={"Date": "date"})
    except Exception:
        # Generate synthetic fallback data
        return _generate_synthetic_data(symbol)


def _generate_synthetic_data(symbol: str) -> pd.DataFrame:
    """Generate synthetic market data for demo purposes"""
    end_date = pd.Timestamp.today().normalize()
    start_date = end_date - pd.Timedelta(days=180)
    dates = pd.date_range(start_date, end_date, freq="B")
    
    # Deterministic pseudo-random based on symbol
    base = 30 + sum(ord(ch) for ch in symbol) % 25
    trend = np.linspace(0.9, 1.15, len(dates))
    noise = np.random.default_rng(sum(ord(ch) for ch in symbol)).normal(0, 0.03, len(dates))
    closes = np.cumprod(1 + (trend - 1) * 0.02 + noise * 0.35) * base
    
    opens = np.roll(closes, 1)
    opens[0] = closes[0] * 0.98
    highs = np.maximum(opens, closes) * (1 + np.abs(np.random.default_rng(2).normal(0, 0.012, len(dates))))
    lows = np.minimum(opens, closes) * (1 - np.abs(np.random.default_rng(3).normal(0, 0.012, len(dates))))
    volume = np.random.default_rng(4).integers(500_000, 5_000_000, len(dates))
    
    return pd.DataFrame({
        "date": dates,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes,
        "Volume": volume,
    })


# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for price data
    
    Indicators:
        - SMA 10/20 (Simple Moving Averages)
        - EMA 12/26 (Exponential Moving Averages)
        - MACD (Moving Average Convergence Divergence)
        - Signal Line
        - Bollinger Bands (20-period, 2 std)
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        DataFrame with added indicators
    """
    df = df.copy()
    
    # Moving averages
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
    
    # MACD
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["Signal"]
    
    # Bollinger Bands
    window = 20
    rolling_mean = df["Close"].rolling(window).mean()
    rolling_std = df["Close"].rolling(window).std()
    df["Upper_Band"] = rolling_mean + (rolling_std * 2)
    df["Lower_Band"] = rolling_mean - (rolling_std * 2)
    
    return df


def assess_recommendation(df: pd.DataFrame, profile: str) -> tuple[str, str]:
    """
    Generate buy/sell recommendation based on technical analysis and investor profile
    
    Args:
        df: DataFrame with technical indicators
        profile: Investor profile ('conservador', 'moderado', 'agressivo')
    
    Returns:
        Tuple of (recommendation_text, badge_class)
    """
    current = float(df["Close"].iloc[-1])
    recent_10 = float(df["Close"].iloc[-10])
    recent_20 = float(df["Close"].iloc[-20]) if len(df) >= 20 else float(df["Close"].iloc[0])
    momentum = (current - recent_20) / recent_20
    macd_signal = float(df["MACD_Hist"].iloc[-1])
    last_rsi = 50 + 50 * (df["MACD"].iloc[-1] / (abs(df["MACD"].iloc[-1]) + 1))

    if profile == "conservador":
        if momentum > 0.05 and macd_signal > 0 and last_rsi < 70:
            return "Compra", "buy"
        if momentum < -0.06 or macd_signal < 0:
            return "Venda", "sell"
        return "Neutra", "neutral"

    if profile == "moderado":
        if momentum > 0.08 and macd_signal > 0:
            return "Compra", "buy"
        if momentum < -0.08 or macd_signal < -0.2:
            return "Venda", "sell"
        return "Neutra", "neutral"

    if momentum > 0.12 and macd_signal > 0.4:
        return "Compra", "buy"
    if momentum < -0.1 or macd_signal < -0.4:
        return "Venda", "sell"
    return "Neutra", "neutral"


def get_recommendation_details(df: pd.DataFrame, profile: str) -> dict:
    """
    Generate detailed recommendation explanation with technical sources
    
    Args:
        df: DataFrame with technical indicators
        profile: Investor profile ('conservador', 'moderado', 'agressivo')
    
    Returns:
        Dict with recommendation details, indicators, and analysis
    """
    current = float(df["Close"].iloc[-1])
    recent_10 = float(df["Close"].iloc[-10])
    recent_20 = float(df["Close"].iloc[-20]) if len(df) >= 20 else float(df["Close"].iloc[0])
    momentum = (current - recent_20) / recent_20
    macd = float(df["MACD"].iloc[-1])
    macd_signal = float(df["MACD_Hist"].iloc[-1])
    sma_10 = float(df["SMA_10"].iloc[-1]) if "SMA_10" in df.columns else None
    sma_20 = float(df["SMA_20"].iloc[-1]) if "SMA_20" in df.columns else None
    
    recommendation, badge = assess_recommendation(df, profile)
    
    sources = []
    indicators_status = {
        "Momentum (20d)": {"value": f"{momentum*100:.2f}%", "status": "📈" if momentum > 0 else "📉"},
        "MACD": {"value": f"{macd:.4f}", "status": "✅" if macd > 0 else "❌"},
        "MACD Histogram": {"value": f"{macd_signal:.4f}", "status": "✅" if macd_signal > 0 else "❌"},
        "Preço Atual": {"value": f"R$ {current:.2f}", "status": "💰"},
    }
    
    if sma_10 and sma_20:
        indicators_status["SMA 10"] = {"value": f"R$ {sma_10:.2f}", "status": "📊"}
        indicators_status["SMA 20"] = {"value": f"R$ {sma_20:.2f}", "status": "📊"}
        
        if current > sma_10 > sma_20:
            sources.append("📈 Preço acima das médias móveis (tendência de alta)")
        elif current < sma_10 < sma_20:
            sources.append("📉 Preço abaixo das médias móveis (tendência de baixa)")
    
    if profile == "conservador":
        if momentum > 0.05:
            sources.append("📊 Momentum positivo (20d) acima de 5%")
        if macd_signal > 0:
            sources.append("✅ MACD Histogram positivo (convergência de EMAs)")
        if momentum < -0.06:
            sources.append("⚠️ Momentum negativo (20d) abaixo de -6%")
    
    elif profile == "moderado":
        if momentum > 0.08:
            sources.append("📊 Momentum positivo (20d) acima de 8%")
        if macd_signal > 0:
            sources.append("✅ MACD Histogram positivo")
        if momentum < -0.08:
            sources.append("⚠️ Momentum negativo abaixo de -8%")
    
    else:  # agressivo
        if momentum > 0.12:
            sources.append("📊 Momentum forte (20d) acima de 12%")
        if macd_signal > 0.4:
            sources.append("✅ MACD Histogram muito positivo (>0.4)")
        if momentum < -0.1:
            sources.append("⚠️ Momentum negativo abaixo de -10%")
    
    return {
        "recommendation": recommendation,
        "badge": badge,
        "indicators": indicators_status,
        "sources": sources if sources else ["📋 Análise sem sinais técnicos dominantes"],
        "profile": profile,
    }


def forecast_prices(df: pd.DataFrame, profile: str, days: int = 30) -> pd.DataFrame:
    """
    Generate price forecast using Monte Carlo simulation
    
    Args:
        df: DataFrame with price history
        profile: Investor profile for volatility adjustment
        days: Number of days to forecast
    
    Returns:
        DataFrame with forecast dates and prices
    """
    recent = df["Close"].dropna().tail(30)
    last = float(recent.iloc[-1])
    vol = recent.pct_change().std() or 0.015
    profile_bias = {"conservador": 0.012, "moderado": 0.019, "agressivo": 0.028}[profile]
    rng = np.random.default_rng(sum(ord(ch) for ch in df.columns[0]) + len(recent))
    shocks = rng.normal(profile_bias, vol, days)
    
    forecast = [last]
    for value in shocks:
        forecast.append(forecast[-1] * (1 + value))
    forecast = forecast[1:]
    
    dates = pd.date_range(pd.Timestamp.today() + pd.Timedelta(days=1), periods=days, freq="B")
    return pd.DataFrame({"date": dates, "price": forecast})
