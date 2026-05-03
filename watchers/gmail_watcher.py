#!/usr/bin/env python3
"""
Gmail Watcher Script
Monitors Gmail for unread important emails using Google API
Run instructions: python gmail_watcher.py (use nohup or tmux to run in background)
"""

import time
import os
import json
import logging
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def setup_logging():
    """Setup logging to file"""
    log_dir = "Logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        filename=os.path.join(log_dir, 'gmail_log.md'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def authenticate_gmail():
    """Authenticate with Gmail API using credentials.json"""
    creds = None

    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found. Please set up Gmail API access.")
                print("Setup steps:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API")
                print("4. Create credentials (OAuth 2.0 Client ID)")
                print("5. Download credentials.json and place in vault root")
                print("6. Run this script to complete authentication")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def check_unread_emails(service):
    """Check for unread important emails"""
    try:
        # Query for unread important emails
        results = service.users().messages().list(
            userId='me',
            q='is:unread is:important category:primary',
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            # Extract headers
            headers = msg['payload']['headers']
            subject = ''
            sender = ''
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    sender = header['value']

            # Extract snippet
            snippet = msg.get('snippet', '')

            # Create .md file in Needs_Action
            needs_action_dir = "Needs_Action"
            if not os.path.exists(needs_action_dir):
                os.makedirs(needs_action_dir)

            filename = f"gmail_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{message['id']}.md"
            filepath = os.path.join(needs_action_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Gmail Alert\n\n")
                f.write(f"**From:** {sender}\n\n")
                f.write(f"**Subject:** {subject}\n\n")
                f.write(f"**Time Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Snippet:**\n{snippet}\n\n")
                f.write(f"**Action Required:** Review and respond to this important email.\n")

            logging.info(f"Created alert for email from {sender} with subject '{subject}'")

        return len(messages)

    except Exception as e:
        logging.error(f"Error checking emails: {str(e)}")
        return 0

def main():
    """Main function to run the Gmail watcher"""
    setup_logging()
    logging.info("Starting Gmail Watcher")

    creds = authenticate_gmail()
    if not creds:
        logging.error("Failed to authenticate with Gmail API")
        return

    try:
        service = build('gmail', 'v1', credentials=creds)

        while True:
            try:
                count = check_unread_emails(service)
                if count > 0:
                    logging.info(f"Found {count} unread important email(s)")

                # Wait 120 seconds before checking again
                time.sleep(120)

            except KeyboardInterrupt:
                logging.info("Gmail Watcher stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                time.sleep(120)  # Wait before retrying

    except Exception as e:
        logging.error(f"Gmail API error: {str(e)}")

if __name__ == "__main__":
    main()