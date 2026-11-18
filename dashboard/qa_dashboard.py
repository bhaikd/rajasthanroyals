"""
dashboard/qa_dashboard.py - Automated visual and UI QA runner using Playwright.
Takes high-resolution screenshots of each dashboard page, checks for console errors,
checks viewport responsiveness at 1366px, and saves screenshots to outputs/dashboard_screens/.
"""
import time
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
SCREENS_DIR = OUTPUTS_DIR / "dashboard_screens"
SCREENS_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:8501"

PAGES = [
    ("1. Overview", "page_1_overview.png"),
    ("2. Player Explorer", "page_2_player_explorer.png"),
    ("3. Rankings Explorer", "page_3_rankings_explorer.png"),
    ("4. Evidence & Reliability", "page_4_evidence_reliability.png"),
    ("5. Pressure Explorer", "page_5_pressure_explorer.png"),
    ("6. Excluded Players & Methodology", "page_6_excluded_methodology.png")
]

def run_qa():
    print("[QA] Starting Playwright browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Test at standard laptop resolution: 1366 x 800
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()
        
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        
        print(f"[QA] Navigating to {APP_URL}...")
        try:
            page.goto(APP_URL, wait_until="networkidle", timeout=20000)
        except Exception as e:
            print(f"[ERROR] Failed to load {APP_URL}: {e}")
            browser.close()
            return False
            
        time.sleep(3) # Wait for initial Streamlit render and cache load
        
        for nav_text, img_name in PAGES:
            print(f"[QA] Testing page: '{nav_text}'...")
            # Click sidebar navigation option
            # Streamlit radio labels
            label_locator = page.locator(f'label:has-text("{nav_text}")')
            if label_locator.count() > 0:
                label_locator.first.click()
            else:
                print(f"      Warning: could not find radio with text '{nav_text}'")
                
            time.sleep(2.5) # Wait for charts and animations to render
            
            # Save screenshot
            out_fp = SCREENS_DIR / img_name
            page.screenshot(path=str(out_fp), full_page=True)
            print(f"      Saved screenshot to: {out_fp}")
            
            # Check horizontal overflow on main body
            body_scroll_width = page.evaluate("document.body.scrollWidth")
            body_client_width = page.evaluate("document.body.clientWidth")
            if body_scroll_width > body_client_width + 10:
                print(f"      [ALERT] Potential horizontal scroll detected on {nav_text}: scrollWidth={body_scroll_width}, clientWidth={body_client_width}")
            else:
                print(f"      Responsive check: perfect fit (clientWidth={body_client_width}, scrollWidth={body_scroll_width}).")
                
        browser.close()
        
        print("\n[QA Summary]")
        print(f"Total Screenshots Saved: {len(PAGES)}")
        if console_errors:
            print(f"Console errors encountered: {len(console_errors)}")
            for ce in console_errors[:5]:
                print(f"  - {ce}")
        else:
            print("Console errors encountered: 0 (Clean run!)")
            
    return True

if __name__ == "__main__":
    success = run_qa()
    sys.exit(0 if success else 1)
