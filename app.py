import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Market Mind AI v28", layout="wide")

# CSS: Nuclear Contrast & High-Visibility UI
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 22px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 12px !important; }
    [data-testid="stMetric"] { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; padding: 10px !important; border-radius: 8px !important; }
    [data-testid="stTextInput"] { width: 180px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; height: 32px; }
    .force-white-v28 { color: #FFFFFF !important; background: transparent !important; font-weight: 600 !important; font-size: 15px !important; display: block !important; margin-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

# Helper: Historical Returns
def get_historical_return(ticker_obj, years):
    try:
        hist = ticker_obj.history(period=f"{years}y")
        if len(hist) < (years * 200): return "N/A"
        start, end = hist['Close'].iloc[0], hist['Close'].iloc[-1]
        return f"{((end - start) / start) * 100:+.1f}%"
    except: return "N/A"

# Helper: 52-Week Range
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"<div class='force-white-v28'>52W Range: ${low:,.2f} — ${high:,.2f}</div>", unsafe_allow_html=True)
        st.progress(min(max(percent, 0.0), 1.0))
    else: st.write("52W Range: N/A")

st.title("🧠 Market Mind AI")
ticker_input = st.text_input("Ticker:", "RXRX").upper()

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
        target = info.get('targetMeanPrice', price * 1.1) # Fallback to +10%

        # 1. MOAT & REPORT CARD LOGIC
        moat_status = "None/Speculative"
        if roe > 0.18 and margin > 0.12: moat_status = "Wide Moat (Elite)"
        elif roe > 0.08 or margin > 0.08: moat_status = "Narrow Moat (Stable)"
        
        g_pts = (min(rev_g, 0.25) * 4) + (min(roe, 0.4) * 5) + (min(margin, 0.2) * 10)
        letter_grade = "F"
        if g_pts > 4.2: letter_grade = "A"
        elif g_pts > 3.0: letter_grade = "B"
        elif g_pts > 1.8: letter_grade = "C"
        elif g_pts > 0.8: letter_grade = "D"

        # 2. MOMENT GRADE (With RXRX Speculative Floor)
        m_pts = (2.0 if price > ma200 else 0.5)
        v_pts = (3.0 if pe < 35 else (1.5 if pe < 60 else 0.5))
        raw_moment = g_pts + m_pts + v_pts
        if m_cap > 1e9 and raw_moment < 2.5: raw_moment = 2.5 
        current_grade = min(max(raw_moment, 1.0), 10.0)

        # 1) TOP BANNER
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input}) Current Grade: {current_grade:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Current Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'Healthcare'))
        with b4: draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS & RATIONALE
        st.subheader("Strategic Outlook & Rationale")
        base = 7.5 if letter_grade in ["A", "B"] else 4.5
        s12, s24, s36, s60 = [base + ((price > ma200) * 1.5), base + (max(roe, -0.2) * 2), base + (max(margin, -0.1) * 4), base + (1.2 if m_cap > 1e10 else 0)]
        scores = [min(max(s, 1.0), 10.0) for s in [s12, s24, s36, s60]]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")

        for i in range(len(scores)-1):
            diff = scores[i+1] - scores[i]
            if abs(diff) >= 1.0:
                st.info(f"**{i*12+12}m to {i*12+24}m Shift:** {('Surge' if diff > 0 else 'Decay')} driven by {('Core Business Durability' if diff > 0 else 'Growth Normalization')}.")

        st.divider()

        # 3) ASYMMETRIC PRICE PROJECTIONS (V28 UPGRADE)
        st.subheader("Price Projections (Analyst-Anchored & Sector-Adjusted)")
        p_cols = st.columns(4)
        
        # Sector Multipliers for "Moonshot" potential
        is_spec = 1.8 if (letter_grade in ["D", "F", "Speculative"] or info.get('sector') == 'Healthcare') else 1.25
        
        for i, year in enumerate([1, 2, 3, 5]):
            # 12m Base Case uses Analyst Target if available
            if i == 0: 
                base_p = max(target, price * 1.08)
            else:
                # Compound based on the 12m Analyst trajectory, capped for sanity
                implied_g = (base_p / price) - 1
                base_p = price * ((1 + min(implied_g, 0.35)) ** year)
            
            bull_p = base_p * (is_spec ** (year**0.5)) # Asymmetric expansion
            bear_p = base_p * (0.65 ** (year**0.5))
            
            with p_cols[i]:
                st.write(f"**{['12m','24m','36m','60m'][i]} Outlook**")
                st.success(f"🐂 Bull: ${bull_p:,.2f} ({((bull_p/price)-1)*100:+.1f}%)")
                st.info(f"📊 Base: ${base_p:,.2f} ({((base_p/price)-1)*100:+.1f}%)")
                st.error(f"🐻 Bear: ${bear_p:,.2f} ({((bear_p/price)-1)*100:+.1f}%)")

        st.divider()

        # 4) FUNDAMENTAL SCORECARD & MOAT
        st.subheader("Fundamental Scorecard & Strategic Insights")
        st.markdown(f"### **Business Grade: {letter_grade}**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**Core Quality & Moat**")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• Return on Equity: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• **Economic Moat:** {moat_status}")
        with c2:
            st.write("**Valuation & Technicals**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
            st.write(f"• PEG Ratio: **{peg:.2f}**")
            st.write(f"• Beta (Volatility): **{beta}**")
            st.write(f"• Above 200D MA: **{'✅' if price > ma200 else '❌'}**")
        with c3:
            st.write("**Strategic Alerts**")
            if debt > 110: st.warning("⚠️ High Leverage detected.")
            if rev_g < 0: st.error("🚨 Declining Revenue detected.")
            st.write(f"• Analyst Target: **${target:,.2f}**")
            st.write(f"• Implied Upside: **{((target/price)-1)*100:.1f}%**")

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

st.sidebar.write("V28: The Asymmetric Build")
