"""Page object for the Notification management page (/admin/notification)."""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NotificationPage:
    """Notification management page: All Notifications list and Send a Notification form."""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self._wait = WebDriverWait(driver, 15)

    def open_notification_page(self, url: str):
        """Navigate to the notification management page."""
        self.driver.get(url)
        self._wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'All Notifications') or contains(text(), 'Notifications')]"
            ))
        )

    def click_new_notification(self):
        """Click the 'New Notification' button to open the Send a Notification form."""
        for by, value in [
            (By.XPATH, "//button[contains(., 'New Notification')]"),
            (By.XPATH, "//*[contains(@class,'btn')][contains(., 'New Notification')]"),
            (By.LINK_TEXT, "New Notification"),
        ]:
            try:
                btn = self._wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
                return
            except Exception:
                continue
        raise AssertionError("New Notification button not found")

    def wait_for_send_notification_form(self, timeout: int = 8):
        """Wait until the 'Send a Notification' form is visible."""
        self._wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'Send a Notification')]"
            ))
        )
        time.sleep(0.3)

    def select_project(self, project_name: str):
        """Open the Project dropdown and select the given project (e.g. 'abdulrahman-project')."""
        for trigger_xpath in [
            "//label[contains(., 'Project')]/following::*[contains(@class,'p-multiselect')][1]",
            "//label[contains(., 'Project')]/following::*[contains(@class,'p-dropdown') or @role='combobox'][1]",
            "//*[contains(@placeholder,'Select Projects')]/ancestor::*[contains(@class,'p-dropdown') or contains(@class,'p-multiselect')][1]",
        ]:
            try:
                trigger = self.driver.find_element(By.XPATH, trigger_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                break
            except Exception:
                continue
        else:
            raise AssertionError("Project dropdown trigger not found")

        time.sleep(0.5)
        panel_xpath = (
            "//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]"
            "[contains(@class,'p-component') or contains(@class,'p-visible')]"
        )
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, panel_xpath))
            )
        except Exception:
            pass
        time.sleep(0.4)

        for opt_xpath in [
            f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]"
            f"//li[contains(., '{project_name}')]",
            f"//*[contains(@class,'p-multiselect-item') or contains(@class,'p-dropdown-item')]"
            f"[contains(normalize-space(.), '{project_name}')]",
        ]:
            try:
                opt = self.driver.find_element(By.XPATH, opt_xpath)
                if opt.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opt)
                    self.driver.execute_script("arguments[0].click();", opt)
                    time.sleep(0.4)
                    return
            except Exception:
                continue
        raise AssertionError(f"Project option '{project_name}' not found in dropdown")

    def fill_message(self, text: str):
        """Fill the Message textarea."""
        for xpath in [
            "//label[contains(., 'Message')]/following::textarea[1]",
            "//textarea[contains(@placeholder,'Message') or @formcontrolname='message']",
            "//*[contains(text(), 'Message')]/following::textarea[1]",
        ]:
            try:
                textarea = self.driver.find_element(By.XPATH, xpath)
                if textarea.is_displayed():
                    textarea.clear()
                    textarea.send_keys(text)
                    return
            except Exception:
                continue
        raise AssertionError("Message textarea not found")

    def toggle_show_on_popup(self, on: bool = True):
        """Turn the 'Show on popup' toggle on or off."""
        for switch_xpath in [
            "//*[contains(normalize-space(.), 'Show on popup')]/preceding-sibling::label[contains(@class,'switch')][1]",
            "//*[contains(normalize-space(.), 'Show on popup')]/ancestor::*[.//label[contains(@class,'switch')]][1]//label[contains(@class,'switch')][1]",
            "//label[contains(@class,'switch')][following-sibling::*[contains(., 'Show on popup')]][1]",
        ]:
            try:
                switch_label = self.driver.find_element(By.XPATH, switch_xpath)
                if not switch_label.is_displayed():
                    continue
                checkbox = None
                try:
                    checkbox = switch_label.find_element(By.XPATH, ".//input[@type='checkbox']")
                except Exception:
                    pass

                def is_checked():
                    if not checkbox:
                        return None
                    try:
                        return checkbox.is_selected()
                    except Exception:
                        return None

                if is_checked() == on:
                    return

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch_label)
                time.sleep(0.25)
                if checkbox:
                    try:
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        time.sleep(0.3)
                        if is_checked() == on:
                            return
                    except Exception:
                        pass
                try:
                    self.driver.execute_script("arguments[0].click();", switch_label)
                    time.sleep(0.3)
                    if is_checked() == on:
                        return
                except Exception:
                    pass
                ActionChains(self.driver).move_to_element(switch_label).click().perform()
                time.sleep(0.3)
                return
            except Exception:
                continue
        raise AssertionError("Show on popup toggle not found")

    def click_save(self):
        """Click the Save button on the Send a Notification form."""
        for by, value in [
            (By.XPATH, "//button[contains(., 'Save')]"),
            (By.XPATH, "//*[contains(@class,'btn')][contains(., 'Save')]"),
        ]:
            try:
                btn = self.driver.find_element(by, value)
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    self.driver.execute_script("arguments[0].click();", btn)
                    return
            except Exception:
                continue
        raise AssertionError("Save button not found")

    def wait_for_notification_popup_visible(self, message_substring: str, timeout: int = 15) -> bool:
        """
        Wait for a notification popup/toast containing the given message to be visible.
        Used after agent login when 'Show on popup' was enabled for the notification.
        """
        xpath = f"//*[contains(., '{message_substring}')]"
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            return el.is_displayed()
        except Exception:
            return False

    def click_viewed_on_notification_popup(self, message_substring: str, timeout: int = 10):
        """
        Find the notification popup containing the message and click the 'Viewed' button/link.
        """
        for viewed_xpath in [
            f"//*[contains(., '{message_substring}')]/ancestor::*[.//*[contains(., 'Viewed')]][1]//*[contains(., 'Viewed')]",
            f"//*[contains(., '{message_substring}')]/following::*[contains(., 'Viewed')][1]",
            f"//*[contains(., '{message_substring}')]/preceding::*[contains(., 'Viewed')][1]",
            "//button[contains(., 'Viewed')]",
            "//a[contains(., 'Viewed')]",
            "//*[contains(@class,'btn')][contains(., 'Viewed')]",
            "//*[normalize-space()='Viewed']",
        ]:
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, viewed_xpath))
                )
                if el.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    self.driver.execute_script("arguments[0].click();", el)
                    time.sleep(0.5)
                    return
            except Exception:
                continue
        raise AssertionError("Viewed button/link not found on notification popup")

    def click_notification_icon(self, timeout: int = 10):
        """Click the notification bell icon in the nav bar to open the notification dropdown."""
        for xpath in [
            "//*[contains(@class,'notification-container')]//img[contains(@src,'notification')]",
            "//*[contains(@class,'notification-container')]",
            "//img[@alt='notification']",
            "//*[contains(@class,'notification')]//img",
        ]:
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                self.driver.execute_script("arguments[0].click();", el)
                time.sleep(0.5)
                return
            except Exception:
                continue
        raise AssertionError("Notification icon not found in nav bar")

    def get_notification_badge_count(self) -> int:
        """Get the unread notification count from the badge (span.number-badge). Returns 0 if no badge."""
        try:
            badge = self.driver.find_element(By.CSS_SELECTOR, "span.number-badge")
            if badge.is_displayed():
                return int(badge.text.strip())
        except Exception:
            pass
        return 0

    def click_viewed_on_notification_dropdown(self, message_substring: str, timeout: int = 10):
        """Click Viewed on the notification with the given message in the dropdown (opened by clicking notification icon)."""
        for viewed_xpath in [
            f"//span[contains(@class,'notification-message') and contains(., '{message_substring}')]/ancestor::*[.//button[contains(@class,'viewed-btn')]][1]//button[contains(@class,'viewed-btn')]",
            f"//*[contains(., '{message_substring}')]/ancestor::*[.//button[contains(., 'Viewed')]][1]//button[contains(., 'Viewed')]",
            f"//*[contains(., '{message_substring}')]/following::button[contains(@class,'viewed-btn')][1]",
            f"//button[contains(@class,'viewed-btn')][ancestor::*[contains(., '{message_substring}')]]",
        ]:
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, viewed_xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                self.driver.execute_script("arguments[0].click();", el)
                time.sleep(0.5)
                return
            except Exception:
                continue
        raise AssertionError(f"Viewed button not found for notification '{message_substring}'")

    def click_check_later(self, timeout: int = 5) -> bool:
        """
        If the notification popup is visible, click 'Check Later' to dismiss it.
        Returns True if clicked, False if popup/button not found (no notifications).
        Use when agent logs in - popup may or may not appear.
        """
        for xpath in [
            "//button[contains(., 'Check Later')]",
            "//*[contains(@class,'btn')][contains(., 'Check Later')]",
            "//*[normalize-space()='Check Later']",
        ]:
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                if el.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    self.driver.execute_script("arguments[0].click();", el)
                    time.sleep(0.5)
                    return True
            except Exception:
                continue
        return False
