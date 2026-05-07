import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="Institutional Stock Scorecard V6", layout="wide")

# Custom CSS for that "Terminal" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Institutional High-Conviction Dashboard")
st.sidebar.header("Analyst Settings")
persona = st.sidebar.selectbox("Analyst Persona", ["Senior Buy-Side", "Contrarian Value", "Growth Specialist"])
ticker = st.text_input("Enter Stock Ticker:", "COHR").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        # --- DATA GATHERING ---
        price = info.get('currentPrice', 0)
        rev_growth = info.get('revenueGrowth', 0)
        pe_fwd = info.get('forwardPE', 0)
        debt_to_eq = info.get('debtToEquity', 0)
        roe = info.get('returnOnEquity', 0)
        profit_margin = info.get('profitMargins', 0)
        beta = info.get('beta', 1.0)
        ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        insider_pct = info.get('heldPercentInsiders', 0) * 100
        inst_pct = info.get('heldPercentInstitutions', 0) * 100

        # --- CONTINUITY SCORING ENGINE (V6) ---
        # We calculate a 'Base Quality' score so ratings don't flip-flop wildly
        quality_score = (roe * 20) + (profit_margin * 20) + (10 if debt_to_eq < 100 else 5)
        quality_score = min(max(quality_score / 5, 1), 10)

        # 12m: Entry & Momentum (30% Quality, 70% Trend/Analysts)
        mom_score = 10 if price > ma_50 else 5
        score_12m = (quality_score * 0.3) + (mom_score * 0.7)
        
        # 24m/36m: Execution (70% Quality, 30% Growth)
        growth_score = 10 if rev_growth > 0.2 else 5
        score_24m = (quality_score * 0.7) + (growth_score * 0.3)
        score_36m = (quality_score * 0.8) + (growth_score * 0.2)
        
        # 60m: Durability (Must stay within 3 points of 36m to avoid 'catastrophic' jumps)
        score_60m = max(score_36m - 1.5, min(quality_score, score_36m + 1.5))

        # --- UI TABS ---
        tab1, tab2, tab3 = st.tabs(["📊 Snapshot", "🏗️ Fundamentals", "📉 Technicals"])

        with tab1:
            st.header(f"{info.get('longName', ticker)}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("12m Rating", f"{score_12m:.1f}/10")
            c2.metric("24m Rating", f"{score_24m:.1f}/10")
            c3.metric("36m Rating", f"{score_36m:.1f}/10")
            c4.metric("60m Rating", f"{score_60m:.1f}/10")
            
            st.divider()
            
            # Risk Level
            risk_val = "High" if debt_to_eq > 150 or beta > 1.5 else "Moderate"
            if debt_to_eq < 50 and beta < 1.1: risk_val = "Low"
            
            r1, r2 = st.columns(2)
            r1.write(f"### Risk Level: **{risk_val}**")
            r1.write(f"**Institutional Ownership:** {inst_pct:.1f}%")
            r2.write(f"### Analyst Target: **${info.get('targetMeanPrice', 0)}**")
            r2.write(f"**Upside:** {((info.get('targetMeanPrice', 0)/price)-1)*100:.1f}%")

        with tab2:
            st.subheader("Fundamental Integrity")
            f1, f2, f3 = st.columns(3)
            f1.write(f"**Rev Growth:** {rev_growth*100:.1f}%")
            f1.write(f"**ROE:** {roe*100:.1f}%")
            f2.write(f"**Forward P/E:** {pe_fwd:.2f}")
            f2.write(f"**PEG Ratio:** {info.get('pegRatio', 'N/A')}")
            f3.write(f"**Debt/Equity:** {debt_to_eq:.1f}")
            f3.write(f"**Profit Margin:** {profit_margin*100:.1f}%")
            
            st.subheader("Peer Comparison (Context)")
            st.write(f"Sector Avg P/E: **22.0** | This Stock: **{pe_fwd:.1f}**")
            st.progress(min(pe_fwd/100, 1.0), text="Valuation vs Sector Median")

        with tab3:
            st.subheader("Technical Picture")
            t1, t2 = st.columns(2)
            t1.write(f"**Above 200-Day MA:** {'✅ Yes' if price > ma_200 else '❌ No'}")
            t1.write(f"**Above 50-Day MA:** {'✅ Yes' if price > ma_50 else '❌ No'}")
            t2.write(f"**Beta (Volatility):** {beta}")
            t2.write(f"**52-Week Range:** ${info.get('fiftyTwoWeekLow')} - ${info.get('fiftyTwoWeekHigh')}")

        st.divider()
        st.subheader("🔍 AI Investment Thesis")
        st.write(f"**The Bull Case:** {ticker} is riding a {rev_growth*100:.0f}% growth wave with strong institutional backing ({inst_pct:.0f}%).")
        st.write(f"**The Bear Case:** {risk_val} risk detected. Debt-to-Equity is {debt_to_eq:.1f}, requiring perfect execution to maintain valuation.")

    except Exception as e:
        st.error(f"Data mapping error for {ticker}. Check symbol.")

st.sidebar.markdown("---")
st.sidebar.write("V6.0 Build: Institutional Integrity Mode")
