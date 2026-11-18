"""
streamlit_app.py - Root entrypoint for Streamlit Community Cloud deployment.
Prepares the environment and launches the SupeRR Selector Round 1 dashboard.
"""
import sys
from pathlib import Path

# Add repository root and dashboard directory to sys.path so all imports resolve
ROOT_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = ROOT_DIR / "dashboard"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

# Read and execute dashboard/app.py in this script runner context on every rerun
app_path = DASHBOARD_DIR / "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_code = compile(f.read(), str(app_path), "exec")

exec(app_code, globals())
