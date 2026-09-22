"""Retrieval route."""
from fastapi import APIRouter

from .. import responses, store
from ..schemas import RetrievalReq
from ..services import vector_service, db_service

router = APIRouter(prefix="/api/databases/{db_id}/retrieval", tags=["retrieval"])


@router.post("")
def retrieval(db_id: str, req: RetrievalReq):
    store.require_db(db_id)
    vector_config = db_service.get_vector_config(db_id)
    top_k = req.topK if req.topK is not None else vector_config["topK"]
    threshold = req.threshold if req.threshold is not None else vector_config["similarityThreshold"]
    query_vec = vector_service.encode(
        req.query,
        vector_service.resolve_model_path(vector_config["model"]),
    )

    with store.open_collection(db_id, True) as col:
        hits = col.find({"recordType": "record"}).vector_search(
            "embedding", query_vec, limit=max(1, top_k),
        ).to_list()

    results = []
    for rank, (doc, score) in enumerate(hits, start=1):
        if score < threshold:
            continue
        results.append({
            "rank": rank,
            "score": round(float(score), 4),
            "source": doc.get("document", ""),
            "chunkIndex": doc.get("index", 0),
            "content": doc.get("content", ""),
            "documentId": doc.get("documentId", ""),
        })
    return responses.ok(results)
