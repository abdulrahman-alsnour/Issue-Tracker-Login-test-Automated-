"""
Ticketing test: login as moderator, land on /issue, click Report a New Ticket,
then on create page select project, enable Create on behalf of, select agency.
"""

import time

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import (
    BASE_URL,
    MODERATOR_TICKET_USER,
    AGENT_TICKET_USER,
    ISSUE_CREATE_URL,
    TICKET_PROJECT,
    TICKET_CREATE_ON_BEHALF_OF,
    TICKET_TITLE,
    TICKET_RELATED_TICKET,
    TICKET_CATEGORY,
    TICKET_SEVERITY,
    TICKET_DESCRIPTION,
    TICKET_EXPECTED_BEHAVIOR,
    TICKET_ADDITIONAL_NOTES,
    TICKET_EDIT_TYPE,
    TICKET_EDIT_SEVERITY,
    TICKET_EDIT_STATUS,
    TICKET_EDIT_ASSIGNEE,
    TICKET_EDIT_DESCRIPTION,
    TICKET_EDIT_EXPECTED_BEHAVIOR,
    TICKET_EDIT_ADDITIONAL_NOTES,
    TICKET_EDIT_RELATED_TICKET,
    TICKET_AGENT_CLOSE_STATUS,
    TICKET_AGENT_COMMENT,
    TICKET_AGENT_TITLE,
)
from pages.login_page import LoginPage
from pages.issue_page import IssuePage


@pytest.fixture
def logged_in_moderator(driver):
    """Log in as moderator (Abdulrahman) and wait for redirect to /issue."""
    login = LoginPage(driver, BASE_URL)
    login.open(return_url="/issue")
    login.login(MODERATOR_TICKET_USER["email"], MODERATOR_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    return driver


def test_moderator_login_and_click_report_new_ticket(logged_in_moderator):
    """
    Login as moderator, get directed to /issue, click Report a New Ticket,
    then on create page: select project, enable Create on behalf of, select Abdulrahman-Agency.
    """
    driver = logged_in_moderator
    assert "/issue" in driver.current_url, "Should be redirected to issue page after login"

    issue_page = IssuePage(driver, BASE_URL)
    issue_page.wait_for_issue_page(timeout=5)
    issue_page.click_report_new_ticket()
    issue_page.wait_for_issue_create_page(timeout=10, pause_seconds=5)

    assert "/issue/create" in driver.current_url, f"Should be on create page: {ISSUE_CREATE_URL}"

    issue_page.select_project(TICKET_PROJECT)
    issue_page.toggle_create_on_behalf_of(on=True)
    issue_page.select_create_on_behalf_of(TICKET_CREATE_ON_BEHALF_OF)
    issue_page.fill_ticket_title(TICKET_TITLE)
    issue_page.toggle_related_ticket(on=True)
    issue_page.select_related_ticket(TICKET_RELATED_TICKET)
    issue_page.click_next(timeout=15)
    issue_page.select_category(TICKET_CATEGORY)
    issue_page.select_severity(TICKET_SEVERITY)
    issue_page.click_next(timeout=15)  # step 2 -> step 3 (text areas)
    issue_page.fill_description(TICKET_DESCRIPTION)
    issue_page.fill_expected_behavior(TICKET_EXPECTED_BEHAVIOR)
    issue_page.click_next(timeout=15)  # step 3 -> Add screenshot/s
    issue_page.click_next(timeout=15)  # skip screenshot step
    issue_page.fill_additional_notes(TICKET_ADDITIONAL_NOTES)
    issue_page.click_next(timeout=15)  # -> review/summary page
    issue_page.click_submit(timeout=15)
    issue_page.wait_for_all_tickets_page(timeout=15)
    issue_page.search_ticket_by_title(TICKET_TITLE)
    issue_page.click_first_ticket_in_list(TICKET_TITLE, timeout=10)
    issue_page.wait_for_issue_edit_page(timeout=10)
    issue_page.select_edit_type(TICKET_EDIT_TYPE)
    issue_page.select_edit_severity(TICKET_EDIT_SEVERITY)
    issue_page.select_edit_status(TICKET_EDIT_STATUS)
    issue_page.select_edit_assignee(TICKET_EDIT_ASSIGNEE)
    issue_page.fill_edit_description(TICKET_EDIT_DESCRIPTION)
    issue_page.fill_edit_expected_behavior(TICKET_EDIT_EXPECTED_BEHAVIOR)
    issue_page.fill_edit_additional_notes(TICKET_EDIT_ADDITIONAL_NOTES)
    issue_page.select_edit_related_ticket(TICKET_EDIT_RELATED_TICKET)
    issue_page.click_save_changes(timeout=15)
    # Wait until we're back on the issue page (not edit), then open nav menu and Sign out
    issue_page.wait_for_all_tickets_page(timeout=15)
    login = LoginPage(driver, BASE_URL)
    login.logout(open_menu_first=True)
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))
    login.open(return_url="/issue")
    login.login(AGENT_TICKET_USER["email"], AGENT_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    # Agent: search for the ticket, open edit, set status to Closed, add comment, submit comment, save
    issue_page.wait_for_all_tickets_page(timeout=10)
    issue_page.search_ticket_by_title(TICKET_TITLE)
    issue_page.click_first_ticket_in_list(TICKET_TITLE, timeout=10)
    issue_page.wait_for_issue_edit_page(timeout=10)
    issue_page.select_edit_status(TICKET_AGENT_CLOSE_STATUS)
    issue_page.fill_edit_comment(TICKET_AGENT_COMMENT)
    issue_page.click_submit_comment(timeout=8)
    issue_page.click_save_changes(timeout=15)
    issue_page.wait_for_all_tickets_page(timeout=15)
    time.sleep(3)
    # Agent: Report a new ticket (no Create on behalf of - agent form has Project, Title, Related ticket only)
    issue_page.wait_for_issue_page(timeout=5)
    issue_page.click_report_new_ticket()
    issue_page.wait_for_issue_create_page(timeout=10, pause_seconds=2)
    issue_page.select_project(TICKET_PROJECT)
    issue_page.fill_ticket_title(TICKET_AGENT_TITLE)
    issue_page.toggle_related_ticket(on=True)
    issue_page.select_related_ticket(TICKET_RELATED_TICKET)
    issue_page.click_next(timeout=15)
    issue_page.select_category(TICKET_CATEGORY)
    issue_page.select_severity(TICKET_SEVERITY)
    issue_page.click_next(timeout=15)
    issue_page.fill_description(TICKET_DESCRIPTION)
    issue_page.fill_expected_behavior(TICKET_EXPECTED_BEHAVIOR)
    issue_page.click_next(timeout=15)
    issue_page.click_next(timeout=15)
    issue_page.fill_additional_notes(TICKET_ADDITIONAL_NOTES)
    issue_page.click_next(timeout=15)
    issue_page.click_submit(timeout=15)
