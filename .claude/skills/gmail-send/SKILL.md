---
name: gmail-send
description: Send real emails using SMTP
version: 1.0
author: AI Employee System
category: Communication
---

# Gmail Send Skill

## Purpose
Send real emails using SMTP authentication.

## Usage
Call this skill to send emails with the following parameters:
- to: Recipient email address
- subject: Email subject line
- body: Email content

## Prerequisites
Set environment variables:
- EMAIL_ADDRESS: Your Gmail address
- EMAIL_PASSWORD: Your Gmail app password

## Example
```python
result = send_email(to="recipient@example.com", subject="Hello", body="Message content")
```

## Output
Returns success confirmation or error message.