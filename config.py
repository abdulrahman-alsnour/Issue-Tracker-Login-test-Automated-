"""Configuration and test data for QBS Issue Tracker login tests."""

BASE_URL = "http://aminmuwafi-001-site35.itempurl.com"
LOGIN_URL = f"{BASE_URL}/login"
PROTECTED_PAGE_URL = f"{BASE_URL}/issue"
MANAGEMENT_USERS_URL = f"{BASE_URL}/admin/user"
MANAGEMENT_USER_CREATE_URL = f"{BASE_URL}/admin/user/create"

CUSTOMER_USERS = [
    {"email": "client1.project2", "password": "123456", "project_id": "project1"},
    {"email": "client2.project", "password": "123456"},
    {"email": "client2.project2", "password": "123456"},
]

SUPPORT_USERS = [
    {"email": "new.superadmin", "password": "123456", "role": "Moderator"},
    {"email": "admin.project1", "password": "123456", "role": "Admin"},
]

# Superadmin (for user management tests)
SUPERADMIN_USER = {"email": "new.superadmin", "password": "123456"}

# Test user created then deleted in user management test (unique so we can search)
NEW_USER_FOR_MANAGEMENT_TEST = {
    "user_name": "test.auto.admin109",
    "first_name": "Test",
    "last_name": "Automation",
    "email": "test.auto.admin109@example.com",
    "password": "TestPass123!",
    "role": "Admin",
}
# Required project when creating a new user (Projects dropdown)
PROJECT_FOR_NEW_USER = "Legal"

# Data to set on the Update User (edit) page: new name, email, first/last name, role Agency, projects Sales Academy + Subscriptions, Active OFF
UPDATED_USER_FOR_EDIT_TEST = {
    "user_name": "test.auto.edited9",
    "first_name": "Edited",
    "last_name": "User",
    "email": "test.auto.edited9@example.com",
    "role": "Agency",
}
# On edit: deselect this project, then select these
PROJECTS_DESELECT_ON_EDIT = ["Legal"]
PROJECTS_SELECT_ON_EDIT = ["Sales Academy", "Subscriptions"]

MSG_EMAIL_REQUIRED = "Email is required"
MSG_PASSWORD_REQUIRED = "Password is required"
MSG_INVALID_CREDENTIALS = "Invalid email or password"
MSG_COMPLETE_CAPTCHA = "Please complete CAPTCHA"

INVALID_EMAIL_FORMAT = "testuser.com"
INVALID_PASSWORD = "wrongpassword123"
ANY_PASSWORD = "anspassword123"
