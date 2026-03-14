"""Page object for the Issue Tracker dashboard (/issue) and report ticket flow."""

import re
import time
from datetime import date
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IssuePage:
    """Issue dashboard and Report a New Ticket create form."""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self._wait = WebDriverWait(driver, 15)

    def wait_for_issue_page(self, timeout: int = 15):
        """Wait until we're on the issue page (URL contains /issue)."""
        WebDriverWait(self.driver, timeout).until(EC.url_contains("/issue"))
        self._wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Report a New Ticket') or contains(text(), 'Issue Tracker')]"))
        )

    def click_report_new_ticket(self):
        """Click the 'Report a New Ticket' button. Real DOM: <a class='report-btn' href='/issue/create'>."""
        for by, value in [
            (By.CSS_SELECTOR, "a.report-btn"),
            (By.XPATH, "//a[contains(@class,'report-btn')]"),
            (By.XPATH, "//a[@href='/issue/create']"),
            (By.XPATH, "//a[contains(., 'Report a New Ticket')]"),
        ]:
            try:
                btn = self._wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", btn)
                return
            except Exception:
                continue
        raise AssertionError("Report a New Ticket button not found")

    def wait_for_issue_create_page(self, timeout: int = 10, pause_seconds: float = 0):
        """Wait until we're on the create ticket page (URL contains /issue/create). Optionally pause after."""
        WebDriverWait(self.driver, timeout).until(EC.url_contains("/issue/create"))
        if pause_seconds > 0:
            time.sleep(pause_seconds)

    def _visible_dropdown_triggers(self):
        """Return visible PrimeNG dropdown triggers (div.p-dropdown)."""
        triggers = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'p-dropdown') and .//*[contains(@class,'p-dropdown-trigger') or contains(@class,'p-dropdown-label')]]",
        )
        return [t for t in triggers if t.is_displayed()]

    def _open_dropdown_trigger(self, trigger):
        """Open a dropdown by clicking its trigger. Accepts either the p-dropdown container or the trigger element."""
        # If we have the container (e.g. p-dropdown), click the actual trigger button inside it
        try:
            inner = trigger.find_element(
                By.XPATH,
                ".//*[contains(@class,'p-dropdown-trigger') or @aria-label='dropdown trigger']"
            )
            if inner.is_displayed():
                trigger = inner
        except Exception:
            pass
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
        try:
            self.driver.execute_script("arguments[0].click();", trigger)
        except Exception:
            trigger.click()
        time.sleep(0.4)

    def _wait_for_visible_dropdown_panel(self, timeout: int = 8):
        """Wait for the PrimeNG dropdown panel to be visible."""
        panel_locator = (
            By.XPATH,
            "//*[contains(@class,'p-dropdown-panel') and (contains(@class,'p-component') or @role='listbox')]",
        )
        panel = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(panel_locator))
        return panel

    def _select_option_from_open_panel(self, option_text: str, timeout: int = 10):
        """Select option from the currently open PrimeNG dropdown panel (optionlabel=name, text in span)."""
        panel = self._wait_for_visible_dropdown_panel(timeout=timeout)
        # PrimeNG: li.p-dropdown-item with span containing the label text (optionlabel="name")
        for option_xpath in [
            f".//li[contains(@class,'p-dropdown-item')]//span[contains(normalize-space(.), '{option_text}')]",
            f".//li[contains(@class,'p-dropdown-item')][contains(normalize-space(.), '{option_text}')]",
            f".//*[@role='option'][contains(., '{option_text}')]",
            f".//li[.//span[normalize-space()='{option_text}']]",
        ]:
            try:
                option = WebDriverWait(panel, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
                self.driver.execute_script("arguments[0].click();", option)
                try:
                    WebDriverWait(self.driver, 4).until(EC.invisibility_of_element(panel))
                except Exception:
                    pass
                return
            except Exception:
                continue
        raise AssertionError(f"Could not select option '{option_text}' from dropdown panel")

    def _open_dropdown_by_label_text(self, label_text: str):
        """Open a dropdown using its nearby label text (e.g. 'Project')."""
        trigger_xpath = (
            f"//*[contains(normalize-space(.), '{label_text}')]/following::*[contains(@class,'p-dropdown')][1]"
        )
        trigger = self._wait.until(EC.element_to_be_clickable((By.XPATH, trigger_xpath)))
        self._open_dropdown_trigger(trigger)
        return trigger

    def _select_dropdown_option_by_label(self, label_text: str, option_text: str):
        """Open dropdown near label_text and select option_text."""
        self._open_dropdown_by_label_text(label_text)
        self._select_option_from_open_panel(option_text)

    def select_project(self, project_name: str):
        """Select project from the 'Project *' dropdown (e.g. 'abdulrahman-project')."""
        self._wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Report a New Ticket')]")))
        self._select_dropdown_option_by_label("Project", project_name)

    def toggle_create_on_behalf_of(self, on: bool = True):
        """
        Turn on the 'Create on behalf of' toggle so the second dropdown appears.
        Uses same pattern as user_management_page._set_active_toggle and show_inactive_users:
        find label.switch (by text context or form), scroll, then ActionChains click.
        """
        # Scope everything under the create-ticket section so we never click unrelated toggles (e.g. night mode)
        header = self._wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(.), 'Report a New Ticket')]"))
        )

        # Same DOM as user management: <label class="switch"><input type="checkbox"><span class="slider"></span></label>
        # The label.switch is right next to the visible text "Create on behalf of".
        switch_label = self._find_switch_label_in_create_form(header, "Create on behalf of")

        if not switch_label:
            raise AssertionError("Create on behalf of toggle not found")

        self._toggle_switch_label(switch_label, on=on)

    def _find_switch_label_in_create_form(self, header, toggle_text: str):
        """Find the correct label.switch in the create-ticket form next to toggle_text."""
        for switch_xpath in [
            f".//following::label[contains(@class,'switch')][following-sibling::*[contains(normalize-space(.), '{toggle_text}')]][1]",
            f".//following::*[contains(normalize-space(.), '{toggle_text}')][1]/preceding-sibling::label[contains(@class,'switch')][1]",
            f".//following::*[contains(normalize-space(.), '{toggle_text}')][1]/ancestor::*[.//label[contains(@class,'switch')]][1]//label[contains(@class,'switch')][1]",
        ]:
            try:
                el = header.find_element(By.XPATH, switch_xpath)
                if el.is_displayed():
                    return el
            except Exception:
                continue
        return None

    def _toggle_switch_label(self, switch_label, on: bool = True):
        """Toggle a label.switch to ON/OFF using the proven click pattern."""
        checkbox = None
        try:
            checkbox = switch_label.find_element(By.XPATH, ".//input[@type='checkbox']")
        except Exception:
            checkbox = None

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

        # 1) Try JS click on checkbox (same as _set_active_toggle)
        if checkbox:
            try:
                self.driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.3)
                if is_checked() == on:
                    return
            except Exception:
                pass

        # 2) JS click on the label (same as show_inactive_users first try)
        try:
            self.driver.execute_script("arguments[0].click();", switch_label)
            time.sleep(0.3)
            if is_checked() == on:
                return
        except Exception:
            pass

        # 3) ActionChains click (same as _set_active_toggle and show_inactive_users fallback)
        ActionChains(self.driver).move_to_element(switch_label).click().perform()
        time.sleep(0.3)

        try:
            if checkbox:
                WebDriverWait(self.driver, 6).until(lambda d: checkbox.is_selected() == on)
        except Exception:
            pass

    def select_create_on_behalf_of(self, option_text: str):
        """
        After turning on 'Create on behalf of', open the dropdown that appears under that toggle
        (formcontrolname="onBehalfOfUserId") and select the option (e.g. 'Abdulrahman-Agency').
        """
        # Target the on-behalf dropdown by form control so we never open the Project dropdown
        on_behalf_dropdown_xpath = (
            "//*[@formcontrolname='onBehalfOfUserId']"
            " | //*[contains(normalize-space(.), 'Report a New Ticket')]/following::*[contains(normalize-space(.), 'Create on behalf of')][1]/following::*[contains(@class,'p-dropdown')][1]"
        )
        dropdown_el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, on_behalf_dropdown_xpath))
        )
        self._open_dropdown_trigger(dropdown_el)
        self._select_option_from_open_panel(option_text)

    def fill_ticket_title(self, title: str):
        """Fill the Ticket title input (id='ticketTitle', formcontrolname='title')."""
        title_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input#ticketTitle, input[formcontrolname='title']")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_input)
        try:
            title_input.clear()
        except Exception:
            pass
        title_input.send_keys(title)

    def toggle_related_ticket(self, on: bool = True):
        """Turn on the 'Related ticket' toggle so the related ticket dropdown appears."""
        header = self._wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(.), 'Report a New Ticket')]"))
        )
        switch_label = self._find_switch_label_in_create_form(header, "Related ticket")
        if not switch_label:
            raise AssertionError("Related ticket toggle not found")
        self._toggle_switch_label(switch_label, on=on)

    def select_related_ticket(self, option_text: str):
        """Select a related ticket from the dropdown (formcontrolname='relatedIssueId')."""
        related_dropdown_xpath = (
            "//*[@formcontrolname='relatedIssueId']"
            " | //*[contains(normalize-space(.), 'Report a New Ticket')]/following::*[contains(normalize-space(.), 'Related ticket')][1]/following::*[contains(@class,'p-dropdown')][1]"
        )
        dropdown_el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, related_dropdown_xpath))
        )
        self._open_dropdown_trigger(dropdown_el)
        self._select_option_from_open_panel(option_text)

    def click_next(self, timeout: int = 10):
        """Click the Next button on the create ticket wizard (waits until enabled)."""
        next_btn = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(@class,'next-btn') and normalize-space(.)='Next']"
                    " | //button[normalize-space(.)='Next']",
                )
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)

        def is_enabled(el) -> bool:
            disabled_attr = el.get_attribute("disabled")
            aria_disabled = el.get_attribute("aria-disabled")
            if disabled_attr is not None:
                return False
            if aria_disabled is not None and aria_disabled.strip().lower() == "true":
                return False
            return el.is_enabled()

        WebDriverWait(self.driver, timeout).until(lambda d: is_enabled(next_btn))
        try:
            self.driver.execute_script("arguments[0].click();", next_btn)
        except Exception:
            next_btn.click()

    def _select_radio_option_by_name(self, group_name: str, option_text: str, timeout: int = 5):
        """Select a radio option by input[name] and label text. Fast path: click label once."""
        label_xpath = (
            f"//label[contains(@class,'radio')][.//input[@type='radio' and @name='{group_name}']]"
            f"[contains(normalize-space(.), '{option_text}')]"
        )
        label = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, label_xpath))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
        inp = label.find_element(By.XPATH, ".//input[@type='radio']")
        if inp.is_selected():
            return
        self.driver.execute_script("arguments[0].click();", label)
        try:
            WebDriverWait(self.driver, 2).until(lambda d: inp.is_selected())
            return
        except Exception:
            pass
        ActionChains(self.driver).move_to_element(label).click().perform()
        try:
            WebDriverWait(self.driver, 2).until(lambda d: inp.is_selected())
            return
        except Exception:
            pass
        self.driver.execute_script("arguments[0].click();", inp)
        WebDriverWait(self.driver, 2).until(lambda d: inp.is_selected())

    def select_category(self, category_text: str):
        """On step 2, select Category (e.g. Bug)."""
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(.), 'Category')]"))
        )
        self._select_radio_option_by_name("category", category_text, timeout=5)

    def select_severity(self, severity_text: str):
        """On step 2, select Severity (e.g. High)."""
        self._select_radio_option_by_name("severity", severity_text, timeout=5)

    def fill_description(self, text: str):
        """On step 3, fill 'Describe the issue *'."""
        el = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "textarea#description, textarea[formcontrolname='description']")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        try:
            el.clear()
        except Exception:
            pass
        el.send_keys(text)

    def fill_expected_behavior(self, text: str):
        """On step 3, fill 'Expected behavior *'."""
        # Best-effort selectors (DOM may vary); try by formcontrolname/id first, then by label text proximity.
        selectors = [
            (By.CSS_SELECTOR, "textarea#expectedBehavior, textarea[formcontrolname='expectedBehavior']"),
            (By.CSS_SELECTOR, "textarea[formcontrolname='expected'], textarea#expected"),
            (
                By.XPATH,
                "//*[contains(normalize-space(.), 'Expected behavior')]/following::textarea[1]",
            ),
        ]
        textarea = None
        for by, value in selectors:
            try:
                textarea = WebDriverWait(self.driver, 4).until(
                    EC.visibility_of_element_located((by, value))
                )
                break
            except Exception:
                continue
        if not textarea:
            raise AssertionError("Expected behavior textarea not found")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
        try:
            textarea.clear()
        except Exception:
            pass
        textarea.send_keys(text)

    def fill_additional_notes(self, text: str):
        """On the Additional notes step, fill the text area (placeholder: 'Add any additional information...')."""
        # Wait until we're on the Additional notes step
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(.), 'Additional notes')]"))
        )
        selectors = [
            (By.CSS_SELECTOR, "textarea[formcontrolname='additionalNotes']"),
            (By.CSS_SELECTOR, "textarea[placeholder*='additional']"),
            (By.CSS_SELECTOR, "textarea[placeholder*='Additional']"),
            (By.XPATH, "//*[contains(., 'Additional notes')]/following::textarea[1]"),
            (By.XPATH, "//label[contains(., 'Additional notes')]/following::textarea[1]"),
            (By.XPATH, "//textarea[contains(@placeholder, 'additional')]"),
        ]
        textarea = None
        for by, value in selectors:
            try:
                textarea = WebDriverWait(self.driver, 6).until(
                    EC.visibility_of_element_located((by, value))
                )
                if textarea and textarea.is_displayed():
                    break
            except Exception:
                continue
        if not textarea or not textarea.is_displayed():
            raise AssertionError("Additional notes textarea not found")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
        try:
            textarea.clear()
        except Exception:
            pass
        textarea.send_keys(text)

    def click_submit(self, timeout: int = 10):
        """On the review/summary page, click the Submit button."""
        submit_btn = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Submit') and not(contains(., 'Edit'))]")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        try:
            self.driver.execute_script("arguments[0].click();", submit_btn)
        except Exception:
            submit_btn.click()

    def wait_for_all_tickets_page(self, timeout: int = 15):
        """Wait until we're back on the issue list (URL has /issue but not /edit) and search bar is ready."""
        def on_list_page(driver):
            url = driver.current_url or ""
            if "/edit" in url:
                return False
            if "/issue" not in url:
                return False
            return True

        WebDriverWait(self.driver, timeout).until(on_list_page)
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(., 'All Tickets') or contains(., 'Search')]"))
        )
        # Wait for search input - it may load after the header (avoids flaky failures)
        for xpath in [
            "//input[contains(@placeholder, 'Search') or @placeholder='Search']",
            "//input[@type='search']",
            "//input[contains(@placeholder, 'search')]",
        ]:
            try:
                WebDriverWait(self.driver, timeout // 2).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                return
            except Exception:
                continue

    def click_filter_button(self, timeout: int = 10):
        """Click the filter button (filters-group icon). Sort button also has filter-group class, so target by img src."""
        for xpath in [
            "//button[.//img[contains(@src,'filters-group')]]",
            "//button[.//img[@alt='add']]",
            "//button[@class='filter-group'][.//img[contains(@src,'filters')]]",
        ]:
            try:
                btn = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
                return
            except Exception:
                continue
        raise AssertionError("Filter button not found")

    def _check_filter_checkbox(self, section_name: str, option_text: str, timeout: int = 5):
        """Check a checkbox in the filter panel under the given section (Category, Severity, Status)."""
        panel_xpath = "//div[contains(@class,'filter-panel') and contains(@class,'open')]"
        section_xpath = f"{panel_xpath}//h4[contains(normalize-space(.), '{section_name}')]/following-sibling::div[1]"
        for label_xpath in [
            f"{section_xpath}//label[.//span[contains(normalize-space(.), '{option_text}')]]",
            f"{section_xpath}//label[contains(normalize-space(.), '{option_text}')]",
        ]:
            try:
                label = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, label_xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                checkbox = label.find_element(By.XPATH, ".//input[@type='checkbox']")
                if not checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", label)
                time.sleep(0.2)
                return
            except Exception:
                continue
        raise AssertionError(f"Could not find checkbox '{option_text}' in filter section '{section_name}'")

    def select_filter_category(self, category: str):
        """Select category filter (e.g. Bug)."""
        self._check_filter_checkbox("Category", category)

    def select_filter_severity(self, severity: str):
        """Select severity filter (e.g. High)."""
        self._check_filter_checkbox("Severity", severity)

    def select_filter_status(self, status: str):
        """Select status filter (e.g. Open)."""
        self._check_filter_checkbox("Status", status)

    def select_filter_date(self, filter_date: date, timeout: int = 10):
        """Select date in filter panel. Opens p-calendar, then clicks the day in the datepicker."""
        panel_xpath = "//div[contains(@class,'filter-panel') and contains(@class,'open')]"
        calendar_xpath = f"{panel_xpath}//p-calendar//input[@placeholder='Select date range']"
        calendar_input = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, calendar_xpath))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calendar_input)
        calendar_input.click()
        time.sleep(0.5)
        # Wait for p-datepicker overlay and click the day cell
        day_num = str(filter_date.day)
        for day_xpath in [
            f"//div[contains(@class,'p-datepicker')]//td[not(contains(@class,'p-disabled'))]//span[text()='{day_num}']",
            f"//div[contains(@class,'p-datepicker')]//td[not(contains(@class,'p-disabled')) and not(contains(@class,'p-datepicker-other-month'))]//span[normalize-space()='{day_num}']",
            f"//div[contains(@class,'p-datepicker')]//span[normalize-space()='{day_num}']",
        ]:
            try:
                day_cell = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, day_xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", day_cell)
                self.driver.execute_script("arguments[0].click();", day_cell)
                time.sleep(0.3)
                return
            except Exception:
                continue
        raise AssertionError(f"Could not select date {filter_date} in calendar")

    def select_filter_project(self, project_name: str, timeout: int = 10):
        """Select project in filter panel. Uses p-multiselect with Select Projects placeholder."""
        panel_xpath = "//div[contains(@class,'filter-panel') and contains(@class,'open')]"
        for xpath in [
            f"{panel_xpath}//h4[contains(.,'Project')]/following-sibling::*[contains(@class,'p-multiselect')][1]",
            f"{panel_xpath}//p-multiselect",
            f"{panel_xpath}//*[contains(@class,'p-multiselect')]",
        ]:
            try:
                trigger = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                self.driver.execute_script("arguments[0].click();", trigger)
                time.sleep(0.5)
                self._select_option_from_open_panel(project_name, timeout=timeout)
                return
            except Exception:
                continue
        raise AssertionError(f"Could not select project '{project_name}' in filter")

    def click_apply_filters(self, timeout: int = 10):
        """Click the Apply Filters button in the filter panel."""
        panel_xpath = "//div[contains(@class,'filter-panel') and contains(@class,'open')]"
        btn_xpath = f"{panel_xpath}//button[contains(normalize-space(.), 'Apply Filters')]"
        btn = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, btn_xpath))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)

    def search_ticket_by_title(self, title: str, timeout: int = 15):
        """Type the ticket title in the search bar to filter the list."""
        # Try multiple selectors - app may use different placeholders
        for xpath in [
            "//input[contains(@placeholder, 'Search') or @placeholder='Search']",
            "//input[@type='search']",
            "//input[contains(@placeholder, 'search')]",
            "//input[contains(@aria-label, 'Search') or contains(@aria-label, 'search')]",
        ]:
            try:
                search_input = WebDriverWait(self.driver, timeout // 2).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
                break
            except Exception:
                continue
        else:
            raise TimeoutException(f"Search input not found within {timeout}s")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
        try:
            search_input.clear()
        except Exception:
            pass
        search_input.send_keys(title)

    def click_first_ticket_in_list(self, title: str, timeout: int = 10, max_retries: int = 3):
        """Click the first table row that contains the given title (opens /issue/{id}/edit).
        Tries link inside row first (more reliable for navigation), then row. Retries on StaleElementReferenceException."""
        row_xpath = f"//tr[.//*[contains(normalize-space(.), '{title}')]]"
        link_xpath = f"{row_xpath}//a[contains(@href,'issue')]"
        for attempt in range(max_retries):
            try:
                # Prefer clicking the link - more reliable for navigation (especially for agent role)
                try:
                    link = WebDriverWait(self.driver, timeout // 2).until(
                        EC.element_to_be_clickable((By.XPATH, link_xpath))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    try:
                        self.driver.execute_script("arguments[0].click();", link)
                    except Exception:
                        link.click()
                    return
                except Exception:
                    pass
                # Fallback: click the row
                row = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, row_xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                try:
                    self.driver.execute_script("arguments[0].click();", row)
                except Exception:
                    row.click()
                return
            except StaleElementReferenceException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.5)

    def wait_for_issue_edit_page(self, timeout: int = 10):
        """Wait until URL matches /issue/{id}/edit."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: re.search(r"/issue/\d+/edit", d.current_url) is not None
        )

    def _select_edit_dropdown(self, label_text: str, option_text: str):
        """On edit page: open dropdown by label and select option."""
        self._select_dropdown_option_by_label(label_text, option_text)

    def select_edit_type(self, option_text: str):
        """On edit page: change Type dropdown (e.g. CR). Tries multiple label variants and trigger approaches."""
        time.sleep(0.5)
        for label in ["Type", "Ticket Type", "Issue Type"]:
            try:
                trigger_xpath = (
                    f"//*[contains(normalize-space(.), '{label}')]/following::*[contains(@class,'p-dropdown')][1]"
                )
                trigger = self._wait.until(EC.element_to_be_clickable((By.XPATH, trigger_xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                time.sleep(0.2)
                try:
                    inner = trigger.find_element(
                        By.XPATH,
                        ".//*[contains(@class,'p-dropdown-trigger') or @aria-label='dropdown trigger']"
                    )
                    if inner.is_displayed():
                        trigger = inner
                except Exception:
                    pass
                try:
                    self.driver.execute_script("arguments[0].click();", trigger)
                except Exception:
                    ActionChains(self.driver).move_to_element(trigger).click().perform()
                time.sleep(0.5)
                self._select_option_from_open_panel(option_text)
                return
            except Exception:
                continue
        try:
            edit_form = self.driver.find_element(By.XPATH, "//*[contains(., 'Update') or contains(., 'Edit')]/ancestor::form | //form[.//*[contains(@class,'p-dropdown')]]")
            trigger = edit_form.find_element(By.XPATH, ".//*[contains(@class,'p-dropdown')][1]")
            self._open_dropdown_trigger(trigger)
            self._select_option_from_open_panel(option_text)
            return
        except Exception:
            pass
        raise AssertionError(f"Could not open Type dropdown to select '{option_text}'")

    def select_edit_severity(self, option_text: str):
        """On edit page: change Severity (e.g. Medium)."""
        self._select_edit_dropdown("Severity", option_text)

    def select_edit_status(self, option_text: str):
        """On edit page: change Status (e.g. Solved)."""
        self._select_edit_dropdown("Status", option_text)

    def select_edit_assignee(self, option_text: str):
        """On edit page: select Assignee (e.g. mekayed)."""
        for label in ["Assignee", "Select Assignee"]:
            try:
                self._select_edit_dropdown(label, option_text)
                return
            except Exception:
                continue
        raise AssertionError(f"Could not select assignee '{option_text}'")

    def fill_edit_description(self, text: str):
        """On edit page: fill Issue Description textarea."""
        el = WebDriverWait(self.driver, 8).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(., 'Issue Description')]/following::textarea[1] | //textarea[@formcontrolname='description' or @id='description']")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        try:
            el.clear()
        except Exception:
            pass
        el.send_keys(text)

    def fill_edit_expected_behavior(self, text: str):
        """On edit page: fill Expected Behaviour textarea."""
        for xpath in [
            "//*[contains(., 'Expected Behaviour') or contains(., 'Expected behavior')]/following::textarea[1]",
            "//textarea[@formcontrolname='expectedBehavior' or @formcontrolname='expectedBehaviour']",
        ]:
            try:
                el = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                try:
                    el.clear()
                except Exception:
                    pass
                el.send_keys(text)
                return
            except Exception:
                continue
        raise AssertionError("Edit page: Expected behaviour textarea not found")

    def fill_edit_additional_notes(self, text: str):
        """On edit page: fill Additional notes textarea."""
        for xpath in [
            "//*[contains(., 'Additional notes')]/following::textarea[1]",
            "//textarea[@formcontrolname='additionalNotes']",
        ]:
            try:
                el = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                try:
                    el.clear()
                except Exception:
                    pass
                el.send_keys(text)
                return
            except Exception:
                continue
        raise AssertionError("Edit page: Additional notes textarea not found")

    def select_edit_related_ticket(self, option_text: str):
        """On edit page: change Related ticket dropdown (e.g. test3)."""
        self._select_edit_dropdown("Related ticket", option_text)

    def fill_edit_comment(self, text: str):
        """On edit page: fill the comment text area (id=newComment). Uses value set for speed."""
        for locator in [
            (By.ID, "newComment"),
            (By.XPATH, "//textarea[@formcontrolname='newComment' or @placeholder='Leave a comment']"),
        ]:
            try:
                el = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(locator))
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                    el, text
                )
                return
            except Exception:
                continue
        raise AssertionError("Edit page: comment textarea not found")

    def click_submit_comment(self, timeout: int = 4):
        """On edit page: click the Submit button that posts the comment (not Save Changes)."""
        for xpath in [
            "//textarea[@id='newComment']/following-sibling::button[contains(., 'Submit')]",
            "//textarea[@id='newComment']/..//button[contains(., 'Submit')]",
            "//button[contains(., 'Submit') and contains(@class,'cancel-btn')]",
            "//button[contains(., 'Submit') and not(contains(., 'Save'))]",
        ]:
            try:
                btn = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", btn)
                return
            except Exception:
                continue
        raise AssertionError("Edit page: comment Submit button not found")

    def click_save_changes(self, timeout: int = 10):
        """On edit page: click Save Changes button."""
        btn = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Save Changes')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        try:
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            btn.click()
