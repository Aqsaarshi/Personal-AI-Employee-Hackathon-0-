# Audit Logger Skill

## Overview
The Audit Logger skill maintains comprehensive logs of all actions performed by any skill, including timestamp, skill name, action type, status, and output. It tracks retries for failed actions and maintains structured logs for CEO report integration.

## Features
- **Comprehensive Action Logging**: Records timestamp, skill name, action type, status, and output
- **Performance Metrics**: Tracks execution time and other performance indicators
- **Retry Tracking**: Monitors and logs retry attempts for failed actions
- **Error Reporting**: Detailed error information with stack traces
- **Structured Logging**: JSON format for easy parsing and reporting
- **Integration Tools**: Decorators and context managers for easy skill integration

## Configuration
The skill uses `config.json` for logging settings:

```json
{
  "logging": {
    "enabled": true,
    "log_level": "INFO",
    "log_format": "structured",
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

## Logging Schema
Each log entry contains:
```json
{
  "timestamp": "2026-02-21T01:15:30.123456",
  "skill_name": "LedgerManager",
  "action_type": "create_entry",
  "status": "success",
  "output": "entry_20260221_011530_0",
  "error_details": "",
  "performance_metrics": {
    "duration_seconds": 0.015,
    "start_time": "2026-02-21T01:15:30.108000",
    "end_time": "2026-02-21T01:15:30.123000"
  },
  "original_action": "",
  "retry_count": 0,
  "related_logs": []
}
```

## Integration Examples

### Using the Decorator
```python
from Skills.Audit_Logger.audit_logger import audit_log

@audit_log(skill_name="MySkill", action_type="process_data")
def my_function(data):
    # Your function logic here
    return processed_data
```

### Using the Context Manager
```python
from Skills.Audit_Logger.audit_logger import get_audit_logger

logger = get_audit_logger()

with logger.log_context("MySkill", "complex_operation"):
    # Your code here
    result = perform_complex_operation()
```

### Manual Logging
```python
from Skills.Audit_Logger.audit_logger import get_audit_logger

logger = get_audit_logger()

# For performance tracking
result = logger.log_with_performance(
    skill_name="MySkill",
    action_type="data_processing",
    action_func=my_function,
    arg1, arg2
)

# For retry logic with logging
result = logger.retry_with_logging(
    skill_name="MySkill",
    action_type="unreliable_operation",
    action_func=unreliable_function,
    max_retries=3,
    arg1, arg2
)
```

### Direct Logging
```python
logger = get_audit_logger()

logger.log_action(
    skill_name="MySkill",
    action_type="manual_action",
    status="success",
    output="Operation completed successfully"
)
```

## Data Access
- **Get logs by skill**: `get_logs_by_skill(skill_name, start_date, end_date, limit)`
- **Get failed actions**: `get_failed_actions(start_date, end_date)`
- **Get performance summary**: `get_performance_summary(start_date, end_date)`

The Audit Logger provides comprehensive tracking of all system activities with structured data suitable for both debugging and executive reporting.