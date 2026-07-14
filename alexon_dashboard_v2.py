import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from pathlib import Path

st.set_page_config(page_title="Alexon Group M&E", layout="centered")
st.title("🏗️ Alexon Group - M&E Dashboard")

# ── Database ────────────────────────────────────────────────
DB = Path(__file__).parent / "alexon_data.db"

def conn():
    return sqlite3.connect(str(DB))

def init():
    c = conn()
    c.execute("""CREATE TABLE IF NOT EXISTS e(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        d TEXT, s TEXT, i TEXT, p INTEGER, q INTEGER, r REAL
    )""")
    c.commit(); c.close()

init()

# ── Prices ──────────────────────────────────────────────────
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

# ── Helpers ─────────────────────────────────────────────────
def add(d, s, i, p, q):
    r = q * PRICES[i]
    c = conn()
    c.execute("INSERT INTO e(d,s,i,p,q,r) VALUES(?,?,?,?,?,?)", (d.isoformat(), s, i, p, q, r))
    c.commit(); c.close()
    return r

def load():
    return pd.read_sql_query("SELECT rowid as id,* FROM e ORDER BY d DESC", conn())

# ── Tabs (always visible on mobile) ─────────────────────────
tab1, tab2 = st.tabs(["📊 Dashboard", "📝 Daily Entries"])

with tab2:
    st.subheader("New Entry")
    with st.form("f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", date.today())
        s = col2.selectbox("Site", ["Ugunja", "Siaya", "Bondo"])
        i = st.selectbox("Product", list(PRICES.keys()))
        col3, col4 = st.columns(2)
        p = col3.number_input("Produced", 0)
        q = col4.number_input("Sold", 0)
        if st.form_submit_button("💾 Save"):
            if q > 0:
                r = add(d, s, i, p, q)
                st.success(f"Saved! Revenue: Ksh {r:,}")
            else:
                st.error("Sold qty must be > 0")

    st.divider()
    st.subheader("Entry History")
    df = load()
    if not df.empty:
        st.dataframe(df[["d", "s", "i", "p", "q", "r"]], use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "Alexon_Report.csv", "text/csv")

        if st.button("🗑️ Delete Last Entry"):
            c = conn()
            c.execute("DELETE FROM e WHERE id = (SELECT MAX(id) FROM e)")
            c.commit(); c.close()
            st.rerun()
    else:
        st.info("No entries yet")

with tab1:
    df = load()
    if not df.empty:
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("💰 Total Revenue", f"Ksh {df['r'].sum():,}")
        kpi2.metric("📦 Items Sold", f"{df['q'].sum():,}")
        kpi3.metric("🏭 Produced", f"{df['p'].sum():,}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sales by Product")
            st.bar_chart(df.groupby("i")["r"].sum())
        with col2:
            st.subheader("Sales by Site")
            st.bar_chart(df.groupby("s")["r"].sum())

        st.subheader("Stock Alert")
        stock = df.groupby("i")[["p", "q"]].sum()
        stock["Balance"] = stock["p"] - stock["q"]
        def color(v):
            return ["background: #ffcccc" if x < 100 else "" for x in v]
        st.dataframe(stock.style.apply(color, axis=1), use_container_width=True)
    else:
        st.info("Go to Daily Entries tab and add some data")
