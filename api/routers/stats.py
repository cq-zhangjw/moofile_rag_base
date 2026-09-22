"""Stats route."""
from fastapi import APIRouter

from .. import responses
from ..services import stats_service

router = APIRouter(prefix="/api/databases/{db_id}/stats", tags=["stats"])


@router.get("")
def get_stats(db_id: str):
    return responses.ok(stats_service.get_stats(db_id))
