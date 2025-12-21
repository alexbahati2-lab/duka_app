import os
import sqlite3
import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter

# ---------------------------
# Paths & Setup
# ---------------------------
DB_PATH = "database/stock.db"
def get_product_by_barcode(barcode):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT name, category, price, quantity
        FROM products
        WHERE barcode = ?
    """, (barcode,))
    product = c.fetchone()
    conn.close()
    return product

BARCODE_FOLDER = "assets/barcodes"

os.makedirs("database", exist_ok=True)
os.makedirs(BARCODE_FOLDER, exist_ok=True)

# ---------------------------
# Database Functions
# ---------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            barcode TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def generate_barcode_number():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM products")
    max_id = c.fetchone()[0]
    conn.close()
    return str((max_id or 0) + 1001)

def add_product(name, category, price, quantity):
    barcode_number = generate_barcode_number()
    barcode_path = os.path.join(BARCODE_FOLDER, f"{barcode_number}.png")

    # Generate barcode image
    with open(barcode_path, "wb") as f:
        Code128(barcode_number, writer=ImageWriter()).write(f)

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO products (name, category, price, quantity, barcode)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, price, quantity, barcode_number))
    conn.commit()
    conn.close()

    return barcode_path

def get_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, category, price, quantity, barcode FROM products")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_product(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Streamlit UI
# ---------------------------
def product_ui():
    st.set_page_config(
        page_title="Duka App",
        page_icon="🧦",
        layout="wide"
    )

    st.markdown(
        "<h1 style='text-align:center;color:#4CAF50;'>🛍️ Product Management</h1>",
        unsafe_allow_html=True
    )

    init_db()

    # -------- Add Product --------
    with st.expander("➕ Add New Product", expanded=True):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        price = st.number_input("Price (KSh)", min_value=0.0, format="%.2f")
        quantity = st.number_input("Quantity", min_value=0, step=1)

        if st.button("Add Product", use_container_width=True):
            if name.strip() and price >= 0 and quantity >= 0:
                barcode_file = add_product(name, category, price, quantity)
                st.success(f"✅ {name} added successfully")
                st.image(barcode_file, caption="Generated Barcode", width=220)
                st.experimental_rerun()
            else:
                st.error("❌ Please fill all fields correctly")

    st.markdown("---")

    # -------- Product List --------
    st.subheader("📦 Current Products")

    products = get_products()

    if not products:
        st.info("No products added yet")
        return

    for pid, name, category, price, qty, barcode in products:
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 2, 1])

        col1.write(name)
        col2.write(category or "-")
        col3.write(f"KSh {price}")
        col4.write(qty)

        barcode_path = os.path.join(BARCODE_FOLDER, f"{barcode}.png")
        if os.path.exists(barcode_path):
            col5.image(barcode_path, width=100)

        if col6.button("🗑 Delete", key=f"del_{pid}"):
            delete_product(pid)
            st.experimental_rerun()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Products table
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            barcode TEXT UNIQUE NOT NULL
        )
    """)

    # Sales table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            total REAL,
            sale_date TEXT
        )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    product_ui()
