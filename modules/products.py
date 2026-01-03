import os
import re
import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter

from database.tables import (
    init_db,
    barcode_exists,
    generate_barcode_number,
    add_product,
    get_products,
    delete_product
)

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BARCODE_FOLDER = os.path.join(BASE_DIR, "barcodes")
os.makedirs(BARCODE_FOLDER, exist_ok=True)

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

    # initialize DB tables if not exists
    init_db()

    # -------- Add Product --------
    with st.expander("➕ Add New Product", expanded=True):
        # initialize session_state defaults if they don't exist
        if "name" not in st.session_state:
            st.session_state.name = ""
        if "category" not in st.session_state:
            st.session_state.category = ""
        if "price" not in st.session_state:
            st.session_state.price = 0.0
        if "quantity" not in st.session_state:
            st.session_state.quantity = 0
        if "barcode" not in st.session_state:
            st.session_state.barcode = generate_barcode_number()

        with st.form("add_product_form"):
            name = st.text_input("Product Name", key="name")
            category = st.text_input("Category", key="category")
            price = st.number_input("Price (KSh)", min_value=0.0, format="%.2f", key="price")
            quantity = st.number_input("Quantity", min_value=0, step=1, key="quantity")
            barcode = st.text_input(
                "Barcode (editable)",
                key="barcode",
                help="Must be unique and alphanumeric"
            )

            submitted = st.form_submit_button("➕ Add Product")

            if submitted:
                barcode = barcode.strip()
                if not name.strip():
                    st.error("❌ Product name is required")
                elif not re.match("^[A-Za-z0-9-]+$", barcode):
                    st.error("❌ Barcode can only contain letters, numbers, and dashes")
                elif barcode_exists(barcode):
                    st.error("❌ Barcode already exists")
                else:
                    # generate barcode image
                    barcode_path = os.path.join(BARCODE_FOLDER, f"{barcode}.png")
                    with open(barcode_path, "wb") as f:
                        Code128(barcode, writer=ImageWriter()).write(f)

                    # add product to DB
                    add_product(name, category, price, quantity, barcode)
                    st.success(f"✅ {name} added successfully")
                    st.image(barcode_path, width=220)

                    # ✅ safe way to clear the form: rerun script
                    st.rerun()

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
            st.rerun()  # refresh product list after delete

# ---------------------------
# Run UI
# ---------------------------
if __name__ == "__main__":
    product_ui()
