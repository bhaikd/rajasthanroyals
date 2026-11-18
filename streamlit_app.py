"""
streamlit_app.py - Root entrypoint for Streamlit Community Cloud deployment.
Prepares the environment and launches the SupeRR Selector Round 1 dashboard.
"""
import sys
from pathlib import Path

# Add dashboard folder to sys.path so internal imports resolve cleanly
BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = BASE_DIR / "dashboard"

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

# Launch main dashboard application
import app
