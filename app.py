import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="Professional Stock Scorecard V5", layout="wide")

st.title("🛡️ Professional High-Conviction Dashboard")
ticker = st.text_input("Enter Stock Ticker:", "NVDA").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # --- DATA GATHERING ---
        price = info.get('currentPrice', 0)
        rev_growth = info.get('revenueGrowth', 0)
        pe_fwd = info.get('forwardPE', 0)
        debt_to_eq = info.get('debtToEquity', 0)
        roe = info.get('returnOnEquity', 0)
        profit_margin = info.get('profitMargins', 0)
        beta = info.get('beta', 1.0)
        analysts = info.get('numberOfAnalystOpinions', 0)
        rec_mean = info.get('recommendationMean', 3.0)
        ma_200 = info.get('twoHundredDayAverage', 0)
        peg = info.get('pegRatio', 1.0)

        # --- ADVANCED RISK & CONTEXT LOGIC ---
        risk_factors = []
        if debt_to_eq > 120: risk_factors.append("High Debt")
        if pe_fwd > 45: risk_factors.append("Valuation Stretch")
        if beta > 1.4: risk_factors.append("Price Volatility")
        if profit_margin < 0.08: risk_factors.append("Thin Margins")

        risk_label = "Low" if len(risk_factors) == 0 else ("Moderate" if len(risk_factors) <= 1 else ("High" if len(risk_factors) <= 2 else "Very High"))
        risk_desc = f"{risk_label} - Driven by: {', '.join(risk_factors)}" if risk_factors else f"{risk_label} - Solid Fundamentals"

        # Expectations Gap (Model vs Wall Street)
        # We compare rev_growth to the consensus recommendation as a proxy
        exp_gap = "Positive" if (rev_growth > 0.2 and rec_mean < 2.5) else "Neutral"

        # --- HORIZON SCORING (12, 24, 36, 60) ---
        score_12m = ((price > ma_200) * 4) + ((rec_mean < 2.2) * 4) + ((pe_fwd < 25) * 2)
        score_24m = ((rev_growth > 0.2) * 5) + ((profit_margin > 0.12) * 3) + ((peg < 1.5) * 2)
        score_36m = ((roe > 0.18) * 5) + ((debt_to_eq < 70) * 4) + (1 if exp_gap == "Positive" else 0)
        score_60m = ((roe > 0.25) * 4) + ((rev_growth > 0.1) * 3) + ((debt_to_eq < 40) * 3)

        # --- UI LAYOUT ---
        st.header(f"Strategy Analysis: {ticker}")
        
        # Summary Row
        s1, s2, s3 = st.columns(3)
        s1.metric("Risk Assessment", risk_label, help=risk_desc)
        s2.metric("Expectations Gap", exp_gap, help="Is the market underestimating this stock?")
        s3.metric("Sector Context", "Expensive" if pe_fwd > 30 else "Fair Value", delta=f"{pe_fwd - 22:.1f} vs S&P500")

        st.divider()

        # The Horizon Grid
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12m Rating", f"{score_12m:.1f}/10")
        h1.caption("Confidence: High")
        
        # Focus on 24-36m as requested for your age/style
        h2.metric("24m Rating", f"{score_24m:.1f}/10", delta="Core Horizon")
        h2.caption("Confidence: Medium-High")
        
        h3.metric("36m Rating", f"{score_36m:.1f}/10", delta="Core Horizon")
        h3.caption("Confidence: Medium")
        
        h4.metric("60m Rating", f"{score_60m:.1f}/10")
        h4.caption("Confidence: Low (Stretch)")

        st.divider()

        # Bull / Base / Bear
        st.subheader("Scenario Forecasting (24-Month Target)")
        p_col1, p_col2, p_col3 = st.columns(3)
        p_col1.error(f"🐻 Bear Case: ${price * 0.75:.2f} (-25%)")
        p_col2.info(f"📊 Base Case: ${price * 1.15:.2f} (+15%)")
        p_col3.success(f"🐂 Bull Case: ${price * 1.50:.2f} (+50%)")

        st.divider()

        # Decision Factors
        f1, f2, f3 = st.columns(3)
        with f1:
            st.subheader("✅ Why It Scores")
            if rev_growth > 0.2: st.write("• **Top-Line Engine:** Exceptional growth speed.")
            if roe > 0.15: st.write("• **Moat Strength:** High capital efficiency.")
            if peg < 1.2: st.write("• **Growth at Price:** PEG ratio is attractive.")
        with f2:
            st.subheader("⚠️ Why It Risks")
            if debt_to_eq > 100: st.write("• **Leverage:** Debt levels are a structural concern.")
            if pe_fwd > 40: st.write("• **Sentiment Risk:** High valuation depends on perfection.")
            if beta > 1.5: st.write("• **Volatility:** High Beta means larger swings.")
        with f3:
            st.subheader("🔍 What to Watch")
            st.write("• **Next Earnings:** Look for margin stability.")
            if pe_fwd > 35: st.write("• **Macro:** Sensitivity to interest rate hikes.")
            if rev_growth < 0.15: st.write("• **Growth Tap:** Watch for revenue deceleration.")

    except Exception as e:
        st.error("Enter a valid ticker to generate dashboard.")

st.sidebar.markdown(f"""
### **User Perspective (Age 57)**
Focus on the **24m and 36m** ratings. These are your primary decision windows.
- **12m** is for entry timing.
- **60m** is for checking business durability.
""")
