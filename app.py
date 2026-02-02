import streamlit as st
from modules.products import product_ui
from modules.sales import sales_ui
from modules.reports import reports_ui
from database.tables import init_db

from utils.visitor_db import init_visitor_db
from utils.whatsapp_notifier import notify


# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(
    page_title="Duka App",
    page_icon="🧦",
    layout="wide"
)


# ---------------------------
# Initialize DBs
# ---------------------------
init_db()
init_visitor_db()


# =====================================================
# 🔐 SIMPLE DEMO LOGIN
# =====================================================

def login_screen():
    st.title("🔐 Duka App Login")

    with st.form("login_form"):
        name = st.text_input("Your Name")
        password = st.text_input("Password", type="password")
        st.caption("Demo password: 1234")  # 👈 hint
        submitted = st.form_submit_button("Enter App")

    if submitted:
        # demo password (change if you want)
        if password == "1234" and name.strip():
            st.session_state.logged_in = True
            st.session_state.username = name

            # 🔔 SEND WHATSAPP NOTIFICATION HERE
            notify(name, "Logged into Duka App")

            st.success("Welcome!")
            st.rerun()
        else:
            st.error("Invalid password")


# ---------------------------
# Auth gate
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()   # stops rest of app until login


# =====================================================
# MAIN SYSTEM (only after login)
# =====================================================

st.sidebar.title("🧦 Duka App")
st.sidebar.write(f"👤 {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()


page = st.sidebar.radio(
    "Navigate",
    ["Products", "Sales", "Reports"]
)


# ---------------------------
# Page routing
# ---------------------------
if page == "Products":
    product_ui()

elif page == "Sales":
    sales_ui()

elif page == "Reports":
    reports_ui()
