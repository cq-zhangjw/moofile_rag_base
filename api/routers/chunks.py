"""Chunk routes."""
from fastapi import APIRouter, Query

from .. import responses
from ..schemas import DeleteIdsReq
from ..services import chunk_service

router = APIRouter(prefix="/api/databases/{db_id}/chunks", tags=["chunks"])


@router.get("")
def list_chunks(
    db_id: str,
    page: int = 1,
    pageSize: int = 20,
    search: str = "",
    docId: str = Query(default=""),
):
    return responses.ok(chunk_service.list_chunks(db_id, page, pageSize, search, docId))


@router.post("/{chunk_id}/reembed")
def reembed(db_id: str, chunk_id: str):
    ok = chunk_service.reembed_chunk(db_id, chunk_id)
    return responses.ok({"reembedded": ok})


@router.post("/delete")
def delete_chunks(db_id: str, req: DeleteIdsReq):
    count = chunk_service.delete_chunks(db_id, req.ids)
    return responses.ok({"deleted": count})
