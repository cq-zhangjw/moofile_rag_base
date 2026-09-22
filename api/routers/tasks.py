"""Task routes."""
from fastapi import APIRouter, Query

from .. import responses
from ..services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks(
    dbId: str = Query(default=""),
    type: str = Query(default=""),
    status: str = Query(default=""),
):
    db_id = dbId or None
    return responses.ok(task_service.list_tasks(db_id, type, status))


@router.post("/{task_id}/cancel")
def cancel(task_id: str, dbId: str = Query(...)):
    return responses.ok({"cancelled": task_service.cancel_task(dbId, task_id)})


@router.post("/{task_id}/retry")
def retry(task_id: str, dbId: str = Query(...)):
    t = task_service.retry_task(dbId, task_id)
    return responses.ok(t)


@router.get("/{task_id}/logs")
def logs(task_id: str, dbId: str = Query(...)):
    t = task_service.get_task(dbId, task_id)
    return responses.ok((t or {}).get("logs", []))
