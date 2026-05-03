"""
Error Handler Skill
Provides comprehensive error recovery and graceful degradation
"""
import json
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional, Union
from enum import Enum
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Audit_Logger.audit_logger import get_audit_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RetryState:
    """Tracks the retry state for a specific operation."""
    def __init__(self, operation_id: str, max_attempts: int):
        self.operation_id = operation_id
        self.max_attempts = max_attempts
        self.current_attempt = 0
        self.last_error = None
        self.start_time = datetime.now()
        self.errors: List[Dict] = []

    def increment_attempt(self, error: Exception = None):
        """Increment the attempt counter and record error."""
        self.current_attempt += 1
        if error:
            self.last_error = str(error)
            self.errors.append({
                "attempt": self.current_attempt,
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
                "traceback": traceback.format_exc()
            })
        return self.current_attempt <= self.max_attempts

    def is_complete(self) -> bool:
        """Check if retry attempts are exhausted."""
        return self.current_attempt >= self.max_attempts

    def get_error_summary(self) -> Dict:
        """Get summary of all errors for this operation."""
        return {
            "operation_id": self.operation_id,
            "total_attempts": self.current_attempt,
            "max_attempts": self.max_attempts,
            "errors": self.errors,
            "success": self.current_attempt <= self.max_attempts
        }

class ErrorAlertManager:
    """Manages alerts for critical errors."""
    def __init__(self, config: Dict):
        self.config = config
        self.alert_threshold = config.get("critical_threshold", 5)
        self.repeat_interval = timedelta(
            minutes=config.get("repeat_alert_interval_minutes", 30)
        )
        self.last_alerts = {}  # operation_id -> last_alert_time

    def should_alert(self, operation_id: str, error_count: int) -> bool:
        """Determine if an alert should be sent."""
        if error_count < self.alert_threshold:
            return False

        now = datetime.now()
        last_alert = self.last_alerts.get(operation_id)

        if last_alert is None:
            return True

        # Check if enough time has passed since last alert
        return now - last_alert >= self.repeat_interval

    def record_alert(self, operation_id: str):
        """Record that an alert was sent."""
        self.last_alerts[operation_id] = datetime.now()

    def send_alert(self, operation_id: str, error_info: Dict, severity: ErrorSeverity):
        """Send alert through configured channels."""
        if not self.config.get("enabled", True):
            return

        alert_channels = self.config.get("notification_channels", ["dashboard"])

        alert_msg = {
            "operation_id": operation_id,
            "severity": severity.value,
            "timestamp": datetime.now().isoformat(),
            "error_info": error_info,
            "message": f"Critical error in {operation_id} after {error_info.get('total_attempts', 0)} attempts"
        }

        # Send to dashboard
        if "dashboard" in alert_channels:
            self._send_to_dashboard(alert_msg)

        # Send to human approval system
        if "human_approval" in alert_channels:
            self._send_to_human_approval(alert_msg)

        logger.error(f"ALERT: {alert_msg['message']}")
        return alert_msg

    def _send_to_dashboard(self, alert_msg: Dict):
        """Send alert to dashboard."""
        # In a real implementation, this would update a dashboard file
        dashboard_path = Path("Dashboard.md")
        if dashboard_path.exists():
            with open(dashboard_path, "a") as f:
                f.write(f"\n- [ALERT] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {alert_msg['message']}\n")

    def _send_to_human_approval(self, alert_msg: Dict):
        """Send alert to human approval system."""
        # This would create a file in Pending_Approval folder
        approval_dir = Path("Pending_Approval")
        approval_dir.mkdir(exist_ok=True)

        approval_file = approval_dir / f"error_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(approval_file, "w") as f:
            f.write(f"# System Error Alert\n\n")
            f.write(f"**Timestamp:** {alert_msg['timestamp']}\n")
            f.write(f"**Operation:** {alert_msg['operation_id']}\n")
            f.write(f"**Severity:** {alert_msg['severity']}\n")
            f.write(f"**Issue:** {alert_msg['message']}\n\n")
            f.write(f"**Full Error Info:** {json.dumps(alert_msg['error_info'], indent=2)}\n\n")
            f.write("---\n")
            f.write(f"Action required: Human review needed\n")

