---
name: human-approval
description: Human-in-the-loop for sensitive actions
version: 1.0
author: AI Employee System
category: Approval Workflow
---

# Human Approval Skill

## Purpose
Handle human-in-the-loop approval for sensitive actions.

## Usage
Call this skill to request human approval for an action:
- action_type: Type of action requiring approval
- details: Details about the action
- identifier: Unique identifier for the approval request

## Example
```python
result = request_approval(action_type="email_send", details={"to": "user@example.com", "subject": "Important"}, identifier="email_123")
```

## Output
Returns approval status (pending, approved, rejected) or error message.