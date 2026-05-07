import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v17", layout="wide")

# CSS: Nuclear Contrast, Compact UI
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 13px !important; }
    [data-testid="stMetric"] { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; padding: 10px !important; border-radius: 8px !important; }
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"52W Range: ${low:,.2f} — ${high:,.2f}")
        st.progress(min(max(percent, 0.0), 1.0))
    else: st.write("52W Range: N/A")

st.title("🧠 Market Mind AI")
ticker_input = st.text_input("Ticker:", "BEAM").upper()

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

        # --- THE "GROWTH GOVERNOR" (Fixes the $32k Price Bug) ---
        # We cap the projection growth rate at 25% for compounding purposes
        proj_growth = min(rev_g, 0.25) if rev_g > 0 else 0.08 

        # 1. CURRENT STOCK GRADE (V17 Logic)
        # Penalizes negative margins more heavily to keep Biotechs/Penny stocks realistic
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
        b1.metric("Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4: draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC RATINGS
        st.subheader("Strategic Outlook (12-60 Months)")
        base = 6.8 if (m_cap > 5e11 or roe > 0.15) else 4.2
        s12 = base + ((price > ma200) * 1.5)
        s24 = base + (max(roe, -0.2) * 2)
        s36 = base + (max(margin, -0.2) * 4)
        s60 = base + (1.0 if m_cap > 1e10 else 0)
        
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        # 3) RATIONALE ENGINE (FIXED)
        st.subheader("Strategic Rationale")
        rationale_found = False
        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.2:
                rationale_found = True
                time = f"{i*12+12}m to {i*12+24}m"
                trend = "Surge" if diff > 0 else "Decay"
                # Context-Aware Logic
                reason = "Capital Efficiency/Moat" if diff > 0 else "Speculative Burn/Valuation"
                if i == 0 and price < ma200: reason = "Negative Price Trend"
                st.info(f"**{time} {trend}:** {reason} is the primary driver for this {abs(diff):.1f} pt shift.")
        
        if not rationale_found: st.write("• Stable outlook based on current fundamental trends.")

        st.divider()

        # 4) SCENARIO MATRIX (WITH PERCENTAGES & GROWTH CAP)
        st.subheader("Price Projections (Normalized Growth)")
        p_cols = st.columns(4)
        h_labels = ["12m", "24m", "36m", "60m"]
        for i, year in enumerate([1, 2, 3, 5]):
            base_p = price * ((1 + proj_growth) ** year)
            bull_p, bear_p = base_p * 1.25, base_p * 0.70
            with p_cols[i]:
                st.write(f"**{h_labels[i]} Outlook**")
                st.success(f"🐂 Bull: ${bull_p:,.2f} ({((bull_p/price)-1)*100:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({((base_p/price)-1)*100:+.1f}%)")
                st.error(f"🐻 Bear: ${bear_p:,.2f} ({((bear_p/price)-1)*100:+.1f}%)")

        st.divider()

        # 5) FUNDAMENTALS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Key Metrics")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• ROE: **{roe*100:.1f}%**")
        with c2:
            st.subheader("⚠️ Top Risks")
            if margin < 0: st.write("• **Cash Burn:** Company is currently unprofitable.")
            if beta > 1.6: st.write("• **Volatility:** Stock moves significantly more than the S&P 500.")
            if rev_g > 1.0: st.write("• **Lumpy Revenue:** Growth may be driven by one-time payments.")

    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("V17: The Sanity Build")
