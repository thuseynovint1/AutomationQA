from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import time

# Function to initialize a headless Chrome driver
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid memory issues
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size for proper rendering

    hub_url = "http://selenium-grid-hub:4444/wd/hub"  # Selenium Grid URL
    browser = webdriver.Remote(command_executor=hub_url, options=chrome_options)
    return browser

# Test 1: Verify the homepage loads correctly
def check_homepage():
    browser = None
    try:
        browser = setup_browser()
        browser.get("https://useinsider.com/")  # Open the homepage
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for the page to load
        assert "Insider" in browser.title  # Check if "Insider" is in the page title
        print("✅ TEST 1 PASSED: Homepage loaded successfully")
    except Exception as e:
        print(f"❌ TEST 1 FAILED: Homepage - {e}")
    finally:
        if browser:
            browser.quit()  # Close the browser

# Test 2: Verify the Careers page loads correctly
def verify_careers_section():
    browser = None
    try:
        browser = setup_browser()
        browser.get("https://useinsider.com/")  # Open the homepage

        # Navigate to the Careers page via the Company menu
        company_tab = WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Company")))
        company_tab.click()
        careers_tab = WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.LINK_TEXT, "Careers")))
        careers_tab.click()

        # Verify the Careers page URL and key elements
        WebDriverWait(browser, 10).until(EC.url_contains("careers"))
        assert "careers" in browser.current_url
        assert WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Our Locations')]")))
        assert WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'See all teams')]")))
        assert WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Life at Insider')]")))

        print("✅ TEST 2 PASSED: Careers page loaded successfully")
    except Exception as e:
        print(f"❌ TEST 2 FAILED: Careers page - {e}")
    finally:
        if browser:
            browser.quit()  # Close the browser

# Test 3: Verify the QA Jobs page and its functionality
def validate_qa_jobs():
    browser = None
    try:
        browser = setup_browser()
        browser.get("https://useinsider.com/careers/quality-assurance/")  # Open the QA Jobs page

        # Handle cookie consent banner if it appears
        try:
            accept_cookies = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept')]")))
            accept_cookies.click()
            print("✅ Cookie consent accepted")
        except Exception:
            print("ℹ️ No cookie banner found or already dismissed")

        # Click "See all QA jobs" link
        all_qa_jobs = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'qualityassurance')]"))
        )
        all_qa_jobs.click()

        # Verify redirection to the QA jobs page
        WebDriverWait(browser, 15).until(EC.url_contains("open-positions"))
        assert "qualityassurance" in browser.current_url, "❌ Redirection to QA jobs page failed"
        print("✅ TEST 3 PASSED: QA Jobs page loaded successfully")

        # Test 4: Apply location filter
        try:
            location_filter = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "filter-by-location")))
            select_location = Select(location_filter)
            time.sleep(6)  # Wait for dropdown options to load
            select_location.select_by_index(1)  # Select the second option (e.g., Istanbul, Turkiye)
            time.sleep(6)

            selected_location = select_location.first_selected_option.text
            assert selected_location == "Istanbul, Turkiye", "❌ Location filter not applied correctly"
            print("✅ TEST 4 PASSED: Location filter applied successfully")
        except Exception as e:
            print(f"❌ TEST 4 FAILED: Failed to apply location filter: {e}")

        # Test 5: Click "View Role" button and verify redirection
        try:
            # Hover over the job listing to make the "View Role" button visible
            job_listing = browser.find_element(By.XPATH, '//*[@id="jobs-list"]/div[1]/div')
            hover_action = ActionChains(browser)
            hover_action.move_to_element(job_listing).perform()
            print("✅ Hovered over the job listing")

            # Click the "View Role" button
            view_role = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'View Role')]"))
            )
            role_url = view_role.get_attribute("href")
            print(f"ℹ️ View Role button URL: {role_url}")

            # Open the URL in a new tab
            browser.execute_script(f"window.open('{role_url}', '_blank');")
            print("✅ Opened the View Role URL in a new tab")

            # Switch to the new tab and verify the URL
            WebDriverWait(browser, 15).until(EC.number_of_windows_to_be(2))
            browser.switch_to.window(browser.window_handles[1])
            WebDriverWait(browser, 15).until(EC.url_contains("jobs.lever.co"))
            assert "jobs.lever.co" in browser.current_url, "❌ View Role button did not open correct URL"
            print("✅ TEST 5 PASSED: View Role button opened the correct URL")

        except Exception as e:
            print(f"❌ TEST 5 FAILED: {e}")

    finally:
        if browser:
            browser.quit()  # Close the browser

# Run all tests
if __name__ == "__main__":
    check_homepage()
    verify_careers_section()
    validate_qa_jobs()
