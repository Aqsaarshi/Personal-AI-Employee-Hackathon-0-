# Error Handler Skill

## Overview
The Error Handler skill provides comprehensive error recovery and graceful degradation capabilities. It automatically retries failed actions with configurable settings, provides fallback modes for partial failures, alerts humans for critical or repeated failures, and ensures the system continues safely during partial errors.

## Features
- **Configurable Retry Policy**: Exponential backoff with customizable parameters
- **Fallback Strategies**: Multiple fallback approaches for different failure scenarios
- **Circuit Breaker Pattern**: Prevents system overload during persistent failures
- **Alerting System**: Critical failure notifications via multiple channels
- **Safe Mode Execution**: Reduced functionality to maintain system operation
- **Comprehensive Audit Logging**: Complete tracking of all error events
- **Graceful Degradation**: Continues operation with reduced functionality when possible

## Configuration
The skill uses `config.json` for error handling settings:

```json
{
  "retry_policy": {
    "enabled": true,
    "max_attempts": 3,
    "base_delay_seconds": 1,
    "max_delay_seconds": 60,
    "backoff_multiplier": 2,
    "retryable_errors": ["ConnectionError", "TimeoutError", "RateLimitError", "TemporaryError", "Exception"]
  },
  "fallback_modes": {
    "enabled": true,
    "strategies": {
      "service_degradation": true,
      "circuit_breaker": true,
      "fallback_values": true
    }
  },
  "alerting": {
    "enabled": true,
    "critical_threshold": 5,
    "repeat_alert_interval_minutes": 30,
    "notification_channels": ["dashboard", "human_approval"]
  },
  "degradation": {
    "enabled": true,
    "safe_mode_operations": ["read_only", "cache_fallback", "reduced_functionality"]
  }
}
```

## Core Components

### 1. Retry System
- **Exponential Backoff**: Increases delay between retry attempts
- **Configurable Parameters**: Max attempts, delay ranges, backoff multiplier
- **Retryable Error Classification**: Determines which errors should be retried
- **Retry State Tracking**: Monitors attempt counts and error history

### 2. Fallback Strategies
- **Service Degradation**: Reduces functionality instead of failing completely
- **Circuit Breaker**: Temporarily stops requests during persistent failures
- **Fallback Values**: Returns safe default values when primary operation fails
- **Alternative Operations**: Switches to backup functions when primary fails

### 3. Alerting System
- **Threshold-based Alerts**: Triggers alerts after specific failure counts
- **Rate Limiting**: Prevents alert spam with configurable intervals
- **Multiple Channels**: Dashboard updates and human approval requests
- **Critical Error Detection**: Identifies and prioritizes severe issues

## Usage Examples

### Execute with Retry
```python
from Skills.Error_Handler.error_handler import get_error_handler

handler = get_error_handler()

def unstable_operation():
    # Some operation that might fail
    pass

result = handler.execute_with_retry(
    unstable_operation,
    skill_name="MySkill",
    operation_type="critical_operation",
    max_attempts=5
)
```

### Execute with Fallback
```python
def primary_function():
    # Primary operation
    pass

def fallback_function():
    # Fallback operation
    return "safe_default_value"

result = handler.execute_with_fallback(
    primary_function,
    fallback_function,
    skill_name="MySkill",
    operation_type="critical_operation"
)
```

### Execute in Safe Mode
```python
def normal_operation():
    # Normal operation that might fail
    pass

def safe_mode_operation():
    # Reduced functionality operation
    pass

result = handler.execute_in_safe_mode(
    normal_operation,
    skill_name="MySkill",
    operation_type="critical_operation",
    safe_alternative_func=safe_mode_operation
)
```

### Graceful Error Handling
```python
result = handler.handle_error_gracefully(
    risky_operation,
    skill_name="MySkill",
    operation_type="risky_operation",
    fallback_value="default_response"
)
```

## Error Recovery Guide

### Retry Policy Implementation
The retry system uses exponential backoff:
1. First attempt: 1 second delay
2. Second attempt: 2 seconds delay (1 * 2^1)
3. Third attempt: 4 seconds delay (1 * 2^2)
4. And so on, capped at max delay

### Fallback Strategies
1. **Primary → Fallback**: Try primary operation, fall back on failure
2. **Safe Mode**: Execute in reduced functionality mode
3. **Circuit Breaker**: Stop operations temporarily during persistent failures
4. **Graceful Degradation**: Continue with partial functionality

### Alerting Logic
1. Monitor failure count per operation
2. When threshold reached (>5 failures by default), send alert
3. Rate limit alerts (default every 30 minutes)
4. Send to configured channels (dashboard, human approval)

The Error Handler provides robust protection against failures while maintaining system stability and operation.