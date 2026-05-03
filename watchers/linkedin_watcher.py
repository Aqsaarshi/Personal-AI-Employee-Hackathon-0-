#!/usr/bin/env python3
"""
LinkedIn Watcher - Simple All-in-One
Login + Post + Monitor
"""

import time
import os
import random
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# ---------------- POST TEMPLATES ----------------
POSTS = [
    "🌟 Success tip: Always prioritize customer satisfaction #Success #BusinessTips",
    "💡 Did you know? 89% of companies compete on customer experience #BusinessInsights",
    "🚀 Digital transformation is essential for modern business #Innovation",
    "📈 Data-driven decisions outperform intuition #Leadership #Strategy",
    "🎯 Focus: Building stronger communication channels #Productivity",
    "🤝 Relationships matter: Social selling = 78% more leads #Networking",
    "🔥 AI is transforming every industry #Trends #Innovation",
    "⭐ Success is a journey - celebrate small wins #Wisdom",
    "📊 Sustainability is a key business differentiator #Business",
    "💡 Technology enables new business models #Innovation #Tech"
]

# ---------------- LOGGING ----------------
def log_message(message):
    log_dir = Path("Logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = log_dir / "linkedin_watcher.md"
    
    entry = f"[{timestamp}] {message}\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(message)

# ---------------- GET CREDENTIALS ----------------
def get_credentials():
    env_path = Path(".env")
    email = None
    password = None
    
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("LINKEDIN_EMAIL="):
                    email = line.split("=", 1)[1].strip()
                elif line.startswith("LINKEDIN_PASSWORD="):
                    password = line.split("=", 1)[1].strip()
    
    return email, password

# ---------------- LOGIN ----------------
def login(page, email, password):
    try:
        log_message("🔐 Logging in...")
        page.goto("https://www.linkedin.com/login", timeout=60000)
        time.sleep(3)
        
        page.fill("input[name='session_key']", email)
        page.fill("input[name='session_password']", password)
        page.click("button[type='submit']")
        time.sleep(5)
        
        if "feed" in page.url:
            log_message("   ✅ Login successful!")
            return True
        else:
            log_message("   ⚠️ Please complete login manually...")
            time.sleep(10)
            return "feed" in page.url
            
    except Exception as e:
        log_message(f"   ❌ Login error: {e}")
        return False

# ---------------- CHECK LOGIN ----------------
def is_logged_in(page):
    try:
        page.goto("https://www.linkedin.com/feed/", timeout=30000)
        time.sleep(3)
        page.wait_for_selector("button[aria-label='Create a post']", timeout=5000)
        return True
    except:
        return False

# ---------------- CREATE POST ----------------
def create_post(page, content):
    try:
        log_message("📝 Creating post...")
        
        # Go to feed with retry
        for attempt in range(3):
            try:
                log_message(f"   Loading feed (attempt {attempt+1}/3)...")
                page.goto("https://www.linkedin.com/feed/", timeout=120000, wait_until="domcontentloaded")
                time.sleep(5)
                break
            except Exception as e:
                if attempt == 2:
                    log_message(f"   ❌ Failed to load feed after 3 attempts")
                    return False
                log_message(f"   ⚠️ Retry {attempt+1}...")
                time.sleep(3)
        
        # Click create post - try multiple selectors
        log_message("   Opening post creator...")
        
        create_post_selectors = [
            "button[aria-label='Create a post']",
            "button:has-text('Start a post')",
            ".share-box-feed-entry__trigger",
            "div[role='button']:has-text('Start a post')",
        ]
        
        clicked = False
        for selector in create_post_selectors:
            try:
                page.click(selector, timeout=10000)
                log_message(f"   ✅ Clicked: {selector}")
                clicked = True
                break
            except:
                continue
        
        if not clicked:
            log_message("   ❌ Could not find create post button")
            return False
        
        time.sleep(5)
        
        # Take screenshot for debugging
        page.screenshot(path="debug_post_modal.png")
        log_message("   📸 Screenshot saved: debug_post_modal.png")
        
        # Fill content - try multiple selectors with proper event triggering
        log_message("   Writing content...")

        content_selectors = [
            "div[contenteditable='true']",
            "textarea[aria-label='What do you want to talk about?']",
            "div.editor-textarea",
        ]

        filled = False
        for selector in content_selectors:
            try:
                editor = page.locator(selector).first
                editor.click()
                time.sleep(0.5)
                
                # Clear existing content
                page.keyboard.press("Control+A")
                page.keyboard.press("Delete")
                time.sleep(0.5)
                
                # Type content slowly to trigger input events
                editor.type(content, delay=50)
                time.sleep(2)
                
                # Press Enter then Backspace to ensure content is registered
                page.keyboard.press("Enter")
                page.keyboard.press("Backspace")
                time.sleep(1)
                
                log_message(f"   ✅ Filled: {selector}")
                filled = True
                break
            except:
                continue

        if not filled:
            log_message("   ❌ Could not fill content")
            return False
        
        time.sleep(3)

        # Click post button - try multiple selectors with wait loop
        log_message("   Looking for Post button...")

        post_selectors = [
            "button[aria-label='Post']",
            "button:has-text('Post')",
            "button.post-button",
            "div[role='dialog'] button:has-text('Post')",
        ]

        # Wait for button to become enabled (LinkedIn sometimes delays this)
        max_wait = 30
        wait_interval = 5

        for i in range(max_wait // wait_interval):
            for selector in post_selectors:
                try:
                    post_btn = page.locator(selector).first
                    if post_btn.is_visible():
                        if post_btn.is_enabled():
                            log_message("   📤 Clicking Post button...")
                            post_btn.click()
                            time.sleep(3)

                            # Check if Post settings modal appeared
                            log_message("   Checking for Post settings modal...")
                            
                            # Look for "Anyone" option or Post settings modal
                            settings_modal = page.locator("div[role='dialog']").first
                            
                            # Check if this is the settings modal by looking for "Who can see your post"
                            if settings_modal.inner_text().find("Who can see your post") != -1:
                                log_message("   ⚙️ Post settings modal detected...")

                                # Click "Anyone" option to select visibility
                                try:
                                    anyone_option = page.locator("text='Anyone'").first
                                    if anyone_option.is_visible():
                                        log_message("   ✅ Selected: Anyone")
                                        anyone_option.click()
                                        time.sleep(2)
                                except:
                                    pass

                                # Click "Done" button first
                                try:
                                    done_btn = settings_modal.locator("button:has-text('Done')").first
                                    if done_btn.is_visible() and done_btn.is_enabled():
                                        log_message("   ✅ Clicked Done button")
                                        done_btn.click()
                                        time.sleep(2)
                                except:
                                    log_message("   ⚠️ Done button not found, continuing...")

                                # Click final Post button in settings modal
                                try:
                                    final_post_btn = settings_modal.locator("button:has-text('Post')").last
                                    if final_post_btn.is_visible() and final_post_btn.is_enabled():
                                        log_message("   📤 Clicking final Post button...")
                                        final_post_btn.click()
                                        time.sleep(5)
                                        log_message("   ✅ Post published!")

                                        # Log to file
                                        log_dir = Path("Logs")
                                        log_dir.mkdir(exist_ok=True)
                                        post_log = log_dir / "linkedin_posts.md"

                                        with open(post_log, "a", encoding="utf-8") as f:
                                            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {content}\n\n")

                                        return True
                                except Exception as e:
                                    log_message(f"   ⚠️ Could not click final Post button: {e}")
                                    # Take screenshot for debugging
                                    page.screenshot(path="debug_post_settings.png")
                                    log_message("   📸 Screenshot saved: debug_post_settings.png")
                                    return False
                            else:
                                # No settings modal, post was published directly
                                time.sleep(3)
                                log_message("   ✅ Post published!")

                                log_dir = Path("Logs")
                                log_dir.mkdir(exist_ok=True)
                                post_log = log_dir / "linkedin_posts.md"

                                with open(post_log, "a", encoding="utf-8") as f:
                                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {content}\n\n")

                                return True
                        else:
                            log_message(f"   ⏳ Button found but disabled, waiting... ({(i+1)*wait_interval}s)")
                except:
                    continue

            time.sleep(wait_interval)

        # Final attempt - search all buttons in dialog for 'Post'
        try:
            dialog = page.locator("div[role='dialog']").first
            buttons = dialog.locator("button").all()
            for btn in buttons:
                text = btn.inner_text().strip()
                if text.lower() == 'post':
                    if btn.is_visible() and btn.is_enabled():
                        log_message("   Publishing...")
                        btn.click()
                        time.sleep(5)
                        log_message("   ✅ Post published!")

                        log_dir = Path("Logs")
                        log_dir.mkdir(exist_ok=True)
                        post_log = log_dir / "linkedin_posts.md"

                        with open(post_log, "a", encoding="utf-8") as f:
                            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {content}\n\n")

                        return True
                    break
        except:
            pass

        # Take final screenshot
        page.screenshot(path="debug_post_button.png")
        log_message("   📸 Screenshot saved: debug_post_button.png")
        log_message("   ❌ Post button not found or disabled")
        return False
            
    except Exception as e:
        log_message(f"   ❌ Error: {e}")
        return False

# ---------------- MAIN ----------------
def main():
    print("=" * 50)
    print("  LINKEDIN WATCHER - SIMPLE")
    print("=" * 50)
    
    email, password = get_credentials()
    
    if not email or not password:
        print("\n❌ Error: LINKEDIN_EMAIL and LINKEDIN_PASSWORD not set in .env")
        return
    
    try:
        with sync_playwright() as p:
            # Launch browser
            log_message("🌐 Launching browser...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            # Check login
            log_message("🔐 Checking login status...")
            if not is_logged_in(page):
                if not login(page, email, password):
                    print("\n❌ Login failed. Please check credentials.")
                    browser.close()
                    return
            
            log_message("\n✅ Logged in successfully!\n")
            
            # Menu
            print("\n" + "=" * 50)
            print("  MENU")
            print("=" * 50)
            print("  1. Post once now")
            print("  2. Auto-post every hour")
            print("  3. Exit")
            print("=" * 50)
            
            choice = input("\nSelect option (1/2/3): ").strip()
            
            if choice == "1":
                # Post once
                post_content = random.choice(POSTS)
                log_message(f"\n📄 Post: {post_content}")
                create_post(page, post_content)
                
            elif choice == "2":
                # Auto-post
                log_message("\n⏰ Auto-posting started (every 60 minutes)...")
                last_post = time.time()
                interval = 3600  # 1 hour
                
                try:
                    while True:
                        if (time.time() - last_post) >= interval:
                            post_content = random.choice(POSTS)
                            log_message(f"\n📄 Posting: {post_content}")
                            create_post(page, post_content)
                            last_post = time.time()
                        
                        log_message(f"⏳ Next post in {int((interval - (time.time() - last_post)) / 60)} minutes...")
                        time.sleep(60)
                        
                except KeyboardInterrupt:
                    log_message("\n\n🛑 Auto-posting stopped")
            
            elif choice == "3":
                log_message("Exiting...")
            
            browser.close()
            
    except Exception as e:
        log_message(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
