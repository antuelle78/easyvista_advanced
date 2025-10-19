# mock_api/main.py
import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Enhanced Sample Data ---
now = datetime.utcnow()
tickets = {
    "RFC123": {"rfc_number": "RFC123", "title": "Network printer is offline", "status": "Open", "priority": "High", "category": "Incidents", "group_id": "GRP-IT", "support_team": "T1-Support", "assigned_to": "Alice", "created_at": (now - timedelta(days=1)).isoformat(), "updated_at": (now - timedelta(hours=2)).isoformat()},
    "RFC456": {"rfc_number": "RFC456", "title": "Request for new software license", "status": "In Progress", "priority": "Medium", "category": "Requests", "group_id": "GRP-FIN", "support_team": "T2-Finance-Apps", "assigned_to": "Bob", "created_at": (now - timedelta(days=5)).isoformat(), "updated_at": (now - timedelta(days=1)).isoformat()},
    "RFC789": {"rfc_number": "RFC789", "title": "Email server is slow", "status": "Open", "priority": "High", "category": "Incidents", "group_id": "GRP-IT", "support_team": "T1-Support", "assigned_to": "Alice", "created_at": (now - timedelta(hours=6)).isoformat(), "updated_at": (now - timedelta(minutes=30)).isoformat()},
    "RFC102": {"rfc_number": "RFC102", "title": "Cannot access shared drive", "status": "Closed", "priority": "Low", "category": "Incidents", "group_id": "GRP-IT", "support_team": "T1-Support", "assigned_to": "Charlie", "created_at": (now - timedelta(days=10)).isoformat(), "updated_at": (now - timedelta(days=8)).isoformat(), "resolution_time_seconds": 172800},
    "RFC105": {"rfc_number": "RFC105", "title": "Quarterly financial report access", "status": "Closed", "priority": "Medium", "category": "Requests", "group_id": "GRP-FIN", "support_team": "T2-Finance-Apps", "assigned_to": "Bob", "created_at": (now - timedelta(days=20)).isoformat(), "updated_at": (now - timedelta(days=15)).isoformat(), "resolution_time_seconds": 432000},
}

# --- Status History Tracking ---
ticket_status_history = {
    "RFC123": [{"status": "Open", "changed_at": (now - timedelta(days=1)).isoformat()}],
    "RFC456": [
        {"status": "Open", "changed_at": (now - timedelta(days=5)).isoformat()},
        {"status": "In Progress", "changed_at": (now - timedelta(days=1)).isoformat()}
    ],
    "RFC789": [{"status": "Open", "changed_at": (now - timedelta(hours=6)).isoformat()}],
    "RFC102": [
        {"status": "Open", "changed_at": (now - timedelta(days=10)).isoformat()},
        {"status": "Closed", "changed_at": (now - timedelta(days=8)).isoformat()}
    ],
    "RFC105": [
        {"status": "Open", "changed_at": (now - timedelta(days=20)).isoformat()},
        {"status": "Closed", "changed_at": (now - timedelta(days=15)).isoformat()}
    ],
}

