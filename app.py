import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v12", layout="wide")

# CSS: Nuclear Contrast, Compact UI, & Left-Aligned Input
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics Sizing */
    [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { font-size: 11px !important; color: #94A3B8 !important; }
    
    /* Compact Metric Boxes */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 8px !important;
        border-radius: 6px !important;
    }
    
    /* Left-Aligned, Compact Ticker Box */
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; height: 32px; }
    
    .stDivider { margin: 8px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"52W Range: ${low:,.2f} — ${high:,.2f}")
        st.progress(min(max(percent, 0.0), 1.0))
    else:
        st.write("52W Range: N/A")

st.title("🧠 Market Mind AI")

# Ticker Input: Left Margin
ticker_input = st.text_input("Ticker:", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- CALCULATION ENGINE V12 ---
        price = info.get('currentPrice', 1)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 29) # Market avg is 29 in May 2026
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 0)
        beta = info.get('beta', 1.2)
        debt = info.get('debtToEquity', 100)
        ma200 = info.get('twoHundredDayAverage', 1)
        
        # 1. GRADE CALCULATION (1-10)
        # Quality (40%) + Momentum (30%) + Value (30%)
        q_score = (min(roe, 1.0) * 5) + (min(margin, 0.4) * 10)
        m_score = (3.0 if price > ma200 else 1.0) + (min(rev_g, 0.5) * 10)
        v_score = 3 if pe < 25 else (2 if pe < 40 else 1)
        
        raw_grade = (q_score + m_score + v_score) / 1.7
        
        # Size & Liquidity Penalty
        if m_cap < 2e9: raw_grade *= 0.8  # 20% Penalty for Micro-caps
        if beta > 1.8: raw_grade *= 0.9   # 10% Penalty for extreme volatility
        
        current_grade = min(max(raw_grade, 1.0), 10.0)

        # 1) TOP BANNER
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) | Current Grade: {current_grade:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS
        st.subheader("Strategic Outlook (12-60 Months)")
        base = 7.2 if (m_cap > 1e11 and roe > 0.12) else 4.5
        
        s12 = base + ((price > ma200) * 1.5)
        s24 = base + (min(roe, 1.0) * 2)
        s36 = base + (min(margin, 0.3) * 5)
        s60 = base + (1.0 if debt < 50 else 0)
        
        scores = [min(s12, 10), min(s24, 10), min(s36, 10), min(s60, 10)]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        # 3) THE RATIONALE ENGINE (THE "WHY")
        st.subheader("Strategic Rationale")
        rationale_found = False
        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.5:
                rationale_found = True
                direction = "Improvement" if diff > 0 else "Decay"
                reason = "Strong operational margins" if margin > 0.15 else "Debt/Valuation pressure"
                st.info(f"**{direction} Alert ({i*12+12}m to {i*12+24}m):** Score shift of {abs(diff):.1f} points. {reason} becomes the primary driver in this window.")
        
        if not rationale_found:
            st.write("• Consistent outlook across all time horizons based on current stability.")

        st.divider()

        # 4) PRICE PROJECTIONS (All 4 Horizons)
        st.subheader("Scenario Matrix (Bear / Base / Bull)")
        p_cols = st.columns(4)
        h_labels = ["12-Month", "24-Month", "36-Month", "60-Month"]
        h_years = [1, 2, 3, 5]
        expected_growth = max(rev_g, 0.08)
        
        for i, year in enumerate(h_years):
            base_p = price * ((1 + expected_growth) ** year)
            with p_cols[i]:
                st.write(f"**{h_labels[i]}**")
                st.success(f"🐂 Bull: ${base_p * 1.3:,.2f}")
                st.info(f"📊 Base: ${base_p:,.2f}")
                st.error(f"🐻 Bear: ${base_p * 0.7:,.2f}")

        st.divider()

        # 5) FUNDAMENTALS & RISKS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Fundamental Scorecard")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• Return on Equity: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        
        with c2:
            st.subheader("⚠️ Top Risks")
            risks = []
            if debt > 100: risks.append("Balance Sheet Leverage")
            if pe > 40: risks.append("Valuation Compression")
            if beta > 1.4: risks.append("Excessive Volatility")
            if risks:
                for r in risks: st.write(f"• {r}")
            else:
                st.write("• No severe structural risks detected.")

    except Exception as e:
        st.error(f"Ticker Error: {e}")

st.sidebar.markdown("### Market Mind AI v12")
st.sidebar.write("Institutional Logic | Liquidity Penalties")
