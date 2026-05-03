# Odoo Integration Skill

## Purpose
The Odoo Integration skill provides integration with Odoo Community Edition for accounting system functionality using JSON-RPC APIs. It synchronizes financial data between the local system and Odoo, handles accounting operations, and provides MCP server integration for external access.

## Configuration
The skill requires Odoo connection settings:

```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
    "enabled": true
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

## Core Functions

### 1. Odoo Connection Management
- Establish connection to Odoo via JSON-RPC
- Handle authentication and session management
- Manage connection pooling and error recovery

### 2. Data Synchronization
- Bidirectional sync between local and Odoo accounting data
- Conflict resolution for concurrent updates
- Incremental sync to minimize data transfer

### 3. MCP Server Integration
- Provide external access to Odoo operations via MCP protocol
- Support for CRUD operations on accounting records
- Authentication and authorization for external access

### 4. Accounting Operations
- Create financial transactions in Odoo
- Retrieve financial reports and statements
- Handle invoices, payments, and journal entries
- Manage accounts, partners, and products