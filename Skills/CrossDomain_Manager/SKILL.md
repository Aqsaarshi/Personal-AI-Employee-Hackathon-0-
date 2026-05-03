# Cross-Domain Manager Skill

## Purpose
The Cross-Domain Manager skill provides unified task management across personal and business domains, integrating data from all watcher scripts and social media sources. It handles task creation, updates, deadlines, priorities, and maintains centralized task tracking.

## Configuration
The skill requires a configuration file to define domain-specific settings:

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

## Core Functions

### 1. Task Creation and Classification
- Receives raw data from watchers
- Classifies tasks as personal or business
- Creates structured task files with metadata

### 2. Task Prioritization
- Analyzes task urgency and importance
- Assigns priority levels based on domain rules
- Updates task status in real-time

### 3. Deadline Management
- Sets deadlines based on domain-specific rules
- Sends reminders before deadlines
- Handles deadline extensions

### 4. Status Tracking
- Maintains task lifecycle: created → pending → in_progress → completed/failed
- Updates dashboard with status changes
- Tracks completion metrics

### 5. Cross-Domain Reporting
- Generates unified reports across domains
- Provides progress analytics
- Identifies bottlenecks and inefficiencies