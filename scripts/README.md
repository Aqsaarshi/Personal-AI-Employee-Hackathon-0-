# AI Employee Scheduler

This scheduler automatically processes tasks from your Inbox using the task-planner skill every 5 minutes.

## How It Works

1. The scheduler runs continuously, checking for new tasks in the `Inbox` directory
2. Every 5 minutes, it processes any new tasks by running the task-planner skill
3. The task-planner creates structured plans in the `Needs_Action` directory
4. The system handles the entire workflow automatically

## Setup Instructions

### Windows Task Scheduler

To run the scheduler automatically on Windows:

1. Press `Win + R`, type `taskschd.msc`, and press Enter
2. Click `Create Basic Task...` in the right panel
3. Give the task a name like `AI Employee Scheduler`
4. Choose `Daily` and set the start time
5. Select `Start a program` as the action
6. Click `Browse` and select your Python executable (e.g., `python.exe`)
7. In `Arguments`, enter: `scripts/run_ai_employee.py`
8. In `Start in`, enter the directory containing this script
9. Check `Open the Properties dialog...` and click `Next`
10. Check `Run whether user is logged on or not` and click `Finish`

### Linux/mac Cron Job

To run the scheduler automatically on Linux/mac:

1. Open terminal
2. Type: `crontab -e`
3. Add the following line to run every 5 minutes:
   ```
   */5 * * * * cd /path/to/AI_Employee_Vault && python scripts/run_ai_employee.py >> scheduler.log 2>&1
   ```
4. To run at startup, add to crontab:
   ```
   @reboot cd /path/to/AI_Employee_Vault && python scripts/run_ai_employee.py >> scheduler.log 2>&1
   ```

Note: Replace `/path/to/AI_Employee_Vault` with your actual path.

## Manual Execution

To run the scheduler manually:
```bash
python scripts/run_ai_employee.py
```

To view setup instructions:
```bash
python scripts/run_ai_employee.py --setup-info
```

## Requirements

- Python 3.10+
- Required packages: `schedule`
- The reasoning_workflow.py script (already included in the vault)

## Troubleshooting

If the scheduler fails to run:
1. Ensure Python is in your PATH
2. Install required packages: `pip install schedule`
3. Verify the Inbox directory exists
4. Check that reasoning_workflow.py exists in the vault root