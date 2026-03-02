"""Configuration and test data for QBS Issue Tracker login tests."""

BASE_URL = "http://aminmuwafi-001-site35.itempurl.com"
LOGIN_URL = f"{BASE_URL}/login"
PROTECTED_PAGE_URL = f"{BASE_URL}/issue"

CUSTOMER_USERS = [
    {"email": "client1.project1", "password": "123456", "project_id": "project1"},
    {"email": "client2.project", "password": "123456"},
    {"email": "client2.project2", "password": "123456"},
]

SUPPORT_USERS = [
    {"email": "new.superadmin", "password": "123456", "role": "Moderator"},
    {"email": "admin.project1", "password": "123456", "role": "Admin"},
]

MSG_EMAIL_REQUIRED = "Email is required"
MSG_PASSWORD_REQUIRED = "Password is required"
MSG_INVALID_CREDENTIALS = "Invalid email or password"
MSG_COMPLETE_CAPTCHA = "Please complete CAPTCHA"

INVALID_EMAIL_FORMAT = "testuser.com"
INVALID_PASSWORD = "wrongpassword123"
ANY_PASSWORD = "anspassword123"
