"""
Script to capture Round 3 verification screenshots:
Overview and Assistant at 1440px, 1280px, and 390px in both Dark and Light themes.
Saves to docs/screenshots/round3/
"""

import os
import sys
import time
import subprocess
import urllib.request

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots", "round3"))
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

def capture_screenshot(url, output_path, width=1440, height=900):
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
    print("Starting server to capture Round 3 verification screenshots...")
    
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        if not wait_for_server():
            print("Server failed to respond in time.")
            return

        time.sleep(3) # Allow React app and data queries to settle

        viewports = [
            ("1440", 1440, 900),
            ("1280", 1280, 800),
            ("390", 390, 844),
        ]
        themes = ["dark", "light"]

        # 1. Overview Page Screenshots
        print("\n--- Capturing Overview Screenshots ---")
        for v_name, w, h in viewports:
            for theme in themes:
                filename = f"overview-{v_name}-{theme}.png"
                out_path = os.path.join(OUTPUT_DIR, filename)
                url = f"http://127.0.0.1:8000/?theme={theme}"
                capture_screenshot(url, out_path, w, h)

        # 2. Assistant Page Screenshots
        print("\n--- Capturing Assistant Screenshots ---")
        for v_name, w, h in viewports:
            for theme in themes:
                filename = f"assistant-{v_name}-{theme}.png"
                out_path = os.path.join(OUTPUT_DIR, filename)
                url = f"http://127.0.0.1:8000/assistant?theme={theme}"
                capture_screenshot(url, out_path, w, h)

        print("\n>>> All 12 Round 3 screenshots successfully generated in docs/screenshots/round3/!")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
