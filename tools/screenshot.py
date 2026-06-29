"""Capture a screenshot of the running Streamlit app for visual QA."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8533"
OUT = sys.argv[2] if len(sys.argv) > 2 else "tools/setup_screenshot.png"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(URL, wait_until="networkidle", timeout=60000)
        # Streamlit needs a moment to hydrate + run reruns.
        page.wait_for_timeout(9000)
        full = "--full" in sys.argv
        page.screenshot(path=OUT, full_page=full)
        browser.close()
        print(f"saved {OUT}")


if __name__ == "__main__":
    main()
