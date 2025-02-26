from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import time


def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")  # Use new headless mode for better stability
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
    options.add_argument("--window-size=1920,1080")  # Ensure proper rendering in headless mode

    grid_url = "http://selenium-grid-hub:4444/wd/hub"  # Ensure this is correct
    driver = webdriver.Remote(command_executor=grid_url, options=options)
    return driver


def test_homepage():
    driver = None
    try:
        driver = get_headless_driver()
        driver.get("https://useinsider.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Insider" in driver.title
        print("✅ TEST 1 PASSED: Homepage loaded successfully")
    except Exception as e:
        print(f"❌ TEST 1 FAILED: Homepage - {e}")
    finally:
        if driver:
            driver.quit()


def test_careers_page():
    driver = None
    try:
        driver = get_headless_driver()
        driver.get("https://useinsider.com/")

        company_menu = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Company"))
        )
        company_menu.click()

        careers_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Careers"))
        )
        careers_link.click()

        WebDriverWait(driver, 10).until(EC.url_contains("careers"))
        assert "careers" in driver.current_url
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Our Locations')]"))
        )
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'See all teams')]"))
        )
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Life at Insider')]"))
        )

        print("✅ TEST 2 PASSED: Careers page loaded successfully")
    except Exception as e:
        print(f"❌ TEST 2 FAILED: Careers page - {e}")
    finally:
        if driver:
            driver.quit()


def test_qa_jobs_page(): #test_qa_jobs_page
    driver = None
    try:
        driver = get_headless_driver()
        driver.get("https://useinsider.com/careers/quality-assurance/")

        # Handle cookie consent banner if it exists
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept')]"))
            )
            accept_button.click()
            print("✅ TEST 3 PASSED:  Cookie consent accepted and QA Jobs Loaded successfully ")
        except Exception:
            print("❌ TEST 3  FAILED: No cookie banner found or already dismissed")

        # Click "See all QA jobs"
        see_all_qa_jobs_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@href='https://useinsider.com/careers/open-positions/?department=qualityassurance']")
            )
        )
        see_all_qa_jobs_link.click()

        # Verify redirection
        WebDriverWait(driver, 15).until(EC.url_contains("open-positions"))
        assert "qualityassurance" in driver.current_url, "❌ Redirection to QA jobs page failed"


        try: #test_apply_locatiom
            dropdown_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "filter-by-location"))
            )
            select = Select(dropdown_element)
            time.sleep(3)  # Allow dropdown options to load
            select.select_by_index(1)  # Select the second option
            time.sleep(2)

            selected_option = select.first_selected_option.text
            assert selected_option == "Istanbul, Turkiye", "❌ Location filter not applied correctly"
            print("✅ TEST 4 PASSED: Location filter applied successfully")
        except Exception as e:
            print(f"❌ TEST 4 FAILED: Failed to apply location filter: {e}")

        # Click "View Role" button

        try: #test_view_role
            # Locate the element to hover over (the parent container or the button itself)
            hover_element = driver.find_element(By.XPATH, '//*[@id="jobs-list"]/div[1]/div')

            # Use ActionChains to move the cursor to the element
            actions = ActionChains(driver)
            actions.move_to_element(hover_element).perform()
            print("✅ Cursor moved to the element")

            # Wait for the "View Role" button to be clickable
            view_role_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class, 'btn-navy') and contains(text(), 'View Role')]")
                )
            )
            view_role_url = view_role_button.get_attribute("href")
            print(f"ℹ️ View Role button URL: {view_role_url}")

            # Open the URL in a new tab using JavaScript
            driver.execute_script(f"window.open('{view_role_url}', '_blank');")
            print("✅ Opened the View Role URL in a new tab")

            # Wait for new tab to open and switch to it
            WebDriverWait(driver, 15).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])

            # Verify new tab URL
            WebDriverWait(driver, 15).until(EC.url_contains("jobs.lever.co"))
            assert "jobs.lever.co" in driver.current_url, "❌ View Role button did not open correct URL"
            print("✅ TEST 5 PASSED: View Role button opened the correct URL")

        except TimeoutException as e:
            print(f"❌ TEST 5 FAILED: Timeout while waiting for element or new tab: {e}")
        except NoSuchElementException as e:
            print(f"❌ TEST 5 FAILED: Element not found: {e}")
        except Exception as e:
            print(f"❌ TEST 5 FAILED: Unexpected error: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    test_homepage()
    test_careers_page()
    test_qa_jobs_page()
