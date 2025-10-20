# app/services/mcp_easyvista_tools.py
import os
from typing import Dict, List, Any
import httpx
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.rpc import RPCError, RPCException
from app.models.reporting import TicketFilterArgs
from app.core.config import settings

class CreateTicketArgs(BaseModel):
    title: str = Field(..., description="Ticket title")
    description: str = Field(..., description="Ticket description")
    category: str = Field(..., description="Ticket category")
    priority: str = Field(..., description="Ticket priority")
    support_team: str | None = Field(None, description="Support team")
    assigned_to: str | None = Field(None, description="Assigned to")

class UpdateTicketArgs(BaseModel):
    rfc_number: str = Field(..., description="RFC number of the ticket")
    params: Dict[str, Any] = Field(..., description="Fields to update")

class CloseTicketArgs(BaseModel):
    rfc_number: str = Field(..., description="RFC number of the ticket")
    comment: str = Field(..., description="Closing comment")

class ReportArgs(BaseModel):
    report_type: str = Field(..., description="One of: summary, csv, html")
    filters: Dict[str, Any] | None = Field(
        None, description="Optional filters for the report"
    )

def get_easyvista_config() -> Dict[str, str]:
    """
    Returns a dictionary of the required EasyVista connection settings.
    """
    return {
        "url": str(settings.EASYVISTA_URL).rstrip("/"),
        "key": settings.EASYVISTA_API_KEY,
        "account": settings.EASYVISTA_ACCOUNT_ID,
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _request(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Any:
    try:
        resp = await client.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise RPCException(
            error=RPCError(
                code=exc.response.status_code,
                message=f"EasyVista API error: {exc.response.text}",
            )
        ) from exc

async def create_ticket(client: httpx.AsyncClient, args: CreateTicketArgs) -> Dict[str, Any]:
    cfg = get_easyvista_config()
    payload = {
        "account_id": cfg["account"],
        "title": args.title,
        "description": args.description,
        "category": args.category,
        "priority": args.priority,
        "support_team": args.support_team,
        "assigned_to": args.assigned_to,
    }
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
    }
    return await _request(
        client, "POST", f"{cfg['url']}/api/v1/tickets", json=payload, headers=headers
    )

async def update_ticket(client: httpx.AsyncClient, args: UpdateTicketArgs) -> Dict[str, Any]:
    cfg = get_easyvista_config()
    payload = {"account_id": cfg["account"], **args.params}
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
    }
    return await _request(
        client, "PUT", f"{cfg['url']}/api/v1/tickets/{args.rfc_number}", json=payload, headers=headers
    )

async def close_ticket(client: httpx.AsyncClient, args: CloseTicketArgs) -> Dict[str, Any]:
    cfg = get_easyvista_config()
    payload = {
        "account_id": cfg["account"],
        "status": "closed",
        "comment": args.comment,
    }
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
    }
    return await _request(
        client, "PUT", f"{cfg['url']}/api/v1/tickets/{args.rfc_number}/close", json=payload, headers=headers
    )

async def get_ticket(client: httpx.AsyncClient, rfc_number: str) -> Dict[str, Any]:
    cfg = get_easyvista_config()
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Accept": "application/json",
    }
    return await _request(client, "GET", f"{cfg['url']}/api/v1/tickets/{rfc_number}", headers=headers)

async def get_ticket_history(client: httpx.AsyncClient, rfc_number: str) -> List[Dict[str, Any]]:
    cfg = get_easyvista_config()
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Accept": "application/json",
    }
    return await _request(client, "GET", f"{cfg['url']}/api/v1/tickets/{rfc_number}/history", headers=headers)

async def get_resolution_metrics(client: httpx.AsyncClient) -> Dict[str, float]:
    cfg = get_easyvista_config()
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Accept": "application/json",
    }
    return await _request(client, "GET", f"{cfg['url']}/api/v1/metrics/resolution", headers=headers)

async def list_tickets(client: httpx.AsyncClient, filter_args: TicketFilterArgs) -> List[Dict[str, Any]]:
    cfg = get_easyvista_config()
    params = {"account_id": cfg["account"], "limit": filter_args.limit, "offset": filter_args.offset}
    for key in ("group_id", "status", "priority", "assigned_to"):
        val = getattr(filter_args, key)
        if val:
            params[key] = val
    headers = {"Authorization": f"Bearer {cfg['key']}", "Accept": "application/json"}
    data = await _request(client, "GET", f"{cfg['url']}/api/v1/tickets", params=params, headers=headers)
    return data.get("tickets", [])

async def generate_report(client: httpx.AsyncClient, args: ReportArgs) -> str:
    filter_args = TicketFilterArgs(**(args.filters or {}))
    tickets = await list_tickets(client, filter_args)

    if args.report_type == "summary":
        lines = [f"Ticket {t['rfc_number']}: {t['title']} ({t['status']})" for t in tickets]
        return "\n".join(lines)

    if args.report_type == "csv":
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["rfc_number", "title", "status", "priority", "category", "assigned_to"])
        writer.writeheader()
        for t in tickets:
            writer.writerow({k: t.get(k, "") for k in writer.fieldnames})
        return output.getvalue()

    if args.report_type == "html":
        rows = "".join(f"<tr><td>{t.get('rfc_number', '')}</td><td>{t.get('title', '')}</td><td>{t.get('status', '')}</td></tr>" for t in tickets)
        return f"<html><body><table border='1'><tr><th>RFC</th><th>Title</th><th>Status</th></tr>{rows}</table></body></html>"

    raise ValueError(f"Unsupported report type: {args.report_type}")

async def dispatch(client: httpx.AsyncClient, method: str, args: Dict[str, Any]) -> Any:
    if method == "create_ticket":
        return await create_ticket(client, CreateTicketArgs(**args))
    if method == "update_ticket":
        return await update_ticket(client, UpdateTicketArgs(**args))
    if method == "close_ticket":
        return await close_ticket(client, CloseTicketArgs(**args))
    if method == "get_ticket":
        return await get_ticket(client, args["rfc_number"])
    if method == "get_ticket_history":
        return await get_ticket_history(client, args["rfc_number"])
    if method == "list_tickets":
        return await list_tickets(client, TicketFilterArgs(**args))
    if method == "get_tickets_by_group":
        return await list_tickets(client, TicketFilterArgs(group_id=args["group_id"]))
    if method == "get_tickets_by_status":
        return await list_tickets(client, TicketFilterArgs(status=args["status"]))
    if method == "get_tickets_by_priority":
        return await list_tickets(client, TicketFilterArgs(priority=args["priority"]))
    if method == "generate_report":
        return await generate_report(client, ReportArgs(**args))
    if method == "get_resolution_metrics":
        return await get_resolution_metrics(client)
    
    raise ValueError(f"Unknown method: {method}")
