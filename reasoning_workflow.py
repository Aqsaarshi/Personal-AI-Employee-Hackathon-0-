#!/usr/bin/env python3
"""
AI Employee Reasoning Workflow

Monitors the Inbox for new tasks and creates detailed plan files in Needs_Action.
"""

import os
import time
from datetime import datetime
import shutil
import re

def read_task_file(file_path):
    """Read the content of a task file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def analyze_task(task_content):
    """Analyze the task and extract relevant information."""
    # Simple analysis to determine task details
    lines = task_content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Untitled Task"
    
    # Determine priority based on keywords
    priority = "Medium"
    high_priority_keywords = ["urgent", "important", "asap", "critical", "high"]
    low_priority_keywords = ["low", "later", "eventually", "when_possible"]
    
    content_lower = task_content.lower()
    if any(keyword in content_lower for keyword in high_priority_keywords):
        priority = "High"
    elif any(keyword in content_lower for keyword in low_priority_keywords):
        priority = "Low"
    
    # Determine if human approval is needed based on keywords
    requires_approval = "Yes"
    no_approval_keywords = ["simple", "basic", "informational", "read_only", "research"]
    if any(keyword in content_lower for keyword in no_approval_keywords):
        requires_approval = "No"
    
    # Suggest output format based on task content
    suggested_output = "Detailed report or action plan"
    if "email" in content_lower:
        suggested_output = "Email draft or response"
    elif "post" in content_lower or "social" in content_lower:
        suggested_output = "Social media post draft"
    elif "analysis" in content_lower or "report" in content_lower:
        suggested_output = "Analysis report with recommendations"
    elif "schedule" in content_lower or "meeting" in content_lower:
        suggested_output = "Calendar event or meeting invitation"
    
    return {
        "title": title,
        "priority": priority,
        "requires_approval": requires_approval,
        "suggested_output": suggested_output
    }

def create_plan_file(task_path, task_content, analysis):
    """Create a plan file in Needs_Action with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds for uniqueness
    plan_filename = f"Plan_{timestamp}.md"
    plan_path = os.path.join("Needs_Action", plan_filename)
    
    # Create the plan content
    plan_content = f"""# Task Plan

## Original Task
{task_content}

## Objective
Process the task described above and execute the required actions according to the plan below.

## Step-by-Step Plan
1. Analyze the task requirements in detail
2. Gather any necessary resources or information
3. Execute the planned actions
4. Verify the results meet the objective
5. Document the outcome and move to Done

## Priority
{analysis['priority']}

## Requires Human Approval?
{analysis['requires_approval']}

## Suggested Output
{analysis['suggested_output']}
"""
    
    # Write the plan file
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    return plan_path

def process_new_tasks():
    """Monitor Inbox for new tasks and create plan files."""
    inbox_dir = "Inbox"
    needs_action_dir = "Needs_Action"
    
    # Ensure Needs_Action directory exists
    if not os.path.exists(needs_action_dir):
        os.makedirs(needs_action_dir)
    
    # Get all task files in Inbox
    inbox_files = []
    for filename in os.listdir(inbox_dir):
        if filename.endswith('.md') or filename.endswith('.txt'):
            inbox_files.append(os.path.join(inbox_dir, filename))
    
    if not inbox_files:
        print("No new tasks found in Inbox.")
        return []
    
    created_plans = []
    
    for task_path in inbox_files:
        print(f"Processing task: {task_path}")
        
        # Read the task
        task_content = read_task_file(task_path)
        
        # Analyze the task
        analysis = analyze_task(task_content)
        
        # Create plan file
        plan_path = create_plan_file(task_path, task_content, analysis)
        
        # Print confirmation
        print(f"Created plan file: {plan_path}")
        
        # Optionally move the original task to a processed folder
        processed_dir = "Processed"
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
        
        # Move the original task file to processed
        processed_task_path = os.path.join(processed_dir, os.path.basename(task_path))
        shutil.move(task_path, processed_task_path)
        print(f"Moved original task to: {processed_task_path}")
        
        created_plans.append(plan_path)
    
    return created_plans

def run_workflow():
    """Run the reasoning workflow."""
    print("Starting AI Employee Reasoning Workflow...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    created_plans = process_new_tasks()
    
    if created_plans:
        print(f"\nWorkflow completed. Created {len(created_plans)} plan file(s):")
        for plan in created_plans:
            print(f"  - {plan}")
    else:
        print("\nNo new tasks to process.")
    
    print(f"Workflow finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def run_continuous_monitoring(interval=30):
    """Run the workflow continuously, checking for new tasks every interval seconds."""
    print(f"Starting continuous monitoring. Checking every {interval} seconds...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            run_workflow()
            print(f"Sleeping for {interval} seconds...\n")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Run in continuous monitoring mode
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        run_continuous_monitoring(interval)
    else:
        # Run once
        run_workflow()