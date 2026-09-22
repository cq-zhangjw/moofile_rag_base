"""Statistics aggregation for a database."""
from datetime import datetime, timedelta, timezone

from .. import store


def _count(col, query: dict) -> int:
    try:
        return col.count(query)
    except Exception:
        return len(col.find(query).to_list())


def get_stats(db_id: str) -> dict:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    is_vector = meta.get("type") == "vector"

    document_count = 0
    chunk_count = 0
    vector_count = 0
    failed_docs = 0
    failed_tasks = 0
    upload_dates: list[str] = []
    status_dist: dict[str, int] = {}

    if is_vector:
        with store.open_collection(db_id, True) as col:
            docs = col.find({"recordType": "doc"}).to_list()
            document_count = len(docs)
            for d in docs:
                st = d.get("docStatus", "unknown")
                status_dist[st] = status_dist.get(st, 0) + 1
                if st == "failed":
                    failed_docs += 1
                ut = d.get("uploadTime")
                if ut:
                    upload_dates.append(ut[:10])
            chunks = col.find({"recordType": "record"}).to_list()
            chunk_count = len(chunks)
            vector_count = sum(1 for c in chunks if c.get("embedding"))
            tasks = col.find({"recordType": "task"}).to_list()
            failed_tasks = sum(1 for t in tasks if t.get("status") == "failed")
    else:
        with store.open_collection(db_id, False) as col:
            chunk_count = _count(col, {"recordType": "record"})
            vector_count = 0

    # last 7 days trend
    today = datetime.now(timezone.utc).date()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    uploads = [0] * 7
    vectorized = [0] * 7
    for d in docs if is_vector else []:
        ut = (d.get("uploadTime") or "")[:10]
        if ut in dates:
            uploads[dates.index(ut)] += 1
        if d.get("docStatus") == "completed":
            # approximate vectorized day = upload day
            if ut in dates:
                vectorized[dates.index(ut)] += 1

    color_map = {
        "uploaded": "#6B7280", "parsed": "#2563EB", "vectorizing": "#7C3AED",
        "completed": "#16A34A", "failed": "#DC2626",
    }
    distribution = [
        {"name": k, "value": v, "color": color_map.get(k, "#9CA3AF")}
        for k, v in sorted(status_dist.items(), key=lambda x: -x[1])
    ]

    return {
        "cards": {
            "documentCount": document_count,
            "chunkCount": chunk_count,
            "vectorCount": vector_count,
            "storageMB": store.file_size_mb(db_id),
            "failedDocs": failed_docs,
            "failedTasks": failed_tasks,
        },
        "dates": dates,
        "uploads": uploads,
        "vectorized": vectorized,
        "distribution": distribution,
    }
