"""Unified response envelope."""
from typing import Any

# Error codes
OK = 0
ERR_BAD_REQUEST = 40001
ERR_NOT_FOUND = 40401        # database not found
ERR_RESOURCE_NOT_FOUND = 40402  # record / document / task not found
ERR_CONFLICT = 40901         # name conflict
ERR_INTERNAL = 50000


def ok(data: Any = None, message: str = "ok") -> dict:
    return {"code": OK, "data": data, "message": message}


def error(code: int, message: str, data: Any = None) -> dict:
    return {"code": code, "data": data, "message": message}
