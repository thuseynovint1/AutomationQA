from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize the browser
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size to HD

    hub_url = "http://selenium-grid-hub:4444/wd/hub"  # Selenium Grid Hub URL
    try:
        browser = webdriver.Remote(command_executor=hub_url, options=chrome_options)
        logging.info("Browser initialized successfully.")
        return browser
    except WebDriverException as e:
        logging.error(f"Failed to initialize browser: {e}")
        raise

# Test the Careers page
def verify_careers_section():
    browser = None
    try:
        browser = setup_browser()
        logging.info("Navigating to the Insider homepage...")
        browser.get("https://useinsider.com/")

        # Navigate to the Careers page via the Company menu
        logging.info("Opening the 'Company' menu...")
        company_tab = WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Company")))
        company_tab.click()

        logging.info("Clicking on the 'Careers' link...")
        careers_tab = WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Careers")))
        careers_tab.click()

        # Verify the Careers page URL
        logging.info("Verifying the Careers page URL...")
        WebDriverWait(browser, 10).until(EC.url_contains("careers"))
        assert "careers" in browser.current_url, f"Expected 'careers' in URL, but got '{browser.current_url}'"

        # Verify key elements on the Careers page
        logging.info("Verifying key elements on the Careers page...")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Our Locations')]")))
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'See all teams')]")))
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Life at Insider')]")))

        logging.info("🚀 TEST 2 PASSED: Careers page loaded successfully and all elements are present.")

    except TimeoutException:
        logging.error("❌ TEST 2 FAILED: Timed out waiting for an element to load.")
    except NoSuchElementException:
        logging.error("❌ TEST 2 FAILED: An expected element was not found on the page.")
    except AssertionError as e:
        logging.error(f"❌ TEST 2 FAILED: {e}")
    except Exception as e:
        logging.error(f"❌ TEST 2 FAILED: An unexpected error occurred - {e}")
    finally:
        if browser:
            logging.info("Closing the browser.")
            browser.quit()

# Run the test
if __name__ == "__main__":
    verify_careers_section()