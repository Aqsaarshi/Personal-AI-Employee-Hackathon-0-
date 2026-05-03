#!/usr/bin/env python3
"""
Vault File Manager Skill
Manage task workflow between Inbox, Needs_Action, and Done
"""

import os
import sys
import json
import shutil

def get_full_path(directory):
    """
    Get the full path for a given directory alias
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    vault_path = os.path.abspath(base_path)
    
    if directory.lower() == "inbox":
        return os.path.join(vault_path, "Inbox")
    elif directory.lower() == "needs_action":
        return os.path.join(vault_path, "Needs_Action")
    elif directory.lower() == "done":
        return os.path.join(vault_path, "Done")
    else:
        raise ValueError(f"Invalid directory: {directory}. Use 'inbox', 'needs_action', or 'done'.")

def move_task(source, destination, filename):
    """
    Move a file from source directory to destination directory
    """
    try:
        source_path = get_full_path(source)
        dest_path = get_full_path(destination)
        
        # Validate directories exist
        if not os.path.isdir(source_path):
            return {
                "success": False,
                "error": f"Source directory does not exist: {source_path}"
            }
        
        if not os.path.isdir(dest_path):
            return {
                "success": False,
                "error": f"Destination directory does not exist: {dest_path}"
            }
        
        # Construct full file paths
        source_file = os.path.join(source_path, filename)
        dest_file = os.path.join(dest_path, filename)
        
        # Check if source file exists
        if not os.path.isfile(source_file):
            return {
                "success": False,
                "error": f"Source file does not exist: {source_file}"
            }
        
        # Check if destination file already exists
        if os.path.isfile(dest_file):
            return {
                "success": False,
                "error": f"Destination file already exists: {dest_file}"
            }
        
        # Move the file
        shutil.move(source_file, dest_file)
        
        return {
            "success": True,
            "message": f"File moved from {source}/{filename} to {destination}/{filename}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """
    Main function to handle command line execution
    """
    if len(sys.argv) != 4:
        print(json.dumps({
            "success": False,
            "error": "Usage: python move_task.py <source> <destination> <filename>"
        }))
        return
    
    source = sys.argv[1]
    destination = sys.argv[2]
    filename = sys.argv[3]
    
    result = move_task(source, destination, filename)
    print(json.dumps(result))

if __name__ == "__main__":
    main()