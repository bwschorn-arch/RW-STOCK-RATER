import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="Market Mind AI v11", layout="wide")

# CSS: Nuclear Contrast & High-Visibility UI
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 14px !important; }
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    [data-testid="stTextInput"] { width: 220px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    .stAlert { background-color: #1E293B !important; border: 1px solid #3B82F6 !important; color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 52-Week Range
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"**52W Range:** **${low:,.2f}** — **${high:,.2f}**")
        st.progress(min(max(percent, 0.0), 1.0))
    else:
        st.write("52W Data N/A")

st.title("🧠 Market Mind AI")
ticker_input = st.text_input("Ticker:", "BMNR").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- DATA GATHERING ---
        price = info.get('currentPrice', 0)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 0)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 0)
        debt = info.get('debtToEquity', 0)
        ma200 = info.get('twoHundredDayAverage', 1)

        # Market Cap Scaling Fix
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"

        # MOMENT SCORE (High-Conviction Logic)
        q_score = (max(roe, -0.2) * 5) + (max(margin, -0.2) * 10)
        v_score = 3 if pe < 30 else (2 if pe < 50 else 1)
        m_score = (q_score + v_score + (rev_g * 10)) / 1.6
        moment_score = min(max(m_score, 1.0), 10.0)

        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} | Moment Score: {moment_score:.1f}/10")
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4: draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS & RATIONALE
        st.subheader("Strategic Outlook & Rationale")
        base = 7.0 if (m_cap > 5e11 and roe > 0.1) else 4.0
        
        # Smoothed Scoring (Prevents catastrophic drops for negative ROE/Margin)
        s12 = base + ((price > ma200) * 1.5)
        s24 = base + (max(roe, -0.5) * 2)
        s36 = base + (max(margin, -0.5) * 5)
        s60 = base + (1.0 if (debt and debt < 60) else 0)
        
        # Final scores capped at 1.0 minimum
        scores = [max(s12, 1.0), max(s24, 1.0), max(s36, 1.0), max(s60, 1.0)]
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{scores[0]:.1f}/10")
        h2.metric("24-Month", f"{scores[1]:.1f}/10")
        h3.metric("36-Month", f"{scores[2]:.1f}/10")
        h4.metric("60-Month", f"{scores[3]:.1f}/10")
        
        # RATIONALE ENGINE
        r1, r2, r3, r4 = st.columns(4)
        r1.caption(f"{'Strong momentum' if price > ma200 else 'Weak technicals'} driving timing.")
        r2.caption(f"{'Earnings risk' if roe < 0 else 'Stable execution'} in 2yr window.")
        r3.caption(f"{'Margin pressure' if margin < 0 else 'Profit durability'} check.")
        r4.caption(f"{'Fortress balance sheet' if (debt and debt < 50) else 'High leverage risk'}.")

        # Divergence Alert
        if abs(scores[0] - scores[1]) > 2.0:
            st.warning(f"⚠️ **Divergence Alert:** Rating shifts between 12m and 24m because current price momentum is hiding {'poor operational earnings' if roe < 0 else 'valuation stretch'}.")

        st.divider()

        # 3) FULL PROJECTIONS
        st.subheader("Price Projections (Bear / Base / Bull)")
        p_cols = st.columns(4)
        horizons, h_labels = [1, 2, 3, 5], ["12m", "24m", "36m", "60m"]
        est_g = max(rev_g, 0.08)
        
        for i, h in enumerate(horizons):
            base_p = price * ((1 + est_g) ** h)
            with p_cols[i]:
                st.write(f"**{h_labels[i]}**")
                st.success(f"🐂 Bull: ${base_p * 1.3:,.2f}")
                st.info(f"📊 Base: ${base_p:,.2f}")
                st.error(f"🐻 Bear: ${base_p * 0.7:,.2f}")

        st.divider()

        # 4) FUNDAMENTALS & RISKS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Key Metrics")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• ROE: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        with c2:
            st.subheader("⚠️ Major Risks")
            risk_list = []
            if debt > 120: risk_list.append("High Leverage")
            if pe > 45: risk_list.append("Valuation Stretch")
            if info.get('beta', 1) > 1.5: risk_list.append("Volatility")
            if risk_list:
                for r in risk_list: st.write(f"• {r}")
            else: st.write("• No severe structural risks detected.")

    except Exception as e:
        st.error(f"Ticker {ticker_input} temporarily unavailable.")

st.sidebar.markdown("### Market Mind AI v11")
st.sidebar.write("Rationale Engine | Crypto-Proxy Awareness")
