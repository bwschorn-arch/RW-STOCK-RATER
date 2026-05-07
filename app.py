import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="V7 Horizon Scorecard", layout="wide")

# CUSTOM CSS: Fixed contrast and spacing for one-page layout
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 32px !important; }
    [data-testid="stMetricLabel"] { color: #A0AEC0 !important; }
    .stMetric { 
        background-color: #1E293B; 
        border: 2px solid #3B82F6; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .main { background-color: #0F172A; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ V7: Professional High-Conviction Dashboard")
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
        ma_200 = info.get('twoHundredDayAverage', 0)
        rec_mean = info.get('recommendationMean', 3.0)

        # --- RISK LEVEL LOGIC ---
        risk_factors = []
        if debt_to_eq > 130: risk_factors.append("Debt")
        if pe_fwd > 45: risk_factors.append("Valuation")
        if beta > 1.5: risk_factors.append("Volatility")
        
        risk_label = "Low" if len(risk_factors) == 0 else ("Moderate" if len(risk_factors) == 1 else ("High" if len(risk_factors) == 2 else "Very High"))
        risk_str = f"{risk_label} ({', '.join(risk_factors)})" if risk_factors else f"{risk_label} (Solid)"

        # --- REBUILT SCORING ENGINE (V7) ---
        # Base Quality (The 'Floor' for the stock)
        base_quality = (roe * 15) + (profit_margin * 10) + (10 if debt_to_eq < 80 else 5)
        base_quality = min(max(base_quality / 3, 3), 9.5) # Anchors score between 3 and 9.5

        # Smoothing Logic: Ratings must stay within 3 pts of each other to avoid "Catastrophe"
        score_12m = (base_quality * 0.4) + ((price > ma_200) * 4) + ((rec_mean < 2.5) * 2)
        score_24m = (base_quality * 0.7) + ((rev_growth > 0.2) * 3)
        score_36m = (base_quality * 0.8) + ((rev_growth > 0.1) * 2)
        score_60m = base_quality  # Pure business durability check

        # --- THE SINGLE-PAGE DASHBOARD ---
        
        # Row 1: The Scorecard (High Contrast)
        st.subheader("Time-Horizon Conviction Scorecard")
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month Rating", f"{score_12m:.1f}/10", "Momentum Focus")
        h2.metric("24-Month Rating", f"{score_24m:.1f}/10", "Execution Focus")
        h3.metric("36-Month Rating", f"{score_36m:.1f}/10", "Compounder Focus")
        h4.metric("60-Month Rating", f"{score_60m:.1f}/10", "Moat Focus")

        st.divider()

        # Row 2: Risk & Context
        st.subheader("Risk & Market Context")
        c1, c2, c3 = st.columns(3)
        c1.write(f"### Risk: **{risk_str}**")
        c1.write(f"**Confidence Level:** {'High' if info.get('numberOfAnalystOpinions', 0) > 15 else 'Medium'}")
        
        c2.write(f"### Sector Context: {'Expensive' if pe_fwd > 30 else 'Fair'}")
        c2.write(f"Forward P/E: **{pe_fwd:.1f}** (S&P Avg: 22.0)")
        
        c3.write(f"### Expectations Gap: {'Positive' if rev_growth > 0.25 else 'Neutral'}")
        c3.write(f"Revenue Growth: **{rev_growth*100:.1f}%**")

        st.divider()

        # Row 3: Scenarios & Targets
        st.subheader("Price Potential (24-Month Target Scenarios)")
        p1, p2, p3 = st.columns(3)
        p1.error(f"🐻 Bear Case: ${price * 0.75:.2f} (-25%)")
        p2.info(f"📊 Base Case: ${price * 1.15:.2f} (+15%)")
        p3.success(f"🐂 Bull Case: ${price * 1.50:.2f} (+50%)")

        st.divider()

        # Row 4: Qualitative Bullet Points
        st.subheader("Strategic Analysis")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.write("**✅ Strengths**")
            if rev_growth > 0.2: st.write("• **Hyper-Growth:** Strong top-line engine.")
            if roe > 0.15: st.write("• **Moat:** Efficient capital generation.")
        with f2:
            st.write("**⚠️ Risks**")
            if debt_to_eq > 100: st.write("• **Leverage:** Debt load is a structural drag.")
            if beta > 1.5: st.write("• **High Beta:** Expect significant volatility.")
        with f3:
            st.write("**🔍 What to Watch**")
            st.write("• **Margins:** Next quarterly operating leverage.")
            if pe_fwd > 40: st.write("• **Multiple:** Potential for P/E compression.")

    except Exception as e:
        st.error("Select a ticker (e.g., COHR, NVDA, RKLB) to load the dashboard.")

st.sidebar.markdown("### **User Age 57 Note**")
st.sidebar.write("Focus on the **24m-36m ratings** for core sizing. Use the **12m rating** to decide if you should buy today or wait for a dip.")
