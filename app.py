import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# App Configuration
st.set_page_config(page_title="Market Mind AI v19", layout="wide")

# CSS: Nuclear Contrast & Compact UI
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics Sizing */
    [data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 13px !important; }
    [data-testid="stMetric"] { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; padding: 10px !important; border-radius: 8px !important; }
    
    /* Left-Aligned, Narrow Ticker Box */
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; height: 32px; }
    
    .stDivider { margin: 12px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for Historical Returns calculation
def get_hist_return(ticker_obj, years):
    try:
        # Fetch data for the specified period
        hist = ticker_obj.history(period=f"{years}y")
        if len(hist) < (years * 200): # Approximate trading days check
            return "Not Available"
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        ret = ((end_price - start_price) / start_price) * 100
        return f"{ret:+.1f}%"
    except:
        return "Not Available"

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.write(f"52W Range: ${low:,.2f} — ${high:,.2f}")
        st.progress(min(max(percent, 0.0), 1.0))
    else: st.write("52W Range: N/A")

st.title("🧠 Market Mind AI")
ticker_input = st.text_input("Ticker:", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- DATA GATHERING ---
        price = info.get('currentPrice', 1)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 29)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 1)
        beta = info.get('beta', 1.2)
        ma200 = info.get('twoHundredDayAverage', 1)

        # Growth Governor
        proj_growth = min(rev_g, 0.25) if rev_g > 0 else 0.08 

        # 1. MOMENT GRADE
        q_score = (max(roe, -0.5) * 4) + (max(margin, -0.5) * 8)
        m_score = (2.5 if price > ma200 else 1.0) + (min(rev_g, 0.4) * 8)
        v_score = 3 if pe < 30 else (2 if pe < 50 else 1)
        raw_grade = (q_score + m_score + v_score) / 1.8
        if m_cap < 2e9: raw_grade *= 0.8
        current_grade = min(max(raw_grade, 1.0), 10.0)

        # TOP BANNER
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) Current Grade: {current_grade:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4: draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC RATINGS & RATIONALE
        st.subheader("Strategic Outlook (12-60 Months)")
        base = 7.0 if (m_cap > 5e11 or roe > 0.15) else 4.5
        s12, s24, s36, s60 = [base + ((price > ma200) * 1.5), base + (max(roe, -0.2) * 2), base + (max(margin, -0.2) * 4), base + (1.0 if m_cap > 1e10 else 0)]
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        # Rationale Engine
        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.2:
                st.info(f"**{i*12+12}m to {i*12+24}m Shift:** {('Surge' if diff > 0 else 'Decay')} driven by {('Efficiency' if diff > 0 else 'Speculative Burn')}.")

        st.divider()

        # 3) PRICE PROJECTIONS
        st.subheader("Price Scenarios (Bull / Base / Bear)")
        p_cols = st.columns(4)
        for i, year in enumerate([1, 2, 3, 5]):
            base_p = price * ((1 + proj_growth) ** year)
            with p_cols[i]:
                st.write(f"**{['12m','24m','36m','60m'][i]}**")
                st.success(f"🐂 Bull: ${base_p*1.25:,.2f} ({((base_p*1.25/price)-1)*100:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({((base_p/price)-1)*100:+.1f}%)")
                st.error(f"🐻 Bear: ${base_p*0.7:,.2f} ({((base_p*0.7/price)-1)*100:+.1f}%)")

        st.divider()

        # 4) HISTORICAL PERFORMANCE (NEW SECTION)
        st.subheader("Historical Returns (Performance Track Record)")
        ret1 = get_hist_return(stock, 1)
        ret3 = get_hist_return(stock, 3)
        ret5 = get_hist_return(stock, 5)
        ret10 = get_hist_return(stock, 10)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("1-Year Return", ret1)
        c2.metric("3-Year Return", ret3)
        c3.metric("5-Year Return", ret5)
        c4.metric("10-Year Return", ret10)

    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("V19: Performance Pro")
