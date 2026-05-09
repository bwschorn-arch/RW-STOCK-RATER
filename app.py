# ═══════════════════════════════════════════════════════════════
# MARKET MIND AI — v31
# Now with full Mutual Fund & ETF support
# 100% Free · Powered by yfinance
# ═══════════════════════════════════════════════════════════════

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Market Mind AI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #080d17; color: #cbd5e1; }
.stApp { background-color: #080d17; }
.block-container { padding: 1.2rem 2rem 3rem; max-width: 1440px; }
.mm-header { background: linear-gradient(135deg, #0d1526 0%, #0a1f3d 100%); border: 1px solid #1e3a5f; border-radius: 16px; padding: 26px 32px; margin-bottom: 18px; position: relative; overflow: hidden; }
.mm-header::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #3b82f6, #60a5fa, #3b82f6, transparent); }
.mm-ticker { font-family:'JetBrains Mono',monospace; font-size:12px; color:#3b82f6; letter-spacing:0.18em; text-transform:uppercase; }
.mm-company { font-size:30px; font-weight:800; color:#f1f5f9; margin:3px 0 6px; letter-spacing:-0.02em; }
.mm-price { font-family:'JetBrains Mono',monospace; font-size:44px; font-weight:600; color:#f8fafc; line-height:1; }
.mm-meta { font-family:'JetBrains Mono',monospace; font-size:11px; color:#475569; margin-top:5px; }
.mm-card { background: #0d1526; border: 1px solid #1e2d40; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }
.mm-section-label { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:500; letter-spacing:0.16em; text-transform:uppercase; color:#334155; margin-bottom:14px; }
.rating-wrap { text-align:center; background:#0d1526; border:1px solid #1e2d40; border-radius:12px; padding:18px 10px; }
.rating-wrap:hover { border-color:#3b82f6; }
.r-horizon { font-family:'JetBrains Mono',monospace; font-size:10px; color:#475569; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:6px; }
.r-score { font-family:'JetBrains Mono',monospace; font-size:42px; font-weight:700; line-height:1; }
.r-conf { font-family:'JetBrains Mono',monospace; font-size:10px; color:#334155; margin-top:4px; }
.sc-bull { background:#031a0f; border:1px solid #14532d; border-radius:10px; padding:16px; text-align:center; }
.sc-base { background:#0c1a2e; border:1px solid #1e3a5f; border-radius:10px; padding:16px; text-align:center; }
.sc-bear { background:#1a0808; border:1px solid #7f1d1d; border-radius:10px; padding:16px; text-align:center; }
.sc-label { font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:6px; }
.sc-price { font-family:'JetBrains Mono',monospace; font-size:26px; font-weight:600; line-height:1; }
.sc-pct { font-size:13px; font-weight:500; margin-top:3px; }
.chip { display:inline-block; padding:3px 10px; border-radius:20px; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:500; margin:2px; }
.chip-g { background:#052e16; color:#22c55e; border:1px solid #166534; }
.chip-r { background:#450a0a; color:#f87171; border:1px solid #991b1b; }
.chip-y { background:#1c1407; color:#facc15; border:1px solid #713f12; }
.chip-b { background:#0c1a2e; color:#60a5fa; border:1px solid #1e3a5f; }
.chip-n { background:#111827; color:#9ca3af; border:1px solid #374151; }
.chip-p { background:#1a0a2e; color:#c084fc; border:1px solid #7e22ce; }
.trow { display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px solid #1e2d40; font-family:'JetBrains Mono',monospace; font-size:11px; }
.trow-label { color:#64748b; }
.trow-val { color:#e2e8f0; }
.alert-g { background:#031a0f; border-left:3px solid #22c55e; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#86efac; }
.alert-r { background:#1a0808; border-left:3px solid #ef4444; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#fca5a5; }
.alert-y { background:#1c1407; border-left:3px solid #eab308; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#fde047; }
.alert-b { background:#0c1a2e; border-left:3px solid #3b82f6; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#93c5fd; }
.alert-p { background:#1a0a2e; border-left:3px solid #a855f7; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#d8b4fe; }
div[data-testid="metric-container"] { background:#0d1526; border:1px solid #1e2d40; border-radius:10px; padding:14px; }
[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace !important; color:#f1f5f9 !important; font-size:20px !important; font-weight:600 !important; }
[data-testid="stMetricLabel"] { color:#64748b !important; font-size:11px !important; font-family:'JetBrains Mono',monospace !important; }
.stTextInput input { background:#0d1526 !important; border:1px solid #1e3a5f !important; border-radius:8px !important; color:#f1f5f9 !important; font-family:'JetBrains Mono',monospace !important; font-size:20px !important; font-weight:600 !important; text-transform:uppercase !important; letter-spacing:0.1em !important; }
.stButton button { background:#1e3a5f !important; color:#60a5fa !important; border:1px solid #3b82f6 !important; border-radius:8px !important; font-family:'Syne',sans-serif !important; font-weight:600 !important; }
.stTabs [data-baseweb="tab"] { font-family:'Syne',sans-serif; color:#64748b; }
.stTabs [data-baseweb="tab-list"] { background:#0d1526; }
hr { border-color:#1e2d40 !important; }
.footer { text-align:center; color:#1e293b; font-family:'JetBrains Mono',monospace; font-size:10px; margin-top:40px; padding:20px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════

def safe(d, key, default=None):
    try:
        v = d.get(key, default)
        if v is None: return default
        if isinstance(v, float) and math.isnan(v): return default
        return v
    except: return default

def fmt(val, prefix="", suffix="", dec=1, fallback="—"):
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)): return fallback
        return f"{prefix}{val:,.{dec}f}{suffix}"
    except: return fallback

def fmt_big(val, fallback="—"):
    try:
        val = float(val)
        if abs(val) >= 1e12: return f"${val/1e12:.2f}T"
        if abs(val) >= 1e9:  return f"${val/1e9:.2f}B"
        if abs(val) >= 1e6:  return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"
    except: return fallback

def pct_str(val, fallback="—"):
    try:
        if val is None: return fallback
        return f"{val*100:+.1f}%"
    except: return fallback

def score_color(s):
    if s >= 8:   return "#22c55e"
    if s >= 6.5: return "#84cc16"
    if s >= 5:   return "#eab308"
    if s >= 3.5: return "#f97316"
    return "#ef4444"

def grade(s):
    if s >= 8.5: return "A+"
    if s >= 8.0: return "A"
    if s >= 7.0: return "A−"
    if s >= 6.5: return "B+"
    if s >= 6.0: return "B"
    if s >= 5.5: return "B−"
    if s >= 4.5: return "C+"
    if s >= 4.0: return "C"
    if s >= 3.0: return "D"
    return "F"

def trow(label, val, val_color="#e2e8f0"):
    return f'<div class="trow"><span class="trow-label">{label}</span><span class="trow-val" style="color:{val_color};">{val}</span></div>'

def is_fund(info):
    qt = (safe(info, 'quoteType') or '').upper()
    return qt in ['MUTUALFUND', 'ETF']


# ══════════════════════════════════════
# TECHNICAL INDICATORS
# ══════════════════════════════════════

def calc_rsi(prices, n=14):
    try:
        d = prices.diff()
        g = d.where(d > 0, 0.0).rolling(n).mean()
        l = (-d.where(d < 0, 0.0)).rolling(n).mean()
        return round(float((100 - 100/(1 + g/l)).iloc[-1]), 1)
    except: return None

def calc_macd(prices, fast=12, slow=26, sig=9):
    try:
        e1 = prices.ewm(span=fast, adjust=False).mean()
        e2 = prices.ewm(span=slow, adjust=False).mean()
        m  = e1 - e2; s = m.ewm(span=sig, adjust=False).mean()
        return {'macd': float(m.iloc[-1]), 'signal': float(s.iloc[-1]),
                'hist': float((m-s).iloc[-1]), 'bull': bool(m.iloc[-1] > s.iloc[-1])}
    except: return None

def get_ta(hist):
    try:
        c = hist['Close'].squeeze()
        cur   = float(c.iloc[-1])
        ma50  = float(c.rolling(50).mean().iloc[-1])
        ma200 = float(c.rolling(200).mean().iloc[-1])
        hi52  = float(c.rolling(252).max().iloc[-1])
        lo52  = float(c.rolling(252).min().iloc[-1])
        vol_avg = float(hist['Volume'].rolling(20).mean().iloc[-1])
        vol_cur = float(hist['Volume'].iloc[-1])
        return dict(cur=cur, ma50=ma50, ma200=ma200, hi52=hi52, lo52=lo52,
                    rsi=calc_rsi(c), macd=calc_macd(c),
                    above50=cur>ma50, above200=cur>ma200,
                    pct50=((cur-ma50)/ma50)*100, pct200=((cur-ma200)/ma200)*100,
                    pct_hi=((cur-hi52)/hi52)*100, pct_lo=((cur-lo52)/lo52)*100,
                    vol_ratio=vol_cur/vol_avg if vol_avg else 1)
    except: return {}

def calc_hist_annual_return(hist, years):
    """Calculate true annualized return from price history."""
    try:
        periods = int(years * 252)
        if len(hist) < int(periods * 0.6): return None
        actual_periods = min(len(hist) - 1, periods)
        start = float(hist['Close'].iloc[-actual_periods])
        end   = float(hist['Close'].iloc[-1])
        actual_years = actual_periods / 252
        if actual_years <= 0 or start <= 0: return None
        return (end / start) ** (1 / actual_years) - 1
    except: return None


# ══════════════════════════════════════
# SCORING ENGINE
# ══════════════════════════════════════

def score_fundamentals(info, fund_mode=False):
    if fund_mode:
        # For funds, fundamentals come from holdings quality — use available proxies
        s, pos, neg = 6.0, [], []
        pe = safe(info, 'trailingPE')
        if pe and pe > 0:
            if pe < 20:   s+=1.0; pos.append(f"Holdings P/E {pe:.1f}x — value territory")
            elif pe < 35: s+=0.5; pos.append(f"Holdings P/E {pe:.1f}x — reasonable")
            elif pe > 60: s-=1.0; neg.append(f"Holdings P/E {pe:.1f}x — expensive")
        pm = safe(info, 'profitMargins')
        if pm and pm > 0: s+=1.0; pos.append(f"Positive aggregate profit margin {pm*100:.1f}%")
        return round(max(0,min(10,s)),1), pos, neg

    s, pos, neg = 5.0, [], []
    rg = safe(info,'revenueGrowth')
    if rg is not None:
        if rg > .40:   s+=2.0; pos.append(f"Revenue growth {rg*100:.0f}% — exceptional")
        elif rg > .20: s+=1.2; pos.append(f"Revenue growth {rg*100:.0f}% — strong")
        elif rg > .08: s+=0.5; pos.append(f"Revenue growth {rg*100:.0f}% — solid")
        elif rg < 0:   s-=1.5; neg.append(f"Revenue declining {rg*100:.0f}%")
    eg = safe(info,'earningsGrowth')
    if eg is not None:
        if eg > .50:   s+=1.5; pos.append(f"EPS growth {eg*100:.0f}% — exceptional")
        elif eg > .20: s+=0.8; pos.append(f"EPS growth {eg*100:.0f}% — strong")
        elif eg < 0:   s-=1.0; neg.append(f"EPS declining {eg*100:.0f}%")
    pm = safe(info,'profitMargins')
    if pm is not None:
        if pm > .20:   s+=1.0; pos.append(f"Net margin {pm*100:.1f}% — excellent")
        elif pm > .08: s+=0.5; pos.append(f"Net margin {pm*100:.1f}% — healthy")
        elif pm < 0:   s-=1.2; neg.append(f"Unprofitable — margin {pm*100:.1f}%")
    gm = safe(info,'grossMargins')
    if gm is not None:
        if gm > .60:   s+=0.6; pos.append(f"Gross margin {gm*100:.1f}% — software-like")
        elif gm > .35: s+=0.3; pos.append(f"Gross margin {gm*100:.1f}%")
        elif gm < .20: s-=0.5; neg.append(f"Thin gross margins {gm*100:.1f}%")
    fcf = safe(info,'freeCashflow'); mc = safe(info,'marketCap')
    if fcf and mc and mc > 0:
        fy = fcf/mc
        if fy > .05:   s+=1.0; pos.append(f"FCF yield {fy*100:.1f}% — strong")
        elif fy > .02: s+=0.4; pos.append(f"FCF yield {fy*100:.1f}%")
        elif fy < 0:   s-=0.8; neg.append("Negative free cash flow")
    roe = safe(info,'returnOnEquity')
    if roe is not None:
        if roe > .25:   s+=0.8; pos.append(f"ROE {roe*100:.0f}% — elite capital returns")
        elif roe > .12: s+=0.4; pos.append(f"ROE {roe*100:.0f}% — good")
        elif roe < 0:   s-=0.6; neg.append(f"Negative ROE {roe*100:.0f}%")
    return round(max(0,min(10,s)),1), pos, neg

def score_fund_performance(hist):
    """Score a fund based on its historical return track record."""
    s, pos, neg = 5.0, [], []
    r1  = calc_hist_annual_return(hist, 1)
    r3  = calc_hist_annual_return(hist, 3)
    r5  = calc_hist_annual_return(hist, 5)
    r10 = calc_hist_annual_return(hist, 10)
    if r1  is not None:
        if r1 > .50:   s+=2.0; pos.append(f"1-year return {r1*100:.0f}% — exceptional")
        elif r1 > .20: s+=1.0; pos.append(f"1-year return {r1*100:.0f}% — strong")
        elif r1 < 0:   s-=1.5; neg.append(f"1-year return {r1*100:.0f}% — negative")
    if r5  is not None:
        if r5 > .25:   s+=2.0; pos.append(f"5-year annualized {r5*100:.0f}% — elite")
        elif r5 > .15: s+=1.2; pos.append(f"5-year annualized {r5*100:.0f}% — strong")
        elif r5 > .08: s+=0.5; pos.append(f"5-year annualized {r5*100:.0f}% — decent")
        elif r5 < 0:   s-=1.0; neg.append(f"5-year annualized negative {r5*100:.0f}%")
    if r10 is not None:
        if r10 > .20:  s+=1.5; pos.append(f"10-year annualized {r10*100:.0f}% — exceptional long-term track record")
        elif r10 > .12: s+=0.8; pos.append(f"10-year annualized {r10*100:.0f}% — solid long-term track record")
    if r3  is not None:
        if r3 > .30:   s+=0.5; pos.append(f"3-year annualized {r3*100:.0f}%")
    return round(max(0,min(10,s)),1), pos, neg

def score_valuation(info, fund_mode=False):
    s, pos, neg = 5.0, [], []
    if fund_mode:
        er = safe(info, 'annualReportExpenseRatio') or safe(info, 'totalExpenseRatio')
        if er is not None:
            if er < 0.005:   s+=2.0; pos.append(f"Very low expense ratio {er*100:.2f}%")
            elif er < 0.015: s+=1.0; pos.append(f"Low expense ratio {er*100:.2f}%")
            elif er > 0.05:  s-=1.0; neg.append(f"High expense ratio {er*100:.2f}%")
        pe = safe(info, 'trailingPE')
        if pe and pe > 0:
            if pe < 25:   s+=1.5
            elif pe < 40: s+=0.5
            elif pe > 60: s-=1.0; neg.append(f"High P/E on holdings {pe:.0f}x")
        return round(max(0,min(10,s)),1), pos, neg

    peg = safe(info,'pegRatio')
    if peg and peg > 0:
        if peg < 1.0:   s+=2.5; pos.append(f"PEG {peg:.2f} — growth at discount")
        elif peg < 2.0: s+=1.0; pos.append(f"PEG {peg:.2f} — fairly valued")
        elif peg < 3.5: s-=0.5; neg.append(f"PEG {peg:.2f} — moderately expensive")
        else:           s-=2.0; neg.append(f"PEG {peg:.2f} — expensive")
    fpe = safe(info,'forwardPE')
    if fpe and fpe > 0:
        if fpe < 15:    s+=1.5; pos.append(f"Forward P/E {fpe:.1f}x — cheap")
        elif fpe < 25:  s+=0.5; pos.append(f"Forward P/E {fpe:.1f}x — reasonable")
        elif fpe < 45:  s-=0.5; neg.append(f"Forward P/E {fpe:.1f}x — premium")
        elif fpe < 80:  s-=1.5; neg.append(f"Forward P/E {fpe:.1f}x — expensive")
        else:           s-=2.5; neg.append(f"Forward P/E {fpe:.1f}x — extreme premium")
    ps = safe(info,'priceToSalesTrailing12Months')
    if ps is not None:
        if ps < 3:    s+=1.0; pos.append(f"P/S {ps:.1f}x — attractive")
        elif ps < 8:  s+=0.3; pos.append(f"P/S {ps:.1f}x — moderate")
        elif ps > 20: s-=1.5; neg.append(f"P/S {ps:.1f}x — very expensive")
        elif ps > 12: s-=0.8; neg.append(f"P/S {ps:.1f}x — elevated")
    return round(max(0,min(10,s)),1), pos, neg

def score_balance_sheet(info, fund_mode=False):
    if fund_mode:
        return 7.0, ["Diversified fund structure provides built-in risk management"], []
    s, pos, neg = 5.0, [], []
    dte = safe(info,'debtToEquity')
    if dte is not None:
        if dte < 20:    s+=2.0; pos.append(f"Very low debt D/E {dte:.0f}%")
        elif dte < 80:  s+=1.0; pos.append(f"Manageable debt D/E {dte:.0f}%")
        elif dte > 250: s-=2.0; neg.append(f"High leverage D/E {dte:.0f}%")
        elif dte > 140: s-=1.0; neg
