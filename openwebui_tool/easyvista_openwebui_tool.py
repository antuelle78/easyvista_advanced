# easyvista_openwebui_tool.py
import os
import httpx
from typing import Literal, Optional, Dict, Any

class Tools:
    """
    A class that provides tools for interacting with the EasyVista API.
    Open-WebUI will introspect this class to generate the tool schemas for the LLM.
    """
    def __init__(self):
        self.base_url = os.getenv("EASYVISTA_SERVICE_URL", "http://host.docker.internal:8004/api/v1/mcp")
        self.api_key = "a-very-secret-api-key"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0)

    def _make_rpc_call(self, method: str, params: dict) -> dict:
        """Helper function to make a JSON-RPC call to the EasyVista service."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "open-webui-tool-call"
        }
        try:
            response = self.client.post(self.base_url, json=payload)
            response.raise_for_status()
            rpc_response = response.json()
            
            if rpc_response.get("error"):
                return {"status": "error", "details": rpc_response["error"]}
            
            return rpc_response.get("result", {"status": "success", "details": "No result returned."})
        except httpx.HTTPStatusError as e:
            return {"status": "error", "details": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"status": "error", "details": f"Request Failed: {e}"}
        except Exception as e:
            return {"status": "error", "details": f"An unexpected error occurred: {str(e)}"}

    def create_ticket(self, title: str, description: str, category: str, priority: Literal["High", "Medium", "Low"]) -> dict:
        """
        Creates a new ticket in the EasyVista system.

        :param title: The title for the new ticket.
        :param description: A detailed description of the issue or request.
        :param category: The category of the ticket, for example, 'Incidents' or 'Requests'.
        :param priority: The priority of the ticket. Must be one of 'High', 'Medium', or 'Low'.
        :return: A dictionary containing the details of the newly created ticket.
        """
        params = {
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
        }
        return self._make_rpc_call("create_ticket", params)

    def get_ticket(self, rfc_number: str) -> dict:
        """
        Retrieves the details of a specific ticket using its RFC number.

        :param rfc_number: The unique RFC number of the ticket to retrieve (e.g., 'RFC123').
        :return: A dictionary containing the ticket's details.
        """
        return self._make_rpc_call("get_ticket", {"rfc_number": rfc_number})

    def list_tickets(self, status: Optional[Literal["Open", "In Progress", "Closed"]] = None, limit: int = 20) -> dict:
        """
        Lists tickets from EasyVista, with an option to filter by their status.

        :param status: Optional. The status to filter tickets by.
        :param limit: The maximum number of tickets to return. Defaults to 20.
        :return: A list of dictionaries, where each dictionary is a ticket.
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._make_rpc_call("list_tickets", params)

    def get_tickets_by_group(self, group_id: str) -> dict:
        """
        Retrieves a list of tickets assigned to a specific group.

        :param group_id: The ID of the group to filter tickets by.
        :return: A list of dictionaries, where each dictionary is a ticket.
        """
        return self._make_rpc_call("get_tickets_by_group", {"group_id": group_id})

    def get_tickets_by_status(self, status: Literal["Open", "In Progress", "Closed"]) -> dict:
        """
        Retrieves a list of tickets with a specific status.

        :param status: The status to filter tickets by.
        :return: A list of dictionaries, where each dictionary is a ticket.
        """
        return self._make_rpc_call("get_tickets_by_status", {"status": status})

    def get_tickets_by_priority(self, priority: Literal["High", "Medium", "Low"]) -> dict:
        """
        Retrieves a list of tickets with a specific priority.

        :param priority: The priority to filter tickets by.
        :return: A list of dictionaries, where each dictionary is a ticket.
        """
        return self._make_rpc_call("get_tickets_by_priority", {"priority": priority})

    def generate_report(
        self,
        report_type: Literal["summary", "csv", "html"],
        status: Optional[Literal["Open", "In Progress", "Closed"]] = None,
        priority: Optional[Literal["High", "Medium", "Low"]] = None,
        group_id: Optional[str] = None,
    ) -> dict:
        """
        Generates and returns a report of tickets in the specified format with optional filters.

        :param report_type: The desired format for the report.
        :param status: Optional. Filter the report to include tickets with this status.
        :param priority: Optional. Filter the report to include tickets with this priority.
        :param group_id: Optional. Filter the report to include tickets assigned to this group.
        :return: A string containing the generated report.
        """
        filters: Dict[str, Any] = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if group_id:
            filters["group_id"] = group_id
            
        params = {"report_type": report_type, "filters": filters}
        return self._make_rpc_call("generate_report", params)