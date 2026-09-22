"""Chunk (vector record) listing, re-embedding and deletion."""
from .. import store
from . import vector_service


def list_chunks(db_id: str, page: int = 1, page_size: int = 20,
                search: str = "", doc_id: str = "") -> dict:
    store.require_db(db_id)
    with store.open_collection(db_id, True) as col:
        query = {"recordType": "record"}
        if doc_id:
            query["documentId"] = doc_id
        rows = col.find(query).to_list()

    if search:
        kw = search.lower()
        rows = [r for r in rows if kw in str(r.get("content", "")).lower()]

    rows.sort(key=lambda r: (r.get("documentId", ""), r.get("index", 0)))
    total = len(rows)
    start = max(0, (page - 1) * page_size)
    page_rows = rows[start:start + page_size]

    out = []
    for r in page_rows:
        out.append({
            "id": r.get("_id"),
            "dbId": db_id,
            "documentId": r.get("documentId"),
            "document": r.get("document"),
            "index": r.get("index"),
            "content": r.get("content"),
            "tokens": r.get("tokens"),
            "embedStatus": r.get("embedStatus", "done"),
            "page": r.get("page", 1),
        })
    return {"list": out, "total": total, "page": page, "pageSize": page_size}


def reembed_chunk(db_id: str, chunk_id: str) -> bool:
    store.require_db(db_id)
    with store.open_collection(db_id, True) as col:
        chunk = col.find_one({"_id": chunk_id, "recordType": "record"})
        if not chunk:
            return False
        new_vec = vector_service.encode(chunk.get("content", ""))
        col.update_one({"_id": chunk_id}, set={
            "embedding": new_vec, "embedStatus": "done",
        })
    return True


def delete_chunks(db_id: str, ids: list[str]) -> int:
    store.require_db(db_id)
    with store.open_collection(db_id, True) as col:
        for cid in ids:
            col.delete_one({"_id": cid, "recordType": "record"})
    return len(ids)
