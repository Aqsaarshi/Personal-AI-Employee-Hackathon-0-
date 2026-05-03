# Ledger Manager Skill

## Overview
The Ledger Manager skill maintains a lightweight local accounting system using JSON/SQLite to record income, expenses, profit/loss. It provides query access through an MCP server and generates weekly financial summaries for CEO reports.

## Features
- **Lightweight Accounting**: Uses JSON or SQLite for financial data storage
- **Income & Expense Tracking**: Records transactions with categories and descriptions
- **Financial Summaries**: Generates income, expense, and profit/loss reports
- **MCP Server Integration**: Provides external query access to ledger data
- **Weekly Financial Reports**: Generates CEO reports with trend analysis
- **Data Backup/Restore**: Built-in backup and restore functionality
- **Trend Analysis**: Analyzes financial patterns and generates recommendations

## Configuration
The skill uses `config.json` for database settings and categories:

```json
{
  "database": {
    "type": "json",  // "json" or "sqlite"
    "path": "ledger_data.json",
    "backup_enabled": true,
    "backup_path": "backups/ledger_backup.json"
  },
  "categories": {
    "income": ["sales", "consulting", "investment", "other_income"],
    "expenses": ["office_rent", "utilities", "salaries", "marketing", "travel", "software", "hardware", "other_expenses"]
  },
  "mcp_server": {
    "enabled": true,
    "port": 3001,
    "host": "localhost"
  },
  "reporting": {
    "weekly_summary_day": "fri",
    "currency": "USD"
  }
}
```

## Schema & CRUD Operations

### Ledger Entry Schema
Each entry contains:
```json
{
  "id": "unique_identifier",
  "date": "YYYY-MM-DD",
  "amount": 123.45,
  "category": "category_name",
  "description": "transaction description",
  "type": "income" or "expense",
  "tags": ["tag1", "tag2"]
}
```

### CRUD Operations
- **Create**: `create_entry()` - Add new transactions
- **Read**: `get_entry()`, `get_entries()` - Retrieve transactions
- **Update**: `update_entry()` - Modify existing transactions
- **Delete**: `delete_entry()` - Remove transactions

## MCP Server Integration
The MCP server provides external access through HTTP endpoints:

### POST Endpoint
```json
{
  "command": "create_entry",
  "args": {
    "amount": 100.00,
    "category": "sales",
    "description": "Product sale",
    "type": "income"
  }
}
```

### GET Endpoints
- `GET /query/summary?[start_date=YYYY-MM-DD&end_date=YYYY-MM-DD]` - Financial summary
- `GET /query/weekly?[week_start=YYYY-MM-DD]` - Weekly summary
- `GET /query/entries?[type=income&start_date=YYYY-MM-DD]` - Transaction list

## Weekly Financial Summary Template
The system generates comprehensive CEO reports including:
- Income and expense breakdowns
- Category-wise analysis
- Trend analysis with week-over-week comparisons
- Key financial metrics (profit margin, etc.)
- AI-generated recommendations

## Usage Examples

### Basic Usage
```python
from ledger_manager import LedgerManager

# Initialize the ledger
ledger = LedgerManager()

# Add an income entry
income_id = ledger.create_entry(
    amount=1500.00,
    category="sales",
    description="Website development project",
    entry_type="income",
    tags=["project", "client_a"]
)

# Add an expense entry
expense_id = ledger.create_entry(
    amount=300.00,
    category="marketing",
    description="Google Ads campaign",
    entry_type="expense"
)
```

### Financial Summaries
```python
# Get financial summary for a date range
summary = ledger.get_financial_summary("2026-01-01", "2026-01-31")
print(f"Total Income: ${summary['total_income']}")
print(f"Total Expenses: ${summary['total_expenses']}")
print(f"Profit/Loss: ${summary['profit_loss']}")
```

### Weekly Reports
```python
from weekly_summary_template import generate_weekly_summary_report, save_weekly_summary_report

# Generate weekly summary
weekly_summary = ledger.generate_weekly_summary()

# Generate formatted report
report_text = generate_weekly_summary_report(weekly_summary)
print(report_text)

# Save to file
file_path = save_weekly_summary_report(weekly_summary)
print(f"Report saved to: {file_path}")
```

### MCP Server
```python
from ledger_mcp_server import start_mcp_server

# Start the MCP server
start_mcp_server(port=3001)
```

## MCP Server Commands
- `create_entry`: Create a new ledger entry
- `get_entry`: Get a specific entry by ID
- `update_entry`: Update an existing entry
- `delete_entry`: Delete an entry
- `get_entries`: Get entries with optional filters
- `get_financial_summary`: Get financial summary
- `generate_weekly_summary`: Generate weekly report
- `backup_data`: Create data backup
- `restore_from_backup`: Restore from backup

## Data Management
- **Backup**: `backup_data()` creates a backup of all ledger data
- **Restore**: `restore_from_backup()` restores from backup
- **Export/Import**: JSON format supports external tool integration
- **Audit Trail**: All changes are tracked through the system

The Ledger Manager provides a complete, modular financial tracking solution that integrates seamlessly with the MCP protocol for external access and generates comprehensive financial reports for management.