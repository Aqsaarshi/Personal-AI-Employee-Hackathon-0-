"""
Test script for CEO Briefing Generator
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator

def test_ceo_briefing_generator():
    print("Testing CEO Briefing Generator...")

    # Initialize the CEO Briefing Generator
    generator = CEOBriefingGenerator()
    print("[OK] CEO Briefing Generator initialized")

    # Test getting weekly summary data
    print("\nTesting weekly summary generation...")
    summary_data = generator.get_weekly_summary()
    print(f"[OK] Weekly summary generated with {len(summary_data)} sections")

    # Check that all expected sections are present
    expected_sections = [
        "report_date",
        "reporting_period",
        "financial_summary",
        "social_media_performance",
        "leads_and_opportunities",
        "risks_and_recommendations",
        "performance_metrics"
    ]

    for section in expected_sections:
        if section in summary_data:
            print(f"[OK] {section} section present")
        else:
            print(f"[WARNING] {section} section missing")

    # Test generating and saving the report
    print("\nTesting report generation and saving...")
    saved_files = generator.generate_weekly_report()
    print(f"[OK] Report generated and saved to: {saved_files}")

    # If files were created, check their content
    for file_path in saved_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] File {file_path} created successfully (size: {size} bytes)")

            # Read and display first few lines to verify content
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = ''.join([next(f) for _ in range(min(5, size))]) if size > 0 else ""
                print(f"   Sample content: {first_lines[:100]}...")
        else:
            print(f"[ERROR] File {file_path} was not created")

    # Test with specific week
    print("\nTesting with specific week...")
    specific_files = generator.generate_weekly_report("2026-02-15")
    print(f"[OK] Specific week report generated: {specific_files}")

    print("\n[SUCCESS] CEO Briefing Generator tests completed!")

if __name__ == "__main__":
    test_ceo_briefing_generator()