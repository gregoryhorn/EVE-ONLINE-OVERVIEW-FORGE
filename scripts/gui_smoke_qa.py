"""Browser smoke QA for the local Overview Forge GUI."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="")
    parser.add_argument("--port", type=int, default=7477)
    parser.add_argument("--output", default="qa-artifacts")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    server = None
    url = args.url or f"http://127.0.0.1:{args.port}"
    if not args.url:
        server = _start_server(args.port)
        _wait_for_server(url)

    try:
        _run_browser_checks(url, Path(args.output), headed=args.headed)
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
    return 0


def _start_server(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.Popen(
        [sys.executable, "-m", "eve_overview_manager.cli", "gui", "--port", str(port), "--no-browser"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for_server(url: str) -> None:
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"GUI did not become ready: {url}")


def _run_browser_checks(url: str, output: Path, *, headed: bool) -> None:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as error:
        raise RuntimeError("Install QA dependencies with: python -m pip install -e .[dev] && python -m playwright install chromium") from error

    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed)
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.goto(url)
        expect(page.locator(".brand-name")).to_contain_text("OVERVIEW FORGE")
        expect(page.locator('button[data-template="standard"]')).to_be_visible()
        page.screenshot(path=output / "dashboard.png", full_page=True)

        page.locator('button[data-template="standard"]').click()
        expect(page.locator(".overview-filename")).to_contain_text("standard")
        page.locator('li[data-screen="presets"]').click()
        expect(page.locator("text=Ship Groups & Entity Types")).to_be_visible()
        page.screenshot(path=output / "presets.png", full_page=True)

        page.locator('li[data-screen="importexport"]').click()
        expect(page.locator("#center-panel .section-header")).to_contain_text("Import / Export")
        page.screenshot(path=output / "import-export.png", full_page=True)

        page.locator('li[data-screen="profiles"]').click()
        expect(page.locator("#center-panel .section-header")).to_contain_text("Profile Tools")
        page.screenshot(path=output / "profiles-same-pc.png", full_page=True)

        page.locator('button[data-profile-mode-tab="other-pc"]').click()
        expect(page.locator("text=Portable Profile Package")).to_be_visible()
        page.screenshot(path=output / "profiles-other-pc.png", full_page=True)

        page.locator('button[data-profile-mode-tab="snapshots"]').click()
        expect(page.locator("text=Known-Good Profile Snapshots")).to_be_visible()
        page.screenshot(path=output / "profiles-snapshots.png", full_page=True)
        browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
