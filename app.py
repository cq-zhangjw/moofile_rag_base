"""MooFile FastAPI entrypoint.

Run:  python app.py
Then: http://127.0.0.1:8888  (docs at /docs)
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import config
from api.exceptions import BizError, biz_exception_handler, unhandled_exception_handler
from api.services import vector_service, task_service
from api.routers import (
    databases, trash, records, documents, chunks,
    tasks, retrieval, stats, system,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload the embedding model once at startup.
    # print("[mootfile] loading embedding model ...")
    # vector_service.load_model()
    # print("[mootfile] embedding model ready.")
    task_service.start_worker()
    print("[mootfile] task worker started.")
    yield


app = FastAPI(title="MooFile API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(BizError, biz_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

for r in (
    databases.router, trash.router, records.router, documents.router,
    chunks.router, tasks.router, retrieval.router, stats.router, system.router,
):
    app.include_router(r)


@app.get("/")
def root():
    return {"code": 0, "data": {"name": "MooFile API", "version": "3.0.0"}, "message": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )
