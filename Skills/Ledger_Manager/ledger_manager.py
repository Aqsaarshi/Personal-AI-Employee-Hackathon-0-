"""
Ledger Manager Skill
Maintains a lightweight local accounting system (JSON/SQLite)
Records income, expenses, profit/loss
Provides query access and generates financial summaries
"""
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, TYPE_CHECKING
import logging
from pathlib import Path
import copy
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if TYPE_CHECKING:
    from Skills.Odoo_Integration.odoo_integration import OdooIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LedgerEntry:
    """Represents a single financial transaction"""
    def __init__(self, entry_id: str, date: str, amount: float, category: str, description: str, entry_type: str, tags: List[str] = None):
        self.id = entry_id
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description
        self.type = entry_type  # "income" or "expense"
        self.tags = tags or []

    def to_dict(self) -> Dict:
        """Convert the ledger entry to a dictionary"""
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "type": self.type,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create a LedgerEntry from a dictionary"""
        return cls(
            entry_id=data["id"],
            date=data["date"],
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            entry_type=data["type"],
            tags=data.get("tags", [])
        )

class LedgerManager:
    def __init__(self, config_path: str = "Skills/Ledger_Manager/config.json"):
        """Initialize the Ledger Manager with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # Initialize database based on config
        self.db_type = self.config["database"]["type"]
        self.db_path = self.config["database"]["path"]

        # Create backup directory if needed
        backup_path = self.config["database"].get("backup_path", "backups/ledger_backup.json")
        backup_dir = os.path.dirname(backup_path)
        if backup_dir:
            os.makedirs(backup_dir, exist_ok=True)

        # Initialize the database
        self._init_database()

        # Define categories
        self.income_categories = self.config["categories"]["income"]
        self.expense_categories = self.config["categories"]["expenses"]

        # Load existing data
        self.entries = self._load_entries()

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "database": {
                "type": "json",  # "json" or "sqlite"
                "path": "ledger_data.json",
                "backup_enabled": True,
                "backup_path": "backups/ledger_backup.json"
            },
            "categories": {
                "income": ["sales", "consulting", "investment", "other_income"],
                "expenses": ["office_rent", "utilities", "salaries", "marketing", "travel", "software", "hardware", "other_expenses"]
            },
            "mcp_server": {
                "enabled": True,
                "port": 3001,
                "host": "localhost"
            },
            "reporting": {
                "weekly_summary_day": "fri",
                "currency": "USD"
            }
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config file
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at {self.config_path}")
            return default_config

    def _init_database(self):
        """Initialize the database based on configuration."""
        if self.db_type == "json":
            # Create JSON file if it doesn't exist
            if not os.path.exists(self.db_path):
                with open(self.db_path, 'w') as f:
                    json.dump([], f)
        elif self.db_type == "sqlite":
            # Initialize SQLite database
            self._init_sqlite_db()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _init_sqlite_db(self):
        """Initialize SQLite database with proper schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledger_entries (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                tags TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _load_entries(self) -> List[LedgerEntry]:
        """Load entries from the database."""
        if self.db_type == "json":
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            return [LedgerEntry.from_dict(entry) for entry in data]
        elif self.db_type == "sqlite":
            return self._load_entries_sqlite()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _load_entries_sqlite(self) -> List[LedgerEntry]:
        """Load entries from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ledger_entries")
        rows = cursor.fetchall()

        entries = []
        for row in rows:
            entry = LedgerEntry(
                entry_id=row[0],
                date=row[1],
                amount=row[2],
                category=row[3],
                description=row[4],
                entry_type=row[5],
                tags=json.loads(row[6]) if row[6] else []
            )
            entries.append(entry)

        conn.close()
        return entries

    def _save_entries(self):
        """Save entries to the database."""
        if self.db_type == "json":
            data = [entry.to_dict() for entry in self.entries]
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif self.db_type == "sqlite":
            self._save_entries_sqlite()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _save_entries_sqlite(self):
        """Save entries to SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing entries
        cursor.execute("DELETE FROM ledger_entries")

        # Insert all entries
        for entry in self.entries:
            cursor.execute('''
                INSERT INTO ledger_entries (id, date, amount, category, description, type, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.id,
                entry.date,
                entry.amount,
                entry.category,
                entry.description,
                entry.type,
                json.dumps(entry.tags)
            ))

        conn.commit()
        conn.close()

    def create_entry(self, amount: float, category: str, description: str, entry_type: str, date: str = None, tags: List[str] = None) -> str:
        """Create a new ledger entry."""
        # Validate entry type
        if entry_type not in ["income", "expense"]:
            raise ValueError(f"Invalid entry type: {entry_type}. Must be 'income' or 'expense'")

        # Validate category
        if entry_type == "income" and category not in self.income_categories:
            raise ValueError(f"Invalid income category: {category}")
        if entry_type == "expense" and category not in self.expense_categories:
            raise ValueError(f"Invalid expense category: {category}")

        # Use current date if not provided
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Generate unique ID
        entry_id = f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.entries)}"

        # Create the entry
        entry = LedgerEntry(
            entry_id=entry_id,
            date=date,
            amount=amount,
            category=category,
            description=description,
            entry_type=entry_type,
            tags=tags or []
        )

        # Add to entries and save
        self.entries.append(entry)
        self._save_entries()

        logger.info(f"Created {entry_type} entry: {entry_id} - ${amount} for {category}")
        return entry_id

    def get_entry(self, entry_id: str) -> Optional[LedgerEntry]:
        """Get a specific ledger entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def update_entry(self, entry_id: str, amount: float = None, category: str = None,
                    description: str = None, entry_type: str = None, date: str = None, tags: List[str] = None) -> bool:
        """Update an existing ledger entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return False

        # Validate updates
        if entry_type is not None:
            if entry_type not in ["income", "expense"]:
                raise ValueError(f"Invalid entry type: {entry_type}. Must be 'income' or 'expense'")
            entry.type = entry_type

        if category is not None:
            if entry.type == "income" and category not in self.income_categories:
                raise ValueError(f"Invalid income category: {category}")
            if entry.type == "expense" and category not in self.expense_categories:
                raise ValueError(f"Invalid expense category: {category}")
            entry.category = category

        if amount is not None:
            entry.amount = amount
        if date is not None:
            entry.date = date
        if description is not None:
            entry.description = description
        if tags is not None:
            entry.tags = tags

        self._save_entries()
        return True

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a ledger entry."""
        original_count = len(self.entries)
        self.entries = [entry for entry in self.entries if entry.id != entry_id]

        if len(self.entries) < original_count:
            self._save_entries()
            logger.info(f"Deleted entry: {entry_id}")
            return True
        return False

    def get_entries(self, start_date: str = None, end_date: str = None,
                   entry_type: str = None, category: str = None) -> List[LedgerEntry]:
        """Get entries with optional filters."""
        filtered_entries = self.entries.copy()

        # Apply date filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            filtered_entries = [
                e for e in filtered_entries
                if datetime.strptime(e.date, "%Y-%m-%d") >= start_dt
            ]

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            filtered_entries = [
                e for e in filtered_entries
                if datetime.strptime(e.date, "%Y-%m-%d") <= end_dt
            ]

        # Apply type filter
        if entry_type:
            filtered_entries = [e for e in filtered_entries if e.type == entry_type]

        # Apply category filter
        if category:
            filtered_entries = [e for e in filtered_entries if e.category == category]

        return filtered_entries

    def get_financial_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get financial summary including income, expenses, and profit/loss."""
        entries = self.get_entries(start_date, end_date)

        total_income = 0
        total_expenses = 0
        income_by_category = {}
        expenses_by_category = {}

        for entry in entries:
            if entry.type == "income":
                total_income += entry.amount
                income_by_category[entry.category] = income_by_category.get(entry.category, 0) + entry.amount
            elif entry.type == "expense":
                total_expenses += entry.amount
                expenses_by_category[entry.category] = expenses_by_category.get(entry.category, 0) + entry.amount

        profit_loss = total_income - total_expenses

        return {
            "period_start": start_date or "beginning",
            "period_end": end_date or "now",
            "total_income": total_income,
            "total_expenses": total_expenses,
            "profit_loss": profit_loss,
            "income_by_category": income_by_category,
            "expenses_by_category": expenses_by_category,
            "currency": self.config["reporting"]["currency"]
        }

    def generate_weekly_summary(self, week_start: str = None) -> Dict:
        """Generate a weekly financial summary for CEO reports."""
        if not week_start:
            # Calculate the start of the current week (Monday)
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start_dt = today - timedelta(days=days_since_monday)
            week_start = week_start_dt.strftime("%Y-%m-%d")

        # Calculate the end of the week (Sunday)
        week_start_dt = datetime.strptime(week_start, "%Y-%m-%d")
        week_end_dt = week_start_dt + timedelta(days=6)
        week_end = week_end_dt.strftime("%Y-%m-%d")

        # Get weekly summary
        summary = self.get_financial_summary(week_start, week_end)
        summary["week_start"] = week_start
        summary["week_end"] = week_end

        # Add trend analysis
        prev_week_start = (week_start_dt - timedelta(weeks=1)).strftime("%Y-%m-%d")
        prev_week_end = (week_end_dt - timedelta(weeks=1)).strftime("%Y-%m-%d")
        prev_summary = self.get_financial_summary(prev_week_start, prev_week_end)

        # Calculate changes
        income_change = summary["total_income"] - prev_summary["total_income"]
        expense_change = summary["total_expenses"] - prev_summary["total_expenses"]
        profit_change = summary["profit_loss"] - prev_summary["profit_loss"]

        summary["comparisons"] = {
            "income_change_from_prev_week": income_change,
            "expense_change_from_prev_week": expense_change,
            "profit_loss_change_from_prev_week": profit_change
        }

        summary["trend_analysis"] = self._analyze_trends(week_start, week_end)

        return summary

    def _analyze_trends(self, start_date: str, end_date: str) -> Dict:
        """Analyze financial trends."""
        # Get data for the specified period
        entries = self.get_entries(start_date, end_date)

        # Group by day to look for patterns
        daily_totals = {}
        for entry in entries:
            day = entry.date
            if day not in daily_totals:
                daily_totals[day] = {"income": 0, "expenses": 0}

            if entry.type == "income":
                daily_totals[day]["income"] += entry.amount
            else:
                daily_totals[day]["expenses"] += entry.amount

        # Find top categories
        incomes = {}
        expenses = {}
        for entry in entries:
            if entry.type == "income":
                incomes[entry.category] = incomes.get(entry.category, 0) + entry.amount
            else:
                expenses[entry.category] = expenses.get(entry.category, 0) + entry.amount

        return {
            "daily_patterns": daily_totals,
            "top_income_sources": sorted(incomes.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_expense_categories": sorted(expenses.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def backup_data(self) -> bool:
        """Create a backup of the ledger data."""
        if not self.config["database"]["backup_enabled"]:
            logger.info("Backup is disabled in configuration")
            return False

        try:
            backup_path = self.config["database"]["backup_path"]
            if self.db_type == "json":
                # For JSON, simply copy the file
                with open(self.db_path, 'r') as src:
                    data = json.load(src)
                with open(backup_path, 'w') as dest:
                    json.dump(data, dest, indent=2)
            elif self.db_type == "sqlite":
                # For SQLite, do a proper backup
                src = sqlite3.connect(self.db_path)
                dest = sqlite3.connect(backup_path)
                src.backup(dest)
                dest.close()
                src.close()

            logger.info(f"Backup created at: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False

    def restore_from_backup(self) -> bool:
        """Restore ledger data from backup."""
        try:
            backup_path = self.config["database"]["backup_path"]
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False

            if self.db_type == "json":
                # For JSON, copy the backup file to main path
                with open(backup_path, 'r') as src:
                    data = json.load(src)
                with open(self.db_path, 'w') as dest:
                    json.dump(data, dest, indent=2)
            elif self.db_type == "sqlite":
                # For SQLite, copy the backup to main path
                import shutil
                shutil.copy2(backup_path, self.db_path)

            # Reload entries
            self.entries = self._load_entries()
            logger.info(f"Restored from backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False

    def sync_from_odoo(self, odoo_integration: 'OdooIntegration') -> Dict:
        """Sync paid invoices from Odoo to the local ledger."""
        sync_result = {
            "status": "started",
            "synced_invoices": 0,
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        try:
            logger.info("Starting Odoo to Ledger sync...")

            # First, check if we need to import OdooIntegration
            if 'OdooIntegration' not in str(type(odoo_integration)):
                # Import it dynamically to avoid circular imports
                from Skills.Odoo_Integration.odoo_integration import OdooIntegration

            # Get paid invoices from Odoo
            odoo_moves = odoo_integration.search_read(
                model="account.move",
                domain=[
                    ["move_type", "=", "out_invoice"],  # Customer invoices
                    ["payment_state", "=", "paid"],  # Only paid invoices
                    ["state", "=", "posted"]  # Posted invoices
                ],
                fields=[
                    "id", "name", "ref", "invoice_date", "invoice_date_due",
                    "amount_total", "partner_id", "invoice_payment_term_id"
                ],
                order="invoice_date ASC"
            )

            logger.info(f"Found {len(odoo_moves)} paid invoices in Odoo")

            # Sync each invoice as an income entry
            for move in odoo_moves:
                try:
                    # Check if this invoice already exists in our ledger
                    invoice_number = move.get("name", "")
                    invoice_exists = any(
                        invoice_number in entry.description
                        for entry in self.entries
                    )

                    if invoice_exists:
                        logger.info(f"Skipping duplicate invoice: {invoice_number}")
                        continue

                    # Determine category based on invoice content or partner
                    category = "sales"
                    partner_name = ""
                    if move.get("partner_id"):
                        partner_info = odoo_integration.get_partner_info(move["partner_id"][0])
                        partner_name = partner_info.get("name", "")

                        # Map categories based on partner or other criteria
                        if "consulting" in (partner_name or "").lower():
                            category = "consulting"

                    # Create the ledger entry
                    description = f"Odoo Invoice: {invoice_number}"
                    if partner_name:
                        description += f" - {partner_name}"

                    entry_date = move.get("invoice_date") or move.get("date") or datetime.now().strftime("%Y-%m-%d")
                    amount = float(move.get("amount_total", 0))

                    # Skip zero or negative amounts
                    if amount <= 0:
                        continue

                    entry_id = self.create_entry(
                        amount=amount,
                        category=category,
                        description=description,
                        entry_type="income",
                        date=entry_date,
                        tags=["odoo_sync", "invoice"]
                    )

                    sync_result["synced_invoices"] += 1
                    logger.info(f"Synced invoice {invoice_number} as entry {entry_id}")

                except Exception as e:
                    error_msg = f"Failed to sync invoice {move.get('name', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    sync_result["errors"].append(error_msg)
                    continue

            # Save entries
            self._save_entries()

            sync_result["status"] = "completed"
            total_invoices = len(odoo_moves)
            logger.info(f"Sync completed: {sync_result['synced_invoices']}/{total_invoices} invoices synced successfully")

        except Exception as e:
            error_msg = f"Odoo sync failed: {str(e)}"
            logger.error(error_msg)
            sync_result["status"] = "failed"
            sync_result["errors"].append(error_msg)

        return sync_result

# Example usage
if __name__ == "__main__":
    # Initialize the Ledger Manager
    ledger = LedgerManager()

    print("Ledger Manager initialized successfully!")

    # Example: Create some entries
    print("\nCreating sample entries...")

    # Add some income
    income_id = ledger.create_entry(
        amount=1500.00,
        category="sales",
        description="Website development project payment",
        entry_type="income",
        tags=["project", "client_a"]
    )
    print(f"Added income entry: {income_id}")

    # Add some expenses
    expense_id = ledger.create_entry(
        amount=300.00,
        category="marketing",
        description="Google Ads campaign",
        entry_type="expense",
        tags=["q1", "advertising"]
    )
    print(f"Added expense entry: {expense_id}")

    # Get financial summary
    print("\nGenerating financial summary...")
    summary = ledger.get_financial_summary()
    print(f"Total Income: ${summary['total_income']}")
    print(f"Total Expenses: ${summary['total_expenses']}")
    print(f"Profit/Loss: ${summary['profit_loss']}")

    # Generate weekly summary
    print("\nGenerating weekly summary...")
    weekly_summary = ledger.generate_weekly_summary()
    print(f"Weekly Income: ${weekly_summary['total_income']}")
    print(f"Weekly Expenses: ${weekly_summary['total_expenses']}")
    print(f"Weekly Profit/Loss: ${weekly_summary['profit_loss']}")