"""MooFile FastAPI entrypoint.

Run:  python app.py
Then: http://127.0.0.1:8888  (docs at /docs)

By default the script also launches the MCP server
(mcp_servers/knowledge_mcp_server.py) in the background. Pass
`--with_mcp false` (or set MOOFILE_WITH_MCP=false) to disable it.
"""
import argparse
import os
import socket
import subprocess
import sys
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


def _str_to_bool(value: str | bool) -> bool:
    """Parse a boolean CLI/env value (true/false/1/0/yes/no/on/off/y/n)."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "on", "y")


def _port_in_use(host: str, port: int) -> bool:
    """Return True if something is already listening on host:port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False


def _start_mcp_server() -> subprocess.Popen | None:
    """Launch the MCP server script in the background if it is not running.

    Returns the child process handle when this call started it, otherwise None
    (either the script is missing, or an MCP server is already listening).
    """
    mcp_script = os.path.join(config.BASE_DIR, "mcp_servers", "knowledge_mcp_server.py")
    if not os.path.isfile(mcp_script):
        print(f"[moofile] MCP server script not found, skipped: {mcp_script}")
        return None

    mcp_port = int(os.environ.get("MOOFILE_MCP_PORT", "8010"))
    if _port_in_use(config.HOST, mcp_port):
        print(f"[moofile] MCP server already running at "
              f"http://{config.HOST}:{mcp_port}/mcp, not starting another")
        return None

    log_dir = os.path.join(config.BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mcp_server.log")
    with open(log_file, "ab") as log_stream:
        proc = subprocess.Popen(
            [sys.executable, mcp_script],
            cwd=config.BASE_DIR,
            stdout=log_stream,
            stderr=log_stream,
        )
    print(f"[moofile] MCP server started (pid={proc.pid}) -> "
          f"http://{config.HOST}:{mcp_port}/mcp")
    print(f"[moofile] MCP server log: {log_file}")
    return proc


def _stop_mcp_server(proc: subprocess.Popen | None) -> None:
    """Terminate the MCP server child process we started, if it is still alive."""
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    print("[moofile] MCP server stopped")


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
    parser = argparse.ArgumentParser(
        description="MooFile FastAPI backend, optionally with the MCP server.",
    )
    parser.add_argument(
        "--with-mcp", "--with_mcp",
        dest="with_mcp",
        type=_str_to_bool,
        default=_str_to_bool(os.environ.get("MOOFILE_WITH_MCP", "true")),
        help="Launch the MCP server in the background (default: true).",
    )
    args = parser.parse_args()

    mcp_proc = _start_mcp_server() if args.with_mcp else None
    try:
        uvicorn.run(
            "app:app",
            host=config.HOST,
            port=config.PORT,
            reload=False,
        )
    finally:
        _stop_mcp_server(mcp_proc)
