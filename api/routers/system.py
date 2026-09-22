"""System routes: health, storage, models."""
import os

from fastapi import APIRouter, Request

from .. import config, responses
from ..services import vector_service, db_service

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def health():
    return responses.ok({
        "status": "ok",
        "model": os.path.basename(config.MODEL_PATH),
        "dims": config.EMBEDDING_DIMS,
    })


@router.get("/storage")
def storage():
    used_bytes = 0
    if os.path.isdir(config.DB_DIR):
        for root, _, files in os.walk(config.DB_DIR):
            for f in files:
                try:
                    used_bytes += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    used_gb = round(used_bytes / (1024 ** 3), 3)
    quota = config.STORAGE_QUOTA_GB
    percent = round(min(100.0, used_gb / quota * 100), 1) if quota else 0.0
    return responses.ok({
        "usedGB": used_gb,
        "quotaGB": quota,
        "percent": percent,
        "databaseCount": len(db_service.list_databases()),
    })


@router.get("/models")
def models():
    return responses.ok(vector_service.available_models())


@router.get("/help")
def help_document(request: Request, locale: str | None = None):
    accepted = locale or request.headers.get("accept-language", "")
    preferred = accepted.lower().split(",", 1)[0].strip()
    if preferred.startswith("zh"):
        locale, filename = "zh", "README_ZH.md"
    elif preferred.startswith("ja"):
        locale, filename = "ja", "README_JP.md"
    else:
        locale, filename = "en", "README.md"

    with open(os.path.join(config.BASE_DIR, filename), "r", encoding="utf-8") as readme:
        return responses.ok({"locale": locale, "content": readme.read()})
