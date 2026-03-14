"""Configuration and test data for QBS Issue Tracker automation tests.

Values marked with # CHANGE must be updated per run to avoid "already exists" errors
(client name, ticket name, project name, emails, user names, notification message).
"""

# =============================================================================
# GLOBAL
# =============================================================================

BASE_URL = "http://aminmuwafi-001-site35.itempurl.com"
LOGIN_URL = f"{BASE_URL}/login"
PROTECTED_PAGE_URL = f"{BASE_URL}/issue"

# =============================================================================
# AUTH TESTS (test_auth.py)
# =============================================================================

CUSTOMER_USERS = [
    {"email": "client1.project2", "password": "123456", "project_id": "project1"},
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

# =============================================================================
# USER MANAGEMENT TESTS (test_user_management.py)
# =============================================================================

MANAGEMENT_USERS_URL = f"{BASE_URL}/admin/user"
MANAGEMENT_USER_CREATE_URL = f"{BASE_URL}/admin/user/create"

SUPERADMIN_USER = {"email": "new.superadmin", "password": "123456"}

NEW_USER_FOR_MANAGEMENT_TEST = {
    "user_name": "test.auto.admin400",  # CHANGE: unique per run (avoid "already exists")
    "first_name": "Test",
    "last_name": "Automation",
    "email": "test.auto.admin400@example.com",  # CHANGE: unique per run (match user_name)
    "password": "TestPass123!",
    "role": "Admin",
}

PROJECT_FOR_NEW_USER = "Legal"

UPDATED_USER_FOR_EDIT_TEST = {
    "user_name": "test.auto.edited401",  # CHANGE: unique per run (avoid "already exists")
    "first_name": "Edited",
    "last_name": "User",
    "email": "test.auto.edited401@example.com",  # CHANGE: unique per run (match user_name)
    "role": "Agency",
}

PROJECTS_DESELECT_ON_EDIT = ["Legal"]
PROJECTS_SELECT_ON_EDIT = ["Sales Academy", "Subscriptions"]

# =============================================================================
# TICKETING TESTS (test_ticketing.py)
# =============================================================================

MODERATOR_TICKET_USER = {"email": "Abdulrahman", "password": "Abdnsour$0216191"}  # CHANGE: valid moderator credentials
AGENT_TICKET_USER = {"email": "Abdulrahman-Agency", "password": "Abdnsour$0216191"}  # CHANGE: valid agent credentials

ISSUE_PAGE_URL = f"{BASE_URL}/issue"
ISSUE_CREATE_URL = f"{BASE_URL}/issue/create"

TICKET_PROJECT = "abdulrahman-project"  # CHANGE: existing project name
TICKET_CREATE_ON_BEHALF_OF = "Abdulrahman-Agency"  # CHANGE: existing agency user
TICKET_TITLE = "Automation Ticket405"  # CHANGE: unique per run (avoid duplicate ticket)
TICKET_RELATED_TICKET = "test4"  # CHANGE: existing ticket for relation
TICKET_CATEGORY = "Bug"
TICKET_SEVERITY = "High"
TICKET_DESCRIPTION = "Automation: description of the issue."
TICKET_EXPECTED_BEHAVIOR = "Automation: expected behavior."
TICKET_ADDITIONAL_NOTES = "Automation: additional notes."

TICKET_EDIT_TYPE = "CR"
TICKET_EDIT_SEVERITY = "Medium"
TICKET_EDIT_STATUS = "Solved"
TICKET_EDIT_ASSIGNEE = "m.alsadi"
TICKET_EDIT_DESCRIPTION = "anything"
TICKET_EDIT_EXPECTED_BEHAVIOR = "anything"
TICKET_EDIT_ADDITIONAL_NOTES = "anything"
TICKET_EDIT_RELATED_TICKET = "test3"

TICKET_AGENT_CLOSE_STATUS = "Closed"
TICKET_AGENT_COMMENT = "anything"
TICKET_AGENT_TITLE = "Automation Ticket Agent406"  # CHANGE: unique per run (agent creates 2nd ticket)

# =============================================================================
# ADMIN TICKET TESTS (test_admin_ticket.py)
# =============================================================================

ADMIN_TICKET_USER = {"email": "Abdulrahman-Admin", "password": "Abdnsour$0216191"}  # CHANGE: valid admin credentials
ADMIN_TICKET_TITLE = "Automation Ticket Admin 407"  # CHANGE: unique per run (admin creates ticket)
ADMIN_TICKET_EDIT_STATUS = "Solved"
ADMIN_TICKET_EDIT_COMMENT = "solved and waiting for QA to confirm"

# =============================================================================
# NOTIFICATION TESTS (test_notification.py)
# =============================================================================

NOTIFICATION_URL = f"{BASE_URL}/admin/notification"
NOTIFICATION_PROJECT = "abdulrahman-project"  # CHANGE: existing project name
NOTIFICATION_MESSAGE = "Automation notification message"  # CHANGE: unique per run (avoid duplicate)

# =============================================================================
# ADMIN NOTIFICATION TESTS (test_admin_notification.py)
# =============================================================================

ADMIN_NOTIFICATION_MESSAGE = "testing message"  # CHANGE: unique per run (admin creates notification)

# =============================================================================
# PROJECT MANAGEMENT TESTS (test_client_project.py)
# =============================================================================

PROJECT_URL = f"{BASE_URL}/admin/project"
PROJECT_CREATE_URL = f"{BASE_URL}/admin/project/create"

NEW_PROJECT_NAME = "Abdulrahman-project408"  # CHANGE: unique per run (avoid duplicate project)
EDIT_PROJECT_NAME = "Abdulrahman-project409"  # CHANGE: unique per run (edit target)
PROJECT_CLIENT_NAME = "QBS"  # CHANGE: existing client name
PROJECT_ASSOCIATED_USERS_CREATE = ["Abdulrahman-Agency", "Abdulrahman-Admin"]  # CHANGE: existing users
PROJECT_USER_EMAIL = "automation.project@example.com"  # CHANGE: unique per run if creating user
PROJECT_DESCRIPTION = "Automation: project description for testing."

PROJECT_EDIT_DESELECT_USERS = ["Abdulrahman-Admin"]  # CHANGE: existing user to deselect
PROJECT_EDIT_SELECT_USERS = ["test.auto.admin107"]  # CHANGE: existing user to select (must exist)
PROJECT_EDIT_DESCRIPTION = "Automation: edited description."
