import time
import re
import json
import random
import argparse
import os
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class InstagramCancellationTool:
    def __init__(self, headless=True, delay_min=2, delay_max=4):
        """
        Initialize the Instagram cancellation tool.
        
        Args:
            headless (bool): Run browser in headless mode (without UI)
            delay_min (int): Minimum delay between requests in seconds
            delay_max (int): Maximum delay between requests in seconds
        """
        self.delay_min = delay_min
        self.delay_max = delay_max
        
        # Initialize the webdriver with Docker-compatible settings
        options = webdriver.ChromeOptions()
        
        # Never run headless when 2FA is involved as we need to see and interact with the prompts
        if headless:
            print("Note: If 2FA is required, browser will be visible despite headless setting.")
            # We'll disable headless mode during login if 2FA is detected
        
        # Required for running Chrome in a Docker container
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")  # Reduce logging
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        # Add user agent to make it look like a real browser
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # For Docker: specify the Chrome binary location if needed
        chrome_binary = "/usr/bin/google-chrome"
        if os.path.exists(chrome_binary):
            options.binary_location = chrome_binary
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Login status
        self.logged_in = False
        
        print("Browser initialized successfully.")

    def login(self, username, password):
        """
        Log in to Instagram with 2FA support.
        
        Args:
            username (str): Instagram username
            password (str): Instagram password
            
        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            print(f"Attempting to log in as {username}...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for the login form to appear
            time.sleep(5)
            
            # Save screenshot of login page
            self.driver.save_screenshot("/app/data/login_page.png")
            
            # Enter username
            username_input = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_input.send_keys(username)
            
            # Enter password
            password_input = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_input.send_keys(password)
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            login_button.click()
            
            # Wait for login to proceed
            time.sleep(5)
            
            # Save screenshot after initial login attempt
            self.driver.save_screenshot("/app/data/after_login_click.png")
            
            # Check for 2FA screen
            if self.check_for_2fa():
                print("Two-factor authentication detected!")
                if self.handle_2fa():
                    print("2FA authentication successful!")
                else:
                    print("Failed to complete 2FA authentication.")
                    return False
            
            # Handle "Save Your Login Info?" prompt if it appears
            self.handle_save_login_prompt()
            
            # Handle "Turn on Notifications" prompt if it appears
            self.handle_notifications_prompt()
            
            # Check if login was successful
            if "challenge" in self.driver.current_url or "login" in self.driver.current_url:
                print("Login failed or additional verification required.")
                self.driver.save_screenshot("/app/data/login_challenge.png")
                return False
            
            # Wait for the feed to load to confirm we're logged in
            time.sleep(3)
            self.driver.save_screenshot("/app/data/after_login.png")
            
            # Verify we're logged in by checking for typical elements or URL
            if self.check_login_success():
                self.logged_in = True
                print("Login successful!")
                return True
            else:
                print("Login verification failed - couldn't confirm successful login.")
                return False
                
        except TimeoutException:
            print("Login failed: page elements not found or took too long to load.")
            self.driver.save_screenshot("/app/data/login_timeout.png")
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot("/app/data/login_error.png")
            return False

    def check_for_2fa(self):
        """Check if 2FA screen is present."""
        self.driver.save_screenshot("/app/data/checking_2fa.png")
        try:
            # Look for common 2FA indicators
            two_factor_indicators = [
                "//input[@name='verificationCode']",
                "//form[contains(@id, 'two_factor')]",
                "//h2[contains(text(), 'Enter Security Code')]",
                "//h2[contains(text(), 'Enter Confirmation Code')]",
                "//h2[contains(text(), 'Enter the code')]",
                "//label[contains(text(), 'Security code')]",
                "//p[contains(text(), 'Enter the 6-digit code')]"
            ]
            
            for indicator in two_factor_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        return True
                except:
                    continue
                
            # Also check for text in the page source
            page_source = self.driver.page_source.lower()
            two_factor_texts = [
                "two-factor authentication", 
                "2-factor authentication",
                "security code",
                "confirmation code",
                "authentication app",
                "6-digit code"
            ]
            
            for text in two_factor_texts:
                if text in page_source:
                    return True
                    
            return False
        except:
            return False

    def handle_2fa(self):
        """Handle 2FA without requiring visible browser"""
        try:
            # Take a screenshot of the 2FA screen
            self.driver.save_screenshot("/app/data/2fa_screen.png")
            
            print("\n" + "="*80)
            print("TWO-FACTOR AUTHENTICATION REQUIRED")
            print("="*80)
            print("A screenshot has been saved to /app/data/2fa_screen.png")
            print("Please check this screenshot to see if you need to enter a verification code.")
            
            # Ask the user if 2FA is needed
            needs_2fa = input("Do you need to enter a 2FA code? (y/n): ").strip().lower()
            
            if needs_2fa == 'y':
                verification_code = input("Enter the 6-digit verification code from your auth app: ").strip()
                
                # Try to find the input field
                input_found = False
                for selector in ["input[name='verificationCode']", "input[aria-label='Security code']", "input[inputmode='numeric']", "input[type='tel']", "input[type='text']"]:
                    try:
                        code_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if code_input.is_displayed():
                            code_input.clear()
                            code_input.send_keys(verification_code)
                            print(f"Entered verification code using selector: {selector}")
                            input_found = True
                            break
                    except:
                        continue
                
                if not input_found:
                    print("Could not find verification code input field. Taking screenshot...")
                    self.driver.save_screenshot("/app/data/2fa_input_missing.png")
                    print("See screenshot at /app/data/2fa_input_missing.png")
                    
                    # Try to enter code using JavaScript as a fallback
                    try:
                        js_code = f"""document.querySelector('input[inputmode="numeric"]').value = '{verification_code}';"""
                        self.driver.execute_script(js_code)
                        print("Attempted to enter code using JavaScript")
                    except Exception as e:
                        print(f"JavaScript entry failed: {str(e)}")
                
                # Try to find and click the confirm button
                button_found = False
                for button_selector in [
                    "//button[contains(., 'Confirm')]",
                    "//button[contains(., 'Submit')]",
                    "//button[contains(., 'Verify')]",
                    "//button[contains(@class, 'sqdOP')]",
                    "button[type='submit']"
                ]:
                    try:
                        button = None
                        if '//' in button_selector:
                            button = self.driver.find_element(By.XPATH, button_selector)
                        else:
                            button = self.driver.find_element(By.CSS_SELECTOR, button_selector)
                        
                        if button and button.is_displayed():
                            button.click()
                            print(f"Clicked button using selector: {button_selector}")
                            button_found = True
                            break
                    except:
                        continue
                
                if not button_found:
                    print("Could not find confirmation button. Taking screenshot...")
                    self.driver.save_screenshot("/app/data/2fa_button_missing.png")
                    print("See screenshot at /app/data/2fa_button_missing.png")
                    
                    # Try to submit the form as a fallback
                    try:
                        self.driver.find_element(By.TAG_NAME, "form").submit()
                        print("Attempted to submit the form directly")
                    except:
                        print("Form submission also failed")
                
                # Wait for processing - extended time
                print("Waiting for 2FA processing (30 seconds)...")
                time.sleep(30)
                self.driver.save_screenshot("/app/data/after_2fa.png")
                print("Check /app/data/after_2fa.png to see the result")
                
                # Check if we're still on the 2FA screen
                if "two_factor" in self.driver.current_url or "challenge" in self.driver.current_url:
                    current_url = self.driver.current_url
                    print(f"Still on verification screen: {current_url}")
                    
                    # One more attempt with a different approach
                    print("Trying alternative approach...")
                    try:
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if button.is_displayed():
                                button.click()
                                print("Clicked an available button")
                                time.sleep(2)
                        
                        time.sleep(10)
                        self.driver.save_screenshot("/app/data/final_2fa_attempt.png")
                        
                        if "two_factor" not in self.driver.current_url and "challenge" not in self.driver.current_url:
                            print("Alternative approach succeeded!")
                            return True
                    except:
                        pass
                    
                    print("2FA may have failed. Check the screenshot.")
                    return False
                
                print("2FA verification appears successful!")
                return True
            
            return True  # If no 2FA needed
            
        except Exception as e:
            print(f"Error handling 2FA: {str(e)}")
            return False

    def handle_save_login_prompt(self):
        """Handle the 'Save Your Login Info?' prompt if it appears."""
        try:
            # Common text for the buttons on this prompt
            save_login_buttons = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Not now')]",
                "//a[contains(text(), 'Not Now')]"
            ]
            
            for selector in save_login_buttons:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    if button.is_displayed():
                        print("Handling 'Save Login Info' prompt...")
                        button.click()
                        time.sleep(2)
                        return True
                except:
                    continue
                    
            return False
        except:
            return False

    def handle_notifications_prompt(self):
        """Handle the 'Turn on Notifications' prompt if it appears."""
        try:
            # Common text for the buttons on this prompt
            notification_buttons = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Not now')]",
                "//a[contains(text(), 'Not Now')]"
            ]
            
            for selector in notification_buttons:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    if button.is_displayed():
                        print("Handling 'Turn on Notifications' prompt...")
                        button.click()
                        time.sleep(2)
                        return True
                except:
                    continue
                    
            return False
        except:
            return False

    def check_login_success(self):
        """Verify if login was successful."""
        try:
            # Check if we're not on login or challenge pages
            if "login" in self.driver.current_url or "challenge" in self.driver.current_url:
                return False
                
            # Look for common elements that indicate we're logged in
            logged_in_indicators = [
                "//nav//a[contains(@href, '/direct/inbox/')]",
                "//nav//a[contains(@href, '/explore/')]",
                "//nav//span[contains(text(), 'Search')]",
                "//svg[@aria-label='Home']",
                "//svg[@aria-label='Search']",
                "//svg[@aria-label='Explore']"
            ]
            
            for indicator in logged_in_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        return True
                except:
                    continue
            
            # If we're on the user's profile, that's also a success
            if f"/accounts/onetap/" in self.driver.current_url or "/feed/" in self.driver.current_url:
                return True
                
            return False
        except:
            return False

    def extract_usernames_from_html(self, html_file):
        """
        Extract usernames from the HTML file of pending follow requests.
        
        Args:
            html_file (str): Path to the HTML file
            
        Returns:
            list: List of usernames
        """
        try:
            print(f"Extracting usernames from {html_file}...")
            
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links to Instagram profiles
            profile_links = soup.find_all('a', href=re.compile(r'https://www\.instagram\.com/[^/]+'))
            
            # Extract usernames from the links
            usernames = []
            for link in profile_links:
                href = link.get('href')
                username = href.replace('https://www.instagram.com/', '').rstrip('/')
                if username and username not in usernames:
                    usernames.append(username)
            
            print(f"Found {len(usernames)} usernames.")
            return usernames
            
        except Exception as e:
            print(f"Error extracting usernames: {str(e)}")
            return []

    def cancel_follow_request(self, username):
        """
        Cancel a follow request for a specific user.
        
        Args:
            username (str): Instagram username
            
        Returns:
            bool: True if the request was cancelled successfully, False otherwise
        """
        if not self.logged_in:
            print("You must be logged in to cancel follow requests.")
            return False
        
        try:
            # Navigate to the user's profile
            print(f"Navigating to {username}'s profile...")
            self.driver.get(f"https://www.instagram.com/{username}/")
            
            # Wait for the page to load
            time.sleep(random.uniform(2, 3))
            
            # Save a screenshot for debugging
            self.driver.save_screenshot(f"/app/data/profile_{username}.png")
            
            # Check if the profile exists
            if "Page Not Found" in self.driver.title or "Sorry, this page isn't available." in self.driver.page_source:
                print(f"Profile not found: {username}")
                return False
            
            # Look for the "Requested" button using multiple selectors
            print(f"Looking for Requested button...")
            requested_button = None
            
            # List of potential selector strategies
            selectors = [
                "//button[contains(., 'Requested')]",
                "//button[.//div[contains(text(), 'Requested')]]",
                "//button[contains(@class, '_acan') and contains(@class, '_acap')]",
                "//div[@role='button' and contains(., 'Requested')]",
                "//div[contains(@class, '_ap3a') and contains(text(), 'Requested')]"
            ]
            
            # Try each selector
            for selector in selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if 'Requested' in button.text:
                            requested_button = button
                            break
                    if requested_button:
                        break
                except:
                    continue
            
            # If we still haven't found it, try a more generic approach
            if not requested_button:
                try:
                    # Find all buttons on the page
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in all_buttons:
                        if 'Requested' in button.text:
                            requested_button = button
                            break
                except:
                    pass
            
            if not requested_button:
                print(f"No Requested button found for {username}")
                return False
            
            # Click the Requested button
            print(f"Clicking Requested button...")
            try:
                requested_button.click()
            except:
                # Try JavaScript click if regular click fails
                self.driver.execute_script("arguments[0].click();", requested_button)
            
            # Wait for the confirmation dialog
            time.sleep(2)
            
            # Save a screenshot of the dialog
            self.driver.save_screenshot(f"/app/data/dialog_{username}.png")
            
            # Look for the "Unfollow" button in the dialog
            unfollow_button = None
            unfollow_selectors = [
                "//button[contains(., 'Unfollow')]",
                "//button[.//div[contains(text(), 'Unfollow')]]",
                "//div[@role='dialog']//button[contains(., 'Unfollow')]",
                "//div[@role='dialog']//button"
            ]
            
            for selector in unfollow_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if 'Unfollow' in button.text or 'Cancel' in button.text:
                            unfollow_button = button
                            break
                    if unfollow_button:
                        break
                except:
                    continue
            
            # If we still haven't found it, try a more generic approach
            if not unfollow_button:
                try:
                    # Find all buttons in the dialog
                    dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
                    buttons = dialog.find_elements(By.TAG_NAME, "button")
                    # Usually the Unfollow button is the first or second button
                    if buttons and len(buttons) >= 1:
                        unfollow_button = buttons[0]
                except:
                    pass
            
            if not unfollow_button:
                print(f"No Unfollow button found in dialog for {username}")
                return False
            
            # Click the Unfollow button
            print(f"Clicking Unfollow button...")
            try:
                unfollow_button.click()
            except:
                # Try JavaScript click if regular click fails
                self.driver.execute_script("arguments[0].click();", unfollow_button)
            
            # Add a random delay to avoid rate limiting
            delay = random.uniform(self.delay_min, self.delay_max)
            print(f"Waiting {delay:.1f} seconds before next request...")
            time.sleep(delay)
            
            print(f"Successfully cancelled follow request for {username}")
            return True
            
        except Exception as e:
            print(f"Error cancelling follow request for {username}: {str(e)}")
            return False

    def cancel_all_requests(self, usernames, batch_size=10, continue_from=0):
        """
        Cancel follow requests for multiple users.
        
        Args:
            usernames (list): List of Instagram usernames
            batch_size (int): Number of requests to cancel in one batch
            continue_from (int): Index to continue from (for resuming)
            
        Returns:
            tuple: (success_count, failed_usernames)
        """
        if not self.logged_in:
            print("You must be logged in to cancel follow requests.")
            return 0, usernames
        
        total = len(usernames)
        success_count = 0
        failed_usernames = []
        
        # Process usernames in batches
        for i in range(continue_from, total):
            username = usernames[i]
            
            print(f"\nProcessing {i+1}/{total}: {username}")
            success = self.cancel_follow_request(username)
            
            if success:
                success_count += 1
            else:
                failed_usernames.append(username)
            
            # Save progress after each request
            self.save_progress(i + 1, success_count, failed_usernames)
            
            # Check if we need to take a break between batches
            if (i + 1) % batch_size == 0 and i + 1 < total:
                batch_delay = random.uniform(20, 30)
                print(f"\nCompleted batch of {batch_size}. Taking a {batch_delay:.1f} second break...")
                time.sleep(batch_delay)
        
        return success_count, failed_usernames

    def save_progress(self, position, success_count, failed_usernames):
        """
        Save the current progress to a file.
        
        Args:
            position (int): Current position in the list
            success_count (int): Number of successful cancellations
            failed_usernames (list): List of usernames that failed
        """
        progress = {
            "position": position,
            "success_count": success_count,
            "failed_usernames": failed_usernames,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("/app/data/instagram_cancellation_progress.json", "w") as f:
            json.dump(progress, f, indent=4)

    def load_progress(self):
        """
        Load progress from a file.
        
        Returns:
            tuple: (position, success_count, failed_usernames)
        """
        try:
            with open("/app/data/instagram_cancellation_progress.json", "r") as f:
                progress = json.load(f)
            
            return progress.get("position", 0), progress.get("success_count", 0), progress.get("failed_usernames", [])
            
        except FileNotFoundError:
            return 0, 0, []
        except Exception as e:
            print(f"Error loading progress: {str(e)}")
            return 0, 0, []

    def close(self):
        """
        Close the browser and clean up.
        """
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("Browser closed.")


def main():
    parser = argparse.ArgumentParser(description='Instagram Pending Follow Requests Cancellation Tool')
    parser.add_argument('--html', type=str, help='Path to the HTML file containing pending follow requests')
    parser.add_argument('--username', type=str, help='Instagram username')
    parser.add_argument('--password', type=str, help='Instagram password')
    parser.add_argument('--no-headless', action='store_true', help='Run with browser UI (not headless)')
    parser.add_argument('--delay-min', type=int, default=2, help='Minimum delay between requests in seconds')
    parser.add_argument('--delay-max', type=int, default=4, help='Maximum delay between requests in seconds')
    parser.add_argument('--batch-size', type=int, default=10, help='Number of requests to cancel in one batch')
    parser.add_argument('--continue', dest='continue_from_last', action='store_true', help='Continue from last saved position')
    parser.add_argument('--usernames-file', type=str, help='Path to a text file with usernames (one per line)')
    
    args = parser.parse_args()
    
    # Create the data directory if it doesn't exist
    os.makedirs("/app/data", exist_ok=True)
    
    # Because we're handling 2FA, we need the browser to be visible during login
    # But we can respect the headless setting for the rest of the process
    is_headless = not args.no_headless
    
    print("Note: When using 2FA, the browser will be visible during login regardless of headless setting.")
    
    # Create the cancellation tool - always set headless to False for 2FA
    tool = InstagramCancellationTool(
        headless=False,  # Always show browser for 2FA 
        delay_min=args.delay_min, 
        delay_max=args.delay_max
    )
    
    try:
        # Login to Instagram
        if not args.username or not args.password:
            args.username = input("Enter your Instagram username: ")
            args.password = input("Enter your Instagram password: ")
        
        if not tool.login(args.username, args.password):
            print("Failed to log in. Exiting.")
            tool.close()
            return
        
        # Get usernames
        usernames = []
        
        if args.html:
            # Extract usernames from HTML file
            usernames = tool.extract_usernames_from_html(args.html)
        elif args.usernames_file:
            # Load usernames from text file
            with open(args.usernames_file, 'r') as f:
                usernames = [line.strip() for line in f.readlines() if line.strip()]
            print(f"Loaded {len(usernames)} usernames from {args.usernames_file}")
        else:
            # Look for HTML file in the data directory
            html_files = list(Path("/app/data").glob("*.html"))
            if html_files:
                html_path = str(html_files[0])
                print(f"Found HTML file: {html_path}")
                usernames = tool.extract_usernames_from_html(html_path)
            else:
                # Ask for HTML file path
                html_path = input("Enter the path to your pending_follow_requests.html file (in /app/data/): ")
                full_path = f"/app/data/{html_path}"
                if os.path.exists(full_path):
                    usernames = tool.extract_usernames_from_html(full_path)
                else:
                    print(f"File not found: {full_path}")
                    tool.close()
                    return
        
        if not usernames:
            print("No usernames found. Exiting.")
            tool.close()
            return
        
        # Ask for confirmation
        print(f"\nFound {len(usernames)} pending follow requests.")
        confirm = input(f"Do you want to cancel them all? (y/n): ")
        
        if confirm.lower() != 'y':
            print("Operation cancelled by user.")
            tool.close()
            return
        
        # Determine starting position
        start_position = 0
        success_count = 0
        failed_usernames = []
        
        if args.continue_from_last:
            start_position, success_count, failed_usernames = tool.load_progress()
            print(f"Continuing from position {start_position} with {success_count} previously successful cancellations.")
            
            # Remove already processed usernames
            usernames = usernames[start_position:]
            
            if not usernames:
                print("All usernames have been processed already.")
                tool.close()
                return
        
        # Cancel the follow requests
        print(f"\nCancelling {len(usernames)} follow requests (batch size: {args.batch_size})...")
        new_success_count, new_failed_usernames = tool.cancel_all_requests(
            usernames, 
            batch_size=args.batch_size,
            continue_from=0  # We've already adjusted the list
        )
        
        total_success = success_count + new_success_count
        total_failed = failed_usernames + new_failed_usernames
        
        print(f"\nCancellation process completed.")
        print(f"Successfully cancelled: {total_success}")
        print(f"Failed to cancel: {len(total_failed)}")
        
        if total_failed:
            print("\nFailed usernames:")
            for username in total_failed:
                print(f"- {username}")
            
            # Save failed usernames to a file
            with open("/app/data/failed_cancellations.txt", "w") as f:
                for username in total_failed:
                    f.write(f"{username}\n")
            print("Failed usernames saved to /app/data/failed_cancellations.txt")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Saving progress...")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Saving progress...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        tool.close()


if __name__ == "__main__":
    main()