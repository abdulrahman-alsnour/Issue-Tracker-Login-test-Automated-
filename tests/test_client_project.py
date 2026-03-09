"""
Project management test: login as moderator, create new project (client QBS),
edit project, show inactive and verify.
"""

import time

import pytest
from config import (
    BASE_URL,
    MODERATOR_TICKET_USER,
    PROJECT_URL,
    NEW_PROJECT_NAME,
    EDIT_PROJECT_NAME,
    PROJECT_CLIENT_NAME,
    PROJECT_ASSOCIATED_USERS_CREATE,
    PROJECT_USER_EMAIL,
    PROJECT_DESCRIPTION,
    PROJECT_EDIT_DESELECT_USERS,
    PROJECT_EDIT_SELECT_USERS,
    PROJECT_EDIT_DESCRIPTION,
)
from pages.login_page import LoginPage
from pages.project_page import ProjectPage


@pytest.fixture
def logged_in_moderator(driver):
    """Log in as moderator (Abdulrahman) and wait for redirect to /issue."""
    login = LoginPage(driver, BASE_URL)
    login.open(return_url="/issue")
    login.login(MODERATOR_TICKET_USER["email"], MODERATOR_TICKET_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    return driver


def test_moderator_create_and_edit_project(logged_in_moderator):
    """
    Login as moderator, create new project (Abdulrahman-project2, client QBS, users, email, description, Active ON), Save.
    Search for project, click first result to edit.
    Edit: name Abdulrahman-project3, remove Abdulrahman-Admin add test.auto.admin107, edit description, Active OFF, Save.
    Show inactive, search for Abdulrahman-project3, verify it appears in table.
    """
    driver = logged_in_moderator
    assert "/issue" in driver.current_url, "Should be redirected to issue page after login"

    project_page = ProjectPage(driver, BASE_URL)
    project_page.open_projects_page(PROJECT_URL)
    project_page.click_new_project()
    project_page.wait_for_create_project_form()
    project_page.fill_project_name(NEW_PROJECT_NAME)
    project_page.select_client(PROJECT_CLIENT_NAME)
    project_page.select_associated_users(PROJECT_ASSOCIATED_USERS_CREATE)
    project_page.fill_user_email(PROJECT_USER_EMAIL)
    project_page.fill_description(PROJECT_DESCRIPTION)
    project_page.toggle_active(on=True)
    project_page.click_save()
    time.sleep(2)

    project_page.wait_back_on_projects_list(projects_url=PROJECT_URL)
    project_page.search_project(NEW_PROJECT_NAME)
    project_page.click_first_project_in_list(NEW_PROJECT_NAME)
    project_page.wait_for_edit_project_page()

    project_page.fill_edit_project_name(EDIT_PROJECT_NAME)
    project_page.set_associated_users_on_edit(PROJECT_EDIT_DESELECT_USERS, PROJECT_EDIT_SELECT_USERS)
    project_page.fill_edit_description(PROJECT_EDIT_DESCRIPTION)
    project_page.toggle_active(on=False)
    project_page.click_save()
    time.sleep(2)

    project_page.wait_back_on_projects_list(projects_url=PROJECT_URL)
    project_page.show_inactive_projects()
    project_page.search_project(EDIT_PROJECT_NAME, wait_after_sec=3)
    time.sleep(1)
    assert project_page.is_project_in_table(EDIT_PROJECT_NAME), (
        f"Project '{EDIT_PROJECT_NAME}' should appear in table when Show inactive is on"
    )
