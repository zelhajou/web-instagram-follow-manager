import os
import json
import time
import argparse
import re
from bs4 import BeautifulSoup
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, TwoFactorRequired

class InstagramCancellationAPI:
    def __init__(self, username=None, password=None):
        """
        Initialize the Instagram API client.
        
        Args:
            username (str): Instagram username
            password (str): Instagram password
        """
        self.username = username
        self.password = password
        self.client = Client()
        self.is_logged_in = False
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Try to load session if it exists
        self.session_file = "data/instagram_session.json"
        if os.path.exists(self.session_file):
            print("Loading existing session...")
            try:
                self.client.load_settings(self.session_file)
                self.client.get_timeline_feed()  # Test if session is valid
                self.is_logged_in = True
                print("Session loaded successfully!")
            except LoginRequired:
                print("Session expired, need to login again.")
                self.is_logged_in = False
    
    def login(self):
        """
        Log in to Instagram.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        if self.is_logged_in:
            print("Already logged in.")
            return True
            
        if not self.username or not self.password:
            self.username = input("Enter your Instagram username: ")
            self.password = input("Enter your Instagram password: ")
        
        print(f"Logging in as {self.username}...")
        
        try:
            # Attempt to login
            self.client.login(self.username, self.password)
            self.is_logged_in = True
            
            # Save session
            self.client.dump_settings(self.session_file)
            print("Login successful and session saved!")
            return True
            
        except TwoFactorRequired:
            print("Two-factor authentication is required.")
            code = input("Enter the code from your authentication app: ")
            try:
                self.client.login(self.username, self.password, verification_code=code)
                self.is_logged_in = True
                self.client.dump_settings(self.session_file)
                print("Login successful and session saved!")
                return True
            except Exception as e:
                print(f"Failed to complete 2FA: {str(e)}")
                return False
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
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
        Cancel a follow request for a specific user using the API.
        
        Args:
            username (str): Instagram username
            
        Returns:
            bool: True if the request was cancelled successfully, False otherwise
        """
        if not self.is_logged_in:
            print("You must be logged in to cancel follow requests.")
            return False
        
        try:
            print(f"Finding user ID for {username}...")
            # Get user ID from username
            user_id = self.client.user_id_from_username(username)
            
            if not user_id:
                print(f"Could not find user ID for {username}")
                return False
            
            print(f"Cancelling follow request for {username} (ID: {user_id})...")
            # Cancel the follow request
            result = self.client.user_unfollow(user_id)
            
            if result:
                print(f"Successfully cancelled follow request for {username}")
                return True
            else:
                print(f"Failed to cancel follow request for {username}")
                return False
                
        except Exception as e:
            print(f"Error cancelling follow request for {username}: {str(e)}")
            return False
    
    def cancel_all_requests(self, usernames, delay=1, batch_size=50, continue_from=0):
        """
        Cancel follow requests for multiple users.
        
        Args:
            usernames (list): List of Instagram usernames
            delay (int): Delay between requests in seconds
            batch_size (int): Number of requests to process before taking a longer break
            continue_from (int): Index to continue from (for resuming)
            
        Returns:
            tuple: (success_count, failed_usernames)
        """
        if not self.is_logged_in:
            print("You must be logged in to cancel follow requests.")
            return 0, usernames
        
        total = len(usernames)
        success_count = 0
        failed_usernames = []
        
        # Process usernames
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
            
            # Add delay between requests to avoid rate limiting
            if i < total - 1:  # Don't delay after the last request
                time.sleep(delay)
            
            # Take a longer break after each batch
            if (i + 1) % batch_size == 0 and i + 1 < total:
                batch_delay = 10
                print(f"\nCompleted batch of {batch_size}. Taking a {batch_delay} second break...")
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
        
        with open("data/instagram_cancellation_progress.json", "w") as f:
            json.dump(progress, f, indent=4)
    
    def load_progress(self):
        """
        Load progress from a file.
        
        Returns:
            tuple: (position, success_count, failed_usernames)
        """
        try:
            with open("data/instagram_cancellation_progress.json", "r") as f:
                progress = json.load(f)
            
            return progress.get("position", 0), progress.get("success_count", 0), progress.get("failed_usernames", [])
            
        except FileNotFoundError:
            return 0, 0, []
        except Exception as e:
            print(f"Error loading progress: {str(e)}")
            return 0, 0, []


def main():
    parser = argparse.ArgumentParser(description='Instagram Pending Follow Requests Cancellation Tool (API Version)')
    parser.add_argument('--html', type=str, help='Path to the HTML file containing pending follow requests')
    parser.add_argument('--username', type=str, help='Instagram username')
    parser.add_argument('--password', type=str, help='Instagram password')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    parser.add_argument('--batch-size', type=int, default=50, help='Number of requests to cancel in one batch')
    parser.add_argument('--continue', dest='continue_from_last', action='store_true', help='Continue from last saved position')
    parser.add_argument('--usernames-file', type=str, help='Path to a text file with usernames (one per line)')
    
    args = parser.parse_args()
    
    # Create the cancellation tool
    tool = InstagramCancellationAPI(args.username, args.password)
    
    try:
        # Login to Instagram
        if not tool.login():
            print("Failed to log in. Exiting.")
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
            html_files = list(filter(lambda f: f.endswith('.html'), os.listdir("data")))
            if html_files:
                html_path = os.path.join("data", html_files[0])
                print(f"Found HTML file: {html_path}")
                usernames = tool.extract_usernames_from_html(html_path)
            else:
                # Ask for HTML file path
                html_path = input("Enter the path to your pending_follow_requests.html file: ")
                if os.path.exists(html_path):
                    usernames = tool.extract_usernames_from_html(html_path)
                else:
                    print(f"File not found: {html_path}")
                    return
        
        if not usernames:
            print("No usernames found. Exiting.")
            return
        
        # Ask for confirmation
        print(f"\nFound {len(usernames)} pending follow requests.")
        confirm = input(f"Do you want to cancel them all? (y/n): ")
        
        if confirm.lower() != 'y':
            print("Operation cancelled by user.")
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
                return
        
        # Cancel the follow requests
        print(f"\nCancelling {len(usernames)} follow requests (batch size: {args.batch_size}, delay: {args.delay}s)...")
        new_success_count, new_failed_usernames = tool.cancel_all_requests(
            usernames, 
            delay=args.delay,
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
            with open("data/failed_cancellations.txt", "w") as f:
                for username in total_failed:
                    f.write(f"{username}\n")
            print("Failed usernames saved to data/failed_cancellations.txt")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Saving progress...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()