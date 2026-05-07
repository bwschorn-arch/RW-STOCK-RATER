import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="Pro Stock Scorecard", layout="wide")

st.title("🚀 Advanced High-Conviction Scorecard")
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
        ma_200 = info.get('twoHundredDayAverage', 0)
        
        # --- MULTI-FACTOR SCORING ENGINE ---
        # 1. Valuation Score (0-10)
        val_score = 10 if pe_fwd < 20 else (7 if pe_fwd < 35 else 4)
        
        # 2. Growth Score (0-10)
        growth_score = 10 if rev_growth > 0.3 else (7 if rev_growth > 0.15 else 4)
        
        # 3. Quality/Efficiency Score (0-10)
        qual_score = 10 if roe > 0.2 else (7 if roe > 0.1 else 4)
        
        # 4. Momentum Score (0-10)
        mom_score = 10 if price > ma_200 else 5

        # --- HORIZON-SPECIFIC WEIGHTING ---
        # 12 Months: 40% Momentum, 40% Valuation, 20% Growth
        score_12m = (mom_score * 0.4) + (val_score * 0.4) + (growth_score * 0.2)
        
        # 24 Months: 50% Growth, 30% Quality, 20% Valuation
        score_24m = (growth_score * 0.5) + (qual_score * 0.3) + (val_score * 0.2)
        
        # 60 Months: 60% Quality, 30% Growth, 10% Debt Health
        debt_penalty = 1 if debt_to_eq > 100 else 0
        score_60m = (qual_score * 0.6) + (growth_score * 0.3) + (10 * 0.1) - debt_penalty

        # --- THE DASHBOARD ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("12-Month Rating", f"{score_12m:.1f}/10")
            st.write("Focus: Momentum & Entry Price")
            
        with col2:
            st.metric("24-Month Rating", f"{score_24m:.1f}/10")
            st.write("Focus: Business Execution")
            
        with col3:
            st.metric("60-Month Rating", f"{score_60m:.1f}/10")
            st.write("Focus: Long-Term Moat")

        st.divider()

        # Streamlined Bullet Points
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Strengths")
            if rev_growth > 0.2: st.write("• **Hyper-Growth:** Revenue expanding >20% Y/Y.")
            if roe > 0.2: st.write("• **Capital Machine:** Excellent return on equity.")
            if price > ma_200: st.write("• **Strong Trend:** Trading above 200-day average.")
        
        with c2:
            st.subheader("⚠️ Risks")
            if pe_fwd > 40: st.write("• **Pricey:** Valuation is significantly above market average.")
            if debt_to_eq > 100: st.write("• **Leverage:** High debt could sting in a high-rate environment.")
            if profit_margin < 0.1: st.write("• **Thin Margins:** Little room for error in execution.")

        st.divider()
        
        # Bull/Bear Scenario
        st.subheader("Price Potential (Est.)")
        st.write(f"**Current:** ${price}")
        st.write(f"🐂 **Bull Case (24m):** ${price * 1.4:.2f} (+40%)")
        st.write(f"🐻 **Bear Case (24m):** ${price * 0.8:.2f} (-20%)")

    except Exception as e:
        st.error("Data not available for this ticker. Try a major symbol like NVDA or RKLB.")

st.sidebar.markdown("""
### **How to read this:**
- **9-10:** Rare "Conviction" Buy
- **7-8:** Strong Core Holding
- **5-6:** Speculative / Watchlist
- **<5:** Avoid / Overvalued
""")
