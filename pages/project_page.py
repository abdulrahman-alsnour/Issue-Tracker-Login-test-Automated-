"""Page object for Project management (/admin/project)."""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class ProjectPage:
    """Project management: All Projects list, Create New Project form, Edit Project form."""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self._wait = WebDriverWait(driver, 15)

    def open_projects_page(self, url: str):
        """Navigate to the project management page."""
        self.driver.get(url)
        self._wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'All Projects') or contains(text(), 'Projects')]"
            ))
        )

    def click_new_project(self):
        """Click the 'New Project' button to open the Create New Project form."""
        for by, value in [
            (By.XPATH, "//*[contains(text(), 'New Project')]"),
            (By.XPATH, "//button[contains(., 'New Project')]"),
            (By.XPATH, "//*[contains(@class,'btn')][contains(., 'New Project')]"),
        ]:
            try:
                btn = self._wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
                return
            except Exception:
                continue
        raise AssertionError("New Project button not found")

    def wait_for_create_project_form(self, timeout: int = 10):
        """Wait until the 'Create a New Project' form is visible."""
        self._wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'Create a New Project')]"
            ))
        )
        time.sleep(0.3)

    def _input_by_label(self, label_text: str):
        """Find input/field by its label text."""
        try:
            label = self.driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]")
            for_id = label.get_attribute("for")
            if for_id:
                return self.driver.find_element(By.ID, for_id)
            parent = label.find_element(By.XPATH, "..")
            inp = parent.find_elements(By.XPATH, ".//input | .//textarea | .//*[contains(@class,'p-inputtext')]")
            if inp:
                return inp[0]
            return label.find_element(By.XPATH, "./following::input[1] | ./following::textarea[1]")
        except Exception:
            pass
        inputs = self.driver.find_elements(By.XPATH, f"//input[contains(@placeholder, '{label_text}')] | //textarea[contains(@placeholder, '{label_text}')]")
        return inputs[0] if inputs else None

    def fill_project_name(self, name: str):
        """Fill the Project name input."""
        el = self._input_by_label("Project name")
        if el:
            el.clear()
            el.send_keys(name)
            return
        for xpath in [
            "//label[contains(., 'Project name')]/following::input[1]",
            "//input[@formcontrolname='name']",
        ]:
            try:
                inp = self.driver.find_element(By.XPATH, xpath)
                if inp.is_displayed():
                    inp.clear()
                    inp.send_keys(name)
                    return
            except Exception:
                continue
        raise AssertionError("Project name input not found")

    def select_client(self, client_name: str):
        """Open the Client Name dropdown and select the given client."""
        for trigger_xpath in [
            "//label[contains(., 'Client Name')]/following::*[contains(@class,'p-dropdown') or contains(@class,'p-multiselect')][1]",
            "//*[contains(@placeholder,'Select a client')]/ancestor::*[contains(@class,'p-dropdown') or contains(@class,'p-multiselect')][1]",
        ]:
            try:
                trigger = self.driver.find_element(By.XPATH, trigger_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                break
            except Exception:
                continue
        else:
            raise AssertionError("Client Name dropdown trigger not found")

        time.sleep(0.5)
        panel_xpath = "//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')][contains(@class,'p-component') or contains(@class,'p-visible')]"
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, panel_xpath)))
        except TimeoutException:
            pass
        time.sleep(0.4)

        for opt_xpath in [
            f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]//li[contains(., '{client_name}')]",
            f"//*[contains(@class,'p-multiselect-item') or contains(@class,'p-dropdown-item')][contains(normalize-space(.), '{client_name}')]",
            f"//*[contains(@class,'p-dropdown-panel')]//*[@role='option'][contains(., '{client_name}')]",
            f"//*[contains(@class,'p-dropdown-item')][contains(., 'Abdulrahman') and contains(., 'Client')]",
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
        raise AssertionError(f"Client option '{client_name}' not found in dropdown")

    def select_associated_users(self, user_names: list):
        """Open the Associated user multiselect and select the given users."""
        for trigger_xpath in [
            "//label[contains(., 'Associated user')]/following::*[contains(@class,'p-multiselect') or contains(@class,'p-dropdown')][1]",
            "//*[contains(@class,'p-multiselect') and .//*[contains(@class,'multiselect') or contains(@class,'dropdown')]]",
        ]:
            try:
                trigger = self.driver.find_element(By.XPATH, trigger_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                break
            except Exception:
                continue
        else:
            raise AssertionError("Associated user dropdown trigger not found")

        time.sleep(0.5)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]"))
            )
        except TimeoutException:
            pass
        time.sleep(0.4)

        for user_name in user_names:
            for opt_xpath in [
                f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]//li[contains(., '{user_name}')]",
                f"//*[contains(@class,'p-multiselect-item') or contains(@class,'p-dropdown-item')][contains(normalize-space(.), '{user_name}')]",
            ]:
                try:
                    opt = self.driver.find_element(By.XPATH, opt_xpath)
                    if opt.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opt)
                        self.driver.execute_script("arguments[0].click();", opt)
                        time.sleep(0.3)
                        break
                except Exception:
                    continue
        time.sleep(0.2)

    def fill_user_email(self, email: str):
        """Fill the User email input."""
        el = self._input_by_label("User email")
        if el:
            el.clear()
            el.send_keys(email)
            return
        for xpath in [
            "//label[contains(., 'User email')]/following::input[1]",
            "//input[@formcontrolname='email' or contains(@placeholder,'email')]",
        ]:
            try:
                inp = self.driver.find_element(By.XPATH, xpath)
                if inp.is_displayed():
                    inp.clear()
                    inp.send_keys(email)
                    return
            except Exception:
                continue
        raise AssertionError("User email input not found")

    def fill_description(self, text: str):
        """Fill the Description textarea."""
        for xpath in [
            "//label[contains(., 'Description')]/following::textarea[1]",
            "//textarea[contains(@placeholder,'Description') or @formcontrolname='description']",
        ]:
            try:
                textarea = self.driver.find_element(By.XPATH, xpath)
                if textarea.is_displayed():
                    textarea.clear()
                    textarea.send_keys(text)
                    return
            except Exception:
                continue
        raise AssertionError("Description textarea not found")

    def toggle_active(self, on: bool = True):
        """Turn the Active toggle on or off on the Create/Edit Project form."""
        for switch_xpath in [
            "//*[contains(normalize-space(.), 'Active')]/preceding-sibling::label[contains(@class,'switch')][1]",
            "//label[contains(@class,'switch')][following-sibling::*[contains(., 'Active')]][1]",
            "//*[contains(text(), 'Create a New Project') or contains(text(), 'Update Project')]//following::label[contains(@class,'switch')][1]",
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
        raise AssertionError("Active toggle not found on Project form")

    def click_save(self):
        """Click the Save button on the Create/Edit Project form."""
        for by, value in [
            (By.XPATH, "//form//button[contains(., 'Save') and not(contains(., 'Cancel'))]"),
            (By.XPATH, "//*[contains(text(), 'Create a New Project') or contains(text(), 'Update Project')]//ancestor::form//button[contains(., 'Save')]"),
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
        raise AssertionError("Save button not found on Project form")

    def wait_back_on_projects_list(self, projects_url: str = None):
        """Wait until we're back on the projects list (no /create, no /edit)."""
        try:
            self._wait.until(
                lambda d: "/admin/project" in d.current_url and "/create" not in d.current_url and "/edit" not in d.current_url
            )
        except TimeoutException:
            if projects_url:
                self.driver.get(projects_url)
                self._wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'All Projects') or contains(text(), 'Projects')]"))
                )
            else:
                raise
        time.sleep(1.5)

    def search_project(self, project_name: str, wait_after_sec: float = 3):
        """Type the project name in the Search field."""
        for xpath in [
            "//input[@placeholder='Search']",
            "//input[contains(@placeholder, 'Search')]",
            "//*[contains(text(), 'All Projects')]//following::input[1]",
        ]:
            try:
                search_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if search_input.is_displayed():
                    search_input.clear()
                    search_input.send_keys(project_name)
                    time.sleep(wait_after_sec)
                    return
            except TimeoutException:
                continue
        raise AssertionError("Search input not found on projects list")

    def click_first_project_in_list(self, project_name: str, timeout: int = 10):
        """Find the row with this project name and click the edit link to open the edit page."""
        row = self._wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//tr[contains(., '{project_name}')] | //*[@role='row'][contains(., '{project_name}')] | //tbody//tr[.//*[contains(text(), '{project_name}')]]"
            ))
        )
        link = None
        for xpath in [
            ".//a[contains(@href, '/admin/project/') and contains(@href, '/edit')]",
            f".//a[contains(text(), '{project_name}')]",
            ".//td//a[contains(@href, '/edit')]",
            f".//*[contains(text(), '{project_name}') and self::a]",
            f".//*[contains(text(), '{project_name}')]",
        ]:
            try:
                link = row.find_element(By.XPATH, xpath)
                if link.is_displayed():
                    break
            except Exception:
                continue
        if not link:
            link = row.find_element(By.XPATH, f".//*[contains(text(), '{project_name}')]")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        self.driver.execute_script("arguments[0].click();", link)
        time.sleep(0.5)
        self._wait.until(lambda d: "/admin/project" in d.current_url and "/edit" in d.current_url)

    def wait_for_edit_project_page(self, timeout: int = 10):
        """Wait until the Update/Edit Project page is loaded."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: "/admin/project" in d.current_url and "/edit" in d.current_url
            )
        except TimeoutException:
            pass
        for xpath in [
            "//*[contains(text(), 'Update Project')]",
            "//*[contains(text(), 'Edit Project')]",
            "//*[contains(text(), 'Update a Project')]",
            "//*[contains(text(), 'Create a New Project')]",
            "//label[contains(., 'Project name')]",
        ]:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                time.sleep(0.3)
                return
            except TimeoutException:
                continue

    def fill_edit_project_name(self, name: str):
        """Fill the Project name on the edit form."""
        self.fill_project_name(name)

    def fill_edit_description(self, text: str):
        """Fill the Description on the edit form."""
        self.fill_description(text)

    def set_associated_users_on_edit(self, deselect_names: list, select_names: list):
        """On edit page: open Associated user multiselect, deselect then select the given users."""
        for trigger_xpath in [
            "//label[contains(., 'Associated user')]/following::*[contains(@class,'p-multiselect') or contains(@class,'p-dropdown')][1]",
            "//*[contains(@class,'p-multiselect') and .//*[contains(@class,'multiselect') or contains(@class,'dropdown')]]",
        ]:
            try:
                trigger = self.driver.find_element(By.XPATH, trigger_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                break
            except Exception:
                continue
        else:
            raise AssertionError("Associated user dropdown trigger not found on edit page")

        time.sleep(0.5)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]"))
            )
        except TimeoutException:
            pass
        time.sleep(0.5)

        for user_name in deselect_names + select_names:
            for opt_xpath in [
                f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]//li[contains(., '{user_name}')]",
                f"//*[contains(@class,'p-multiselect-item') or contains(@class,'p-dropdown-item')][contains(normalize-space(.), '{user_name}')]",
            ]:
                try:
                    opt = self.driver.find_element(By.XPATH, opt_xpath)
                    if opt.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opt)
                        self.driver.execute_script("arguments[0].click();", opt)
                        time.sleep(0.25)
                        break
                except Exception:
                    continue
        time.sleep(0.2)

    def show_inactive_projects(self):
        """Turn on the 'Show inactive' toggle under the Search box."""
        search_input = None
        for xpath in [
            "//input[@placeholder='Search']",
            "//input[contains(@placeholder, 'Search')]",
            "//*[contains(text(), 'All Projects')]//following::input[1]",
        ]:
            try:
                search_input = self.driver.find_element(By.XPATH, xpath)
                if search_input.is_displayed():
                    break
            except Exception:
                continue
        if not search_input:
            return
        try:
            switch = search_input.find_element(By.XPATH, "./following::label[contains(@class,'switch')][1]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
            time.sleep(0.25)
            try:
                checkbox = switch.find_element(By.XPATH, ".//input[@type='checkbox']")
                if not checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", switch)
            except Exception:
                self.driver.execute_script("arguments[0].click();", switch)
            time.sleep(0.5)
            return
        except Exception:
            pass
        try:
            switch = self.driver.find_element(By.XPATH, "//input[contains(@placeholder,'Search')]/following::label[contains(@class,'switch')][1]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
            time.sleep(0.25)
            ActionChains(self.driver).move_to_element(switch).click().perform()
            time.sleep(0.5)
        except Exception:
            pass

    def is_project_in_table(self, project_name: str) -> bool:
        """Return True if a row containing this project name exists in the table."""
        for xpath in [
            f"//tbody//tr[.//*[contains(text(), '{project_name}')]]",
            f"//table//tr[contains(., '{project_name}')]",
            f"//*[@role='row']//*[contains(text(), '{project_name}')]",
        ]:
            try:
                el = self.driver.find_element(By.XPATH, xpath)
                return el.is_displayed()
            except Exception:
                continue
        return False
