import streamlit as st
from datetime import datetime
import urllib.parse
import base64

from database.tables import (
    init_db,
    get_product_by_barcode,
    update_stock,
    record_sale
)
from modules.receipt import generate_receipt


# ---------------------------
# Helpers
# ---------------------------
def play_beep():
    """Play a short beep sound on successful scan."""
    beep_base64 = (
        "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA="
    )
    audio_bytes = base64.b64decode(beep_base64)
    st.audio(audio_bytes, format="audio/wav", autoplay=True)


def reset_cart_and_receipt():
    st.session_state.cart = []
    st.session_state.last_receipt = ""
    st.session_state.ui_refresh = datetime.now()


def remove_from_cart(idx):
    st.session_state.cart.pop(idx)
    st.session_state.ui_refresh = datetime.now()


# ---------------------------
# Sales UI
# ---------------------------
def sales_ui():
    st.set_page_config(
        page_title="Duka App - Sales",
        page_icon="🧾",
        layout="wide"
    )

    st.markdown(
        "<h1 style='text-align:center;color:#FF9800;'>🧾 Sales</h1>",
        unsafe_allow_html=True
    )

    # Initialize DB
    init_db()

    # ---------------------------
    # Session defaults
    # ---------------------------
    if "cart" not in st.session_state:
        st.session_state.cart = []

    if "last_receipt" not in st.session_state:
        st.session_state.last_receipt = ""

    if "attendant" not in st.session_state:
        st.session_state.attendant = ""

    # ---------------------------
    # Attendant input
    # ---------------------------
    st.session_state.attendant = st.text_input(
        "Attendant Name",
        value=st.session_state.attendant,
        placeholder="Type your name here"
    )

    if not st.session_state.attendant.strip():
        st.warning("⚠️ Please enter attendant name before selling")
        return

    # ---------------------------
    # Barcode Scan (HARD LOCK)
    # ---------------------------
    st.subheader("🔍 Scan Product Barcode")

    barcode = st.text_input(
        "Scan barcode",
        placeholder="Scan using barcode scanner",
        key="barcode_input"
    ).strip()

    if not barcode:
        st.info("📷 Waiting for barcode scan...")
        return

    selected_product = get_product_by_barcode(barcode)

    if not selected_product:
        st.error("❌ Invalid barcode. Product not found.")
        return

    product_id, name, price, stock = selected_product

    # Beep on successful scan
    play_beep()

    st.success("✅ Product loaded")
    st.write(f"**Product:** {name}")
    st.write(f"**Price:** KSh {price}")
    st.write(f"**Stock Available:** {stock}")

    # ---------------------------
    # Stock check
    # ---------------------------
    if stock <= 0:
        st.error("⛔ Product is OUT OF STOCK")
        return

    # ---------------------------
    # Quantity & Add to Cart
    # ---------------------------
    qty_sold = st.number_input(
        "Quantity to sell",
        min_value=1,
        max_value=stock,
        step=1
    )

    if st.button("➕ Add to Cart"):
        existing = next(
            (item for item in st.session_state.cart if item["product_id"] == product_id),
            None
        )

        if existing:
            if existing["qty"] + qty_sold > stock:
                st.error("❌ Quantity exceeds available stock")
            else:
                existing["qty"] += qty_sold
                st.success(f"Updated {name} quantity")
        else:
            st.session_state.cart.append({
                "product_id": product_id,
                "name": name,
                "price": price,
                "qty": qty_sold,
                "stock": stock
            })
            st.success(f"Added {qty_sold} x {name} to cart")

        st.session_state.ui_refresh = datetime.now()

    # ---------------------------
    # Cart Display
    # ---------------------------
    if st.session_state.cart:
        st.subheader("🛒 Cart")
        total_amount = 0
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3, col4 = st.columns([4, 1, 2, 1])
            col1.write(item["name"])
            col2.write(item["qty"])
            col3.write(f"KSh {item['price'] * item['qty']}")
            col4.button(
                "❌",
                key=f"remove_{i}",
                on_click=remove_from_cart,
                args=(i,)
            )
            total_amount += item["price"] * item["qty"]
        st.info(f"💰 Total Amount: KSh {total_amount}")

    # ---------------------------
    # Receipt
    # ---------------------------
    if st.button("🧾 Generate Receipt"):
        st.session_state.last_receipt = generate_receipt(
            st.session_state.attendant,
            st.session_state.cart
        )

    if st.session_state.last_receipt:
        st.subheader("🧾 Generated Receipt")
        st.text_area(
            "Receipt",
            st.session_state.last_receipt,
            height=260
        )

        owner_phone = "254726224423"
        encoded = urllib.parse.quote(st.session_state.last_receipt)
        wa_link = f"https://wa.me/{owner_phone}?text={encoded}"
        st.markdown(
            f"[📲 Send Receipt to WhatsApp Owner]({wa_link})",
            unsafe_allow_html=True
        )

    # ---------------------------
    # Complete Sale
    # ---------------------------
    if st.button("♻️ Complete / New Sale"):
        for item in st.session_state.cart:
            new_stock = item["stock"] - item["qty"]
            update_stock(item["product_id"], new_stock)
            record_sale(
                item["product_id"],
                item["name"],
                item["qty"],
                item["price"],
                st.session_state.attendant
            )

        reset_cart_and_receipt()
        st.success("✅ Sale completed successfully")
