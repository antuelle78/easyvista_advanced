# mock_api/main.py
import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- More extensive sample data ---
now = datetime.utcnow()
tickets = {
    "RFC123": {"rfc_number": "RFC123", "title": "Network printer is offline", "status": "Open", "priority": "High", "category": "Incidents", "group_id": "GRP-IT", "created_at": (now - timedelta(days=1)).isoformat(), "updated_at": (now - timedelta(hours=2)).isoformat()},
    "RFC456": {"rfc_number": "RFC456", "title": "Request for new software license", "status": "In Progress", "priority": "Medium", "category": "Requests", "group_id": "GRP-FIN", "created_at": (now - timedelta(days=5)).isoformat(), "updated_at": (now - timedelta(days=1)).isoformat()},
    "RFC789": {"rfc_number": "RFC789", "title": "Email server is slow", "status": "Open", "priority": "High", "category": "Incidents", "group_id": "GRP-IT", "created_at": (now - timedelta(hours=6)).isoformat(), "updated_at": (now - timedelta(minutes=30)).isoformat()},
    "RFC101": {"rfc_number": "RFC101", "title": "Onboarding for new employee", "status": "Pending", "priority": "Medium", "category": "Requests", "group_id": "GRP-HR", "created_at": (now - timedelta(days=2)).isoformat(), "updated_at": (now - timedelta(days=2)).isoformat()},
    "RFC102": {"rfc_number": "RFC102", "title": "Cannot access shared drive", "status": "Closed", "priority": "Low", "category": "Incidents", "group_id": "GRP-IT", "created_at": (now - timedelta(days=10)).isoformat(), "updated_at": (now - timedelta(days=8)).isoformat()},
    "RFC103": {"rfc_number": "RFC103", "title": "Update company website homepage", "status": "In Progress", "priority": "Low", "category": "Changes", "group_id": "GRP-WEB", "created_at": (now - timedelta(days=3)).isoformat(), "updated_at": (now - timedelta(hours=5)).isoformat()},
    "RFC104": {"rfc_number": "RFC104", "title": "System crash reported on server DB-01", "status": "Open", "priority": "Critical", "category": "Problems", "group_id": "GRP-OPS", "created_at": (now - timedelta(minutes=15)).isoformat(), "updated_at": (now - timedelta(minutes=15)).isoformat()},
    "RFC105": {"rfc_number": "RFC105", "title": "Quarterly financial report access", "status": "Closed", "priority": "Medium", "category": "Requests", "group_id": "GRP-FIN", "created_at": (now - timedelta(days=20)).isoformat(), "updated_at": (now - timedelta(days=15)).isoformat()},
    "RFC106": {"rfc_number": "RFC106", "title": "VPN connection issues for remote user", "status": "In Progress", "priority": "High", "category": "Incidents", "group_id": "GRP-IT", "created_at": (now - timedelta(hours=3)).isoformat(), "updated_at": (now - timedelta(hours=1)).isoformat()},
    "RFC107": {"rfc_number": "RFC107", "title": "New desk phone installation", "status": "Open", "priority": "Low", "category": "Requests", "group_id": "GRP-OPS", "created_at": (now - timedelta(days=4)).isoformat(), "updated_at": (now - timedelta(days=4)).isoformat()},
    "RFC108": {"rfc_number": "RFC108", "title": "Performance review system access", "status": "Open", "priority": "Medium", "category": "Requests", "group_id": "GRP-HR", "created_at": (now - timedelta(days=1)).isoformat(), "updated_at": (now - timedelta(hours=8)).isoformat()},
    "RFC109": {"rfc_number": "RFC109", "title": "Firewall rule change request", "status": "Pending", "priority": "High", "category": "Changes", "group_id": "GRP-IT", "created_at": (now - timedelta(days=6)).isoformat(), "updated_at": (now - timedelta(days=6)).isoformat()},
    "RFC110": {"rfc_number": "RFC110", "title": "Unusual login activity detected", "status": "Open", "priority": "Critical", "category": "Problems", "group_id": "GRP-SECURITY", "created_at": (now - timedelta(hours=1)).isoformat(), "updated_at": (now - timedelta(hours=1)).isoformat()},
    "RFC111": {"rfc_number": "RFC111", "title": "Update benefits documentation", "status": "Closed", "priority": "Low", "category": "Changes", "group_id": "GRP-HR", "created_at": (now - timedelta(days=30)).isoformat(), "updated_at": (now - timedelta(days=25)).isoformat()},
    "RFC112": {"rfc_number": "RFC112", "title": "Deploy new version of CRM to production", "status": "In Progress", "priority": "High", "category": "Changes", "group_id": "GRP-WEB", "created_at": (now - timedelta(days=2)).isoformat(), "updated_at": (now - timedelta(hours=1)).isoformat()},
}

class Ticket(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    group_id: Optional[str] = "GRP-IT"

@app.post("/api/v1/tickets", status_code=201)
async def create_ticket(ticket: Ticket, request: Request):
    logger.info(f"Received request to create ticket: {await request.json()}")
    rfc_number = f"RFC{len(tickets) + 100}"
    new_ticket = {
        "rfc_number": rfc_number,
        "title": ticket.title,
        "status": "Open",
        "priority": ticket.priority,
        "category": ticket.category,
        "group_id": ticket.group_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    tickets[rfc_number] = new_ticket
    logger.info(f"Created new ticket: {new_ticket}")
    return new_ticket

@app.get("/api/v1/tickets")
async def list_tickets(status: str = None, priority: str = None, group_id: str = None, limit: int = 20, offset: int = 0):
    logger.info(f"Listing tickets with filters: status={status}, priority={priority}, group_id={group_id}")
    filtered_tickets = list(tickets.values())
    if status:
        filtered_tickets = [t for t in filtered_tickets if t.get("status") == status]
    if priority:
        filtered_tickets = [t for t in filtered_tickets if t.get("priority") == priority]
    if group_id:
        filtered_tickets = [t for t in filtered_tickets if t.get("group_id") == group_id]
    logger.info(f"Found {len(filtered_tickets)} tickets matching criteria.")
    return {"tickets": filtered_tickets[offset:offset+limit]}

@app.get("/api/v1/tickets/{rfc_number}")
async def get_ticket(rfc_number: str):
    logger.info(f"Request received for ticket: {rfc_number}")
    if rfc_number not in tickets:
        logger.warning(f"Ticket not found: {rfc_number}")
        raise HTTPException(status_code=404, detail="Ticket not found")
    logger.info(f"Returning ticket: {tickets[rfc_number]}")
    return tickets[rfc_number]

@app.put("/api/v1/tickets/{rfc_number}")
async def update_ticket(rfc_number: str, params: Dict[str, Any], request: Request):
    logger.info(f"Received request to update ticket {rfc_number} with params: {await request.json()}")
    if rfc_number not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    tickets[rfc_number].update(params)
    tickets[rfc_number]["updated_at"] = datetime.utcnow().isoformat()
    logger.info(f"Updated ticket {rfc_number}: {tickets[rfc_number]}")
    return tickets[rfc_number]

@app.put("/api/v1/tickets/{rfc_number}/close")
async def close_ticket(rfc_number: str, comment: str, request: Request):
    logger.info(f"Received request to close ticket {rfc_number} with comment: {await request.json()}")
    if rfc_number not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    tickets[rfc_number]["status"] = "Closed"
    tickets[rfc_number]["closing_comment"] = comment
    tickets[rfc_number]["updated_at"] = datetime.utcnow().isoformat()
    logger.info(f"Closed ticket {rfc_number}: {tickets[rfc_number]}")
    return tickets[rfc_number]
