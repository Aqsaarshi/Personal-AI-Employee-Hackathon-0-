---
name: Reasoning Loop
description: Iterates reasoning until task complete, creates Plan.md
version: 1.0
---

## Reasoning Loop Agent Skill

### Purpose
Implements a reasoning loop that iterates until a task is complete, creating and updating Plan.md files to track progress.

### Instructions (Ralph Wiggum style loop simulation):
1. For task in /Needs_Action: Read file.
2. Loop: Think step-by-step → Create/update Plan_[task].md in /Plans with checkboxes.
3. If not done: Re-prompt self with previous output.
4. When complete: Move to /Done, update Dashboard.
5. Max 5 iterations.

### Process
- Reads tasks from the Needs_Action folder
- Creates detailed plans with checkboxes for tracking
- Iterates reasoning until all steps are completed
- Moves completed tasks to the Done folder
- Updates the dashboard with progress