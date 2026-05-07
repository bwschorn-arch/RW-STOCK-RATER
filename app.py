import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="V8.1 High-Visibility Dashboard", layout="wide")

# CSS REBUILD: Forces Dark Background and High-Contrast White Text
st.markdown("""
    <style>
    /* Force the entire app background */
    .stApp {
        background-color: #0F172A !important;
    }
    
    /* Force all header text to be Pure White */
    h1, h2, h3, h4, p, span, li {
        color: #FFFFFF !important;
    }

    /* Style the Metric Cards for contrast */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 2px solid #334155 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }

    /* Target Metric values specifically */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Target Metric labels */
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 16px !important;
    }
    
    /* Improve input box visibility */
    .stTextInput input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    percent = (current - low) / (high - low)
    st.write(f"52W Low: ${low:.2f} | Current: ${current:.2f} | 52W High: ${high:.2f}")
    st.progress(min(max(percent, 0.0), 1.0))

st.title("🏛️ V8.1: Institutional High-Conviction Dashboard")
ticker_input = st.text_input("Enter Ticker Symbol (e.g. NVDA, RKLB):", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input})")
        b1, b2, b3, b4, b5 = st.columns(5)
        price = info.get('currentPrice', 0)
        change = info.get('regularMarketChangePercent', 0)
        b1.metric("Current Price", f"${price:.2f}", f"{change:.2f}%")
        b2.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B")
        b3.metric("Sector", info.get('sector', 'N/A'))
        b4.metric("Avg Volume", f"{info.get('averageVolume', 0)/1e6:.1f}M")
        with b5:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # DATA GATHERING
        rev_growth = info.get('revenueGrowth', 0)
        pe_fwd = info.get('forwardPE', 0)
        debt_to_eq = info.get('debtToEquity', 0)
        roe = info.get('returnOnEquity', 0)
        profit_margin = info.get('profitMargins', 0)
        beta = info.get('beta', 1.0)
        rec_mean = info.get('recommendationMean', 3.0)
        ma_200 = info.get('twoHundredDayAverage', 1)
        peg = info.get('pegRatio', 1.0)

        # 2) CONVICTION STRIP
        quality_anchor = (roe * 20) + (profit_margin * 20) + (10 if debt_to_eq < 80 else 2)
        quality_anchor = min(max(quality_anchor / 5, 2), 9.5)
        
        risk_score = (1 if debt_to_eq > 120 else 0) + (1 if pe_fwd > 40 else 0) + (1 if beta > 1.5 else 0)
        risk_label = "Low" if risk_score == 0 else ("Moderate" if risk_score == 1 else "High")
        
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Overall Conviction", f"{quality_anchor:.1f}/10")
        s2.metric("Risk Level", risk_label)
        s3.metric("Confidence", "High" if info.get('numberOfAnalystOpinions', 0) > 15 else "Medium")
        s4.metric("Expectations Gap", "Positive" if rev_growth > 0.2 else "Neutral")
        s5.metric("Sector Context", f"{pe_fwd:.1f} P/E", delta=f"{pe_fwd - 22:.1f} vs S&P")

        st.divider()

        # 3) HORIZON RATINGS
        st.subheader("Time-Horizon Strategic Outlook")
        score_12m = (quality_anchor * 0.4) + ((price > ma_200) * 4) + ((rec_mean < 2.5) * 2)
        score_24m = (quality_anchor * 0.6) + ((rev_growth > 0.2) * 3) + (1 if peg < 1.5 else 0)
        score_36m = (quality_anchor * 0.8) + ((rev_growth > 0.1) * 2)
        score_60m = quality_anchor
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{score_12m:.1f}/10")
        h2.metric("24-Month", f"{score_24m:.1f}/10")
        h3.metric("36-Month", f"{score_36m:.1f}/10")
        h4.metric("60-Month", f"{score_60m:.1f}/10")
        
        r1, r2, r3, r4 = st.columns(4)
        r1.write(f"Trend: {'Bullish' if price > ma_200 else 'Weak'}")
        r2.write(f"Growth
