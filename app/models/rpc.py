from pydantic import BaseModel
from typing import Any, Dict, Optional, Union

class RPCRequest(BaseModel):
    method: str
    id: Union[str, int]
    params: Optional[Dict[str, Any]] = None

class RPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class RPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[RPCError] = None
    id: Union[str, int]

class RPCException(Exception):
    def __init__(self, error: RPCError):
        self.error = error
        super().__init__(error.message)
