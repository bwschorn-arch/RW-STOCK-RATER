import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="High-Conviction Pro", layout="wide")

st.title("🚀 High-Conviction AI & Infrastructure Scorecard")
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

        # --- RISK LEVEL LOGIC ---
        risk_score = 0
        if debt_to_eq > 150: risk_score += 3
        elif debt_to_eq > 80: risk_score += 1
        if pe_fwd > 50: risk_score += 2
        if beta > 1.5: risk_score += 2
        if profit_margin < 0.05: risk_score += 3
        
        risk_label = "Low" if risk_score <= 2 else ("Moderate" if risk_score <= 4 else ("High" if risk_score <= 7 else "Very High"))
        risk_color = "green" if risk_label == "Low" else ("orange" if risk_label == "Moderate" else "red")

        # --- CONFIDENCE SCORE LOGIC ---
        conf_val = "Medium"
        if analysts > 15 and rec_mean < 2.5: conf_val = "High"
        if analysts < 5: conf_val = "Low"

        # --- HORIZON-SPECIFIC RATINGS (0-10) ---
        # 12-Month: Focus on Momentum & Analyst Revisions
        mom_factor = 10 if price > ma_200 else 4
        rev_factor = 10 if rec_mean < 2.2 else 5
        score_12m = (mom_factor * 0.5) + (rev_factor * 0.3) + (pe_fwd < 30) * 2
        
        # 24-Month: Focus on Growth & Execution
        growth_factor = 10 if rev_growth > 0.25 else 5
        margin_factor = 10 if profit_margin > 0.15 else 5
        score_24m = (growth_factor * 0.6) + (margin_factor * 0.4)
        
        # 60-Month: Focus on Durability & ROE
        roe_factor = 10 if roe > 0.2 else 5
        debt_factor = 10 if debt_to_eq < 50 else 3
        score_60m = (roe_factor * 0.6) + (debt_factor * 0.4)

        # --- THE UI LAYOUT ---
        st.header(f"Analysis for {ticker}")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Risk Level", risk_label)
            st.write(f"Confidence: **{conf_val}**")
        with m2:
            st.metric("12-Month Rating", f"{score_12m:.1f}/10")
            st.write("Focus: Momentum")
        with m3:
            st.metric("60-Month Rating", f"{score_60m:.1f}/10")
            st.write("Focus: Durability")

        st.divider()

        # Horizon Verdicts
        v1, v2, v3 = st.columns(3)
        v1.info(f"**12m Outlook:** {'🟢 Bullish' if score_12m > 7 else '🟡 Neutral'}")
        v2.success(f"**24m Outlook:** {'🟢 Strong Buy' if score_24m > 7 else '🟡 Hold'}")
        v3.warning(f"**5y Outlook:** {'🟢 Conviction' if score_60m > 7 else '🟡 Speculative'}")

        # Price Spread
        st.subheader("Price Potential & Spread")
        bull = price * 1.45
        bear = price * 0.75
        st.write(f"Current: **${price:.2f}** | Bull Case: **${bull:.2f}** (+45%) | Bear Case: **${bear:.2f}** (-25%)")
        st.progress(0.4, text=f"Uncertainty Spread: {((bull-bear)/price)*100:.0f}%")

        st.divider()

        # Detailed Bullets
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Strengths")
            if rev_growth > 0.2: st.write("• **Hyper-Growth:** Strong top-line expansion.")
            if roe > 0.15: st.write("• **Efficiency:** Management is generating high ROE.")
            if analysts > 20: st.write("• **Institutional Backing:** High analyst coverage.")
        with c2:
            st.subheader("⚠️ Risks")
            if debt_to_eq > 100: st.write("• **High Leverage:** Balance sheet is heavy with debt.")
            if beta > 1.4: st.write("• **Volatile:** Stock swings harder than the market.")
            if pe_fwd > 45: st.write("• **Valuation:** Paying a high premium for growth.")

    except Exception as e:
        st.error("Select a ticker to see data.")

st.sidebar.markdown("### Decision Guardrails")
st.sidebar.write("- **High Risk / High Score**: Sizing matters. Don't go all-in.")
st.sidebar.write("- **Low Confidence**: Use small 'starter' positions.")
