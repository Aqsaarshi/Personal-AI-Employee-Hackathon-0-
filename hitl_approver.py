#!/usr/bin/env python3
"""
HITL (Human-in-the-Loop) Approver for LinkedIn Posts
Creates approval files that require human confirmation before posting
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass  # Skip if reconfigure not available


class HITLApprover:
    """Human-in-the-Loop Approver for sensitive actions"""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            # Use the directory where this script is located
            base_dir = Path(__file__).parent
        
        self.pending_dir = base_dir / "Pending_Approval"
        self.approved_dir = base_dir / "Approved"
        self.rejected_dir = base_dir / "Rejected"
        self.done_dir = base_dir / "Done"
        
        # Create directories if they don't exist
        for dir_path in [self.pending_dir, self.approved_dir, self.rejected_dir, self.done_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def create_approval(self, action_type: str, details: dict) -> Path:
        """
        Create an approval file for a sensitive action
        
        Args:
            action_type: Type of action (e.g., 'linkedin_post')
            details: Dictionary with action details
        
        Returns:
            Path to the created approval file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{action_type}_approval_{timestamp}.md"
        file_path = self.pending_dir / file_name
        
        # Extract relevant details
        post_content = details.get("content", details.get("post_content", ""))
        post_preview = post_content[:100] + "..." if len(post_content) > 100 else post_content
        
        yaml_frontmatter = f"""---
type: {action_type}
details:
  content: |
    {post_content}
  timestamp: {datetime.now().isoformat()}
  status: pending
---

# LinkedIn Post Approval Request

## Post Details
- **Type**: {action_type}
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Character Count**: {len(post_content)}

## Post Preview

{post_preview}

## Full Content

{post_content}

## Instructions

Review this LinkedIn post and move this file to:
- **Approved/** folder to publish the post
- **Rejected/** folder to discard the post

The system will automatically process based on the folder location.
"""
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(yaml_frontmatter)
        
        print(f"✅ Created approval file: {file_path}")
        return file_path
    
    def check_approval_status(self, approval_file_path: Path) -> dict:
        """
        Check if an action has been approved or rejected
        
        Args:
            approval_file_path: Path to the approval file
        
        Returns:
            dict with 'approved' (True/False/None), 'path', and 'reason'
        """
        file_name = approval_file_path.name
        
        # Check if file exists in Approved directory
        approved_path = self.approved_dir / file_name
        if approved_path.exists():
            return {"approved": True, "path": approved_path, "reason": "Manually approved by human"}
        
        # Check if file exists in Rejected directory
        rejected_path = self.rejected_dir / file_name
        if rejected_path.exists():
            return {"approved": False, "path": rejected_path, "reason": "Manually rejected by human"}
        
        # Still pending
        return {"approved": None, "path": approval_file_path, "reason": "Still pending approval"}
    
    def move_to_done(self, approval_file_path: Path, prefix: str = "") -> Path:
        """
        Move a processed file to the Done directory
        
        Args:
            approval_file_path: Path to the approval file
            prefix: Optional prefix for the file name (e.g., 'rejected_')
        
        Returns:
            Path to the new file location
        """
        file_name = approval_file_path.name
        done_path = self.done_dir / f"{prefix}{file_name}"
        
        approval_file_path.rename(done_path)
        print(f"📁 Moved file to Done: {done_path}")
        return done_path
    
    def extract_content_from_approval(self, approval_file_path: Path) -> str:
        """
        Extract the post content from an approval file
        
        Args:
            approval_file_path: Path to the approval file
        
        Returns:
            The post content string
        """
        with open(approval_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract content from YAML frontmatter
        import re
        yaml_match = re.search(r'---\n([\s\S]*?)\n---', content)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            # Extract content field
            content_match = re.search(r'content:\s*\|\s*\n(.+?)(?=\n\w+:|\Z)', yaml_content, re.DOTALL)
            if content_match:
                return content_match.group(1).strip()
        
        # Fallback: extract from markdown section
        full_content_match = re.search(r'## Full Content\n\n(.+)', content, re.DOTALL)
        if full_content_match:
            return full_content_match.group(1).strip()
        
        return ""


def wait_for_approval(approval_file_path: Path, timeout_hours: int = 24) -> bool:
    """
    Wait for human approval (file moved to Approved or Rejected)
    
    Args:
        approval_file_path: Path to the approval file
        timeout_hours: Maximum hours to wait for approval
    
    Returns:
        True if approved, False if rejected or timeout
    """
    approver = HITLApprover()
    start_time = datetime.now()
    timeout_delta = timedelta(hours=timeout_hours)
    
    print(f"⏳ Waiting for approval... (timeout: {timeout_hours} hours)")
    print(f"📁 Approval file: {approval_file_path}")
    print(f"👉 Move file to Approved/ to publish, Rejected/ to discard")
    
    while True:
        status = approver.check_approval_status(approval_file_path)
        
        if status["approved"] is True:
            print("✅ Post APPROVED by human!")
            return True
        elif status["approved"] is False:
            print("❌ Post REJECTED by human!")
            return False
        
        # Check timeout
        elapsed = datetime.now() - start_time
        if elapsed > timeout_delta:
            print(f"⏰ Approval timeout after {timeout_hours} hours")
            return False
        
        # Wait before checking again
        time.sleep(30)  # Check every 30 seconds
