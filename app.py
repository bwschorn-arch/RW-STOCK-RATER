import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="V8 Institutional Dashboard", layout="wide")

# CUSTOM CSS: High Contrast, Professional Spacing, and Metric Visibility
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 28px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #CBD5E1 !important; font-size: 14px !important; }
    .stMetric { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        padding: 15px; 
        border-radius: 8px; 
    }
    .main { background-color: #0F172A; color: #F8FAFC; }
    h1, h2, h3 { color: #F1F5F9 !important; }
    stMarkdown { color: #E2E8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    percent = (current - low) / (high - low)
    st.write(f"52W Low: ${low:.2f} | Current: ${current:.2f} | 52W High: ${high:.2f}")
    st.progress(min(max(percent, 0.0), 1.0))

st.title("🏛️ V8: Institutional High-Conviction Dashboard")
ticker_input = st.text_input("Enter Ticker Symbol:", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        hist = stock.history(period="1y")
        
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

        # DATA FOR SCORING
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
        # Calculation Logic
        quality_anchor = (roe * 20) + (profit_margin * 20) + (10 if debt_to_eq < 80 else 2)
        quality_anchor = min(max(quality_anchor / 5, 2), 9.5)
        
        risk_score = (1 if debt_to_eq > 120 else 0) + (1 if pe_fwd > 40 else 0) + (1 if beta > 1.5 else 0)
        risk_label = "Low" if risk_score == 0 else ("Moderate" if risk_score == 1 else "High")
        
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Overall Conviction", f"{quality_anchor:.1f}/10")
        s2.metric("Risk Level", risk_label)
        s3.
