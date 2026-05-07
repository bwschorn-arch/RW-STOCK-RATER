import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI", layout="wide")

# CSS: Nuclear Contrast & Left-Aligned Input
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics Sizing & Wrapping */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 14px !important; }
    
    /* Compact Metric Boxes */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }
    
    /* Force Left Alignment for Input */
    [data-testid="stTextInput"] { width: 250px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    
    .stDivider { margin: 15px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar (Fixed for Markdown rendering)
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"**52W Range:** ${low:,.2f} <span style='color:#3B82F6; font-weight:bold;'> — </span> ${high:,.2f}", unsafe_allow_html=True)
        st.progress(min(max(percent, 0.0), 1.0))
    else:
        st.write("52W Data Unavailable")

st.title("🧠 Market Mind AI")

# Ticker Input moved to the Left Margin
ticker_input = st.text_input("Enter Ticker:", "GOOGL").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- CALCULATION ENGINE ---
        price = info.get('currentPrice', 0)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 0)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 0)
        
        # Moment Score Logic (Optimized for Blue Chips)
        q_score = (min(roe, 1.0) * 4) + (min(margin, 0.4) * 10)
        v_score = 3 if pe < 25 else (2 if pe < 40 else 1)
        m_score = (q_score + v_score + (rev_g * 10)) / 1.5
        moment_score = min(max(m_score, 1.0), 10.0)

        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) | Moment Score: {moment_score:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS
        st.subheader("Time-Horizon Strategic Ratings")
        base = 6.5 if m_cap > 5e11 else 4.0
        s12 = base + ((price > info.get('twoHundredDayAverage', 0)) * 2) + ((rev_g > 0.1) * 1.5)
        s24 = base + (min(roe, 1.0) * 3)
        s36 = base + (min(margin, 0.3) * 10)
        s60 = base + (1.5 if (info.get('debtToEquity', 0) < 50) else 0)
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{min(s12, 10):.1f}/10")
        h2.metric("24-Month", f"{min(s24, 10):.1f}/10")
        h3.metric("36-Month", f"{min(s36, 10):.1f}/10")
        h4.metric("60-Month", f"{min(s60, 10):.1f}/10")

        st.divider()

        # 3) FULL PRICE PROJECTIONS
        st.subheader("Price Projections (Bear / Base / Bull)")
        proj_cols = st.columns(4)
        horizons = [1, 2, 3, 5]
        h_labels = ["12-Month", "24-Month", "36-Month", "60-Month"]
        
        expected_growth = max(rev_g, 0.08)
        
        for i, h in enumerate(horizons):
            base_p = price * ((1 + expected_growth) ** h)
            with proj_cols[i]:
                st.write(f"**{h_labels[i]}**")
                st.success(f"🐂 Bull: ${base_p * 1.25:,.2f}")
                st.info(f"📊 Base: ${base_p:,.2f}")
                st.error(f"🐻 Bear: ${base_p * 0.80:,.2f}")

        st.divider()

        # 4) FUNDAMENTALS & RISKS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Key Metrics")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• Return on Equity: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        
        with c2:
            st.subheader("⚠️ Major Risks")
            debt = info.get('debtToEquity', 0)
            risk_list = []
            if debt and debt > 120: risk_list.append("High Leverage")
            if pe > 45: risk_list.append("Valuation Premium")
            if info.get('beta', 1) > 1.5: risk_list.append("Market Volatility")
            
            if risk_list:
                for r in risk_list: st.write(f"• {r}")
            else:
                st.write("• No major structural risks detected.")

    except Exception as e:
        st.error(f"Analysis Error: {e}")

st.sidebar.markdown("### Market Mind AI v9.1")
st.sidebar.write("Left-Aligned Entry | Fixed 52W Range")
