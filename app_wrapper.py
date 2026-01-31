import webview
import threading
import subprocess
import sys
import os
import time

# Path to your Streamlit app
streamlit_app = os.path.join(os.path.dirname(__file__), "app.py")

def run_streamlit():
    """Run Streamlit in the background"""
    subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app, "--server.port", "8501"])

# Start Streamlit in a background thread
threading.Thread(target=run_streamlit, daemon=True).start()

# Give the server a few seconds to start
time.sleep(2)

# Open a desktop window pointing to the local Streamlit server
webview.create_window("Duka App 🧦", "http://127.0.0.1:8501", width=900, height=700)
webview.start()

