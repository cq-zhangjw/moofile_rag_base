"""Document upload, listing, deletion and vectorization triggers."""
import os
from datetime import datetime, timezone

from .. import config, store
from ..exceptions import BadRequestError, NotFoundError
from . import task_service


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ext_of(filename: str) -> str:
    return os.path.splitext(filename)[1].lstrip(".").upper() or "TXT"


def upload_document(db_id: str, filename: str, file_bytes: bytes) -> dict:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    if meta.get("type") != "vector":
        raise BadRequestError("只有向量知识库支持文档上传")

    ext = os.path.splitext(filename)[1].lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise BadRequestError(f"不支持的文件类型: {ext}")

    up_dir = store.upload_dir(db_id)
    os.makedirs(up_dir, exist_ok=True)
    safe_name = os.path.basename(filename)
    dest = os.path.join(up_dir, safe_name)
    with open(dest, "wb") as f:
        f.write(file_bytes)

    doc = {
        "_id": store.new_doc_id(),
        "recordType": "doc",
        "dbId": db_id,
        "name": safe_name,
        "type": _ext_of(safe_name),
        "size": len(file_bytes),
        "uploadTime": _now(),
        "docStatus": "uploaded",
        "chunkCount": 0,
        "vectorStatus": "none",
        "errorMsg": "",
        "localPath": os.path.join("_upload", safe_name),
    }
    with store.open_collection(db_id, True) as col:
        col.insert(doc)
    return _normalize(doc)


def list_documents(db_id: str, search: str = "", status: str = "") -> list[dict]:
    store.require_db(db_id)
    out: list[dict] = []
    with store.open_collection(db_id, True) as col:
        rows = col.find({"recordType": "doc"}).to_list()
    for d in rows:
        if status and d.get("docStatus") != status:
            continue
        if search and search.lower() not in str(d.get("name", "")).lower():
            continue
        out.append(_normalize(d))
    out.sort(key=lambda x: x.get("uploadTime", ""), reverse=True)
    return out


def get_document(db_id: str, doc_id: str) -> dict | None:
    with store.open_collection(db_id, True) as col:
        d = col.find_one({"_id": doc_id, "recordType": "doc"})
    return _normalize(d) if d else None


def get_document_file(db_id: str, doc_id: str) -> tuple[str, str]:
    store.require_db(db_id)
    with store.open_collection(db_id, True) as col:
        doc = col.find_one({"_id": doc_id, "recordType": "doc"})
    if not doc:
        raise NotFoundError(f"文档不存在: {doc_id}")
    path = store.resolve_upload_path(db_id, doc.get("localPath", ""))
    if not path or not os.path.isfile(path):
        raise NotFoundError("原始文档文件不存在")
    return path, doc.get("name") or os.path.basename(path)


def delete_documents(db_id: str, doc_ids: list[str]) -> int:
    store.require_db(db_id)
    with store.open_collection(db_id, True) as col:
        for doc_id in doc_ids:
            col.delete_many({"recordType": "record", "documentId": doc_id})
            col.delete_one({"_id": doc_id, "recordType": "doc"})
    return len(doc_ids)


def start_vectorization(db_id: str, doc_ids: list[str],
                        chunk_size: int, overlap: int,
                        model: str | None = None) -> list[dict]:
    store.require_db(db_id)
    if not doc_ids:
        raise BadRequestError("未选择文档")
    created = []
    for doc_id in doc_ids:
        doc = get_document(db_id, doc_id)
        if not doc:
            raise NotFoundError(f"文档不存在: {doc_id}")
        # persist requested chunk params onto the doc record
        with store.open_collection(db_id, True) as col:
            col.update_one({"_id": doc_id}, set={
                "docStatus": "vectorizing",
                "vectorStatus": "doing",
                "chunkSize": chunk_size,
                "overlap": overlap,
                "model": model or "",
            })
        task = task_service.create_task(
            db_id, "vectorization", f"向量化 {doc['name']}", [doc_id],
            model_name=model,
        )
        created.append(task_service.get_task(db_id, task["_id"]))
    return created


def _normalize(d: dict) -> dict:
    out = {k: v for k, v in d.items() if k != "localPath"}
    out["id"] = d.get("_id")
    return out
