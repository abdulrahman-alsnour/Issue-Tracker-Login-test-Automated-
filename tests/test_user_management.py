"""
Superadmin user management test: add user (role Admin), verify in table, delete, verify gone.
"""
#test-commit 

import time
import pytest
from config import (
    BASE_URL,
    MANAGEMENT_USERS_URL,
    MANAGEMENT_USER_CREATE_URL,
    SUPERADMIN_USER,
    NEW_USER_FOR_MANAGEMENT_TEST,
    PROJECT_FOR_NEW_USER,
    UPDATED_USER_FOR_EDIT_TEST,
    PROJECTS_DESELECT_ON_EDIT,
    PROJECTS_SELECT_ON_EDIT,
)
from pages.login_page import LoginPage
from pages.user_management_page import UserManagementPage


@pytest.fixture
def logged_in_superadmin(driver):
    """Log in as superadmin and wait for redirect to app."""
    login = LoginPage(driver, BASE_URL)
    login.open(return_url=None)
    login.login(SUPERADMIN_USER["email"], SUPERADMIN_USER["password"])
    login.wait_for_redirect_to_issue(timeout=15)
    return driver


def test_superadmin_add_user_search_and_delete(logged_in_superadmin):
    """
    Superadmin logs in, goes to User Management, adds a new user (role Admin),
    searches and verifies user is in the table, deletes the user,
    searches again and verifies user is not found.
    """
    driver = logged_in_superadmin
    um = UserManagementPage(driver, BASE_URL)
    user_data = NEW_USER_FOR_MANAGEMENT_TEST
    username = user_data["user_name"]

    um.open_users_page(MANAGEMENT_USERS_URL)
    um.click_new_user(create_url=MANAGEMENT_USER_CREATE_URL)
    um.fill_new_user_form(
        user_name=user_data["user_name"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        password=user_data["password"],
        role=user_data["role"],
        project=PROJECT_FOR_NEW_USER,
    )
    um.click_save_user()
    time.sleep(4)

    um.wait_back_on_users_list(users_list_url=MANAGEMENT_USERS_URL)
    um.search_user(username, users_list_url=MANAGEMENT_USERS_URL)
    if not um.is_user_in_table(username):
        time.sleep(3)
        um.search_user(username, users_list_url=MANAGEMENT_USERS_URL)
    assert um.is_user_in_table(username), f"User '{username}' should appear in the table after creation"

    um.click_user_name_to_edit(username)
    updated = UPDATED_USER_FOR_EDIT_TEST
    um.fill_edit_user_form(
        user_name=updated["user_name"],
        first_name=updated["first_name"],
        last_name=updated["last_name"],
        email=updated["email"],
        role=updated["role"],
        deselect_projects=PROJECTS_DESELECT_ON_EDIT,
        select_projects=PROJECTS_SELECT_ON_EDIT,
    )
    um.wait_back_on_users_list(users_list_url=MANAGEMENT_USERS_URL)
    um.show_inactive_users()
    um.search_user(updated["user_name"], users_list_url=MANAGEMENT_USERS_URL)

    um.delete_user_row(updated["user_name"])
    um.verify_user_deleted(updated["user_name"], timeout=4)
