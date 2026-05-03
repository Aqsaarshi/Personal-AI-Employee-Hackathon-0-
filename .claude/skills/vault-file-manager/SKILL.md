---
name: vault-file-manager
description: Manage task workflow between Inbox, Needs_Action, and Done
version: 1.0
author: AI Employee System
category: File Management
---

# Vault File Manager Skill

## Purpose
Manage task workflow between different vault directories.

## Usage
Call this skill to move files between directories:
- source: Source directory (inbox, needs_action, done)
- destination: Destination directory (inbox, needs_action, done)
- filename: Name of the file to move

## Example
```python
result = move_task(source="inbox", destination="needs_action", filename="task.md")
```

## Output
Returns success confirmation or error message.