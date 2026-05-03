#!/usr/bin/env python3
"""
WhatsApp Watcher Script
Monitors WhatsApp Web for unread urgent messages using Playwright
Run instructions: python whatsapp_watcher.py (use nohup or tmux to run in background)
"""

import time
import os
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
import re

def setup_logging():
    """Setup logging to file"""
    log_dir = "Logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        filename=os.path.join(log_dir, 'whatsapp_log.md'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_needs_action_file(message_data):
    """Create a .md file in Needs_Action with message details"""
    needs_action_dir = "Needs_Action"
    if not os.path.exists(needs_action_dir):
        os.makedirs(needs_action_dir)

    filename = f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(needs_action_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# WhatsApp Alert\n\n")
        f.write(f"**Contact:** {message_data['contact']}\n\n")
        f.write(f"**Time Received:** {message_data['time']}\n\n")
        f.write(f"**Message:**\n{message_data['message']}\n\n")
        f.write(f"**Keywords Detected:** {', '.join(message_data['keywords'])}\n\n")
        f.write("**Action Required:** Review and respond to this urgent message.\n")

    logging.info(f"Created alert for message from {message_data['contact']}")

def check_whatsapp_messages(page):
    """Check for unread messages with keywords"""
    try:
        # Find chat elements with unread messages
        unread_chats = page.locator('div[aria-label="Chat list"] div[role="row"].unread')

        if unread_chats.count() == 0:
            # Alternative selector for unread messages
            unread_chats = page.locator('div[tabindex="-1"][class*="unread"]')

        keywords = ['urgent', 'invoice', 'asap', 'important', 'critical', 'emergency', 'need', 'help']

        for i in range(unread_chats.count()):
            chat = unread_chats.nth(i)

            # Get contact name
            contact_element = chat.locator('div[data-testid="cell-frame-title"]')
            if not contact_element.count():
                contact_element = chat.locator('._1wjpf')  # Alternative selector

            if contact_element.count():
                contact = contact_element.text_content().strip()

                # Click on the chat to view messages
                try:
                    chat.click(timeout=5000)

                    # Wait for messages to load
                    page.wait_for_timeout(2000)

                    # Get all message bubbles
                    messages = page.locator('div.copyable-text span.selectable-text')

                    for j in range(messages.count()):
                        message_text = messages.nth(j).text_content().lower()

                        # Check for keywords
                        detected_keywords = []
                        for keyword in keywords:
                            if keyword.lower() in message_text:
                                detected_keywords.append(keyword)

                        if detected_keywords:
                            # Get the full message text
                            full_message = messages.nth(j).text_content()

                            message_data = {
                                'contact': contact,
                                'message': full_message,
                                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'keywords': detected_keywords
                            }

                            create_needs_action_file(message_data)

                except TimeoutError:
                    logging.warning(f"Timeout clicking on chat: {contact}")
                    continue

        return True

    except Exception as e:
        logging.error(f"Error checking WhatsApp messages: {str(e)}")
        return False

def main():
    """Main function to run the WhatsApp watcher"""
    setup_logging()
    logging.info("Starting WhatsApp Watcher")

    try:
        with sync_playwright() as p:
            # Launch browser with persistent context to save session
            # Use headless=False for first run to scan QR code
            browser = p.chromium.launch(headless=False)
            
            # Check if session file exists
            if os.path.exists("whatsapp_session.json"):
                context = browser.new_context(
                    storage_state="whatsapp_session.json",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            else:
                # First run - no session saved
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            
            page = context.new_page()

            # Navigate to WhatsApp Web
            logging.info("Navigating to WhatsApp Web...")
            page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=60000)
            
            # Wait for page to fully load
            page.wait_for_timeout(5000)

            # Wait for QR code scan (or use saved session)
            logging.info("Please wait for WhatsApp Web to load...")
            logging.info("If first run, please scan QR code with WhatsApp mobile app")
            try:
                page.wait_for_selector('div[data-testid="chat-list"]', timeout=120000)
                logging.info("Successfully logged in to WhatsApp Web")
                
                # Save session after successful login
                if not os.path.exists("whatsapp_session.json"):
                    context.storage_state(path="whatsapp_session.json")
                    logging.info("Session saved to whatsapp_session.json")
            except TimeoutError:
                logging.error("Failed to log in to WhatsApp Web. Please scan QR code manually and restart.")
                browser.close()
                return

            while True:
                try:
                    # Check for unread messages with keywords
                    success = check_whatsapp_messages(page)

                    if success:
                        logging.info("Checked WhatsApp messages")

                    # Wait 120 seconds before checking again
                    time.sleep(120)

                except KeyboardInterrupt:
                    logging.info("WhatsApp Watcher stopped by user")
                    # Save session state
                    context.storage_state(path="whatsapp_session.json")
                    break
                except Exception as e:
                    logging.error(f"Error in main loop: {str(e)}")
                    time.sleep(120)  # Wait before retrying

            browser.close()

    except Exception as e:
        logging.error(f"Browser error: {str(e)}")

if __name__ == "__main__":
    main()