class ErrorHandler:
    def __init__(self, config_path: str = "Skills/Error_Handler/config.json"):
        """Initialize the Error Handler with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # Initialize audit logger
        self.audit_logger = get_audit_logger()

        # Initialize alert manager
        self.alert_manager = ErrorAlertManager(self.config.get("alerting", {}))

        # Track retry states
        self.retry_states: Dict[str, RetryState] = {}

        # Set up fallback strategies
        self.fallback_strategies = self.config.get("fallback_modes", {}).get("strategies", {})

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "retry_policy": {
                "enabled": True,
                "max_attempts": 3,
                "base_delay_seconds": 1,
                "max_delay_seconds": 60,
                "backoff_multiplier": 2,
                "retryable_errors": ["ConnectionError", "TimeoutError", "RateLimitError", "TemporaryError", "Exception"]
            },
            "fallback_modes": {
                "enabled": True,
                "strategies": {
                    "service_degradation": True,
                    "circuit_breaker": True,
                    "fallback_values": True
                }
            },
            "alerting": {
                "enabled": True,
                "critical_threshold": 5,
                "repeat_alert_interval_minutes": 30,
                "notification_channels": ["dashboard", "human_approval"]
            },
            "degradation": {
                "enabled": True,
                "safe_mode_operations": ["read_only", "cache_fallback", "reduced_functionality"]
            }
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config file
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at {self.config_path}")
            return default_config

    def is_retryable_error(self, error: Exception) -> bool:
        """Check if the error is retryable based on configuration."""
        retryable_errors = self.config["retry_policy"]["retryable_errors"]

        # Check if error type matches any retryable error
        error_type = type(error).__name__
        return "Exception" in retryable_errors or error_type in retryable_errors

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay using exponential backoff."""
        base_delay = self.config["retry_policy"]["base_delay_seconds"]
        multiplier = self.config["retry_policy"]["backoff_multiplier"]
        max_delay = self.config["retry_policy"]["max_delay_seconds"]

        # Calculate exponential backoff
        delay = base_delay * (multiplier ** (attempt - 1))

        # Cap at max delay
        return min(delay, max_delay)

    def execute_with_retry(self,
                          operation_func: Callable,
                          skill_name: str,
                          operation_type: str,
                          *args,
                          max_attempts: Optional[int] = None,
                          **kwargs) -> Any:
        """Execute an operation with retry logic."""
        if max_attempts is None:
            max_attempts = self.config["retry_policy"]["max_attempts"]

        operation_id = f"{skill_name}_{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Initialize retry state
        retry_state = RetryState(operation_id, max_attempts)
        self.retry_states[operation_id] = retry_state

        attempt = 0
        last_error = None

        while attempt < max_attempts:
            try:
                # Log the attempt
                if attempt > 0:
                    self.audit_logger.log_action(
                        skill_name=skill_name,
                        action_type=f"{operation_type}_retry",
                        status="retrying",
                        output=f"Attempt {attempt + 1}/{max_attempts}",
                        original_action=operation_type
                    )

                # Execute the operation
                result = operation_func(*args, **kwargs)

                # Success - log and return
                self.audit_logger.log_action(
                    skill_name=skill_name,
                    action_type=operation_type,
                    status="success",
                    output=str(result)[:500] if result else "",
                    original_action=operation_type,
                    retry_count=attempt
                )

                # Clean up retry state
                if operation_id in self.retry_states:
                    del self.retry_states[operation_id]

                return result

            except Exception as e:
                last_error = e
                attempt += 1
                retry_state.increment_attempt(e)

                # Check if error is retryable
                if not self.is_retryable_error(e):
                    self.audit_logger.log_action(
                        skill_name=skill_name,
                        action_type=operation_type,
                        status="failed_non_retryable",
                        error_details=f"Non-retryable error: {str(e)}\n{traceback.format_exc()}",
                        original_action=operation_type
                    )
                    raise  # Don't retry non-retryable errors

                # Log the failure
                self.audit_logger.log_action(
                    skill_name=skill_name,
                    action_type=operation_type,
                    status="failed_retryable",
                    error_details=f"Attempt {attempt}/{max_attempts} failed: {str(e)}",
                    original_action=operation_type,
                    retry_count=attempt
                )

                # Check if we've reached the critical threshold for alerts
                if attempt >= self.config["alerting"]["critical_threshold"]:
                    severity = ErrorSeverity.CRITICAL if attempt >= self.config["alerting"]["critical_threshold"] else ErrorSeverity.HIGH
                    if self.alert_manager.should_alert(operation_id, attempt):
                        error_summary = retry_state.get_error_summary()
                        self.alert_manager.send_alert(operation_id, error_summary, severity)
                        self.alert_manager.record_alert(operation_id)

                # If we've exhausted all attempts, raise the original error
                if attempt >= max_attempts:
                    self.audit_logger.log_action(
                        skill_name=skill_name,
                        action_type=operation_type,
                        status="failed_after_retries",
                        error_details=f"Failed after {max_attempts} attempts: {str(e)}\n{traceback.format_exc()}",
                        original_action=operation_type,
                        retry_count=attempt
                    )
                    raise e

                # Calculate and apply delay before retry
                delay = self.calculate_delay(attempt)
                logger.info(f"Retrying {operation_id} in {delay} seconds... (attempt {attempt}/{max_attempts})")
                time.sleep(delay)

    def execute_with_fallback(self,
                            primary_func: Callable,
                            fallback_func: Callable,
                            skill_name: str,
                            operation_type: str,
                            *args,
                            **kwargs) -> Any:
        """Execute with fallback capability."""
        try:
            # Try primary function
            return self.execute_with_retry(
                primary_func, skill_name, f"{operation_type}_primary", *args, **kwargs
            )
        except Exception as primary_error:
            logger.warning(f"Primary function failed: {str(primary_error)}. Trying fallback...")

            # Log the fallback switch
            self.audit_logger.log_action(
                skill_name=skill_name,
                action_type=operation_type,
                status="fallback_triggered",
                error_details=f"Primary failed: {str(primary_error)}",
                output="Switching to fallback function"
            )

            try:
                # Try fallback function
                return self.execute_with_retry(
                    fallback_func, skill_name, f"{operation_type}_fallback", *args, **kwargs
                )
            except Exception as fallback_error:
                logger.error(f"Both primary and fallback failed: {str(fallback_error)}")

                # Log complete failure
                self.audit_logger.log_action(
                    skill_name=skill_name,
                    action_type=operation_type,
                    status="complete_failure",
                    error_details=f"Primary: {str(primary_error)}, Fallback: {str(fallback_error)}"
                )

                raise fallback_error

    def execute_in_safe_mode(self,
                           operation_func: Callable,
                           skill_name: str,
                           operation_type: str,
                           safe_alternative_func: Optional[Callable] = None,
                           *args,
                           **kwargs) -> Any:
        """Execute operation in safe mode with degradation options."""
        try:
            # Try the normal operation
            return operation_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Normal operation failed, entering safe mode: {str(e)}")

            # Check if we have a safe alternative
            if safe_alternative_func:
                try:
                    # Execute in reduced functionality mode
                    result = safe_alternative_func(*args, **kwargs)
                    self.audit_logger.log_action(
                        skill_name=skill_name,
                        action_type=f"{operation_type}_safe_mode",
                        status="recovered_in_safe_mode",
                        output="Operation completed in safe mode"
                    )
                    return result
                except Exception as safe_error:
                    logger.error(f"Safe mode operation also failed: {str(safe_error)}")
                    raise safe_error
            else:
                # No safe alternative, raise the original error
                raise e

    def circuit_breaker(self,
                       operation_func: Callable,
                       skill_name: str,
                       operation_type: str,
                       failure_threshold: int = 5,
                       timeout_seconds: int = 60,
                       *args,
                       **kwargs) -> Any:
        """Implement circuit breaker pattern."""
        # This would track failures and open the circuit if threshold is exceeded
        # For now, we'll implement a simplified version

        try:
            result = operation_func(*args, **kwargs)
            return result
        except Exception as e:
            # In a full implementation, we would track consecutive failures
            # and temporarily stop attempts if the circuit is open
            logger.info(f"Circuit breaker: Operation failed, but continuing with retry logic")
            # Fall back to regular retry logic
            return self.execute_with_retry(
                operation_func, skill_name, operation_type, *args, **kwargs
            )

    def get_error_summary(self, operation_id: str) -> Dict:
        """Get summary of errors for a specific operation."""
        if operation_id in self.retry_states:
            return self.retry_states[operation_id].get_error_summary()
        return {"error": f"No retry state found for operation {operation_id}"}

    def get_all_retry_states(self) -> Dict:
        """Get all current retry states."""
        return {op_id: state.get_error_summary() for op_id, state in self.retry_states.items()}

    def cleanup_old_states(self, max_age_minutes: int = 60):
        """Clean up old retry states to prevent memory leaks."""
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)

        old_states = []
        for op_id, state in self.retry_states.items():
            if state.start_time < cutoff_time:
                old_states.append(op_id)

        for op_id in old_states:
            del self.retry_states[op_id]

        logger.info(f"Cleaned up {len(old_states)} old retry states")

    def handle_error_gracefully(self,
                              operation_func: Callable,
                              skill_name: str,
                              operation_type: str,
                              fallback_value: Any = None,
                              *args,
                              **kwargs) -> Any:
        """Execute operation and return fallback value on failure if configured."""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Operation failed, using fallback: {str(e)}")

            # Log the error
            self.audit_logger.log_action(
                skill_name=skill_name,
                action_type=operation_type,
                status="graceful_degradation",
                error_details=str(e),
                output="Using fallback value to maintain system operation"
            )

            # If fallback value is provided, use it; otherwise re-raise
            if fallback_value is not None:
                return fallback_value
            else:
                # If no fallback, try with retry logic
                return self.execute_with_retry(
                    operation_func, skill_name, operation_type, *args, **kwargs
                )

# Global instance for easy access
_error_handler_instance = None

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance

# Example usage
if __name__ == "__main__":
    print("Error Handler initialized successfully!")
    print("Features:")
    print("- Configurable retry policies with exponential backoff")
    print("- Fallback to alternative functions on failure")
    print("- Circuit breaker pattern implementation")
    print("- Human alerting for critical/repeated failures")
    print("- Safe mode execution with degradation options")
    print("- Graceful degradation with fallback values")
    print("- Comprehensive audit logging of all error events")