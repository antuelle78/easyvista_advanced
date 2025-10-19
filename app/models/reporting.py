from pydantic import BaseModel

class TicketFilterArgs(BaseModel):
    group_id: str | None = None
    status: str | None = None
    priority: str | None = None
    limit: int = 50
    offset: int = 0
