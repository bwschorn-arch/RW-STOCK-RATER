import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="V8.3 Rationale Dashboard", layout="wide")

# CSS: Nuclear Contrast & High-Visibility UI
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 2px solid #3B82F6 !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800 !important; font-size: 36px !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 16px !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 600; }
    .stAlert { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    percent = (current - low) / (high - low)
    st.write(f"**52W Range:** Low ${low:.2f} <span style='color:#3B82F6'>|</span> High ${high:.2f}", unsafe_allow_html=True)
    st.progress(min(max(percent, 0.0), 1.0))

st.title("🏛️ V8.3: Institutional Dashboard & Rationale Engine")
ticker_input = st.text_input("Enter Ticker Symbol (e.g. CVNA, NVDA, COHR):", "CVNA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input})")
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        price = info.get('currentPrice', 0)
        change = info.get('regularMarketChangePercent', 0)
        b1.metric("Current Price", f"${price:.2f}", f"{change:.2f}%")
        b2.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B")
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4:
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
        
        risk_p = (1 if debt > 120 else 0) + (1 if pe > 45 else 0) + (1 if beta > 1.5 else 0)
        risk_l = "Low" if risk_p == 0 else ("Moderate" if risk_p == 1 else ("High" if risk_p == 2 else "Extreme"))
        
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Conviction Anchor", f"{quality:.1f}/10")
        s2.metric("Risk Level", risk_l)
        s3.metric("Confidence", "High" if info.get('numberOfAnalystOpinions', 0) > 15 else "Medium")
        s4.metric("Expectations Gap", "Positive" if rev_g > 0.25 else "Neutral")
        s5.metric("Sector Context", f"{pe:.1f} P/E", delta=f"{pe - 22:.1f} vs S&P")

        st.divider()

        # 3) HORIZON RATINGS
        st.subheader("Time-Horizon Strategic Ratings")
        s12 = (quality * 0.4) + ((price > ma200) * 4) + ((rec < 2.5) * 2)
        s24 = (quality * 0.6) + ((rev_g > 0.2) * 3) + (1 if pe < 30 else 0)
        s36 = (quality * 0.8) + ((rev_g > 0.1) * 2)
        s60 = quality
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{s12:.1f}/10")
        h2.metric("24-Month", f"{s24:.1f}/10")
        h3.metric("36-Month", f"{s36:.1f}/10")
        h4.metric("60-Month", f"{s60:.1f}/10")
        
        # DYNAMIC RATIONALE ENGINE
        st.info(f"**12m Rationale:** {'Momentum is strong' if price > ma200 else 'Trend is weak'}, coupled with analyst sentiment.")
        st.info(f"**24m/36m Rationale:** Execution based on {rev_g*100:.1f}% growth and {roe*100:.1f}% ROE.")
        
        if abs(s12 - s24) > 1.5:
            st.warning(f"⚠️ **Divergence Alert (The 'Why'):** The rating drops between 12m and 24m because current price momentum is masking structural issues (Debt: {debt:.1f}, Margin: {margin*100:.1f}%). The long-term durability is lower than the short-term buzz.")

        st.divider()

        # 4) SCENARIOS
        st.subheader("Price Potential (Bull Case Matrix)")
        p1, p2, p3, p4 = st.columns(4)
        p1.write(f"12m Target: **${price*1.2:.2f}**")
        p2.write(f"24m Target: **${price*1.45:.2f}**")
        p3.write(f"36m Target: **${price*1.7:.2f}**")
        p4.write(f"60m Target: **${price*2.2:.2f}**")

        st.divider()

        # 5) FUNDAMENTALS & ANALYSIS
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("📊 Fundamental Grades")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• ROE: **{roe*100:.1f}%**")
            st.write(f"• Debt/Equity: **{debt:.1f}**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
        with c2:
            st.subheader("⚠️ Top Risks")
            if debt > 120: st.write("• **High Leverage:** Balance sheet is a structural drag.")
            if pe > 40: st.write("• **Valuation Stretch:** Trading at a heavy premium.")
            if beta > 1.5: st.write("• **High Beta:** Expect violent price swings.")
        with c3:
            st.subheader("🔍 Institutional Thesis")
            st.write(f"Recommended Action: **{'ADD/HOLD' if s24 > 6.5 else 'WATCH/AVOID'}**")
            st.write(f"Beta Factor: **{beta}**")
            st.write(f"Analyst Consensus: **{info.get('recommendationKey', 'N/A').title()}**")

    except Exception as e:
        st.error(f"Analysis Error: {e}")

st.sidebar.write("V8.3 Institutional Rationale Engine")
