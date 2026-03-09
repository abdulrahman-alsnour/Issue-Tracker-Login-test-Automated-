""" Configuration and test data for QBS Issue Tracker login tests."""

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
    "user_name": "test.auto.admin79",
    "first_name": "Test",
    "last_name": "Automation",
    "email": "test.auto.admin79@example.com",
    "password": "TestPass123!",
    "role": "Admin",
}
# Required project when creating a new user (Projects dropdown)
PROJECT_FOR_NEW_USER = "Legal"

# Data to set on the Update User (edit) page: new name, email, first/last name, role Agency, projects Sales Academy + Subscriptions, Active OFF
UPDATED_USER_FOR_EDIT_TEST = {
    "user_name": "test.auto.edited27",
    "first_name": "Edited",
    "last_name": "User",
    "email": "test.auto.edited27@example.com",
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

# Moderator for ticketing tests (login, then use Report a New Ticket on /issue)
MODERATOR_TICKET_USER = {"email": "Abdulrahman", "password": "Abdnsour$0216191"}
AGENT_TICKET_USER = {"email": "Abdulrahman-Agency", "password": "Abdnsour$0216191"}
ISSUE_PAGE_URL = f"{BASE_URL}/issue"
ISSUE_CREATE_URL = f"{BASE_URL}/issue/create"
# Create ticket form: Project dropdown and "Create on behalf of" selection
TICKET_PROJECT = "abdulrahman-project"
TICKET_CREATE_ON_BEHALF_OF = "Abdulrahman-Agency"
TICKET_TITLE = "Automation Ticket97"
TICKET_RELATED_TICKET = "test4"
TICKET_CATEGORY = "Bug"
TICKET_SEVERITY = "High"
TICKET_DESCRIPTION = "Automation: description of the issue."
TICKET_EXPECTED_BEHAVIOR = "Automation: expected behavior."
TICKET_ADDITIONAL_NOTES = "Automation: additional notes."

# Edit page: change Type, Severity, Status, Assignee, text areas, Related ticket
TICKET_EDIT_TYPE = "CR"
TICKET_EDIT_SEVERITY = "Medium"
TICKET_EDIT_STATUS = "Solved"
TICKET_EDIT_ASSIGNEE = "m.alsadi"
TICKET_EDIT_DESCRIPTION = "anything"
TICKET_EDIT_EXPECTED_BEHAVIOR = "anything"
TICKET_EDIT_ADDITIONAL_NOTES = "anything"
TICKET_EDIT_RELATED_TICKET = "test3"

# Agent: close ticket (change status to Closed, add comment, submit comment, save)
TICKET_AGENT_CLOSE_STATUS = "Closed"
TICKET_AGENT_COMMENT = "anything"

# Agent: report a new ticket (same fields as moderator, different title)
TICKET_AGENT_TITLE = "Automation Ticket Agent4"

# Notification automation test (moderator on /admin/notification)
NOTIFICATION_URL = f"{BASE_URL}/admin/notification"
NOTIFICATION_PROJECT = "abdulrahman-project"
NOTIFICATION_MESSAGE = "Automation notification message"

# Project management test (moderator)
PROJECT_URL = f"{BASE_URL}/admin/project"
PROJECT_CREATE_URL = f"{BASE_URL}/admin/project/create"
NEW_PROJECT_NAME = "Abdulrahman-project96"
EDIT_PROJECT_NAME = "Abdulrahman-project97"
PROJECT_CLIENT_NAME = "QBS"
PROJECT_ASSOCIATED_USERS_CREATE = ["Abdulrahman-Agency", "Abdulrahman-Admin"]
PROJECT_USER_EMAIL = "automation.project@example.com"
PROJECT_DESCRIPTION = "Automation: project description for testing."
PROJECT_EDIT_DESELECT_USERS = ["Abdulrahman-Admin"]
PROJECT_EDIT_SELECT_USERS = ["test.auto.admin107"]
PROJECT_EDIT_DESCRIPTION = "Automation: edited description."
