from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

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

    hub_url = "http://localhost:51231/wd/hub"  # Selenium Grid Hub URL
    try:
        browser = webdriver.Remote(command_executor=hub_url, options=chrome_options)
        logging.info("🚀 Browser initialized successfully.")
        return browser
    except WebDriverException as e:
        logging.error(f"❌ Failed to initialize browser: {e}")
        raise

# Test 1: Verify the homepage loads correctly
def check_homepage():
    browser = None
    try:
        browser = setup_browser()
        logging.info("Navigating to the Insider homepage...")
        browser.get("https://useinsider.com/")

        # Wait for the page to load
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Insider" in browser.title, f"Expected 'Insider' in title, but got '{browser.title}'"
        logging.info("🚀 TEST 1 PASSED: Homepage loaded successfully.")

    except TimeoutException:
        logging.error("❌ TEST 1 FAILED: Timed out waiting for the homepage to load.")
    except AssertionError as e:
        logging.error(f"❌ TEST 1 FAILED: {e}")
    except Exception as e:
        logging.error(f"❌ TEST 1 FAILED: An unexpected error occurred - {e}")
    finally:
        if browser:
            logging.info("Closing the browser.")
            browser.quit()

# Test 2: Verify the Careers page loads correctly
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

# Test 3: Verify the QA Jobs page and its functionality
def validate_qa_jobs():
    browser = None
    try:
        browser = setup_browser()
        logging.info("Navigating to the QA Jobs page...")
        browser.get("https://useinsider.com/careers/quality-assurance/")

        # Handle cookie consent banner if it appears
        try:
            accept_cookies = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept')]")))
            accept_cookies.click()
            logging.info("✅ Cookie consent accepted")
        except Exception:
            logging.info("ℹ️ No cookie banner found or already dismissed")

        # Click "See all QA jobs" link
        logging.info("Clicking 'See all QA jobs' link...")
        all_qa_jobs = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'qualityassurance')]"))
        )
        all_qa_jobs.click()

        # Verify redirection to the QA jobs page
        logging.info("Verifying redirection to the QA jobs page...")
        WebDriverWait(browser, 15).until(EC.url_contains("open-positions"))
        assert "qualityassurance" in browser.current_url, "❌ Redirection to QA jobs page failed"
        logging.info("🚀 TEST 3 PASSED: QA Jobs page loaded successfully")

        # Test 4: Apply location filter
        try:
            logging.info("Applying location filter...")
            location_filter = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "filter-by-location")))
            select_location = Select(location_filter)
            time.sleep(6)  # Wait for dropdown options to load
            select_location.select_by_index(1)  # Select the second option (e.g., Istanbul, Turkiye)
            time.sleep(6)

            selected_location = select_location.first_selected_option.text
            assert selected_location == "Istanbul, Turkiye", "❌ Location filter not applied correctly"
            logging.info("🚀 TEST 4 PASSED: Location filter applied successfully")
        except Exception as e:
            logging.error(f"❌ TEST 4 FAILED: Failed to apply location filter: {e}")

        # Test 5: Click "View Role" button and verify redirection
        try:
            logging.info("Hovering over the job listing...")
            job_listing = browser.find_element(By.XPATH, '//*[@id="jobs-list"]/div[1]/div')
            hover_action = ActionChains(browser)
            hover_action.move_to_element(job_listing).perform()
            logging.info("✅ Hovered over the job listing")

            # Click the "View Role" button
            logging.info("Clicking 'View Role' button...")
            view_role = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'View Role')]"))
            )
            role_url = view_role.get_attribute("href")
            logging.info(f"ℹ️ View Role button URL: {role_url}")

            # Open the URL in a new tab
            browser.execute_script(f"window.open('{role_url}', '_blank');")
            logging.info("✅ Opened the View Role URL in a new tab")

            # Switch to the new tab and verify the URL
            WebDriverWait(browser, 15).until(EC.number_of_windows_to_be(2))
            browser.switch_to.window(browser.window_handles[1])
            WebDriverWait(browser, 15).until(EC.url_contains("jobs.lever.co"))
            assert "jobs.lever.co" in browser.current_url, "❌ View Role button did not open correct URL"
            logging.info("🚀 TEST 5 PASSED: View Role button opened the correct URL")

        except Exception as e:
            logging.error(f"❌ TEST 5 FAILED: {e}")

    finally:
        if browser:
            logging.info("Closing the browser.")
            browser.quit()

# Run all tests
if __name__ == "__main__":
    check_homepage()
    verify_careers_section()
    validate_qa_jobs()