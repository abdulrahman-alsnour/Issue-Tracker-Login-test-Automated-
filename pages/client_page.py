"""Page object for Client management (/admin/client)."""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ClientPage:
    """Client management: All Clients list and Create New Client form."""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self._wait = WebDriverWait(driver, 15)

    def open_clients_page(self, url: str):
        """Navigate to the client management page."""
        self.driver.get(url)
        self._wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'All Clients') or contains(text(), 'Clients')]"
            ))
        )

    def click_new_client(self):
        """Click the 'New Client' button to open the Create New Client form."""
        for by, value in [
            (By.XPATH, "//*[contains(text(), 'New Client')]"),
            (By.XPATH, "//button[contains(., 'New Client')]"),
            (By.XPATH, "//*[contains(@class,'btn')][contains(., 'New Client')]"),
        ]:
            try:
                btn = self._wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
                return
            except Exception:
                continue
        raise AssertionError("New Client button not found")

    def wait_for_create_client_form(self, timeout: int = 8):
        """Wait until the 'Create New Client' form is visible."""
        self._wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'Create New Client')]"
            ))
        )
        time.sleep(0.3)

    def fill_client_name(self, name: str):
        """Fill the Client Name input field."""
        for xpath in [
            "//label[contains(., 'Client Name')]/following::input[1]",
            "//*[contains(text(), 'Client Name')]/following::input[1]",
            "//input[contains(@placeholder,'Client') or @formcontrolname='name']",
        ]:
            try:
                inp = self.driver.find_element(By.XPATH, xpath)
                if inp.is_displayed():
                    inp.clear()
                    inp.send_keys(name)
                    return
            except Exception:
                continue
        raise AssertionError("Client Name input not found")

    def toggle_active(self, on: bool = True):
        """Turn the Active toggle on or off."""
        for switch_xpath in [
            "//*[contains(normalize-space(.), 'Active')]/preceding-sibling::label[contains(@class,'switch')][1]",
            "//label[contains(@class,'switch')][following-sibling::*[contains(., 'Active')]][1]",
            "//*[contains(text(), 'Create New Client')]//following::label[contains(@class,'switch')][1]",
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
        raise AssertionError("Active toggle not found on Create New Client form")

    def click_save(self):
        """Click the Save button on the Create New Client form."""
        for by, value in [
            (By.XPATH, "//*[contains(text(), 'Create New Client')]//ancestor::form//button[contains(., 'Save')]"),
            (By.XPATH, "//form//button[contains(., 'Save') and not(contains(., 'Cancel'))]"),
            (By.XPATH, "//button[contains(., 'Save')]"),
        ]:
            try:
                btn = self.driver.find_element(by, value)
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    self.driver.execute_script("arguments[0].click();", btn)
                    return
            except Exception:
                continue
        raise AssertionError("Save button not found on Create New Client form")
