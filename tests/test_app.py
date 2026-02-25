import subprocess
import time

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def app_url():
    """Start the Shiny app server for testing."""
    proc = subprocess.Popen(
        ["python", "-m", "shiny", "run", "--port", "8765", "src/app.py"],
    )
    time.sleep(5)  # Wait for server startup
    yield "http://localhost:8765"
    proc.terminate()
    proc.wait()


def test_app_loads(page: Page, app_url: str):
    """Smoke test: app loads and displays the navbar title."""
    page.goto(app_url)
    expect(page.locator("text=fin-health")).to_be_visible(timeout=10_000)
