"""Pytest fixtures for Selenium WebDriver and test setup."""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config import LOGIN_URL


@pytest.fixture(scope="function")
def driver():
    """Create a Chrome WebDriver instance per test."""
    import os
    options = Options()
    if os.environ.get("HEADLESS", "1") == "1":
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(30)
    yield browser
    browser.quit()


@pytest.fixture
def login_url():
    """Login page URL."""
    return LOGIN_URL
