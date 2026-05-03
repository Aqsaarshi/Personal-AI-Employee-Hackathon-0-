
# Run with: python vault_watcher.py
# First install: pip install watchdog

import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MDFileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        
    def on_created(self, event):
        # Only process .md files
        if not event.is_directory and event.src_path.endswith('.md'):
            # Check if the file is in Needs_Action or Inbox folder
            path_parts = event.src_path.split(os.sep)
            if len(path_parts) >= 2 and path_parts[-2] in ['Needs_Action', 'Inbox']:
                # Print to console
                print(f"New task detected: {event.src_path}")
                
                # Append to log file
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename = os.path.basename(event.src_path)
                
                # Ensure Logs directory exists
                logs_dir = os.path.join(os.getcwd(), 'Logs')
                os.makedirs(logs_dir, exist_ok=True)
                
                log_file_path = os.path.join(logs_dir, 'watcher_log.md')
                
                try:
                    with open(log_file_path, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"- [{timestamp}] Detected new file: {filename}\n")
                except Exception as e:
                    print(f"Error writing to log file: {e}")


def main():
    # Get the current directory
    current_dir = os.getcwd()
    
    # Create handler and observer
    event_handler = MDFileHandler()
    observer = Observer()
    
    # Schedule watching for the current directory recursively
    observer.schedule(event_handler, current_dir, recursive=True)
    
    print(f"Starting file watcher for directory: {current_dir}")
    print("Watching for new .md files in Needs_Action or Inbox folders...")
    
    # Start the observer
    observer.start()
    
    try:
        # Run indefinitely with 10-second sleep between checks
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nStopping file watcher...")
        observer.stop()
    
    # Wait for observer thread to finish
    observer.join()
    print("File watcher stopped.")


if __name__ == "__main__":
    main()