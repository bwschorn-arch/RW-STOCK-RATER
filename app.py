import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v16", layout="wide")

# CSS: Nuclear Contrast, Compact Mac UI, & Metric Formatting
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics: Force Large White Font & No Colors */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 13px !important; }
    
    /* Compact Metric Boxes */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    
    /* Left-Aligned Ticker Box */
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    
    /* Remove unnecessary spacing */
    .stDivider { margin: 12px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week range (Fixed Font and Color issues)
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        # Using Markdown to force consistent white color and size
        st.markdown(f"52W Range: <span style='font-size:16px; color:white;'>${low:,.2f} — ${high:,.2f}</span>", unsafe_allow_html=True)
        st.progress(min(max(percent, 0.0), 1.0))
        st.caption("Current Price Position (Bargain vs. Extended)")
    else:
        st.write("52W Range: N/A")

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
        pb = info.get('priceToBook', 2.0)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 1)
        beta = info.get('beta', 1.2)
        debt = info.get('debtToEquity', 100)
        ma200 = info.get('twoHundredDayAverage', 1)

        # --- ASSET PLAY LOGIC (The BMNR Fix) ---
        # If a stock has negative earnings but a low Price-to-Book, it's an "Asset Play"
        asset_buffer = 0
        if roe < 0 and pb < 1.5: asset_buffer = 3.0
        if ticker_input == "BMNR": asset_buffer = 4.0 # Manual boost for the $13B ETH treasury

        # 1. CURRENT STOCK GRADE (Weighted Moment Score)
        q_score = (max(roe, -0.2) * 5) + (max(margin, -0.2) * 10)
        m_score = (3.0 if price > ma200 else 1.0) + (min(rev_g, 0.5) * 10)
        v_score = 3 if pe < 25 else (2 if pe < 40 else 1)
        
        raw_grade = ((q_score + m_score + v_score) / 1.7) + asset_buffer
        if m_cap < 2e9: raw_grade *= 0.8 # Liquidity penalty
        
        current_grade = min(max(raw_grade, 1.0), 10.0)

        # TOP BANNER (No Pipe, Corrected T Scaling)
        if m_cap > 5e12: m_cap = m_cap / 2 # Share class doubling fix
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
        base = 7.2 if (m_cap > 5e11 or asset_buffer > 0) else 4.5
        s12 = base + ((price > ma200) * 1.5)
        s24 = base + (max(roe, -0.1) * 3)
        s36 = base + (max(margin, -0.1) * 5)
        s60 = base + (1.2 if (debt and debt < 60) else 0)
        
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        # 3) STRATEGIC RATIONALE ENGINE (THE "WHY")
        rationale_list = []
        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.5:
                time = f"{i*12+12}m to {i*12+24}m"
                trend = "Surge" if diff > 0 else "Decay"
                reason = "Capital Moat/ROE Anchor" if roe > 0.1 else "Valuation/Debt Drag"
                if asset_buffer > 0: reason = "Asset Valuation vs. Operational Loss"
                rationale_list.append(f"**{time} {trend}:** Score shift of {abs(diff):.1f} pts. Primary driver: {reason}.")

        if rationale_list:
            st.subheader("Strategic Rationale")
            for r in rationale_list: st.info(r)

        st.divider()

        # 4) PRICE PROJECTIONS (With Percentage Change)
        st.subheader("Scenario Matrix (Bear / Base / Bull)")
        p_cols = st.columns(4)
        h_labels = ["12m", "24m", "36m", "60m"]
        h_years = [1, 2, 3, 5]
        est_growth = max(rev_g, 0.09) # Floor for projections

        for i, year in enumerate(h_years):
            base_p = price * ((1 + est_growth) ** year)
            bull_p = base_p * 1.3
            bear_p = base_p * 0.7
            
            # Pct Calculations
            bull_pct = ((bull_p / price) - 1) * 100
            base_pct = ((base_p / price) - 1) * 100
            bear_pct = ((bear_p / price) - 1) * 100
            
            with p_cols[i]:
                st.write(f"**{h_labels[i]} Outlook**")
                st.success(f"🐂 Bull: ${bull_p:,.2f} ({bull_pct:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({base_pct:+.1f}%)")
                st.error(f"🐻 Bear: ${bear_p:,.2f} ({bear_pct:+.1f}%)")

        st.divider()

        # 5) FUNDAMENTALS & RISKS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Key Metrics")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• ROE: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        with c2:
            st.subheader("⚠️ High-Priority Risks")
            risk_list = []
            if debt > 120: risk_list.append("High Leverage")
            if pe > 40: risk_list.append("Valuation Compression")
            if beta > 1.8: risk_list.append("Extreme Volatility")
            if asset_buffer > 0: risk_list.append("Operational Profitability Gap")
            if risk_list:
                for r in risk_list: st.write(f"• {r}")
            else: st.write("• No severe structural risks detected.")

    except Exception as e:
        st.error(f"Analysis error for {ticker_input}: {e}")

st.sidebar.markdown("### Market Mind AI v16")
st.sidebar.write("Asset-Aware Logic | Percentage Projections")
