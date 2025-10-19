# openwebui_tool/easyvista_openwebui_tool.py
import os
import httpx
from typing import Literal, Optional, Dict, Any

class Tools:
    """
    A class that provides tools for interacting with the EasyVista API.
    Open-WebUI will introspect this class to generate the tool schemas for the LLM.
    """
    def __init__(self):
        # The base URL for the service, which then calls the mock API
        self.base_url = os.getenv("EASYVISTA_SERVICE_URL", "http://host.docker.internal:8004/api/v1")
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
            # Note: The RPC call is always to the /mcp endpoint
            response = self.client.post(f"{self.base_url}/mcp", json=payload)
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

    def create_ticket(self, title: str, description: str, category: str, priority: Literal["High", "Medium", "Low"], support_team: Optional[str] = "T1-Support", assigned_to: Optional[str] = None) -> dict:
        """
        Creates a new ticket in the EasyVista system.

        :param title: The title for the new ticket.
        :param description: A detailed description of the issue or request.
        :param category: The category of the ticket (e.g., 'Incidents', 'Requests').
        :param priority: The priority of the ticket.
        :param support_team: Optional. The support team to assign the ticket to. Defaults to 'T1-Support'.
        :param assigned_to: Optional. The specific person to assign the ticket to.
        :return: A dictionary containing the details of the newly created ticket.
        """
        params = {
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "support_team": support_team,
            "assigned_to": assigned_to,
        }
        return self._make_rpc_call("create_ticket", params)

    def assign_ticket(self, rfc_number: str, assigned_to: str) -> dict:
        """
        Assigns or reassigns a ticket to a specific support person.

        :param rfc_number: The RFC number of the ticket to update.
        :param assigned_to: The name or ID of the person to assign the ticket to.
        :return: The updated ticket details.
        """
        params = {
            "rfc_number": rfc_number,
            "params": {"assigned_to": assigned_to}
        }
        return self._make_rpc_call("update_ticket", params)

    def get_ticket(self, rfc_number: str) -> dict:
        """
        Retrieves the details of a specific ticket using its RFC number.
        """
        return self._make_rpc_call("get_ticket", {"rfc_number": rfc_number})

    def list_tickets(self, status: Optional[Literal["Open", "In Progress", "Closed", "Pending"]] = None, assigned_to: Optional[str] = None, limit: int = 20) -> dict:
        """
        Lists tickets from EasyVista, with options for filtering.

        :param status: Optional. The status to filter tickets by.
        :param assigned_to: Optional. Filter tickets by the assigned person.
        :param limit: The maximum number of tickets to return. Defaults to 20.
        :return: A list of dictionaries, where each dictionary is a ticket.
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        if assigned_to:
            params["assigned_to"] = assigned_to
        return self._make_rpc_call("list_tickets", params)

    def get_ticket_history(self, rfc_number: str) -> dict:
        """
        Retrieves the status change history for a specific ticket.
        """
        try:
            response = self.client.get(f"{self.base_url}/tickets/{rfc_number}/history")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "details": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"status": "error", "details": f"Request Failed: {e}"}

    def get_resolution_metrics(self) -> dict:
        """
        Retrieves average ticket resolution times, aggregated by support team.
        """
        try:
            response = self.client.get(f"{self.base_url}/metrics/resolution")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "details": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"status": "error", "details": f"Request Failed: {e}"}

    def get_tickets_by_group(self, group_id: str) -> dict:
        """
        Retrieves a list of tickets assigned to a specific group.
        """
        return self._make_rpc_call("get_tickets_by_group", {"group_id": group_id})

    def get_tickets_by_status(self, status: Literal["Open", "In Progress", "Closed", "Pending"]) -> dict:
        """
        Retrieves a list of tickets with a specific status.
        """
        return self._make_rpc_call("get_tickets_by_status", {"status": status})

    def get_tickets_by_priority(self, priority: Literal["High", "Medium", "Low", "Critical"]) -> dict:
        """
        Retrieves a list of tickets with a specific priority.
        """
        return self._make_rpc_call("get_tickets_by_priority", {"priority": priority})

    def generate_report(
        self,
        report_type: Literal["summary", "csv", "html"],
        status: Optional[Literal["Open", "In Progress", "Closed", "Pending"]] = None,
        priority: Optional[Literal["High", "Medium", "Low", "Critical"]] = None,
        group_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> dict:
        """
        Generates and returns a report of tickets in the specified format with optional filters.
        """
        filters: Dict[str, Any] = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if group_id:
            filters["group_id"] = group_id
        if assigned_to:
            filters["assigned_to"] = assigned_to
            
        params = {"report_type": report_type, "filters": filters}
        return self._make_rpc_call("generate_report", params)