class Ticket(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    group_id: Optional[str] = "GRP-IT"
    support_team: Optional[str] = "T1-Support"
    assigned_to: Optional[str] = None

@app.post("/api/v1/tickets", status_code=201)
async def create_ticket(ticket: Ticket, request: Request):
    logger.info(f"Received request to create ticket: {await request.json()}")
    rfc_number = f"RFC{len(tickets) + 200}" # Increment to avoid collision
    creation_time = datetime.utcnow()
    new_ticket = {
        "rfc_number": rfc_number,
        "title": ticket.title,
        "status": "Open",
        "priority": ticket.priority,
        "category": ticket.category,
        "group_id": ticket.group_id,
        "support_team": ticket.support_team,
        "assigned_to": ticket.assigned_to,
        "created_at": creation_time.isoformat(),
        "updated_at": creation_time.isoformat(),
    }
    tickets[rfc_number] = new_ticket
    ticket_status_history[rfc_number] = [{"status": "Open", "changed_at": creation_time.isoformat()}]
    logger.info(f"Created new ticket: {new_ticket}")
    return new_ticket

@app.put("/api/v1/tickets/{rfc_number}")
async def update_ticket(rfc_number: str, params: Dict[str, Any], request: Request):
    logger.info(f"Received request to update ticket {rfc_number} with params: {await request.json()}")
    if rfc_number not in tickets:
        logger.warning(f"Ticket not found: {rfc_number}. Returning default ticket RFC123.")
        rfc_number = "RFC123" # Default to a known ticket
    
    original_status = tickets[rfc_number].get("status")
    tickets[rfc_number].update(params)
    now_iso = datetime.utcnow().isoformat()
    tickets[rfc_number]["updated_at"] = now_iso
    
    new_status = tickets[rfc_number].get("status")
    if new_status != original_status:
        ticket_status_history.setdefault(rfc_number, []).append({"status": new_status, "changed_at": now_iso})
        if new_status == "Closed":
            created_at = datetime.fromisoformat(tickets[rfc_number]["created_at"])
            resolution_time = datetime.utcnow() - created_at
            tickets[rfc_number]["resolution_time_seconds"] = resolution_time.total_seconds()

    logger.info(f"Updated ticket {rfc_number}: {tickets[rfc_number]}")
    return tickets[rfc_number]

@app.put("/api/v1/tickets/{rfc_number}/close")
async def close_ticket(rfc_number: str, comment: str, request: Request):
    logger.info(f"Received request to close ticket {rfc_number} with comment: {await request.json()}")
    if rfc_number not in tickets:
        logger.warning(f"Ticket not found: {rfc_number}. Returning default ticket RFC123.")
        rfc_number = "RFC123" # Default to a known ticket
    
    now_iso = datetime.utcnow().isoformat()
    tickets[rfc_number]["status"] = "Closed"
    tickets[rfc_number]["closing_comment"] = comment
    tickets[rfc_number]["updated_at"] = now_iso
    
    created_at = datetime.fromisoformat(tickets[rfc_number]["created_at"])
    resolution_time = datetime.utcnow() - created_at
    tickets[rfc_number]["resolution_time_seconds"] = resolution_time.total_seconds()
    
    ticket_status_history.setdefault(rfc_number, []).append({"status": "Closed", "changed_at": now_iso})
    logger.info(f"Closed ticket {rfc_number}: {tickets[rfc_number]}")
    return tickets[rfc_number]

@app.get("/api/v1/tickets/{rfc_number}/history")
async def get_ticket_history(rfc_number: str):
    logger.info(f"Request received for ticket history: {rfc_number}")
    if rfc_number not in ticket_status_history:
        logger.warning(f"History not found for ticket: {rfc_number}. Returning history for default ticket RFC123.")
        rfc_number = "RFC123" # Default to a known ticket
    return ticket_status_history[rfc_number]

@app.get("/api/v1/metrics/resolution")
async def get_resolution_metrics():
    logger.info("Request received for resolution metrics")
    team_metrics = {}
    for ticket in tickets.values():
        if ticket.get("status") == "Closed" and "resolution_time_seconds" in ticket:
            team = ticket.get("support_team", "Unassigned")
            if team not in team_metrics:
                team_metrics[team] = []
            team_metrics[team].append(ticket["resolution_time_seconds"])
    
    avg_resolution_times = {
        team: sum(times) / len(times) for team, times in team_metrics.items()
    }
    return avg_resolution_times

# --- Existing Endpoints (Updated) ---
@app.get("/api/v1/tickets")
async def list_tickets(status: str = None, priority: str = None, group_id: str = None, assigned_to: str = None, limit: int = 20, offset: int = 0):
    logger.info(f"Listing tickets with filters: status={status}, priority={priority}, group_id={group_id}, assigned_to={assigned_to}")
    filtered_tickets = list(tickets.values())
    if status:
        filtered_tickets = [t for t in filtered_tickets if t.get("status") == status]
    if priority:
        filtered_tickets = [t for t in filtered_tickets if t.get("priority") == priority]
    if group_id:
        filtered_tickets = [t for t in filtered_tickets if t.get("group_id") == group_id]
    if assigned_to:
        filtered_tickets = [t for t in filtered_tickets if t.get("assigned_to") == assigned_to]
    logger.info(f"Found {len(filtered_tickets)} tickets matching criteria.")
    return {"tickets": filtered_tickets[offset:offset+limit]}

@app.get("/api/v1/tickets/{rfc_number}")
async def get_ticket(rfc_number: str):
    logger.info(f"Request received for ticket: {rfc_number}")
    if rfc_number not in tickets:
        logger.warning(f"Ticket not found: {rfc_number}. Returning default ticket RFC123.")
        return tickets["RFC123"]
    logger.info(f"Returning ticket: {tickets[rfc_number]}")
    return tickets[rfc_number]
