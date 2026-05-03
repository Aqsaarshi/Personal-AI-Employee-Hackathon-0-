#!/usr/bin/env python3
"""
LinkedIn Post Skill
Create real LinkedIn posts using browser automation with persistent sessions
"""

import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Persistent user data directory for saving LinkedIn session
USER_DATA_DIR = Path(__file__).parent.parent / "linkedin_session"

def post_linkedin(content, headless=False):
    """
    Create a LinkedIn post using browser automation with persistent session
    
    Args:
        content: The post content to publish
        headless: Run browser in headless mode (default False for visibility)
    
    Returns:
        dict with success status and message/error
    """
    try:
        # Ensure user data directory exists
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            # Launch browser with persistent user data directory
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-gpu"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            # Get the first page or create a new one
            page = browser.pages[0] if browser.pages else browser.new_page()

            print("🌐 Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)

            # Check if already logged in
            is_logged_in = False
            try:
                page.wait_for_selector("button[aria-label='Create a post']", timeout=10000)
                is_logged_in = True
                print("✅ Already logged in")
            except:
                pass

            if not is_logged_in:
                print("🔐 Not logged in. Checking credentials...")
                linkedin_email = os.getenv('LINKEDIN_EMAIL')
                linkedin_password = os.getenv('LINKEDIN_PASSWORD')

                if not linkedin_email or not linkedin_password:
                    browser.close()
                    return {
                        "success": False,
                        "error": "Not logged in and no credentials found. Run: python linkedin_login_simple.py"
                    }

                print("📝 Logging in with credentials...")
                page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
                
                # Wait for login form and fill credentials
                page.wait_for_selector("input[name='session_key']", timeout=10000)
                page.fill("input[name='session_key']", linkedin_email)
                page.fill("input[name='session_password']", linkedin_password)
                page.click("button[type='submit']")
                
                try:
                    page.wait_for_url("https://www.linkedin.com/feed/*", timeout=30000)
                    print("✅ Login successful")
                except:
                    if "feed" not in page.url and "login" in page.url:
                        browser.close()
                        return {"success": False, "error": "Login failed. Check credentials or run: python linkedin_login_simple.py"}
                    print("✅ Logged in (URL:", page.url, ")")

            # Create the post
            print("📝 Creating post...")
            page.click("button[aria-label='Create a post']", timeout=10000)
            page.wait_for_selector("div[contenteditable='true']", timeout=10000)
            
            # Type the content
            page.fill("div[contenteditable='true']", content)
            time.sleep(2)
            
            # Click post button
            post_button = page.locator("button[aria-label='Post']")
            if post_button.is_enabled():
                print("📤 Publishing post...")
                post_button.click()
                time.sleep(5)
                browser.close()
                return {"success": True, "message": "LinkedIn post published successfully"}
            else:
                browser.close()
                return {"success": False, "error": "Post button disabled"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """
    Main function to handle command line execution
    """
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python post_linkedin.py <content>"
        }))
        return
    
    content = sys.argv[1]
    
    result = post_linkedin(content)
    print(json.dumps(result))

if __name__ == "__main__":
    main()