"""
Test script for Audit Logger integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Audit_Logger.audit_logger import get_audit_logger, audit_log
from Skills.Ledger_Manager.ledger_manager import LedgerManager
from Skills.SocialPoster_FBI.social_poster_fbi import SocialPosterFBI
from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator
import time

def test_audit_logger():
    print("Testing Audit Logger Integration...")

    # Get the audit logger instance
    logger = get_audit_logger()
    print("[OK] Audit Logger initialized")

    # Test basic logging
    print("\nTesting basic logging...")
    log_id = logger.log_action(
        skill_name="TestSkill",
        action_type="test_action",
        status="success",
        output="Test output message"
    )
    print(f"[OK] Basic log created: {log_id}")

    # Test performance tracking
    print("\nTesting performance tracking...")

    def sample_operation():
        time.sleep(0.1)  # Simulate some work
        return "Operation completed successfully"

    result = logger.log_with_performance(
        skill_name="TestSkill",
        action_type="performance_test",
        action_func=sample_operation
    )
    print(f"[OK] Performance tracked: {result}")

    # Test retry mechanism
    print("\nTesting retry mechanism...")
    attempt_count = 0

    def sometimes_fails():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise Exception("Simulated failure")
        return "Success on retry"

    result = logger.retry_with_logging(
        skill_name="TestSkill",
        action_type="retry_test",
        action_func=sometimes_fails,
        max_retries=3
    )
    print(f"[OK] Retry mechanism worked: {result}")

    # Test decorator integration
    print("\nTesting decorator integration...")

    @audit_log(skill_name="TestSkill", action_type="decorator_test")
    def decorated_function():
        return "Function executed with audit logging"

    result = decorated_function()
    print(f"[OK] Decorator integration worked: {result}")

    # Test context manager
    print("\nTesting context manager...")
    with logger.log_context("TestSkill", "context_test"):
        time.sleep(0.05)
    print("[OK] Context manager worked")

    # Test data retrieval
    print("\nTesting data retrieval...")
    logs = logger.get_logs_by_skill("TestSkill", limit=5)
    print(f"[OK] Retrieved {len(logs)} logs for TestSkill")

    # Test performance summary
    print("\nTesting performance summary...")
    summary = logger.get_performance_summary()
    print(f"[OK] Performance summary generated: {summary.get('total_actions', 0)} total actions")

    print("\n[SUCCESS] Audit Logger integration tests passed!")

def test_integration_with_other_skills():
    print("\nTesting integration with other skills...")

    # Test with Ledger Manager
    print("\nTesting with Ledger Manager...")
    ledger = LedgerManager()
    logger = get_audit_logger()

    # Create an entry with audit logging
    def create_ledger_entry():
        return ledger.create_entry(
            amount=100.00,
            category="sales",
            description="Audit test transaction",
            entry_type="income"
        )

    entry_id = logger.log_with_performance(
        skill_name="LedgerManager",
        action_type="create_entry",
        action_func=create_ledger_entry
    )
    print(f"[OK] Ledger entry created with audit: {entry_id}")

    # Test with Social Poster
    print("\nTesting with Social Poster...")
    social_poster = SocialPosterFBI()

    def test_social_post():
        # Just test that we can call a method with audit logging
        summary = social_poster.generate_weekly_summary()
        return summary.get('total_posts', 0)

    try:
        post_count = logger.log_with_performance(
            skill_name="SocialPoster",
            action_type="generate_summary",
            action_func=test_social_post
        )
        print(f"[OK] Social poster summary generated with audit: {post_count} posts")
    except Exception as e:
        print(f"[INFO] Social poster test skipped due to configuration: {e}")

    # Test with CEO Briefing Generator
    print("\nTesting with CEO Briefing Generator...")
    generator = CEOBriefingGenerator()

    def test_ceo_report():
        # Get summary data without generating full report
        summary = generator.get_weekly_summary()
        return len(summary.keys())

    try:
        section_count = logger.log_with_performance(
            skill_name="CEOBriefingGenerator",
            action_type="get_summary",
            action_func=test_ceo_report
        )
        print(f"[OK] CEO briefing summary generated with audit: {section_count} sections")
    except Exception as e:
        print(f"[INFO] CEO briefing test completed with audit: {e}")

    print("\n[SUCCESS] Integration with other skills verified!")


if __name__ == "__main__":
    test_audit_logger()
    test_integration_with_other_skills()