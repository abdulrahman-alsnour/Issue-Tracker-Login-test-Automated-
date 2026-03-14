"""
Admin creates notification: login as admin, go to /admin/notification,
click New Notification, select project, fill message, keep Show on popup OFF, Save.
Then logout, login as agent, click notification icon, click Viewed on the notification,
verify badge count decreases.
"""

import time

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import (
    BASE_URL,
    ADMIN_TICKET_USER,
    AGENT_TICKET_USER,
    NOTIFICATION_URL,
    NOTIFICATION_PROJECT,
    ADMIN_NOTIFICATION_MESSAGE,
)
from pages.login_page import LoginPage
from pages.notification_page import NotificationPage


@pytest.fixture
def logged_in_admin(driver):
    """Log in as admin (Abdulrahman-Admin) and wait for redirect to /issue."""
    login = LoginPage(driver, BASE_URL)
    login.open(return_url="/issue")
    login.login(ADMIN_TICKET_USER["email"], ADMIN_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    return driver


def test_admin_creates_notification(logged_in_admin):
    """
    Login as admin, create notification (abdulrahman-project, testing message, Show on popup OFF).
    Logout, login as agent, click notification icon, click Viewed, verify badge count decreases.
    """
    driver = logged_in_admin
    assert "/issue" in driver.current_url, "Should be redirected to issue page after login"

    notification_page = NotificationPage(driver, BASE_URL)
    notification_page.open_notification_page(NOTIFICATION_URL)
    notification_page.click_new_notification()
    notification_page.wait_for_send_notification_form()

    notification_page.select_project(NOTIFICATION_PROJECT)
    notification_page.fill_message(ADMIN_NOTIFICATION_MESSAGE)
    notification_page.toggle_show_on_popup(on=False)
    notification_page.click_save()

    time.sleep(2)
    assert "notification" in driver.current_url.lower(), "Should remain on notification page after save"

    login = LoginPage(driver, BASE_URL)
    login.logout(open_menu_first=True)
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))

    login.open(return_url="/issue")
    login.login(AGENT_TICKET_USER["email"], AGENT_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)

    time.sleep(2)
    notification_page = NotificationPage(driver, BASE_URL)
    notification_page.click_notification_icon()
    badge_before = notification_page.get_notification_badge_count()
    assert badge_before >= 1, f"Expected at least 1 unread notification, got {badge_before}"
    notification_page.click_viewed_on_notification_dropdown(ADMIN_NOTIFICATION_MESSAGE)
    time.sleep(1)
    badge_after = notification_page.get_notification_badge_count()
    assert badge_after == badge_before - 1, (
        f"Badge count should decrease by 1 after viewing. Before: {badge_before}, after: {badge_after}"
    )
