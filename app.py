import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# App Configuration
st.set_page_config(page_title="V8 Institutional Dashboard", layout="wide")

# CUSTOM CSS: High Contrast, Professional Spacing, and Metric Visibility
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 28px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #CBD5E1 !important; font-size: 14px !important; }
    .stMetric { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        padding: 15px; 
        border-radius: 8px; 
    }
    .main { background-color: #0F172A; color: #F8FAFC; }
    h1, h2, h3 { color: #F1F5F9 !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-week bar
def draw_52week_bar(low, high, current):
    percent = (current - low) / (high - low)
    st.write(f"52W Low: ${low:.2f} | Current: ${current:.2f} | 52W High: ${high:.2f}")
    st.progress(min(max(percent, 0.0), 1.0))

st.title("🏛️ V8: Institutional High-Conviction Dashboard")
ticker_input = st.text_input("Enter Ticker Symbol:", "NVDA").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} ({ticker_input})")
        b1, b2, b3, b4, b5 = st.columns(5)
        price = info.get('currentPrice', 0)
        change = info.get('regularMarketChangePercent', 0)
        b1.metric("Current Price", f"${price:.2f}", f"{change:.2f}%")
        b2.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B")
        b3.metric("Sector", info.get('sector', 'N/A'))
        b4.metric("Avg Volume", f"{info.get('averageVolume', 0)/1e6:.1f}M")
        with b5:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # DATA FOR SCORING
        rev_growth = info.get('revenueGrowth', 0)
        pe_fwd = info.get('forwardPE', 0)
        debt_to_eq = info.get('debtToEquity', 0)
        roe = info.get('returnOnEquity', 0)
        profit_margin = info.get('profitMargins', 0)
        beta = info.get('beta', 1.0)
        rec_mean = info.get('recommendationMean', 3.0)
        ma_200 = info.get('twoHundredDayAverage', 1)
        peg = info.get('pegRatio', 1.0)

        # 2) CONVICTION STRIP
        quality_anchor = (roe * 20) + (profit_margin * 20) + (10 if debt_to_eq < 80 else 2)
        quality_anchor = min(max(quality_anchor / 5, 2), 9.5)
        
        risk_score = (1 if debt_to_eq > 120 else 0) + (1 if pe_fwd > 40 else 0) + (1 if beta > 1.5 else 0)
        risk_label = "Low" if risk_score == 0 else ("Moderate" if risk_score == 1 else "High")
        
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Overall Conviction", f"{quality_anchor:.1f}/10")
        s2.metric("Risk Level", risk_label)
        s3.metric("Confidence", "High" if info.get('numberOfAnalystOpinions', 0) > 15 else "Medium")
        s4.metric("Expectations Gap", "Positive" if rev_growth > 0.2 else "Neutral")
        s5.metric("Sector Context", f"{pe_fwd:.1f} P/E", delta=f"{pe_fwd - 22:.1f} vs S&P")

        st.divider()

        # 3) HORIZON RATINGS & RATIONALE
        st.subheader("Time-Horizon Strategic Outlook")
        
        # Scoring Logic
        score_12m = (quality_anchor * 0.4) + ((price > ma_200) * 4) + ((rec_mean < 2.5) * 2)
        score_24m = (quality_anchor * 0.6) + ((rev_growth > 0.2) * 3) + (1 if peg < 1.5 else 0)
        score_36m = (quality_anchor * 0.8) + ((rev_growth > 0.1) * 2)
        score_60m = quality_anchor
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{score_12m:.1f}/10")
        h2.metric("24-Month", f"{score_24m:.1f}/10")
        h3.metric("36-Month", f"{score_36m:.1f}/10")
        h4.metric("60-Month", f"{score_60m:.1f}/10")
        
        r1, r2, r3, r4 = st.columns(4)
        r1.caption(f"{'Momentum strength' if price > ma_200 else 'Technical weakness'} driving short term.")
        r2.caption(f"{'Strong execution' if rev_growth > 0.15 else 'Growth slowdown'} expected in 2yr window.")
        r3.caption(f"Driven by core capital efficiency (ROE: {roe*100:.1f}%).")
        r4.caption("Business durability based on debt and margins.")
        
        if abs(score_12m - score_24m) > 2.0:
            st.warning(f"⚠️ **Divergence Alert:** Rating shifts between 12m and 24m because {'momentum outpaces fundamentals' if score_12m > score_24m else 'business quality exceeds price trend'}. Proceed with sizing caution.")

        st.divider()

        # 4) PRICE SCENARIOS
        st.subheader("Price Potential (Scenario Matrix)")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.write("**12-Month Targets**")
            st.write(f"🐂 Bull: ${price*1.2:.2f}")
            st.write(f"🐻 Bear: ${price*0.85:.2f}")
        with p2:
            st.write("**24-Month Targets**")
            st.write(f"🐂 Bull: ${price*1.45:.2f}")
            st.write(f"🐻 Bear: ${price*0.75:.2f}")
        with p3:
            st.write("**36-Month Targets**")
            st.write(f"🐂 Bull: ${price*1.7:.2f}")
            st.write(f"🐻 Bear: ${price*0.65:.2f}")
        with p4:
            st.write("**60-Month Targets**")
            st.write(f"🐂 Bull: ${price*2.2:.2f}")
            st.write(f"🐻 Bear: ${price*0.5:.2f}")

        st.divider()

        # 5 & 6) FUNDAMENTALS & VALUATION
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.subheader("📊 Fundamental Scorecard")
            st.write(f"• **Revenue Growth:** {rev_growth*100:.1f}%")
            st.write(f"• **ROE:** {roe*100:.1f}% (Benchmark: 15%)")
            st.write(f"• **Net Debt / Equity:** {debt_to_eq:.1f}")
            st.write(f"• **Profit Margin:** {profit_margin*100:.1f}%")
        with col_f2:
            st.subheader("💎 Valuation Panel")
            st.write(f"• **Forward P/E:** {pe_fwd:.1f}")
            st.write(f"• **PEG Ratio:** {peg:.2f} (Ideal: < 1.5)")
            st.write(f"• **Price/Sales:** {info.get('priceToSalesTrailing12Months', 0):.2f}")

        st.divider()

        # 7, 8, 9) TECHNICALS, ANALYSTS, EARNINGS
        t1, t2, t3 = st.columns(3)
        with t1:
            st.subheader("📉 Technicals")
            st.write(f"• **Above 200D MA:** {'✅' if price > ma_200 else '❌'}")
            st.write(f"• **Above 50D MA:** {'✅' if price > info.get('fiftyDayAverage', 0) else '❌'}")
            st.write(f"• **Beta:** {beta}")
        with t2:
            st.subheader("🤝 Analyst Sentiment")
            st.write(f"• **Consensus:** {info.get('recommendationKey', 'N/A').title()}")
            st.write(f"• **Avg Target:** ${info.get('targetMeanPrice', 0)}")
            st.write(f"• **Implied Upside:** {((info.get('targetMeanPrice', 0)/price)-1)*100:.1f}%")
        with t3:
            st.subheader("📅 Earnings & Catalysts")
            st.write(f"• **Next Earnings:** {info.get('nextEarningsDate', 'TBA')}")
            st.write(f"• **Last Surprise:** {info.get('earningsQuarterlyGrowth', 0)*100:.1f}%")

        st.divider()

        # 10) RISK & THESIS
        st.subheader("Final Institutional Thesis")
        th1, th2 = st.columns(2)
        with th1:
            st.write("**✅ Strengths**")
            if rev_growth > 0.2: st.write("• Scalable revenue model with significant sector tailwinds.")
            if roe > 0.15: st.write("• Elite capital efficiency indicating a durable moat.")
        with th2:
            st.write("**⚠️ Risks**")
            if debt_to_eq > 100: st.write("• High leverage creates sensitivity to credit cycles.")
            if pe_fwd > 40: st.write("• Valuation requires flawless execution to sustain.")

        st.info(f"**Recommended Action:** {'ADD / HOLD' if quality_anchor > 7 else 'WATCH / AVOID'} | Horizon Preference: 24-36 Months")

    except Exception as e:
        st.error(f"Error analyzing {ticker_input}. Please ensure it is a valid ticker.")

st.sidebar.markdown(f"**V8.0: The Institutional Standard**")
st.sidebar.write("Optimized for 2-5 year conviction horizons.")
