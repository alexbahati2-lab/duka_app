import streamlit as st
from modules.products import product_ui
from modules.sales import sales_ui
from modules.reports import reports_ui
from database.tables import init_db

from utils.visitor_db import init_visitor_db, save_visitor, get_recent_visitors
from utils.whatsapp_notifier import notify

import webbrowser
import threading

def open_browser():
    webbrowser.open_new("http://localhost:8501")

threading.Timer(1, open_browser).start()


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
    ["Products", "Sales", "Reports", "Visitors"]
)

# ---------------------------
# Page routing
# ---------------------------
init_db()
init_visitor_db()

if page == "Products":
    product_ui()
elif page == "Sales":
    sales_ui()
elif page == "Reports":
    reports_ui()
elif page == "Visitors":
    st.header("Demo Visitors")

    with st.form("visitor_form"):
        name = st.text_input("Name")
        contact = st.text_input("Contact (phone or email)")
        send_whatsapp = st.checkbox("Send WhatsApp notification", value=False)
        submitted = st.form_submit_button("Save Visitor")

    if submitted:
        try:
            rowid = save_visitor(name, contact)
            st.success(f"Saved visitor #{rowid}")
            if send_whatsapp:
                try:
                    ok = notify(name, contact)
                except Exception as e:
                    ok = False
                    st.error(f"Notifier error: {e}")
                if ok:
                    st.success("WhatsApp notification sent")
                else:
                    st.error("WhatsApp notification failed")
        except Exception as e:
            st.error(str(e))

    st.subheader("Recent visitors")
    visitors = get_recent_visitors(20)
    if visitors:
        st.table(visitors)
    else:
        st.write("No visitors yet.")
