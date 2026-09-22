"""Trash routes."""
from fastapi import APIRouter

from .. import responses
from ..services import db_service

router = APIRouter(prefix="/api/trash", tags=["trash"])


@router.get("")
def list_trash():
    return responses.ok(db_service.list_databases(trashed=True))


@router.post("/{db_id}/restore")
def restore(db_id: str):
    db_service.restore_database(db_id)
    return responses.ok({"id": db_id, "trashed": False})


@router.delete("/{db_id}")
def destroy(db_id: str):
    db_service.destroy_database(db_id)
    return responses.ok({"id": db_id, "destroyed": True})


@router.delete("")
def empty_trash():
    count = db_service.empty_trash()
    return responses.ok({"cleared": count})
