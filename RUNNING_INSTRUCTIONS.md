# Running Instructions for Autonomous Employee System

## Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation and Setup](#installation-and-setup)
4. [Running the System](#running-the-system)
5. [Odoo Integration Setup](#odoo-integration-setup)
6. [MCP Servers](#mcp-servers)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

The Autonomous Employee System is a complete business automation platform with:
- Social media management (Facebook, Instagram, Twitter)
- Financial accounting and reporting
- Task management across personal/business domains
- Error recovery and autonomous operation
- Executive reporting
- Odoo Community Edition integration

---

## Prerequisites

### Required Software
```bash
# Python 3.8 or higher
python --version

# Git (if cloning/fetching code)
git --version

# Node.js (for MCP servers) - if not already installed
node --version
npm --version
```

### Python Dependencies
```bash
pip install requests
pip install python-dotenv  # if using environment variables
```

---

## Installation and Setup

### 1. Clone/Download the System
```bash
cd E:\hackathon-0  # your project directory
```

### 2. Verify Directory Structure
```bash
# You should see the following structure:
hackathon-0/
├── Dashboard.md
├── Company_Handbook.md
├── SYSTEM_ARCHITECTURE.md
├── IMPLEMENTATION_GUIDE.md
├── RUNNING_INSTRUCTIONS.md
├── mcp.json
├── .env (optional)
├── Inbox/
├── Needs_Action/
├── Done/
├── Personal_Tasks/
├── Business_Tasks/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Logs/
├── Reports/
└── Skills/
    ├── CrossDomain_Manager/
    ├── SocialPoster_FBI/
    ├── SocialPoster_Twitter/
    ├── Ledger_Manager/
    ├── CEO_Briefing_Generator/
    ├── Error_Handler/
    ├── Audit_Logger/
    ├── Autonomous_Loop/
    └── Odoo_Integration/
```

### 3. Environment Setup
Create a `.env` file if needed (for API keys):
```bash
# .env file
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_app_password
GMAIL_TOKEN_PATH=token.json
FB_ACCESS_TOKEN=your_facebook_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
ODOO_URL=http://localhost:8069
ODOO_DB=your_database_name
ODOO_USER=your_username
ODOO_PASS=your_password
```

---

## Running the System

### Option 1: Quick Start (Recommended for Testing)
Open multiple command prompts/terminals and run each component:

#### Terminal 1: Start the main autonomous loop
```bash
cd E:\hackathon-0
python -c "
from Skills.Autonomous_Loop.autonomous_loop import get_autonomous_loop
loop = get_autonomous_loop()
loop.run_loop()
"
```

#### Terminal 2: Start MCP servers (if using external integration)
```bash
cd E:\hackathon-0
# Note: The system includes Python-based MCP servers now
python -c "
from Skills.Odoo_Integration.odoo_mcp_server import start_odoo_mcp_server
from Skills.SocialPoster_FBI.unified_social_manager import SocialPosterFBI
import threading
import time

# Start Odoo MCP server
odoo_thread = threading.Thread(target=start_odoo_mcp_server, args=(3002, 'localhost'), daemon=True)
odoo_thread.start()

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('Shutting down MCP servers...')
"
```

#### Terminal 3: Monitor dashboard
```bash
cd E:\hackathon-0
# Just monitor the dashboard file for updates
type Dashboard.md
# Or use a file monitoring tool to watch for changes
```

### Option 2: Using Script Files
Create batch files for Windows:

#### 1. Create `start_system.bat`
```batch
@echo off
echo Starting Autonomous Employee System...

REM Start the main autonomous loop in a new window
start "Autonomous Loop" cmd /k "cd /d E:\hackathon-0 && python -c \"from Skills.Autonomous_Loop.autonomous_loop import get_autonomous_loop; loop = get_autonomous_loop(); loop.run_loop()\""

REM Start MCP servers in another window
start "MCP Servers" cmd /k "cd /d E:\hackathon-0 && python -c \"from Skills.Odoo_Integration.odoo_mcp_server import start_odoo_mcp_server; start_odoo_mcp_server(3002)\""

echo System started in separate windows.
echo Check Dashboard.md for status updates.
pause
```

#### 2. Create `run_skills_test.py` for individual testing
```python
"""
Test script to verify all skills are working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_skills():
    print("Testing all skills...")

    try:
        from Skills.CrossDomain_Manager.crossdomain_manager import CrossDomainManager
        cdm = CrossDomainManager()
        print("✅ CrossDomain Manager - Working")
    except Exception as e:
        print(f"❌ CrossDomain Manager - Error: {e}")

    try:
        from Skills.SocialPoster_FBI.social_poster_fbi import SocialPosterFBI
        fb = SocialPosterFBI()
        print("✅ SocialPoster FBI - Working")
    except Exception as e:
        print(f"❌ SocialPoster FBI - Error: {e}")

    try:
        from Skills.SocialPoster_Twitter.social_poster_twitter import SocialPosterTwitter
        twitter = SocialPosterTwitter()
        print("✅ SocialPoster Twitter - Working")
    except Exception as e:
        print(f"❌ SocialPoster Twitter - Error: {e}")

    try:
        from Skills.Ledger_Manager.ledger_manager import LedgerManager
        ledger = LedgerManager()
        print("✅ Ledger Manager - Working")
    except Exception as e:
        print(f"❌ Ledger Manager - Error: {e}")

    try:
        from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator
        ceo = CEOBriefingGenerator()
        print("✅ CEO Briefing Generator - Working")
    except Exception as e:
        print(f"❌ CEO Briefing Generator - Error: {e}")

    try:
        from Skills.Error_Handler.error_handler import ErrorHandler
        error = ErrorHandler()
        print("✅ Error Handler - Working")
    except Exception as e:
        print(f"❌ Error Handler - Error: {e}")

    try:
        from Skills.Audit_Logger.audit_logger import AuditLogger
        audit = AuditLogger()
        print("✅ Audit Logger - Working")
    except Exception as e:
        print(f"❌ Audit Logger - Error: {e}")

    try:
        from Skills.Autonomous_Loop.autonomous_loop import AutonomousLoop
        loop = AutonomousLoop()
        print("✅ Autonomous Loop - Working")
    except Exception as e:
        print(f"❌ Autonomous Loop - Error: {e}")

    try:
        from Skills.Odoo_Integration.odoo_integration import OdooIntegration
        odoo = OdooIntegration()
        print("✅ Odoo Integration - Working (config status: {})".format(odoo.config['odoo']['enabled']))
    except Exception as e:
        print(f"❌ Odoo Integration - Error: {e}")

if __name__ == "__main__":
    test_all_skills()
```

Run the test:
```bash
python run_skills_test.py
```

---

## Odoo Integration Setup

### 1. Install Odoo Community Edition (Required for Gold Tier)

#### Option A: Quick Installation (Recommended)
```bash
# Install Odoo via pip
pip install odoo==19.0  # or latest 19.x version

# Or download from official source
curl -L https://nightly.odoo.com/19.0/nightly/src/odoo_19.0.latest.zip -o odoo.zip
unzip odoo.zip
pip install odoo/
```

#### Option B: Docker Installation
```bash
# Using Docker
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:13
docker run -p 8069:8069 --name odoo --link db:db -t odoo:19.0
```

### 2. Start Odoo Server
```bash
# Create a database first
odoo -d your_database_name --stop-after-init

# Start the server
odoo -d your_database_name

# Or with specific options
odoo -d your_database_name -r your_username -w your_password --addons-path=addons
```

### 3. Configure Odoo Integration
1. Open `Skills/Odoo_Integration/config.json`
2. Update the configuration:
```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
    "enabled": false  # Set to true ONLY after Odoo is running
  },
  "sync": {
    "enabled": true,
    "frequency_minutes": 30,
    "sync_direction": "bidirectional"
  },
  "mcp_server": {
    "enabled": true,
    "port": 3002,
    "host": "localhost"
  }
}
```

### 4. Enable Odoo Integration
Only enable after Odoo server is running and configured:
1. Set `"enabled": true` in the config file
2. Restart the system

---

## MCP Servers

The system includes multiple MCP (Machine Control Protocol) servers:

### 1. Email MCP Server (`mcp_servers/email_mcp.js`)
```bash
# Start manually if needed
cd mcp_servers
node email_mcp.js
```

### 2. Odoo MCP Server (Python-based)
Starts automatically when system starts if configured in `mcp.json`.

### 3. Testing MCP Connectivity
```bash
# Test Odoo MCP server
curl -X POST http://localhost:3002/mcp -H "Content-Type: application/json" -d '{
  "command": "test_connection",
  "args": {}
}'

# Test system status
curl -X POST http://localhost:3000/mcp -H "Content-Type: application/json" -d '{
  "command": "get_status",
  "args": {}
}'
```

---

## Monitoring and Maintenance

### 1. Dashboard Monitoring
Regularly check `Dashboard.md` for system status:
```bash
# View the dashboard
type Dashboard.md

# Or use a monitoring tool to watch for changes
```

### 2. Log Files
Check log files in `Logs/` directory:
- `audit.log` - Main system audit trail
- Console output from running components

### 3. Performance Monitoring
```bash
# Check system resource usage
tasklist | findstr python
tasklist | findstr node
```

### 4. Regular Maintenance Tasks
1. **Daily**: Check Dashboard.md for status
2. **Weekly**: Review Reports/CEO_Reports/ for business insights
3. **Monthly**: Check Logs/ for error patterns
4. **As needed**: Verify backup integrity

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "No module named Skills"
**Symptoms**: Import errors when starting the system
**Solution**:
```bash
# Make sure you're running from the correct directory
cd E:\hackathon-0
python -c "import sys; print(sys.path)"
```

#### Issue 2: MCP Server Not Starting
**Symptoms**: Connection refused when accessing MCP endpoints
**Solutions**:
1. Check if Node.js is installed: `node --version`
2. Verify `mcp.json` configuration
3. Check firewall settings

#### Issue 3: Odoo Connection Failed
**Symptoms**: Odoo integration errors
**Solutions**:
1. Verify Odoo server is running
2. Check credentials in `Skills/Odoo_Integration/config.json`
3. Ensure `"enabled": false` until Odoo is properly configured

#### Issue 4: Permission Errors
**Symptoms**: Unable to create files/write to directories
**Solution**: Run command prompt as administrator

#### Issue 5: Port Already in Use
**Symptoms**: Server startup errors
**Solution**:
```bash
# Check what's using the port
netstat -ano | findstr :3000
# Kill the process if needed
taskkill /PID <PID> /F
```

### Debug Commands
```bash
# Test individual skills
python -c "from Skills.Autonomous_Loop.autonomous_loop import get_autonomous_loop; print('AutoLoop working')"

# Check file permissions
dir Inbox Needs_Action Done

# Monitor system resources
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"
```

### Recovery Procedures
1. **System Hang**: Restart individual components
2. **Data Corruption**: Restore from `backups/` directory
3. **Configuration Error**: Revert config files to known good state
4. **Critical Failure**: Stop all processes and restart systematically

---

## Quick Start Checklist

- [ ] Verify all prerequisites installed
- [ ] Check directory structure is complete
- [ ] Install Python dependencies: `pip install requests`
- [ ] (Optional) Install Odoo Community Edition if using accounting features
- [ ] Run skill test: `python run_skills_test.py`
- [ ] Start autonomous loop
- [ ] Start MCP servers (if needed)
- [ ] Monitor Dashboard.md for activity
- [ ] Check Logs/ for any errors
- [ ] Verify Reports/ are being generated

---

## Support Command

To quickly verify your system is working:
```bash
cd E:\hackathon-0
python -c "
import sys
sys.path.append('.')
print('=== Autonomous Employee System Health Check ===')

try:
    from Skills.Autonomous_Loop.autonomous_loop import get_autonomous_loop
    print('✅ Core system - ACCESSIBLE')
except:
    print('❌ Core system - ERROR')

try:
    from Skills.Odoo_Integration.odoo_integration import OdooIntegration
    print('✅ Odoo integration - ACCESSIBLE (enable after installing Odoo)')
except:
    print('❌ Odoo integration - NEEDS SETUP')

print('=== Run Instructions ===')
print('1. For basic operation: Run the autonomous loop')
print('2. For full operation: Install Odoo + Run full system')
print('3. Monitor Dashboard.md for status updates')
"
```

The system is now ready for operation! Start with individual skill testing, then progress to full autonomous operation.