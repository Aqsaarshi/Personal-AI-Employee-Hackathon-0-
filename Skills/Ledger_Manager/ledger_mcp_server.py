"""
Ledger MCP Server
Provides external query access to the ledger data through MCP protocol
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime
import logging

import sys
import os
# Add the project root to the path so we can import from Skills
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Ledger_Manager.ledger_manager import LedgerManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LedgerMCPHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.ledger_manager = LedgerManager()
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests for ledger operations."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            request_data = json.loads(post_data.decode('utf-8'))
            command = request_data.get('command')
            args = request_data.get('args', {})

            # Process the command
            result = self.process_command(command, args)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON in request")
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            self.send_error_response(f"Error processing request: {str(e)}")

    def do_GET(self):
        """Handle GET requests for simple queries."""
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')

        try:
            if path_parts[0] == "query":
                # Parse query parameters
                query_params = parse_qs(parsed_path.query)

                # Build args from query parameters
                args = {}
                for key, values in query_params.items():
                    # Take the first value for each parameter
                    value = values[0] if values else None
                    # Convert numeric values
                    if value and value.replace('.', '').replace('-', '').isdigit():
                        args[key] = float(value) if '.' in value else int(value)
                    else:
                        args[key] = value

                # Process query based on path
                if path_parts[1] == "summary":
                    result = self.process_command("get_financial_summary", args)
                elif path_parts[1] == "weekly":
                    result = self.process_command("generate_weekly_summary", args)
                elif path_parts[1] == "entries":
                    result = self.process_command("get_entries", args)
                else:
                    result = {"success": False, "error": f"Unknown query: {path_parts[1]}"}

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
            else:
                self.send_error_response(f"Unknown endpoint: {'/'.join(path_parts)}")

        except Exception as e:
            logger.error(f"Error processing GET request: {str(e)}")
            self.send_error_response(f"Error processing GET request: {str(e)}")

    def process_command(self, command: str, args: dict):
        """Process ledger commands."""
        logger.info(f"Processing command: {command} with args: {args}")

        try:
            if command == "create_entry":
                return self.handle_create_entry(args)
            elif command == "get_entry":
                return self.handle_get_entry(args)
            elif command == "update_entry":
                return self.handle_update_entry(args)
            elif command == "delete_entry":
                return self.handle_delete_entry(args)
            elif command == "get_entries":
                return self.handle_get_entries(args)
            elif command == "get_financial_summary":
                return self.handle_get_financial_summary(args)
            elif command == "generate_weekly_summary":
                return self.handle_generate_weekly_summary(args)
            elif command == "backup_data":
                return self.handle_backup_data(args)
            elif command == "restore_from_backup":
                return self.handle_restore_from_backup(args)
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
        except Exception as e:
            logger.error(f"Error processing command {command}: {str(e)}")
            return {"success": False, "error": str(e)}

    def handle_create_entry(self, args: dict):
        """Handle create entry command."""
        required_fields = ["amount", "category", "description", "type"]
        for field in required_fields:
            if field not in args:
                return {"success": False, "error": f"Missing required field: {field}"}

        try:
            entry_id = self.ledger_manager.create_entry(
                amount=float(args["amount"]),
                category=args["category"],
                description=args["description"],
                entry_type=args["type"],
                date=args.get("date"),
                tags=args.get("tags", [])
            )
            return {"success": True, "entry_id": entry_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_get_entry(self, args: dict):
        """Handle get entry command."""
        if "entry_id" not in args:
            return {"success": False, "error": "Missing entry_id"}

        entry = self.ledger_manager.get_entry(args["entry_id"])
        if entry:
            return {"success": True, "data": entry.to_dict()}
        else:
            return {"success": False, "error": "Entry not found"}

    def handle_update_entry(self, args: dict):
        """Handle update entry command."""
        if "entry_id" not in args:
            return {"success": False, "error": "Missing entry_id"}

        try:
            success = self.ledger_manager.update_entry(
                entry_id=args["entry_id"],
                amount=args.get("amount"),
                category=args.get("category"),
                description=args.get("description"),
                entry_type=args.get("type"),
                date=args.get("date"),
                tags=args.get("tags")
            )
            return {"success": success, "updated": success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_delete_entry(self, args: dict):
        """Handle delete entry command."""
        if "entry_id" not in args:
            return {"success": False, "error": "Missing entry_id"}

        success = self.ledger_manager.delete_entry(args["entry_id"])
        return {"success": success, "deleted": success}

    def handle_get_entries(self, args: dict):
        """Handle get entries command."""
        try:
            entries = self.ledger_manager.get_entries(
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                entry_type=args.get("type"),
                category=args.get("category")
            )
            return {"success": True, "data": [entry.to_dict() for entry in entries]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_get_financial_summary(self, args: dict):
        """Handle get financial summary command."""
        try:
            summary = self.ledger_manager.get_financial_summary(
                start_date=args.get("start_date"),
                end_date=args.get("end_date")
            )
            return {"success": True, "data": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_generate_weekly_summary(self, args: dict):
        """Handle generate weekly summary command."""
        try:
            summary = self.ledger_manager.generate_weekly_summary(
                week_start=args.get("week_start")
            )
            return {"success": True, "data": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_backup_data(self, args: dict):
        """Handle backup data command."""
        try:
            success = self.ledger_manager.backup_data()
            return {"success": success, "backed_up": success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_restore_from_backup(self, args: dict):
        """Handle restore from backup command."""
        try:
            success = self.ledger_manager.restore_from_backup()
            return {"success": success, "restored": success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_error_response(self, error_msg: str):
        """Send an error response."""
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {"success": False, "error": error_msg}
        self.wfile.write(json.dumps(error_response, indent=2).encode('utf-8'))

def start_mcp_server(port: int = 3001, host: str = "localhost"):
    """Start the MCP server."""
    server = HTTPServer((host, port), LedgerMCPHandler)
    logger.info(f"Ledger MCP Server starting on {host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Ledger MCP Server...")
        server.shutdown()

def run_server_in_background(port: int = 3001, host: str = "localhost"):
    """Run the MCP server in a background thread."""
    server_thread = threading.Thread(
        target=start_mcp_server,
        args=(port, host),
        daemon=True
    )
    server_thread.start()
    return server_thread

# Example usage
if __name__ == "__main__":
    print("Ledger MCP Server can be started with the start_mcp_server() function")
    print("Example usage for testing:")
    print("from ledger_mcp_server import start_mcp_server")
    print("start_mcp_server(port=3001)")