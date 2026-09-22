"""Task registry + background worker thread.

Tasks are stored inside each database's db.bson as recordType=task. A single
daemon worker thread drains pending tasks and drives their state machine.
"""
import os
import threading
import traceback
from datetime import datetime, timezone

from moofile import Collection

from .. import config, store
from . import vector_service


_lock = threading.Lock()
_woken = threading.Condition(_lock)
_stop = threading.Event()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_vector(db_id: str) -> bool:
    return store.read_meta(db_id).get("type") == "vector"


def create_task(db_id: str, task_type: str, target: str, doc_ids: list[str],
                model_name: str | None = None) -> dict:
    task = {
        "_id": store.new_task_id(),
        "recordType": "task",
        "dbId": db_id,
        "type": task_type,
        "target": target,
        "status": "pending",
        "progress": 0.0,
        "startAt": None,
        "endAt": None,
        "docIds": doc_ids,
        "model": model_name or "",
        "logs": [],
    }
    with store.open_collection(db_id, True) as col:
        col.insert(task)
    wake()
    return task


def list_tasks(db_id: str | None = None, task_type: str = "", status: str = "") -> list[dict]:
    results: list[dict] = []
    targets = [db_id] if db_id else store.list_db_dirs()
    for did in targets:
        if not store.exists(did):
            continue
        is_vec = store.read_meta(did).get("type") == "vector"
        try:
            with store.open_collection(did, is_vec) as col:
                rows = col.find({"recordType": "task"}).to_list()
        except Exception:
            continue
        for t in rows:
            if task_type and t.get("type") != task_type:
                continue
            if status and t.get("status") != status:
                continue
            results.append(_normalize(t))
    results.sort(key=lambda x: x.get("startAt") or "", reverse=True)
    return results


def get_task(db_id: str, task_id: str) -> dict | None:
    is_vec = store.read_meta(db_id).get("type") == "vector"
    with store.open_collection(db_id, is_vec) as col:
        t = col.find_one({"_id": task_id})
    return _normalize(t) if t else None


def _normalize(t: dict) -> dict:
    out = dict(t)
    out["id"] = t.get("_id")
    out["logs"] = t.get("logs", [])
    return out


def _update(db_id: str, task_id: str, **fields) -> None:
    is_vec = store.read_meta(db_id).get("type") == "vector"
    with store.open_collection(db_id, is_vec) as col:
        col.update_one({"_id": task_id}, set=fields)


def append_log(db_id: str, task_id: str, message: str) -> None:
    t = get_task(db_id, task_id)
    if not t:
        return
    logs = list(t.get("logs", []))
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    _update(db_id, task_id, logs=logs)


def cancel_task(db_id: str, task_id: str) -> bool:
    t = get_task(db_id, task_id)
    if not t or t["status"] not in ("pending", "running"):
        return False
    _update(db_id, task_id, status="cancelled", endAt=_now())
    return True


def retry_task(db_id: str, task_id: str) -> dict | None:
    t = get_task(db_id, task_id)
    if not t:
        return None
    _update(db_id, task_id, status="pending", progress=0.0,
            startAt=None, endAt=None, logs=[])
    wake()
    return get_task(db_id, task_id)


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------
def wake():
    with _woken:
        _woken.notify()


def _load_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".markdown", ".csv", ".html", ".htm", ".json", ".log"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    # Best-effort binary text extraction (no heavy deps in this build)
    raise RuntimeError(f"暂不支持的文件类型 {ext}（请上传 txt/md/csv 文本文件）")


def _vectorize_document(db_id: str, task_id: str, doc: dict,
                        chunk_size: int, overlap: int,
                        model_name: str | None = None) -> None:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    file_path = store.resolve_upload_path(db_id, doc.get("localPath", ""))
    append_log(db_id, task_id, f"开始处理文档: {doc.get('name')}")
    text = _load_text(file_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
    )
    raw_chunks = splitter.split_text(text)
    append_log(db_id, task_id, f"切分为 {len(raw_chunks)} 个分片")

    is_vec = True
    with store.open_collection(db_id, is_vec) as col:
        # remove old chunks for this document
        col.delete_many({"recordType": "record", "documentId": doc["_id"]})

        total = len(raw_chunks)
        for idx, chunk_text in enumerate(raw_chunks, start=1):
            if get_task(db_id, task_id) and get_task(db_id, task_id).get("status") == "cancelled":
                raise RuntimeError("任务已取消")
            embedding = vector_service.encode(chunk_text, vector_service.resolve_model_path(model_name))
            col.insert({
                "recordType": "record",
                "documentId": doc["_id"],
                "document": doc.get("name"),
                "index": idx,
                "content": chunk_text,
                "tokens": len(chunk_text),
                "page": 1,
                "embedStatus": "done",
                "embedding": embedding,
            })
            _update(db_id, task_id, progress=round(idx / max(total, 1) * 100, 1))
            if idx % 5 == 0 or idx == total:
                append_log(db_id, task_id, f"向量化进度 {idx}/{total}")

    # update document record
    with store.open_collection(db_id, True) as col:
        col.update_one({"_id": doc["_id"]}, set={
            "docStatus": "completed",
            "vectorStatus": "done",
            "chunkCount": len(raw_chunks),
            "chunkSize": chunk_size,
            "overlap": overlap,
            "errorMsg": "",
        })
    append_log(db_id, task_id, f"文档 {doc.get('name')} 向量化完成")


def _run_task(task: dict):
    db_id = task["dbId"]
    task_id = task["_id"]
    _update(db_id, task_id, status="running", startAt=_now())
    try:
        if task["type"] == "vectorization":
            for doc_id in task.get("docIds", []):
                doc = None
                with store.open_collection(db_id, True) as col:
                    doc = col.find_one({"_id": doc_id, "recordType": "doc"})
                if not doc:
                    append_log(db_id, task_id, f"跳过不存在的文档 {doc_id}")
                    continue
                chunk_size = doc.get("chunkSize", config.DEFAULT_CHUNK_SIZE)
                overlap = doc.get("overlap", config.DEFAULT_OVERLAP)
                model_name = task.get("model") or doc.get("model")
                _vectorize_document(db_id, task_id, doc, chunk_size, overlap, model_name)
        else:
            append_log(db_id, task_id, f"任务类型 {task['type']} 已受理")
        _update(db_id, task_id, status="completed", progress=100.0, endAt=_now())
    except Exception as e:
        traceback.print_exc()
        append_log(db_id, task_id, f"任务失败: {e}")
        _update(db_id, task_id, status="failed", endAt=_now())


def _worker_loop():
    while not _stop.is_set():
        try:
            pending = [t for t in list_tasks() if t.get("status") == "pending"]
            if not pending:
                with _woken:
                    _woken.wait(timeout=2.0)
                continue
            for task in pending:
                if _stop.is_set():
                    break
                _run_task(task)
        except Exception:
            traceback.print_exc()


_worker_thread: threading.Thread | None = None


def start_worker():
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return
    _worker_thread = threading.Thread(target=_worker_loop, daemon=True, name="mootask-worker")
    _worker_thread.start()
