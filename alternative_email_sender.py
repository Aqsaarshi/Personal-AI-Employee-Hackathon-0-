#!/usr/bin/env python3
"""
Alternative Email Sender using SMTP
Does not require Google Cloud credentials - uses username/password authentication
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

def send_email_smtp(to_email, subject, body, smtp_server=None, smtp_port=None, username=None, password=None):
    """
    Send email using SMTP with username/password authentication
    """
    try:
        # Load credentials from environment or config file
        if not smtp_server:
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        if not smtp_port:
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
        if not username:
            username = os.getenv('EMAIL_USERNAME')
        if not password:
            password = os.getenv('EMAIL_PASSWORD')
        
        # Validate required credentials
        if not username or not password:
            raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD must be set in environment variables")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(username, password)
        
        # Convert message to string and send
        text = msg.as_string()
        server.sendmail(username, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def create_email_task(to_email, subject, body, priority="Medium"):
    """
    Create an email task file in Needs_Action for processing
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"Email_Task_{timestamp}.md"
    filepath = os.path.join("Needs_Action", filename)
    
    task_content = f"""# Email Task

## Recipient
{to_email}

## Subject
{subject}

## Body
{body}

## Priority
{priority}

## Status
Pending

## Created
{datetime.now().isoformat()}

## Instructions
Process this email task using SMTP authentication.
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(task_content)
    
    print(f"Created email task: {filepath}")
    return filepath

def process_email_tasks():
    """
    Process all email tasks in Needs_Action directory
    """
    import os
    import re
    
    needs_action_dir = "Needs_Action"
    email_tasks = []
    
    for filename in os.listdir(needs_action_dir):
        if filename.startswith("Email_Task_") and filename.endswith(".md"):
            filepath = os.path.join(needs_action_dir, filename)
            email_tasks.append(filepath)
    
    if not email_tasks:
        print("No email tasks found in Needs_Action")
        return
    
    print(f"Found {len(email_tasks)} email task(s) to process")
    
    for task_path in email_tasks:
        print(f"Processing: {task_path}")
        
        with open(task_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract email details using regex
        recipient_match = re.search(r'## Recipient\n(.+)', content)
        subject_match = re.search(r'## Subject\n(.+)', content)
        body_match = re.search(r'## Body\n(.+)', content, re.DOTALL)
        
        if recipient_match and subject_match and body_match:
            to_email = recipient_match.group(1).strip()
            subject = subject_match.group(1).strip()
            body = body_match.group(1).strip()
            
            # Send the email
            success = send_email_smtp(to_email, subject, body)
            
            if success:
                # Move task to Done folder after successful processing
                done_dir = "Done"
                if not os.path.exists(done_dir):
                    os.makedirs(done_dir)
                
                import shutil
                done_path = os.path.join(done_dir, os.path.basename(task_path))
                shutil.move(task_path, done_path)
                print(f"Moved {task_path} to {done_path}")
            else:
                print(f"Failed to send email for task: {task_path}")
        else:
            print(f"Could not parse email details from: {task_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--send":
            # Send a single email
            if len(sys.argv) >= 5:
                to_email = sys.argv[2]
                subject = sys.argv[3]
                body = sys.argv[4]
                send_email_smtp(to_email, subject, body)
            else:
                print("Usage: python alternative_email_sender.py --send <to_email> <subject> <body>")
        elif sys.argv[1] == "--create-task":
            # Create an email task
            if len(sys.argv) >= 5:
                to_email = sys.argv[2]
                subject = sys.argv[3]
                body = sys.argv[4]
                create_email_task(to_email, subject, body)
            else:
                print("Usage: python alternative_email_sender.py --create-task <to_email> <subject> <body>")
        elif sys.argv[1] == "--process-tasks":
            # Process all email tasks
            process_email_tasks()
        else:
            print("Usage:")
            print("  python alternative_email_sender.py --send <to_email> <subject> <body>")
            print("  python alternative_email_sender.py --create-task <to_email> <subject> <body>")
            print("  python alternative_email_sender.py --process-tasks")
    else:
        print("Alternative Email Sender - Use command line options:")
        print("  --send: Send an email directly")
        print("  --create-task: Create an email task in Needs_Action")
        print("  --process-tasks: Process all email tasks in Needs_Action")