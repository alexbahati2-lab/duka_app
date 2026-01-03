import streamlit as st
from modules.products import product_ui
from modules.sales import sales_ui
from modules.reports import reports_ui
from database.tables import init_db


# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(
    page_title="Duka App",
    page_icon="🧦",
    layout="wide"
)

# ---------------------------
# Sidebar navigation
# ---------------------------
st.sidebar.title("🧦 Duka App")

page = st.sidebar.radio(
    "Navigate",
    ["Products", "Sales", "Reports"]
)

# ---------------------------
# Page routing
# ---------------------------
init_db()

if page == "Products":
    product_ui()
elif page == "Sales":
    sales_ui()
elif page == "Reports":
    reports_ui()
