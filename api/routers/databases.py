"""Database CRUD routes."""
from fastapi import APIRouter, Request

from .. import responses
from ..schemas import CreateDatabaseReq, RenameDatabaseReq, VectorConfigReq
from ..services import db_service

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("")
def list_databases():
    return responses.ok(db_service.list_databases(trashed=False))


@router.post("")
def create_database(req: CreateDatabaseReq):
    return responses.ok(db_service.create_database(req.name, req.type))


@router.get("/{db_id}")
def get_database(db_id: str):
    return responses.ok(db_service.get_database(db_id))


@router.get("/{db_id}/vector-config")
def get_vector_config(db_id: str):
    return responses.ok(db_service.get_vector_config(db_id))


@router.put("/{db_id}/vector-config")
def update_vector_config(db_id: str, req: VectorConfigReq):
    return responses.ok(db_service.update_vector_config(db_id, req.model_dump()))


@router.put("/{db_id}")
def rename_database(db_id: str, req: RenameDatabaseReq):
    return responses.ok(db_service.rename_database(db_id, req.name))


@router.delete("/{db_id}")
def delete_database(db_id: str):
    db_service.soft_delete_database(db_id)
    return responses.ok({"id": db_id, "trashed": True})
