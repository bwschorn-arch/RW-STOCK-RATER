# ═══════════════════════════════════════════════════════════════
# MARKET MIND AI — v32
# Major upgrade: Year-by-year growth decay model
# Full cyclicality awareness (memory, semis, energy, mining etc.)
# Analyst 12m target anchoring + multi-year decay toward long-term mean
# Stocks · Mutual Funds · ETFs · 100% Free · yfinance
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
.chip-o { background:#1c1005; color:#fb923c; border:1px solid #9a3412; }
.trow { display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px solid #1e2d40; font-family:'JetBrains Mono',monospace; font-size:11px; }
.trow-label { color:#64748b; }
.trow-val { color:#e2e8f0; }
.alert-g { background:#031a0f; border-left:3px solid #22c55e; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#86efac; }
.alert-r { background:#1a0808; border-left:3px solid #ef4444; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#fca5a5; }
.alert-y { background:#1c1407; border-left:3px solid #eab308; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#fde047; }
.alert-b { background:#0c1a2e; border-left:3px solid #3b82f6; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#93c5fd; }
.alert-p { background:#1a0a2e; border-left:3px solid #a855f7; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#d8b4fe; }
.alert-o { background:#1c1005; border-left:3px solid #f97316; border-radius:0 6px 6px 0; padding:10px 14px; margin:5px 0; font-size:12px; color:#fdba74; }
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

def is_fund_check(info):
    qt = (safe(info, 'quoteType') or '').upper()
    return qt in ['MUTUALFUND', 'ETF']

# ── Cyclicality detection ─────────────────────────────────────
CYCLICAL_KEYWORDS = [
    'semiconductor', 'memory', 'nand', 'dram', 'hbm',
    'semiconductor equipment', 'oil', 'gas', 'energy',
    'mining', 'steel', 'metals', 'chemicals', 'materials',
    'shipping', 'airlines', 'auto', 'homebuilding',
    'construction', 'agriculture', 'paper', 'lumber'
]

def detect_cyclical(info):
    industry  = (safe(info, 'industry')  or '').lower()
    sector_s  = (safe(info, 'sector')    or '').lower()
    combined  = industry + ' ' + sector_s
    return any(kw in combined for kw in CYCLICAL_KEYWORDS)

CYCLICAL_SECTOR_NAMES = {
    'semiconductor': 'Semiconductors & Memory',
    'memory': 'Semiconductors & Memory',
    'nand': 'Flash Memory',
    'dram': 'DRAM Memory',
    'oil': 'Energy',
    'gas': 'Energy',
    'mining': 'Mining & Metals',
    'steel': 'Steel & Metals',
    'chemicals': 'Chemicals',
    'shipping': 'Shipping',
    'airlines': 'Airlines',
    'auto': 'Automotive',
}

def cyclical_label(info):
    industry = (safe(info, 'industry') or '').lower()
    for kw, label in CYCLICAL_SECTOR_NAMES.items():
        if kw in industry:
            return label
    return "Cyclical Industry"


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
        elif dte > 140: s-=1.0; neg.append(f"Elevated debt D/E {dte:.0f}%")
    cr = safe(info,'currentRatio')
    if cr is not None:
        if cr > 2.5:   s+=1.5; pos.append(f"Current ratio {cr:.1f}x — very liquid")
        elif cr > 1.5: s+=0.8; pos.append(f"Current ratio {cr:.1f}x — healthy")
        elif cr < 1.0: s-=1.5; neg.append(f"Current ratio {cr:.1f}x — liquidity risk")
    cash = safe(info,'totalCash'); mc = safe(info,'marketCap')
    if cash and mc and mc > 0:
        cp = (cash/mc)*100
        if cp > 20:  s+=1.5; pos.append(f"Cash-rich {cp:.0f}% of market cap")
        elif cp > 8: s+=0.8; pos.append(f"Solid cash {cp:.0f}% of market cap")
    return round(max(0,min(10,s)),1), pos, neg

def score_momentum(ta, info):
    s, pos, neg = 5.0, [], []
    if not ta: return s, pos, neg
    rsi = ta.get('rsi')
    if rsi:
        if 45 < rsi < 68:   s+=1.5; pos.append(f"RSI {rsi:.0f} — healthy uptrend")
        elif rsi >= 68:      s+=0.3; pos.append(f"RSI {rsi:.0f} — strong but overbought")
        elif rsi < 35:       s+=1.0; pos.append(f"RSI {rsi:.0f} — oversold (contrarian)")
        elif rsi < 45:       s-=0.5; neg.append(f"RSI {rsi:.0f} — weak momentum")
    if ta.get('above200'):   s+=1.5; pos.append("Above 200-day MA — bull trend intact")
    else:                    s-=1.5; neg.append("Below 200-day MA — bear trend")
    if ta.get('above50'):    s+=1.0; pos.append("Above 50-day MA — near-term strength")
    else:                    s-=0.5; neg.append("Below 50-day MA")
    macd = ta.get('macd')
    if macd:
        if macd['bull']:     s+=0.8; pos.append("MACD bullish crossover")
        else:                s-=0.5; neg.append("MACD bearish signal")
    phi = ta.get('pct_hi', 0)
    if phi > -5:             s+=0.5; pos.append("Near 52-week high — momentum")
    elif phi < -40:          s+=1.0; pos.append(f"{abs(phi):.0f}% off 52-week high — deep value")
    return round(max(0,min(10,s)),1), pos, neg

def score_analyst(info, fund_mode=False):
    if fund_mode:
        return 7.0, ["Sector-focused fund with strong institutional support"], []
    s, pos, neg = 5.0, [], []
    rm = safe(info,'recommendationMean')
    if rm is not None:
        if rm <= 1.5:    s+=2.5; pos.append(f"Analyst consensus: Strong Buy ({rm:.1f}/5)")
        elif rm <= 2.0:  s+=1.5; pos.append(f"Analyst consensus: Buy ({rm:.1f}/5)")
        elif rm <= 2.5:  s+=0.5; pos.append(f"Analyst consensus: Moderate Buy ({rm:.1f}/5)")
        elif rm > 3.5:   s-=2.0; neg.append(f"Analyst consensus: Sell/Underweight ({rm:.1f}/5)")
        elif rm > 3.0:   s-=1.0; neg.append(f"Analyst consensus: Hold ({rm:.1f}/5)")
    cur = safe(info,'currentPrice') or safe(info,'regularMarketPrice')
    tgt = safe(info,'targetMeanPrice')
    if cur and tgt and cur > 0:
        up = ((tgt-cur)/cur)*100
        if up > 40:    s+=2.0; pos.append(f"Analyst PT implies {up:.0f}% upside")
        elif up > 20:  s+=1.2; pos.append(f"Analyst PT implies {up:.0f}% upside")
        elif up > 10:  s+=0.5; pos.append(f"Analyst PT implies {up:.0f}% upside")
        elif up < -10: s-=1.5; neg.append(f"Analyst PT implies {abs(up):.0f}% downside")
    return round(max(0,min(10,s)),1), pos, neg


# ══════════════════════════════════════
# RATINGS
# ══════════════════════════════════════

def calc_ratings(fs, vs, ms, bs, ans):
    quality = fs*0.45 + bs*0.30 + ans*0.25
    vdrag   = max(0, (7-vs)*0.28)
    r12 = fs*0.25 + ms*0.30 + vs*0.25 + ans*0.20 - vdrag*0.5
    r24 = fs*0.40 + vs*0.20 + ans*0.25 + bs*0.15  - vdrag*0.2
    r36 = fs*0.50 + bs*0.25 + ans*0.15 + vs*0.10
    r60 = fs*0.55 + bs*0.30 + ans*0.15
    if quality >= 6.0:
        r24 = max(r24, r12*0.88)
        r36 = max(r36, r24*0.92)
        r60 = max(r60, r36*0.90)
    def conf(v):
        if v >= 8:   return "High Confidence"
        if v >= 6.5: return "Medium-High"
        if v >= 5:   return "Medium"
        if v >= 3.5: return "Low-Medium"
        return "Low"
    return {k: {'score': round(max(1,min(10,v)),1), 'conf': conf(v)}
            for k,v in [('12m',r12),('24m',r24),('36m',r36),('60m',r60)]}


# ══════════════════════════════════════
# SCENARIO FORECASTING — v32 COMPLETE REWRITE
# Year-by-year decay model with cyclicality awareness
# ══════════════════════════════════════

def annual_growth_rate(yr, start_momentum, ltg, cyclical, scenario):
    """
    Calculate the growth rate for a specific future year.

    Growth decays exponentially from start_momentum toward ltg (long-term growth).
    For cyclical stocks: applies down-cycle headwinds in years 3 and 4.

    Args:
        yr:             Year number (1, 2, 3, 4, 5)
        start_momentum: Starting growth rate (from analyst implied or rg, capped)
        ltg:            Long-term structural growth rate (historical mean reversion target)
        cyclical:       Whether this is a cyclical industry
        scenario:       'base', 'bull', or 'bear'
    """
    if scenario == 'base':
        # Moderate decay — reverts to ltg over ~4-5 years
        decay = 0.75
        g = ltg + (start_momentum - ltg) * math.exp(-decay * (yr - 1))
        if cyclical and yr in [3, 4]:
            # Down-cycle: sharply compress growth, can go negative
            # Base case: think MU revenue dropping 40-60% from peak
            g = max(-0.30, g * 0.12)

    elif scenario == 'bull':
        # Slower decay — bull case maintains momentum longer
        decay = 0.40
        g = ltg + (start_momentum - ltg) * math.exp(-decay * (yr - 1))
        # Bull case floor: never drops below 70% of ltg
        g = max(ltg * 0.70, g)
        # Even in bull case for cyclicals, year 4 sees some normalization
        if cyclical and yr == 4:
            g = max(ltg * 0.50, g * 0.60)

    elif scenario == 'bear':
        # Fast decay — bear case reverts quickly and overshoots to the downside
        decay = 1.40
        g = ltg * 0.30 + (start_momentum - ltg * 0.30) * math.exp(-decay * (yr - 1))
        if cyclical and yr in [2, 3, 4]:
            # Bear case down-cycle: deep negative growth
            # Think memory prices crashing 50%+
            if yr == 2:   g = max(-0.20, g - 0.15)
            elif yr == 3: g = max(-0.45, g - 0.25)
            elif yr == 4: g = max(-0.35, g - 0.15)
        else:
            g = max(-0.35, g)

    return g


def gen_scenarios(price, rev_growth, info, hist=None):
    """
    Build Bear / Base / Bull scenarios for 12m, 24m, 36m, 60m.

    Key improvements in v32:
    - Year 1 ALWAYS anchored to analyst consensus price target (most accurate)
    - Years 2+ use year-by-year decay model (growth decays toward long-term mean)
    - Cyclical industries: explicit down-cycle modeled in years 3-4
    - Never blindly extrapolates one growth rate forward
    - Returns scenario assumptions for display in UI
    """
    current = price or 100

    # ── FUND / ETF PATH (unchanged from v31) ────────────────────
    qt = (safe(info, 'quoteType') or '').upper()
    fund_mode = qt in ['MUTUALFUND', 'ETF']

    if fund_mode and hist is not None and not hist.empty:
        r1  = calc_hist_annual_return(hist, 1)
        r3  = calc_hist_annual_return(hist, 3)
        r5  = calc_hist_annual_return(hist, 5)
        r10 = calc_hist_annual_return(hist, 10)
        weighted, total_w = 0.0, 0.0
        for ret, weight, cap in [(r1, 0.10, 0.80), (r3, 0.25, 0.80),
                                  (r5, 0.40, 0.80), (r10, 0.25, 0.80)]:
            if ret is not None:
                weighted += min(ret, cap) * weight
                total_w  += weight
        base_annual = (weighted / total_w) * 0.80 if total_w > 0 else 0.10
        bull_annual = min(max(r1 or base_annual, base_annual * 1.60), 1.00)
        bear_annual = max(-0.40, base_annual * 0.05)
        out = {}
        for yr, key in [(1,'12m'),(2,'24m'),(3,'36m'),(5,'60m')]:
            bear_p = max(0.01, current * ((1 + bear_annual) ** yr))
            base_p = max(bear_p * 1.15, current * ((1 + base_annual) ** yr))
            bull_p = max(base_p * 1.30, current * ((1 + bull_annual) ** yr))
            def sc(p): return {'p': round(p,2), 'pct': round(((p/current)-1)*100,1)}
            out[key] = {'bear': sc(bear_p), 'base': sc(base_p), 'bull': sc(bull_p)}
        return out, {}, False

    # ── STOCK PATH ───────────────────────────────────────────────

    rg = rev_growth if rev_growth else 0.10
    rg = max(-0.50, min(2.0, rg))  # allow up to 200% revenue growth

    # Analyst price targets (12-month consensus)
    target_mean = safe(info, 'targetMeanPrice')
    target_high = safe(info, 'targetHighPrice')
    target_low  = safe(info, 'targetLowPrice')

    # Cyclicality
    cyclical = detect_cyclical(info)

    # Long-term structural growth rate (mean reversion target)
    # Use 10-year historical price CAGR, capped to avoid supercycle distortion
    ltg = 0.08 if cyclical else 0.12
    if hist is not None and len(hist) > 252 * 4:
        hcagr = calc_hist_annual_return(hist, min(10, len(hist)//252))
        if hcagr is not None:
            # For cyclicals, cap at 20% to avoid supercycle inflation
            ltg = max(0.04, min(0.20 if cyclical else 0.30, hcagr * 0.75))

    # ── Set starting momentum for year 2+ decay ──────────────────
    # When analyst target is available, derive momentum from what
    # analysts expect (far more accurate than raw revenue growth).
    # This avoids the problem where rg=200% creates absurd year 2+ projections.
    if target_mean and target_mean > 0 and current > 0:
        implied_1y = (target_mean / current) - 1
        # Cap the momentum to avoid explosive compounding
        start_mom_base = max(-0.30, min(0.60, implied_1y))
        start_mom_bull = max(-0.20, min(0.80, (target_high/current - 1) if target_high else implied_1y * 1.30))
        start_mom_bear = max(-0.50, min(0.30, (target_low/current - 1) if target_low else implied_1y * 0.50))
    else:
        # No analyst target — use revenue growth, reasonably capped
        start_mom_base = max(-0.30, min(0.50, rg * 0.70))
        start_mom_bull = max(-0.20, min(0.70, rg * 1.10))
        start_mom_bear = max(-0.50, min(0.30, rg * 0.30))

    # ── Build prices year by year ─────────────────────────────────
    prices = {'base': {0: current}, 'bull': {0: current}, 'bear': {0: current}}
    assumptions = {}  # store for UI display

    for yr in range(1, 6):
        for scenario, mom in [('base', start_mom_base),
                               ('bull', start_mom_bull),
                               ('bear', start_mom_bear)]:
            if yr == 1:
                # ── YEAR 1: ANCHOR TO ANALYST TARGET ──────────────
                if target_mean and target_mean > 0:
                    if scenario == 'base':
                        p = target_mean
                    elif scenario == 'bull':
                        p = target_high if target_high else target_mean * 1.20
                        if cyclical: p = min(p, target_mean * 1.35)  # cap bull for cyclicals
                    elif scenario == 'bear':
                        p = target_low if target_low else target_mean * 0.78
                        if cyclical: p = min(p, current * 0.82)  # extra bear for cyclicals at cycle peak
                else:
                    # No analyst target: use modeled growth
                    g_1 = annual_growth_rate(1, mom, ltg, cyclical, scenario)
                    p = current * (1 + g_1)
                    assumptions[f'{scenario}_yr1'] = g_1
            else:
                # ── YEARS 2-5: DECAY MODEL ─────────────────────────
                g = annual_growth_rate(yr, mom, ltg, cyclical, scenario)
                p = prices[scenario][yr-1] * (1 + g)
                assumptions[f'{scenario}_yr{yr}'] = g

            prices[scenario][yr] = max(0.01, p)

    # Enforce logical ordering at each horizon: bull > base > bear
    for yr in range(1, 6):
        bear_p = prices['bear'][yr]
        base_p = max(bear_p * 1.08, prices['base'][yr])
        bull_p = max(base_p * 1.12, prices['bull'][yr])
        prices['base'][yr] = base_p
        prices['bull'][yr] = bull_p

    def sc(p):
        return {'p': round(p, 2), 'pct': round(((p / current) - 1) * 100, 1)}

    out = {}
    for yr, key in [(1,'12m'),(2,'24m'),(3,'36m'),(5,'60m')]:
        out[key] = {
            'bear': sc(prices['bear'][yr]),
            'base': sc(prices['base'][yr]),
            'bull': sc(prices['bull'][yr]),
        }

    return out, assumptions, cyclical


# ══════════════════════════════════════
# CHARTS
# ══════════════════════════════════════

BG = '#080d17'; GRID = '#1e2d40'; TXT = '#475569'

def chart_price(hist, ticker):
    c = hist['Close'].squeeze(); v = hist['Volume'].squeeze()
    ma50 = c.rolling(50).mean(); ma200 = c.rolling(200).mean()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.04)
    fig.add_trace(go.Scatter(x=hist.index, y=c, name='Price', line=dict(color='#3b82f6',width=1.8), fill='tozeroy', fillcolor='rgba(59,130,246,0.05)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=ma50, name='MA50', line=dict(color='#eab308',width=1,dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=ma200, name='MA200', line=dict(color='#ef4444',width=1,dash='dot')), row=1, col=1)
    colors = ['#22c55e' if c.iloc[i]>=c.iloc[i-1] else '#ef4444' for i in range(len(c))]
    fig.add_trace(go.Bar(x=hist.index, y=v, name='Volume', marker_color=colors, opacity=0.6), row=2, col=1)
    fig.update_layout(height=340, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor=BG, plot_bgcolor=BG, showlegend=True,
        font=dict(family='JetBrains Mono',color=TXT,size=10), legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(size=10)),
        xaxis2=dict(showgrid=True,gridcolor=GRID), yaxis=dict(showgrid=True,gridcolor=GRID,tickprefix='$'),
        yaxis2=dict(showgrid=False), title=dict(text=f"{ticker} — 2yr History | 50MA | 200MA | Volume", font=dict(size=11,color=TXT)))
    return fig

def chart_rsi(hist):
    c = hist['Close'].squeeze(); d = c.diff()
    g = d.where(d>0,0).rolling(14).mean(); l = (-d.where(d<0,0)).rolling(14).mean()
    rsi = (100-(100/(1+g/l))).dropna()
    fig = go.Figure()
    fig.add_hrect(y0=70,y1=100,fillcolor='rgba(239,68,68,0.07)',line_width=0)
    fig.add_hrect(y0=0,y1=30,fillcolor='rgba(34,197,94,0.07)',line_width=0)
    fig.add_hline(y=70,line=dict(color='#ef4444',width=1,dash='dash'))
    fig.add_hline(y=30,line=dict(color='#22c55e',width=1,dash='dash'))
    fig.add_hline(y=50,line=dict(color='#374151',width=1))
    fig.add_trace(go.Scatter(x=rsi.index,y=rsi,mode='lines',line=dict(color='#a78bfa',width=1.5),name='RSI'))
    fig.update_layout(height=160, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor=BG, plot_bgcolor=BG, showlegend=False,
        font=dict(family='JetBrains Mono',color=TXT,size=10), yaxis=dict(showgrid=True,gridcolor=GRID,range=[0,100]),
        xaxis=dict(showgrid=False), title=dict(text="RSI (14) — Overbought >70 | Oversold <30", font=dict(size=11,color=TXT)))
    return fig

def chart_scenarios(scenarios, price):
    ks = ['12m','24m','36m','60m']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=['Now']+ks, y=[price]+[scenarios[k]['bull']['p'] for k in ks], name='Bull 🐂', mode='lines+markers', line=dict(color='#22c55e',width=2), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=['Now']+ks, y=[price]+[scenarios[k]['base']['p'] for k in ks], name='Base 📊', mode='lines+markers', line=dict(color='#3b82f6',width=2), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=['Now']+ks, y=[price]+[scenarios[k]['bear']['p'] for k in ks], name='Bear 🐻', mode='lines+markers', line=dict(color='#ef4444',width=2), marker=dict(size=7)))
    fig.update_layout(height=280, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family='JetBrains Mono',color=TXT,size=11), xaxis=dict(showgrid=True,gridcolor=GRID),
        yaxis=dict(showgrid=True,gridcolor=GRID,tickprefix='$'), legend=dict(bgcolor='rgba(0,0,0,0)'),
        title=dict(text="Price Scenario Trajectories — Year-by-Year Decay Model", font=dict(size=11,color=TXT)))
    return fig

def chart_earnings(df):
    if df is None or df.empty: return None
    try:
        est = df.get('EPS Estimate', pd.Series()); act = df.get('Reported EPS', pd.Series())
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index.astype(str), y=est, name='Estimate', marker_color='#334155', opacity=0.8))
        colors = ['#22c55e' if (r >= e) else '#ef4444' for r,e in zip(act, est)]
        fig.add_trace(go.Bar(x=df.index.astype(str), y=act, name='Actual', marker_color=colors))
        fig.update_layout(height=220, margin=dict(l=0,r=0,t=8,b=0), barmode='group', paper_bgcolor=BG, plot_bgcolor=BG,
            font=dict(family='JetBrains Mono',color=TXT,size=10), yaxis=dict(showgrid=True,gridcolor=GRID),
            xaxis=dict(showgrid=False), legend=dict(bgcolor='rgba(0,0,0,0)'),
            title=dict(text="EPS: Estimate vs Actual (green=beat)", font=dict(size=11,color=TXT)))
        return fig
    except: return None


# ══════════════════════════════════════
# AI ANALYSIS
# ══════════════════════════════════════

def get_ai(ticker, company, summary, scores):
    try:
        from anthropic import Anthropic
        key = st.secrets.get("ANTHROPIC_API_KEY","")
        if not key: return None
        c = Anthropic(api_key=key)
        prompt = f"""You are a senior buy-side equity analyst with 20 years at a top-tier fund.
Analyze {ticker} ({company}): {summary}
Scores — Fundamentals:{scores['f']}/10 Valuation:{scores['v']}/10 Momentum:{scores['m']}/10 Balance Sheet:{scores['b']}/10 Analyst:{scores['a']}/10
Write exactly three sections:
BULL CASE: 2-3 sentences on the strongest reasons to own this for 3+ years.
BEAR CASE: 2-3 sentences on the most credible risks that could derail the thesis.
VERDICT: 2-3 sentences with a clear action: STRONG BUY / BUY / HOLD / TRIM / AVOID. State one metric or event that would change your view.
Be direct, specific, quantitative. No vague language."""
        r = c.messages.create(model="claude-sonnet-4-20250514", max_tokens=650, messages=[{"role":"user","content":prompt}])
        return r.content[0].text
    except: return None

def hist_return(stock, years):
    try:
        h = stock.history(period=f"{years}y")
        if len(h) < years*180: return "—"
        s, e = float(h['Close'].iloc[0]), float(h['Close'].iloc[-1])
        return f"{((e-s)/s)*100:+.1f}%"
    except: return "—"

def hist_return_annualized(stock, years):
    try:
        h = stock.history(period=f"{years}y")
        if len(h) < years*150: return "—"
        s, e = float(h['Close'].iloc[0]), float(h['Close'].iloc[-1])
        ann = ((e/s) ** (1/years) - 1) * 100
        return f"{ann:+.1f}%/yr"
    except: return "—"


# ══════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════

def main():
    st.markdown("""
    <div style="text-align:center;padding:12px 0 6px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.2em;color:#1e3a5f;text-transform:uppercase;margin-bottom:4px;">◈ PROFESSIONAL STOCK & FUND ANALYSIS</div>
        <div style="font-family:'Syne',sans-serif;font-size:36px;font-weight:800;color:#f1f5f9;letter-spacing:-.02em;line-height:1;">Market Mind AI</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#334155;margin-top:4px;">v32 · Cyclicality-aware · Analyst-anchored · Year-by-year decay model · 100% free</div>
    </div>
    <hr style="border:none;border-top:1px solid #1e2d40;margin:14px 0 20px;">
    """, unsafe_allow_html=True)

    ci, cb, _ = st.columns([2,1,4])
    with ci: ticker = st.text_input("", placeholder="MU, NVDA, FSELX…", label_visibility="collapsed").upper().strip()
    with cb: st.button("⚡ Analyze", use_container_width=True, type="primary")

    if not ticker:
        st.markdown("""<div style="text-align:center;padding:70px 20px;color:#1e3a5f;">
            <div style="font-size:52px;margin-bottom:14px;">📊</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.1em;">Stocks · Mutual Funds · ETFs · NYSE · NASDAQ · Global</div>
        </div>""", unsafe_allow_html=True)
        return

    with st.spinner(f"Loading {ticker}..."):
        try:
            stk    = yf.Ticker(ticker)
            info   = stk.info
            hist2y = stk.history(period="2y")
            hist1y = stk.history(period="1y")
            hist5y = stk.history(period="5y")
            hist10y= stk.history(period="10y")
            eh     = stk.earnings_history
            recs   = stk.recommendations
            inst   = stk.institutional_holders
            ins    = stk.insider_transactions
            cal    = stk.calendar
        except Exception as e:
            st.error(f"Could not load {ticker}: {e}"); return

    if not info or not any(safe(info,k) for k in ['longName','shortName','currentPrice','regularMarketPrice','navPrice']):
        st.error(f"No data found for '{ticker}'. Please check the ticker symbol."); return

    name     = safe(info,'longName') or safe(info,'shortName') or ticker
    sector   = safe(info,'sector') or safe(info,'category') or 'N/A'
    ind      = safe(info,'industry') or safe(info,'fundFamily') or 'N/A'
    price    = safe(info,'currentPrice') or safe(info,'regularMarketPrice') or safe(info,'navPrice')
    prev     = safe(info,'previousClose')
    mc       = safe(info,'marketCap') or safe(info,'totalAssets')
    vol      = safe(info,'volume')
    avgvol   = safe(info,'averageVolume')
    rg       = safe(info,'revenueGrowth')
    fund_mode_flag = is_fund_check(info)

    if price is None and not hist1y.empty: price = float(hist1y['Close'].iloc[-1])
    if prev is None and not hist1y.empty and len(hist1y)>1: prev = float(hist1y['Close'].iloc[-2])

    chg     = price - prev if price and prev else None
    chg_pct = (chg/prev)*100 if chg and prev else None
    chg_col = "#22c55e" if (chg_pct or 0)>=0 else "#ef4444"
    chg_sym = "▲" if (chg_pct or 0)>=0 else "▼"

    ta = get_ta(hist2y) if not hist2y.empty else {}

    if fund_mode_flag:
        fs, fpos, fneg   = score_fund_performance(hist10y if not hist10y.empty else hist5y)
        vs, vpos, vneg   = score_valuation(info, fund_mode=True)
        bs, bpos, bneg   = score_balance_sheet(info, fund_mode=True)
        ms, mpos, mneg   = score_momentum(ta, info)
        as_, apos, aneg  = score_analyst(info, fund_mode=True)
    else:
        fs, fpos, fneg   = score_fundamentals(info)
        vs, vpos, vneg   = score_valuation(info)
        bs, bpos, bneg   = score_balance_sheet(info)
        ms, mpos, mneg   = score_momentum(ta, info)
        as_, apos, aneg  = score_analyst(info)

    overall   = round(fs*.35 + vs*.20 + bs*.20 + ms*.10 + as_*.15, 1)
    ratings   = calc_ratings(fs, vs, ms, bs, as_)

    # gen_scenarios now returns (scenarios, assumptions, is_cyclical)
    scenario_result = gen_scenarios(price or 100, rg, info, hist2y)
    if len(scenario_result) == 3:
        scenarios, assumptions, is_cyclical = scenario_result
    else:
        scenarios = scenario_result; assumptions = {}; is_cyclical = False

    all_pos = fpos+vpos+bpos+mpos+apos
    all_neg = fneg+vneg+bneg+mneg+aneg

    pstr = f"{price:,.2f}" if price else "—"
    cstr = f"{chg_sym} ${abs(chg):.2f} ({chg_pct:+.2f}%)" if chg and chg_pct else "—"
    mc_label = "Total Assets" if fund_mode_flag else "Market Cap"

    # ── HEADER ──
    qt_str = (safe(info,'quoteType','') or '').upper()
    fund_badge = f'<span class="chip chip-p">{"MUTUAL FUND" if qt_str=="MUTUALFUND" else "ETF"}</span>' if fund_mode_flag else ''
    cyclical_badge = f'<span class="chip chip-o">⚠ CYCLICAL</span>' if is_cyclical and not fund_mode_flag else ''

    st.markdown(f"""
    <div class="mm-header">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
        <div>
          <div class="mm-ticker">◈ {ticker}</div>
          <div class="mm-company">{name}</div>
          <div style="margin-top:6px;">{fund_badge}{cyclical_badge}<span class="chip chip-b">{sector}</span><span class="chip chip-n">{ind}</span></div>
        </div>
        <div style="text-align:right;">
          <div class="mm-price">${pstr}</div>
          <div style="color:{chg_col};font-family:'JetBrains Mono',monospace;font-size:15px;margin-top:4px;">{cstr}</div>
          <div class="mm-meta">{mc_label}: {fmt_big(mc)}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cyclicality warning ──
    if is_cyclical and not fund_mode_flag:
        cyc_label = cyclical_label(info)
        target_mean_display = safe(info, 'targetMeanPrice')
        anchor_note = f" · Year 1 anchored to analyst consensus target (${target_mean_display:.2f})" if target_mean_display else " · Year 1 anchored to analyst-implied growth"
        st.markdown(f"""
        <div class="alert-o">
          ⚠️ <strong>Cyclical Industry Detected — {cyc_label}</strong><br>
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;">
          Scenarios use a year-by-year decay model, NOT simple extrapolation.{anchor_note}<br>
          Years 3-4 apply down-cycle headwinds — supply gluts, margin compression, and earnings normalization are modeled.
          The chart may show a peak-then-dip shape reflecting the boom-bust cycle rather than a straight line up.
          </span>
        </div>""", unsafe_allow_html=True)

    # ── Fund mode banner ──
    if fund_mode_flag:
        r1s  = calc_hist_annual_return(hist1y,  1)
        r3s  = calc_hist_annual_return(hist5y,  3)
        r5s  = calc_hist_annual_return(hist5y,  5)
        r10s = calc_hist_annual_return(hist10y, 10)
        def rp(r): return f"{r*100:+.1f}%/yr" if r is not None else "—"
        st.markdown(f"""
        <div class="alert-p">
          📊 <strong>Fund Mode Active</strong> — Scenarios driven by historical return track record.<br>
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;">
          1yr: <strong>{rp(r1s)}</strong> &nbsp;·&nbsp; 3yr: <strong>{rp(r3s)}</strong> &nbsp;·&nbsp;
          5yr: <strong>{rp(r5s)}</strong> &nbsp;·&nbsp; 10yr: <strong>{rp(r10s)}</strong>
          </span>
        </div>""", unsafe_allow_html=True)

    # ── Quick stats (stocks only) ──
    if not fund_mode_flag:
        s1,s2,s3,s4,s5,s6,s7 = st.columns(7)
        for col,(lbl,val) in zip([s1,s2,s3,s4,s5,s6,s7],[
            ("P/E Trailing", fmt(safe(info,'trailingPE'),suffix="x")),
            ("P/E Forward",  fmt(safe(info,'forwardPE'),suffix="x")),
            ("P/S Ratio",    fmt(safe(info,'priceToSalesTrailing12Months'),suffix="x")),
            ("PEG",          fmt(safe(info,'pegRatio'))),
            ("Beta",         fmt(safe(info,'beta'))),
            ("EPS (TTM)",    fmt(safe(info,'trailingEps'),prefix="$")),
            ("Div Yield",    fmt((safe(info,'dividendYield') or 0)*100,suffix="%")),
        ]): col.metric(lbl, val)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── CONVICTION DASHBOARD ──
    st.markdown('<div class="mm-section-label">📊 conviction dashboard</div>', unsafe_allow_html=True)
    ov_col, r12c, r24c, r36c, r60c = st.columns([1.6,1,1,1,1])
    with ov_col:
        oc = score_color(overall)
        st.markdown(f"""<div class="mm-card" style="text-align:center;padding:28px 16px;">
          <div class="mm-section-label">OVERALL CONVICTION</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:62px;font-weight:700;color:{oc};line-height:1;">{overall}</div>
          <div style="font-size:12px;color:#475569;margin-top:4px;">/10 &nbsp; Grade: <strong style="color:{oc};">{grade(overall)}</strong></div>
        </div>""", unsafe_allow_html=True)
    for col, key, lbl in zip([r12c,r24c,r36c,r60c],['12m','24m','36m','60m'],['12 Months','24 Months','36 Months','5 Years']):
        r = ratings[key]; rc = score_color(r['score'])
        with col:
            st.markdown(f"""<div class="rating-wrap">
              <div class="r-horizon">{lbl}</div>
              <div class="r-score" style="color:{rc};">{r['score']}</div>
              <div style="font-size:11px;color:#475569;">/10</div>
              <div class="r-conf">↗ {r['conf']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── PRICE CHART ──
    st.markdown('<div class="mm-section-label">📈 price history</div>', unsafe_allow_html=True)
    if not hist2y.empty:
        pc1, pc2 = st.columns([3,1])
        with pc1:
            st.plotly_chart(chart_price(hist2y, ticker), use_container_width=True, config={'displayModeBar':False})
        with pc2:
            st.plotly_chart(chart_rsi(hist2y), use_container_width=True, config={'displayModeBar':False})
            if ta:
                rsi_v = ta.get('rsi',50) or 50
                rl    = "Overbought" if rsi_v>70 else "Oversold" if rsi_v<30 else "Neutral"
                rows  = (trow("RSI (14)", f"{rsi_v:.0f} — {rl}", "#ef4444" if rsi_v>70 else "#22c55e" if rsi_v<30 else "#eab308") +
                         trow("50-Day MA", f"{'↑' if ta.get('above50') else '↓'} ${ta.get('ma50',0):,.2f}", "#22c55e" if ta.get('above50') else "#ef4444") +
                         trow("200-Day MA", f"{'↑' if ta.get('above200') else '↓'} ${ta.get('ma200',0):,.2f}", "#22c55e" if ta.get('above200') else "#ef4444") +
                         trow("52w High", f"${ta.get('hi52',0):,.2f} ({ta.get('pct_hi',0):+.1f}%)","#6b7280") +
                         trow("52w Low",  f"${ta.get('lo52',0):,.2f} ({ta.get('pct_lo',0):+.1f}%)","#6b7280") +
                         trow("MACD", "Bullish" if (ta.get('macd') or {}).get('bull') else "Bearish", "#22c55e" if (ta.get('macd') or {}).get('bull') else "#ef4444"))
                st.markdown(f'<div class="mm-card" style="padding:12px 14px;">{rows}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── SCENARIO FORECASTS ──
    st.markdown('<div class="mm-section-label">🎯 scenario forecasts — analyst-anchored · year-by-year decay</div>', unsafe_allow_html=True)

    target_mean_v = safe(info, 'targetMeanPrice')
    if target_mean_v and not fund_mode_flag:
        upside_v = ((target_mean_v - price) / price * 100) if price else 0
        st.markdown(f'<div class="alert-b" style="font-size:11px;">📌 <strong>12-Month Anchor:</strong> Analyst consensus target <strong>${target_mean_v:.2f}</strong> ({upside_v:+.1f}% vs current) · High: ${fmt(safe(info,"targetHighPrice"))} · Low: ${fmt(safe(info,"targetLowPrice"))} · Years 2-5 use decay model from this anchor</div>', unsafe_allow_html=True)

    sg1, sg2 = st.columns([1,1.6])
    with sg1:
        st.plotly_chart(chart_scenarios(scenarios, price or 100), use_container_width=True, config={'displayModeBar':False})
    with sg2:
        tabs = st.tabs(["12 Months","24 Months","36 Months","5 Years"])
        for tab, key in zip(tabs,['12m','24m','36m','60m']):
            with tab:
                sc = scenarios[key]; b1,b2,b3 = st.columns(3)
                with b1: st.markdown(f'<div class="sc-bear"><div class="sc-label" style="color:#f87171;">🐻 Bear</div><div class="sc-price" style="color:#f87171;">${sc["bear"]["p"]:,.2f}</div><div class="sc-pct" style="color:#ef4444;">{sc["bear"]["pct"]:+.1f}%</div></div>', unsafe_allow_html=True)
                with b2: st.markdown(f'<div class="sc-base"><div class="sc-label" style="color:#93c5fd;">📊 Base</div><div class="sc-price" style="color:#93c5fd;">${sc["base"]["p"]:,.2f}</div><div class="sc-pct" style="color:#60a5fa;">{sc["base"]["pct"]:+.1f}%</div></div>', unsafe_allow_html=True)
                with b3: st.markdown(f'<div class="sc-bull"><div class="sc-label" style="color:#86efac;">🐂 Bull</div><div class="sc-price" style="color:#86efac;">${sc["bull"]["p"]:,.2f}</div><div class="sc-pct" style="color:#22c55e;">{sc["bull"]["pct"]:+.1f}%</div></div>', unsafe_allow_html=True)

    # ── Scenario assumptions expander ──
    if assumptions and not fund_mode_flag:
        with st.expander("🔍 View scenario logic — year-by-year growth assumptions"):
            st.markdown('<div style="font-size:11px;color:#64748b;font-family:JetBrains Mono,monospace;margin-bottom:8px;">Growth rates applied to each future year. Year 1 is anchored to analyst target; Years 2-5 use the decay model. Cyclical stocks show down-cycle adjustment in years 3-4.</div>', unsafe_allow_html=True)
            rows_a = ""
            yr_labels = {2:"Year 2 (24m)", 3:"Year 3 (36m)", 4:"Year 4", 5:"Year 5 (60m)"}
            for yr in [2,3,4,5]:
                lbl = yr_labels.get(yr, f"Year {yr}")
                bg = assumptions.get(f'base_yr{yr}')
                bul = assumptions.get(f'bull_yr{yr}')
                bea = assumptions.get(f'bear_yr{yr}')
                if bg is not None:
                    bg_c = "#22c55e" if bg > 0.05 else "#eab308" if bg > -0.05 else "#ef4444"
                    bu_c = "#22c55e" if (bul or 0) > 0.05 else "#eab308"
                    be_c = "#ef4444" if (bea or 0) < -0.05 else "#eab308"
                    rows_a += f'<div class="trow"><span class="trow-label">{lbl}</span><span style="color:{bu_c};">🐂 {(bul or 0)*100:+.1f}%</span><span style="color:{bg_c};">📊 {bg*100:+.1f}%</span><span style="color:{be_c};">🐻 {(bea or 0)*100:+.1f}%</span></div>'
            if rows_a:
                st.markdown(f'<div class="mm-card" style="padding:12px 16px;">{rows_a}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── SCORECARD ──
    sc_label_name = "Performance Track Record" if fund_mode_flag else "Fundamentals"
    st.markdown('<div class="mm-section-label">🏆 scorecard</div>', unsafe_allow_html=True)
    sc_cols = st.columns(5)
    for col,(nm,sc_v,pos,neg) in zip(sc_cols,[(sc_label_name,fs,fpos,fneg),("Valuation",vs,vpos,vneg),("Balance Sheet",bs,bpos,bneg),("Momentum",ms,mpos,mneg),("Analyst View",as_,apos,aneg)]):
        cc = score_color(sc_v); gr = grade(sc_v)
        with col:
            pts = "".join([f'<div class="alert-g" style="padding:4px 8px;font-size:11px;">✓ {p}</div>' for p in pos[:2]])
            rks = "".join([f'<div class="alert-r" style="padding:4px 8px;font-size:11px;">✗ {n}</div>' for n in neg[:1]])
            st.markdown(f'<div class="mm-card" style="min-height:180px;"><div class="mm-section-label">{nm}</div><div style="display:flex;align-items:baseline;gap:8px;margin-bottom:10px;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:34px;font-weight:700;color:{cc};">{sc_v}</div><div style="color:#334155;font-size:13px;">/10</div><div style="margin-left:auto;font-family:\'JetBrains Mono\',monospace;font-size:18px;font-weight:700;color:{cc};">{gr}</div></div>{pts}{rks}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── VALUATION & GROWTH (stocks only) ──
    if not fund_mode_flag:
        st.markdown('<div class="mm-section-label">💰 valuation & growth metrics</div>', unsafe_allow_html=True)
        v1,v2 = st.columns(2)
        with v1:
            vmet = [("P/E Trailing",safe(info,'trailingPE'),"x",15,25,45),("P/E Forward",safe(info,'forwardPE'),"x",15,25,45),("Price/Sales",safe(info,'priceToSalesTrailing12Months'),"x",3,8,18),("Price/Book",safe(info,'priceToBook'),"x",2,5,12),("EV/EBITDA",safe(info,'enterpriseToEbitda'),"x",10,20,35),("EV/Revenue",safe(info,'enterpriseToRevenue'),"x",3,8,15),("PEG Ratio",safe(info,'pegRatio'),"",1,2,3.5)]
            rows_v = ""
            for lbl,val,sfx,cheap,fair,exp in vmet:
                if val is None: continue
                if val<cheap: clr="#22c55e"; tag="Cheap"
                elif val<fair: clr="#60a5fa"; tag="Fair"
                elif val<exp: clr="#eab308"; tag="Premium"
                else: clr="#ef4444"; tag="Expensive"
                rows_v += trow(lbl, f"{val:.1f}{sfx} — {tag}", clr)
            st.markdown(f'<div class="mm-card" style="padding:12px 16px;">{rows_v}</div>', unsafe_allow_html=True)
        with v2:
            grow_met = [("Revenue Growth YoY",pct_str(safe(info,'revenueGrowth')),safe(info,'revenueGrowth') or 0),("Earnings Growth YoY",pct_str(safe(info,'earningsGrowth')),safe(info,'earningsGrowth') or 0),("Gross Margin",pct_str(safe(info,'grossMargins')),safe(info,'grossMargins') or 0),("Operating Margin",pct_str(safe(info,'operatingMargins')),safe(info,'operatingMargins') or 0),("Net Profit Margin",pct_str(safe(info,'profitMargins')),safe(info,'profitMargins') or 0),("Return on Equity",pct_str(safe(info,'returnOnEquity')),safe(info,'returnOnEquity') or 0),("Return on Assets",pct_str(safe(info,'returnOnAssets')),safe(info,'returnOnAssets') or 0),("Free Cash Flow",fmt_big(safe(info,'freeCashflow')),safe(info,'freeCashflow') or 0),("Total Cash",fmt_big(safe(info,'totalCash')),1),("Total Debt",fmt_big(safe(info,'totalDebt')),-1),("Debt/Equity",fmt(safe(info,'debtToEquity'),suffix="%"),safe(info,'debtToEquity') or 0)]
            rows_g = ""
            for lbl,disp,num in grow_met:
                if disp=="—": continue
                nc = "#22c55e" if num>0 else "#ef4444" if num<0 else "#6b7280"
                rows_g += trow(lbl, disp, nc)
            st.markdown(f'<div class="mm-card" style="padding:12px 16px;">{rows_g}</div>', unsafe_allow_html=True)

    # ── ANALYST CONSENSUS (stocks only) ──
    if not fund_mode_flag:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="mm-section-label">👨‍💼 analyst consensus</div>', unsafe_allow_html=True)
        ac1,ac2 = st.columns([1,1])
        with ac1:
            tgt_mean=safe(info,'targetMeanPrice'); tgt_hi=safe(info,'targetHighPrice'); tgt_lo=safe(info,'targetLowPrice'); tgt_med=safe(info,'targetMedianPrice')
            n_an=safe(info,'numberOfAnalystOpinions'); rec_key=(safe(info,'recommendationKey') or 'N/A').upper().replace('_',' '); rec_mean=safe(info,'recommendationMean')
            upside=((tgt_mean-price)/price*100) if tgt_mean and price else None; up_c="#22c55e" if (upside or 0)>0 else "#ef4444"
            rows_a=(trow("Consensus Rating",rec_key,"#3b82f6")+trow("Rating Score",f"{rec_mean:.2f} / 5.0 (1=Strong Buy)","#22c55e" if (rec_mean or 3)<2.5 else "#eab308" if (rec_mean or 3)<3.5 else "#ef4444")+trow("Analyst Count",str(n_an or "—"),"#9ca3af")+trow("Mean Target",fmt(tgt_mean,prefix="$"),up_c)+trow("Median Target",fmt(tgt_med,prefix="$"),"#9ca3af")+trow("High Target",fmt(tgt_hi,prefix="$"),"#22c55e")+trow("Low Target",fmt(tgt_lo,prefix="$"),"#ef4444")+trow("Implied Upside",f"{upside:+.1f}%" if upside else "—",up_c))
            st.markdown(f'<div class="mm-card" style="padding:12px 16px;">{rows_a}</div>', unsafe_allow_html=True)
        with ac2:
            st.markdown('<div class="mm-section-label" style="margin-bottom:6px;">Recent Rating Changes</div>', unsafe_allow_html=True)
            try:
                if recs is not None and not recs.empty:
                    rows_r=""
                    for _,row in recs.tail(10).iterrows():
                        firm=str(row.get('Firm',row.get('firm','N/A')))[:20]; tog=str(row.get('To Grade',row.get('toGrade','N/A')))
                        bg="#22c55e" if any(x in tog.lower() for x in ['buy','outperform','overweight','positive']) else "#ef4444" if any(x in tog.lower() for x in ['sell','underperform','underweight','negative']) else "#eab308"
                        rows_r+=f'<div class="trow"><span class="trow-label">{firm}</span><span style="color:{bg};font-family:JetBrains Mono,monospace;font-size:11px;">{tog}</span></div>'
                    st.markdown(f'<div class="mm-card" style="padding:12px 16px;">{rows_r}</div>', unsafe_allow_html=True)
                else: st.markdown('<div class="alert-b">No recent rating changes available.</div>', unsafe_allow_html=True)
            except: st.markdown('<div class="alert-b">Rating data unavailable.</div>', unsafe_allow_html=True)
        rec_key_var = rec_key
    else:
        rec_key_var = "N/A"

    # ── EARNINGS (stocks only) ──
    if not fund_mode_flag:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="mm-section-label">📅 earnings track record</div>', unsafe_allow_html=True)
        try:
            if cal is not None:
                ned=cal.get('Earnings Date') or cal.get('earningsDate')
                if ned:
                    if isinstance(ned,list): ned=ned[0]
                    st.markdown(f'<div class="alert-b">📅 Next Earnings: <strong>{ned}</strong></div>', unsafe_allow_html=True)
        except: pass
        try:
            if eh is not None and not eh.empty:
                df8=eh.tail(8); beats=0; total=0; rows_e=""
                for _,row in df8.iterrows():
                    est=row.get('EPS Estimate'); act=row.get('Reported EPS'); sp=row.get('Surprise(%)'); dt=str(row.get('Earnings Date',row.name))[:10]
                    if act is not None and est is not None:
                        beat=float(act)>=float(est); beats+=1 if beat else 0; total+=1
                        bc="#22c55e" if beat else "#ef4444"; bl="BEAT" if beat else "MISS"; spstr=f"{float(sp):+.1f}%" if sp is not None else "—"
                        rows_e+=f'<div class="trow"><span class="trow-label">{dt}</span><span style="color:#94a3b8;font-family:JetBrains Mono,monospace;font-size:11px;">Est ${float(est):.2f}</span><span style="color:#f1f5f9;font-family:JetBrains Mono,monospace;font-size:11px;">Act ${float(act):.2f}</span><span style="color:{bc};font-weight:700;font-family:JetBrains Mono,monospace;font-size:11px;">{bl} {spstr}</span></div>'
                if rows_e:
                    br=int(beats/total*100) if total else 0; brc="#22c55e" if br>=70 else "#eab308" if br>=50 else "#ef4444"
                    ec1,ec2=st.columns([1,1])
                    with ec1: st.markdown(f'<div class="mm-card" style="padding:12px 16px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;"><span style="font-size:12px;color:#64748b;">Last {total} Quarters</span><span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;font-weight:700;color:{brc};">Beat Rate: {br}%</span></div>{rows_e}</div>', unsafe_allow_html=True)
                    with ec2:
                        efig=chart_earnings(df8)
                        if efig: st.plotly_chart(efig,use_container_width=True,config={'displayModeBar':False})
            else: st.markdown('<div class="alert-b">Earnings history not available for this ticker.</div>', unsafe_allow_html=True)
        except: st.markdown('<div class="alert-b">Could not load earnings data.</div>', unsafe_allow_html=True)

    # ── HISTORICAL PERFORMANCE ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="mm-section-label">📊 historical total return</div>', unsafe_allow_html=True)
    h1c,h2c,h3c,h4c,h5c,h6c = st.columns(6)
    for col,(yrs,lbl,ann) in zip([h1c,h2c,h3c,h4c,h5c,h6c],[(1,"1-Year",False),(3,"3-Year",True),(5,"5-Year",True),(10,"10-Year",True),(15,"15-Year",True),(20,"20-Year",True)]):
        val = hist_return_annualized(stk,yrs) if ann else hist_return(stk,yrs)
        col.metric(lbl, val)

    # ── RISK DASHBOARD ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="mm-section-label">⚠️ risk dashboard</div>', unsafe_allow_html=True)
    rd1,rd2,rd3 = st.columns(3)
    with rd1:
        st.markdown('<div class="mm-section-label" style="margin-bottom:6px;">Risk Metrics</div>', unsafe_allow_html=True)
        beta_v=safe(info,'beta'); short_f=safe(info,'shortPercentOfFloat'); short_r=safe(info,'shortRatio'); dte_v=safe(info,'debtToEquity')
        rows_r=(trow("Beta",fmt(beta_v),"#ef4444" if (beta_v or 1)>1.5 else "#eab308" if (beta_v or 1)>1 else "#22c55e")+trow("Short % Float",fmt((short_f or 0)*100,suffix="%"),"#ef4444" if (short_f or 0)>.15 else "#eab308" if (short_f or 0)>.05 else "#22c55e")+trow("Short Ratio (days)",fmt(short_r),"#ef4444" if (short_r or 0)>5 else "#eab308" if (short_r or 0)>2 else "#22c55e")+trow("Debt/Equity",fmt(dte_v,suffix="%"),"#ef4444" if (dte_v or 0)>200 else "#eab308" if (dte_v or 0)>80 else "#22c55e")+trow("Current Ratio",fmt(safe(info,'currentRatio')),"#22c55e" if (safe(info,'currentRatio') or 0)>1.5 else "#ef4444")+trow("Volume vs Avg",f"{(vol or 0)/(avgvol or 1):.1f}x","#3b82f6"))
        st.markdown(f'<div class="mm-card" style="padding:12px 14px;">{rows_r}</div>', unsafe_allow_html=True)
    with rd2:
        st.markdown('<div class="mm-section-label" style="margin-bottom:6px;">Institutional Holders</div>', unsafe_allow_html=True)
        try:
            if inst is not None and not inst.empty:
                rows_i=""
                for _,row in inst.head(7).iterrows():
                    h_=str(row.get('Holder','N/A'))[:22]; p_=row.get('% Out',row.get('pctHeld',None)); ps_=f"{float(p_)*100:.2f}%" if p_ is not None else "N/A"
                    rows_i+=trow(h_,ps_,"#60a5fa")
                st.markdown(f'<div class="mm-card" style="padding:12px 14px;">{rows_i}</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="alert-b">Institutional data unavailable.</div>', unsafe_allow_html=True)
        except: st.markdown('<div class="alert-b">Institutional data unavailable.</div>', unsafe_allow_html=True)
    with rd3:
        st.markdown('<div class="mm-section-label" style="margin-bottom:6px;">Insider Transactions</div>', unsafe_allow_html=True)
        try:
            if ins is not None and not ins.empty:
                rows_in=""
                for _,row in ins.head(7).iterrows():
                    nm_=str(row.get('Insider',row.get('Name','N/A')))[:18]; tx_=str(row.get('Transaction',row.get('Start Date','N/A')))
                    buy_='buy' in tx_.lower() or 'purchase' in tx_.lower(); sell_='sell' in tx_.lower()
                    tc_="#22c55e" if buy_ else "#ef4444" if sell_ else "#6b7280"
                    rows_in+=trow(nm_,tx_[:14],tc_)
                st.markdown(f'<div class="mm-card" style="padding:12px 14px;">{rows_in}</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="alert-b">Insider data unavailable.</div>', unsafe_allow_html=True)
        except: st.markdown('<div class="alert-b">Insider data unavailable.</div>', unsafe_allow_html=True)

    # ── CONVICTION BREAKDOWN ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="mm-section-label">🔍 conviction breakdown</div>', unsafe_allow_html=True)
    bb1,bb2 = st.columns(2)
    with bb1:
        pts="".join([f'<div class="alert-g" style="font-size:12px;">✅ {p}</div>' for p in all_pos[:8]])
        st.markdown(f'<div class="mm-card"><div class="mm-section-label">BULL POINTS</div>{pts}</div>', unsafe_allow_html=True)
    with bb2:
        rks="".join([f'<div class="alert-r" style="font-size:12px;">⚠️ {n}</div>' for n in all_neg[:8]])
        if not all_neg: rks='<div class="alert-b" style="font-size:12px;">No major risk flags identified.</div>'
        st.markdown(f'<div class="mm-card"><div class="mm-section-label">RISK POINTS</div>{rks}</div>', unsafe_allow_html=True)

    desc = safe(info,'longBusinessSummary') or safe(info,'longName')
    if desc and len(str(desc)) > 50:
        with st.expander("📖 Company Description"):
            st.markdown(f'<div style="font-size:13px;color:#94a3b8;line-height:1.75;">{desc}</div>', unsafe_allow_html=True)

    # ── AI THESIS ──
    st.markdown("<hr>", unsafe_allow_html=True)
    has_key=False
    try: has_key=bool(st.secrets.get("ANTHROPIC_API_KEY",""))
    except: pass
    if has_key:
        st.markdown('<div class="mm-section-label">🤖 ai analyst thesis — claude</div>', unsafe_allow_html=True)
        if st.button("⚡ Generate AI Analyst Thesis", type="primary"):
            with st.spinner("Generating professional analysis..."):
                r1s=calc_hist_annual_return(hist1y,1); r5s=calc_hist_annual_return(hist5y,5)
                cyc_note = f"|Cyclical:Yes|DownCycleRisk:Years3-4" if is_cyclical else ""
                summ=f"Type:{'Fund' if fund_mode_flag else 'Stock'}|Sector:{sector}|Industry:{ind}|Price:${price:.2f}|{'TotalAssets' if fund_mode_flag else 'MarketCap'}:{fmt_big(mc)}|RevGrowth:{pct_str(rg)}|NetMargin:{pct_str(safe(info,'profitMargins'))}|ForwardPE:{fmt(safe(info,'forwardPE'),suffix='x')}|PEG:{fmt(safe(info,'pegRatio'))}|Beta:{fmt(safe(info,'beta'))}|AnalystTarget:{fmt(safe(info,'targetMeanPrice'),prefix='$')}|RSI:{fmt(ta.get('rsi'))}|Above200MA:{'Yes' if ta.get('above200') else 'No'}|Score:{overall}/10{cyc_note}"
                ai=get_ai(ticker,name,summ,{'f':fs,'v':vs,'m':ms,'b':bs,'a':as_})
                if ai:
                    for block in ai.split('\n\n'):
                        if 'BULL' in block.upper(): st.markdown(f'<div class="alert-g" style="font-size:13px;line-height:1.7;">{block}</div>', unsafe_allow_html=True)
                        elif 'BEAR' in block.upper(): st.markdown(f'<div class="alert-r" style="font-size:13px;line-height:1.7;">{block}</div>', unsafe_allow_html=True)
                        elif block.strip(): st.markdown(f'<div class="alert-b" style="font-size:13px;line-height:1.7;">{block}</div>', unsafe_allow_html=True)
                else: st.warning("AI analysis failed — check ANTHROPIC_API_KEY in Streamlit Secrets.")
    else:
        st.markdown('<div class="alert-b" style="font-size:12px;">🤖 <strong>Optional AI Thesis:</strong> Add <code>ANTHROPIC_API_KEY</code> to Streamlit Secrets to unlock AI-generated analysis. Core analysis is always 100% free.</div>', unsafe_allow_html=True)

    from datetime import datetime
    st.markdown(f'<div class="footer">Market Mind AI v32 · Cyclicality-aware · Analyst-anchored scenarios · Data: Yahoo Finance · {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}<br>⚠️ For informational purposes only · Not financial advice · Always conduct your own research</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
