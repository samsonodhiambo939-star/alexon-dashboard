import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, timedelta
from pathlib import Path
import base64

st.set_page_config(page_title="Alexon Group M&E", layout="centered")

# ── Logo (inline base64) ────────────────────────────────────
logo_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAYGBgYHBgcICAcKCwoLCg8ODAwODxYQERAREBYiFRkVFRkVIh4kHhweJB42KiYmKjY+NDI0PkxERExfWl98fKcBBgYGBgcGBwgIBwoLCgsKDw4MDA4PFhAREBEQFiIVGRUVGRUiHiQeHB4kHjYqJiYqNj40MjQ+TERETF9aX3x8pP/CABEIA8AD6AMBIgACEQEDEQH/xAAZAAEBAQEBAQAAAAAAAAAAAAAAAQIDBAX/xAAYAQEBAQEBAAAAAAAAAAAAAAAAAQIDBP/aAAwDAQACEAMQAAAB+V9AAAAAAAAAAAAAAAM5AAAAAAAzQAADNAAAAAAAADNAAAAAAAAM0AAAAAAAM0AAAAAAAM0AAAAAAAzQAAAAAAAzQAAAAAADNAAAAAAAAzQAAAAAADNAAAAAAAAzQAAAAAADNAAAAAAAAzQAAAAAADNAAAAAAAAzQAAAAAADNAAAAAAAAzQAAAAAADNAAAAAAAAzQAAAAAAAAAAAAA//EABQRAQAAAAAAAAAAAAAAAAAAAJD/2gAIAQIQAAAAAoAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAAAACQ/9oACAECEAAAAH//xAAC/9sACwABAAMBAQEBAAAAAAAAAQAQMTBBUWFxgZGhscHR/9oACAEBAAE/EDDZz7zfbOy9XnavPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeOXnarPF3+eueAceWeBHLzgcnOjvbSndc4nLzgeP/xAAiEQEBAQACAwACAwEAAAAAAAAAAREQMSBQIGFxUEGQobH/2gAIAQIBAT8Q/wD/2gAIAQMBAT8Q/wD/2Q=="

st.markdown(f"""
    <div style="text-align:center;padding:15px 0 5px">
        <div style="
            width:100px;height:100px;border-radius:50%;
            overflow:hidden;margin:0 auto;
            border:3px solid #2d6a4f;box-shadow:0 2px 10px rgba(0,0,0,0.15);
            display:flex;align-items:center;justify-content:center;
            background:#fff;
        ">
            <img src="{logo_b64}" style="width:100%;height:100%;object-fit:cover">
        </div>
        <div style="
            font-size:28px;font-weight:800;color:#1a3a5c;
            letter-spacing:4px;margin-top:6px;text-transform:uppercase;
        ">ALEXON</div>
        <div style="font-size:13px;color:#666;letter-spacing:2px">Group</div>
    </div>
""", unsafe_allow_html=True)

st.title("🏗️ M&E Dashboard")

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

PERFORMANCE_ORDER = ["Top Performer", "Good", "Average", "Low", "Very Low"]

# ── Helpers ─────────────────────────────────────────────────
def add(d, s, i, p, q):
    r = q * PRICES[i]
    c = conn()
    c.execute("INSERT INTO e(d,s,i,p,q,r) VALUES(?,?,?,?,?,?)", (d.isoformat(), s, i, p, q, r))
    c.commit(); c.close()
    return r

def load():
    return pd.read_sql_query("SELECT rowid as id,* FROM e ORDER BY d DESC", conn())

def performance_color(val, reverse=False):
    """Color bands: green -> yellow -> orange -> red"""
    if reverse:
        if val >= 80: return "#1a7a2e"
        if val >= 50: return "#2d8f1a"
        if val >= 30: return "#b8860b"
        if val >= 15: return "#cc5500"
        return "#cc0000"
    else:
        if val >= 80: return "#1a7a2e"
        if val >= 50: return "#2d8f1a"
        if val >= 30: return "#b8860b"
        if val >= 15: return "#cc5500"
        return "#cc0000"

def style_performance_row(row, max_val, col, reverse=False):
    pct = (row[col] / max_val * 100) if max_val > 0 else 0
    bg = performance_color(pct, reverse)
    return [f"background: {bg}; color: white; font-weight: bold" if c == col else "" for c in row.index]

# ── Tabs ─────────────────────────────────────────────────────
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

        # ── Sales by Product (color ranked) ──
        st.subheader("📈 Sales by Product — Performance Ranking")
        prod_sales = df.groupby("i")["q"].sum().reset_index().sort_values("q", ascending=False)
        prod_sales.columns = ["Product", "Qty Sold"]
        max_q = prod_sales["Qty Sold"].max()
        styled_prod = prod_sales.style.apply(
            lambda row: style_performance_row(row, max_q, "Qty Sold"), axis=1
        )
        st.dataframe(styled_prod, use_container_width=True, hide_index=True)

        # Bar chart
        st.bar_chart(df.groupby("i")["r"].sum())

        # ── Sales by Site (color ranked) ──
        st.subheader("📈 Sales by Site — Performance Ranking")
        site_sales = df.groupby("s")["q"].sum().reset_index().sort_values("q", ascending=False)
        site_sales.columns = ["Site", "Qty Sold"]
        max_site = site_sales["Qty Sold"].max() if not site_sales.empty else 1
        styled_site = site_sales.style.apply(
            lambda row: style_performance_row(row, max_site, "Qty Sold"), axis=1
        )
        st.dataframe(styled_site, use_container_width=True, hide_index=True)

        st.bar_chart(df.groupby("s")["r"].sum())

        # ── Time-based: Daily / Weekly / Monthly ──
        st.subheader("📅 Time-Based Performance")
        time_col, time_range = st.columns([1, 2])
        period = time_col.radio("Period", ["Daily", "Weekly", "Monthly"], horizontal=True, label_visibility="collapsed")

        df_time = df.copy()
        df_time["d"] = pd.to_datetime(df_time["d"])

        if period == "Daily":
            perf = df_time.groupby("d")["q"].sum().reset_index()
            perf.columns = ["Date", "Qty Sold"]
        elif period == "Weekly":
            df_time["week"] = df_time["d"].dt.isocalendar().week.astype(str) + "-" + df_time["d"].dt.year.astype(str)
            perf = df_time.groupby("week")["q"].sum().reset_index()
            perf.columns = ["Week", "Qty Sold"]
        else:
            df_time["month"] = df_time["d"].dt.month_name() + " " + df_time["d"].dt.year.astype(str)
            perf = df_time.groupby("month")["q"].sum().reset_index()
            perf.columns = ["Month", "Qty Sold"]

        max_t = perf["Qty Sold"].max() if not perf.empty else 1
        styled_time = perf.style.apply(
            lambda row: style_performance_row(row, max_t, "Qty Sold"), axis=1
        )
        st.dataframe(styled_time, use_container_width=True, hide_index=True)

        st.caption("🟢 Green = Top Performer  🟡 Yellow/Orange = Average  🔴 Red = Low / Very Low")

        # ── Stock Alert ──
        st.subheader("Stock Alert")
        stock = df.groupby("i")[["p", "q"]].sum()
        stock["Balance"] = stock["p"] - stock["q"]
        def color(v):
            return ["background: #ffcccc" if x < 100 else "background: #ccffcc" for x in v]
        st.dataframe(stock.style.apply(color, axis=1), use_container_width=True)
    else:
        st.info("Go to Daily Entries tab and add some data")
