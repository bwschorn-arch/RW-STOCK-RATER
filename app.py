import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v20", layout="wide")

# CSS: Nuclear Contrast, Compact Mac UI, & Metric Formatting
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics: Force Large White Font & No Colors */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 22px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 12px !important; }
    
    /* Compact Metric Boxes */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 8px !important;
        border-radius: 6px !important;
    }
    
    /* Left-Aligned Ticker Box */
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    
    /* Fix for the persistent green box/delta issue */
    .range-text { color: white !important; background-color: transparent !important; font-weight: 600 !important; font-size: 14px !important; }
    
    .stDivider { margin: 10px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for Historical Returns
def get_historical_return(ticker_obj, years):
    try:
        hist = ticker_obj.history(period=f"{years}y")
        if len(hist) < (years * 200): return "Not Available"
        start, end = hist['Close'].iloc[0], hist['Close'].iloc[-1]
        ret = ((end - start) / start) * 100
        return f"{ret:+.1f}%"
    except: return "Not Available"

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        # Using HTML span to force color and prevent auto-formatting
        st.markdown(f"<span class='range-text'>52W Range: ${low:,.2f} — ${high:,.2f}</span>", unsafe_allow_html=True)
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
        debt = info.get('debtToEquity', 100)
        ma200 = info.get('twoHundredDayAverage', 1)

        # Asset Play Logic (Treasury boost for stocks like BMNR)
        asset_boost = 3.5 if (ticker_input == "BMNR" or "bitmine" in info.get('longName', '').lower()) else 0
        
        # Current Grade Calculation
        q_score = (max(roe, -0.5) * 5) + (max(margin, -0.5) * 10)
        m_score = (2.5 if price > ma200 else 1.0) + (min(rev_g, 0.4) * 8)
        v_score = 3 if pe < 30 else (2 if pe < 50 else 1)
        raw_grade = ((q_score + m_score + v_score) / 1.7) + asset_boost
        if m_cap < 2e9: raw_grade *= 0.85
        current_grade = min(max(raw_grade, 1.0), 10.0)

        # 1) TOP BANNER
        if m_cap > 5e12: m_cap = m_cap / 2 # Share class correction
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) Current Grade: {current_grade:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4: draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS
        st.subheader("Strategic Outlook (12-60 Months)")
        base = 7.0 if (m_cap > 5e11 or roe > 0.15) else 4.5
        s12, s24, s36, s60 = [base + ((price > ma200) * 1.5), base + (max(roe, -0.2) * 2.5), base + (max(margin, -0.2) * 4.5), base + (1.2 if m_cap > 1e10 else 0)]
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        # 3) RATIONALE ENGINE (THE "WHY")
        rationale_list = []
        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.0:
                time = f"{i*12+12}m to {i*12+24}m"
                trend = "Surge" if diff > 0 else "Decay"
                reason = "Capital Efficiency & Margin Anchor" if diff > 0 else "Operational Drag or Growth Normalization"
                if i == 0 and price < ma200: reason = "Momentum Lag vs. Long-term Fundamentals"
                rationale_list.append(f"**{time} {trend}:** Score shift of {abs(diff):.1f} pts. Primary driver: {reason}.")

        if rationale_list:
            st.subheader("Strategic Rationale")
            for r in rationale_list: st.info(r)

        st.divider()

        # 4) PRICE PROJECTIONS (With % and Growth Governor)
        st.subheader("Scenario Matrix (Bear / Base / Bull)")
        proj_growth = min(rev_g, 0.25) if rev_g > 0 else 0.08 
        p_cols = st.columns(4)
        h_years, h_labels = [1, 2, 3, 5], ["12m", "24m", "36m", "60m"]
        for i, year in enumerate(h_years):
            base_p = price * ((1 + proj_growth) ** year)
            with p_cols[i]:
                st.write(f"**{h_labels[i]} Outlook**")
                st.success(f"🐂 Bull: ${base_p*1.25:,.2f} ({((base_p*1.25/price)-1)*100:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({((base_p/price)-1)*100:+.1f}%)")
                st.error(f"🐻 Bear: ${base_p*0.75:,.2f} ({((base_p*0.75/price)-1)*100:+.1f}%)")

        st.divider()

        # 5) FUNDAMENTALS & RISKS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Fundamental Scorecard")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• ROE: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        with c2:
            st.subheader("⚠️ High-Priority Risks")
            risks = []
            if debt > 120: risks.append("Balance Sheet Leverage")
            if pe > 40: risks.append("Valuation Compression")
            if beta > 1.6: risks.append("High Beta Volatility")
            if risks:
                for r in risks: st.write(f"• {r}")
            else: st.write("• No severe structural risks detected.")

        st.divider()

        # 6) HISTORICAL PERFORMANCE
        st.subheader("Historical Returns")
        ret_cols = st.columns(4)
        with ret_cols[0]: st.metric("1-Year", get_historical_return(stock, 1))
        with ret_cols[1]: st.metric("3-Year", get_historical_return(stock, 3))
        with ret_cols[2]: st.metric("5-Year", get_historical_return(stock, 5))
        with ret_cols[3]: st.metric("10-Year", get_historical_return(stock, 10))

    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("V20: The Comprehensive Build")
