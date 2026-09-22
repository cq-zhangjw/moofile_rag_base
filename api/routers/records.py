"""Record routes."""
import json
from fastapi import APIRouter, Request, Query

from .. import responses
from ..schemas import DeleteIdsReq
from ..services import record_service

router = APIRouter(prefix="/api/databases/{db_id}/records", tags=["records"])


@router.get("")
def list_records(
    db_id: str,
    page: int = 1,
    pageSize: int = 20,
    search: str = "",
    filter: str = Query(default=""),
):
    flt = None
    if filter:
        try:
            flt = json.loads(filter)
        except json.JSONDecodeError:
            flt = None
    data = record_service.list_records(db_id, page, pageSize, search, flt)
    return responses.ok(data)


@router.get("/fields")
def list_fields(db_id: str):
    return responses.ok(record_service.list_fields(db_id))


@router.post("")
async def create_record(db_id: str, request: Request):
    body = await request.json()
    return responses.ok(record_service.create_record(db_id, body))


@router.put("/{rid}")
async def update_record(db_id: str, rid: str, request: Request):
    body = await request.json()
    return responses.ok(record_service.update_record(db_id, rid, body))


@router.post("/delete")
def delete_records(db_id: str, req: DeleteIdsReq):
    count = record_service.delete_records(db_id, req.ids)
    return responses.ok({"deleted": count})
