"""Database CRUD + trash + meta.json management."""
import os
import re
import shutil
from datetime import datetime, timezone

from moofile import Collection

from .. import config, store
from ..exceptions import ConflictError, NotFoundError, BadRequestError


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_name(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_]{2,64}", name or ""):
        raise BadRequestError("名称需为 2-64 位英文字母、数字或下划线")


def _record_count(col: Collection) -> int:
    try:
        return col.count({"recordType": "record"})
    except Exception:
        return 0


def _default_vector_config() -> dict:
    from . import vector_service

    model = vector_service.resolve_model(None)
    return {
        "model": model["name"],
        "dimensions": model["dims"],
        "chunkSize": config.DEFAULT_CHUNK_SIZE,
        "chunkOverlap": config.DEFAULT_OVERLAP,
        "topK": config.DEFAULT_TOP_K,
        "similarityThreshold": config.DEFAULT_SIMILARITY_THRESHOLD,
    }


def get_vector_config(db_id: str) -> dict:
    meta = store.read_meta(db_id)
    if meta.get("type") != "vector":
        raise BadRequestError("只有向量数据库支持向量配置")
    return {**_default_vector_config(), **meta.get("vectorConfig", {})}


def update_vector_config(db_id: str, values: dict) -> dict:
    from . import vector_service

    current = get_vector_config(db_id)
    model = vector_service.resolve_model(values.get("model"))
    chunk_size = values.get("chunkSize")
    overlap = values.get("chunkOverlap")
    top_k = values.get("topK")
    threshold = values.get("similarityThreshold")
    if not isinstance(chunk_size, int) or not 100 <= chunk_size <= 2000:
        raise BadRequestError("chunkSize 必须在 100-2000 之间")
    if not isinstance(overlap, int) or not 0 <= overlap < chunk_size:
        raise BadRequestError("chunkOverlap 必须大于等于 0 且小于 chunkSize")
    if not isinstance(top_k, int) or not 1 <= top_k <= 50:
        raise BadRequestError("topK 必须在 1-50 之间")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise BadRequestError("similarityThreshold 必须在 0-1 之间")

    with store.open_collection(db_id, True) as col:
        tasks = col.find({"recordType": "task"}).to_list()
        if any(task.get("status") in ("pending", "running") for task in tasks):
            raise ConflictError("数据库存在进行中任务，暂时无法修改向量配置")
        if model["name"] != current["model"]:
            col.delete_many({"recordType": "record"})
            for document in col.find({"recordType": "doc"}).to_list():
                col.update_one({"_id": document["_id"]}, set={
                    "docStatus": "waiting",
                    "vectorStatus": "none",
                    "chunkCount": 0,
                    "model": model["name"],
                })

    vector_config = {
        "model": model["name"],
        "dimensions": model["dims"],
        "chunkSize": chunk_size,
        "chunkOverlap": overlap,
        "topK": top_k,
        "similarityThreshold": float(threshold),
    }
    meta = store.read_meta(db_id)
    meta["vectorConfig"] = vector_config
    meta["updatedAt"] = _now()
    store.write_meta(db_id, meta)
    return vector_config


def list_databases(trashed: bool = False) -> list[dict]:
    out = []
    for db_id in store.list_db_dirs():
        meta = store.read_meta(db_id)
        if bool(meta.get("trashed", False)) != trashed:
            continue
        out.append(_decorate(db_id, meta))
    return out


def _decorate(db_id: str, meta: dict) -> dict:
    is_vector = meta.get("type") == "vector"
    document_count = 0
    field_count = 0
    try:
        with store.open_collection(db_id, is_vector) as col:
            count = _record_count(col)
            if is_vector:
                document_count = col.count({"recordType": "doc"})
            else:
                fields = {
                    key
                    for record in col.find({"recordType": "record"}).to_list()
                    for key in record
                    if key not in {"_id", "recordType"} and not key.startswith("_")
                }
                field_count = len(fields)
    except Exception:
        count = 0
    result = {
        "id": db_id,
        "name": meta.get("name"),
        "type": meta.get("type", "normal"),
        "recordCount": count,
        "documentCount": document_count,
        "fieldCount": field_count,
        "sizeMB": store.file_size_mb(db_id),
        "createdAt": meta.get("createdAt"),
        "updatedAt": meta.get("updatedAt"),
        "trashed": bool(meta.get("trashed", False)),
    }
    if is_vector:
        result["vectorConfig"] = {**_default_vector_config(), **meta.get("vectorConfig", {})}
    return result


