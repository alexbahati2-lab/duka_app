import sqlite3
import streamlit as st
from datetime import date, datetime
import pandas as pd

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
        sql_filter = "DATE(sale_date) = ?"
        param = query_date

    elif filter_type == "monthly":
        query_date = selected_date.strftime("%Y-%m")
        sql_filter = "strftime('%Y-%m', sale_date) = ?"
        param = query_date

    else:
        conn.close()
        return []

    c.execute(f"""
        SELECT product_name, quantity, price, total, attendant, sale_date
        FROM sales
        WHERE {sql_filter}
        ORDER BY sale_date ASC
    """, (param,))

    rows = c.fetchall()
    conn.close()
    return rows


def get_summary(filter_type, selected_date):
    conn = get_connection()
    c = conn.cursor()

    if filter_type == "daily":
        query_date = selected_date.strftime("%Y-%m-%d")
        sql_filter = "DATE(sale_date) = ?"
        param = query_date

    elif filter_type == "monthly":
        query_date = selected_date.strftime("%Y-%m")
        sql_filter = "strftime('%Y-%m', sale_date) = ?"
        param = query_date

    else:
        conn.close()
        return (0, 0, 0)

    c.execute(f"""
        SELECT COUNT(*), IFNULL(SUM(quantity),0), IFNULL(SUM(total),0)
        FROM sales
        WHERE {sql_filter}
    """, (param,))

    summary = c.fetchone()
    conn.close()
    return summary


def get_sales_by_attendant(filter_type, selected_date):
    conn = get_connection()
    c = conn.cursor()

    if filter_type == "daily":
        query_date = selected_date.strftime("%Y-%m-%d")
        sql_filter = "DATE(sale_date) = ?"
        param = query_date

    else:
        query_date = selected_date.strftime("%Y-%m")
        sql_filter = "strftime('%Y-%m', sale_date) = ?"
        param = query_date

    c.execute(f"""
        SELECT attendant, COUNT(*), SUM(total)
        FROM sales
        WHERE {sql_filter}
        GROUP BY attendant
        ORDER BY SUM(total) DESC
    """, (param,))

    rows = c.fetchall()
    conn.close()
    return rows


# ---------------------------
# Streamlit UI
# ---------------------------
def reports_ui():
    st.markdown(
        "<h1 style='text-align:center;color:#2196F3;'>📊 Sales Reports</h1>",
        unsafe_allow_html=True
    )

    # --- Quick Today Summary ---
    today = date.today()
    today_count, today_qty, today_total = get_summary("daily", today)

    col1, col2, col3 = st.columns(3)
    col1.metric("📆 Today Transactions", today_count)
    col2.metric("📦 Items Sold Today", today_qty)
    col3.metric("💰 Today Sales (KSh)", today_total)

    st.markdown("---")

    report_type = st.radio("Report type", ["Daily", "Monthly"])

    if report_type == "Daily":
        selected_date = st.date_input("Select date", value=today)
        filter_type = "daily"
    else:
        selected_date = st.date_input("Select month", value=today)
        filter_type = "monthly"

    sales = get_sales(filter_type, selected_date)
    summary = get_summary(filter_type, selected_date)

    st.markdown("---")

    if not sales:
        st.info("No sales recorded for this selection")
        return

    # ---------------------------
    # Sales List
    # ---------------------------
    st.subheader("🧾 Sales List")

    df = pd.DataFrame(
        sales,
        columns=["Product", "Qty", "Price", "Total", "Attendant", "Sale Date"]
    )

    st.dataframe(df, use_container_width=True)

    # ---------------------------
    # Summary
    # ---------------------------
    count, total_qty, total_amount = summary

    st.subheader("📌 Summary")
    col1, col2, col3 = st.columns(3)
    col1.success(f"🛒 Transactions: {count}")
    col2.success(f"📦 Items Sold: {total_qty}")
    col3.success(f"💰 Total Sales: KSh {total_amount}")

    # ---------------------------
    # Sales by Attendant
    # ---------------------------
    st.markdown("---")
    st.subheader("👤 Sales by Attendant")

    attendants = get_sales_by_attendant(filter_type, selected_date)

    if attendants:
        att_df = pd.DataFrame(
            attendants,
            columns=["Attendant", "Transactions", "Total Sales"]
        )
        st.dataframe(att_df, use_container_width=True)
    else:
        st.info("No attendant data available")

    # ---------------------------
    # Export
    # ---------------------------
    st.markdown("---")
    st.subheader("📤 Export Report")

    csv = df.to_csv(index=False).encode("utf-8")
    filename = f"sales_report_{filter_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )
