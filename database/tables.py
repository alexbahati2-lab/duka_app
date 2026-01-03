import os
import re
import sqlite3
from barcode import Code128
from barcode.writer import ImageWriter
from datetime import datetime

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stock.db")
BARCODE_FOLDER = os.path.join(BASE_DIR, "barcodes")
os.makedirs(BARCODE_FOLDER, exist_ok=True)

# ---------------------------
# Connection & Table Init
# ---------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


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
        sale_date TEXT,
        attendant TEXT,
        receipt_no TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# Product Functions
# ---------------------------
def barcode_exists(barcode):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM products WHERE barcode = ?", (barcode,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def generate_barcode_number():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM products")
    max_id = c.fetchone()[0]
    conn.close()
    return str((max_id or 0) + 1001)


def add_product(name, category, price, quantity, barcode):
    conn = get_connection()
    c = conn.cursor()

    # Check if product with barcode already exists
    c.execute(
        "SELECT id, quantity FROM products WHERE barcode = ?",
        (barcode,)
    )
    existing = c.fetchone()

    barcode_path = os.path.join(BARCODE_FOLDER, f"{barcode}.png")

    if existing:
        # Product exists → UPDATE stock
        product_id, old_qty = existing
        new_qty = old_qty + quantity

        c.execute("""
            UPDATE products
            SET name = ?, category = ?, price = ?, quantity = ?
            WHERE barcode = ?
        """, (name, category, price, new_qty, barcode))

    else:
        # New product → INSERT
        c.execute("""
            INSERT INTO products (name, category, price, quantity, barcode)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, quantity, barcode))

        # Generate barcode image only for new products
        with open(barcode_path, "wb") as f:
            Code128(barcode, writer=ImageWriter()).write(f)

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


def search_products_by_name(query):
    """Return a list of matching products by name"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, price, quantity
        FROM products
        WHERE name LIKE ?
        ORDER BY name ASC
    """, (f"%{query}%",))
    results = c.fetchall()
    conn.close()
    return results


def update_stock(product_id, new_quantity):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


# ---------------------------
# Sales Functions
# ---------------------------
def record_sale(product_id, product_name, qty, price, attendant):
    conn = get_connection()
    c = conn.cursor()

    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = qty * price
    receipt_no = f"RCT-{int(datetime.now().timestamp())}"

    c.execute("""
        INSERT INTO sales (
            product_id,
            product_name,
            quantity,
            price,
            total,
            sale_date,
            attendant,
            receipt_no
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        product_name,
        qty,
        price,
        total,
        sale_date,
        attendant,  
        receipt_no
    ))

    conn.commit()
    conn.close()
