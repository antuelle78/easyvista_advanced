# app/api/router.py
import logging
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
import httpx

from app.models.rpc import RPCRequest, RPCResponse, RPCError, RPCException
from app.services.mcp_easyvista_tools import dispatch
from app.api.dependencies import get_http_client, get_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/mcp", response_model=RPCResponse)
async def mcp_handler(
    request: Request,
    body: RPCRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    api_key: str = Depends(get_api_key),
):
    """
    Generic JSON-RPC dispatcher for EasyVista operations.
    """
    logger.info(f"RPC call {body.method} (id={body.id}) from {request.client.host}")
    try:
        if body.method == "tools/list":
            result = {
                "methods": [
                    {"name": "create_ticket", "params": "CreateTicketArgs", "result": "Ticket"},
                    {"name": "update_ticket", "params": "UpdateTicketArgs", "result": "Ticket"},
                    {"name": "close_ticket", "params": "CloseTicketArgs", "result": "Ticket"},
                    {"name": "get_ticket", "params": "rfc_number: str", "result": "Ticket"},
                    {"name": "list_tickets", "params": "TicketFilterArgs", "result": "List[Ticket]"},
                    {"name": "get_tickets_by_group", "params": "group_id: str", "result": "List[Ticket]"},
                    {"name": "get_tickets_by_status", "params": "status: str", "result": "List[Ticket]"},
                    {"name": "get_tickets_by_priority", "params": "priority: str", "result": "List[Ticket]"},
                    {"name": "generate_report", "params": "ReportArgs", "result": "str"},
                ]
            }
        else:
            result = await dispatch(client, body.method, body.params or {})
        return RPCResponse(result=result, id=body.id)
    except RPCException as exc:
        logger.warning(f"RPCException processing method {body.method}: {exc.error.message}")
        return RPCResponse(error=exc.error, id=body.id)
    except ValidationError as exc:
        logger.warning(f"Invalid parameters for method {body.method}: {exc}")
        error = RPCError(code=-32602, message=f"Invalid params: {exc}")
        return RPCResponse(error=error, id=body.id)
    except ValueError as exc:
        logger.warning(f"Method not found for method {body.method}: {exc}")
        error = RPCError(code=-32601, message=f"Method not found: {exc}")
        return RPCResponse(error=error, id=body.id)
    except httpx.RequestError as exc:
        logger.error(f"Network error while processing method {body.method}: {exc}")
        error = RPCError(code=-32000, message=f"Network error: {exc}")
        return RPCResponse(error=error, id=body.id)
    except Exception as exc:
        logger.exception(f"An unexpected error occurred while processing method {body.method}")
        error = RPCError(code=-32603, message=f"Internal server error: {exc}")
        return RPCResponse(error=error, id=body.id)

@router.get("/health")
async def health():
    return {"status": "ok"}