def get_database(db_id: str) -> dict:
    store.require_db(db_id)
    return _decorate(db_id, store.read_meta(db_id))


def create_database(name: str, db_type: str) -> dict:
    if db_type not in ("normal", "vector"):
        raise BadRequestError("type 必须是 normal 或 vector")
    _validate_name(name)

    db_id = store.new_db_id(name)
    if os.path.exists(store.db_dir(db_id)):
        raise ConflictError(f"数据库 ID 已存在: {db_id}")

    for existing_db_id in store.list_db_dirs():
        meta = store.read_meta(existing_db_id)
        if str(meta.get("name", "")).casefold() == name.casefold():
            raise ConflictError(f"同名数据库已存在: {name}")

    os.makedirs(store.db_dir(db_id), exist_ok=True)
    os.makedirs(store.upload_dir(db_id), exist_ok=True)

    is_vector = db_type == "vector"
    vector_indexes = {"embedding": config.EMBEDDING_DIMS} if is_vector else None
    with Collection(store.db_bson_path(db_id), indexes=["recordType", "documentId"],
                    vector_indexes=vector_indexes):
        pass

    now = _now()
    meta = {
        "id": db_id,
        "name": name,
        "type": db_type,
        "createdAt": now,
        "updatedAt": now,
        "trashed": False,
    }
    if is_vector:
        meta["vectorConfig"] = _default_vector_config()
    store.write_meta(db_id, meta)
    return get_database(db_id)


def rename_database(db_id: str, new_name: str) -> dict:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    _validate_name(new_name)
    if meta.get("name") == new_name:
        return get_database(db_id)

    new_db_id = store.new_db_id(new_name)
    if os.path.exists(store.db_dir(new_db_id)):
        raise ConflictError(f"数据库 ID 已存在: {new_db_id}")

    for other in store.list_db_dirs():
        if other == db_id:
            continue
        m = store.read_meta(other)
        if str(m.get("name", "")).casefold() == new_name.casefold():
            raise ConflictError(f"同名数据库已存在: {new_name}")

    is_vector = meta.get("type") == "vector"
    with store.open_collection(db_id, is_vector) as col:
        active_tasks = col.find({"recordType": "task"}).to_list()
    if any(task.get("status") in ("pending", "running") for task in active_tasks):
        raise ConflictError("数据库存在进行中任务，暂时无法重命名")

    legacy_upload_dir = os.path.join(config.LEGACY_UPLOAD_DIR, db_id)
    if os.path.isdir(legacy_upload_dir):
        os.makedirs(store.upload_dir(db_id), exist_ok=True)
        for filename in os.listdir(legacy_upload_dir):
            source = os.path.join(legacy_upload_dir, filename)
            target = os.path.join(store.upload_dir(db_id), filename)
            if not os.path.exists(target):
                shutil.move(source, target)
        shutil.rmtree(legacy_upload_dir)

    shutil.move(store.db_dir(db_id), store.db_dir(new_db_id))
    meta["name"] = new_name
    meta["id"] = new_db_id
    meta["updatedAt"] = _now()
    store.write_meta(new_db_id, meta)

    with store.open_collection(new_db_id, is_vector) as col:
        for row in col.find({"dbId": db_id}).to_list():
            col.update_one({"_id": row["_id"]}, set={"dbId": new_db_id})
    return get_database(new_db_id)


def soft_delete_database(db_id: str) -> None:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    meta["trashed"] = True
    meta["updatedAt"] = _now()
    store.write_meta(db_id, meta)


def restore_database(db_id: str) -> None:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    meta["trashed"] = False
    meta["updatedAt"] = _now()
    store.write_meta(db_id, meta)


def destroy_database(db_id: str) -> None:
    store.require_db(db_id)
    shutil.rmtree(store.db_dir(db_id), ignore_errors=True)
    up = os.path.join(config.LEGACY_UPLOAD_DIR, db_id)
    if os.path.isdir(up):
        shutil.rmtree(up, ignore_errors=True)


def empty_trash() -> int:
    ids = [db_id for db_id in store.list_db_dirs() if store.read_meta(db_id).get("trashed")]
    for db_id in ids:
        destroy_database(db_id)
    return len(ids)
