"""Page object for User Management (Management > Users): add user, search, delete."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


class UserManagementPage:
    """User management: All Users list, New User form, search, delete."""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self._wait = WebDriverWait(driver, 15)

    def open_users_page(self, users_url: str):
        """Navigate to the Users management page."""
        self.driver.get(users_url)
        self._wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'All Users') or contains(text(), 'Users')]")))

    def click_new_user(self, create_url: str = None):
        """Click the 'New User' button and wait for the create form (/admin/user/create)."""
        btn = self._wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'New User')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        if create_url and "/admin/user/create" in create_url:
            self._wait.until(lambda d: "/admin/user/create" in d.current_url)
        self._wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Create a New User')]")))

    def _input_by_label(self, label_text: str):
        """Find input/field by its label text (e.g. 'User name', 'First name')."""
        try:
            label = self.driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]")
            for_id = label.get_attribute("for")
            if for_id:
                return self.driver.find_element(By.ID, for_id)
            parent = label.find_element(By.XPATH, "..")
            inp = parent.find_elements(By.XPATH, ".//input[not(@type='hidden')] | .//*[contains(@class,'p-inputtext')] | .//p-password//input")
            if inp:
                return inp[0]
            return label.find_element(By.XPATH, "./following::input[1] | ./following::*[contains(@class,'p-inputtext')][1]")
        except Exception:
            pass
        inputs = self.driver.find_elements(By.XPATH, f"//input[contains(@placeholder, '{label_text}') or contains(@name, '{label_text.replace(' ', '').lower()}')]")
        return inputs[0] if inputs else None

    def _select_project(self, project_name: str):
        """Open the Projects dropdown menu, then click the option matching project_name (e.g. 'Legal'). Required field."""
        import time
        # 1) Open the Projects menu: click the label's following multiselect/dropdown trigger
        for trigger_xpath in [
            "//label[contains(., 'Projects')]/following::*[contains(@class,'p-multiselect')][1]",
            "//label[contains(., 'Projects')]/following::*[contains(@class,'p-dropdown') or @role='combobox'][1]",
            "//*[contains(@class,'p-multiselect') and .//*[contains(@class,'p-multiselect-label')]]",
        ]:
            try:
                trigger = self.driver.find_element(By.XPATH, trigger_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                break
            except Exception:
                continue
        else:
            return
        # 2) Wait for the overlay panel to be visible (PrimeNG appends it to body)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel') or contains(@class,'p-overlay-panel')][contains(@class,'p-component') or contains(@class,'p-visible')]"
                ))
            )
        except TimeoutException:
            pass
        time.sleep(0.5)
        # 3) Click the option that contains the project name (e.g. "Legal") inside the panel
        for opt_xpath in [
            f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]//li[contains(., '{project_name}')]",
            f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]//*[@role='option'][contains(., '{project_name}')]",
            f"//*[contains(@class,'p-multiselect-item') or contains(@class,'p-dropdown-item')][contains(normalize-space(.), '{project_name}')]",
            f"//ul[contains(@class,'p-multiselect-list') or contains(@class,'p-dropdown-list')]//li[contains(., '{project_name}')]",
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

    def _select_role(self, role: str):
        """Select role. On edit page: if switching away from Admin, click Admin first to turn it off, then click the new role."""
        import time
        # When switching to Agency (or PM/Moderator), click Admin first to turn it off, then click the target role
        if role != "Admin":
            self._click_role_option("Admin")
            time.sleep(0.25)
        self._click_role_option(role)

    def _click_role_option(self, role: str):
        """Click a single role option (Admin, Agency, PM, Moderator). Toggles that option."""
        role_value = {"Admin": "1", "Agency": "2", "PM": "3", "Moderator": "4"}.get(role)
        if role_value:
            try:
                inp = self.driver.find_element(By.CSS_SELECTOR, f"input[name='userRole'][value='{role_value}']")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                self.driver.execute_script("arguments[0].click();", inp)
                return
            except Exception:
                pass
        try:
            label = self.driver.find_element(By.XPATH, f"//label[contains(@class,'radio')][.//*[contains(@class,'radio_text') and contains(., '{role}')]]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
            self.driver.execute_script("arguments[0].click();", label)
            return
        except Exception:
            pass
        try:
            label = self.driver.find_element(By.XPATH, f"//label[contains(@class,'radio')][contains(., '{role}')]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
            self.driver.execute_script("arguments[0].click();", label)
        except Exception:
            pass

    def fill_new_user_form(
        self,
        user_name: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        role: str = "Admin",
        project: str = "Legal",
    ):
        """Fill all required fields on Create a New User form: User name, First name, Last name, User email, Password, Confirm password, Projects, Role, Active."""
        self._wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Create a New User')]")))
        for label, value in [
            ("User name", user_name),
            ("First name", first_name),
            ("Last name", last_name),
            ("User email", email),
        ]:
            el = self._input_by_label(label)
            if el and el.is_displayed():
                el.clear()
                el.send_keys(value)
        password_el = self._input_by_label("Password")
        if password_el:
            password_el.clear()
            password_el.send_keys(password)
        confirm_el = self._input_by_label("Confirm password")
        if confirm_el:
            confirm_el.clear()
            confirm_el.send_keys(password)
        try:
            pwd_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input.p-password-input")
            if len(pwd_inputs) >= 2:
                pwd_inputs[1].clear()
                pwd_inputs[1].send_keys(password)
        except Exception:
            pass
        self._select_project(project)
        import time
        time.sleep(0.3)
        self._select_role(role)
        time.sleep(0.3)
        self._set_active_toggle(on=True)

    def _set_active_toggle(self, on: bool = True):
        """Turn the Active toggle ON or OFF. Uses input[formcontrolname='isActive'] or label.switch."""
        import time
        checkbox = None
        try:
            checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='isActive']")
        except Exception:
            try:
                checkbox = self.driver.find_element(By.XPATH, "//input[@formcontrolname='isActive']")
            except Exception:
                pass
        if checkbox:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                time.sleep(0.2)
                selected = checkbox.is_selected()
                if on and not selected:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                elif not on and selected:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.3)
                return
            except Exception:
                pass
        label = None
        try:
            label = self.driver.find_element(By.XPATH, "//label[contains(@class,'switch')][.//input[@formcontrolname='isActive']]")
        except Exception:
            try:
                label = self.driver.find_element(By.CSS_SELECTOR, "label.switch")
            except Exception:
                pass
        if label:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                time.sleep(0.2)
                inp = self.driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='isActive']")
                selected = inp.is_selected()
                if (on and not selected) or (not on and selected):
                    ActionChains(self.driver).move_to_element(label).click().perform()
                time.sleep(0.3)
            except Exception:
                pass

    def click_save_user(self):
        """Click the Save button on the new user form. Uses short wait (5s) per selector so the step is fast."""
        short_wait = WebDriverWait(self.driver, 5)
        for by, value in [
            (By.XPATH, "//form//button[contains(., 'Save') and not(contains(., 'Cancel'))]"),
            (By.CSS_SELECTOR, "form button.green-btn"),
            (By.XPATH, "//*[contains(text(), 'Create a New User')]//ancestor::form//button[contains(., 'Save')]"),
            (By.XPATH, "//button[normalize-space(.)='Save']"),
            (By.XPATH, "//button[contains(., 'Save')]"),
        ]:
            try:
                save_btn = short_wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", save_btn)
                return
            except TimeoutException:
                continue
        raise AssertionError("Save button not found on Create a New User form")

    def wait_for_edit_page(self):
        """Wait until the Update User (edit) page is loaded."""
        self._wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Update User')]")))

    def _set_projects_on_edit(self, deselect_names: list, select_names: list):
        """On edit page: open Projects dropdown, click to deselect then select the given project names (multiselect toggles)."""
        import time
        for trigger_xpath in [
            "//label[contains(., 'Projects')]/following::*[contains(@class,'p-multiselect')][1]",
            "//*[contains(@class,'p-multiselect') and .//*[contains(@class,'p-multiselect-label')]]",
        ]:
            try:
                trigger = self.driver.find_element(By.XPATH, trigger_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                break
            except Exception:
                continue
        else:
            return
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]"))
            )
        except TimeoutException:
            pass
        time.sleep(0.5)
        for project_name in deselect_names + select_names:
            for opt_xpath in [
                f"//*[contains(@class,'p-multiselect-panel') or contains(@class,'p-dropdown-panel')]//li[contains(., '{project_name}')]",
                f"//*[contains(@class,'p-multiselect-item') or contains(@class,'p-dropdown-item')][contains(normalize-space(.), '{project_name}')]",
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

    def fill_edit_user_form(
        self,
        user_name: str,
        first_name: str,
        last_name: str,
        email: str,
        role: str,
        deselect_projects: list,
        select_projects: list,
    ):
        """Fill the Update User form: new name/email/first/last, projects (deselect then select), role, Active OFF, then Save."""
        import time
        self.wait_for_edit_page()
        for label, value in [
            ("User name", user_name),
            ("User email", email),
            ("First name", first_name),
            ("Last name", last_name),
        ]:
            el = self._input_by_label(label)
            if el and el.is_displayed():
                el.clear()
                el.send_keys(value)
        time.sleep(0.2)
        self._set_projects_on_edit(deselect_projects, select_projects)
        time.sleep(0.3)
        self._select_role(role)
        time.sleep(0.3)
        self._set_active_toggle(on=False)
        time.sleep(0.2)
        self._click_save_on_edit_page()

    def _click_save_on_edit_page(self):
        """Click Save on the Update User (edit) page. Uses short wait (5s) per selector so the step is fast."""
        short_wait = WebDriverWait(self.driver, 5)
        for by, value in [
            (By.XPATH, "//form//button[contains(., 'Save') and not(contains(., 'Cancel'))]"),
            (By.CSS_SELECTOR, "form button.green-btn"),
            (By.XPATH, "//*[contains(text(), 'Update User')]//ancestor::form//button[contains(., 'Save')]"),
            (By.XPATH, "//form[.//*[contains(text(), 'Update User')]]//button[contains(., 'Save')]"),
            (By.XPATH, "//button[normalize-space(.)='Save']"),
            (By.XPATH, "//button[contains(., 'Save')]"),
        ]:
            try:
                save_btn = short_wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", save_btn)
                return
            except TimeoutException:
                continue
        raise AssertionError("Save button not found on Update User form")

    def wait_back_on_users_list(self, users_list_url: str = None):
        """Wait until we're back on the users list (no /create, no /edit), or navigate there if not."""
        try:
            self._wait.until(lambda d: "/admin/user" in d.current_url and "/create" not in d.current_url and "/edit" not in d.current_url)
        except TimeoutException:
            if users_list_url:
                self.driver.get(users_list_url)
                self._wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'All Users') or contains(text(), 'Users')]")))
            else:
                raise
        import time
        time.sleep(1.5)

    def show_inactive_users(self):
        """Turn on the 'Show inactive' toggle that is directly under the Search box (not the Status toggles in the table)."""
        import time
        # The correct switch is the one under the Search box: first label.switch that appears AFTER the search input in the DOM (before the table)
        search_input = None
        for xpath in [
            "//input[@placeholder='Search']",
            "//input[contains(@placeholder, 'Search')]",
            "//*[contains(text(), 'All Users')]//following::input[1]",
        ]:
            try:
                search_input = self.driver.find_element(By.XPATH, xpath)
                if search_input.is_displayed():
                    break
            except Exception:
                continue
        if not search_input:
            return
        # First label.switch after the search input = the "Show inactive" filter (table Status toggles come later)
        try:
            switch = search_input.find_element(By.XPATH, "./following::label[contains(@class,'switch')][1]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
            time.sleep(0.25)
            if not switch.find_element(By.XPATH, ".//input[@type='checkbox']").is_selected():
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

    def search_user(self, user_name: str, users_list_url: str = None):
        """Type the username in the Search field (active users only; do not use Show inactive)."""
        self.wait_back_on_users_list(users_list_url=users_list_url)
        self._type_search(user_name, wait_after_sec=3)

    def _type_search(self, user_name: str, wait_after_sec: float = 2):
        """Find search input, clear, type username, wait. Caller ensures we're on the users list."""
        import time
        for xpath in [
            "//input[@placeholder='Search']",
            "//input[contains(@placeholder, 'Search')]",
            "//*[contains(text(), 'All Users')]//following::input[1]",
            "//input[@type='text' and contains(@class, 'search') or contains(@class, 'filter')]",
        ]:
            try:
                search_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if search_input.is_displayed():
                    search_input.clear()
                    search_input.send_keys(user_name)
                    time.sleep(wait_after_sec)
                    return
            except TimeoutException:
                continue
        raise AssertionError("Search input not found on users list")

    def search_user_after_delete(self, user_name: str):
        """Re-run search after delete to refresh the list. Short wait."""
        self._type_search(user_name, wait_after_sec=0.8)

    def _row_xpaths(self, user_name: str):
        """XPath list to find a table row containing the given username. First row first when filtered."""
        return [
            f"//tbody//tr[1][.//*[contains(text(), '{user_name}')]]",
            f"//tbody//tr[.//*[contains(text(), '{user_name}')]]",
            f"//table//tr[contains(., '{user_name}')]",
            f"//*[@role='table']//*[@role='row']//*[contains(text(), '{user_name}')]",
        ]

    def is_user_in_table(self, user_name: str) -> bool:
        """Return True if a row containing this username exists in the table (checks first row first when search is applied)."""
        for xpath in self._row_xpaths(user_name):
            try:
                el = self.driver.find_element(By.XPATH, xpath)
                return el.is_displayed()
            except Exception:
                continue
        return False

    def verify_user_deleted(self, user_name: str, timeout: float = 4):
        """After delete: type name in search, then pass as soon as no row with that name is found (polls every 0.25s)."""
        import time
        self._type_search(user_name, wait_after_sec=0.5)
        poll_interval = 0.25
        elapsed = 0.0
        while elapsed < timeout:
            if not self.is_user_in_table(user_name):
                return
            time.sleep(poll_interval)
            elapsed += poll_interval
        assert not self.is_user_in_table(user_name), f"User '{user_name}' should not be in table after deletion"

    def wait_for_user_row_gone(self, user_name: str, timeout: int = 8):
        """Wait until no row with this username is in the table (e.g. after delete). Faster than re-searching."""
        def row_gone(driver):
            for xpath in self._row_xpaths(user_name):
                try:
                    if driver.find_element(By.XPATH, xpath).is_displayed():
                        return False
                except Exception:
                    pass
            return True
        WebDriverWait(self.driver, timeout, poll_frequency=0.25).until(row_gone)

    def click_user_name_to_edit(self, user_name: str):
        """Find the row with this username and click the <a href="/admin/user/{id}/edit"> link to open the edit page."""
        row = self._wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//tr[contains(., '{user_name}')] | //*[@role='row'][contains(., '{user_name}')] | //tbody//tr[.//*[contains(text(), '{user_name}')]]"
            ))
        )
        # Real DOM: <td><a href="/admin/user/4182/edit" class="text-decoration-none">username</a></td>
        link = None
        for xpath in [
            ".//a[contains(@href, '/admin/user/') and contains(@href, '/edit')]",
            f".//a[contains(text(), '{user_name}')]",
            ".//td//a[contains(@href, '/edit')]",
            f".//*[contains(text(), '{user_name}') and self::a]",
        ]:
            try:
                link = row.find_element(By.XPATH, xpath)
                if link.is_displayed():
                    break
            except Exception:
                continue
        if not link:
            link = row.find_element(By.XPATH, f".//*[contains(text(), '{user_name}')]")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        self.driver.execute_script("arguments[0].click();", link)
        self._wait.until(lambda d: "/admin/user/" in d.current_url and "/edit" in d.current_url)

    def delete_user_row(self, user_name: str):
        """Find the row with this username and click the trash icon (img with alt='Remove'), then confirm in the modal."""
        row = self._wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//tr[contains(., '{user_name}')] | //*[@role='row'][contains(., '{user_name}')] | //tbody//tr[.//*[contains(text(), '{user_name}')]]"
            ))
        )
        # Real DOM: <td class="cursor-pointer"> <img src="assets/icons/attatchment-delete.svg" alt="Remove" data-bs-toggle="modal" ...>
        trash = None
        for by, value in [
            (By.CSS_SELECTOR, "img[alt='Remove']"),
            (By.CSS_SELECTOR, "img[src*='attatchment-delete']"),
            (By.XPATH, ".//td[contains(@class,'cursor-pointer')]//img"),
            (By.XPATH, ".//img[@alt='Remove']"),
        ]:
            try:
                trash = row.find_element(by, value)
                break
            except Exception:
                continue
        if not trash:
            trash = row.find_element(By.XPATH, ".//*[contains(@class, 'trash') or contains(@class, 'delete')] | .//*[@title='Delete' or @aria-label='Delete']")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trash)
        self.driver.execute_script("arguments[0].click();", trash)
        self._confirm_delete_modal()

    def _confirm_delete_modal(self):
        """Trash opens a Bootstrap modal. Click the green 'Delete' button (button.green-btn) to confirm."""
        try:
            # Wait for modal to be visible (Bootstrap .modal.show or modal backdrop)
            WebDriverWait(self.driver, 8).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show .action-btns, .modal.show button.green-btn, [id^='delete_user_']"))
            )
        except TimeoutException:
            pass
        import time
        time.sleep(0.4)
        # Real DOM: <button type="button" class="green-btn"> Delete </button> inside div.action-btns
        for by, value in [
            (By.CSS_SELECTOR, ".modal.show button.green-btn"),
            (By.CSS_SELECTOR, ".modal button.green-btn"),
            (By.XPATH, "//div[contains(@class,'action-btns')]//button[contains(@class,'green-btn')]"),
            (By.XPATH, "//button[contains(@class,'green-btn') and (contains(., 'Delete') or normalize-space(.)='Delete')]"),
            (By.XPATH, "//*[contains(@class,'modal')]//button[contains(., 'Delete')]"),
        ]:
            try:
                delete_btn = self.driver.find_element(by, value)
                if delete_btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_btn)
                    time.sleep(0.2)
                    self.driver.execute_script("arguments[0].click();", delete_btn)
                    time.sleep(0.3)
                    return
            except Exception:
                continue
        try:
            delete_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Delete')]"))
            )
            self.driver.execute_script("arguments[0].click();", delete_btn)
        except TimeoutException:
            pass
