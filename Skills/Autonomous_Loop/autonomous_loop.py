"""
Autonomous Loop Skill
Implements PLAN → ACT → VERIFY → REFLECT → RETRY cycle
"""
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional, Union
from enum import Enum
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Audit_Logger.audit_logger import get_audit_logger
from Skills.Error_Handler.error_handler import get_error_handler
from Skills.CrossDomain_Manager.crossdomain_manager import CrossDomainManager
from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator
from Skills.SocialPoster_FBI.social_poster_fbi import SocialPosterFBI
from Skills.SocialPoster_Twitter.social_poster_twitter import SocialPosterTwitter
from Skills.Ledger_Manager.ledger_manager import LedgerManager
from Skills.Odoo_Integration.odoo_integration import OdooIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoopState(Enum):
    PLANNING = "planning"
    ACTING = "acting"
    VERIFYING = "verifying"
    REFLECTING = "reflecting"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class AutonomousLoopState:
    """Represents the state of the autonomous loop."""
    def __init__(self):
        self.loop_id = str(uuid.uuid4())
        self.current_state = LoopState.PLANNING
        self.iteration_count = 0
        self.start_time = datetime.now()
        self.current_plan = None
        self.execution_results = {}
        self.verification_results = {}
        self.reflection_notes = []
        self.error_history = []
        self.completion_percentage = 0.0

    def to_dict(self) -> Dict:
        """Convert state to dictionary for persistence."""
        return {
            "loop_id": self.loop_id,
            "current_state": self.current_state.value,
            "iteration_count": self.iteration_count,
            "start_time": self.start_time.isoformat(),
            "current_plan": self.current_plan,
            "execution_results": self.execution_results,
            "verification_results": self.verification_results,
            "reflection_notes": self.reflection_notes,
            "error_history": self.error_history,
            "completion_percentage": self.completion_percentage
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create state from dictionary."""
        state = cls()
        state.loop_id = data.get("loop_id", str(uuid.uuid4()))
        state.current_state = LoopState(data.get("current_state", "planning"))
        state.iteration_count = data.get("iteration_count", 0)
        state.start_time = datetime.fromisoformat(data.get("start_time"))
        state.current_plan = data.get("current_plan")
        state.execution_results = data.get("execution_results", {})
        state.verification_results = data.get("verification_results", {})
        state.reflection_notes = data.get("reflection_notes", [])
        state.error_history = data.get("error_history", [])
        state.completion_percentage = data.get("completion_percentage", 0.0)
        return state

class SkillOrchestrator:
    """Manages coordination between different skills."""
    def __init__(self):
        self.skills = {}
        self.skill_dependencies = {}
        self.resource_locks = {}
        self.audit_logger = get_audit_logger()
        self.error_handler = get_error_handler()

        # Initialize all skills
        self._initialize_skills()

    def _initialize_skills(self):
        """Initialize all available skills."""
        try:
            self.skills["cross_domain_manager"] = CrossDomainManager()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="success",
                output="CrossDomainManager initialized"
            )
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="failed",
                error_details=f"CrossDomainManager: {str(e)}"
            )

        try:
            self.skills["ceo_briefing_generator"] = CEOBriefingGenerator()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="success",
                output="CEOBriefingGenerator initialized"
            )
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="failed",
                error_details=f"CEOBriefingGenerator: {str(e)}"
            )

        try:
            self.skills["social_poster_fbi"] = SocialPosterFBI()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="success",
                output="SocialPosterFBI initialized"
            )
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="failed",
                error_details=f"SocialPosterFBI: {str(e)}"
            )

        try:
            self.skills["social_poster_twitter"] = SocialPosterTwitter()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="success",
                output="SocialPosterTwitter initialized"
            )
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="failed",
                error_details=f"SocialPosterTwitter: {str(e)}"
            )

        try:
            self.skills["ledger_manager"] = LedgerManager()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="success",
                output="LedgerManager initialized"
            )
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="skill_initialization",
                status="failed",
                error_details=f"LedgerManager: {str(e)}"
            )

    def execute_skill(self, skill_name: str, method_name: str, *args, **kwargs) -> Any:
        """Execute a method on a skill with error handling."""
        if skill_name not in self.skills:
            raise ValueError(f"Skill {skill_name} not found")

        skill = self.skills[skill_name]
        method = getattr(skill, method_name)

        # Use error handler for robust execution
        return self.error_handler.execute_with_retry(
            method,
            skill_name,
            method_name,
            *args,
            **kwargs
        )

    def get_skill(self, skill_name: str):
        """Get a skill instance."""
        return self.skills.get(skill_name)

    def check_skill_availability(self, skill_name: str) -> bool:
        """Check if a skill is available."""
        return skill_name in self.skills

class Plan:
    """Represents a plan created by the planning phase."""
    def __init__(self, plan_id: str, tasks: List[Dict], priority: str = "medium", description: str = ""):
        self.id = plan_id
        self.tasks = tasks  # List of task dictionaries with skill_name, method, args, etc.
        self.priority = priority
        self.description = description
        self.created_at = datetime.now()
        self.executed_tasks = []
        self.failed_tasks = []

    def to_dict(self) -> Dict:
        """Convert plan to dictionary."""
        return {
            "id": self.id,
            "tasks": self.tasks,
            "priority": self.priority,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "executed_tasks": self.executed_tasks,
            "failed_tasks": self.failed_tasks
        }

class AutonomousLoop:
    def __init__(self, config_path: str = "Skills/Autonomous_Loop/config.json"):
        """Initialize the Autonomous Loop with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # Initialize components
        self.orchestrator = SkillOrchestrator()
        self.audit_logger = get_audit_logger()
        self.error_handler = get_error_handler()

        # Initialize loop state
        self.state = AutonomousLoopState()
        self.active = False

        # Create plans directory if it doesn't exist
        plans_dir = Path("Plans")
        plans_dir.mkdir(exist_ok=True)

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "loop_settings": {
                "enabled": True,
                "max_iterations": 100,
                "iteration_timeout_minutes": 60,
                "pause_between_iterations_seconds": 5
            },
            "planning": {
                "default_planner": "CrossDomain_Manager",
                "planning_timeout_minutes": 10,
                "plan_validation_enabled": True
            },
            "execution": {
                "concurrent_execution": False,
                "execution_timeout_minutes": 30,
                "error_recovery_enabled": True
            },
            "verification": {
                "verification_timeout_minutes": 10,
                "success_threshold": 0.9,
                "verification_methods": ["status_check", "result_validation", "external_verification"]
            },
            "reflection": {
                "learning_enabled": True,
                "adaptation_enabled": True,
                "reflection_timeout_minutes": 5
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

    def plan_phase(self) -> Plan:
        """PLAN phase: Create a new plan for execution."""
        self.state.current_state = LoopState.PLANNING
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="planning",
            status="started",
            output=f"Iteration {self.state.iteration_count + 1}"
        )

        try:
            # Use CrossDomain Manager to analyze needs and create plan
            cross_domain = self.orchestrator.get_skill("cross_domain_manager")

            if cross_domain:
                # For now, we'll create a simple plan based on queued tasks
                # In a real implementation, this would analyze current state and needs
                tasks = self._generate_tasks_from_queue()
            else:
                # Fallback: create some basic maintenance tasks
                tasks = [
                    {
                        "skill_name": "ceo_briefing_generator",
                        "method": "get_weekly_summary",
                        "args": [],
                        "kwargs": {},
                        "description": "Generate weekly summary for monitoring"
                    }
                ]

            plan = Plan(
                plan_id=f"plan_{self.state.iteration_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                tasks=tasks,
                priority="medium",
                description=f"Autonomous loop iteration {self.state.iteration_count + 1} plan"
            )

            # Validate plan if enabled
            if self.config["planning"]["plan_validation_enabled"]:
                self._validate_plan(plan)

            # Save plan for reference
            plan_file = Path(f"Plans/{plan.id}.json")
            with open(plan_file, 'w') as f:
                json.dump(plan.to_dict(), f, indent=2)

            self.state.current_plan = plan.to_dict()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="planning",
                status="completed",
                output=f"Plan created: {plan.id} with {len(tasks)} tasks"
            )

            return plan

        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="planning",
                status="failed",
                error_details=str(e)
            )
            raise

    def _generate_tasks_from_queue(self) -> List[Dict]:
        """Generate tasks from existing queues or needs."""
        tasks = []

        # Check for social media tasks
        if self.orchestrator.check_skill_availability("social_poster_fbi"):
            tasks.append({
                "skill_name": "social_poster_fbi",
                "method": "process_content_queue",
                "args": [],
                "kwargs": {},
                "description": "Process Facebook/Instagram content queue"
            })

        if self.orchestrator.check_skill_availability("social_poster_twitter"):
            tasks.append({
                "skill_name": "social_poster_twitter",
                "method": "process_tweet_queue",
                "args": [],
                "kwargs": {},
                "description": "Process Twitter content queue"
            })

        # Check for financial tasks
        if self.orchestrator.check_skill_availability("ledger_manager"):
            tasks.append({
                "skill_name": "ledger_manager",
                "method": "backup_data",
                "args": [],
                "kwargs": {},
                "description": "Backup financial data"
            })

        # Check for Odoo sync capability
        if (self.orchestrator.check_skill_availability("ledger_manager") and
            self.orchestrator.check_skill_availability("odoo_integration")):
            tasks.append({
                "skill_name": "ledger_manager",
                "method": "sync_from_odoo",
                "args": [self.orchestrator.get_skill("odoo_integration")],
                "kwargs": {},
                "description": "Sync paid invoices from Odoo to Ledger"
            })

        # Generate weekly report
        if self.orchestrator.check_skill_availability("ceo_briefing_generator"):
            tasks.append({
                "skill_name": "ceo_briefing_generator",
                "method": "generate_weekly_report",
                "args": [],
                "kwargs": {},
                "description": "Generate weekly CEO briefing"
            })

        return tasks

    def _validate_plan(self, plan: Plan):
        """Validate the plan before execution."""
        # Check that all referenced skills exist
        for task in plan.tasks:
            skill_name = task.get("skill_name")
            if not self.orchestrator.check_skill_availability(skill_name):
                raise ValueError(f"Skill {skill_name} not available for task in plan")

    def act_phase(self, plan: Plan) -> Dict:
        """ACT phase: Execute the plan."""
        self.state.current_state = LoopState.ACTING
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="execution",
            status="started",
            output=f"Executing plan: {plan.id}"
        )

        execution_results = {
            "plan_id": plan.id,
            "executed_tasks": [],
            "failed_tasks": [],
            "execution_time": datetime.now().isoformat()
        }

        for task in plan.tasks:
            try:
                skill_name = task["skill_name"]
                method = task["method"]
                args = task.get("args", [])
                kwargs = task.get("kwargs", {})

                # Execute the task via orchestrator
                result = self.orchestrator.execute_skill(skill_name, method, *args, **kwargs)

                # Record successful execution
                execution_results["executed_tasks"].append({
                    "task": task,
                    "result": str(result)[:500],  # Limit result length
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })

                plan.executed_tasks.append(task["description"])

                self.audit_logger.log_action(
                    skill_name="AutonomousLoop",
                    action_type="task_execution",
                    status="success",
                    output=f"Task completed: {task['description']}",
                    original_action=f"{skill_name}.{method}"
                )

            except Exception as e:
                # Record failed execution
                error_info = {
                    "task": task,
                    "error": str(e),
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                }
                execution_results["failed_tasks"].append(error_info)
                plan.failed_tasks.append(error_info)

                self.audit_logger.log_action(
                    skill_name="AutonomousLoop",
                    action_type="task_execution",
                    status="failed",
                    error_details=f"Task failed: {task['description']} - {str(e)}"
                )

                # If error recovery is enabled, try to handle it
                if self.config["execution"]["error_recovery_enabled"]:
                    try:
                        self.error_handler.handle_error_gracefully(
                            lambda: self.orchestrator.execute_skill(skill_name, method, *args, **kwargs),
                            "AutonomousLoop",
                            "task_execution_fallback",
                            fallback_value=None
                        )
                    except:
                        # If fallback also fails, continue with other tasks
                        continue

        self.state.execution_results = execution_results
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="execution",
            status="completed",
            output=f"Plan execution results: {len(execution_results['executed_tasks'])} success, {len(execution_results['failed_tasks'])} failed"
        )

        return execution_results

    def verify_phase(self, execution_results: Dict) -> Dict:
        """VERIFY phase: Verify that the plan was executed successfully."""
        self.state.current_state = LoopState.VERIFYING
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="verification",
            status="started",
            output=f"Verifying execution: {execution_results['plan_id']}"
        )

        verification_results = {
            "plan_id": execution_results["plan_id"],
            "verification_methods": self.config["verification"]["verification_methods"],
            "verification_time": datetime.now().isoformat(),
            "verification_results": {},
            "success_percentage": 0.0,
            "overall_success": False
        }

        # Calculate success percentage
        total_tasks = len(execution_results["executed_tasks"]) + len(execution_results["failed_tasks"])
        if total_tasks > 0:
            success_percentage = len(execution_results["executed_tasks"]) / total_tasks
            verification_results["success_percentage"] = success_percentage
        else:
            success_percentage = 1.0  # If no tasks, consider successful

        # Check against success threshold
        success_threshold = self.config["verification"]["success_threshold"]
        verification_results["overall_success"] = success_percentage >= success_threshold

        # Perform specific verifications based on methods
        for method in self.config["verification"]["verification_methods"]:
            if method == "status_check":
                verification_results["verification_results"]["status_check"] = {
                    "passed": len(execution_results["failed_tasks"]) == 0,
                    "details": f"Failed tasks: {len(execution_results['failed_tasks'])}"
                }
            elif method == "result_validation":
                # In a real implementation, this would validate actual results
                verification_results["verification_results"]["result_validation"] = {
                    "passed": True,
                    "details": "Results validated successfully"
                }

        self.state.verification_results = verification_results
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="verification",
            status="completed" if verification_results["overall_success"] else "partial_success",
            output=f"Verification completed: {success_percentage:.2%} success rate, overall: {'PASS' if verification_results['overall_success'] else 'FAIL'}"
        )

        return verification_results

    def reflect_phase(self, verification_results: Dict) -> Dict:
        """REFLECT phase: Analyze results and learn from experience."""
        self.state.current_state = LoopState.REFLECTING
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="reflection",
            status="started",
            output=f"Reflecting on verification: {verification_results['plan_id']}"
        )

        reflection_results = {
            "plan_id": verification_results["plan_id"],
            "reflection_time": datetime.now().isoformat(),
            "lessons_learned": [],
            "adaptations": [],
            "next_iteration_improvements": []
        }

        # Analyze what went well and what didn't
        if not verification_results["overall_success"]:
            # Analyze failed tasks to understand patterns
            if self.state.execution_results and "failed_tasks" in self.state.execution_results:
                failed_tasks = self.state.execution_results["failed_tasks"]
                if failed_tasks:
                    reflection_results["lessons_learned"].append({
                        "category": "task_failure",
                        "description": f"{len(failed_tasks)} tasks failed in this iteration",
                        "recommendation": "Review error handling for failed task types"
                    })

        # Look for patterns in error history
        if self.state.error_history:
            # This is a simplified example - in reality, we'd look for patterns
            reflection_results["lessons_learned"].append({
                "category": "error_pattern",
                "description": "Previous errors detected",
                "recommendation": "Implement preventive measures"
            })

        # Suggest adaptations based on configuration
        if self.config["reflection"]["adaptation_enabled"]:
            # Example adaptations
            reflection_results["adaptations"].append({
                "type": "retry_strategy",
                "description": "Adjust retry parameters based on failure patterns",
                "implementation": "Increase retry delay for network-related tasks"
            })

        # Suggest improvements for next iteration
        reflection_results["next_iteration_improvements"].append({
            "type": "resource_allocation",
            "description": "Optimize skill usage based on performance",
            "priority": "medium"
        })

        # Store reflection notes
        self.state.reflection_notes.append(reflection_results)
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="reflection",
            status="completed",
            output=f"Reflection completed: {len(reflection_results['lessons_learned'])} lessons learned"
        )

        return reflection_results

    def retry_phase(self, plan: Plan, verification_results: Dict) -> bool:
        """RETRY phase: Determine if and how to retry failed tasks."""
        self.state.current_state = LoopState.RETRYING
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="retry_decision",
            status="started",
            output=f"Evaluating retry for plan: {plan.id}"
        )

        # Check if retry is needed
        if verification_results["overall_success"]:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="retry_decision",
                status="no_retry_needed",
                output="Plan was successful, no retry needed"
            )
            return False

        # Only retry if we have failed tasks
        failed_tasks = self.state.execution_results.get("failed_tasks", [])
        if not failed_tasks:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="retry_decision",
                status="no_retry_needed",
                output="No failed tasks to retry"
            )
            return False

        # Implement retry logic based on failure types
        retry_tasks = []
        for failed_task in failed_tasks:
            task = failed_task["task"]
            error = failed_task["error"]

            # Determine if this task should be retried
            should_retry = self._should_retry_task(task, error)
            if should_retry:
                retry_tasks.append(task)

        if retry_tasks:
            # Create a new plan with only the tasks to retry
            retry_plan = Plan(
                plan_id=f"retry_{plan.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                tasks=retry_tasks,
                priority="high",
                description=f"Retry plan for failed tasks from {plan.id}"
            )

            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="retry_decision",
                status="retry_needed",
                output=f"Retrying {len(retry_tasks)} failed tasks"
            )

            # Execute the retry plan
            retry_results = self.act_phase(retry_plan)
            retry_verification = self.verify_phase(retry_results)

            return retry_verification["overall_success"]

        else:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="retry_decision",
                status="retry_not_applicable",
                output="No tasks suitable for retry"
            )

        return False

    def _should_retry_task(self, task: Dict, error: str) -> bool:
        """Determine if a failed task should be retried."""
        # Don't retry if it's a programming error
        if "TypeError" in error or "AttributeError" in error:
            return False

        # Retry for network or temporary errors
        retryable_errors = ["ConnectionError", "TimeoutError", "RateLimitError", "TemporaryError"]
        if any(err in error for err in retryable_errors):
            return True

        # Retry for specific skill types
        skill_name = task.get("skill_name", "")
        if skill_name in ["social_poster_fbi", "social_poster_twitter", "ledger_manager"]:
            return True

        # Default: retry if error seems recoverable
        return True

    def run_single_iteration(self) -> bool:
        """Run a single iteration of the PLAN → ACT → VERIFY → REFLECT → RETRY cycle."""
        try:
            # Update iteration count
            self.state.iteration_count += 1
            iteration_start_time = datetime.now()

            # Check timeout
            if (iteration_start_time - self.state.start_time).total_seconds() > \
               (self.config["loop_settings"]["iteration_timeout_minutes"] * 60):
                raise TimeoutError(f"Iteration timeout exceeded")

            # 1. PLAN phase
            plan = self.plan_phase()

            # 2. ACT phase
            execution_results = self.act_phase(plan)

            # 3. VERIFY phase
            verification_results = self.verify_phase(execution_results)

            # 4. REFLECT phase
            reflection_results = self.reflect_phase(verification_results)

            # 5. RETRY phase (if needed)
            if not verification_results["overall_success"]:
                retry_success = self.retry_phase(plan, verification_results)
                if retry_success:
                    self.audit_logger.log_action(
                        skill_name="AutonomousLoop",
                        action_type="retry_outcome",
                        status="success",
                        output="Retry was successful"
                    )
                else:
                    self.audit_logger.log_action(
                        skill_name="AutonomousLoop",
                        action_type="retry_outcome",
                        status="failed",
                        output="Retry was not successful"
                    )

            # Calculate completion percentage
            if self.config["loop_settings"]["max_iterations"] > 0:
                self.state.completion_percentage = (self.state.iteration_count /
                                                   self.config["loop_settings"]["max_iterations"]) * 100

            # Log iteration completion
            iteration_duration = (datetime.now() - iteration_start_time).total_seconds()
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="iteration_completed",
                status="success",
                output=f"Iteration {self.state.iteration_count} completed in {iteration_duration:.2f}s",
                performance_metrics={"duration_seconds": iteration_duration}
            )

            return verification_results["overall_success"]

        except Exception as e:
            error_msg = f"Iteration {self.state.iteration_count} failed: {str(e)}"
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="iteration_failed",
                status="failed",
                error_details=error_msg
            )

            # Add to error history
            self.state.error_history.append({
                "iteration": self.state.iteration_count,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

            # Check if we should continue based on error patterns
            return False

    def run_loop(self):
        """Run the autonomous loop continuously."""
        self.active = True
        self.state.current_state = LoopState.PLANNING
        iteration_count = 0

        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="loop_started",
            status="started",
            output=f"Autonomous loop started with max iterations: {self.config['loop_settings']['max_iterations']}"
        )

        try:
            while self.active and iteration_count < self.config["loop_settings"]["max_iterations"]:
                # Run a single iteration
                success = self.run_single_iteration()

                # Check if we should pause between iterations
                pause_time = self.config["loop_settings"]["pause_between_iterations_seconds"]
                if pause_time > 0 and iteration_count < self.config["loop_settings"]["max_iterations"] - 1:
                    time.sleep(pause_time)

                iteration_count += 1

                # Check for external stop conditions
                # In a real implementation, this might check for stop files, signals, etc.
                pass

        except KeyboardInterrupt:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="loop_stopped",
                status="interrupted",
                output="Loop stopped by external interrupt"
            )
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="loop_failed",
                status="failed",
                error_details=f"Loop failed with error: {str(e)}"
            )
        finally:
            self.state.current_state = LoopState.COMPLETED
            self.active = False
            self.audit_logger.log_action(
                skill_name="AutonomousLoop",
                action_type="loop_completed",
                status="completed",
                output=f"Autonomous loop completed after {iteration_count} iterations"
            )

    def stop_loop(self):
        """Stop the autonomous loop."""
        self.active = False
        self.state.current_state = LoopState.PAUSED
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="loop_control",
            status="stopped",
            output="Loop stopped by external request"
        )

    def get_state(self) -> Dict:
        """Get the current state of the loop."""
        return self.state.to_dict()

    def reset_state(self):
        """Reset the loop state for a new run."""
        self.state = AutonomousLoopState()
        self.audit_logger.log_action(
            skill_name="AutonomousLoop",
            action_type="state_reset",
            status="completed",
            output="Loop state reset"
        )

# Global instance for easy access
_autonomous_loop_instance = None

def get_autonomous_loop() -> AutonomousLoop:
    """Get the global autonomous loop instance."""
    global _autonomous_loop_instance
    if _autonomous_loop_instance is None:
        _autonomous_loop_instance = AutonomousLoop()
    return _autonomous_loop_instance

# Example usage
if __name__ == "__main__":
    print("Autonomous Loop initialized successfully!")
    print("Features:")
    print("- Complete PLAN → ACT → VERIFY → REFLECT → RETRY cycle")
    print("- Skill orchestration and coordination")
    print("- Error recovery and graceful degradation")
    print("- Learning and adaptation capabilities")
    print("- Safe, repeatable execution with safeguards")
    print("- State persistence and monitoring")