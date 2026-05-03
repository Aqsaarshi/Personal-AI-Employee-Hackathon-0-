"""
Audit Logger Skill
Logs every action performed by any skill with comprehensive details
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from functools import wraps
import traceback
from logging.handlers import RotatingFileHandler
import threading
import time

# Global instance for easy access
_audit_logger_instance = None

class AuditLogEntry:
    """Represents a single audit log entry"""
    def __init__(self, skill_name: str, action_type: str, status: str,
                 output: str = "", timestamp: str = None, error_details: str = "",
                 performance_metrics: Dict = None, original_action: str = "",
                 retry_count: int = 0, related_logs: list = None):
        self.timestamp = timestamp or datetime.now().isoformat()
        self.skill_name = skill_name
        self.action_type = action_type
        self.status = status  # "success", "failed", "retried", "warning"
        self.output = output
        self.error_details = error_details
        self.performance_metrics = performance_metrics or {}
        self.original_action = original_action
        self.retry_count = retry_count
        self.related_logs = related_logs or []

    def to_dict(self) -> Dict:
        """Convert the log entry to a dictionary"""
        return {
            "timestamp": self.timestamp,
            "skill_name": self.skill_name,
            "action_type": self.action_type,
            "status": self.status,
            "output": self.output,
            "error_details": self.error_details,
            "performance_metrics": self.performance_metrics,
            "original_action": self.original_action,
            "retry_count": self.retry_count,
            "related_logs": self.related_logs
        }

    def to_structured_string(self) -> str:
        """Convert to a structured string format"""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    def __init__(self, config_path: str = "Skills/Audit_Logger/config.json"):
        """Initialize the Audit Logger with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.config["logging"]["output"]["file"]["path"])
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Set up structured logging
        self._setup_logging()

        # For tracking in-progress operations
        self._active_operations = {}
        self._lock = threading.Lock()

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "logging": {
                "enabled": True,
                "log_level": "INFO",
                "log_format": "structured",
                "output": {
                    "file": {
                        "enabled": True,
                        "path": "logs/audit.log",
                        "max_size_mb": 10,
                        "backup_count": 5
                    },
                    "console": {
                        "enabled": False
                    }
                }
            },
            "tracking": {
                "track_retries": True,
                "max_retries_to_log": 5,
                "failed_actions_alert": True
            },
            "reporting": {
                "structured_for_reports": True,
                "include_performance_metrics": True
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
            print(f"Created default configuration at {self.config_path}")
            return default_config

    def _setup_logging(self):
        """Set up the logging system based on configuration."""
        # Create logger
        self.logger = logging.getLogger('AuditLogger')

        # Clear existing handlers
        self.logger.handlers.clear()

        # Set level
        level = getattr(logging, self.config["logging"]["log_level"], logging.INFO)
        self.logger.setLevel(level)

        # Create formatter
        if self.config["logging"]["log_format"] == "structured":
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add file handler if enabled
        if self.config["logging"]["output"]["file"]["enabled"]:
            file_path = self.config["logging"]["output"]["file"]["path"]
            max_bytes = self.config["logging"]["output"]["file"]["max_size_mb"] * 1024 * 1024
            backup_count = self.config["logging"]["output"]["file"]["backup_count"]

            file_handler = RotatingFileHandler(
                file_path, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Add console handler if enabled
        if self.config["logging"]["output"]["console"]["enabled"]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_action(self, skill_name: str, action_type: str, status: str,
                   output: str = "", timestamp: str = None,
                   error_details: str = "", performance_metrics: Dict = None,
                   original_action: str = "", retry_count: int = 0) -> str:
        """Log an action with all required details."""
        if not self.config["logging"]["enabled"]:
            return ""

        log_entry = AuditLogEntry(
            skill_name=skill_name,
            action_type=action_type,
            status=status,
            output=output,
            timestamp=timestamp,
            error_details=error_details,
            performance_metrics=performance_metrics or {},
            original_action=original_action,
            retry_count=retry_count
        )

        # Log to structured file
        log_msg = log_entry.to_structured_string()
        self.logger.info(log_msg)

        # Generate log ID
        log_id = f"audit_{log_entry.timestamp.replace(':', '_').replace('.', '_')}_{skill_name}_{action_type}"

        return log_id

    def log_with_performance(self, skill_name: str, action_type: str,
                           action_func: Callable, *args, **kwargs) -> Any:
        """Log an action and measure its performance."""
        start_time = time.time()

        try:
            # Execute the action
            result = action_func(*args, **kwargs)

            # Calculate performance metrics
            duration = time.time() - start_time
            performance_metrics = {
                "duration_seconds": round(duration, 3),
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.now().isoformat()
            }

            # Log successful action
            self.log_action(
                skill_name=skill_name,
                action_type=action_type,
                status="success",
                output=str(result)[:500] if result else "",  # Limit output length
                performance_metrics=performance_metrics
            )

            return result

        except Exception as e:
            # Calculate performance metrics even for failed actions
            duration = time.time() - start_time
            performance_metrics = {
                "duration_seconds": round(duration, 3),
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.now().isoformat()
            }

            # Log failed action
            error_details = f"{str(e)}\n{traceback.format_exc()}"
            self.log_action(
                skill_name=skill_name,
                action_type=action_type,
                status="failed",
                error_details=error_details,
                performance_metrics=performance_metrics
            )

            # If configured, alert on failed actions
            if self.config["tracking"]["failed_actions_alert"]:
                self.logger.error(f"ACTION FAILED: {skill_name}.{action_type} - {str(e)}")

            raise

    def retry_with_logging(self, skill_name: str, action_type: str,
                          action_func: Callable, max_retries: int = 3,
                          retry_delay: float = 1.0, *args, **kwargs) -> Any:
        """Execute an action with retry logic and comprehensive logging."""
        retry_count = 0

        while retry_count <= max_retries:
            try:
                # Log the retry attempt
                if retry_count > 0:
                    self.log_action(
                        skill_name=skill_name,
                        action_type=action_type,
                        status="retried",
                        output=f"Retry attempt {retry_count}/{max_retries}",
                        retry_count=retry_count
                    )

                # Execute the action with performance tracking
                result = self.log_with_performance(
                    skill_name=skill_name,
                    action_type=action_type,
                    action_func=action_func,
                    *args,
                    **kwargs
                )

                # Success - break out of retry loop
                break

            except Exception as e:
                retry_count += 1

                if retry_count > max_retries:
                    # Final failure after all retries
                    self.log_action(
                        skill_name=skill_name,
                        action_type=action_type,
                        status="failed_after_retries",
                        error_details=str(e),
                        retry_count=retry_count
                    )
                    raise

                # Wait before retry (with exponential backoff)
                time.sleep(retry_delay * (2 ** (retry_count - 1)))

        return result

    def get_logs_by_skill(self, skill_name: str, start_date: str = None,
                         end_date: str = None, limit: int = None) -> list:
        """Retrieve logs for a specific skill."""
        log_file = self.config["logging"]["output"]["file"]["path"]

        if not os.path.exists(log_file):
            return []

        logs = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        # Parse the structured log entry
                        log_entry = json.loads(line.strip())

                        # Check if it matches the criteria
                        if log_entry.get("skill_name") == skill_name:
                            if start_date and log_entry.get("timestamp", "") < start_date:
                                continue
                            if end_date and log_entry.get("timestamp", "") > end_date:
                                continue
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue

        # Sort by timestamp and apply limit
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        if limit:
            logs = logs[:limit]

        return logs

    def get_failed_actions(self, start_date: str = None, end_date: str = None) -> list:
        """Get all failed actions within the date range."""
        log_file = self.config["logging"]["output"]["file"]["path"]

        if not os.path.exists(log_file):
            return []

        failed_logs = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        log_entry = json.loads(line.strip())

                        # Check if status indicates failure
                        status = log_entry.get("status", "")
                        if status in ["failed", "failed_after_retries"]:
                            if start_date and log_entry.get("timestamp", "") < start_date:
                                continue
                            if end_date and log_entry.get("timestamp", "") > end_date:
                                continue
                            failed_logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue

        return failed_logs

    def get_performance_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get performance summary for reporting."""
        log_file = self.config["logging"]["output"]["file"]["path"]

        if not os.path.exists(log_file):
            return {}

        stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "retried_actions": 0,
            "total_duration": 0,
            "avg_duration": 0,
            "slowest_action": None,
            "skills": {}
        }

        logs = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        log_entry = json.loads(line.strip())

                        if start_date and log_entry.get("timestamp", "") < start_date:
                            continue
                        if end_date and log_entry.get("timestamp", "") > end_date:
                            continue

                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue

        # Process logs to calculate statistics
        for log in logs:
            stats["total_actions"] += 1

            # Count by status
            status = log.get("status", "")
            if status == "success":
                stats["successful_actions"] += 1
            elif status in ["failed", "failed_after_retries"]:
                stats["failed_actions"] += 1
            elif status == "retried":
                stats["retried_actions"] += 1

            # Calculate duration stats
            perf_metrics = log.get("performance_metrics", {})
            duration = perf_metrics.get("duration_seconds", 0)
            stats["total_duration"] += duration

            # Track slowest action
            if (stats["slowest_action"] is None or
                perf_metrics.get("duration_seconds", 0) >
                stats.get("slowest_action", {}).get("performance_metrics", {}).get("duration_seconds", 0)):
                stats["slowest_action"] = log

            # Track by skill
            skill = log.get("skill_name")
            if skill not in stats["skills"]:
                stats["skills"][skill] = {
                    "total": 0, "success": 0, "failed": 0, "duration": 0
                }

            stats["skills"][skill]["total"] += 1
            if status == "success":
                stats["skills"][skill]["success"] += 1
            elif status in ["failed", "failed_after_retries"]:
                stats["skills"][skill]["failed"] += 1

            stats["skills"][skill]["duration"] += duration

        # Calculate averages
        if stats["total_actions"] > 0:
            stats["avg_duration"] = stats["total_duration"] / stats["total_actions"]

        # Calculate success rate for each skill
        for skill_stats in stats["skills"].values():
            if skill_stats["total"] > 0:
                skill_stats["success_rate"] = skill_stats["success"] / skill_stats["total"] * 100

        return stats

    def log_context(self, skill_name: str, action_type: str):
        """Context manager for logging around operations."""
        class LogContext:
            def __enter__(ctx):
                self.logger.info(f"Starting {skill_name}.{action_type}")
                return self

            def __exit__(ctx, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    error_msg = f"{exc_type.__name__}: {exc_val}"
                    self.logger.error(f"Failed {skill_name}.{action_type}: {error_msg}")
                    self.log_action(
                        skill_name=skill_name,
                        action_type=action_type,
                        status="failed",
                        error_details=error_msg
                    )
                else:
                    self.logger.info(f"Completed {skill_name}.{action_type}")
                    self.log_action(
                        skill_name=skill_name,
                        action_type=action_type,
                        status="success"
                    )
                return False  # Don't suppress exceptions

        return LogContext()


# Global function to get the audit logger instance
def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance


# Decorator for easy integration with other skills
def audit_log(skill_name: str, action_type: str):
    """Decorator to automatically log function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_audit_logger()
            try:
                result = logger.log_with_performance(
                    skill_name=skill_name,
                    action_type=action_type,
                    action_func=func,
                    *args,
                    **kwargs
                )
                return result
            except Exception:
                # Exception already logged by log_with_performance
                raise
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    print("Audit Logger initialized successfully!")
    print("Features:")
    print("- Comprehensive action logging with timestamps")
    print("- Performance metrics tracking")
    print("- Retry logic with logging")
    print("- Failed action tracking and alerts")
    print("- Performance summary reports")
    print("- Integration decorators and context managers")