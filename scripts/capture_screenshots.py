"""
Script to capture before/after screenshots at 1440px and 390px in both themes.
"""

import os
import sys
import time
import subprocess
import urllib.request

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))

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
        f"--screenshot={output_path}",
        url
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)

def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "before"
    print(f"Starting server to capture {prefix} screenshots...")
    
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        if not wait_for_server():
            print("Server failed to respond in time.")
            return

        time.sleep(2) # Allow React app and data queries to settle

        # 1. 1440px Dark
        p_1440_dark = os.path.join(OUTPUT_DIR, f"overview-{prefix}-1440-dark.png")
        print(f"Capturing {p_1440_dark}...")
        capture_screenshot("http://127.0.0.1:8000?theme=dark", p_1440_dark, 1440, 900)

        # 2. 1440px Light
        p_1440_light = os.path.join(OUTPUT_DIR, f"overview-{prefix}-1440-light.png")
        print(f"Capturing {p_1440_light}...")
        capture_screenshot("http://127.0.0.1:8000?theme=light", p_1440_light, 1440, 900)

        # 3. 390px Dark
        p_390_dark = os.path.join(OUTPUT_DIR, f"overview-{prefix}-390-dark.png")
        print(f"Capturing {p_390_dark}...")
        capture_screenshot("http://127.0.0.1:8000?theme=dark", p_390_dark, 390, 844)

        # 4. 390px Light
        p_390_light = os.path.join(OUTPUT_DIR, f"overview-{prefix}-390-light.png")
        print(f"Capturing {p_390_light}...")
        capture_screenshot("http://127.0.0.1:8000?theme=light", p_390_light, 390, 844)

        print(f"Successfully captured all {prefix} screenshots!")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
