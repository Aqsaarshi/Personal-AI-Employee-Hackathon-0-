# Cross-Domain Manager Skill

## Overview
The Cross-Domain Manager skill provides unified task management across personal and business domains. It integrates data from all watcher scripts and social media sources to create a centralized system for task creation, updates, deadlines, priorities, and status tracking.

## Features
- **Unified Task Management**: Manages both personal and business tasks in a single system
- **Multi-Source Integration**: Works with data from Gmail, LinkedIn, WhatsApp, Vault, and social media
- **Automatic Classification**: Determines if tasks are personal or business based on content
- **Smart Prioritization**: Assigns priorities based on urgency and importance indicators
- **Deadline Management**: Sets and tracks task deadlines
- **Status Tracking**: Maintains task lifecycle from creation to completion
- **Domain-Specific Rules**: Applies different rules and priorities for personal vs business tasks
- **Cross-Domain Reporting**: Generates unified reports across all domains

## Architecture

### Domain Structure
The skill creates separate folders for personal and business tasks:
- `Personal_Tasks/` - Personal task files
- `Business_Tasks/` - Business task files

### Task File Format
Each task is stored as a Markdown file with structured metadata:
```markdown
# Task Title
**ID:** business_gmail_20260221_143022
**Domain:** business
**Source:** gmail
**Priority:** high
**Status:** created
**Deadline:** 2026-02-24
**Created:** 2026-02-21T14:30:22.123456
**Assigned to:** analyst_team
**Tags:** business, report, q1, urgent
**Dependencies:** data_collection, market_analysis

---
## Description
Task content goes here...

---
## Task Progress
- [ ] Initial assessment
- [ ] Planning phase
- [ ] Execution phase
- [ ] Completion review

---
## Notes
_Add notes here as the task progresses_
```

## Configuration
The skill uses a JSON configuration file (`config.json`) that defines domain-specific rules:

```json
{
  "domains": {
    "personal": {
      "folder": "Personal_Tasks",
      "priorities": ["low", "medium", "high"],
      "default_deadline": "7d"
    },
    "business": {
      "folder": "Business_Tasks",
      "priorities": ["low", "medium", "high", "critical"],
      "default_deadline": "3d"
    }
  },
  "integration_sources": [
    "gmail",
    "linkedin",
    "whatsapp",
    "vault",
    "social_media"
  ]
}
```

## Usage Examples

### Creating a Task
```python
from crossdomain_manager import CrossDomainManager

cdm = CrossDomainManager()
raw_task_data = {
    "title": "Prepare Q1 Business Report",
    "content": "The client needs the Q1 business report asap. This is urgent and critical for the upcoming meeting with stakeholders.",
    "source": "gmail",
    "source_id": "email_12345"
}

task_file = cdm.create_task(raw_task_data)
```

### Updating Task Status
```python
cdm.update_task_status("business_gmail_20260221_143022", "in_progress")
```

### Getting Domain Summary
```python
business_summary = cdm.get_domain_summary("business")
unified_summary = cdm.get_unified_summary()
```

## Integration with Watchers
The Cross-Domain Manager is designed to work seamlessly with all watcher scripts:
- Gmail Watcher
- LinkedIn Watcher
- WhatsApp Watcher
- Vault Watcher
- Social Media Watchers

It automatically processes data from these sources and creates appropriately classified tasks.