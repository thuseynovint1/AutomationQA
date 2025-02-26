"""
This module contains automated tests for the Insider website using Selenium and pytest.
"""

import os
import logging
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration
SELENIUM_GRID_URL = os.getenv("SELENIUM_GRID_URL", "http://selenium-grid-hub:4444/wd/hub")
BASE_URL = "https://useinsider.com/"


def get_headless_driver():
    """Initialize and return a headless Chrome driver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Remote(command_executor=SELENIUM_GRID_URL, options=options)
    return driver


def take_screenshot(driver, test_name):
    """Capture a screenshot and save it with the test name."""
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"{test_name}.png")
    driver.save_screenshot(screenshot_path)
    logger.info("Screenshot saved: %s", screenshot_path)


@pytest.fixture(scope="function")
def browser():
    """Fixture to initialize and quit the driver for each test."""
    driver = get_headless_driver()
    yield driver
    driver.quit()


def test_homepage(browser):
    """Test if the Insider homepage loads successfully."""
    try:
        browser.get(BASE_URL)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Insider" in browser.title
        logger.info("✅ TEST 1 PASSED: Homepage loaded successfully")
    except Exception as e:
        take_screenshot(browser, "test_homepage_failure")
        logger.error("❌ TEST 1 FAILED: Homepage - %s", e)
        raise


def test_careers_page(browser):
    """Test navigation to the Careers page and verify sections."""
    try:
        browser.get(BASE_URL)

        company_menu = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Company"))
        )
        company_menu.click()

        careers_link = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Careers"))
        )
        careers_link.click()

        WebDriverWait(browser, 10).until(EC.url_contains("careers"))
        assert "careers" in browser.current_url
        assert WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Our Locations')]"))
        )
        assert WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'See all teams')]"))
        )
        assert WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Life at Insider')]"))
        )

        logger.info("✅ TEST 2 PASSED: Careers page loaded successfully")
    except Exception as e:
        take_screenshot(browser, "test_careers_page_failure")
        logger.error("❌ TEST 2 FAILED: Careers page - %s", e)
        raise


def test_qa_jobs_page(browser):
    """Test the QA jobs page, including filtering and job details."""
    try:
        browser.get(f"{BASE_URL}careers/quality-assurance/")

        # Handle cookie consent banner
        try:
            accept_button = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept')]"))
            )
            accept_button.click()
            logger.info("✅ Cookie consent accepted")
        except Exception:
            logger.info("ℹ️ No cookie banner found or already dismissed")

        # Click "See all QA jobs"
        see_all_qa_jobs_link = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@href='https://useinsider.com/careers/open-positions/?department=qualityassurance']")
            )
        )
        see_all_qa_jobs_link.click()

        # Verify redirection
        WebDriverWait(browser, 15).until(EC.url_contains("open-positions"))
        assert "qualityassurance" in browser.current_url, "❌ Redirection to QA jobs page failed"

        # Filter jobs by location
        try:
            dropdown_element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "filter-by-location"))
            )
            select = Select(dropdown_element)
            time.sleep(3)  # Allow dropdown options to load
            select.select_by_index(1)  # Select the second option
            time.sleep(2)

            selected_option = select.first_selected_option.text
            assert selected_option == "Istanbul, Turkiye", "❌ Location filter not applied correctly"
            logger.info("✅ TEST 3 PASSED: Location filter applied successfully")
        except Exception as e:
            logger.error("❌ TEST 3 FAILED: Failed to apply location filter: %s", e)
            raise

        # Test "View Role" button
        try:
            hover_element = browser.find_element(By.XPATH, '//*[@id="jobs-list"]/div[1]/div')
            actions = ActionChains(browser)
            actions.move_to_element(hover_element).perform()
            logger.info("✅ Cursor moved to the element")

            view_role_button = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'btn-navy') and contains(text(), 'View Role')]")
                )
            )
            view_role_url = view_role_button.get_attribute("href")
            logger.info("ℹ️ View Role button URL: %s", view_role_url)

            browser.execute_script(f"window.open('{view_role_url}', '_blank');")
            logger.info("✅ Opened the View Role URL in a new tab")

            WebDriverWait(browser, 15).until(EC.number_of_windows_to_be(2))
            browser.switch_to.window(browser.window_handles[1])

            WebDriverWait(browser, 15).until(EC.url_contains("jobs.lever.co"))
            assert "jobs.lever.co" in browser.current_url, "❌ View Role button did not open correct URL"
            logger.info("✅ TEST 4 PASSED: View Role button opened the correct URL")
        except Exception as e:
            logger.error("❌ TEST 4 FAILED: %s", e)
            raise

    except Exception as e:
        take_screenshot(browser, "test_qa_jobs_page_failure")
        logger.error("❌ TEST FAILED: QA Jobs page - %s", e)
        raise

if __name__ == "__main__":
    test_homepage()
    test_careers_page()
    test_qa_jobs_page()
    
if __name__ == "__main__":
    pytest.main(["-v", "--html=report.html"])
