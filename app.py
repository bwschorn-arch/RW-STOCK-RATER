import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="V8.2 Institutional Dashboard", layout="wide")

# CSS: Nuclear Contrast (Force Navy background and Pure White text)
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; }
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 2px solid #334155 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    percent = (current - low) / (high - low)
    st.write(f"52W Low: ${low:.2f} | Current: ${current:.2f} | 52W High: ${high:.2f}")
    st.progress(min(max(percent, 0.0), 1.0))

st.title("🏛️ V8.2: High-Conviction Institutional Dashboard")
ticker_input = st.text_input("Enter Ticker Symbol:", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input})")
        b1, b2, b3, b4, b5 = st.columns(5)
        price = info.get('currentPrice', 0)
        change = info.get('regularMarketChangePercent', 0)
        b1.metric("Price", f"${price:.2f}", f"{change:.2f}%")
        b2.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B")
        b3.metric("Sector", info.get('sector', 'N/A'))
        b4.metric("Avg Vol", f"{info.get('averageVolume', 0)/1e6:.1f}M")
        with b5:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0.1), info.get('fiftyTwoWeekHigh', 1), price)

        st.divider()

        # DATA GATHERING
        rev_g = info.get('revenueGrowth', 0)
        pe = info.get('forwardPE', 0)
        debt = info.get('debtToEquity', 0)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        beta = info.get('beta', 1.0)
        ma200 = info.get('twoHundredDayAverage', 1)
        rec = info.get('recommendationMean', 3.0)

        # 2) CONVICTION STRIP
        quality = (roe * 20) + (margin * 20) + (10 if debt < 80 else 2)
        quality = min(max(quality / 5, 2), 9.5)
        
        risk_p = (1 if debt > 120 else 0) + (1 if pe > 40 else 0) + (1 if beta > 1.5 else 0)
        risk_l = "Low" if risk_p == 0 else ("Moderate" if risk_p == 1 else "High")
        
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Conviction", f"{quality:.1f}/10")
        s2.metric("Risk", risk_l)
        s3.metric("Confidence", "High" if info.get('numberOfAnalystOpinions', 0) > 15 else "Medium")
        s4.metric("Exp. Gap", "Positive" if rev_g > 0.2 else "Neutral")
        s5.metric("Context", f"{pe:.1f} P/E", delta=f"{pe - 22:.1f} vs S&P")

        st.divider()

        # 3) HORIZON RATINGS
        st.subheader("Time-Horizon Strategic Outlook")
        s12 = (quality * 0.4) + ((price > ma200) * 4) + ((rec < 2.5) * 2)
        s24 = (quality * 0.6) + ((rev_g > 0.2) * 3) + (1 if pe < 30 else 0)
        s36 = (quality * 0.8) + ((rev_g > 0.1) * 2)
        s60 = quality
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{s12:.1f}/10")
        h2.metric("24-Month", f"{s24:.1f}/10")
        h3.metric("36-Month", f"{s36:.1f}/10")
        h4.metric("60-Month", f"{s60:.1f}/10")
        
        r1, r2, r3, r4 = st.columns(4)
        r1.write(f"Momentum: {'Strong' if price > ma200 else 'Weak'}")
        r2.write(f"Growth: {'High' if rev_g > 0.2 else 'Steady'}")
        r3.write(f"ROE: {roe*100:.1f}%")
        r4.write("Durability Check")

        st.divider()

        # 4) SCENARIOS
        st.subheader("Price Scenarios (Bull Case)")
        p1, p2, p3, p4 = st.columns(4)
        p1.write(f"12m: **${price*1.2:.2f}**")
        p2.write(f"24m: **${price*1.45:.2f}**")
        p3.write(f"36m: **${price*1.7:.2f}**")
        p4.write(f"60m: **${price*2.2:.2f}**")

        st.divider()

        # 5) ANALYSIS
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("✅ Strengths")
            if rev_g > 0.2: st.write("• Strong Growth Engine")
            if roe > 0.15: st.write("• Efficient Capital Moat")
        with c2:
            st.subheader("⚠️ Risks")
            if debt > 100: st.write("• Leverage Concern")
            if pe > 40: st.write("• Valuation Stretch")
        with c3:
            st.subheader("🔍 Catalysts")
            st.write("• Earnings Execution")
            st.write("• Margin Stability")

    except Exception as e:
        st.error(f"Analysis Error: {e}")

st.sidebar.write("V8.2 Institutional Ready")
