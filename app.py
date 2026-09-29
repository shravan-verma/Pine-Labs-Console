"""
Pine Labs Growth Console — Unified Merchant Growth Console (prototype)
Case Study 1: Building a Unified Merchant Growth Console (Cross-Pine Labs Platform)

One console, three sections:
  1. Customer insights   – one unified profile per customer across POS, UPI, online and prepaid
  2. Growth actions      – offers, EMI promos, gift card pushes, WhatsApp/SMS nudges, with how each is derived
  3. Payment trends      – aggregate payment behaviour across every Pine Labs touchpoint

WhatsApp is an add-on (sidebar): it pushes only high-priority, action-ready alerts to the owner.
All data below is synthetic and generated deterministically for demonstration.

Run:  pip install -r requirements.txt  &&  streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Page setup and design tokens
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Pine Labs Growth Console", page_icon="🌲", layout="wide")

TODAY = pd.Timestamp("2026-09-30")
START = pd.Timestamp("2024-01-01")

PINE = "#0E4D3A"      # primary
MOSS = "#3E8A68"      # secondary data
SAGE = "#9CC7B0"      # tertiary data
MINT = "#E8F1EC"      # surfaces
MARIGOLD = "#D99A14"  # opportunities / attention
ROSE = "#B8433A"      # risk
INK = "#1D2622"
SLATE = "#66726C"

CH_COLORS = {"POS card": PINE, "UPI": MOSS, "Online": MARIGOLD, "Prepaid": "#8FA39A"}
CHANNELS = ["POS card", "UPI", "Online", "Prepaid"]

WA_COST = 0.86    # ₹ per WhatsApp marketing message (Meta India rate card, 2026)
WA_UTIL = 0.115   # ₹ per WhatsApp utility message (e-bills, reminders)
SMS_COST = 0.20   # ₹ per promotional SMS (assumption)
BASELINE_CONV = 0.015  # purchase rate of customers who receive nothing (from past control groups)

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea, select {{
    font-family: 'Instrument Sans', 'Segoe UI', system-ui, sans-serif;
}}
[data-testid="stMetricValue"] {{ font-variant-numeric: tabular-nums; font-weight: 600; color: {INK}; font-size: 1.65rem; }}
[data-testid="stMetricLabel"] p {{ color: {SLATE}; font-size: 0.85rem; }}
.block-container {{ padding-top: 2.6rem; max-width: 1400px; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 0.25rem; border-bottom: 2px solid {MINT}; }}
.stTabs [data-baseweb="tab"] {{ font-size: 1.02rem; font-weight: 600; padding: 0.6rem 1.1rem; }}
.stTabs [aria-selected="true"] {{ color: {PINE}; }}
.gc-head {{ display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:1rem; margin-bottom:0.4rem; }}
.gc-store {{ font-size:1.9rem; font-weight:700; color:{INK}; line-height:1.1; }}
.gc-sub {{ color:{SLATE}; font-size:0.95rem; }}
.gc-src {{ display:inline-block; padding:0.18rem 0.6rem; margin:0 0.3rem 0.3rem 0; border-radius:999px;
           background:{MINT}; color:{PINE}; font-size:0.82rem; font-weight:600; }}
.gc-src.off {{ background:#F1F1F1; color:{SLATE}; }}
.gc-card {{ background:#FFFFFF; border:1px solid #DCE6E0; border-radius:10px; padding:1rem 1.1rem; }}
.gc-profile {{ background:{PINE}; color:#FFFFFF; border-radius:12px; padding:1.2rem 1.3rem; }}
.gc-profile .nm {{ font-size:1.6rem; font-weight:700; }}
.gc-profile .meta {{ color:#CFE3D8; font-size:0.93rem; margin-top:0.2rem; }}
.gc-tag {{ display:inline-block; padding:0.12rem 0.55rem; border-radius:6px; font-size:0.8rem; font-weight:600;
           margin:0.35rem 0.3rem 0 0; }}
.gc-tag.seg {{ background:#FFFFFF; color:{PINE}; }}
.gc-tag.opp {{ background:{MARIGOLD}; color:#FFFFFF; }}
.gc-tag.ok {{ background:#1E6A50; color:#FFFFFF; }}
.gc-id {{ border-left:3px solid {MOSS}; padding:0.35rem 0.7rem; margin-bottom:0.45rem; background:#FAFCFB; }}
.gc-id b {{ color:{INK}; }} .gc-id span {{ color:{SLATE}; font-size:0.86rem; }}
.gc-trait {{ padding:0.55rem 0.75rem; border-radius:8px; background:{MINT}; margin-bottom:0.45rem; font-size:0.94rem; }}
.gc-nba {{ border:1px solid #E9D6A8; background:#FFF8E8; border-radius:10px; padding:0.8rem 1rem; margin-bottom:0.6rem; }}
.gc-nba .t {{ font-weight:700; color:{INK}; }} .gc-nba .d {{ color:{SLATE}; font-size:0.9rem; margin-top:0.2rem; }}
.gc-step {{ background:#FFFFFF; border:1px solid #DCE6E0; border-radius:10px; padding:0.75rem 0.85rem; height:100%; }}
.gc-step .n {{ color:{MARIGOLD}; font-weight:700; font-size:0.85rem; }}
.gc-step .h {{ font-weight:700; color:{INK}; margin:0.15rem 0 0.25rem 0; }}
.gc-step .b {{ color:{SLATE}; font-size:0.88rem; }}
.gc-insight {{ border-left:4px solid {MARIGOLD}; background:#FFFFFF; padding:0.6rem 0.9rem; margin-bottom:0.5rem;
               border-radius:0 8px 8px 0; font-size:0.95rem; }}
.wa-wrap {{ background:#E9E2D8; border-radius:12px; padding:0.7rem; }}
.wa-head {{ background:#1F5C4A; color:#FFFFFF; border-radius:8px 8px 0 0; padding:0.5rem 0.7rem; font-weight:600; font-size:0.9rem; }}
.wa-msg {{ background:#FFFFFF; border-radius:8px; padding:0.6rem 0.7rem; margin-top:0.5rem; font-size:0.86rem; line-height:1.4; color:{INK}; }}
.wa-btn {{ background:#FFFFFF; border-radius:8px; padding:0.35rem; margin-top:0.3rem; text-align:center;
           color:#1F7A5C; font-weight:600; font-size:0.84rem; }}
.wa-time {{ color:{SLATE}; font-size:0.72rem; text-align:right; margin-top:0.25rem; }}
.small {{ color:{SLATE}; font-size:0.85rem; }}
.kpi {{ padding:0.2rem 0 0.6rem 0; }}
.kpi .l {{ color:{SLATE}; font-size:0.85rem; }}
.kpi .v {{ font-size:1.55rem; font-weight:600; color:{INK}; font-variant-numeric:tabular-nums; line-height:1.25; }}
.kpi .n {{ font-size:0.82rem; color:{SLATE}; }}
.kpi .s {{ display:inline-block; font-size:0.75rem; font-weight:600; padding:0.05rem 0.45rem; border-radius:5px; margin-left:0.3rem; }}
.kpi .s.good {{ background:#DDEFE5; color:{PINE}; }} .kpi .s.warn {{ background:#FBEBC8; color:#8A5B00; }} .kpi .s.bad {{ background:#F6DAD6; color:{ROSE}; }}
table.mini {{ width:100%; border-collapse:collapse; font-size:0.86rem; }}
table.mini th {{ text-align:left; color:{SLATE}; font-weight:600; border-bottom:1px solid #D5DED9; padding:0.35rem 0.4rem; }}
table.mini td {{ border-bottom:1px solid #EEF2EF; padding:0.4rem 0.4rem; vertical-align:top; }}
.later {{ display:inline-block; font-size:0.75rem; font-weight:600; padding:0.05rem 0.45rem; border-radius:5px; background:#ECEFF6; color:#44507A; margin-left:0.4rem; vertical-align:middle; }}
.pos {{ background:#2B2B2B; border-radius:14px; padding:0.7rem; max-width:300px; }}
.pos .scr {{ background:#FFFFFF; border-radius:6px; padding:0.6rem 0.7rem; font-size:0.85rem; color:{INK}; }}
.pos .bar {{ background:{PINE}; color:#FFFFFF; border-radius:6px 6px 0 0; padding:0.35rem 0.7rem; font-size:0.8rem; font-weight:600; }}
.pos .btn {{ display:inline-block; margin-top:0.45rem; margin-right:0.3rem; padding:0.25rem 0.6rem; border-radius:5px; font-size:0.78rem; font-weight:600; }}
</style>
""",
    unsafe_allow_html=True,
)


