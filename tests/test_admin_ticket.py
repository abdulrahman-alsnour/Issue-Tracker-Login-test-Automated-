"""
Create ticket by admin: login as admin, land on /issue, click Report a New Ticket,
fill the create form (same flow as moderator), save, verify redirect to issue page,
then use filters to search for the ticket.
"""

import time
from datetime import date

import pytest
from config import (
    BASE_URL,
    ADMIN_TICKET_USER,
    ISSUE_CREATE_URL,
    TICKET_PROJECT,
    ADMIN_TICKET_TITLE,
    ADMIN_TICKET_EDIT_STATUS,
    ADMIN_TICKET_EDIT_COMMENT,
    TICKET_RELATED_TICKET,
    TICKET_CATEGORY,
    TICKET_SEVERITY,
    TICKET_DESCRIPTION,
    TICKET_EXPECTED_BEHAVIOR,
    TICKET_ADDITIONAL_NOTES,
)
from pages.login_page import LoginPage
from pages.issue_page import IssuePage


@pytest.fixture
def logged_in_admin(driver):
    """Log in as admin (Abdulrahman-Admin) and wait for redirect to /issue."""
    login = LoginPage(driver, BASE_URL)
    login.open(return_url="/issue")
    login.login(ADMIN_TICKET_USER["email"], ADMIN_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    return driver


def test_create_ticket_by_admin(logged_in_admin):
    """
    Login as admin, create ticket, use filters to find it, click to edit,
    change status to Solved, add comment, save, verify back on issue page.
    """
    driver = logged_in_admin
    assert "/issue" in driver.current_url, "Should be redirected to issue page after login"

    issue_page = IssuePage(driver, BASE_URL)
    issue_page.wait_for_issue_page(timeout=5)
    issue_page.click_report_new_ticket()
    issue_page.wait_for_issue_create_page(timeout=10, pause_seconds=5)

    assert "/issue/create" in driver.current_url, f"Should be on create page: {ISSUE_CREATE_URL}"

    issue_page.select_project(TICKET_PROJECT)
    issue_page.fill_ticket_title(ADMIN_TICKET_TITLE)
    issue_page.toggle_related_ticket(on=True)
    issue_page.select_related_ticket(TICKET_RELATED_TICKET)
    issue_page.click_next(timeout=15)
    issue_page.select_category(TICKET_CATEGORY)
    issue_page.select_severity(TICKET_SEVERITY)
    issue_page.click_next(timeout=15)
    issue_page.fill_description(TICKET_DESCRIPTION)
    issue_page.fill_expected_behavior(TICKET_EXPECTED_BEHAVIOR)
    issue_page.click_next(timeout=15)
    issue_page.click_next(timeout=15)  # skip screenshot step
    issue_page.fill_additional_notes(TICKET_ADDITIONAL_NOTES)
    issue_page.click_next(timeout=15)
    issue_page.click_submit(timeout=15)
    issue_page.wait_for_all_tickets_page(timeout=15)
    # Use filters to search for the ticket we just created
    issue_page.click_filter_button()
    issue_page.select_filter_category(TICKET_CATEGORY)
    issue_page.select_filter_severity(TICKET_SEVERITY)
    issue_page.select_filter_status("Open")
    issue_page.select_filter_date(date.today())
    issue_page.click_apply_filters()
    time.sleep(2)
    # Ticket is at top of table - click to edit
    issue_page.click_first_ticket_in_list(ADMIN_TICKET_TITLE, timeout=10)
    issue_page.wait_for_issue_edit_page(timeout=15)
    issue_page.select_edit_status(ADMIN_TICKET_EDIT_STATUS)
    issue_page.fill_edit_comment(ADMIN_TICKET_EDIT_COMMENT)
    issue_page.click_submit_comment(timeout=8)
    issue_page.click_save_changes(timeout=15)
    issue_page.wait_for_all_tickets_page(timeout=25)
