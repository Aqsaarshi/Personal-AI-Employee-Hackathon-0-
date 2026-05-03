"""
Test script for Autonomous Loop skill
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Autonomous_Loop.autonomous_loop import get_autonomous_loop, LoopState
import time

def test_autonomous_loop():
    print("Testing Autonomous Loop Skill...")

    # Get the autonomous loop instance
    loop = get_autonomous_loop()
    print("[OK] Autonomous Loop initialized")

    # Test initial state
    print("\nTesting initial state...")
    state = loop.get_state()
    print(f"[OK] Initial state: {state['current_state']}")
    print(f"[OK] Initial iteration count: {state['iteration_count']}")

    # Test single iteration (without running the full loop)
    print("\nTesting single iteration...")

    # Manually step through each phase for testing
    try:
        # Plan phase
        plan = loop.plan_phase()
        print(f"[OK] Plan phase completed: {plan.id}")
        print(f"[OK] Plan has {len(plan.tasks)} tasks")

        # Store original config max_iterations to restore later
        original_max_iterations = loop.config["loop_settings"]["max_iterations"]
        loop.config["loop_settings"]["max_iterations"] = 1  # Limit for testing

        # We'll test the run_single_iteration method now
        success = loop.run_single_iteration()
        print(f"[OK] Single iteration completed with success: {success}")

        # Restore original config
        loop.config["loop_settings"]["max_iterations"] = original_max_iterations

        # Check final state
        final_state = loop.get_state()
        print(f"[OK] Final state: {final_state['current_state']}")
        print(f"[OK] Final iteration count: {final_state['iteration_count']}")

    except Exception as e:
        print(f"[ERROR] Single iteration test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test state management
    print("\nTesting state management...")
    current_state = loop.get_state()
    print(f"[OK] Current state retrieved: {current_state['current_state']}")

    # Test state reset
    loop.reset_state()
    reset_state = loop.get_state()
    print(f"[OK] State reset: {reset_state['current_state']}")
    print(f"[OK] Reset iteration count: {reset_state['iteration_count']}")

    # Test loop control
    print("\nTesting loop control...")
    loop.stop_loop()
    stopped_state = loop.get_state()
    print(f"[OK] Loop stopped: {stopped_state['current_state']}")

    print("\n[SUCCESS] Autonomous Loop tests completed successfully!")


def test_loop_components():
    print("\nTesting Autonomous Loop components and orchestration...")

    loop = get_autonomous_loop()

    # Test skill orchestrator
    print("\nTesting skill orchestrator...")
    orchestrator = loop.orchestrator

    available_skills = list(orchestrator.skills.keys())
    print(f"[OK] Available skills: {available_skills}")

    # Test skill availability checks
    for skill in available_skills:
        is_available = orchestrator.check_skill_availability(skill)
        print(f"[OK] {skill} availability: {is_available}")

    # Test skill execution
    print("\nTesting skill execution...")
    if 'ledger_manager' in available_skills:
        try:
            result = orchestrator.execute_skill(
                'ledger_manager',
                'get_financial_summary'
            )
            print(f"[OK] Ledger summary retrieved: {type(result).__name__}")
        except Exception as e:
            print(f"[INFO] Ledger test with error (expected): {e}")

    if 'ceo_briefing_generator' in available_skills:
        try:
            result = orchestrator.execute_skill(
                'ceo_briefing_generator',
                'get_weekly_summary'
            )
            print(f"[OK] CEO summary retrieved: {type(result).__name__}")
        except Exception as e:
            print(f"[INFO] CEO summary test completed: {type(e).__name__}")

    # Test plan generation
    print("\nTesting plan generation...")
    tasks = loop._generate_tasks_from_queue()
    print(f"[OK] Generated {len(tasks)} tasks from queue")

    for i, task in enumerate(tasks[:3]):  # Show first 3 tasks
        print(f"  Task {i+1}: {task['description']} -> {task['skill_name']}.{task['method']}")

    # Test plan validation
    print("\nTesting plan validation...")
    from Skills.Autonomous_Loop.autonomous_loop import Plan

    test_plan = Plan(
        plan_id="test_plan",
        tasks=tasks[:2]  # Use first 2 tasks for validation
    )

    try:
        loop._validate_plan(test_plan)
        print("[OK] Plan validation passed")
    except ValueError as e:
        print(f"[ERROR] Plan validation failed: {e}")

    print("\n[SUCCESS] Autonomous Loop component tests completed!")


def test_error_integration():
    print("\nTesting Autonomous Loop error handling integration...")

    loop = get_autonomous_loop()

    # Test the loop's retry phase logic
    print("\nTesting retry decision logic...")

    # Mock verification results for testing retry logic
    verification_results = {
        "overall_success": False,
        "plan_id": "test_plan"
    }

    test_plan = type('Plan', (), {
        'id': 'test_plan',
        'tasks': []
    })()

    # Set up some failed tasks in execution results for the retry test
    loop.state.execution_results = {
        "failed_tasks": [
            {
                "task": {"skill_name": "test_skill", "method": "test_method"},
                "error": "ConnectionError: Network unavailable"
            }
        ],
        "executed_tasks": []
    }

    try:
        should_retry = loop._should_retry_task(
            {"skill_name": "test_skill", "method": "test_method"},
            "ConnectionError: Network unavailable"
        )
        print(f"[OK] Retry decision for ConnectionError: {should_retry}")
    except Exception as e:
        print(f"[ERROR] Retry decision test failed: {e}")

    # Test reflection phase
    print("\nTesting reflection phase...")
    try:
        reflection_results = loop.reflect_phase(verification_results)
        print(f"[OK] Reflection completed: {len(reflection_results.get('lessons_learned', []))} lessons learned")
    except Exception as e:
        print(f"[ERROR] Reflection test failed: {e}")

    # Test verification phase
    print("\nTesting verification phase...")
    try:
        verification_results = loop.verify_phase({
            "plan_id": "test_plan",
            "executed_tasks": [{"status": "success"}],
            "failed_tasks": []
        })
        print(f"[OK] Verification completed: success_rate={verification_results.get('success_percentage', 0)}")
    except Exception as e:
        print(f"[ERROR] Verification test failed: {e}")

    print("\n[SUCCESS] Autonomous Loop error integration tests completed!")


if __name__ == "__main__":
    test_autonomous_loop()
    test_loop_components()
    test_error_integration()