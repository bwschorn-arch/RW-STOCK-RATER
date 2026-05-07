import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="High-Conviction Scorecard", layout="wide")

st.title("🏗️ AI Infrastructure & Stock Scorecard")
ticker = st.text_input("Enter Stock Ticker (e.g., RKLB, COHR, NVDA):", "NVDA").upper()

if ticker:
    try:
        data = yf.Ticker(ticker)
        info = data.info
        
        # --- CALCULATIONS ---
        # Growth (Revenue Growth)
        rev_growth = info.get('revenueGrowth', 0) * 100
        # Value (P/E vs PEG)
        pe_ratio = info.get('forwardPE', 0)
        # Health (Debt to Equity)
        debt_to_equity = info.get('debtToEquity', 0)
        # Efficiency (ROIC - approximated by ROE for free data)
        roe = info.get('returnOnEquity', 0) * 100

        # --- SCORING LOGIC (1-10) ---
        score = 0
        if rev_growth > 20: score += 3
        elif rev_growth > 10: score += 2
        
        if pe_ratio < 25 and pe_ratio > 0: score += 2
        elif pe_ratio < 40: score += 1
        
        if debt_to_equity < 50: score += 2
        elif debt_to_equity < 100: score += 1
        
        if roe > 15: score += 3
        elif roe > 5: score += 1

        # --- THE DASHBOARD ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Overall Rating", f"{score}/10")
            st.write(f"**Current Price:** ${info.get('currentPrice', 'N/A')}")
            
        with col2:
            st.subheader("Time-Horizon Verdict")
            # Logic based on Score and Sector
            st.write(f"📅 **12-Month:** {'🟢 Bullish' if score > 7 else '🟡 Neutral'}")
            st.write(f"📅 **24-Month:** {'🟢 Strong Buy' if score > 6 else '🟡 Hold'}")
            st.write(f"📅 **5-Year:** {'🟢 High Conviction' if score > 5 else '🔴 Speculative'}")

        st.divider()
        
        # Bullet Points
        st.subheader("The 'Core Four' Pillars")
        st.markdown(f"""
        * **Valuation:** Forward P/E is **{pe_ratio:.2f}**. {'🟢 Fair' if pe_ratio < 30 else '🔴 Stretched'}
        * **Growth:** Revenue is growing at **{rev_growth:.1f}%**. {'🟢 Strong' if rev_growth > 15 else '🟡 Slow'}
        * **Health:** Debt-to-Equity is **{debt_to_equity:.1f}**. {'🟢 Healthy' if debt_to_equity < 70 else '🔴 Leveraged'}
        * **Efficiency:** Return on Equity is **{roe:.1f}%**. {'🟢 Efficient' if roe > 15 else '🟡 Average'}
        """)
        
    except Exception as e:
        st.error(f"Could not find data for {ticker}. Please check the symbol.")

st.sidebar.info("Tip: Use this for 5-year conviction plays. For 'Infrastructure' stocks, watch the Debt and ROE closely.")
