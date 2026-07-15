import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
import hashlib
import uuid
import os
import json

st.set_page_config(page_title="Alexon Group M&E v2.0", layout="wide", initial_sidebar_state="expanded")

# ── Logo ────────────────────────────────────────────────────
LOGO_PATH = Path(__file__).parent / "alexon_logo.jpeg"
if LOGO_PATH.exists():
    import base64
    with open(LOGO_PATH, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    logo_src = f"data:image/jpeg;base64,{logo_b64}"
else:
    logo_src = None

# ── Theme: Cream / Black / Gold ────────────────────────────
BLACK = "#111111"
GOLD = "#D4AF37"
CREAM = "#F8F4ED"
WHITE = "#FFFFFF"
DARK_TEXT = "#1a1a2e"
MUTED = "#666666"

st.markdown(f"""
<style>
    .block-container {{ max-width: 100% !important; padding: 1rem 2rem !important; }}
    @media (max-width: 767px) {{ .block-container {{ padding: 0.5rem 0.8rem !important; }} }}

    #root, .stApp, .main, div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewContainer"] > .main {{
        background-color: {CREAM} !important;
    }}

    h1, h2, h3, h4, h5, h6, .stMarkdown, p, label,
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {{
        color: {DARK_TEXT} !important;
    }}

    .logo-section {{ display:flex; flex-direction:column; align-items:center; justify-content:center; padding:24px 0 16px; }}
    .logo-circle {{ width:120px; height:120px; border-radius:50%; overflow:hidden; border:3px solid {GOLD}; background:#fff; box-shadow:0 0 30px rgba(212,175,55,0.2); }}
    .logo-circle img {{ width:100%; height:100%; object-fit:cover; }}
    .logo-text {{ text-align:center; margin-top:12px; }}
    .logo-text h1 {{ font-size:36px; font-weight:900; color:{BLACK}; letter-spacing:6px; text-transform:uppercase; margin:0; }}
    .logo-text .sub {{ font-size:13px; color:{MUTED}; letter-spacing:3px; }}

    .login-box {{ max-width:400px; margin:40px auto; padding:40px; background:{WHITE}; border-radius:12px; box-shadow:0 4px 30px rgba(0,0,0,0.08); text-align:center; border:1px solid {GOLD}; }}
    .login-box h2 {{ color:{BLACK} !important; }}

    .stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input {{
        background-color: {WHITE} !important; color: {DARK_TEXT} !important; border: 1px solid #ccc !important;
    }}
    div[data-baseweb="select"] > div {{ background-color: {WHITE} !important; color: {DARK_TEXT} !important; }}
    div[data-baseweb="select"] ul {{ background-color: {WHITE} !important; }}
    div[data-baseweb="select"] li {{ color: {DARK_TEXT} !important; }}

    .stButton button {{
        width:100%; border-radius:8px !important; font-weight:600 !important;
        background-color: {BLACK} !important; color: #fff !important; border: none !important;
    }}
    .stButton button:hover {{ background-color: #333 !important; }}

    .st-emotion-cache-1c7y2kd, .stMetric label, .stMetric .metric-label {{ color: {MUTED} !important; }}
    .stMetric .metric-value {{ color: {BLACK} !important; font-weight:700 !important; }}
    .stMetric .metric-delta {{ font-weight:500 !important; }}

    div[data-testid="metric-container"] {{
        background: {WHITE}; padding:16px; border-radius:10px; box-shadow:0 1px 6px rgba(0,0,0,0.04);
    }}

    div[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #111 0%, #222 100%) !important;
        border-right: 2px solid {GOLD} !important;
    }}
    div[data-testid="stSidebar"] .stMarkdown,
    div[data-testid="stSidebar"] .stRadio div,
    div[data-testid="stSidebar"] label {{
        color: #f0f0f0 !important;
    }}
    div[data-testid="stSidebar"] .stRadio label:hover {{ color: {GOLD} !important; }}
    div[data-testid="stSidebarNav"] {{ display:none !important; }}

    .stDataFrame {{ background: {WHITE} !important; border-radius:8px; }}
    .stDataFrame thead tr th {{ background-color: {BLACK} !important; color: {GOLD} !important; }}
    .stDataFrame tbody tr td {{ background-color: {WHITE} !important; border-bottom:1px solid #eee !important; }}

    .stTabs [data-baseweb="tab-list"] {{ background: {WHITE} !important; border-radius:8px 8px 0 0; }}
    .stTabs [data-baseweb="tab"] {{ color: {MUTED} !important; }}
    .stTabs [aria-selected="true"] {{ color: {BLACK} !important; border-bottom-color: {GOLD} !important; }}

    div[role="alert"] {{ background-color: #ffe6e6 !important; color: #b30000 !important; border:1px solid #ff9999 !important; }}
    .stAlert {{ background-color: #e6ffe6 !important; color: #006600 !important; border:1px solid #99ff99 !important; }}

    hr {{ border-color: #e0d8cc !important; }}
</style>
""", unsafe_allow_html=True)

if logo_src:
    st.markdown(f"""
    <div class="logo-section">
        <div class="logo-circle"><img src="{logo_src}"></div>
        <div class="logo-text"><h1>ALEXON</h1><div class="sub">Group · M&E v2.0</div></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<div class='logo-section'><div class='logo-circle' style='width:120px;height:120px;border-radius:50%;background:{GOLD};display:flex;align-items:center;justify-content:center;'><span style='color:#000;font-weight:900;font-size:40px;'>A</span></div><div class='logo-text'><h1>ALEXON</h1><div class='sub'>Group · M&E v2.0</div></div></div>", unsafe_allow_html=True)

# ── Database ────────────────────────────────────────────────
DB = Path(__file__).parent / "alexon_v2.db"

def conn():
    return sqlite3.connect(str(DB))

def init_db():
    c = conn()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'clerk',
            site TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            site TEXT NOT NULL,
            item TEXT NOT NULL,
            produced INTEGER DEFAULT 0,
            sold INTEGER DEFAULT 0,
            wastage INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0,
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            site TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT DEFAULT '',
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS debtors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            qty INTEGER NOT NULL,
            amount REAL NOT NULL,
            paid REAL NOT NULL DEFAULT 0,
            balance REAL NOT NULL,
            entry_date TEXT NOT NULL,
            site TEXT NOT NULL,
            phone TEXT DEFAULT '',
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS hires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            phone TEXT DEFAULT '',
            equipment TEXT NOT NULL,
            daily_rate REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            paid REAL NOT NULL DEFAULT 0,
            balance REAL NOT NULL,
            returned INTEGER NOT NULL DEFAULT 0,
            site TEXT NOT NULL,
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            site TEXT NOT NULL,
            item TEXT NOT NULL,
            qty INTEGER NOT NULL,
            revenue REAL NOT NULL,
            prod_cost REAL DEFAULT 0,
            transport_cost REAL DEFAULT 0,
            profit REAL DEFAULT 0,
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    c.commit()
    admin = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not admin:
        pwd = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, site) VALUES (?,?,?,?)",
                  ("admin", pwd, "admin", ""))
        c.execute("INSERT INTO users (username, password, role, site) VALUES (?,?,?,?)",
                  ("clerk1", hashlib.sha256("clerk123".encode()).hexdigest(), "clerk", "Ugunja"))
        c.execute("INSERT INTO users (username, password, role, site) VALUES (?,?,?,?)",
                  ("clerk2", hashlib.sha256("clerk123".encode()).hexdigest(), "clerk", "Siaya"))
        c.execute("INSERT INTO users (username, password, role, site) VALUES (?,?,?,?)",
                  ("clerk3", hashlib.sha256("clerk123".encode()).hexdigest(), "clerk", "Bondo"))
        c.execute("INSERT INTO users (username, password, role, site) VALUES (?,?,?,?)",
                  ("manager", hashlib.sha256("mgr123".encode()).hexdigest(), "manager", "all"))
        c.commit()
    c.close()

init_db()

EQUIPMENT_ITEMS = [
    "Mixer Hire/Day", "Crane Lifter/Day", "Concrete Mixer", "Concrete Mixer Machine",
    "Caterpillar Grader 140K", "Wheel Loader", "Backhoe Loader", "Excavator",
    "Roller 20T", "Water Bowser 10000L", "Tipper Lorry 10T",
]

PRICES = {
    "Block Large 6x15x10": 75, "Block Medium 4x15x10": 65,
    "Culvert 2ft": 3200, "Culvert 3ft": 5200,
    "Fencing Post 10ft": 1450, "Fencing Post 9ft": 1350, "Fencing Post 8ft": 1250,
    "Cabros Normal": 1000, "Cabros 6x9": 1200,
    "Clear Water Trip": 5000, "Road Channel": 400,
    "Mixer Hire/Day": 6000, "Crane Lifter/Day": 6000,
    "Ballast 10T": 15000, "Sand 10T": 15000, "Road Carb": 500,
    "Machine Cut Stones": 60, "Ndurwe": 60,
    "Concrete Mixer": 10000, "Concrete Mixer Machine": 12000,
    "Manicured lawn": 3000,
    "Caterpillar Grader 140K": 75000, "Wheel Loader": 85000,
    "Backhoe Loader": 75000, "Excavator": 95000,
    "Roller 20T": 100000, "Water Bowser 10000L": 75000, "Tipper Lorry 10T": 65000,
}

# ── Auth ─────────────────────────────────────────────────────
def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def authenticate(u, p):
    c = conn()
    user = c.execute("SELECT id, username, role, site FROM users WHERE username=? AND password=?",
                     (u, hash_pwd(p))).fetchone()
    c.close()
    return user

def get_user():
    if "user" not in st.session_state:
        st.session_state.user = None
    return st.session_state.user

# ── Login screen ────────────────────────────────────────────
if not get_user():
    st.markdown(f"<div class='login-box'><h2>🔐 Alexon M&E Login</h2>", unsafe_allow_html=True)
    with st.form("login"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if st.form_submit_button("Login", use_container_width=True):
            user = authenticate(username, password)
            if user:
                st.session_state.user = {"id": user[0], "username": user[1], "role": user[2], "site": user[3]}
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

user = get_user()
role = user["role"]
site = user["site"]
username = user["username"]

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**👤 {username}** ({role.upper()})")
    st.markdown(f"📍 Site: {site if site else 'All'}")
    st.divider()

    menu_items = []
    if role == "admin":
        menu_items = ["📊 Dashboard", "📝 Daily Entry", "💰 Expenses", "🔧 Equipment Hire", "📋 Debtors", "📈 Profit Report", "👥 Users", "📁 All Data"]
    elif role == "manager":
        menu_items = ["📊 Dashboard", "📝 Daily Entry", "💰 Expenses", "🔧 Equipment Hire", "📋 Debtors", "📈 Profit Report", "📁 All Data"]
    else:
        menu_items = ["📝 Daily Entry", "💰 Expenses", "🔧 Equipment Hire", "📋 Debtors", "📁 My Data"]

    selection = st.radio("Menu", menu_items, label_visibility="collapsed")

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# ── Helpers ─────────────────────────────────────────────────
def load_query(q, params=()):
    c = conn()
    df = pd.read_sql_query(q, c, params=params)
    c.close()
    return df

def site_filter():
    if role == "clerk":
        return f"site='{site}'"
    return "1=1"

def get_sites():
    if role == "clerk":
        return [site]
    return ["Ugunja", "Siaya", "Bondo"]

def rank_color(val, is_max, is_min):
    """Green=best, yellow=good, orange=ok, red=worst"""
    if is_max:
        return "background:#1a6b3c; color:#fff; font-weight:700"
    if is_min:
        return "background:#8b1a1a; color:#fff; font-weight:700"
    return ""

def performance_band(val, min_v, max_v):
    """Map a value to a color band across green→yellow→orange→red"""
    if max_v == min_v:
        return "background:#1a6b3c; color:#fff"
    ratio = (val - min_v) / (max_v - min_v) if max_v != min_v else 1
    if ratio >= 0.75:
        return "background:#1a6b3c; color:#fff; font-weight:700"
    elif ratio >= 0.50:
        return "background:#b5a02a; color:#fff"
    elif ratio >= 0.25:
        return "background:#b5732a; color:#fff"
    else:
        return "background:#8b1a1a; color:#fff; font-weight:700"

# ── DASHBOARD ───────────────────────────────────────────────
if selection == "📊 Dashboard":
    st.subheader("📊 Live Dashboard")
    sf = site_filter()
    df = load_query(f"SELECT * FROM entries WHERE {sf}")
    exp_df = load_query(f"SELECT * FROM expenses WHERE {sf}")
    debt_df = load_query(f"SELECT * FROM debtors WHERE {sf}")

    hire_df = load_query(f"SELECT * FROM hires WHERE {sf}")

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    total_rev = df['revenue'].sum() if not df.empty else 0
    total_sold = df['sold'].sum() if not df.empty else 0
    total_prod = df['produced'].sum() if not df.empty else 0
    total_exp = exp_df['amount'].sum() if not exp_df.empty else 0
    total_debt = debt_df['balance'].sum() if not debt_df.empty else 0
    hire_rev = hire_df['total_cost'].sum() if not hire_df.empty else 0
    hire_bal = hire_df['balance'].sum() if not hire_df.empty else 0

    kpi1.metric("💰 Revenue", f"Ksh {total_rev:,}")
    kpi2.metric("📦 Sold", f"{total_sold:,}")
    kpi3.metric("🏭 Produced", f"{total_prod:,}")
    kpi4.metric("💸 Expenses", f"Ksh {total_exp:,.0f}", delta=f"Debt: Ksh {total_debt:,.0f}")
    kpi5.metric("🔧 Equipment Hire", f"Ksh {hire_rev:,.0f}", delta=f"Due: Ksh {hire_bal:,.0f}")

    if not df.empty:
        # ── Sales Performance Ranking: Products ──────────────
        st.markdown("---")
        st.subheader("🏆 Sales Performance Ranking — by Product")

        prod_perf = df.groupby("item").agg(Revenue=("revenue", "sum"), Sold=("sold", "sum")).reset_index()
        prod_perf = prod_perf.sort_values("Revenue", ascending=False).reset_index(drop=True)
        prod_perf.index = prod_perf.index + 1
        prod_perf.index.name = "Rank"

        if not prod_perf.empty:
            min_r = prod_perf["Revenue"].min()
            max_r = prod_perf["Revenue"].max()
            styled_prod = prod_perf.style.map(
                lambda v: performance_band(v, min_r, max_r), subset=["Revenue"]
            ).map(
                lambda v: performance_band(v, prod_perf["Sold"].min(), prod_perf["Sold"].max()), subset=["Sold"]
            )
            st.dataframe(styled_prod, use_container_width=True)

        # ── Sales Performance Ranking: Sites ────────────────
        st.markdown("---")
        st.subheader("🏆 Sales Performance Ranking — by Site")

        site_perf = df.groupby("site").agg(Revenue=("revenue", "sum"), Sold=("sold", "sum")).reset_index()
        site_perf = site_perf.sort_values("Revenue", ascending=False).reset_index(drop=True)
        site_perf.index = site_perf.index + 1
        site_perf.index.name = "Rank"

        if not site_perf.empty:
            min_s = site_perf["Revenue"].min()
            max_s = site_perf["Revenue"].max()
            styled_site = site_perf.style.map(
                lambda v: performance_band(v, min_s, max_s), subset=["Revenue"]
            ).map(
                lambda v: performance_band(v, site_perf["Sold"].min(), site_perf["Sold"].max()), subset=["Sold"]
            )
            st.dataframe(styled_site, use_container_width=True)

        # ── Charts ──────────────────────────────────────────
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 Sales by Product")
            st.bar_chart(df.groupby("item")["revenue"].sum(), color="#D4AF37")
        with col2:
            st.subheader("📈 Sales by Site")
            st.bar_chart(df.groupby("site")["revenue"].sum(), color="#D4AF37")

        # ── Stock Alert ─────────────────────────────────────
        st.subheader("📦 Stock Alert")
        stock = df.groupby("item")[["produced", "sold"]].sum()
        stock["Balance"] = stock["produced"] - stock["sold"]
        def alert_color(vals):
            return ["background:#8b1a1a; color:#fff; font-weight:700" if x < 50
                    else "background:#1a6b3c; color:#fff" if x >= 200
                    else "background:#b5732a; color:#fff" for x in vals]
        st.dataframe(stock.style.apply(alert_color, axis=1), use_container_width=True)

    if not hire_df.empty:
        st.markdown("---")
        st.subheader("🔧 Active Equipment Hires")
        active_hires = hire_df[hire_df['returned'] == 0]
        if not active_hires.empty:
            st.dataframe(active_hires[["customer", "equipment", "start_date", "end_date", "balance"]], use_container_width=True, hide_index=True)

# ── DAILY ENTRY ─────────────────────────────────────────────
elif selection == "📝 Daily Entry":
    st.subheader("📝 Daily Data Entry")
    sites = get_sites()
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", date.today())
        s = col2.selectbox("Site", sites)
        i = st.selectbox("Product", list(PRICES.keys()))
        col3, col4, col5 = st.columns(3)
        p = col3.number_input("Produced", 0)
        q = col4.number_input("Sold", 0)
        w = col5.number_input("Wastage", 0)

        if st.form_submit_button("💾 Save Entry"):
            revenue = q * PRICES[i]
            c = conn()
            c.execute("INSERT INTO entries (entry_date, site, item, produced, sold, wastage, revenue, user_id) VALUES (?,?,?,?,?,?,?,?)",
                      (d.isoformat(), s, i, p, q, w, revenue, user["id"]))
            c.commit()
            c.close()
            st.success(f"Saved! Revenue: Ksh {revenue:,}")
            st.rerun()

    st.divider()
    st.subheader("Entry History")
    sf = f"site='{site}'" if role == "clerk" else "1=1"
    df = load_query(f"SELECT entry_date as Date, site as Site, item as Item, produced as Prod, sold as Sold, wastage as Waste, revenue as Rev FROM entries WHERE {sf} ORDER BY entry_date DESC LIMIT 50")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "Alexon_Entries.csv", "text/csv")

# ── EXPENSES ────────────────────────────────────────────────
elif selection == "💰 Expenses":
    st.subheader("💰 Daily Expenses")
    sites = get_sites()
    with st.form("exp_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", date.today())
        s = col2.selectbox("Site", sites)
        cat = st.selectbox("Category", ["Fuel", "Labor", "Repairs", "Transport", "Materials", "Other"])
        col3, col4 = st.columns(2)
        amt = col3.number_input("Amount (Ksh)", 0.0)
        desc = col4.text_input("Description (optional)")
        if st.form_submit_button("💾 Save Expense"):
            c = conn()
            c.execute("INSERT INTO expenses (expense_date, site, category, amount, description, user_id) VALUES (?,?,?,?,?,?)",
                      (d.isoformat(), s, cat, amt, desc, user["id"]))
            c.commit()
            c.close()
            st.success(f"Expense saved: Ksh {amt:,.0f}")
            st.rerun()

    st.divider()
    st.subheader("Expense Summary")
    sf = site_filter()
    exp_df = load_query(f"SELECT * FROM expenses WHERE {sf} ORDER BY expense_date DESC LIMIT 50")
    if not exp_df.empty:
        st.dataframe(exp_df[["expense_date", "site", "category", "amount", "description"]], use_container_width=True, hide_index=True)
        st.metric("Total Expenses", f"Ksh {exp_df['amount'].sum():,.0f}")

# ── EQUIPMENT HIRE ─────────────────────────────────────────
elif selection == "🔧 Equipment Hire":
    st.subheader("🔧 Equipment Hire Management")

    tab_new, tab_active, tab_history = st.tabs(["➕ New Hire", "📌 Active Hires", "📋 All History"])

    with tab_new:
        sites = get_sites()
        with st.form("hire_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            customer = col1.text_input("Customer Name")
            phone = col2.text_input("Phone")
            col3, col4 = st.columns(2)
            equip = col3.selectbox("Equipment", EQUIPMENT_ITEMS)
            site = col4.selectbox("Site", sites)
            col5, col6 = st.columns(2)
            sdate = col5.date_input("Start Date", date.today())
            edate = col6.date_input("End Date", date.today() + timedelta(days=1))
            days = max(1, (edate - sdate).days)
            rate = PRICES[equip]
            total = days * rate
            st.info(f"**{days} day(s)** × **Ksh {rate:,}/day** = **Ksh {total:,}**")
            col7, col8 = st.columns(2)
            paid = col7.number_input("Amount Paid", 0.0)
            balance = total - paid
            st.caption(f"Balance: Ksh {balance:,.0f}")

            if st.form_submit_button("💾 Record Hire"):
                c = conn()
                c.execute("""INSERT INTO hires (customer, phone, equipment, daily_rate, start_date, end_date, days, total_cost, paid, balance, site, user_id)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                          (customer, phone, equip, rate, sdate.isoformat(), edate.isoformat(), days, total, paid, balance, site, user["id"]))
                c.commit()
                c.close()
                st.success(f"Hire recorded! Balance: Ksh {balance:,.0f}")
                st.rerun()

    with tab_active:
        sf = site_filter()
        active = load_query(f"SELECT * FROM hires WHERE {sf} AND returned=0 ORDER BY start_date DESC")
        if not active.empty:
            for _, row in active.iterrows():
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([2,1.5,1,1,1])
                    c1.markdown(f"**{row['customer']}** — {row['equipment']}")
                    c2.markdown(f"{row['start_date']} → {row['end_date']} ({row['days']}d)")
                    c3.markdown(f"Ksh {row['total_cost']:,.0f}")
                    c4.markdown(f"Bal: Ksh {row['balance']:,.0f}")
                    if c5.button("✅ Returned", key=f"ret_{row['id']}"):
                        conn().execute("UPDATE hires SET returned=1 WHERE id=?", (row['id'],)).connection.commit()
                        st.rerun()
                    st.divider()
        else:
            st.info("No active hires")

    with tab_history:
        sf = site_filter()
        hires = load_query(f"SELECT customer as Customer, phone as Phone, equipment as Equipment, daily_rate as Rate, start_date as 'Start', end_date as 'End', days as Days, total_cost as Total, paid as Paid, balance as Balance, CASE WHEN returned THEN '✅ Returned' ELSE '❌ Out' END as Status FROM hires WHERE {sf} ORDER BY start_date DESC")
        if not hires.empty:
            st.dataframe(hires, use_container_width=True, hide_index=True)
            csv = hires.to_csv(index=False).encode()
            st.download_button("📥 Download Hires", csv, "Alexon_Hires.csv", "text/csv")
            total_hire_debt = hires[pd.to_numeric(hires['Balance'], errors='coerce') > 0]['Balance'].sum() if 'Balance' in hires.columns else 0
            if total_hire_debt > 0:
                st.metric("Total Outstanding from Hires", f"Ksh {total_hire_debt:,.0f}")

# ── DEBTORS ─────────────────────────────────────────────────
elif selection == "📋 Debtors":
    st.subheader("📋 Credit Sales & Debtors")
    sites = get_sites()
    with st.form("debt_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        customer = col1.text_input("Customer Name")
        phone = col2.text_input("Phone (optional)")
        col3, col4 = st.columns(2)
        d = col3.date_input("Date", date.today())
        s = col4.selectbox("Site", sites)
        i = st.selectbox("Product", list(PRICES.keys()))
        col5, col6, col7 = st.columns(3)
        qty = col5.number_input("Qty", 1)
        amt = col6.number_input("Total Amount (Ksh)", 0.0)
        paid = col7.number_input("Amount Paid", 0.0)
        balance = amt - paid
        st.caption(f"Balance: Ksh {balance:,.0f}")
        if st.form_submit_button("💾 Record Credit Sale"):
            c = conn()
            c.execute("INSERT INTO debtors (customer, product, qty, amount, paid, balance, entry_date, site, phone, user_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (customer, i, qty, amt, paid, balance, d.isoformat(), s, phone, user["id"]))
            c.commit()
            c.close()
            st.success(f"Recorded! Balance: Ksh {balance:,.0f}")
            st.rerun()

    st.divider()
    st.subheader("Debtors List")
    sf = site_filter()
    debt_df = load_query(f"SELECT * FROM debtors WHERE {sf} ORDER BY entry_date DESC")
    if not debt_df.empty:
        st.dataframe(debt_df[["customer", "product", "qty", "amount", "paid", "balance", "entry_date", "site"]], use_container_width=True, hide_index=True)
        total_debt = debt_df["balance"].sum()
        st.metric("Total Outstanding Debt", f"Ksh {total_debt:,.0f}", delta=f"{len(debt_df)} debtors")
        csv = debt_df.to_csv(index=False).encode()
        st.download_button("📥 Download Debtors", csv, "Alexon_Debtors.csv", "text/csv")

# ── PROFIT REPORT ───────────────────────────────────────────
elif selection == "📈 Profit Report":
    st.subheader("📈 Profit Calculator")
    sf = site_filter()
    df = load_query(f"SELECT * FROM entries WHERE {sf}")
    exp_df = load_query(f"SELECT * FROM expenses WHERE {sf}")

    if not df.empty:
        prod_costs = exp_df[exp_df["category"].isin(["Labor", "Materials"])]["amount"].sum() if not exp_df.empty else 0
        transport = exp_df[exp_df["category"] == "Transport"]["amount"].sum() if not exp_df.empty else 0
        total_rev = df["revenue"].sum()
        profit = total_rev - prod_costs - transport

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("💰 Total Revenue", f"Ksh {total_rev:,.0f}")
        kpi2.metric("⚙️ Production Costs", f"Ksh {prod_costs:,.0f}")
        kpi3.metric("📈 Net Profit", f"Ksh {profit:,.0f}", delta=f"Margin: {(profit/total_rev*100):.0f}%" if total_rev > 0 else "0%")

        st.subheader("Profit by Product")
        prod_profit = df.groupby("item").agg({"revenue": "sum", "sold": "sum"}).reset_index()
        prod_profit.columns = ["Product", "Revenue", "Sold"]
        st.dataframe(prod_profit, use_container_width=True, hide_index=True)

        st.subheader("Profit by Site")
        site_profit = df.groupby("site")["revenue"].sum().reset_index()
        site_profit.columns = ["Site", "Revenue"]
        st.dataframe(site_profit, use_container_width=True, hide_index=True)
    else:
        st.info("Add entries to see profit report")

# ── USERS (admin only) ──────────────────────────────────────
elif selection == "👥 Users":
    if role != "admin":
        st.error("Access denied. Admins only.")
        st.stop()
    st.subheader("👥 User Management")

    with st.form("add_user"):
        col1, col2, col3 = st.columns(3)
        nu = col1.text_input("New Username")
        np = col2.text_input("Password", type="password")
        nr = col3.selectbox("Role", ["clerk", "manager", "admin"])
        ns = st.selectbox("Site", ["Ugunja", "Siaya", "Bondo", "all"])
        if st.form_submit_button("➕ Add User"):
            c = conn()
            try:
                c.execute("INSERT INTO users (username, password, role, site) VALUES (?,?,?,?)",
                          (nu, hash_pwd(np), nr, ns))
                c.commit()
                st.success(f"User {nu} created")
                st.rerun()
            except:
                st.error("Username already exists")
            c.close()

    st.divider()
    users_df = load_query("SELECT username, role, site, created_at FROM users")
    st.dataframe(users_df, use_container_width=True, hide_index=True)

# ── ALL / MY DATA ───────────────────────────────────────────
elif selection in ("📁 All Data", "📁 My Data"):
    st.subheader("📁 Full Data View")
    sf = f"site='{site}'" if role == "clerk" else "1=1"

    entries = load_query(f"SELECT entry_date as Date, site as Site, item as Item, produced as Prod, sold as Sold, wastage as Waste, revenue as Rev FROM entries WHERE {sf} ORDER BY entry_date DESC LIMIT 200")
    expenses = load_query(f"SELECT expense_date as Date, site as Site, category as Category, amount as Amount, description as Desc FROM expenses WHERE {sf} ORDER BY expense_date DESC LIMIT 200")
    debtors = load_query(f"SELECT customer as Customer, product as Product, qty as Qty, amount as Amount, paid as Paid, balance as Balance FROM debtors WHERE {sf} ORDER BY entry_date DESC LIMIT 200")

    hires = load_query(f"SELECT customer as Customer, equipment as Equipment, daily_rate as Rate, start_date as 'Start', end_date as 'End', days as Days, total_cost as Total, paid as Paid, balance as Balance, CASE WHEN returned THEN '✅' ELSE '❌' END as Returned FROM hires WHERE {sf} ORDER BY start_date DESC LIMIT 200")

    tab1, tab2, tab3, tab4 = st.tabs(["📦 Entries", "💰 Expenses", "🔧 Hires", "📋 Debtors"])
    with tab1:
        if not entries.empty:
            st.dataframe(entries, use_container_width=True, hide_index=True)
    with tab2:
        if not expenses.empty:
            st.dataframe(expenses, use_container_width=True, hide_index=True)
    with tab3:
        if not hires.empty:
            st.dataframe(hires, use_container_width=True, hide_index=True)
    with tab4:
        if not debtors.empty:
            st.dataframe(debtors, use_container_width=True, hide_index=True)
