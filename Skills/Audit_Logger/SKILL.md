# Audit Logger Skill

## Purpose
The Audit Logger skill maintains comprehensive logs of all actions performed by any skill, including timestamp, skill name, action type, status, and output. It tracks retries for failed actions and maintains structured logs for CEO report integration.

## Configuration
The skill requires a configuration file with logging settings and output options:

```json
{
  "logging": {
    "enabled": true,
    "log_level": "INFO", // DEBUG, INFO, WARNING, ERROR, CRITICAL
    "log_format": "structured", // "structured" or "simple"
    "output": {
      "file": {
        "enabled": true,
        "path": "logs/audit.log",
        "max_size_mb": 10,
        "backup_count": 5
      },
      "console": {
        "enabled": false
      }
    }
  },
  "tracking": {
    "track_retries": true,
    "max_retries_to_log": 5,
    "failed_actions_alert": true
  },
  "reporting": {
    "structured_for_reports": true,
    "include_performance_metrics": true
  }
}
```

## Core Functions

### 1. Logging Schema & Code Example
- Comprehensive logging schema with all required fields
- Timestamp, skill name, action type, status, output
- Performance metrics tracking
- Code examples for integration with other skills

### 2. Integration with All Skills
- Decorator pattern for easy integration
- Context manager for logging around operations
- API for manual logging calls
- Automatic retry tracking

### 3. Retry and Error Reporting Mechanism
- Track retry attempts for failed actions
- Log failed actions with detailed error information
- Generate alerts for persistent failures
- Performance metrics and failure patterns analysis