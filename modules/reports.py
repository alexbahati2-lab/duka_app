import sqlite3
import streamlit as st
from datetime import date

DB_PATH = "database/stock.db"

# ---------------------------
# Database helpers
# ---------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_sales(filter_type, selected_date):
    """
    Fetch sales from the database.
    filter_type: "daily" or "monthly"
    selected_date: datetime.date object
    """
    conn = get_connection()
    c = conn.cursor()

    if filter_type == "daily":
        query_date = selected_date.strftime("%Y-%m-%d")
        sql_filter = "sale_date = ?"
    elif filter_type == "monthly":
        query_date = selected_date.strftime("%Y-%m")
        sql_filter = "strftime('%Y-%m', sale_date) = ?"
    else:
        conn.close()
        return []

    c.execute(f"""
        SELECT product_name, quantity, price, total, sale_date
        FROM sales
        WHERE {sql_filter}
        ORDER BY sale_date ASC
    """, (query_date,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_summary(filter_type, selected_date):
    conn = get_connection()
    c = conn.cursor()

    if filter_type == "daily":
        query_date = selected_date.strftime("%Y-%m-%d")
        sql_filter = "sale_date = ?"
    elif filter_type == "monthly":
        query_date = selected_date.strftime("%Y-%m")
        sql_filter = "strftime('%Y-%m', sale_date) = ?"
    else:
        conn.close()
        return (0, 0, 0)

    c.execute(f"""
        SELECT COUNT(*), SUM(quantity), SUM(total)
        FROM sales
        WHERE {sql_filter}
    """, (query_date,))
    summary = c.fetchone()
    conn.close()
    return summary

# ---------------------------
# Streamlit UI
# ---------------------------
def reports_ui():
    st.markdown(
        "<h1 style='text-align:center;color:#2196F3;'>📊 Sales Reports</h1>",
        unsafe_allow_html=True
    )

    report_type = st.radio("Report type", ["Daily", "Monthly"])

    if report_type == "Daily":
        selected_date = st.date_input("Select date", value=date.today())
        filter_type = "daily"
    else:
        selected_date = st.date_input("Select month", value=date.today())
        filter_type = "monthly"

    sales = get_sales(filter_type, selected_date)
    summary = get_summary(filter_type, selected_date)

    st.markdown("---")

    if not sales:
        st.info("No sales recorded for this selection")
        return

    st.subheader("🧾 Sales List")

    for product_name, qty, price, total, sale_date in sales:
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])
        col1.write(product_name)
        col2.write(qty)
        col3.write(f"KSh {price}")
        col4.write(f"KSh {total}")
        col5.write(sale_date)

    st.markdown("---")

    count, total_qty, total_amount = summary
    st.subheader("📌 Summary")
    st.success(f"🛒 Transactions: {count}")
    st.success(f"📦 Items Sold: {total_qty}")
    st.success(f"💰 Total Sales: KSh {total_amount}")
