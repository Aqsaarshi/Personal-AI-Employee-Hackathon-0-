---
name: linkedin-post
description: Create real LinkedIn posts using browser automation
version: 1.0
author: AI Employee System
category: Social Media
---

# LinkedIn Post Skill

## Purpose
Create real LinkedIn posts using browser automation.

## Usage
Call this skill to create a LinkedIn post with the following parameter:
- content: The text content of the post

## Prerequisites
Set environment variables:
- LINKEDIN_EMAIL: Your LinkedIn email address
- LINKEDIN_PASSWORD: Your LinkedIn password

## Example
```python
result = post_linkedin(content="Your post content here")
```

## Output
Returns success confirmation or error message.