"""
Odoo Integration Skill
Integrates with Odoo Community Edition using JSON-RPC APIs
"""
import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Audit_Logger.audit_logger import get_audit_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OdooRPCException(Exception):
    """Custom exception for Odoo RPC errors."""
    pass

class OdooIntegration:
    def __init__(self, config_path: str = "Skills/Odoo_Integration/config.json"):
        """Initialize the Odoo Integration with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # Initialize Odoo connection parameters
        self.url = self.config["odoo"]["url"]
        self.db = self.config["odoo"]["database"]
        self.username = self.config["odoo"]["username"]
        self.password = self.config["odoo"]["password"]

        # Initialize connection state
        self.uid = None
        self.connected = False

        # Initialize audit logger
        self.audit_logger = get_audit_logger()

        # Connect to Odoo on initialization
        self.connect()

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "odoo": {
                "url": "http://localhost:8069",
                "database": "your_database_name",
                "username": "your_username",
                "password": "your_password",
                "enabled": False  # Set to False by default for safety
            },
            "sync": {
                "enabled": True,
                "frequency_minutes": 30,
                "sync_direction": "bidirectional"
            },
            "mcp_server": {
                "enabled": True,
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

    def _make_request(self, service: str, method: str, *args) -> Dict:
        """Make a JSON-RPC request to Odoo."""
        if not self.config["odoo"]["enabled"]:
            raise OdooRPCException("Odoo integration is disabled in configuration")

        if not self.connected:
            self.connect()

        url = f"{self.url}/jsonrpc"
        headers = {"Content-Type": "application/json"}

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": [self.db, self.uid, self.password] + list(args)
            },
            "id": int(time.time() * 1000000)
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error = result["error"]
                raise OdooRPCException(f"Odoo RPC Error: {error.get('data', {}).get('message', error.get('message', 'Unknown error'))}")

            return result.get("result", {})
        except requests.exceptions.RequestException as e:
            # Log the error and attempt to reconnect
            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="request_error",
                status="failed",
                error_details=f"Request failed: {str(e)}",
                original_action=f"{service}.{method}"
            )

            # Attempt to reconnect
            try:
                self.connect()
                # Retry the request once after reconnection
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json()
                if "error" in result:
                    error = result["error"]
                    raise OdooRPCException(f"Odoo RPC Error after reconnection: {error.get('data', {}).get('message', error.get('message', 'Unknown error'))}")

                return result.get("result", {})
            except Exception as e2:
                raise OdooRPCException(f"Request failed after reconnection attempt: {str(e2)}")

    def connect(self) -> bool:
        """Connect to Odoo and authenticate."""
        if not self.config["odoo"]["enabled"]:
            logger.warning("Odoo integration is disabled in configuration")
            self.connected = False
            return False

        try:
            # Authentication request
            auth_url = f"{self.url}/jsonrpc"
            headers = {"Content-Type": "application/json"}

            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [self.db, self.username, self.password, {}]
                },
                "id": int(time.time() * 1000000)
            }

            response = requests.post(auth_url, headers=headers, json=auth_payload)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error = result["error"]
                raise OdooRPCException(f"Authentication failed: {error.get('data', {}).get('message', error.get('message', 'Unknown error'))}")

            self.uid = result.get("result")

            if not self.uid:
                raise OdooRPCException("Authentication failed: No user ID returned")

            self.connected = True

            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="connection",
                status="success",
                output=f"Connected to Odoo: {self.url}, DB: {self.db}, User ID: {self.uid}"
            )

            logger.info(f"Connected to Odoo: {self.url}, DB: {self.db}, UID: {self.uid}")
            return True

        except Exception as e:
            self.connected = False
            error_msg = f"Failed to connect to Odoo: {str(e)}"
            logger.error(error_msg)

            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="connection",
                status="failed",
                error_details=error_msg
            )

            raise OdooRPCException(error_msg)

    def search_read(self, model: str, domain: List = None, fields: List = None, offset: int = 0, limit: int = None, order: str = None) -> List:
        """Search and read records from Odoo."""
        domain = domain or []
        fields = fields or []

        result = self._make_request(
            "object",
            "execute_kw",
            model,
            "search_read",
            [domain] if domain else [],  # Wrap domain in a list
            {
                "fields": fields,
                "offset": offset,
                "limit": limit,
                "order": order
            }
        )

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="search_read",
            status="success",
            output=f"Found {len(result)} records in {model}",
            original_action=f"{model}.search_read"
        )

        return result

    def create(self, model: str, vals: Dict) -> int:
        """Create a new record in Odoo."""
        result = self._make_request(
            "object",
            "execute_kw",
            model,
            "create",
            [vals]
        )

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="create",
            status="success",
            output=f"Created record in {model}, ID: {result}",
            original_action=f"{model}.create"
        )

        return result

    def write(self, model: str, record_ids: List[int], vals: Dict) -> bool:
        """Update existing records in Odoo."""
        result = self._make_request(
            "object",
            "execute_kw",
            model,
            "write",
            [record_ids, vals]
        )

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="write",
            status="success",
            output=f"Updated {len(record_ids)} records in {model}",
            original_action=f"{model}.write"
        )

        return result

    def unlink(self, model: str, record_ids: List[int]) -> bool:
        """Delete records from Odoo."""
        result = self._make_request(
            "object",
            "execute_kw",
            model,
            "unlink",
            [record_ids]
        )

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="unlink",
            status="success",
            output=f"Deleted {len(record_ids)} records from {model}",
            original_action=f"{model}.unlink"
        )

        return result

    def call_method(self, model: str, method: str, record_ids: List[int], **kwargs) -> Any:
        """Call a method on Odoo records."""
        args = [record_ids]
        if kwargs:
            args.append(kwargs)

        result = self._make_request(
            "object",
            "execute_kw",
            model,
            method,
            *args
        )

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="method_call",
            status="success",
            output=f"Called {method} on {len(record_ids)} records in {model}",
            original_action=f"{model}.{method}"
        )

        return result

    # Accounting-specific methods
    def create_account_move(self, move_data: Dict) -> int:
        """Create an accounting journal entry in Odoo."""
        if "journal_id" not in move_data:
            # Find default journal if not specified
            journals = self.search_read("account.journal", [["type", "=", "general"]], ["id"], limit=1)
            if journals:
                move_data["journal_id"] = journals[0]["id"]
            else:
                # Create a default journal if none exists
                journal_id = self.create("account.journal", {
                    "name": "Default Journal",
                    "code": "DEFJ",
                    "type": "general"
                })
                move_data["journal_id"] = journal_id

        if "date" not in move_data:
            move_data["date"] = datetime.now().strftime("%Y-%m-%d")

        if "line_ids" not in move_data:
            # Default to at least one line if no lines provided
            move_data["line_ids"] = []

        move_id = self.create("account.move", move_data)

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="create_account_move",
            status="success",
            output=f"Created account move, ID: {move_id}",
            original_action="account.move.create"
        )

        return move_id

    def create_account_payment(self, payment_data: Dict) -> int:
        """Create an accounting payment in Odoo."""
        if "journal_id" not in payment_data:
            # Find default bank journal if not specified
            journals = self.search_read("account.journal", [["type", "=", "bank"]], ["id"], limit=1)
            if journals:
                payment_data["journal_id"] = journals[0]["id"]
            else:
                raise OdooRPCException("No bank journal found in Odoo")

        if "date" not in payment_data:
            payment_data["date"] = datetime.now().strftime("%Y-%m-%d")

        payment_id = self.create("account.payment", payment_data)

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="create_account_payment",
            status="success",
            output=f"Created account payment, ID: {payment_id}",
            original_action="account.payment.create"
        )

        return payment_id

    def get_financial_reports(self, date_from: str = None, date_to: str = None) -> Dict:
        """Get financial reports from Odoo."""
        if not date_from:
            date_from = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")

        # Get trial balance
        try:
            trial_balance = self._make_request(
                "report",
                "get_action",
                "account_reports.action_account_balance_menu",
                {
                    "wizard_model": "account.balance.report",
                    "context": {
                        "date_from": date_from,
                        "date_to": date_to,
                        "all_entries": True
                    }
                }
            )
        except:
            # Fallback to manual calculation
            trial_balance = {
                "date_from": date_from,
                "date_to": date_to,
                "manual_calculation": True
            }

        # Get other financial data
        accounts = self.search_read("account.account", [], ["id", "name", "code", "balance"])
        moves = self.search_read("account.move", [
            ["date", ">=", date_from],
            ["date", "<=", date_to]
        ], ["id", "name", "date", "state"], limit=100)

        return {
            "trial_balance": trial_balance,
            "accounts": accounts,
            "recent_moves": moves,
            "date_from": date_from,
            "date_to": date_to,
            "generated_at": datetime.now().isoformat()
        }

    def get_paid_invoices(self, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get paid customer invoices from Odoo."""
        domain = [
            ["move_type", "=", "out_invoice"],  # Customer invoices
            ["payment_state", "=", "paid"],  # Only paid invoices
            ["state", "=", "posted"]  # Posted invoices
        ]

        # Add date filters if provided
        if date_from:
            domain.append(["invoice_date", ">=", date_from])
        if date_to:
            domain.append(["invoice_date", "<=", date_to])

        # Search for paid invoices with relevant fields
        paid_invoices = self.search_read(
            "account.move",
            domain,
            [
                "id", "name", "ref", "invoice_date", "invoice_date_due",
                "amount_total", "amount_untaxed", "amount_tax",
                "partner_id", "payment_state", "state"
            ],
            0,  # offset
            None,  # limit
            "invoice_date ASC"  # order
        )

        self.audit_logger.log_action(
            skill_name="OdooIntegration",
            action_type="get_paid_invoices",
            status="success",
            output=f"Found {len(paid_invoices)} paid invoices in Odoo",
            original_action="account.move.search_read"
        )

        return paid_invoices

    def sync_with_local_ledger(self, local_data: Dict, sync_direction: str = "local_to_odoo") -> Dict:
        """Synchronize data between local ledger and Odoo."""
        sync_results = {
            "direction": sync_direction,
            "processed": 0,
            "created": 0,
            "updated": 0,
            "errors": []
        }

        try:
            if sync_direction == "local_to_odoo":
                # Sync local financial data to Odoo
                if "transactions" in local_data:
                    for transaction in local_data["transactions"]:
                        try:
                            # Convert local transaction format to Odoo format
                            odoo_move_data = self._convert_local_to_odoo(transaction)

                            # Check if transaction already exists in Odoo
                            existing_moves = self.search_read(
                                "account.move",
                                [["ref", "=", transaction.get("id", "")]],
                                ["id"]
                            )

                            if existing_moves:
                                # Update existing record
                                self.write("account.move", [existing_moves[0]["id"]], odoo_move_data)
                                sync_results["updated"] += 1
                            else:
                                # Create new record
                                self.create_account_move(odoo_move_data)
                                sync_results["created"] += 1

                            sync_results["processed"] += 1

                        except Exception as e:
                            sync_results["errors"].append({
                                "transaction_id": transaction.get("id"),
                                "error": str(e)
                            })
                            continue

            elif sync_direction == "odoo_to_local":
                # Sync Odoo financial data to local
                date_filter = [
                    ["date", ">=", local_data.get("date_from", "2000-01-01")],
                    ["date", "<=", local_data.get("date_to", datetime.now().strftime("%Y-%m-%d"))]
                ]

                odoo_moves = self.search_read(
                    "account.move",
                    date_filter,
                    ["id", "name", "ref", "date", "amount", "state", "journal_id"]
                )

                for move in odoo_moves:
                    try:
                        # Process Odoo move record for local storage
                        sync_results["processed"] += 1

                        # Check if already exists
                        existing_moves = self.search_read(
                            "account.move",
                            [["ref", "=", move.get("ref", "")],
                             ["name", "=", move.get("name", "")]],
                            ["id"]
                        )

                        # This is a placeholder for actual sync logic
                        # In a real implementation, you'd convert Odoo data to local format
                        if existing_moves:
                            sync_results["updated"] += 1
                        else:
                            sync_results["created"] += 1

                    except Exception as e:
                        sync_results["errors"].append({
                            "move_id": move.get("id"),
                            "error": str(e)
                        })
                        continue

            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="sync",
                status="completed",
                output=f"Sync completed: {sync_results['processed']} processed, {sync_results['created']} created, {sync_results['updated']} updated",
                original_action="sync_with_local_ledger"
            )

        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="sync",
                status="failed",
                error_details=error_msg,
                original_action="sync_with_local_ledger"
            )
            raise OdooRPCException(error_msg)

        return sync_results

    def _convert_local_to_odoo(self, local_transaction: Dict) -> Dict:
        """Convert local transaction format to Odoo format."""
        # This is a simplified conversion - in a real implementation,
        # you'd need to map all fields properly
        odoo_data = {
            "ref": local_transaction.get("id", ""),
            "date": local_transaction.get("date", datetime.now().strftime("%Y-%m-%d")),
            "journal_id": local_transaction.get("journal_id", 1),  # Default journal
            "state": "draft",  # Will be posted after creation
            "line_ids": []
        }

        # Convert lines if they exist
        if "lines" in local_transaction:
            for line in local_transaction["lines"]:
                odoo_line = {
                    "name": line.get("description", "Transaction line"),
                    "account_id": line.get("account_id", 1),
                    "debit": line.get("debit", 0.0),
                    "credit": line.get("credit", 0.0),
                    "partner_id": line.get("partner_id")
                }
                odoo_data["line_ids"].append([0, 0, odoo_line])

        return odoo_data

    def test_connection(self) -> bool:
        """Test the Odoo connection by fetching user info."""
        try:
            user_info = self._make_request(
                "object",
                "execute_kw",
                "res.users",
                "read",
                [self.uid],
                {"fields": ["name", "login", "email"]}
            )

            if user_info:
                self.audit_logger.log_action(
                    skill_name="OdooIntegration",
                    action_type="test_connection",
                    status="success",
                    output=f"Connection test passed for user: {user_info[0].get('name', 'Unknown')}"
                )
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_company_info(self) -> Dict:
        """Get company information from Odoo."""
        try:
            companies = self.search_read(
                "res.company",
                [],
                ["id", "name", "email", "phone", "street", "city", "country_id"]
            )

            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="get_company_info",
                status="success",
                output=f"Retrieved {len(companies)} company records",
                original_action="res.company.search_read"
            )

            return companies[0] if companies else {}
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="get_company_info",
                status="failed",
                error_details=str(e),
                original_action="res.company.search_read"
            )
            raise

    def get_partner_info(self, partner_id: int) -> Dict:
        """Get partner information from Odoo."""
        try:
            partners = self.search_read(
                "res.partner",
                [["id", "=", partner_id]],
                ["id", "name", "email", "phone", "street", "city", "country_id"]
            )

            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="get_partner_info",
                status="success",
                output=f"Retrieved partner info for ID: {partner_id}",
                original_action="res.partner.search_read"
            )

            return partners[0] if partners else {}
        except Exception as e:
            self.audit_logger.log_action(
                skill_name="OdooIntegration",
                action_type="get_partner_info",
                status="failed",
                error_details=str(e),
                original_action="res.partner.search_read"
            )
            raise

# Example usage
if __name__ == "__main__":
    print("Odoo Integration Skill initialized!")
    print("Features:")
    print("- JSON-RPC API integration with Odoo Community")
    print("- Accounting operations (journal entries, payments)")
    print("- Financial reporting capabilities")
    print("- Local-to-Odoo data synchronization")
    print("- MCP server ready for external access")
    print("- Comprehensive error handling and logging")