import sqlite3
import os
from datetime import datetime
import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter

# ---------------------------

# Database helpers
# ---------------------------
DB_PATH = "database/stock.db"

def get_connection():
    """Return a SQLite connection"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ---------------------------
# Barcode helpers
# ---------------------------
BARCODE_FOLDER = "assets/barcodes"
os.makedirs(BARCODE_FOLDER, exist_ok=True)

def generate_barcode(number):
    """
    Generate barcode image and return file path
    """
    filepath = os.path.join(BARCODE_FOLDER, f"{number}.png")
    Code128(number, writer=ImageWriter()).write(open(filepath, "wb"))
    return filepath

# ---------------------------
# Formatting helpers
# ---------------------------
def format_currency(amount):
    """Format number as KSh currency"""
    return f"KSh {amount:,.2f}"

def format_date(dt):
    """Format datetime/date object as YYYY-MM-DD"""
    return dt.strftime("%Y-%m-%d")

# ---------------------------
# Streamlit UI helpers
# ---------------------------
def show_success(msg):
    st.success(f"✅ {msg}")

def show_error(msg):
    st.error(f"❌ {msg}")

def show_info(msg):
    st.info(f"ℹ️ {msg}")
