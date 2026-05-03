import schedule
import time
import os
import subprocess
import threading
from datetime import datetime
import sys

def run_reasoning_loop():
    """
    Run reasoning loop on files in /Needs_Action directory
    """
    print(f"[{datetime.now()}] Running reasoning loop on /Needs_Action...")
    
    needs_action_dir = "./Needs_Action"
    
    if not os.path.exists(needs_action_dir):
        print(f"Directory {needs_action_dir} does not exist.")
        return
    
    # Get all files in Needs_Action directory
    files = os.listdir(needs_action_dir)
    
    if not files:
        print("No files found in /Needs_Action directory.")
        return
    
    print(f"Found {len(files)} files in /Needs_Action: {files}")
    
    # For each file, run the reasoning loop by calling the Node.js implementation
    for file in files:
        file_path = os.path.join(needs_action_dir, file)
        if os.path.isfile(file_path):
            print(f"Processing file: {file_path}")
            
            # Read the file content to determine the task
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a task based on the file content
            task = {
                "name": f"Task from {file}",
                "description": content[:100] + "..." if len(content) > 100 else content,
                "steps": [
                    {
                        "action": "process_file",
                        "description": f"Process file {file}",
                        "file_path": file_path
                    }
                ]
            }
            
            try:
                # Call the Node.js reasoning loop via subprocess
                import json
                task_json = json.dumps(task)
                
                # Write task to a temporary file
                temp_task_file = f"./temp_task_{int(datetime.now().timestamp())}.json"
                with open(temp_task_file, 'w', encoding='utf-8') as tf:
                    json.dump(task, tf)
                
                # Execute the reasoning loop using Node.js
                result = subprocess.run([
                    "node", 
                    "-e",
                    f"""
                    const ReasoningLoop = require('./Skills/Reasoning_Loop/reasoning_loop.js');
                    const fs = require('fs');
                    const taskData = JSON.parse(fs.readFileSync('{temp_task_file}', 'utf8'));
                    const rl = new ReasoningLoop();
                    rl.execute(taskData, 'scheduled_' + Date.now()).catch(console.error);
                    """
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"  - Successfully processed {file} with reasoning loop")
                else:
                    print(f"  - Error processing {file} with reasoning loop: {result.stderr}")
                
                # Clean up temp file
                if os.path.exists(temp_task_file):
                    os.remove(temp_task_file)
                
                # Move file to Done after processing
                done_dir = "./Done"
                if not os.path.exists(done_dir):
                    os.makedirs(done_dir)
                
                # Move the file to Done directory
                import shutil
                shutil.move(file_path, os.path.join(done_dir, file))
                print(f"  - Moved {file} to Done directory")
                
            except subprocess.TimeoutExpired:
                print(f"  - Timeout processing {file} with reasoning loop")
                
                # Clean up temp file if it exists
                if os.path.exists(temp_task_file):
                    os.remove(temp_task_file)
            except Exception as e:
                print(f"  - Error processing {file} with reasoning loop: {str(e)}")
                
                # Clean up temp file if it exists
                if os.path.exists(temp_task_file):
                    os.remove(temp_task_file)

def check_watchers_status():
    """
    Check status of watchers
    """
    print(f"[{datetime.now()}] Checking watchers status...")
    
    # List all watcher files in the root directory
    watcher_files = [f for f in os.listdir('.') if f.endswith('_watcher.py')]
    
    if not watcher_files:
        print("No watcher files found in root directory.")
        return
    
    for watcher_file in watcher_files:
        print(f"Checking {watcher_file}...")
        
        # Try to run the watcher with a dry-run or status flag if available
        try:
            # Run the watcher with a timeout to check its status
            result = subprocess.run([sys.executable, watcher_file, "--status"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"  - {watcher_file} is running normally: {result.stdout}")
            else:
                print(f"  - {watcher_file} may have issues: {result.stderr}")
                
                # Attempt to restart the watcher if it's not running properly
                print(f"  - Attempting to restart {watcher_file}...")
                restart_result = subprocess.Popen([sys.executable, watcher_file])
                print(f"  - {watcher_file} restarted with PID: {restart_result.pid}")
                
        except subprocess.TimeoutExpired:
            print(f"  - {watcher_file} is still running (timeout on status check)")
        except FileNotFoundError:
            print(f"  - {watcher_file} not found or not executable")
        except Exception as e:
            print(f"  - Error checking {watcher_file}: {str(e)}")
    
    # Also check if any watchers are running as background processes
    try:
        # On Windows, we can check running Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and watcher_file in result.stdout:
            print("  - Watcher processes are running in background")
        else:
            print("  - No watcher processes found in task list")
    except Exception as e:
        print(f"  - Could not check background processes: {str(e)}")

def run_claude_prompt(prompt):
    """
    Run a Claude prompt
    """
    print(f"[{datetime.now()}] Running Claude prompt: {prompt}")
    
    # For now, we'll simulate calling Claude by creating a task file
    # In a real implementation, this would call the Claude API
    try:
        # Create a task file in Inbox to be processed by Claude
        inbox_dir = "./Inbox"
        if not os.path.exists(inbox_dir):
            os.makedirs(inbox_dir)
        
        # Create a timestamped task file
        task_filename = f"claude_task_{int(datetime.now().timestamp())}.md"
        task_path = os.path.join(inbox_dir, task_filename)
        
        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(f"# Claude Task\n\n")
            f.write(f"**Prompt:** {prompt}\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Status:** Pending\n\n")
            f.write("---\n")
            f.write("Results will be placed in the appropriate output folder.\n")
        
        print(f"  - Created Claude task file: {task_path}")
        
    except Exception as e:
        print(f"  - Error creating Claude task: {str(e)}")

def run_scheduler():
    """
    Main scheduler function
    """
    print("Starting scheduler...")
    print(f"Scheduler started at {datetime.now()}")
    
    # Schedule reasoning loop to run daily at 8 AM
    schedule.every().day.at("08:00").do(run_reasoning_loop)
    
    # Schedule watchers status check to run every hour
    schedule.every().hour.do(check_watchers_status)
    
    # Example of scheduling Claude prompts (optional)
    # schedule.every().monday.at("09:00").do(run_claude_prompt, "Weekly status report")
    
    print("Scheduled jobs:")
    print("- Daily reasoning loop at 08:00")
    print("- Hourly watchers status check")
    
    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def show_cron_setup_instructions():
    """
    Display cron setup instructions for Linux/Mac
    """
    print("\n" + "="*60)
    print("CRON SETUP INSTRUCTIONS (Linux/Mac):")
    print("="*60)
    print("1. Open terminal")
    print("2. Type: crontab -e")
    print("3. Add the following line to run scheduler daily at 8 AM:")
    print("   0 8 * * * cd /path/to/vault && python scheduler.py")
    print("")
    print("Alternative approach using a full path:")
    print("   0 8 * * * /full/path/to/python /full/path/to/vault/scheduler.py")
    print("")
    print("To run the orchestrator script instead:")
    print("   0 8 * * * /full/path/to/python /full/path/to/orchestrator.py")
    print("="*60)

def show_windows_task_setup_instructions():
    """
    Display Windows Task Scheduler setup steps
    """
    print("\n" + "="*60)
    print("WINDOWS TASK SCHEDULER SETUP STEPS:")
    print("="*60)
    print("1. Press Win + R, type 'taskschd.msc', and press Enter")
    print("2. Click 'Create Basic Task...' in the right panel")
    print("3. Give the task a name like 'Vault Scheduler'")
    print("4. Choose 'Daily' and set the start time to 8:00 AM")
    print("5. Select 'Start a program' as the action")
    print("6. Click 'Browse' and select your Python executable")
    print("7. In 'Arguments', enter: scheduler.py")
    print("8. In 'Start in', enter the directory path containing scheduler.py")
    print("9. Check 'Open the Properties dialog...' and click 'Next'")
    print("10. Check 'Run whether user is logged on or not' and click 'Finish'")
    print("="*60)

def run_once_for_testing():
    """
    Run scheduled tasks once for testing purposes
    """
    print("Running scheduled tasks once for testing...")
    
    # Run reasoning loop once
    print("\n--- Running reasoning loop ---")
    run_reasoning_loop()
    
    # Run watchers status check once
    print("\n--- Checking watchers status ---")
    check_watchers_status()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Run once for testing
            run_once_for_testing()
        elif sys.argv[1] == "--cron-info":
            # Show cron setup instructions
            show_cron_setup_instructions()
        elif sys.argv[1] == "--windows-info":
            # Show Windows Task Scheduler setup steps
            show_windows_task_setup_instructions()
        elif sys.argv[1] == "--setup-info":
            # Show both cron and Windows setup instructions
            show_cron_setup_instructions()
            show_windows_task_setup_instructions()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage:")
            print("  python scheduler.py              # Run the continuous scheduler")
            print("  python scheduler.py --test       # Run scheduled tasks once for testing")
            print("  python scheduler.py --cron-info  # Show cron setup instructions")
            print("  python scheduler.py --windows-info  # Show Windows Task Scheduler setup steps")
            print("  python scheduler.py --setup-info # Show both setup instructions")
    else:
        # Run the continuous scheduler
        run_scheduler()