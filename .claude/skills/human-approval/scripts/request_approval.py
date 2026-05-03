#!/usr/bin/env python3
"""
Human Approval Skill
Human-in-the-loop for sensitive actions
"""

import os
import sys
import json
import time
from datetime import datetime

def request_approval(action_type, details, identifier):
    """
    Create an approval request file and wait for human decision
    """
    try:
        # Base path for the vault
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        vault_path = os.path.abspath(base_path)
        needs_approval_path = os.path.join(vault_path, "Needs_Approval")
        
        # Create Needs_Approval directory if it doesn't exist
        os.makedirs(needs_approval_path, exist_ok=True)
        
        # Create approval file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"approval_{identifier}_{timestamp}.md"
        approval_file_path = os.path.join(needs_approval_path, filename)
        
        # Create approval request content
        approval_content = f"""# Approval Request

**Action Type:** {action_type}

**Request ID:** {identifier}

**Timestamp:** {datetime.now().isoformat()}

**Details:**
```
{json.dumps(details, indent=2)}
```

**Status:** PENDING

---

**Action Required:** Please review this request and update the status below:

**Status:** [APPROVE/REJECT] <!-- Write your decision here -->

**Reviewer Comments:** [Add your comments here]

**Reviewed By:** [Your name]

**Review Timestamp:** [YYYY-MM-DD HH:MM:SS]
"""
        
        # Write the approval request file
        with open(approval_file_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)
        
        # Wait for approval decision (with timeout)
        timeout = 3600  # 1 hour timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Read the file to check for approval status
            with open(approval_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if approval decision has been made
            if '[APPROVE]' in content:
                # Move to Done folder
                done_path = os.path.join(vault_path, "Done")
                os.makedirs(done_path, exist_ok=True)
                done_file_path = os.path.join(done_path, f"approved_{filename}")
                os.rename(approval_file_path, done_file_path)
                
                return {
                    "success": True,
                    "status": "APPROVED",
                    "message": f"Action approved: {action_type}",
                    "request_id": identifier
                }
            elif '[REJECT]' in content or '[REJECTED]' in content:
                # Move to Done folder
                done_path = os.path.join(vault_path, "Done")
                os.makedirs(done_path, exist_ok=True)
                done_file_path = os.path.join(done_path, f"rejected_{filename}")
                os.rename(approval_file_path, done_file_path)
                
                return {
                    "success": True,
                    "status": "REJECTED",
                    "message": f"Action rejected: {action_type}",
                    "request_id": identifier
                }
            
            # Wait before checking again
            time.sleep(10)  # Check every 10 seconds
        
        # If we reach here, it means timeout occurred
        return {
            "success": False,
            "status": "TIMEOUT",
            "error": f"Approval request timed out after {timeout} seconds",
            "request_id": identifier
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "ERROR"
        }

def main():
    """
    Main function to handle command line execution
    """
    if len(sys.argv) < 4:
        print(json.dumps({
            "success": False,
            "error": "Usage: python request_approval.py <action_type> <details_json> <identifier>"
        }))
        return
    
    action_type = sys.argv[1]
    try:
        details = json.loads(sys.argv[2])
    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "Invalid JSON for details parameter"
        }))
        return
    identifier = sys.argv[3]
    
    result = request_approval(action_type, details, identifier)
    print(json.dumps(result))

if __name__ == "__main__":
    main()