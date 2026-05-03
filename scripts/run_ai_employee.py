#!/usr/bin/env python3
"""
AI Employee Scheduler
Automatically processes tasks from Inbox using the task-planner skill
"""

import os
import time
import subprocess
import sys
import json
from datetime import datetime
import schedule
import threading

def check_inbox():
    """
    Check the Inbox directory for new tasks
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "..")
    inbox_path = os.path.join(base_path, "Inbox")
    
    if not os.path.exists(inbox_path):
        print(f"Inbox directory does not exist: {inbox_path}")
        return []
    
    # Get all .md and .txt files in the Inbox
    inbox_files = []
    for filename in os.listdir(inbox_path):
        if filename.endswith(('.md', '.txt')):
            inbox_files.append(filename)
    
    return inbox_files

def run_task_planner():
    """
    Run the task-planner skill to process new tasks
    """
    print(f"[{datetime.now()}] Running task-planner on Inbox...")
    
    # Check for new tasks in Inbox
    inbox_files = check_inbox()
    
    if not inbox_files:
        print("No new tasks found in Inbox.")
        return
    
    print(f"Found {len(inbox_files)} task(s) in Inbox: {inbox_files}")
    
    # For each task file, run the task-planner
    for filename in inbox_files:
        print(f"Processing task: {filename}")
        
        # In a real implementation, this would call the task-planner skill
        # For now, we'll simulate by running the reasoning workflow we created earlier
        try:
            # Run the reasoning workflow to create plans
            result = subprocess.run([
                sys.executable, 
                os.path.join(os.path.dirname(__file__), "..", "..", "reasoning_workflow.py")
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"Successfully processed: {filename}")
                print(result.stdout)
            else:
                print(f"Error processing {filename}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"Timeout processing {filename}")
        except Exception as e:
            print(f"Error running task-planner on {filename}: {str(e)}")

def run_scheduler():
    """
    Main scheduler function
    """
    print("Starting AI Employee Scheduler...")
    print(f"Scheduler started at {datetime.now()}")
    print("Will run task-planner every 5 minutes to check for new tasks in Inbox")
    
    # Schedule the task-planner to run every 5 minutes
    schedule.every(5).minutes.do(run_task_planner)
    
    # Also run once at startup
    print("\nRunning initial task-planner check...")
    run_task_planner()
    
    print("\nScheduler is now running. Press Ctrl+C to stop.")
    
    # Run the scheduler in a loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Check every second
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Scheduler stopped by user")

def show_setup_instructions():
    """
    Show instructions for setting up automatic execution
    """
    print("\n" + "="*60)
    print("SETUP INSTRUCTIONS FOR AUTOMATIC EXECUTION")
    print("="*60)
    
    import platform
    os_name = platform.system()
    
    if os_name == "Windows":
        print("WINDOWS TASK SCHEDULER SETUP:")
        print("1. Press Win + R, type 'taskschd.msc', and press Enter")
        print("2. Click 'Create Basic Task...' in the right panel")
        print("3. Give the task a name like 'AI Employee Scheduler'")
        print("4. Choose 'Daily' and set the start time")
        print("5. Select 'Start a program' as the action")
        print("6. Click 'Browse' and select your Python executable (e.g., python.exe)")
        print("7. In 'Arguments', enter: scripts/run_ai_employee.py")
        print("8. In 'Start in', enter the directory containing this script")
        print("9. Check 'Open the Properties dialog...' and click 'Next'")
        print("10. Check 'Run whether user is logged on or not' and click 'Finish'")
        print("\nAlternatively, to run in the background, use:")
        print("pythonw scripts/run_ai_employee.py")
    else:
        print("CRON JOB SETUP (Linux/Mac):")
        print("1. Open terminal")
        print("2. Type: crontab -e")
        print("3. Add the following line to run every 5 minutes:")
        print("   */5 * * * * cd /path/to/AI_Employee_Vault && python scripts/run_ai_employee.py >> scheduler.log 2>&1")
        print("\nTo run at startup, add to crontab:")
        print("   @reboot cd /path/to/AI_Employee_Vault && python scripts/run_ai_employee.py >> scheduler.log 2>&1")
        print("\nNote: Replace '/path/to/AI_Employee_Vault' with your actual path")
    
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-info":
        # Show setup instructions only
        show_setup_instructions()
    else:
        # Run the scheduler
        run_scheduler()