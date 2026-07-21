"""QuickBooks MCP server client."""

import json
import logging
import subprocess
import asyncio
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QuickBooksMCPClient:
    """Client for communicating with QB MCP server via stdio."""

    def __init__(self, mcp_server_cmd: str = None):
        """
        Initialize MCP client.

        Args:
            mcp_server_cmd: Command to start MCP server.
                          Default: "python -m quickbooks_mcp"
        """
        self.mcp_server_cmd = mcp_server_cmd or "python -m quickbooks_mcp"
        self.process = None
        self.request_id = 0

    async def connect(self):
        """Start the MCP server process."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.mcp_server_cmd.split(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            logger.info("QB MCP server started")
        except Exception as e:
            logger.error(f"Failed to start QB MCP server: {e}")
            raise

    async def disconnect(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
            logger.info("QB MCP server stopped")

    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server.

        Args:
            method: RPC method name
            params: Method parameters

        Returns:
            Response from server
        """
        if not self.process:
            await self.connect()

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }

        try:
            request_line = json.dumps(request) + "\n"
            self.process.stdin.write(request_line.encode())
            await self.process.stdin.drain()

            # Read response
            response_line = await self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("MCP server disconnected")

            response = json.loads(response_line.decode())

            if "error" in response:
                raise RuntimeError(f"MCP error: {response['error']}")

            return response.get("result", {})

        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            raise

    async def query_customers(self) -> List[Dict[str, Any]]:
        """Query all customers from QB via MCP."""
        logger.info("Querying QB customers via MCP...")
        result = await self._send_request("call_tool", {
            "name": "query",
            "arguments": {"query": "SELECT * FROM Customer"}
        })
        return result.get("rows", [])

    async def query_invoices(self) -> List[Dict[str, Any]]:
        """Query all invoices from QB via MCP."""
        logger.info("Querying QB invoices via MCP...")
        result = await self._send_request("call_tool", {
            "name": "query",
            "arguments": {"query": "SELECT * FROM Invoice"}
        })
        return result.get("rows", [])

    async def query_items(self) -> List[Dict[str, Any]]:
        """Query all items (products) from QB via MCP."""
        logger.info("Querying QB items via MCP...")
        result = await self._send_request("call_tool", {
            "name": "query",
            "arguments": {"query": "SELECT * FROM Item"}
        })
        return result.get("rows", [])

    async def query_payments(self) -> List[Dict[str, Any]]:
        """Query all payments from QB via MCP."""
        logger.info("Querying QB payments via MCP...")
        result = await self._send_request("call_tool", {
            "name": "query",
            "arguments": {"query": "SELECT * FROM Payment"}
        })
        return result.get("rows", [])
