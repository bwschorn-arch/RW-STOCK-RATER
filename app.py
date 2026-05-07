import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v25", layout="wide")

# CSS: Nuclear Contrast, Compact UI & Final Formatting
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics Sizing */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 22px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 12px !important; }
    [data-testid="stMetric"] { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; padding: 10px !important; border-radius: 8px !important; }
    
    /* Input Box */
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; height: 32px; }
    
    /* 52W Range Final Fix */
    .range-white-final { color: #FFFFFF !important; background: transparent !important; border: none !important; font-weight: 600 !important; font-size: 15px !important; margin-bottom: 5px; }
    
    .stDivider { margin: 12px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helpers
def get_historical_return(ticker_obj, years):
    try:
        hist = ticker_obj.history(period=f"{years}y")
        if len(hist) < (years * 200): return "N/A"
        start, end = hist['Close'].iloc[0], hist['Close'].iloc[-1]
        return f"{((end - start) / start) * 100:+.1f}%"
    except: return "N/A"

def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"<div class='range-white-final'>52W Range: ${low:,.2f} — ${high:,.2f}</div>", unsafe_allow_html=True)
        st.progress(min(max(percent, 0.0), 1.0))
    else: st.write("52W Range: N/A")

st.title("🧠 Market Mind AI")
ticker_input = st.text_input("Ticker:", "AMZN").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- DATA GATHERING ---
        price = info.get('currentPrice', 1)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 29)
        peg = info.get('pegRatio', 1.0)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 1)
        debt = info.get('debtToEquity', 0)
        beta = info.get('beta', 1.2)
        ma200 = info.get('twoHundredDayAverage', 1)

        # Grade Logic
        asset_boost = 3.5 if (ticker_input == "BMNR") else 0
        g_pts = (min(rev_g, 0.25) * 4) + (min(roe, 0.4) * 5) + (min(margin, 0.2) * 10)
        m_pts = (2.0 if price > ma200 else 0.5)
        v_pts = (3.0 if pe < 30 else (1.5 if pe < 55 else 0.5))
        current_grade = min(max(g_pts + m_pts + v_pts + asset_boost, 1.0), 10.0)
        
        letter_grade = "F"
        if g_pts > 4.2: letter_grade = "A"
        elif g_pts > 3.0: letter_grade = "B"
        elif g_pts > 1.8: letter_grade = "C"
        elif g_pts > 0.8: letter_grade = "D"

        # 1) TOP BANNER
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) Current Grade: {current_grade:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4: draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) HORIZON RATINGS & RATIONALE
        st.subheader("Strategic Outlook & Rationale")
        base = 7.5 if letter_grade in ["A", "B"] else 4.5
        s12, s24, s36, s60 = [base + ((price > ma200) * 1.5), base + (max(roe, -0.2) * 2), base + (max(margin, -0.1) * 4.5), base + (1.2 if m_cap > 1e10 else 0)]
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.0:
                st.info(f"**{i*12+12}m to {i*12+24}m Shift:** {('Surge' if diff > 0 else 'Decay')} driven by {('Durability' if diff > 0 else 'Normalization')}.")

        st.divider()

        # 3) PRICE SCENARIOS
        st.subheader("Scenario Matrix (Bull / Base / Bear)")
        proj_g = min(rev_g, 0.20) if rev_g > 0 else 0.08
        p_cols = st.columns(4)
        for i, year in enumerate([1, 2, 3, 5]):
            base_p = price * ((1 + proj_g) ** year)
            with p_cols[i]:
                st.write(f"**{['12m','24m','36m','60m'][i]} Outlook**")
                st.success(f"🐂 Bull: ${base_p*1.25:,.2f} ({((base_p*1.25/price)-1)*100:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({((base_p/price)-1)*100:+.1f}%)")
                st.error(f"🐻 Bear: ${base_p*0.75:,.2f} ({((base_p*0.75/price)-1)*100:+.1f}%)")

        st.divider()

        # 4) FUNDAMENTAL SCORECARD & THE "OFF TO THE RIGHT" DATA
        st.subheader("Fundamental Scorecard & Institutional Insights")
        st.markdown(f"### **Business Grade: {letter_grade}**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**Core Quality**")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• Return on Equity: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• **Moat:** {('Wide' if (roe > 0.2 and margin > 0.15) else 'Narrow')}")
        with c2:
            st.write("**Valuation & Technicals**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
            st.write(f"• PEG Ratio: **{peg:.2f}**")
            st.write(f"• Beta (Volatility): **{beta}**")
            st.write(f"• Above 200D MA: **{'✅' if price > ma200 else '❌'}**")
        with c3:
            st.write("**Analyst Sentiment**")
            st.write(f"• Consensus: **{info.get('recommendationKey', 'N/A').title()}**")
            st.write(f"• Avg Target: **${info.get('targetMeanPrice', 0)}**")
            st.write(f"• Upside: **{((info.get('targetMeanPrice', 0 or 1)/price)-1)*100:.1f}%**")
            if debt > 110: st.warning("⚠️ High Debt Alert")

        st.divider()

        # 5) HISTORICAL PERFORMANCE
        st.subheader("Historical Performance Track Record")
        r_cols = st.columns(4)
        with r_cols[0]: st.metric("1-Year", get_historical_return(stock, 1))
        with r_cols[1]: st.metric("3-Year", get_historical_return(stock, 3))
        with r_cols[2]: st.metric("5-Year", get_historical_return(stock, 5))
        with r_cols[3]: st.metric("10-Year", get_historical_return(stock, 10))

    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("V25: Total Restoration Build")