def inr(x, dec=0):
    """Format rupees in Indian style: ₹1.2L, ₹3.4 Cr, ₹12,499."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    x = float(x)
    if abs(x) >= 1e7:
        return f"₹{x/1e7:.2f} Cr"
    if abs(x) >= 1e5:
        return f"₹{x/1e5:.1f}L"
    s = f"{abs(x):,.{dec}f}"
    # convert 1,234,567 -> 12,34,567
    if dec == 0 and abs(x) >= 1000:
        n = str(int(round(abs(x))))
        last3, rest = n[-3:], n[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        s = ",".join(parts + [last3])
    return ("-" if x < 0 else "") + "₹" + s


def html_table(df):
    head = "".join(f"<th>{c_}</th>" for c_ in df.columns)
    body = "".join("<tr>" + "".join(f"<td>{v_}</td>" for v_ in row_) + "</tr>" for row_ in df.astype(str).values)
    return f"<table class='mini'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def kpi(label, value, note="", status=None, status_text=""):
    s_ = f"<span class='s {status}'>{status_text}</span>" if status else ""
    return f"<div class='kpi'><div class='l'>{label}</div><div class='v'>{value}{s_}</div><div class='n'>{note}</div></div>"


def style_fig(fig, height=320, legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=46, b=10),
        font=dict(family="Instrument Sans, Segoe UI, sans-serif", color=INK, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=15),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0, title=None, font=dict(size=12)),
        hoverlabel=dict(font_family="Instrument Sans, sans-serif"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#C9D3CE")
    fig.update_yaxes(gridcolor="#EDF1EE", zeroline=False)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic data (deterministic) — stands in for Pine Labs POS, UPI, Plural online,
# Qwikcilver prepaid and EMI records for one merchant
# ─────────────────────────────────────────────────────────────────────────────
CAT_PRICE = {
    "Smartphones": (8000, 95000),
    "Laptops": (30000, 115000),
    "TVs": (15000, 120000),
    "Home appliances": (4000, 60000),
    "Audio & wearables": (999, 15000),
    "Accessories": (299, 4000),
    "Gift cards": (1000, 10000),
}
ARCHETYPES = {
    "Loyal regular": dict(w=0.13, n=(5, 12), gap=65, ch=[0.33, 0.45, 0.12, 0.10],
                          cat=[0.14, 0.05, 0.04, 0.10, 0.25, 0.37, 0.05]),
    "Upgrade seeker": dict(w=0.14, n=(2, 5), gap=170, ch=[0.55, 0.28, 0.13, 0.04],
                           cat=[0.42, 0.20, 0.10, 0.06, 0.10, 0.12, 0.00]),
    "Occasional": dict(w=0.29, n=(2, 4), gap=190, ch=[0.30, 0.55, 0.10, 0.05],
                       cat=[0.14, 0.05, 0.08, 0.16, 0.20, 0.35, 0.02]),
    "Online-first": dict(w=0.10, n=(2, 6), gap=95, ch=[0.08, 0.14, 0.74, 0.04],
                         cat=[0.20, 0.12, 0.05, 0.10, 0.25, 0.28, 0.00]),
    "One-time": dict(w=0.28, n=(1, 1), gap=0, ch=[0.32, 0.58, 0.08, 0.02],
                     cat=[0.18, 0.05, 0.07, 0.14, 0.18, 0.38, 0.00]),
    "Gift buyer": dict(w=0.06, n=(2, 5), gap=140, ch=[0.40, 0.30, 0.10, 0.20],
                       cat=[0.08, 0.02, 0.03, 0.10, 0.17, 0.20, 0.40]),
}
FIRST_F = ["Ananya", "Priya", "Sneha", "Kavya", "Neha", "Pooja", "Simran", "Aditi", "Ishita", "Meera", "Tanvi",
           "Nisha", "Divya", "Shreya", "Komal", "Jyoti", "Sakshi", "Muskan", "Payal", "Ritu"]
FIRST_M = ["Rahul", "Amit", "Rohit", "Vikram", "Arjun", "Karan", "Sahil", "Deepak", "Manish", "Nikhil", "Gaurav",
           "Ankit", "Varun", "Harsh", "Mohit", "Sandeep", "Yash", "Kunal", "Naveen", "Pardeep"]
LAST = ["Sharma", "Malik", "Dahiya", "Gupta", "Singh", "Verma", "Jain", "Aggarwal", "Kumar", "Yadav", "Chauhan",
        "Bansal", "Arora", "Kapoor", "Saini", "Hooda", "Rathi", "Mittal", "Khatri", "Sehrawat"]
LOCALITIES = [("Model Town", 1.8), ("Sector 14", 4.2), ("Sector 15", 3.6), ("Sector 23", 5.1), ("Kamaspur", 6.4),
              ("Old Sonipat", 2.4), ("Murthal", 9.8), ("Rai", 13.5), ("Kundli", 19.0), ("Ganaur", 22.0),
              ("Gohana Road", 7.2), ("Panipat", 41.0), ("Narela, Delhi", 28.0)]
OCCUPATIONS = ["Salaried (private)", "Government employee", "Business owner", "Student", "Homemaker",
               "Retired", "Self-employed professional"]
BANKS = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak", "IndusInd"]
UPI_APPS = ["PhonePe", "Google Pay", "Paytm", "BHIM / others", "CRED"]


def _round99(x):
    return float(max(99, int(x / 100) * 100 - 1))


@st.cache_data(show_spinner=False)
def build_data(seed: int = 11):
    rng = np.random.default_rng(seed)
    arch_names = list(ARCHETYPES)
    arch_w = np.array([ARCHETYPES[a]["w"] for a in arch_names])
    n_cust = 1450
    cats = list(CAT_PRICE)
    hours = np.arange(10, 22)
    hour_w = np.array([2, 3, 5, 6, 5, 4, 4, 5, 7, 9, 8, 5], float)
    hour_w /= hour_w.sum()
    total_days = (TODAY - START).days

    cust_rows, tx_rows = [], []
    for i in range(2, n_cust + 2):
        cid = f"C{i:04d}"
        arch = rng.choice(arch_names, p=arch_w)
        gender = rng.choice(["Female", "Male"], p=[0.42, 0.58])
        first = rng.choice(FIRST_F if gender == "Female" else FIRST_M)
        name = f"{first} {rng.choice(LAST)}"
        loc, dist = LOCALITIES[rng.choice(len(LOCALITIES), p=None)]
        if arch == "Online-first":
            loc, dist = LOCALITIES[rng.choice([6, 7, 8, 9, 11, 12])]
        age = int(np.clip(rng.normal(33, 10), 18, 72))
        occ = rng.choice(OCCUPATIONS, p=[0.34, 0.12, 0.14, 0.12, 0.12, 0.06, 0.10])
        phone_linked = rng.random() < (0.72 if arch not in ("One-time",) else 0.38)
        wa = phone_linked and rng.random() < 0.74
        sms = phone_linked and rng.random() < 0.86
        cust_rows.append(dict(customer_id=cid, name=name, gender=gender, age=age, locality=loc, distance_km=dist,
                              occupation=occ, language=rng.choice(["Hindi", "English", "Hindi + English"], p=[0.45, 0.2, 0.35]),
                              phone=f"+91 9{rng.integers(1, 9)}{rng.integers(0, 9)}XX XX{rng.integers(100, 999)}",
                              phone_linked=phone_linked, whatsapp_opt_in=wa, sms_opt_in=sms,
                              archetype=arch, demographics_source="Declared at loyalty sign-up" if phone_linked else "Not shared"))
        a = ARCHETYPES[arch]
        n = int(rng.integers(a["n"][0], a["n"][1] + 1))
        d = START + pd.Timedelta(days=int(rng.beta(1.5, 1.1) * (total_days - 20)))
        churn_after = n if rng.random() > 0.25 else max(1, int(rng.integers(1, n + 1)))
        card_bank = rng.choice(BANKS)
        card_last4 = int(rng.integers(1000, 9999))
        upi_app = rng.choice(UPI_APPS, p=[0.46, 0.36, 0.1, 0.05, 0.03])
        for k in range(min(n, churn_after)):
            if d > TODAY:
                break
            cat = rng.choice(cats, p=np.array(a["cat"]) / sum(a["cat"]))
            lo, hi = CAT_PRICE[cat]
            amt = _round99(np.exp(rng.uniform(np.log(lo), np.log(hi))))
            ch = rng.choice(CHANNELS, p=a["ch"])
            if ch == "Prepaid" and amt > 12000:
                ch = "POS card"
            if ch == "UPI" and amt > 25000 and rng.random() < 0.75:
                ch = "POS card"
            if cat == "Gift cards" and ch in ("Prepaid", "Online"):
                ch = "POS card"
            method, bank, app, is_emi, tenure, emi_type = "", "", "", False, 0, ""
            if ch == "POS card":
                method = "Credit card" if rng.random() < 0.62 else "Debit card"
                bank = card_bank
                p_emi = 0.74 if method == "Credit card" else 0.4
                if amt >= 10000 and cat != "Gift cards" and rng.random() < p_emi:
                    is_emi = True
                if amt >= 12000 and cat != "Gift cards" and not is_emi and rng.random() < 0.32:
                    method, bank, is_emi = "Cardless EMI", "Bajaj Finserv", True
            elif ch == "UPI":
                method, app = "UPI", upi_app
            elif ch == "Online":
                method = rng.choice(["Credit card", "UPI", "Debit card", "Net banking"], p=[0.38, 0.4, 0.14, 0.08])
                bank = card_bank if "card" in method else ""
                app = upi_app if method == "UPI" else ""
                if amt >= 10000 and method == "Credit card" and rng.random() < 0.65:
                    is_emi = True
            else:
                method = "Gift card"
            if is_emi:
                tenure = int(rng.choice([3, 6, 9, 12, 18], p=[0.15, 0.3, 0.25, 0.22, 0.08]))
                emi_type = "No-cost (brand/bank funded)" if cat in ("Smartphones", "Laptops", "TVs") and rng.random() < 0.7 else "Standard"
            ts = d + pd.Timedelta(hours=int(rng.choice(hours, p=hour_w)), minutes=int(rng.integers(0, 60)))
            tx_rows.append(dict(customer_id=cid, date=ts, channel=ch, method=method, bank=bank, upi_app=app,
                                category=cat, amount=amt, is_emi=is_emi, emi_tenure=tenure, emi_type=emi_type,
                                identifier=(f"{bank} ••{card_last4}" if bank and bank != "Bajaj Finserv" else
                                            f"{name.split()[0].lower()}@{app.split()[0].lower()}" if app else
                                            "Bajaj Finserv loan" if bank == "Bajaj Finserv" else "Gift card"),
                                linked=phone_linked))
            gap = a["gap"] if a["gap"] else 400
            d = d + pd.Timedelta(days=int(max(3, rng.exponential(gap))))

    # Anonymous transactions: walk-in UPI / card payments with no consented phone number
    n_anon = 3300
    anon_days = rng.integers(0, total_days, n_anon)
    for j in range(n_anon):
        cat = rng.choice(["Accessories", "Audio & wearables", "Home appliances", "Smartphones"], p=[0.62, 0.22, 0.09, 0.07])
        lo, hi = CAT_PRICE[cat]
        amt = _round99(np.exp(rng.uniform(np.log(lo), np.log(hi))))
        ch = "UPI" if rng.random() < 0.8 else "POS card"
        method = "UPI" if ch == "UPI" else rng.choice(["Debit card", "Credit card"])
        tx_rows.append(dict(customer_id=None, date=START + pd.Timedelta(days=int(anon_days[j]), hours=int(rng.choice(hours, p=hour_w))),
                            channel=ch, method=method, bank="" if ch == "UPI" else rng.choice(BANKS),
                            upi_app=rng.choice(UPI_APPS, p=[0.46, 0.36, 0.1, 0.05, 0.03]) if ch == "UPI" else "",
                            category=cat, amount=amt, is_emi=False, emi_tenure=0, emi_type="",
                            identifier="Unlinked", linked=False))

    # ── Riya: hand-written history (the demo customer) ─────────────────────
    riya = dict(customer_id="C0001", name="Riya Malhotra", gender="Female", age=29, locality="Sector 14", distance_km=4.2,
                occupation="Salaried (private) · IT, commutes to Gurugram", language="English + Hindi",
                phone="+91 98XX XX4417", phone_linked=True, whatsapp_opt_in=True, sms_opt_in=True,
                archetype="Upgrade seeker", demographics_source="Declared at loyalty sign-up (Mar 2024)")
    cust_rows.insert(0, riya)
    R = [
        ("2024-03-12 18:40", "POS card", "Credit card", "HDFC Bank", "", "Smartphones", 54999, True, 12, "No-cost (brand/bank funded)", "HDFC Bank ••4821", "Samsung Galaxy S23"),
        ("2024-03-12 18:52", "UPI", "UPI", "", "PhonePe", "Accessories", 1499, False, 0, "", "riya.m@ybl", "Case + screen guard"),
        ("2024-06-20 19:15", "UPI", "UPI", "", "PhonePe", "Audio & wearables", 2299, False, 0, "", "riya.m@ybl", "boAt earbuds"),
        ("2024-10-28 20:05", "POS card", "Credit card", "HDFC Bank", "", "Gift cards", 4000, False, 0, "", "HDFC Bank ••4821", "2 Diwali gift cards (₹2,000 each)"),
        ("2024-11-15 22:10", "Online", "Debit card", "HDFC Bank", "", "Home appliances", 8999, False, 0, "", "riya.malhotra@gmail.com", "Philips air fryer"),
        ("2025-02-08 13:30", "UPI", "UPI", "", "PhonePe", "Audio & wearables", 4999, False, 0, "", "riya.m@ybl", "Smartwatch"),
        ("2025-06-14 18:20", "Prepaid", "Gift card", "", "", "Audio & wearables", 3000, False, 0, "", "Gift card ••7731", "JBL speaker (gift card part)"),
        ("2025-06-14 18:21", "UPI", "UPI", "", "PhonePe", "Audio & wearables", 1599, False, 0, "", "riya.m@ybl", "JBL speaker (UPI balance)"),
        ("2025-10-05 19:45", "POS card", "Credit card", "HDFC Bank", "", "Laptops", 62990, True, 9, "No-cost (brand/bank funded)", "HDFC Bank ••4821", "Lenovo IdeaPad laptop"),
        ("2025-10-05 19:58", "UPI", "UPI", "", "PhonePe", "Accessories", 2199, False, 0, "", "riya.m@ybl", "Laptop bag + mouse"),
        ("2026-01-18 21:40", "Online", "UPI", "", "PhonePe", "Accessories", 1799, False, 0, "", "riya.malhotra@gmail.com", "45W fast charger"),
        ("2026-05-22 18:55", "UPI", "UPI", "", "PhonePe", "Accessories", 1999, False, 0, "", "riya.m@ybl", "Power bank"),
    ]
    for r in R:
        tx_rows.append(dict(customer_id="C0001", date=pd.Timestamp(r[0]), channel=r[1], method=r[2], bank=r[3], upi_app=r[4],
                            category=r[5], amount=float(r[6]), is_emi=r[7], emi_tenure=r[8], emi_type=r[9],
                            identifier=r[10], item=r[11], linked=True))

    customers = pd.DataFrame(cust_rows)
    tx = pd.DataFrame(tx_rows)
    tx["item"] = tx.get("item", pd.Series(index=tx.index, dtype=object)).fillna(tx["category"])
    tx = tx[tx.date <= TODAY].sort_values("date").reset_index(drop=True)
    tx["txn_id"] = [f"T{100000 + i}" for i in range(len(tx))]
    tx["emi_end"] = pd.NaT
    m = tx.is_emi
    tx.loc[m, "emi_end"] = [d + pd.DateOffset(months=int(t)) for d, t in zip(tx.loc[m, "date"], tx.loc[m, "emi_tenure"])]
    tx["emi_end"] = pd.to_datetime(tx["emi_end"])
    tx["month"] = tx.date.dt.to_period("M").dt.to_timestamp()

    # ── Prepaid: gift cards / store credit held by customers (Qwikcilver) ───
    gc_rows = []
    holders = customers.sample(260, random_state=seed).customer_id.tolist()
    for h in holders:
        if h == "C0001":
            continue
        val = float(rng.choice([500, 1000, 2000, 3000, 5000]))
        issued = START + pd.Timedelta(days=int(rng.integers(120, total_days - 10)))
        used = val * rng.choice([0, 0.2, 0.5, 0.8, 1.0], p=[0.28, 0.12, 0.2, 0.12, 0.28])
        gc_rows.append(dict(customer_id=h, card=f"••{rng.integers(1000, 9999)}", source=rng.choice(
            ["Received as a gift", "Bought for self", "Store credit (Link & Earn)", "Corporate gift card"], p=[0.45, 0.15, 0.25, 0.15]),
            value=val, balance=round(val - used), issued=issued, expiry=issued + pd.DateOffset(months=12)))
    gc_rows.append(dict(customer_id="C0001", card="••7731", source="Corporate gift card", value=3000.0, balance=0,
                        issued=pd.Timestamp("2025-04-01"), expiry=pd.Timestamp("2026-04-01")))
    gc_rows.append(dict(customer_id="C0001", card="••9054", source="Store credit (Link & Earn + Diwali promo)", value=750.0,
                        balance=750, issued=pd.Timestamp("2025-12-15"), expiry=pd.Timestamp("2026-12-15")))
    giftcards = pd.DataFrame(gc_rows)

    # ── Riya's campaign engagement (messages she received) ──────────────────
    riya_msgs = pd.DataFrame([
        dict(date="2024-10-20", campaign="Diwali gift card bundle", channel="WhatsApp", opened=True, clicked=True, purchased=True),
        dict(date="2025-01-25", campaign="Wearables week (10% off)", channel="WhatsApp", opened=True, clicked=True, purchased=True),
        dict(date="2025-06-01", campaign="Monsoon appliance sale", channel="SMS", opened=False, clicked=False, purchased=False),
        dict(date="2025-09-28", campaign="Laptop no-cost EMI festival", channel="WhatsApp", opened=True, clicked=True, purchased=True),
        dict(date="2026-03-10", campaign="Summer AC offer", channel="WhatsApp", opened=True, clicked=False, purchased=False),
    ])

    # ── Past campaigns run from the console (measured against a control group) ─
    campaigns = pd.DataFrame([
        dict(campaign="Diwali gift card bundle", type="Gift card push", launched="2025-10-10", channel="WhatsApp", sent=640, holdout=70,
             conv_t=0.071, conv_c=0.014, avg_ticket=5200, cost=640 * WA_COST, funded_by="Merchant (5% bonus value)", opt_outs=4),
        dict(campaign="Laptop no-cost EMI festival", type="EMI promo", launched="2025-09-26", channel="WhatsApp", sent=410, holdout=45,
             conv_t=0.054, conv_c=0.011, avg_ticket=58000, cost=410 * WA_COST, funded_by="Brand + HDFC Bank", opt_outs=3),
        dict(campaign="Win back: quiet regulars (Feb)", type="Offer", launched="2026-02-02", channel="WhatsApp + SMS", sent=520, holdout=58,
             conv_t=0.038, conv_c=0.012, avg_ticket=3100, cost=520 * (WA_COST + SMS_COST), funded_by="Merchant (₹300 off)", opt_outs=9),
        dict(campaign="Summer AC & cooler offer", type="Offer", launched="2026-04-02", channel="WhatsApp", sent=380, holdout=42,
             conv_t=0.046, conv_c=0.018, avg_ticket=32000, cost=380 * WA_COST, funded_by="Brand (cashback)", opt_outs=3),
        dict(campaign="Monsoon appliance sale", type="WhatsApp/SMS nudge", launched="2026-06-20", channel="SMS", sent=700, holdout=78,
             conv_t=0.021, conv_c=0.013, avg_ticket=6500, cost=700 * SMS_COST, funded_by="Merchant (5% off)", opt_outs=11),
        dict(campaign="Phone upgrade: EMI ended (Jul)", type="EMI promo", launched="2026-07-18", channel="WhatsApp", sent=160, holdout=18,
             conv_t=0.094, conv_c=0.019, avg_ticket=43000, cost=160 * WA_COST, funded_by="Samsung (exchange bonus)", opt_outs=1),
        dict(campaign="Second-purchase thank-you", type="WhatsApp/SMS nudge", launched="2026-08-25", channel="WhatsApp", sent=210, holdout=23,
             conv_t=0.052, conv_c=0.017, avg_ticket=2300, cost=210 * WA_COST, funded_by="Merchant (₹150 off)", opt_outs=2),
        dict(campaign="Win back: quiet regulars (Sep)", type="Offer", launched="2026-09-08", channel="WhatsApp + SMS", sent=300, holdout=33,
             conv_t=0.041, conv_c=0.013, avg_ticket=3200, cost=300 * (WA_COST + SMS_COST), funded_by="Merchant (₹300 off)", opt_outs=4),
        dict(campaign="Phone upgrade: EMI ended (Apr)", type="EMI promo", launched="2026-04-15", channel="WhatsApp", sent=190, holdout=21,
             conv_t=0.089, conv_c=0.016, avg_ticket=41000, cost=190 * WA_COST, funded_by="Samsung (exchange bonus)", opt_outs=1),
        dict(campaign="Gift card expiry reminder", type="WhatsApp/SMS nudge", launched="2026-06-05", channel="WhatsApp", sent=115, holdout=13,
             conv_t=0.217, conv_c=0.092, avg_ticket=2600, cost=115 * WA_UTIL, funded_by="None (reminder)", opt_outs=0),
        dict(campaign="Accessory cross-sell after phone", type="Offer", launched="2026-08-12", channel="WhatsApp", sent=260, holdout=29,
             conv_t=0.112, conv_c=0.041, avg_ticket=1650, cost=260 * WA_COST, funded_by="Merchant (15% off)", opt_outs=2),
    ])
    campaigns["launched"] = pd.to_datetime(campaigns["launched"])
    campaigns["buyers"] = (campaigns.sent * campaigns.conv_t).round().astype(int)
    campaigns["lift_x"] = campaigns.conv_t / campaigns.conv_c
    campaigns["incremental_rev"] = campaigns.sent * (campaigns.conv_t - campaigns.conv_c) * campaigns.avg_ticket
    campaigns["revenue"] = campaigns.buyers * campaigns.avg_ticket
    campaigns["roi_x"] = campaigns.incremental_rev / campaigns.cost
    campaigns["opt_out_rate"] = campaigns.opt_outs / campaigns.sent
    return customers, tx, giftcards, riya_msgs, campaigns


@st.cache_data(show_spinner=False)
def customer_metrics(customers, tx, giftcards):
    t = tx[tx.customer_id.notna()].copy()
    g = t.groupby("customer_id")
    m = pd.DataFrame({
        "first_date": g.date.min(), "last_date": g.date.max(), "n_txn": g.size(),
        "total_spend": g.amount.sum(), "avg_ticket": g.amount.mean(), "emi_count": g.is_emi.sum(),
        "n_channels": g.channel.nunique(),
    })
    v = t.assign(day=t.date.dt.normalize()).drop_duplicates(["customer_id", "day"]).sort_values(["customer_id", "day"])
    v["gap"] = v.groupby("customer_id").day.diff().dt.days
    m["n_visits"] = v.groupby("customer_id").size()
    m["median_gap"] = v.groupby("customer_id").gap.median()
    m["days_since"] = (TODAY - m.last_date).dt.days
    m["primary_channel"] = g.channel.agg(lambda s: s.value_counts().idxmax())
    chs = g.channel.agg(lambda s: set(s))
    m["shops_store"] = chs.apply(lambda s: bool(s & {"POS card", "UPI"}))
    m["shops_online"] = chs.apply(lambda s: "Online" in s)
    m["last_emi_end"] = t[t.is_emi].groupby("customer_id").emi_end.max()
    m["active_emis"] = t[t.is_emi & (t.emi_end > TODAY)].groupby("customer_id").size()
    m["last_phone"] = t[t.category == "Smartphones"].groupby("customer_id").date.max()
    m["last_big"] = t[t.category.isin(["Smartphones", "Laptops"])].groupby("customer_id").date.max()
    m["last_acc"] = t[t.category == "Accessories"].groupby("customer_id").date.max()
    m["full_pay_high"] = t[(t.amount >= 25000) & (~t.is_emi)].groupby("customer_id").size()
    m["gift_buyer"] = t[(t.category == "Gift cards") & (t.date.dt.month.isin([10, 11]))].groupby("customer_id").size()
    m["months_active"] = ((TODAY - m.first_date).dt.days / 30.4).clip(lower=1)
    m = m.fillna({"active_emis": 0, "full_pay_high": 0, "gift_buyer": 0})

    gb = giftcards[giftcards.balance > 0].groupby("customer_id")
    m["gift_balance"] = gb.balance.sum()
    m["gift_expiry"] = gb.expiry.min()
    m["gift_balance"] = m["gift_balance"].fillna(0)

    m = m.join(customers.set_index("customer_id"), how="left")

    vip_cut = m.total_spend.quantile(0.90)
    def seg(r):
        if r.days_since > 540:
            return "Lost"
        if r.n_visits >= 2 and r.days_since > max(1.5 * (r.median_gap if pd.notna(r.median_gap) else 180), 180):
            return "At risk"
        if r.n_visits == 1 and r.days_since <= 90:
            return "New"
        if r.total_spend >= vip_cut:
            return "VIP"
        if r.n_visits >= 3:
            return "Regular"
        return "Occasional" if r.n_visits == 2 else "One-time"
    m["segment"] = m.apply(seg, axis=1)

    # Opportunity flags (signals the console watches for)
    m["f_emi_ended"] = m.last_emi_end.between(TODAY - pd.Timedelta(days=90), TODAY) & (m.last_date < m.last_emi_end)
    m["f_upgrade_due"] = m.last_phone.notna() & ((TODAY - m.last_phone).dt.days >= 730)
    m["f_lapsing"] = m.segment.eq("At risk")
    m["f_lost"] = m.segment.eq("Lost")
    m["f_gift_expiring"] = (m.gift_balance > 0) & (m.gift_expiry <= TODAY + pd.Timedelta(days=90)) & (m.gift_expiry > TODAY)
    m["f_cross_sell"] = m.last_big.notna() & ((TODAY - m.last_big).dt.days <= 45) & (m.last_acc.isna() | (m.last_acc < m.last_big))
    m["f_online_only_near"] = m.shops_online & ~m.shops_store & (m.distance_km <= 12)
    m["f_full_pay_high"] = (m.full_pay_high > 0) & (m.emi_count == 0)
    m["f_second_purchase"] = (m.n_visits == 1) & m.days_since.between(20, 120)
    m["f_festive_gifter"] = m.gift_buyer > 0

    # Simple, explainable scores
    months_since_phone = ((TODAY - m.last_phone).dt.days / 30.4)
    m["upgrade_score"] = (0.08 + 0.3 * (months_since_phone.fillna(0) / 30).clip(0, 1)
                          + 0.15 * m.f_emi_ended + 0.1 * (m.emi_count > 0) + 0.06 * m.segment.isin(["VIP", "Regular"])).clip(0, 0.9)
    ratio = m.days_since / m.median_gap.fillna(180).clip(lower=30)
    m["churn_risk"] = (ratio / 3).clip(0.03, 0.97)
    annual = m.total_spend / (m.months_active / 12).clip(lower=1)
    m["pred_12m_value"] = annual * (1 - m.churn_risk)
    return m


customers, tx, giftcards, riya_msgs, campaigns = build_data()
cm = customer_metrics(customers, tx, giftcards)

# ─────────────────────────────────────────────────────────────────────────────
# Growth action catalogue: each action = signal (data) → rule → audience → offer → channel
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = [
    dict(key="emi_ended", short="EMI just ended: send upgrade offer", merchant_cost=0, partner_cost=5000, flag="f_emi_ended", title="Upgrade offer for customers whose EMI just ended", type="EMI promo",
         signal="EMI end dates from Pine Labs affordability (POS + online EMI)",
         rule="Latest EMI ended in the last 90 days AND no purchase since it ended",
         why="Their monthly budget has just freed up and they have a clean repayment record, so they are pre-qualified for another no-cost EMI.",
         offer="Exchange bonus up to ₹5,000 + 0% EMI for 12 months on the latest phones and laptops",
         funded_by="Brand (exchange bonus) + issuing bank (EMI interest)", channel="WhatsApp", conv=0.085, ticket=45000, urgency=1.3),
    dict(key="upgrade_due", short="Phone 2+ years old: upgrade reminder", merchant_cost=0, partner_cost=1500, flag="f_upgrade_due", title="Phone upgrade reminder: 2+ years since last phone", type="EMI promo",
         signal="Last smartphone purchase date across POS, UPI and online",
         rule="Last phone bought 24+ months ago AND no phone bought since",
         why="Most buyers replace phones every 2–3 years. Reaching them first stops the upgrade going to another store or e-commerce.",
         offer="Free exchange valuation + no-cost EMI on new phones",
         funded_by="Brand + bank", channel="WhatsApp", conv=0.045, ticket=32000, urgency=1.1),
    dict(key="lapsing", short="Regulars gone quiet: win-back offer", merchant_cost=300, partner_cost=0, flag="f_lapsing", title="Win back regulars who have gone quiet", type="Offer",
         signal="Each customer's own visit rhythm (median gap between visits)",
         rule="2+ visits AND days since last visit > 1.5× their usual gap (min. 180 days) AND < 18 months",
         why="These customers already trust the store. The sooner they are nudged after missing their usual visit, the likelier they return.",
         offer="₹300 off on ₹2,000+ this month, valid in store or online",
         funded_by="Merchant", channel="WhatsApp + SMS", conv=0.038, ticket=3100, urgency=1.0),
    dict(key="gift_expiring", short="Gift card balance expiring: remind", merchant_cost=200, partner_cost=0, flag="f_gift_expiring", title="Unused gift card balance expiring soon", type="Gift card push",
         signal="Gift card and store credit balances from Qwikcilver (prepaid)",
         rule="Balance > ₹0 AND expiry within the next 90 days",
         why="Customers who redeem a gift card usually spend more than the balance. A reminder is cheap and customers see it as a favour.",
         offer="Reminder of balance + expiry date; ₹200 extra if redeemed on a ₹3,000+ purchase",
         funded_by="Merchant (optional top-up)", channel="WhatsApp (utility message)", conv=0.20, ticket=2600, urgency=1.2),
    dict(key="festive", short="Festive gift card push", merchant_cost=250, partner_cost=0, flag="f_festive_gifter", title="Festive gift card push to last year's gift buyers", type="Gift card push",
         signal="Gift card purchases in Oct–Nov in previous years",
         rule="Bought gift cards in a previous festive season (Oct–Nov)",
         why="The festive season (Oct–Nov) is starting. Gift buyers repeat, and every gift card sold brings a new person into the store.",
         offer="Buy ₹5,000 in gift cards, get ₹250 extra value",
         funded_by="Merchant", channel="WhatsApp", conv=0.07, ticket=5200, urgency=1.25),
    dict(key="cross_sell", short="Recent phone/laptop buyers: accessory offer", merchant_cost=250, partner_cost=0, flag="f_cross_sell", title="Accessory bundle after a phone or laptop purchase", type="Offer",
         signal="Recent big-ticket purchase with no accessory bought afterwards",
         rule="Bought a phone or laptop in the last 45 days AND no accessory since",
         why="New device owners need cases, chargers and earbuds. If the store doesn't offer them, the customer buys online.",
         offer="15% off any accessory for 30 days",
         funded_by="Merchant", channel="WhatsApp", conv=0.11, ticket=1650, urgency=0.9),
    dict(key="online_to_store", mvp=False, short="Nearby online shoppers: invite to store", merchant_cost=500, partner_cost=0, flag="f_online_only_near", title="Bring nearby online shoppers into the store", type="WhatsApp/SMS nudge",
         signal="Channel mix (online only) + distance from store",
         rule="Only ever bought online AND lives within 12 km of the store",
         why="Online-only customers near the store are the easiest to convert to in-store visits, where average bills are higher.",
         offer="In-store demo + free installation on appliances; same prices as online",
         funded_by="Merchant", channel="WhatsApp", conv=0.03, ticket=9000, urgency=0.8),
    dict(key="full_pay_high", mvp=False, short="Full-payment buyers: tell them about EMI", merchant_cost=0, partner_cost=1000, flag="f_full_pay_high", title="Tell full-payment buyers about no-cost EMI", type="EMI promo",
         signal="High-value purchases (₹25,000+) paid in full, never on EMI",
         rule="Paid ₹25,000+ in one go at least once AND never used EMI",
         why="Many customers don't know they are eligible for no-cost EMI on debit cards or cardless EMI. Knowing lets them buy a better model.",
         offer="Check your no-cost EMI eligibility in store: debit card and cardless options",
         funded_by="Bank / NBFC", channel="SMS", conv=0.02, ticket=38000, urgency=0.85),
    dict(key="second_purchase", short="New customers: second-purchase nudge", merchant_cost=150, partner_cost=0, flag="f_second_purchase", title="Second-purchase nudge for new customers", type="WhatsApp/SMS nudge",
         signal="First purchase 20–120 days ago, no second visit yet",
         rule="Exactly 1 visit AND it was 20–120 days ago",
         why="The second purchase is where a one-time buyer becomes a regular. A small thank-you offer works best in the first few months.",
         offer="Thank-you coupon: ₹150 off the next purchase",
         funded_by="Merchant", channel="WhatsApp", conv=0.05, ticket=2400, urgency=0.95),
]


def action_table(m):
    rows = []
    for a in ACTIONS:
        aud = m[m[a["flag"]]]
        reach_col = "sms_opt_in" if a["channel"] == "SMS" else "whatsapp_opt_in"
        reachable = aud[aud[reach_col].fillna(False)]
        ticket = a["ticket"]
        exp_orders = len(reachable) * a["conv"]
        incr = len(reachable) * max(a["conv"] - BASELINE_CONV, 0) * ticket
        msg_cost = len(reachable) * (WA_UTIL if "utility" in a["channel"] else SMS_COST if a["channel"] == "SMS"
                                     else WA_COST + (SMS_COST if "SMS" in a["channel"] else 0))
        msg_cost += exp_orders * a["merchant_cost"]
        rows.append(dict(key=a["key"], Action=a["title"], Type=a["type"], Audience=len(aud), Reachable=len(reachable),
                         **{"Expected buyers": round(exp_orders, 1), "Expected revenue": exp_orders * ticket,
                            "Incremental revenue": incr, "Cost to merchant": msg_cost, "Funded by": a["funded_by"],
                            "Channel": a["channel"], "Priority": incr * a["urgency"]}))
    df = pd.DataFrame(rows).sort_values("Priority", ascending=False).reset_index(drop=True)
    mx = df.Priority.max() if df.Priority.max() > 0 else 1
    df["Priority score"] = (100 * df.Priority / mx).round().astype(int)
    return df


acts = action_table(cm)
ACT = {a["key"]: a for a in ACTIONS}

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar: store, data sources, WhatsApp alerts add-on, console health
# ─────────────────────────────────────────────────────────────────────────────
linked_share = tx.customer_id.notna().mean()
consent_share = cm.whatsapp_opt_in.fillna(False).mean()

with st.sidebar:
    st.markdown(f"**Anand Electronics**  \n<span class='small'>Sonipat, Haryana · Mobile & electronics · MID 4402-118</span>",
                unsafe_allow_html=True)
    view_mode = st.radio("View", ["Full console", "MVP scope only"], horizontal=True,
                         help="MVP scope hides features planned for later phases, so you can see exactly what launches first.")
    MVP = view_mode == "MVP scope only"
    st.divider()
    st.markdown("**Connected Pine Labs sources**")
    st.markdown(
        "<span class='gc-src'>POS card & EMI</span><span class='gc-src'>UPI QR</span>"
        "<span class='gc-src'>Online · Plural</span><span class='gc-src'>Prepaid · Qwikcilver</span>",
        unsafe_allow_html=True)
    st.caption(f"Last synced {TODAY.strftime('%d %b %Y')}, 09:00. {len(tx):,} transactions since Jan 2024.")
    st.progress(float(linked_share), text=f"{linked_share:.0%} of transactions linked to a customer profile")
    st.progress(float(consent_share), text=f"{consent_share:.0%} of known customers opted in to WhatsApp")
    st.divider()

    st.markdown("**WhatsApp alerts** (add-on)")
    st.caption("Sends only the few things that need you today. Everything else stays in the console.")
    wa_on = st.toggle("Send alerts to +91 98XX XX2210", value=True)
    wa_time = st.selectbox("When", ["Every morning, 9:00", "Weekdays only, 9:00", "Monday summary only"], index=0, disabled=not wa_on)
    wa_types = st.multiselect("Alert me about",
                              ["Top growth actions", "Gift cards expiring this week", "Campaign results ready", "Big customers going quiet", "EMI completions"],
                              default=["Top growth actions", "Campaign results ready", "Gift cards expiring this week"], disabled=not wa_on)
    wa_max = st.slider("Max alerts per message", 1, 5, 3, disabled=not wa_on)

    if wa_on:
        lines = []
        if "Campaign results ready" in wa_types:
            last = campaigns.sort_values("launched").iloc[-1]
            lines.append(f"✅ <b>{last.campaign}</b>: {inr(last.incremental_rev)} extra sales.")
        exp7 = cm[(cm.gift_balance > 0) & (cm.gift_expiry <= TODAY + pd.Timedelta(days=7)) & (cm.gift_expiry > TODAY)]
        if "Gift cards expiring this week" in wa_types and len(exp7):
            lines.append(f"⏰ {len(exp7)} gift cards ({inr(exp7.gift_balance.sum())}) expire this week.")
        if "Top growth actions" in wa_types:
            for _, r in acts.head(wa_max).iterrows():
                lines.append(f"🎯 {ACT[r.key]['short']}: <b>{r.Reachable}</b> customers, ~{inr(r['Incremental revenue'])}.")
        body = "<br>".join(lines[:wa_max]) or "Nothing urgent today."
        st.markdown(
            f"""<div class='wa-wrap'><div class='wa-head'>Pine Labs Growth Console</div>
            <div class='wa-msg'><b>Today, {wa_max} things need you:</b><br>{body}</div>
            <div class='wa-btn'>Open console</div><div class='wa-btn'>Approve top action</div>
            <div class='wa-time'>{wa_time.split(',')[-1].strip()}</div></div>""",
            unsafe_allow_html=True)
        st.caption("Only the top items, never the full data. 'Approve top action' launches the #1 campaign with default settings; everything else is done in the console.")
    st.divider()

    st.markdown("**Console health** (tracked by Pine Labs)")
    c90 = campaigns[campaigns.launched >= TODAY - pd.Timedelta(days=180)]
    h1, h2 = st.columns(2)
    h1.metric("Campaigns (6 mo)", len(c90))
    h2.metric("Extra revenue", inr(c90.incremental_rev.sum()))
    h3, h4 = st.columns(2)
    h3.metric("Avg lift vs control", f"{c90.lift_x.mean():.1f}×")
    h4.metric("Opt-out rate", f"{c90.opt_outs.sum() / c90.sent.sum():.1%}")

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
known = cm
repeat_rate = (known.n_visits >= 2).mean()
repeat_rev_share = tx[tx.customer_id.isin(known[known.n_visits >= 2].index)].amount.sum() / tx.amount.sum()
st.markdown(
    f"""<div class='gc-head'><div><div class='gc-sub'>Pine Labs Growth Console</div>
    <div class='gc-store'>Know your customers. Bring them back.</div></div>
    <div class='gc-sub'>Anand Electronics, Sonipat · Data up to {TODAY.strftime('%d %b %Y')}</div></div>""",
    unsafe_allow_html=True)
k = st.columns(5)
k[0].metric("Known customers", f"{len(known):,}", help="Unique people after joining card, UPI, online and gift card records by consented phone number.")
k[1].metric("Repeat customers", f"{repeat_rate:.0%}", help="Share of known customers who visited on 2+ different days.")
k[2].metric("Revenue from repeat customers", f"{repeat_rev_share:.0%}")
k[3].metric("Open growth actions", f"{(acts.Reachable > 0).sum()}", f"{inr(acts['Incremental revenue'].sum())} potential")
k[4].metric("At-risk or lost customers", f"{cm.segment.isin(['At risk', 'Lost']).sum():,}", delta_color="off")

tab1, tab2, tab3 = st.tabs(["Customer insights", "Growth actions", "Payment trends"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — CUSTOMER INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Customer segments")
    st.caption("Every known customer is placed in one segment automatically, using their visits, spend and gaps between visits across all touchpoints.")
    seg_order = ["VIP", "Regular", "New", "Occasional", "One-time", "At risk", "Lost"]
    seg_desc = {"VIP": "Top 10% by lifetime spend", "Regular": "3+ visits, visiting on rhythm", "New": "First visit in last 90 days",
                "Occasional": "2 visits", "One-time": "1 visit, 90+ days ago", "At risk": "Overdue vs their usual gap",
                "Lost": "No visit in 18+ months"}
    sc = cm.groupby("segment").agg(customers=("n_txn", "size"), spend=("total_spend", "sum"), avg=("total_spend", "mean"),
                                   gap=("median_gap", "median")).reindex(seg_order).fillna(0)
    cols = st.columns(len(seg_order))
    for c, s in zip(cols, seg_order):
        with c:
            st.metric(s, f"{int(sc.loc[s, 'customers']):,}", help=seg_desc[s])
            st.caption(f"{inr(sc.loc[s, 'spend'])} lifetime")

    with st.expander("Browse customers by segment or opportunity", expanded=False):
        f1, f2, f3 = st.columns([1, 1, 1])
        segs = f1.multiselect("Segment", seg_order, default=["VIP", "At risk"])
        opp = f2.selectbox("Has opportunity", ["Any"] + [a["title"] for a in ACTIONS])
        chn = f3.multiselect("Shops via", CHANNELS, default=[])
        view = cm[cm.segment.isin(segs)] if segs else cm
        if opp != "Any":
            view = view[view[[a for a in ACTIONS if a["title"] == opp][0]["flag"]]]
        if chn:
            ids = tx[tx.channel.isin(chn)].customer_id.dropna().unique()
            view = view[view.index.isin(ids)]
        show = view.reset_index()[["customer_id", "name", "segment", "n_visits", "total_spend", "days_since", "primary_channel",
                                   "locality", "whatsapp_opt_in"]].sort_values("total_spend", ascending=False)
        st.dataframe(show, hide_index=True, width="stretch", height=280,
                     column_config={"customer_id": "ID", "name": "Name", "segment": "Segment", "n_visits": "Visits",
                                    "total_spend": st.column_config.NumberColumn("Lifetime spend (₹)", format="localized"),
                                    "days_since": "Days since last visit", "primary_channel": "Usual channel",
                                    "locality": "Area", "whatsapp_opt_in": st.column_config.CheckboxColumn("WhatsApp OK")})
        st.caption(f"{len(show):,} customers match.")

    st.divider()
    st.markdown("#### Individual customer")
    names = cm.reset_index().sort_values("total_spend", ascending=False)
    options = ["C0001"] + [c for c in names.customer_id if c != "C0001"]
    pick = st.selectbox("Search a customer by name", options, index=0,
                        format_func=lambda c: f"{cm.loc[c, 'name']}  ({c}, {cm.loc[c, 'segment']})")
    c = cm.loc[pick]
    ctx = tx[tx.customer_id == pick].sort_values("date")
    cgc = giftcards[giftcards.customer_id == pick]

    flags = [a for a in ACTIONS if bool(c[a["flag"]])]
    left, right = st.columns([1.05, 1.95], gap="large")
    with left:
        opp_tags = "".join(f"<span class='gc-tag opp'>{t_}</span>" for t_ in dict.fromkeys(a['type'] for a in flags))
        consent_tags = ("<span class='gc-tag ok'>WhatsApp ✓</span>" if c.whatsapp_opt_in else "") + \
                       ("<span class='gc-tag ok'>SMS ✓</span>" if c.sms_opt_in else "")
        st.markdown(
            f"""<div class='gc-profile'><div class='nm'>{c['name']}</div>
            <div class='meta'>{c.gender}, {c.age} · {c.locality}, {c.distance_km:.1f} km from store</div>
            <div class='meta'>{c.occupation} · Prefers {c.language}</div>
            <div class='meta'>Customer since {c.first_date.strftime('%b %Y')} · {c.phone}</div>
            <span class='gc-tag seg'>{c.segment}</span>{consent_tags}{opp_tags}</div>""",
            unsafe_allow_html=True)
        st.caption(f"Demographics: {c.demographics_source}. Behaviour is derived from payments.")

        st.markdown("**One profile, joined across touchpoints**")
        ids = ctx.groupby(["channel", "identifier"]).agg(n=("txn_id", "size"), first=("date", "min")).reset_index()
        how = {"POS card": "Card token matched when phone was given at the e-bill",
               "UPI": "UPI ID linked on first payment made alongside the known phone",
               "Online": "Email + phone at Plural checkout",
               "Prepaid": "Gift card registered to the same phone"}
        for _, r in ids.iterrows():
            st.markdown(f"<div class='gc-id'><b>{r.channel}</b> · {r.identifier}<br><span>{how[r.channel]} · {r.n} payment(s)</span></div>",
                        unsafe_allow_html=True)

    with right:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Lifetime spend", inr(c.total_spend))
        m2.metric("Visits", int(c.n_visits), f"every ~{int(c.median_gap)} days" if pd.notna(c.median_gap) else None, delta_color="off")
        m3.metric("Last visit", c.last_date.strftime("%d %b"),
                  f"{int(c.days_since)} days ago",
                  delta_color="inverse" if pd.notna(c.median_gap) and c.days_since > c.median_gap else "normal")
        m4.metric("Avg bill", inr(c.avg_ticket))

        fig = px.scatter(ctx, x="date", y="amount", color="channel", size=np.sqrt(ctx.amount), size_max=26,
                         color_discrete_map=CH_COLORS, hover_data={"item": True, "method": True, "identifier": True, "amount": ":,.0f"},
                         title="Purchase history across every touchpoint")
        for _, r in ctx[ctx.is_emi].iterrows():
            fig.add_shape(type="line", x0=r.date, x1=r.emi_end, y0=r.amount, y1=r.amount, line=dict(color=MARIGOLD, width=3, dash="dot"))
            fig.add_annotation(x=r.emi_end, y=np.log10(r.amount), text=f"EMI {'ended' if r.emi_end <= TODAY else 'ends'} {r.emi_end.strftime('%b %y')}", showarrow=False,
                               yshift=-12, xanchor="right", font=dict(size=11, color=MARIGOLD))
        fig.add_vline(x=TODAY, line=dict(color=SLATE, dash="dash", width=1))
        fig.update_yaxes(title="Amount (₹)", type="log", tickvals=[1000, 3000, 10000, 30000, 100000], ticktext=["₹1k", "₹3k", "₹10k", "₹30k", "₹1L"])
        fig.update_xaxes(title=None)
        st.plotly_chart(style_fig(fig, 330), width="stretch")

        b1, b2 = st.columns(2)
        with b1:
            mix = ctx.groupby("channel").agg(amount=("amount", "sum"), n=("txn_id", "size")).reindex(CHANNELS).dropna().reset_index()
            mix["label"] = mix.apply(lambda x: f"{inr(x.amount)} · {int(x.n)} payments", axis=1)
            f = px.bar(mix, x="amount", y="channel", orientation="h", color="channel", color_discrete_map=CH_COLORS, text="label",
                       title="Where she spends", category_orders={"channel": CHANNELS})
            f.update_traces(textposition="outside", cliponaxis=False)
            f.update_xaxes(visible=False, range=[0, mix.amount.max() * 2.3]); f.update_yaxes(title=None)
            st.plotly_chart(style_fig(f, 260, legend=False), width="stretch")
        with b2:
            cat = ctx.groupby("category").amount.sum().sort_values().reset_index()
            f = px.bar(cat, x="amount", y="category", orientation="h", title="What she buys", color_discrete_sequence=[MOSS])
            f.update_xaxes(title=None); f.update_yaxes(title=None)
            st.plotly_chart(style_fig(f, 260, legend=False), width="stretch")

    st.markdown("#### Behaviour and predictions")
    bl, br = st.columns([1.3, 1], gap="large")
    with bl:
        st.markdown("**What her payments tell us**")
        traits = []
        small = ctx[ctx.amount < 5000]; big = ctx[ctx.amount >= 20000]
        if len(small):
            traits.append(f"Pays for small items (under ₹5,000) mostly by <b>{small.method.value_counts().idxmax()}</b>"
                          + (f" via {small.upi_app[small.upi_app != ''].value_counts().idxmax()}" if (small.upi_app != '').any() else "") + ".")
        if len(big):
            e = big.is_emi.mean()
            traits.append(f"Big purchases (₹20,000+): <b>{e:.0%} on EMI</b>" + (f", always with {big.bank.value_counts().idxmax()}" if big.bank.nunique() == 1 and big.bank.iloc[0] else "") + ".")
        dow = ctx.date.dt.day_name().value_counts().idxmax(); hr = int(ctx.date.dt.hour.median())
        traits.append(f"Usually shops around <b>{hr}:00</b>; most common day: <b>{dow}</b>.")
        if c.shops_online and c.shops_store:
            traits.append("Shops <b>both in store and online</b>, so offers should work in both places.")
        if (ctx.category == "Gift cards").any():
            traits.append("Buys <b>gift cards in the festive season</b> for family.")
        if pd.notna(c.median_gap):
            traits.append(f"Returns every <b>~{int(c.median_gap)} days</b>; it has now been {int(c.days_since)} days.")
        tc = st.columns(2)
        for i_, tline in enumerate(traits):
            tc[i_ % 2].markdown(f"<div class='gc-trait'>{tline}</div>", unsafe_allow_html=True)
    with br:
        if MVP:
            st.markdown("**Scores** <span class='later'>Later phase</span>", unsafe_allow_html=True)
            st.caption("Predictive scores are added after the MVP proves the basic segments and alerts work.")
        else:
            st.markdown("**Scores**")
            st.progress(float(c.upgrade_score), text=f"Likely to upgrade soon: {c.upgrade_score:.0%}")
            st.progress(float(c.churn_risk), text=f"Risk of not returning: {c.churn_risk:.0%}")
            st.markdown(kpi("Expected spend, next 12 months", inr(c.pred_12m_value),
                            "Based on visit rhythm, time since last phone, EMI history and segment. Simple and explainable by design."),
                        unsafe_allow_html=True)
        if pick == "C0001" and not MVP:
            st.markdown("**What the cashier sees when she pays** <span class='later'>Later phase</span>", unsafe_allow_html=True)
            st.markdown(f"""<div class='pos'><div class='bar'>Pine Labs POS · Payment received</div><div class='scr'>
                <b>Returning customer: Riya M.</b> · VIP · 10th visit<br>Laptop EMI completed Jul 2026. Phone is 30 months old.<br>
                <b style='color:{PINE}'>Eligible: exchange bonus + 0% EMI</b><br>
                <span class='btn' style='background:{PINE};color:#fff'>Show offer</span><span class='btn' style='background:#EEE;color:#555'>Skip</span>
                </div></div>""", unsafe_allow_html=True)

    t1c, t2c, t3c = st.columns(3, gap="large")
    with t1c:
        st.markdown("**EMI history**")
        emi = ctx[ctx.is_emi].copy()
        if len(emi):
            st.markdown(html_table(pd.DataFrame({"Product": emi["item"], "Amount": emi.amount.map(inr),
                                       "Plan": emi.emi_tenure.astype(int).astype(str) + " months, " + emi.bank,
                                       "Status": np.where(emi.emi_end <= TODAY, "Ended " + emi.emi_end.dt.strftime("%b %Y"),
                                                          "Ends " + emi.emi_end.dt.strftime("%b %Y"))})), unsafe_allow_html=True)
        else:
            st.caption("No EMI purchases.")
    with t2c:
        st.markdown("**Prepaid & gift cards**")
        if len(cgc):
            st.markdown(html_table(pd.DataFrame({"Type": cgc.source.str.replace(r" \(.*\)", "", regex=True), "Balance": cgc.balance.map(inr),
                                       "Expires": cgc.expiry.dt.strftime("%d %b %Y")})), unsafe_allow_html=True)
        else:
            st.caption("No gift cards or store credit.")
    with t3c:
        st.markdown("**How she responds to messages**")
        if pick == "C0001":
            st.markdown(html_table(pd.DataFrame({"Campaign": riya_msgs.campaign, "Via": riya_msgs.channel,
                                       "Result": np.where(riya_msgs.purchased, "Bought", np.where(riya_msgs.opened, "Read", "Ignored"))})), unsafe_allow_html=True)
            st.caption("Reads every WhatsApp; ignored the one SMS. Best channel: WhatsApp.")
        else:
            st.caption("No campaigns sent to this customer yet.")

    st.markdown("#### Next best actions for this customer")
    if flags:
        ncols = st.columns(min(3, len(flags)))
        ranked = sorted(flags, key=lambda a: -a["urgency"] * a["conv"] * a["ticket"])
        for col, a in zip(ncols, ranked[:3]):
            with col:
                st.markdown(f"<div class='gc-nba'><div class='t'>{a['title']}</div><div class='d'><b>Why her:</b> {a['rule']}.</div>"
                            f"<div class='d'><b>Offer:</b> {a['offer']}</div><div class='d'><b>Paid by:</b> {a['funded_by']} · <b>Via:</b> {a['channel']}</div></div>",
                            unsafe_allow_html=True)
        st.caption("Open the Growth actions tab to send any of these to her and everyone else who qualifies.")
    else:
        st.info("No open opportunities for this customer right now. She will appear here when a signal fires (e.g. an EMI ends).")

    with st.expander("All payments for this customer"):
        st.dataframe(ctx[["date", "channel", "method", "identifier", "item", "category", "amount", "is_emi", "emi_tenure"]],
                     hide_index=True, width="stretch",
                     column_config={"date": st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
                                    "amount": st.column_config.NumberColumn("Amount", format="₹%d"),
                                    "is_emi": st.column_config.CheckboxColumn("EMI"), "emi_tenure": "EMI months",
                                    "identifier": "Paid with", "item": "Item"})

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — GROWTH ACTIONS
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### How growth actions are created")
    steps = [
        ("1", "Signal", "The console watches payment data from POS, UPI, online and prepaid: EMI end dates, visit gaps, gift card balances, channel mix."),
        ("2", "Rule", "Each signal has a plain rule, e.g. 'EMI ended in the last 90 days and no purchase since'."),
        ("3", "Audience", "Customers who match, minus anyone who hasn't agreed to messages on that channel."),
        ("4", "Offer & funding", "A ready offer, often funded by a brand or bank through Pine Labs' network, so the merchant pays less."),
        ("5", "Send & measure", "Sent on WhatsApp/SMS with 10% held back. Sales paid on Pine Labs show what the campaign really added."),
    ]
    sc_ = st.columns(5)
    for col, (n, h, b) in zip(sc_, steps):
        col.markdown(f"<div class='gc-step'><div class='n'>Step {n}</div><div class='h'>{h}</div><div class='b'>{b}</div></div>",
                     unsafe_allow_html=True)

    st.markdown("#### Recommended actions, ranked")
    st.caption("Ranked by expected extra revenue (above what these customers would spend anyway) × urgency. "
               f"Baseline purchase rate without any message: {BASELINE_CONV:.1%}, from past control groups.")
    types = ["All", "Offer", "EMI promo", "Gift card push", "WhatsApp/SMS nudge"]
    tsel = st.radio("Action type", types, horizontal=True, label_visibility="collapsed")
    at = acts if tsel == "All" else acts[acts.Type == tsel]
    if MVP:
        at = at[at.key.map(lambda k_: ACT[k_].get("mvp", True))]
    st.dataframe(at[["Priority score", "Action", "Type", "Reachable", "Expected buyers", "Incremental revenue", "Funded by"]],
                 hide_index=True, width="stretch",
                 column_config={"Priority score": st.column_config.ProgressColumn("Priority", min_value=0, max_value=100, format="%d", width="small"),
                                "Type": st.column_config.TextColumn("Type", width="small"),
                                "Expected buyers": st.column_config.NumberColumn("Buyers (est.)", width="small"),
                                "Funded by": st.column_config.TextColumn("Paid for by", width="medium"),
                                "Audience": st.column_config.NumberColumn("Match rule"),
                                "Reachable": st.column_config.NumberColumn("Can message", help="Matched the rule AND opted in on this channel", width="small"),
                                "Incremental revenue": st.column_config.NumberColumn("Extra ₹ (est.)", format="localized", width="small")})

    st.divider()
    st.markdown("#### Build a campaign")
    choice = st.selectbox("Choose an action", at.key.tolist() if len(at) else acts.key.tolist(), format_func=lambda k_: ACT[k_]["title"])
    a = ACT[choice]
    row = acts[acts.key == choice].iloc[0]
    aud = cm[cm[a["flag"]]]

    d1, d2 = st.columns([1.15, 1], gap="large")
    with d1:
        st.markdown(f"<div class='gc-card'><b>{a['title']}</b> <span class='gc-tag opp'>{a['type']}</span><br><br>"
                    f"<b>Signal:</b> {a['signal']}<br><b>Rule:</b> {a['rule']}<br><b>Why it works:</b> {a['why']}<br>"
                    f"<b>Offer:</b> {a['offer']}<br><b>Paid for by:</b> {a['funded_by']}<br><b>Channel:</b> {a['channel']}</div>",
                    unsafe_allow_html=True)
        st.markdown("")
        funnel = go.Figure(go.Funnel(
            y=["Match the rule", "Opted in on channel", "Sent (after hold-back)", "Expected buyers"],
            x=[int(row.Audience), int(row.Reachable), int(round(row.Reachable * 0.9)), max(1, round(row.Reachable * 0.9 * a["conv"]))],
            marker=dict(color=[SAGE, MOSS, PINE, MARIGOLD]), textinfo="value"))
        st.plotly_chart(style_fig(funnel, 250, legend=False).update_layout(title=f"From signal to buyers (out of {len(cm):,} known customers)"), width="stretch")

        st.markdown("**Who is in this audience**")
        prev = aud.reset_index()
        prev["Can message on"] = np.where(prev.whatsapp_opt_in & prev.sms_opt_in, "WhatsApp, SMS",
                                 np.where(prev.whatsapp_opt_in, "WhatsApp", np.where(prev.sms_opt_in, "SMS", "Not opted in")))
        prev["_o"] = (prev.customer_id != "C0001").astype(int)
        prev = prev.sort_values(["_o", "total_spend"], ascending=[True, False])[["name", "segment", "total_spend", "days_since", "Can message on"]]
        st.dataframe(prev.head(50), hide_index=True, width="stretch", height=220,
                     column_config={"name": "Name", "segment": "Segment", "total_spend": st.column_config.NumberColumn("Lifetime spend (₹)", format="localized"),
                                    "days_since": "Days since visit"})
        if "C0001" in aud.index:
            st.caption("Riya Malhotra is in this audience.")

    with d2:
        st.markdown("**Settings**")
        ch_opts = ["WhatsApp", "SMS", "WhatsApp + SMS fallback"]
        ch_def = 1 if a["channel"] == "SMS" else 2 if "SMS" in a["channel"] else 0
        send_ch = st.radio("Send via", ch_opts, index=ch_def, horizontal=True)
        holdout = st.slider("Hold back for comparison", 5, 20, 10, format="%d%%",
                            help="These customers get nothing. Comparing them with those who got the offer shows the real extra sales.")
        cap = st.checkbox("Skip customers who already got 2 offers this month", value=True)
        when = st.selectbox("When", ["Now", "Tomorrow, 10:00", "Saturday, 11:00 (busiest day)"], key="when_sel")
        reach = int(row.Reachable * (0.88 if cap else 1.0))
        sent = int(round(reach * (1 - holdout / 100)))
        unit = WA_COST if send_ch == "WhatsApp" else SMS_COST if send_ch == "SMS" else WA_COST + 0.3 * SMS_COST
        if "utility" in a["channel"]:
            unit = WA_UTIL
        exp_buy = sent * a["conv"]
        incr = sent * max(a["conv"] - BASELINE_CONV, 0) * a["ticket"]
        e1, e2, e3 = st.columns(3)
        e1.metric("Will receive", f"{sent:,}")
        e2.metric("Expected buyers", f"{exp_buy:.0f}")
        e3.metric("Extra revenue", inr(incr))
        your_cost = sent * unit + exp_buy * a["merchant_cost"]
        partner = exp_buy * a["partner_cost"]
        e4, e5, e6 = st.columns(3)
        e4.metric("Held back", f"{reach - sent:,}")
        e5.metric("Cost to you", inr(your_cost), help="Messages + any discount you fund, for the expected buyers.")
        e6.metric("Paid by brand/bank", inr(partner), help="Exchange bonus or EMI interest covered by partners through Pine Labs.")

        first = aud[aud.whatsapp_opt_in.fillna(False)].name.iloc[0].split()[0] if len(aud) else "Riya"
        if "C0001" in aud.index:
            first = "Riya"
        msg = {
            "emi_ended": f"Hi {first}, your laptop EMI with HDFC Bank is complete. Congratulations! 🎉 Upgrade your Galaxy this month at Anand Electronics: exchange bonus up to ₹5,000 + 0% EMI for 12 months. Valid till 31 Oct.",
            "upgrade_due": f"Hi {first}, your phone is over 2 years old. Get a free exchange valuation at Anand Electronics and upgrade on no-cost EMI.",
            "lapsing": f"Hi {first}, we've missed you at Anand Electronics! Here's ₹300 off on ₹2,000+ this month, in store or online.",
            "gift_expiring": f"Hi {first}, you have ₹750 of store credit at Anand Electronics expiring on 15 Dec. Use it on a ₹3,000+ purchase and get ₹200 extra.",
            "festive": f"Hi {first}, festive gifting made easy: buy ₹5,000 in Anand Electronics gift cards and get ₹250 extra value.",
            "cross_sell": f"Hi {first}, enjoying your new device? Get 15% off any case, charger or earbuds at Anand Electronics for 30 days.",
            "online_to_store": f"Hi {first}, you're just a few km from Anand Electronics. Visit for a live demo and free installation, same prices as online.",
            "full_pay_high": f"Hi {first}, did you know you can buy on no-cost EMI with your debit card at Anand Electronics? Check eligibility in store.",
            "second_purchase": f"Hi {first}, thanks for shopping at Anand Electronics! Here's ₹150 off your next purchase.",
        }[choice]
        st.markdown("**Message preview**")
        st.markdown(f"""<div class='wa-wrap'><div class='wa-head'>Anand Electronics</div>
            <div class='wa-msg'>{msg}</div><div class='wa-btn'>View offer</div><div class='wa-btn'>Stop offers</div>
            <div class='wa-time'>{'SMS version is shortened to 160 characters' if send_ch == 'SMS' else 'Sent via Pine Labs'}</div></div>""",
                    unsafe_allow_html=True)
        st.markdown("")
        if st.button(f"Launch campaign to {sent:,} customers", type="primary", width="stretch"):
            st.success(f"Campaign launched. {sent:,} messages scheduled ({when}); {reach - sent:,} customers held back for comparison. "
                       "You'll get the results on WhatsApp after 14 days.")
        st.caption("Only customers who opted in are messaged. Every message has a one-tap opt-out.")

    st.divider()
    st.markdown("#### Results of past campaigns")
    st.caption("Each campaign is compared with the customers held back. 'Lift' = how many times more likely the offer group was to buy.")
    r1 = st.container()
    r2 = st.container()
    with r1:
        cmp = campaigns.melt(id_vars="campaign", value_vars=["conv_t", "conv_c"], var_name="group", value_name="rate")
        cmp["group"] = cmp.group.map({"conv_t": "Got the offer", "conv_c": "Held back"})
        f = px.bar(cmp, x="rate", y="campaign", color="group", barmode="group", orientation="h",
                   color_discrete_map={"Got the offer": PINE, "Held back": "#C3CEC8"}, title="Purchase rate: offer group vs held back")
        f.update_xaxes(tickformat=".0%", title=None); f.update_yaxes(title=None)
        st.plotly_chart(style_fig(f, 420), width="stretch")
    with r2:
        st.dataframe(campaigns.sort_values("launched", ascending=False)[["campaign", "launched", "type", "channel", "sent", "buyers", "lift_x", "incremental_rev", "opt_out_rate", "funded_by"]],
                     hide_index=True, width="stretch",
                     column_config={"campaign": "Campaign", "type": "Type", "sent": "Sent", "buyers": "Buyers",
                                    "lift_x": st.column_config.NumberColumn("Lift", format="%.1f×"),
                                    "launched": st.column_config.DateColumn("Launched", format="DD MMM YY"),
                                    "incremental_rev": st.column_config.NumberColumn("Extra revenue (₹)", format="localized"),
                                    "channel": "Channel",
                                    "opt_out_rate": st.column_config.NumberColumn("Opt-outs", format="percent"),
                                    "funded_by": "Paid for by"})

    st.markdown("#### Is the console working? Success metrics")
    st.caption("What Pine Labs and the merchant track to decide whether the Growth Console is succeeding.")
    s1, s2, s3, s4 = st.columns(4, gap="medium")
    cpm_ = len(c90) / 6
    lift_ = c90.lift_x.mean(); opt_ = c90.opt_outs.sum() / c90.sent.sum()
    with s1:
        st.markdown("**North star**")
        st.markdown(kpi("Extra revenue from campaigns (6 months)", inr(c90.incremental_rev.sum()), "Offer group vs held-back customers, paid on Pine Labs"), unsafe_allow_html=True)
        st.markdown(kpi("Repeat-customer revenue share", f"{repeat_rev_share:.0%}", "Target: +5 points in 6 months"), unsafe_allow_html=True)
    with s2:
        st.markdown("**Is the merchant using it?**")
        st.markdown(kpi("Campaigns launched per month", f"{cpm_:.1f}", "Target: 2 or more", "good" if cpm_ >= 2 else "warn", "on track" if cpm_ >= 2 else "below target"), unsafe_allow_html=True)
        st.markdown(kpi("Days active in console (last 30)", "19", "Target: 12 or more", "good", "on track"), unsafe_allow_html=True)
    with s3:
        st.markdown("**Are customers coming back?**")
        st.markdown(kpi("Transactions linked to a profile", f"{linked_share:.0%}", "Target: 30% or more", "good" if linked_share >= 0.3 else "warn", "on track" if linked_share >= 0.3 else "below target"), unsafe_allow_html=True)
        st.markdown(kpi("Average lift vs held back", f"{lift_:.1f}×", "Target: 3× or more", "good" if lift_ >= 3 else "warn", "on track" if lift_ >= 3 else "below target"), unsafe_allow_html=True)
    with s4:
        st.markdown("**Guardrails**")
        st.markdown(kpi("Opt-out rate", f"{opt_:.1%}", "Must stay under 2%", "good" if opt_ < 0.02 else "bad", "safe" if opt_ < 0.02 else "breached"), unsafe_allow_html=True)
        st.markdown(kpi("Max offers per customer per month", "2", "Frequency cap is on", "good", "safe"), unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — PAYMENT TRENDS (aggregate)
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    fc1, fc2 = st.columns([2, 1])
    period = fc1.radio("Period", ["Last 3 months", "Last 6 months", "Last 12 months", "Since Jan 2024"], index=2, horizontal=True)
    months = {"Last 3 months": 3, "Last 6 months": 6, "Last 12 months": 12, "Since Jan 2024": 33}[period]
    chsel = fc2.multiselect("Touchpoints", CHANNELS, default=CHANNELS)
    p_start = (TODAY.to_period("M") - (months - 1)).to_timestamp() - pd.Timedelta(seconds=1)
    prev_start = (TODAY.to_period("M") - (2 * months - 1)).to_timestamp() - pd.Timedelta(seconds=1)
    T_ = tx[(tx.date > p_start) & tx.channel.isin(chsel)]
    P_ = tx[(tx.date > prev_start) & (tx.date <= p_start) & tx.channel.isin(chsel)]

    def delta(cur, prev, pct=True):
        if prev == 0:
            return None
        return f"{(cur - prev) / prev:+.0%}"

    st.caption("Changes are compared with the previous period of the same length.")
    kk = st.columns(6)
    kk[0].metric("Sales (GTV)", inr(T_.amount.sum()), delta(T_.amount.sum(), P_.amount.sum()))
    kk[1].metric("Transactions", f"{len(T_):,}", delta(len(T_), len(P_)))
    kk[2].metric("Average bill", inr(T_.amount.mean()), delta(T_.amount.mean(), P_.amount.mean() if len(P_) else 0))
    kk[3].metric("UPI share of transactions", f"{(T_.channel == 'UPI').mean():.0%}")
    kk[4].metric("EMI share of sales value", f"{T_[T_.is_emi].amount.sum() / max(T_.amount.sum(), 1):.0%}")
    kk[5].metric("Linked to a customer", f"{T_.customer_id.notna().mean():.0%}", help="Share of transactions the console can tie to a known person.")

    # Auto-generated insights
    upi_cnt = (T_.channel == "UPI").mean(); upi_val = T_[T_.channel == "UPI"].amount.sum() / max(T_.amount.sum(), 1)
    big = T_[T_.amount >= 25000]; emi_big = big.is_emi.mean() if len(big) else 0
    hm = T_.assign(dow=T_.date.dt.day_name(), hr=T_.date.dt.hour).groupby(["dow", "hr"]).size()
    peak = hm.idxmax() if len(hm) else ("Saturday", 19)
    emi_next = tx[tx.is_emi & tx.customer_id.notna() & tx.emi_end.between(TODAY, TODAY + pd.Timedelta(days=90))]
    omni = cm[cm.shops_online & cm.shops_store]; store_only = cm[cm.shops_store & ~cm.shops_online]
    st.markdown("#### What stands out")
    ins = [
        f"<b>UPI is {upi_cnt:.0%} of transactions but only {upi_val:.0%} of sales value.</b> Small buys go on UPI; big-ticket purchases still run on cards and EMI. Without the console, most UPI buyers stay anonymous.",
        f"<b>{emi_big:.0%} of purchases over ₹25,000 are on EMI.</b> EMI is how this store sells high-value products, so EMI end dates are the best upgrade signal.",
        f"<b>{len(emi_next)} customer EMIs end in the next 90 days</b> ({inr(emi_next.amount.sum())} of original purchases). That is next quarter's upgrade pipeline.",
        f"<b>Customers who shop both online and in store spend {omni.total_spend.mean() / max(store_only.total_spend.mean(), 1):.1f}× more</b> than store-only customers, but they are only {len(omni) / len(cm):.0%} of customers.",
        f"<b>Busiest time: {peak[0]}s around {peak[1]}:00.</b> Schedule campaign messages for the morning of the busiest days.",
    ]
    ic = st.columns(2)
    for i, s in enumerate(ins):
        ic[i % 2].markdown(f"<div class='gc-insight'>{s}</div>", unsafe_allow_html=True)

    st.markdown("#### How customers pay")
    g1, g2 = st.columns([1.5, 1], gap="large")
    with g1:
        metric = st.radio("Show", ["Sales value", "Number of transactions"], horizontal=True, key="mixm")
        mon = T_.groupby(["month", "channel"]).agg(v=("amount", "sum"), n=("txn_id", "size")).reset_index()
        f = px.bar(mon, x="month", y="v" if metric == "Sales value" else "n", color="channel", color_discrete_map=CH_COLORS,
                   category_orders={"channel": CHANNELS}, title="Touchpoint mix by month")
        f.update_yaxes(title=None); f.update_xaxes(title=None)
        st.plotly_chart(style_fig(f, 380), width="stretch")
    with g2:
        meth = T_.copy()
        meth["how"] = np.where(meth.is_emi & (meth.method == "Cardless EMI"), "Cardless EMI",
                     np.where(meth.is_emi, meth.method + " EMI", meth.method))
        mm = meth.groupby("how").amount.sum().sort_values(ascending=False).reset_index()
        f = px.pie(mm, names="how", values="amount", hole=0.6, title="Payment method, by value", color="how",
                   color_discrete_map={"UPI": MOSS, "Credit card": PINE, "Debit card": "#5E8C78", "Net banking": "#A7B7AF",
                                       "Gift card": SAGE, "Credit card EMI": MARIGOLD, "Debit card EMI": "#E7C680", "Cardless EMI": "#A8740A"})
        f.update_traces(textinfo="percent", textposition="inside")
        f.update_layout(uniformtext_minsize=11, uniformtext_mode="hide")
        st.plotly_chart(style_fig(f, 420), width="stretch")

    g3, g4 = st.columns(2, gap="large")
    with g3:
        bands = pd.cut(T_.amount, [0, 2000, 10000, 25000, 50000, 1e9], labels=["< ₹2k", "₹2–10k", "₹10–25k", "₹25–50k", "₹50k+"])
        bm_ = T_.assign(band=bands, how=np.where(T_.is_emi, "EMI (card / cardless)", np.where(T_.channel == "UPI", "UPI",
                        np.where(T_.channel == "Prepaid", "Gift card", "Card / online, full payment"))))
        tb = bm_.groupby(["band", "how"], observed=True).size().reset_index(name="n")
        tb["share"] = tb.n / tb.groupby("band", observed=True).n.transform("sum")
        f = px.bar(tb, x="band", y="share", color="how", title="Bill size decides how people pay",
                   color_discrete_map={"UPI": MOSS, "EMI (card / cardless)": MARIGOLD, "Card / online, full payment": PINE, "Gift card": SAGE})
        f.update_yaxes(tickformat=".0%", title=None); f.update_xaxes(title=None)
        st.plotly_chart(style_fig(f, 360), width="stretch")
    with g4:
        up = T_[T_.upi_app != ""].groupby("upi_app").size().sort_values().reset_index(name="n")
        f = px.bar(up, x="n", y="upi_app", orientation="h", title="UPI apps customers use", color_discrete_sequence=[MOSS])
        f.update_xaxes(title=None); f.update_yaxes(title=None)
        st.plotly_chart(style_fig(f, 330, legend=False), width="stretch")

    st.markdown("#### EMI and affordability")
    e1_, e2_, e3_ = st.columns([1.1, 1, 1.2], gap="large")
    E = T_[T_.is_emi]
    with e1_:
        pen = T_[T_.amount >= 10000].groupby("category").agg(emi=("is_emi", "mean"), n=("txn_id", "size")).reset_index()
        pen = pen[pen.n >= 5].sort_values("emi")
        f = px.bar(pen, x="emi", y="category", orientation="h", title="EMI use on ₹10k+ purchases", color_discrete_sequence=[MARIGOLD])
        f.update_xaxes(tickformat=".0%", title=None); f.update_yaxes(title=None)
        st.plotly_chart(style_fig(f, 300, legend=False), width="stretch")
    with e2_:
        lend = E.groupby("bank").amount.sum().sort_values(ascending=False).reset_index()
        f = px.pie(lend, names="bank", values="amount", hole=0.55, title="EMI value by lender",
                   color_discrete_sequence=[PINE, MOSS, MARIGOLD, SAGE, "#6E8B7D", "#E7C680", "#C3CEC8"])
        f.update_traces(textinfo="percent", textposition="inside")
        f.update_layout(uniformtext_minsize=11, uniformtext_mode="hide")
        st.plotly_chart(style_fig(f, 300), width="stretch")
    with e3_:
        pipe = tx[tx.is_emi & tx.customer_id.notna() & tx.emi_end.between(TODAY - pd.Timedelta(days=90), TODAY + pd.Timedelta(days=180))].copy()
        pipe["m"] = pipe.emi_end.dt.to_period("M").dt.to_timestamp()
        pp = pipe.groupby("m").size().reset_index(name="n")
        pp["when"] = np.where(pp.m < TODAY.to_period("M").to_timestamp(), "Ended", "Ending")
        f = px.bar(pp, x="m", y="n", color="when", title="EMIs ending by month: the upgrade pipeline",
                   color_discrete_map={"Ended": SAGE, "Ending": MARIGOLD})
        f.update_xaxes(title=None, dtick="M1", tickformat="%b %y"); f.update_yaxes(title="Customers")
        st.plotly_chart(style_fig(f, 300), width="stretch")

    st.markdown("#### When and how often customers come back")
    w1, w2 = st.columns([1, 1.2], gap="large")
    with w1:
        hmd = T_.assign(dow=T_.date.dt.day_name().str[:3], hr=T_.date.dt.hour)
        piv = hmd.pivot_table(index="dow", columns="hr", values="txn_id", aggfunc="count").reindex(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]).fillna(0)
        f = go.Figure(go.Heatmap(z=piv.values, x=[f"{h}:00" for h in piv.columns], y=piv.index,
                                 colorscale=[[0, "#F4F7F5"], [0.5, SAGE], [1, PINE]], showscale=False))
        f.update_layout(title="Busy hours (transactions)")
        st.plotly_chart(style_fig(f, 300, legend=False), width="stretch")
    with w2:
        nr = tx[tx.customer_id.notna() & tx.channel.isin(chsel)].copy()
        fd = cm.first_date.dt.to_period("M").dt.to_timestamp()
        nr["first_m"] = nr.customer_id.map(fd)
        nr["type"] = np.where(nr.month == nr.first_m, "New customers", "Returning customers")
        nr = nr[nr.date > p_start]
        nrm = nr.groupby(["month", "type"]).amount.sum().reset_index()
        anon = T_[T_.customer_id.isna()].groupby("month").amount.sum().reset_index().assign(type="Unlinked (no consent yet)")
        nrm = pd.concat([nrm, anon])
        f = px.area(nrm, x="month", y="amount", color="type", title="Sales from new vs returning customers",
                    color_discrete_map={"New customers": MARIGOLD, "Returning customers": PINE, "Unlinked (no consent yet)": "#C3CEC8"})
        f.update_yaxes(title=None); f.update_xaxes(title=None)
        st.plotly_chart(style_fig(f, 300), width="stretch")

    c1_, c2_ = st.columns([1.3, 1], gap="large")
    with c1_:
        v = tx[tx.customer_id.notna()].assign(day=lambda d: d.date.dt.normalize())
        v["cohort"] = v.customer_id.map(cm.first_date.dt.to_period("Q").astype(str))
        v["qi"] = ((v.date.dt.year - v.customer_id.map(cm.first_date.dt.year)) * 4 +
                   (v.date.dt.quarter - v.customer_id.map(cm.first_date.dt.quarter)))
        sizes = v.groupby("cohort").customer_id.nunique()
        coh = v.groupby(["cohort", "qi"]).customer_id.nunique().unstack().div(sizes, axis=0)
        coh = coh.loc[:, [c_ for c_ in coh.columns if 1 <= c_ <= 8]]
        f = go.Figure(go.Heatmap(z=coh.values, x=[f"Q+{int(c_)}" for c_ in coh.columns], y=coh.index,
                                 colorscale=[[0, "#F4F7F5"], [0.5, SAGE], [1, PINE]], zmin=0, zmax=0.35,
                                 text=np.where(np.isnan(coh.values), "", (coh.values * 100).round().astype("float").astype(str)),
                                 hovertemplate="Cohort %{y}, %{x}: %{z:.0%} came back<extra></extra>", showscale=False))
        f.update_layout(title="Share of each quarter's new customers who came back later")
        f.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(f, 330, legend=False), width="stretch")
    with c2_:
        om = pd.DataFrame({
            "group": ["Store only", "Online only", "Store + online"],
            "customers": [int((cm.shops_store & ~cm.shops_online).sum()), int((~cm.shops_store & cm.shops_online).sum()), int((cm.shops_store & cm.shops_online).sum())],
            "avg_spend": [cm[cm.shops_store & ~cm.shops_online].total_spend.mean(), cm[~cm.shops_store & cm.shops_online].total_spend.mean(),
                          cm[cm.shops_store & cm.shops_online].total_spend.mean()]})
        f = px.bar(om, x="group", y="avg_spend", text=om.customers.map(lambda n: f"{n:,} customers"), title="Average lifetime spend by how they shop",
                   color="group", color_discrete_map={"Store only": MOSS, "Online only": MARIGOLD, "Store + online": PINE})
        f.update_traces(textposition="outside"); f.update_yaxes(title=None); f.update_xaxes(title=None)
        st.plotly_chart(style_fig(f, 330, legend=False), width="stretch")

    st.markdown("#### Prepaid and gift cards")
    p1, p2, p3, p4 = st.columns(4)
    sold = tx[(tx.category == "Gift cards") & (tx.date > p_start)]
    redeemed = tx[(tx.channel == "Prepaid") & (tx.date > p_start)]
    open_bal = giftcards[(giftcards.balance > 0) & (giftcards.expiry > TODAY)]
    expired_bal = giftcards[(giftcards.balance > 0) & (giftcards.expiry <= TODAY)]
    p1.markdown(kpi("Gift cards sold", inr(sold.amount.sum()), f"{len(sold)} cards in this period"), unsafe_allow_html=True)
    p2.markdown(kpi("Redeemed in store", inr(redeemed.amount.sum()), f"{len(redeemed)} redemptions"), unsafe_allow_html=True)
    p3.markdown(kpi("Unspent balance (still valid)", inr(open_bal.balance.sum()), f"Held by {open_bal.customer_id.nunique()} customers: a reason to invite them back"), unsafe_allow_html=True)
    p4.markdown(kpi("Expired without being used", inr(expired_bal.balance.sum()), "Customers who never came back to redeem", "warn", "missed"), unsafe_allow_html=True)

    if MVP:
        st.markdown("#### How this store compares <span class='later'>Later phase</span>", unsafe_allow_html=True)
        st.caption("Peer benchmarks are added once enough merchants use the console.")
    else:
      st.markdown("#### How this store compares")
      st.caption("Anonymised averages from similar Pine Labs merchants (mobile & electronics, Tier-2 cities, ₹2–5 Cr annual sales). Illustrative.")
      bench = pd.DataFrame({
          "Measure": ["Repeat customers", "UPI share of transactions", "EMI share of sales value", "Average bill", "Transactions linked to a customer"],
          "This store": [f"{repeat_rate:.0%}", f"{(tx.channel == 'UPI').mean():.0%}", f"{tx[tx.is_emi].amount.sum() / tx.amount.sum():.0%}",
                         inr(tx.amount.mean()), f"{linked_share:.0%}"],
          "Similar stores": ["49%", "62%", "36%", "₹11,900", "38%"],
          "Top 25% of similar stores": ["61%", "58%", "43%", "₹14,200", "58%"],
      })
      st.dataframe(bench, hide_index=True, width="stretch")

st.divider()
st.caption("Prototype for Pine Labs Case Study 1. All customers, transactions and results are synthetic. "
           "WhatsApp rates from Meta's 2026 India rate card; other costs and benchmarks are assumptions.")
