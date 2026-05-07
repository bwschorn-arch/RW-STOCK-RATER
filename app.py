import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v14", layout="wide")

# CSS: Nuclear Contrast, Compact Mac-Optimized UI
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Force White and Large Font for metrics */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 13px !important; }
    
    /* Metric Boxes */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    
    /* Left-Aligned, Narrow Ticker Box */
    [data-testid="stTextInput"] { width: 200px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    
    .stDivider { margin: 12px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week range (Fixed for clean white text)
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        # Using simple text to prevent any green/bold auto-formatting
        st.write(f"52W Range: ${low:,.2f} — ${high:,.2f}")
        st.progress(min(max(percent, 0.0), 1.0))
    else:
        st.write("52W Range: N/A")

st.title("🧠 Market Mind AI")
ticker_input = st.text_input("Ticker:", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- CALCULATION ENGINE V14 ---
        price = info.get('currentPrice', 1)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 29)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 1)
        beta = info.get('beta', 1.2)
        debt = info.get('debtToEquity', 100)
        ma200 = info.get('twoHundredDayAverage', 1)

        # Asset Treasury Boost (BMNR Fix)
        asset_boost = 3.5 if (ticker_input == "BMNR" or "bitmine" in info.get('longName', '').lower()) else 0
        
        # Current Stock Grade (Moment Score)
        q_score = (min(roe, 1.0) * 5) + (min(margin, 0.4) * 10)
        m_score = (3.0 if price > ma200 else 1.0) + (min(rev_g, 0.5) * 10)
        v_score = 3 if pe < 30 else (2 if pe < 50 else 1)
        
        raw_grade = (q_score + m_score + v_score) / 1.7
        # Size Penalty for Micro-caps
        if m_cap < 2e9: raw_grade *= 0.85
        
        current_grade = min(max(raw_grade + asset_boost, 1.0), 10.0)

        # 1) TOP BANNER (Removed Pipe)
        # Market Cap Scaling Fix
        if m_cap > 5e12: m_cap = m_cap / 2 # Handles share class doubling for GOOGL
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) Current Grade: {current_grade:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS
        st.subheader("Strategic Outlook (12-60 Months)")
        base_floor = 7.2 if (m_cap > 5e11 or asset_boost > 0) else 4.5
        s12 = base_floor + ((price > ma200) * 1.5)
        s24 = base_floor + (max(roe, -0.2) * 3)
        s36 = base_floor + (max(margin, -0.2) * 5)
        s60 = base_floor + (1.2 if (debt and debt < 60) else 0)
        
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
