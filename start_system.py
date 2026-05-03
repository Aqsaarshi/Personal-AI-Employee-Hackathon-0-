"""
Main startup script for Autonomous Employee System
This script starts all necessary components of the system
"""
import sys
import os
import threading
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_autonomous_loop():
    """Start the main autonomous loop."""
    print(f"[{datetime.now()}] Starting Autonomous Loop...")
    try:
        from Skills.Autonomous_Loop.autonomous_loop import get_autonomous_loop

        # Create dashboard entry
        with open("Dashboard.md", "a") as f:
            f.write(f"\n\n## System Status\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- Autonomous Loop initialized")

        loop = get_autonomous_loop()
        print(f"[{datetime.now()}] Autonomous Loop initialized successfully!")

        # Start the loop (this will run continuously)
        loop.run_loop()

    except Exception as e:
        print(f"[{datetime.now()}] Error starting Autonomous Loop: {e}")
        import traceback
        traceback.print_exc()

def start_mcp_servers():
    """Start MCP servers."""
    print(f"[{datetime.now()}] Starting MCP Servers...")
    try:
        from Skills.Odoo_Integration.odoo_mcp_server import start_odoo_mcp_server

        # Start Odoo MCP server in a thread
        odoo_thread = threading.Thread(
            target=start_odoo_mcp_server,
            args=(3002, 'localhost'),
            daemon=True
        )
        odoo_thread.start()
        print(f"[{datetime.now()}] Odoo MCP Server started on port 3002")

        return [odoo_thread]

    except Exception as e:
        print(f"[{datetime.now()}] Error starting MCP Servers: {e}")
        import traceback
        traceback.print_exc()
        return []

def run_system_monitor():
    """Run system monitoring."""
    print(f"[{datetime.now()}] Starting System Monitor...")

    while True:
        try:
            # Check if dashboard exists and update status
            if os.path.exists("Dashboard.md"):
                with open("Dashboard.md", "r+") as f:
                    content = f.read()
                    f.seek(0)
                    f.write(content)
                    f.write(f"\n- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] System running - Monitor active")

            time.sleep(60)  # Update every minute

        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] System Monitor stopped by user")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Monitor error: {e}")
            time.sleep(10)

def main():
    """Main function to start the complete system."""
    print("="*60)
    print("Autonomous Employee System - Gold Tier")
    print("Starting complete system...")
    print("="*60)

    # Update dashboard
    dashboard_content = f"""# AI Employee Dashboard

## System Status
Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System Status: RUNNING

## Active Components
- Autonomous Loop: Starting...
- MCP Servers: Starting...
- Monitor: Active

## Recent Activity
- System startup initiated
"""

    with open("Dashboard.md", "w") as f:
        f.write(dashboard_content)

    print(f"[{datetime.now()}] Dashboard updated")

    # Start MCP servers in background
    mcp_threads = start_mcp_servers()

    # Start system monitor in background
    monitor_thread = threading.Thread(target=run_system_monitor, daemon=True)
    monitor_thread.start()

    print(f"[{datetime.now()}] System components started")
    print("System is now running!")
    print("\nPress Ctrl+C to stop the system")
    print("Monitor Dashboard.md for system status")

    try:
        # Start the main autonomous loop (this will block)
        start_autonomous_loop()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Shutdown signal received")
        print("System stopping...")

        # Update dashboard
        with open("Dashboard.md", "a") as f:
            f.write(f"\n\n## System Shutdown\nStopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print("System stopped gracefully")
    except Exception as e:
        print(f"[{datetime.now()}] System error: {e}")
        import traceback
        traceback.print_exc()

        # Update dashboard with error
        with open("Dashboard.md", "a") as f:
            f.write(f"\n\n## System Error\nError Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nError: {str(e)[:200]}\n")

if __name__ == "__main__":
    main()