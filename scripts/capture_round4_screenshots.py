"""
SubroRecover AI - Round 4 Verification Screenshot Capture Script
Captures full Overview page screenshots at 1440px and 1280px in both Dark and Light themes.
Saves to docs/screenshots/round4/
"""

import os
import sys
import time
import subprocess
import urllib.request

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots", "round4"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def wait_for_server(url="http://127.0.0.1:8000/api/health", timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as res:
                if res.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def capture_screenshot(url, output_path, width=1440, height=1600):
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--window-size={width},{height}",
        "--virtual-time-budget=6000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={output_path}",
        url
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024
        print(f"Captured: {os.path.basename(output_path)} ({width}x{height}) - {size_kb:.1f} KB")
    else:
        print(f"FAILED to capture: {output_path}")

def main():
    print("Starting FastAPI server to capture Round 4 verification screenshots...")
    
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        if not wait_for_server():
            print("Server failed to respond in time.")
            return

        time.sleep(3) # Allow React SPA bundle and initial TanStack queries to settle

        viewports = [
            ("1440", 1440, 1650),
            ("1280", 1280, 1750),
        ]
        themes = ["dark", "light"]

        print("\n--- Capturing Round 4 Overview Full Page Screenshots ---")
        for v_name, w, h in viewports:
            for theme in themes:
                filename = f"overview-{v_name}-{theme}.png"
                out_path = os.path.join(OUTPUT_DIR, filename)
                url = f"http://127.0.0.1:8000/?theme={theme}"
                capture_screenshot(url, out_path, w, h)

        print(f"\n>>> All Round 4 screenshots successfully generated in {OUTPUT_DIR}!")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
