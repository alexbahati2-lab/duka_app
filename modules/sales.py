import sqlite3
import streamlit as st
from datetime import datetime

DB_PATH = "database/stock.db"

# ---------------------------
# Database helpers
# ---------------------------
def get_connection():
    """Return SQLite connection"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_product_by_barcode(barcode):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, price, quantity
        FROM products
        WHERE barcode = ?
    """, (barcode,))
    product = c.fetchone()
    conn.close()
    return product

def update_stock(product_id, new_quantity):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )
    conn.commit()
    conn.close()

def record_sale(product_id, name, qty, price, attendant):
    """Record sale with attendant"""
    conn = get_connection()
    c = conn.cursor()
    total = qty * price
    sale_date = datetime.now().strftime("%Y-%m-%d")

    c.execute("""
        INSERT INTO sales (
            product_id, product_name, quantity, price, total, sale_date, attendant
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (product_id, name, qty, price, total, sale_date, attendant))

    conn.commit()
    conn.close()

# ---------------------------
# Sales UI
# ---------------------------
def sales_ui():
    st.markdown(
        "<h1 style='text-align:center;color:#FF9800;'>🧾 Sales</h1>",
        unsafe_allow_html=True
    )

    st.subheader("🔍 Scan or Enter Barcode")

    # Attendant input
    attendant = st.text_input("Attendant Name", placeholder="Type your name here")
    if not attendant:
        st.warning("⚠️ Please enter attendant name before selling")
        return

    barcode = st.text_input(
        "Scan barcode or type manually",
        placeholder="Click here then scan barcode"
    )

    if not barcode:
        st.info("Waiting for barcode scan…")
        return

    product = get_product_by_barcode(barcode.strip())
    if not product:
        st.error("❌ Product not found")
        return

    product_id, name, price, stock = product

    st.success("✅ Product loaded")
    st.write(f"**Product:** {name}")
    st.write(f"**Price:** KSh {price}")
    st.write(f"**Stock Available:** {stock}")

    qty_sold = st.number_input(
        "Quantity to sell",
        min_value=1,
        max_value=stock,
        step=1
    )

    total = qty_sold * price
    st.info(f"💰 Total: KSh {total}")

    # Complete Sale button
    if st.button("✅ Complete Sale", use_container_width=True):
        if qty_sold > stock:
            st.error("❌ Not enough stock")
            return

        # Update stock
        new_stock = stock - qty_sold
        update_stock(product_id, new_stock)

        # Record sale with attendant
        record_sale(product_id, name, qty_sold, price, attendant)

        st.success(f"🎉 Sale completed successfully by {attendant}")
        st.write(f"Remaining stock: {new_stock}")

        # Reset for next scan
        st.experimental_rerun()
