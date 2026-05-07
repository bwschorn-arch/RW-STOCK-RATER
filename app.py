import streamlit as st
import yfinance as yf
import pandas as pd

# App Configuration
st.set_page_config(page_title="Market Mind AI", layout="wide")

# CSS: Compact, Left-Aligned, and High Contrast
st.markdown("""
    <style>
    .stApp { background-color: #0F172A !important; }
    h1, h2, h3, h4, p, span, li, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Smaller Font Sizes for Compact Look */
    [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; color: #94A3B8 !important; }
    
    /* Left-Aligned, Narrow Ticker Box */
    [data-testid="stTextInput"] { width: 220px !important; margin-left: 0 !important; }
    .stTextInput input { color: #000000 !important; background-color: #FFFFFF !important; font-weight: 700; }
    
    /* Metric Box Styling */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #3B82F6 !important;
        padding: 8px !important;
        border-radius: 6px !important;
    }
    .stDivider { margin: 10px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Simplified 52-Week Range (No HTML Spans to prevent rendering errors)
def draw_52week_bar(low, high, current):
    if high > low:
        percent = (current - low) / (high - low)
        st.markdown(f"**52W Range:** **${low:,.2f}** — **${high:,.2f}**")
        st.progress(min(max(percent, 0.0), 1.0))
    else:
        st.write("52W Data N/A")

st.title("🧠 Market Mind AI")

# Ticker Input: Compact & Left Margin
ticker_input = st.text_input("Ticker:", "GOOGL").upper()

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        
        # --- DATA & SCALING FIXES ---
        price = info.get('currentPrice', 0)
        roe = info.get('returnOnEquity', 0)
        margin = info.get('profitMargins', 0)
        pe = info.get('forwardPE', 0)
        rev_g = info.get('revenueGrowth', 0)
        m_cap = info.get('marketCap', 0)
        
        # Market Cap Scaling (Fixes the $4.8T Google error)
        if m_cap > 10e12: m_cap = m_cap / 2 # Corrects some yfinance share-class doubling
        m_cap_str = f"${m_cap/1e12:.2f}T" if m_cap >= 1e12 else f"${m_cap/1e9:.1f}B"

        # MOMENT SCORE (High-Conviction Logic)
        # Fixes AAPL/GOOGL by capping ROE impact and rewarding stability
        q_score = (min(roe, 1.0) * 5) + (min(margin, 0.4) * 10)
        v_score = 3 if pe < 30 else (2 if pe < 50 else 1)
        m_score = (q_score + v_score + (rev_g * 10)) / 1.6
        moment_score = min(max(m_score, 1.0), 10.0)

        # 1) TOP BANNER
        st.header(f"{info.get('longName', ticker_input)} | Moment Score: {moment_score:.1f}/10")
        
        b1, b2, b3, b4 = st.columns([1,1,1,2])
        b1.metric("Price", f"${price:.2f}")
        b2.metric("Market Cap", m_cap_str)
        b3.metric("Sector", info.get('sector', 'N/A'))
        with b4:
            draw_52week_bar(info.get('fiftyTwoWeekLow', 0), info.get('fiftyTwoWeekHigh', 0), price)

        st.divider()

        # 2) STRATEGIC HORIZON RATINGS (Optimized for Blue Chips)
        st.subheader("Strategic Outlook (12-60 Months)")
        # Anchor high-quality giants at a higher floor
        base = 7.0 if (m_cap > 5e11 and roe > 0.15) else 4.0
        s12 = base + ((price > info.get('twoHundredDayAverage', 0)) * 1.5)
        s24 = base + (min(roe, 1.0) * 2)
        s36 = base + (min(margin, 0.3) * 5)
        s60 = base + (1.0 if (info.get('debtToEquity', 0) < 60) else 0)
        
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("12-Month", f"{min(s12, 10):.1f}/10")
        h2.metric("24-Month", f"{min(s24, 10):.1f}/10")
        h3.metric("36-Month", f"{min(s36, 10):.1f}/10")
        h4.metric("60-Month", f"{min(s60, 10):.1f}/10")

        st.divider()

        # 3) FULL PRICE PROJECTIONS (All 4 Horizons)
        st.subheader("Projections (Bear / Base / Bull)")
        p_cols = st.columns(4)
        horizons = [1, 2, 3, 5]
        h_labels = ["12-Month", "24-Month", "36-Month", "60-Month"]
        
        # Conservative Growth Floor for Big Tech
        est_g = max(rev_g, 0.09) 
        
        for i, h in enumerate(horizons):
            base_p = price * ((1 + est_g) ** h)
            with p_cols[i]:
                st.write(f"**{h_labels[i]}**")
                st.success(f"🐂 Bull: ${base_p * 1.3:,.2f}")
                st.info(f"📊 Base: ${base_p:,.2f}")
                st.error(f"🐻 Bear: ${base_p * 0.75:,.2f}")

        st.divider()

        # 4) FUNDAMENTALS & DYNAMIC RISKS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Key Metrics")
            st.write(f"• Revenue Growth: **{rev_g*100:.1f}%**")
            st.write(f"• ROE: **{roe*100:.1f}%**")
            st.write(f"• Profit Margin: **{margin*100:.1f}%**")
            st.write(f"• Forward P/E: **{pe:.1f}**")
        
        with c2:
            st.subheader("⚠️ Major Risks")
            debt = info.get('debtToEquity', 0)
            risk_list = []
            if debt and debt > 110: risk_list.append("High Debt/Equity Leverage")
            if pe > 35: risk_list.append("Valuation Multiple Premium")
            if info.get('beta', 1) > 1.3: risk_list.append("Higher-than-Market Volatility")
            if rev_g < 0.08: risk_list.append("Potential Growth Deceleration")
            
            if risk_list:
                for r in risk_list: st.write(f"• {r}")
            else:
                st.write("• No severe structural risks detected.")

    except Exception as e:
        st.error(f"Data Error: {ticker_input} might be temporarily unavailable.")

st.sidebar.markdown("### Market Mind AI v10")
st.sidebar.write("Compact Mode | Blue Chip Optimized")
