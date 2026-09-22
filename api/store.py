"""Low-level storage layer: meta.json read/write and moofile Collection access."""
import json
import os
import uuid
from typing import Optional

from moofile import Collection

from . import config
from .exceptions import NotFoundError


def new_db_id(name: str) -> str:
    return f"db_{name}_{uuid.uuid4().hex[:8]}"


def new_doc_id() -> str:
    return f"id_doc_{uuid.uuid4().hex[:8]}"


def new_task_id() -> str:
    return f"id_task_{uuid.uuid4().hex[:8]}"


def db_dir(db_id: str) -> str:
    return os.path.join(config.DB_DIR, db_id)


def db_bson_path(db_id: str) -> str:
    return os.path.join(db_dir(db_id), "db.bson")


def meta_path(db_id: str) -> str:
    return os.path.join(db_dir(db_id), "meta.json")


def upload_dir(db_id: str) -> str:
    return os.path.join(db_dir(db_id), "_upload")


def resolve_upload_path(db_id: str, stored_path: str) -> str:
    if not stored_path:
        return ""
    if not os.path.isabs(stored_path):
        return os.path.join(db_dir(db_id), stored_path)
    if os.path.isfile(stored_path):
        return stored_path
    return os.path.join(upload_dir(db_id), os.path.basename(stored_path))


def exists(db_id: str) -> bool:
    return os.path.isdir(db_dir(db_id)) and os.path.exists(db_bson_path(db_id))


def require_db(db_id: str) -> None:
    if not exists(db_id):
        raise NotFoundError(f"数据库不存在: {db_id}")


def read_meta(db_id: str) -> dict:
    require_db(db_id)
    with open(meta_path(db_id), "r", encoding="utf-8") as f:
        return json.load(f)


def write_meta(db_id: str, meta: dict) -> dict:
    os.makedirs(db_dir(db_id), exist_ok=True)
    with open(meta_path(db_id), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta


def list_db_dirs() -> list[str]:
    if not os.path.isdir(config.DB_DIR):
        return []
    return sorted(
        name for name in os.listdir(config.DB_DIR)
        if name.startswith("db_")
        and os.path.isdir(os.path.join(config.DB_DIR, name))
        and os.path.exists(os.path.join(config.DB_DIR, name, "db.bson"))
    )


def open_collection(db_id: str, is_vector: bool) -> Collection:
    """Open a moofile Collection with sensible indexes."""
    require_db(db_id)
    dimensions = config.EMBEDDING_DIMS
    if is_vector:
        dimensions = read_meta(db_id).get("vectorConfig", {}).get("dimensions", dimensions)
    vector_indexes = {"embedding": dimensions} if is_vector else None
    return Collection(
        db_bson_path(db_id),
        indexes=["recordType", "documentId", "chunkId"],
        vector_indexes=vector_indexes,
    )


def file_size_mb(db_id: str) -> float:
    p = db_bson_path(db_id)
    if not os.path.exists(p):
        return 0.0
    return round(os.path.getsize(p) / (1024 * 1024), 2)


def strip_vector_field(doc: dict) -> dict:
    """Remove the heavy embedding array before returning a chunk to the frontend."""
    if "embedding" in doc:
        doc = {k: v for k, v in doc.items() if k != "embedding"}
    return doc
