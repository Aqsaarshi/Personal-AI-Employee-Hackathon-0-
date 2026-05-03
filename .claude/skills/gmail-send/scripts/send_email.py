#!/usr/bin/env python3
"""
Gmail Send Skill
Send real emails using SMTP authentication
"""

import smtplib
import os
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_email(to, subject, body):
    """
    Send an email using SMTP with Gmail
    """
    try:
        # Get credentials from environment variables
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_address or not email_password:
            return {
                "success": False,
                "error": "EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set"
            }
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to
        msg['Subject'] = Header(subject, 'utf-8')
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP
        server.starttls()  # Enable security
        server.login(email_address, email_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(email_address, to, text)
        server.quit()
        
        return {
            "success": True,
            "message": f"Email sent successfully to {to}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """
    Main function to handle command line execution
    """
    if len(sys.argv) != 4:
        print(json.dumps({
            "success": False,
            "error": "Usage: python send_email.py <to> <subject> <body>"
        }))
        return
    
    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    result = send_email(to, subject, body)
    print(json.dumps(result))

if __name__ == "__main__":
    main()