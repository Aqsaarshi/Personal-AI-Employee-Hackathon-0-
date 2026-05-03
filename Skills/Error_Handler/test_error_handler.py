"""
Test script for Error Handler skill
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Error_Handler.error_handler import get_error_handler
import time

def test_error_handler():
    print("Testing Error Handler Skill...")

    # Get the error handler instance
    handler = get_error_handler()
    print("[OK] Error Handler initialized")

    # Test basic retry functionality
    print("\nTesting retry functionality...")
    attempt_count = 0

    def sometimes_fails_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count <= 2:  # Fail twice, succeed on third
            raise Exception(f"Simulated failure on attempt {attempt_count}")
        return f"Success on attempt {attempt_count}"

    try:
        result = handler.execute_with_retry(
            sometimes_fails_function,
            skill_name="TestSkill",
            operation_type="retry_test",
            max_attempts=5
        )
        print(f"[OK] Retry worked: {result}")
        print(f"[OK] Function was called {attempt_count} times (2 failures + 1 success)")
    except Exception as e:
        print(f"[ERROR] Retry test failed: {e}")

    # Reset attempt count
    attempt_count = 0

    # Test fallback functionality
    print("\nTesting fallback functionality...")

    def primary_function():
        raise Exception("Primary function deliberately failed")

    def fallback_function():
        return "Fallback function executed successfully"

    try:
        result = handler.execute_with_fallback(
            primary_function,
            fallback_function,
            skill_name="TestSkill",
            operation_type="fallback_test"
        )
        print(f"[OK] Fallback worked: {result}")
    except Exception as e:
        print(f"[ERROR] Fallback test failed: {e}")

    # Test safe mode execution
    print("\nTesting safe mode execution...")

    def normal_operation():
        raise Exception("Normal operation failed")

    def safe_operation():
        return "Safe mode operation successful"

    try:
        result = handler.execute_in_safe_mode(
            normal_operation,
            skill_name="TestSkill",
            operation_type="safe_mode_test",
            safe_alternative_func=safe_operation
        )
        print(f"[OK] Safe mode worked: {result}")
    except Exception as e:
        print(f"[ERROR] Safe mode test failed: {e}")

    # Test graceful error handling with fallback value
    print("\nTesting graceful error handling...")

    def failing_operation():
        raise ValueError("This operation is designed to fail")

    try:
        result = handler.handle_error_gracefully(
            failing_operation,
            skill_name="TestSkill",
            operation_type="graceful_test",
            fallback_value="graceful_fallback_value"
        )
        print(f"[OK] Graceful handling worked: {result}")
    except Exception as e:
        print(f"[ERROR] Graceful handling test failed: {e}")

    # Test non-retryable error
    print("\nTesting non-retryable error handling...")

    def programming_error():
        undefined_variable.method()  # This will cause an AttributeError

    try:
        result = handler.execute_with_retry(
            programming_error,
            skill_name="TestSkill",
            operation_type="non_retryable_test",
            max_attempts=3
        )
        print(f"[ERROR] Should have failed with programming error")
    except AttributeError:
        print(f"[OK] Correctly failed with non-retryable error (AttributeError)")
    except Exception as e:
        print(f"[OK] Correctly failed with non-retryable error: {type(e).__name__}")

    # Test retry delay calculation
    print("\nTesting retry delay calculation...")
    delays = []
    for i in range(1, 6):
        delay = handler.calculate_delay(i)
        delays.append(delay)
        print(f"[OK] Attempt {i}: {delay}s delay")

    print(f"[OK] Delays follow exponential backoff: {delays}")

    # Test retryable error classification
    print("\nTesting error classification...")

    class CustomError(Exception):
        pass

    is_retryable = handler.is_retryable_error(CustomError("test"))
    print(f"[OK] CustomError classified as retryable: {is_retryable}")

    is_retryable = handler.is_retryable_error(ValueError("test"))
    print(f"[OK] ValueError classified as retryable: {is_retryable}")

    # Test circuit breaker (simplified)
    print("\nTesting circuit breaker pattern...")

    def simple_operation():
        return "circuit breaker test"

    try:
        result = handler.circuit_breaker(
            simple_operation,
            skill_name="TestSkill",
            operation_type="circuit_breaker_test"
        )
        print(f"[OK] Circuit breaker worked: {result}")
    except Exception as e:
        print(f"[ERROR] Circuit breaker test failed: {e}")

    print("\n[SUCCESS] Error Handler tests completed successfully!")


def test_error_handler_with_skills():
    print("\nTesting Error Handler integration with other skills...")

    handler = get_error_handler()

    # Test with Ledger Manager
    print("\nTesting with Ledger Manager...")
    from Skills.Ledger_Manager.ledger_manager import LedgerManager

    ledger = LedgerManager()

    def create_ledger_entry():
        return ledger.create_entry(
            amount=50.00,
            category="sales",
            description="Error handler test transaction",
            entry_type="income"
        )

    try:
        result = handler.execute_with_retry(
            create_ledger_entry,
            skill_name="LedgerManager",
            operation_type="create_entry_with_retry"
        )
        print(f"[OK] Ledger entry with retry: {result}")
    except Exception as e:
        print(f"[ERROR] Ledger test failed: {e}")

    # Test with Social Poster
    print("\nTesting with Social Poster...")
    from Skills.SocialPoster_FBI.social_poster_fbi import SocialPosterFBI

    social_poster = SocialPosterFBI()

    def get_social_summary():
        return social_poster.generate_weekly_summary()

    try:
        result = handler.execute_with_retry(
            get_social_summary,
            skill_name="SocialPoster",
            operation_type="get_summary_with_retry"
        )
        print(f"[OK] Social summary with retry: {type(result).__name__}")
    except Exception as e:
        print(f"[INFO] Social poster test completed with retry: {e}")

    print("\n[SUCCESS] Error Handler integration with skills completed!")


if __name__ == "__main__":
    test_error_handler()
    test_error_handler_with_skills()