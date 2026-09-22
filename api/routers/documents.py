"""Document routes."""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse

from .. import config, responses
from ..exceptions import BadRequestError
from ..schemas import DeleteIdsReq, VectorizeReq
from ..services import document_service

router = APIRouter(prefix="/api/databases/{db_id}/documents", tags=["documents"])


@router.get("")
def list_documents(db_id: str, search: str = "", status: str = ""):
    return responses.ok(document_service.list_documents(db_id, search, status))


@router.post("/upload")
async def upload_document(
    db_id: str,
    file: UploadFile = File(...),
):
    size = 0
    chunks = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
        size += len(chunk)
        if size > config.MAX_UPLOAD_MB * 1024 * 1024:
            raise BadRequestError("文件超过 50MB 限制")
    data = b"".join(chunks)
    doc = document_service.upload_document(db_id, file.filename or "upload.txt", data)
    return responses.ok(doc)


@router.post("/delete")
def delete_documents(db_id: str, req: DeleteIdsReq):
    count = document_service.delete_documents(db_id, req.ids)
    return responses.ok({"deleted": count})


@router.get("/{doc_id}/download")
def download_document(db_id: str, doc_id: str):
    path, filename = document_service.get_document_file(db_id, doc_id)
    return FileResponse(path, filename=filename, media_type="application/octet-stream")


@router.post("/vectorize")
def start_vectorization(db_id: str, req: VectorizeReq):
    tasks = document_service.start_vectorization(
        db_id, req.docIds, req.chunkSize, req.overlap, req.model
    )
    return responses.ok(tasks)
