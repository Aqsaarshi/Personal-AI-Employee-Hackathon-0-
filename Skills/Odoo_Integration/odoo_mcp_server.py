"""
Odoo MCP Server
Provides external access to Odoo operations via MCP protocol
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime
import logging

from Skills.Odoo_Integration.odoo_integration import OdooIntegration, OdooRPCException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OdooMCPHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.odoo_integration = OdooIntegration()
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests for Odoo operations."""
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
        except OdooRPCException as e:
            error_result = {"success": False, "error": str(e)}
            self.send_response(200)  # Still return 200 for application errors
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_result, indent=2).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            self.send_error_response(f"Error processing request: {str(e)}")

    def do_GET(self):
        """Handle GET requests for simple queries."""
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')

        try:
            if path_parts[0] == "odoo" and len(path_parts) > 1:
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
                if path_parts[1] == "test_connection":
                    result = self.process_command("test_connection", args)
                elif path_parts[1] == "get_financial_reports":
                    result = self.process_command("get_financial_reports", args)
                elif path_parts[1] == "get_company_info":
                    result = self.process_command("get_company_info", args)
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
        """Process Odoo commands."""
        logger.info(f"Processing Odoo command: {command} with args: {args}")

        try:
            if command == "create_account_move":
                return self.handle_create_account_move(args)
            elif command == "create_account_payment":
                return self.handle_create_account_payment(args)
            elif command == "search_read":
                return self.handle_search_read(args)
            elif command == "create":
                return self.handle_create(args)
            elif command == "write":
                return self.handle_write(args)
            elif command == "unlink":
                return self.handle_unlink(args)
            elif command == "get_financial_reports":
                return self.handle_get_financial_reports(args)
            elif command == "sync_with_local":
                return self.handle_sync_with_local(args)
            elif command == "test_connection":
                return self.handle_test_connection(args)
            elif command == "get_company_info":
                return self.handle_get_company_info(args)
            elif command == "get_partner_info":
                return self.handle_get_partner_info(args)
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
        except OdooRPCException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error processing command {command}: {str(e)}")
            return {"success": False, "error": str(e)}

    def handle_create_account_move(self, args: dict):
        """Handle create account move command."""
        try:
            move_id = self.odoo_integration.create_account_move(args)
            return {"success": True, "data": {"id": move_id}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_create_account_payment(self, args: dict):
        """Handle create account payment command."""
        try:
            payment_id = self.odoo_integration.create_account_payment(args)
            return {"success": True, "data": {"id": payment_id}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_search_read(self, args: dict):
        """Handle search_read command."""
        required_fields = ["model"]
        for field in required_fields:
            if field not in args:
                return {"success": False, "error": f"Missing required field: {field}"}

        try:
            model = args["model"]
            domain = args.get("domain", [])
            fields = args.get("fields", [])
            offset = args.get("offset", 0)
            limit = args.get("limit")
            order = args.get("order")

            results = self.odoo_integration.search_read(model, domain, fields, offset, limit, order)
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_create(self, args: dict):
        """Handle create command."""
        required_fields = ["model", "vals"]
        for field in required_fields:
            if field not in args:
                return {"success": False, "error": f"Missing required field: {field}"}

        try:
            model = args["model"]
            vals = args["vals"]

            record_id = self.odoo_integration.create(model, vals)
            return {"success": True, "data": {"id": record_id}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_write(self, args: dict):
        """Handle write command."""
        required_fields = ["model", "record_ids", "vals"]
        for field in required_fields:
            if field not in args:
                return {"success": False, "error": f"Missing required field: {field}"}

        try:
            model = args["model"]
            record_ids = args["record_ids"]
            vals = args["vals"]

            success = self.odoo_integration.write(model, record_ids, vals)
            return {"success": True, "data": {"success": success}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_unlink(self, args: dict):
        """Handle unlink command."""
        required_fields = ["model", "record_ids"]
        for field in required_fields:
            if field not in args:
                return {"success": False, "error": f"Missing required field: {field}"}

        try:
            model = args["model"]
            record_ids = args["record_ids"]

            success = self.odoo_integration.unlink(model, record_ids)
            return {"success": True, "data": {"success": success}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_get_financial_reports(self, args: dict):
        """Handle get financial reports command."""
        try:
            date_from = args.get("date_from")
            date_to = args.get("date_to")

            reports = self.odoo_integration.get_financial_reports(date_from, date_to)
            return {"success": True, "data": reports}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_sync_with_local(self, args: dict):
        """Handle sync with local ledger command."""
        required_fields = ["local_data"]
        for field in required_fields:
            if field not in args:
                return {"success": False, "error": f"Missing required field: {field}"}

        try:
            local_data = args["local_data"]
            sync_direction = args.get("sync_direction", "local_to_odoo")

            result = self.odoo_integration.sync_with_local_ledger(local_data, sync_direction)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_test_connection(self, args: dict):
        """Handle test connection command."""
        try:
            success = self.odoo_integration.test_connection()
            return {"success": success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_get_company_info(self, args: dict):
        """Handle get company info command."""
        try:
            company_info = self.odoo_integration.get_company_info()
            return {"success": True, "data": company_info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_get_partner_info(self, args: dict):
        """Handle get partner info command."""
        if "partner_id" not in args:
            return {"success": False, "error": "Missing partner_id"}

        try:
            partner_info = self.odoo_integration.get_partner_info(args["partner_id"])
            return {"success": True, "data": partner_info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_error_response(self, error_msg: str):
        """Send an error response."""
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {"success": False, "error": error_msg}
        self.wfile.write(json.dumps(error_response, indent=2).encode('utf-8'))

def start_odoo_mcp_server(port: int = 3002, host: str = "localhost"):
    """Start the Odoo MCP server."""
    server = HTTPServer((host, port), OdooMCPHandler)
    logger.info(f"Odoo MCP Server starting on {host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Odoo MCP Server...")
        server.shutdown()

def run_server_in_background(port: int = 3002, host: str = "localhost"):
    """Run the MCP server in a background thread."""
    server_thread = threading.Thread(
        target=start_odoo_mcp_server,
        args=(port, host),
        daemon=True
    )
    server_thread.start()
    return server_thread

# Example usage
if __name__ == "__main__":
    print("Odoo MCP Server can be started with the start_odoo_mcp_server() function")
    print("Example usage:")
    print("from odoo_mcp_server import start_odoo_mcp_server")
    print("start_odoo_mcp_server(port=3002)")