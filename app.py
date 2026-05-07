import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v22", layout="wide")

# CSS: Nuclear Contrast & Total Formatting Control
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Metrics Sizing */
    [data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 12px !important; }
    [data-testid="stMetric"] { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; padding: 10px !important; border-radius: 8px !important; }
    
    /* Left-Aligned, Narrow Ticker Box */
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; height: 32px; }
    
    /* THE GREEN BOX KILLER: Forces 52W range to be plain white text with NO background */
    .range-box-fix {
        color: #FFFFFF !important;
        background-color: transparent !important;
        border: none !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-bottom: 5px !important;
    }
    
    .stDivider { margin: 12px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for Historical Returns
def get_historical_return(ticker_obj, years):
    try:
        hist = ticker_obj.history(period=f"{years}y")
        if len(hist) < (years * 200): return "Not Available"
        start, end = hist['Close'].iloc[0], hist['Close'].iloc[-1]
        return f"{((end - start) / start) * 100:+.1f}%"
    except: return "Not Available"

# Helper for 52-week range (Nuclear Fix for the Green Box)
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"<div class='range-box-fix'>52W Range: ${low:,.2f} — ${high:,.2f}</div>", unsafe_allow_html=True)
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
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 1)
        beta = info.get('beta', 1.2)
        ma200 = info.get('twoHundredDayAverage', 1)

        # --- THE CALIBRATED ENGINE V22 ---
        # 1. MOAT STATUS
        moat_status = "None/Speculative"
        if roe > 0.20 and margin > 0.15: moat_status = "Wide Moat (Elite)"
        elif roe > 0.10 or margin > 0.08: moat_status = "Narrow Moat (Stable)"
        
        # 2. FUNDAMENTALS GRADE (A-F)
        # Calibrated for Blue Chips: 15% growth for a $2T company is an 'A'
        g_pts = (min(rev_g, 0.25) * 4) + (min(roe, 0.4) * 5) + (min(margin, 0.2) * 10)
        letter_grade = "F"
        if g_pts > 4.5: letter_grade = "A"
        elif g_pts > 3.0: letter_grade = "B"
        elif g_pts > 2.0: letter_grade = "C"
        elif g_pts > 1.0: letter_grade = "D"

        # 3. CURRENT MOMENT GRADE (1-10)
        # Unified with the Letter Grade logic + Momentum & Value
        m_pts = (2.0 if price > ma200 else 0.5)
        v_pts = (3.0 if pe < 30 else (1.5 if pe < 50 else 0.5))
        current_grade = min(max(g_pts + m_pts + v_pts, 1.0), 10.0)

        # 1) TOP BANNER
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
        base = 7.5 if letter_grade in ["A", "B"] else 4.5
        s12, s24, s36, s60 = [base + ((price > ma200) * 1.5), base + (max(roe, -0.2) * 2.5), base + (max(margin, -0.1) * 5), base + (1.2 if m_cap > 1e10 else 0)]
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        # 3) RATIONALE ENGINE
        rationale_list = []
        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 0.8:
                rationale_list.append(f"**{i*12+12}m to {i*12+24}m Shift:** {('Surge' if diff > 0 else 'Decay')} driven by {('Core Business Durability' if diff > 0 else 'Growth Normalization')}.")
        if rationale_list:
            for r in rationale_list: st.info(r)

        st.divider()

        # 4) PRICE PROJECTIONS (With Growth Governor)
        st.subheader("Scenario Matrix (Bear / Base / Bull)")
        proj_g = min(rev_g, 0.22) if rev_g > 0 else 0.08 
        p_cols = st.columns(4)
        for i, year in enumerate([1, 2, 3, 5]):
            base_p = price * ((1 + proj_g) ** year)
            with p_cols[i]:
                st.write(f"**{['12m','24m','36m','60m'][i]} Outlook**")
                st.success(f"🐂 Bull: ${base_p*1.25:,.2f} ({((base_p*1.25/price)-1)*100:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({((base_p/price)-1)*100:+.1f}%)")
                st.error(f"🐻 Bear: ${base_p*0.75:,.2f} ({((base_p*0.75/price)-1)*100:+.1f}%)")

        st.divider()

        # 5) FUNDAMENTAL SCORECARD & MOAT
        st.subheader("Fundamental Scorecard")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• Return on Equity: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        with c2:
            st.write(f"• **Economic Moat:** {moat_status}")
            st.write(f"### **Fundamentals Grade: {letter_grade}**")
            if debt > 120: st.warning("⚠️ High Leverage detected on balance sheet.")

        st.divider()

        # 6) HISTORICAL PERFORMANCE
        st.subheader("Historical Returns")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("1-Year", get_historical_return(stock, 1))
        r2.metric("3-Year", get_historical_return(stock, 3))
        r3.metric("5-Year", get_historical_return(stock, 5))
        r4.metric("10-Year", get_historical_return(stock, 10))

    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("V22: The Calibrated Build")
