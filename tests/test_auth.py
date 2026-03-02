

import pytest
from config import (
    BASE_URL,
    LOGIN_URL,
    PROTECTED_PAGE_URL,
    CUSTOMER_USERS,
    SUPPORT_USERS,
    MSG_EMAIL_REQUIRED,
    MSG_PASSWORD_REQUIRED,
    MSG_INVALID_CREDENTIALS,
    INVALID_EMAIL_FORMAT,
    INVALID_PASSWORD,
    ANY_PASSWORD,
)
from pages.login_page import LoginPage


@pytest.fixture
def login_page(driver, login_url):
    base = BASE_URL
    page = LoginPage(driver, base)
    page.open(return_url=None)
    return page


# --- TC_AUTH_001: Customer login with valid credentials (CAPTCHA disabled) ---
@pytest.mark.parametrize("user", CUSTOMER_USERS[:1], ids=["client1.project1"])
def test_TC_AUTH_001_customer_login_valid_credentials(login_page, user):
    """User logs in with valid credentials; should redirect to /issue."""
    login_page.login(user["email"], user["password"])
    assert login_page.wait_for_redirect_to_issue(timeout=15), (
        f"After login expected redirect to {PROTECTED_PAGE_URL}, got: {login_page.get_current_url()}"
    )
    current_url = login_page.get_current_url()
    assert "/issue" in current_url, f"Expected URL to contain /issue, got: {current_url}"


# --- TC_AUTH_002: Support/Admin user login ---
@pytest.mark.parametrize("user", SUPPORT_USERS, ids=[u["email"] for u in SUPPORT_USERS])
def test_TC_AUTH_002_support_login_success(login_page, user):
    """Support/Admin user logs in successfully; should redirect to /issue."""
    login_page.login(user["email"], user["password"])
    assert login_page.wait_for_redirect_to_issue(timeout=15), (
        f"After login expected redirect to {PROTECTED_PAGE_URL}, got: {login_page.get_current_url()}"
    )


# --- TC_AUTH_003: Wrong password ---
@pytest.mark.parametrize("user", CUSTOMER_USERS[:1] + SUPPORT_USERS[:1], ids=["customer", "support"])
def test_TC_AUTH_003_wrong_password(login_page, user):
    """Wrong password shows error and user stays on login page."""
    login_page.login(user["email"], INVALID_PASSWORD)
    assert "login" in login_page.get_current_url().lower()
    assert MSG_INVALID_CREDENTIALS in login_page.get_validation_messages() or "invalid" in login_page.get_validation_messages().lower()


# --- TC_AUTH_004: Invalid email format ---
def test_TC_AUTH_004_invalid_email_format(login_page):
    """Invalid email format shows validation message; login not submitted."""
    login_page.enter_email(INVALID_EMAIL_FORMAT)
    login_page.enter_password(ANY_PASSWORD)
    login_page.click_login()
    assert "login" in login_page.get_current_url().lower()
    assert "email" in login_page.get_validation_messages().lower()


# --- TC_AUTH_005: Blank email ---
def test_TC_AUTH_005_blank_email(login_page):
    """Blank email shows validation; login not submitted (button may be disabled, use force click)."""
    login_page.enter_password(ANY_PASSWORD)
    login_page.click_login_force()
    assert "login" in login_page.get_current_url().lower()
    msg = login_page.get_validation_messages().lower()
    assert "required" in msg or "username" in msg or "email" in msg


# --- TC_AUTH_006: Blank password ---
def test_TC_AUTH_006_blank_password(login_page):
    """Blank password shows validation; login not submitted."""
    login_page.enter_email(CUSTOMER_USERS[0]["email"])
    login_page.click_login_force()
    assert "login" in login_page.get_current_url().lower()
    msg = login_page.get_validation_messages().lower()
    assert "required" in msg or "password" in msg


# --- TC_AUTH_007: Both fields empty ---
def test_TC_AUTH_007_both_fields_empty(login_page):
    """Both email and password empty show required messages."""
    login_page.click_login_force()
    msg = login_page.get_validation_messages().lower()
    assert "login" in login_page.get_current_url().lower()
    assert "required" in msg or "username" in msg or "password" in msg or "email" in msg


# --- TC_AUTH_008: Login without CAPTCHA (CAPTCHA disabled → login allowed) ---
def test_TC_AUTH_008_customer_login_without_captcha(login_page):
    """With CAPTCHA disabled, user can login without completing CAPTCHA."""
    user = CUSTOMER_USERS[0]
    login_page.login(user["email"], user["password"])
    assert login_page.wait_for_redirect_to_issue(timeout=15), (
        f"Expected redirect to /issue, got: {login_page.get_current_url()}"
    )


# --- TC_AUTH_009: CAPTCHA not shown on login ---
def test_TC_AUTH_009_no_captcha_for_support_login(login_page):
    """Login form does not display CAPTCHA."""
    assert not login_page.is_captcha_visible()


# --- TC_AUTH_011: Direct access to protected page without login ---
def test_TC_AUTH_011_protected_page_redirects_to_login(login_page):
    """Unauthenticated user opening protected URL is redirected to login."""
    login_page.driver.get(PROTECTED_PAGE_URL)
    assert "login" in login_page.get_current_url().lower() or "unauthorized" in login_page.get_page_source().lower()


# --- TC_AUTH_012: Session persists after refresh ---
@pytest.mark.parametrize("user", [CUSTOMER_USERS[0]] + SUPPORT_USERS[:1], ids=["customer", "support"])
def test_TC_AUTH_012_session_after_refresh(login_page, user):
    """User stays logged in after page refresh."""
    login_page.login(user["email"], user["password"])
    login_page.wait_for_redirect_to_issue(timeout=15)
    login_page.driver.refresh()
    login_page.driver.get(PROTECTED_PAGE_URL)
    assert "login" not in login_page.get_current_url().lower()
