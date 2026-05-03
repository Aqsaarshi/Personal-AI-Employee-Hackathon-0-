# Autonomous Loop Skill

## Purpose
The Autonomous Loop skill implements a multi-step autonomous execution loop following the PLAN → ACT → VERIFY → REFLECT → RETRY pattern. It coordinates all other skills automatically, ensures safe, repeatable, error-resilient execution, and allows the system to self-correct and adapt to unexpected situations.

## Configuration
The skill requires a configuration file with loop settings and orchestration parameters:

```json
{
  "loop_settings": {
    "enabled": true,
    "max_iterations": 100,
    "iteration_timeout_minutes": 60,
    "pause_between_iterations_seconds": 5
  },
  "planning": {
    "default_planner": "CrossDomain_Manager",
    "planning_timeout_minutes": 10,
    "plan_validation_enabled": true
  },
  "execution": {
    "concurrent_execution": false,
    "execution_timeout_minutes": 30,
    "error_recovery_enabled": true
  },
  "verification": {
    "verification_timeout_minutes": 10,
    "success_threshold": 0.9,
    "verification_methods": ["status_check", "result_validation", "external_verification"]
  },
  "reflection": {
    "learning_enabled": true,
    "adaptation_enabled": true,
    "reflection_timeout_minutes": 5
  }
}
```

## Core Functions

### 1. Loop Pseudocode / Flowchart
- Complete implementation of PLAN → ACT → VERIFY → REFLECT → RETRY cycle
- Visual flowchart representation of the loop
- State management for loop execution
- Termination conditions and safety checks

### 2. Skill Orchestration Method
- Coordinator that manages execution of other skills
- Dependency management between skills
- Resource allocation and conflict resolution
- Execution state tracking and persistence

### 3. Reflection and Retry Logic
- Learning from past execution outcomes
- Adaptive behavior based on experience
- Intelligent retry strategies based on failure patterns
- Continuous improvement of execution strategies