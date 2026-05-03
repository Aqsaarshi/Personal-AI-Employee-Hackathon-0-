# Odoo Integration Skill

## Overview
The Odoo Integration skill provides integration with Odoo Community Edition for accounting system functionality using JSON-RPC APIs. It synchronizes financial data between the local system and Odoo, handles accounting operations, and provides MCP server integration for external access.

## Features
- **Odoo JSON-RPC Integration**: Connects to Odoo Community Edition using official API
- **Accounting Operations**: Create journal entries, payments, and manage financial records
- **Data Synchronization**: Bidirectional sync between local and Odoo systems
- **MCP Server Integration**: External access via MCP protocol
- **Financial Reporting**: Retrieve and generate financial reports
- **Error Handling**: Robust connection and error management
- **Comprehensive Logging**: All operations logged via Audit Logger

## Configuration
The skill uses `config.json` for Odoo connection settings:

```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
    "enabled": false
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
  },
  "models": {
    "account_move": "account.move",
    "account_journal": "account.journal",
    "res_partner": "res.partner",
    "product_product": "product.product"
  }
}
```

**Important**: Set "enabled" to true only after Odoo is properly installed and configured.

## Installation Requirements

### Odoo Community Setup
To use this integration, you need to have Odoo Community Edition installed:

1. **Install Odoo** (version 19+ as required):
   ```bash
   # Option 1: Using pip
   pip install odoo==19.0  # (or appropriate version)

   # Option 2: From source
   git clone https://github.com/odoo/odoo.git -b 19.0
   cd odoo
   pip install -e .
   ```

2. **Start Odoo Server**:
   ```bash
   # Create a database
   odoo -d your_database_name --stop-after-init

   # Start the server
   odoo -d your_database_name
   ```

3. **Configure Database**: Access Odoo web interface at http://localhost:8069 and complete initial setup

## Core Functions

### 1. Connection Management
- Automatic connection and authentication
- Session management and reconnection
- Connection testing capability

### 2. Accounting Operations
- **Journal Entries**: Create and manage account moves
- **Payments**: Process account payments
- **Records Management**: CRUD operations on various models
- **Financial Reports**: Generate trial balances and reports

### 3. Data Synchronization
- Bidirectional sync between local and Odoo
- Conflict resolution for concurrent updates
- Incremental sync to minimize data transfer
- Local-to-Odoo and Odoo-to-local sync options

## Usage Examples

### Basic Initialization
```python
from Skills.Odoo_Integration.odoo_integration import OdooIntegration

# Initialize with default config
odoo = OdooIntegration()

# Test the connection
if odoo.test_connection():
    print("Connected to Odoo successfully!")
else:
    print("Connection failed")
```

### Creating Financial Records
```python
# Create a journal entry
move_data = {
    "ref": "INV-001",
    "date": "2026-02-21",
    "line_ids": [
        [0, 0, {
            "name": "Service Revenue",
            "account_id": 1,  # Account Receivable
            "debit": 0.0,
            "credit": 1000.0
        }],
        [0, 0, {
            "name": "Income",
            "account_id": 2,  # Income Account
            "debit": 1000.0,
            "credit": 0.0
        }]
    ]
}

move_id = odoo.create_account_move(move_data)
print(f"Created journal entry: {move_id}")
```

### Searching and Reading Records
```python
# Search for recent journal entries
moves = odoo.search_read(
    model="account.move",
    domain=[["date", ">=", "2026-02-01"]],
    fields=["id", "name", "ref", "date", "amount_total"],
    limit=10
)

print(f"Found {len(moves)} journal entries")
```

### Financial Reporting
```python
# Get financial reports
reports = odoo.get_financial_reports(
    date_from="2026-02-01",
    date_to="2026-02-21"
)

print(f"Generated reports from {reports['date_from']} to {reports['date_to']}")
```

### Data Synchronization
```python
# Sync local data to Odoo
local_data = {
    "transactions": [
        {
            "id": "local_txn_1",
            "date": "2026-02-21",
            "amount": 1000.0,
            "description": "Service payment"
        }
    ],
    "date_from": "2026-02-01",
    "date_to": "2026-02-21"
}

sync_result = odoo.sync_with_local_ledger(
    local_data,
    sync_direction="local_to_odoo"
)

print(f"Sync completed: {sync_result['processed']} processed")
```

## MCP Server Integration

The skill includes an MCP server for external access:

### Starting the MCP Server
```python
from Skills.Odoo_Integration.odoo_mcp_server import start_odoo_mcp_server

# Start the server on default port 3002
start_odoo_mcp_server()
```

### MCP Commands

#### Create Account Move
```json
{
  "command": "create_account_move",
  "args": {
    "ref": "INV-001",
    "date": "2026-02-21",
    "journal_id": 1,
    "line_ids": [
      {
        "name": "Service Revenue",
        "account_id": 1,
        "debit": 0.0,
        "credit": 1000.0
      }
    ]
  }
}
```

#### Search and Read
```json
{
  "command": "search_read",
  "args": {
    "model": "account.move",
    "domain": [["date", ">=", "2026-02-01"]],
    "fields": ["id", "name", "date", "amount_total"],
    "limit": 10
  }
}
```

#### Get Financial Reports
```json
{
  "command": "get_financial_reports",
  "args": {
    "date_from": "2026-02-01",
    "date_to": "2026-02-21"
  }
}
```

## Error Handling

The skill includes comprehensive error handling:

- **Connection Errors**: Automatic reconnection attempts
- **RPC Errors**: Proper error propagation with details
- **Authentication Errors**: Clear error messages
- **Data Validation**: Input validation before API calls

## Security Considerations

- **Credentials**: Store Odoo credentials securely
- **Network**: MCP server should be properly firewalled
- **Authentication**: MCP endpoints may need additional auth
- **Data Privacy**: Financial data should be protected

## Troubleshooting

### Common Issues
1. **Connection Refused**: Ensure Odoo server is running
2. **Authentication Failed**: Check username, password, and database name
3. **Model Access Denied**: Ensure user has proper permissions
4. **JSON-RPC Not Available**: Check Odoo configuration

### Testing Connection
```python
from Skills.Odoo_Integration.odoo_integration import OdooIntegration

odoo = OdooIntegration()
try:
    if odoo.test_connection():
        print("Connection successful!")
    else:
        print("Connection failed!")
except Exception as e:
    print(f"Error: {e}")
```

## MCP Server Endpoints

### POST Endpoints
- `/mcp` - All MCP commands via POST body

### GET Endpoints
- `/odoo/test_connection` - Test Odoo connectivity
- `/odoo/get_financial_reports` - Get financial reports
- `/odoo/get_company_info` - Get company information

## Integration with Other Skills

The Odoo Integration skill works with other system components:
- **Ledger Manager**: Synchronize financial transactions
- **CEO Briefing Generator**: Include Odoo financial reports
- **Audit Logger**: Log all integration activities
- **Error Handler**: Handle connection and API errors

The Odoo Integration skill provides a complete bridge between your local autonomous system and Odoo Community Edition, enabling full accounting functionality as required for Gold Tier certification.