"""Page object for the login page."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """Login page actions and locators. Adjust selectors if your DOM differs."""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.login_path = "/login"
        self._wait = WebDriverWait(driver, 10)

    @property
    def url(self):
        return f"{self.base_url}{self.login_path}"

    def open(self, return_url: str = "/issue"):
        """Open login page with optional returnUrl."""
        path = f"{self.login_path}?returnUrl={return_url}" if return_url else self.login_path
        self.driver.get(f"{self.base_url}{path}")

    def _find_email_input(self):
        """Single email/username input (one login form for all users)."""
        selectors = [
            (By.ID, "customerEmailOrUsername"),
            (By.ID, "supportEmailOrUsername"),
            (By.ID, "email"),
            (By.NAME, "emailOrUsername"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]
        for by, value in selectors:
            try:
                el = self.driver.find_element(by, value)
                self._wait.until(EC.visibility_of(el))
                return el
            except Exception:
                continue
        raise AssertionError("Email/username input not found.")

    def _find_password_input(self):
        """Single password input (one login form for all users)."""
        selectors = [
            (By.CSS_SELECTOR, "input.p-password-input"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.ID, "customerPassword"),
            (By.ID, "supportPassword"),
            (By.ID, "password"),
            (By.NAME, "password"),
        ]
        for by, value in selectors:
            try:
                el = self.driver.find_element(by, value)
                self._wait.until(EC.visibility_of(el))
                return el
            except Exception:
                continue
        raise AssertionError("Password input not found.")

    def _find_login_button(self):
        """Submit button (visible; use JS click to avoid intercept in CI)."""
        el = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self._wait.until(EC.visibility_of(el))
        return el

    def enter_email(self, email: str):
        self._find_email_input().clear()
        self._find_email_input().send_keys(email)

    def enter_password(self, password: str):
        self._find_password_input().clear()
        self._find_password_input().send_keys(password)

    def click_login(self):
        """Click login via JavaScript so it works in CI when an overlay blocks normal click."""
        btn = self._find_login_button()
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)

    def click_login_force(self):
        """Click login via JavaScript (use when button may be disabled e.g. blank fields)."""
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)

    def login(self, email: str, password: str):
        """Fill credentials and submit. Single login form for all users (customer and admin)."""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()

    def wait_for_redirect_to_issue(self, timeout: int = 15) -> bool:
        """Wait until current URL contains /issue (redirect after login). Returns True if redirected."""
        from selenium.webdriver.support.expected_conditions import url_contains
        try:
            WebDriverWait(self.driver, timeout).until(url_contains("/issue"))
            return True
        except Exception:
            return False

    def get_page_source(self) -> str:
        return self.driver.page_source

    def get_current_url(self) -> str:
        return self.driver.current_url

    def is_captcha_visible(self) -> bool:
        """Check if CAPTCHA element is present and visible."""
        selectors = [
            (By.CSS_SELECTOR, "[class*='captcha'], [id*='captcha'], [data-captcha]"),
            (By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'recaptcha')]"),
        ]
        for by, value in selectors:
            try:
                el = self.driver.find_element(by, value)
                return el.is_displayed()
            except Exception:
                continue
        return False

    def get_validation_messages(self) -> str:
        """Return visible validation/error text (e.g. under form or in alert)."""
        selectors = [
            (By.CSS_SELECTOR, ".error, .validation-message, .text-danger, [role='alert']"),
            (By.CSS_SELECTOR, ".invalid-feedback"),
            (By.XPATH, "//*[contains(@class,'error') or contains(@class,'invalid')]"),
        ]
        texts = []
        for by, value in selectors:
            try:
                for el in self.driver.find_elements(by, value):
                    if el.is_displayed() and el.text:
                        texts.append(el.text.strip())
            except Exception:
                continue
        return " ".join(texts) if texts else self.driver.page_source[:2000]

    def open_menu_if_present(self) -> bool:
        """Click the menu button in the nav bar (nav div.menu / img[alt='menu']) so Sign out is visible."""
        selectors = [
            (By.CSS_SELECTOR, "nav div.menu"),
            (By.CSS_SELECTOR, "nav img[alt='menu']"),
            (By.XPATH, "//nav//div[contains(@class,'menu')]"),
            (By.XPATH, "//nav//img[@alt='menu']"),
            (By.CSS_SELECTOR, "div.menu"),
            (By.CSS_SELECTOR, "img[alt='menu']"),
        ]
        for by, value in selectors:
            try:
                el = self.driver.find_element(by, value)
                if el.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    self.driver.execute_script("arguments[0].click();", el)
                    return True
            except Exception:
                continue
        return False

    def find_logout(self):
        """Find the Sign out link in the opened menu (a.mobile-menu-link containing 'Sign out')."""
        selectors = [
            (By.XPATH, "//a[contains(@class,'mobile-menu-link')][.//span[contains(.,'Sign out')]]"),
            (By.XPATH, "//span[contains(.,'Sign out')]/ancestor::a[1]"),
            (By.XPATH, "//li[contains(@class,'mobile-menu-item')]//a[.//span[contains(.,'Sign out')]]"),
            (By.XPATH, "//*[normalize-space()='Sign out']/ancestor::a[1]"),
            (By.LINK_TEXT, "Sign out"),
            (By.XPATH, "//*[contains(., 'Sign out')]"),
            (By.XPATH, "//*[contains(text(), 'Logout') or contains(., 'Log out')]"),
            (By.LINK_TEXT, "Logout"),
            (By.LINK_TEXT, "Log out"),
        ]
        for by, value in selectors:
            try:
                el = self.driver.find_element(by, value)
                if el.is_displayed():
                    return el
            except Exception:
                continue
        raise AssertionError("Sign out not found. Open the nav menu first.")

    def logout(self, open_menu_first: bool = True):
        """Open nav menu then click Sign out. Call only after you are back on the issue page."""
        if open_menu_first:
            self.open_menu_if_present()
            self._wait.until(EC.element_to_be_clickable((By.XPATH, "//a[.//span[contains(.,'Sign out')]] | //*[contains(., 'Sign out')]")))
        sign_out_el = self.find_logout()
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_out_el)
        try:
            self.driver.execute_script("arguments[0].click();", sign_out_el)
        except Exception:
            try:
                ActionChains(self.driver).move_to_element(sign_out_el).click().perform()
            except Exception:
                sign_out_el.click()