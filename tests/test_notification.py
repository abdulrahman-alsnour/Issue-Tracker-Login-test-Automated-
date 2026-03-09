"""
Notification automation test: login as moderator, go to /admin/notification,
click New Notification, select project (abdulrahman-project), fill message,
toggle Show on popup, Save. Then logout, login as agent, and verify notification popup is visible.
"""

import time

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import (
    BASE_URL,
    MODERATOR_TICKET_USER,
    AGENT_TICKET_USER,
    NOTIFICATION_URL,
    NOTIFICATION_PROJECT,
    NOTIFICATION_MESSAGE,
)
from pages.login_page import LoginPage
from pages.notification_page import NotificationPage


@pytest.fixture
def logged_in_moderator(driver):
    """Log in as moderator (Abdulrahman) and wait for redirect to /issue."""
    login = LoginPage(driver, BASE_URL)
    login.open(return_url="/issue")
    login.login(MODERATOR_TICKET_USER["email"], MODERATOR_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    return driver


def test_moderator_send_notification_agent_views(logged_in_moderator):
    """
    Login as moderator, create notification (abdulrahman-project, message, Show on popup), Save.
    Logout, login as agent, verify notification popup is visible.
    """
    driver = logged_in_moderator
    assert "/issue" in driver.current_url, "Should be redirected to issue page after login"

    notification_page = NotificationPage(driver, BASE_URL)
    notification_page.open_notification_page(NOTIFICATION_URL)
    notification_page.click_new_notification()
    notification_page.wait_for_send_notification_form()

    notification_page.select_project(NOTIFICATION_PROJECT)
    notification_page.fill_message(NOTIFICATION_MESSAGE)
    notification_page.toggle_show_on_popup(on=True)
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
    assert notification_page.wait_for_notification_popup_visible(
        NOTIFICATION_MESSAGE, timeout=15
    ), f"Agent should see notification popup containing '{NOTIFICATION_MESSAGE}'"

    notification_page.click_viewed_on_notification_popup(NOTIFICATION_MESSAGE)
