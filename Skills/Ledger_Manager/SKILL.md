# Ledger Manager Skill

## Purpose
The Ledger Manager skill maintains a lightweight local accounting system using JSON/SQLite to record income, expenses, profit/loss. It provides query access through an MCP server and generates weekly financial summaries for CEO reports.

## Configuration
The skill requires a configuration file with database settings and financial categories:

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

## Core Functions

### 1. Ledger Schema & CRUD Operations
- Create, Read, Update, Delete financial transactions
- Support for income and expense entries
- Categorization and tagging of transactions
- Validation of transaction data

### 2. MCP Server Integration
- Provides external query access to ledger data
- RESTful API endpoints for transaction management
- Security and authentication for sensitive data
- Query operations for financial reports

### 3. Weekly Financial Summaries
- Aggregates income, expenses, and profit/loss
- Generates CEO reports with key financial metrics
- Trend analysis and comparison with previous periods
- Export capabilities for financial dashboards

### 4. Data Management
- Backup and restore functionality
- Data validation and integrity checks
- Import/export capabilities for external tools
- Audit trail for all financial changes