"""
SubroRecover AI - Round 6 Verification Screenshot Capture Script
Captures full scroll captures of the Overview page in both Dark and Light themes at 1440px and 390px viewports.
Saves to docs/screenshots/round6/
"""

import os
import sys
import time
import subprocess
import urllib.request

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots", "round6"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIEWPORTS = [
    ("1440", 1440, 1750),
    ("390", 390, 2900),
]

THEMES = ["dark", "light"]

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

def capture_screenshot(url, output_path, width, height):
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
        return True
    else:
        print(f"FAILED to capture: {output_path}")
        return False

def main():
    print("Starting FastAPI server for Round 6 screenshots...")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        if not wait_for_server():
            print("Server failed to respond in time.")
            return

        time.sleep(3) # Allow React SPA bundle & TanStack Query to settle
        total_captured = 0

        print(f"\n--- Capturing Round 6 Full Overview (Scroll Capture) to {OUTPUT_DIR} ---")
        for v_name, w, h in VIEWPORTS:
            for theme in THEMES:
                url = f"http://127.0.0.1:8000/?theme={theme}"
                filename = f"overview-{v_name}-{theme}.png"
                out_path = os.path.join(OUTPUT_DIR, filename)
                if capture_screenshot(url, out_path, w, h):
                    total_captured += 1

        print(f"\n>>> Done! Successfully captured {total_captured} screenshots in {OUTPUT_DIR}!")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
