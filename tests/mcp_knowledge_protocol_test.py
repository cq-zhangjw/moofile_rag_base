"""Protocol-level smoke test for knowledge_mcp_server via streamable-http.

Covers the full document workflow over the wire: create vector knowledge base,
upload + vectorize a local document, resolve db_id by name, list documents,
semantic retrieval, delete document, and lookup error handling. The temporary
knowledge base is destroyed at the end.
"""
import asyncio
import json
import time
from pathlib import Path

import requests
from fastmcp import Client
from fastmcp.client import StreamableHttpTransport

API_BASE = "http://127.0.0.1:8888"
MCP_URL = "http://127.0.0.1:8010/mcp"
DOC_PATH = str(Path(__file__).resolve().parent / "mcp_sample_doc.txt")
TEST_NAME = f"mcp_proto_test_{int(time.time())}"


def result_text(res) -> str:
    """Return the tool result text; FastMCP yields empty content for []."""
    return res.content[0].text if res.content else "[]"


async def main() -> str:
    transport = StreamableHttpTransport(MCP_URL)
    async with Client(transport) as client:
        tools = await client.list_tools()
        print("TOOLS over streamable-http:", [t.name for t in tools])

        res = await client.call_tool(
            "create_knowledge_base",
            {"name": TEST_NAME, "db_type": "vector"},
        )
        created = json.loads(res.content[0].text)
        db_id = created["id"]
        print("CREATE via protocol:", db_id)

        res2 = await client.call_tool("get_db_id_by_name", {"db_name": TEST_NAME})
        print("DB_ID_BY_NAME via protocol:", res2.content[0].text)
        assert res2.content[0].text.strip('"') == db_id

        res3 = await client.call_tool(
            "upload_and_vectorize_document",
            {"local_path": DOC_PATH, "db_id": db_id, "wait": True, "timeout": 180},
        )
        result = json.loads(res3.content[0].text)
        print("UPLOAD+VECTORIZE via protocol: taskStatus =", result["taskStatus"],
              "docStatus =", result.get("docStatus"), "chunkCount =", result.get("chunkCount"))
        assert result["taskStatus"] == "completed"
        assert result["chunkCount"] > 0
        doc_id = result["document"]["id"]

        res4 = await client.call_tool("list_documents", {"db_id": db_id})
        docs = json.loads(res4.content[0].text)
        print("LIST_DOCS via protocol:", [(d["id"], d["name"]) for d in docs])
        assert any(d["id"] == doc_id for d in docs)

        res5 = await client.call_tool(
            "retrieve_knowledge",
            {"db_id": db_id, "query": "向量化知识库 分片切分 嵌入模型", "top_k": 3, "threshold": 0.1},
        )
        hits = json.loads(res5.content[0].text)
        print("RETRIEVE via protocol: hits =", len(hits),
              "top score =", hits[0]["score"] if hits else None,
              "source =", hits[0]["source"] if hits else None)
        assert len(hits) > 0
        assert hits[0]["documentId"] == doc_id

        res6 = await client.call_tool("delete_document", {"db_id": db_id, "doc_id": doc_id})
        print("DELETE_DOC via protocol:", res6.content[0].text)

        res7 = await client.call_tool("list_documents", {"db_id": db_id})
        print("LIST after delete via protocol:", result_text(res7))
        assert json.loads(result_text(res7)) == []

        res8 = await client.call_tool(
            "retrieve_knowledge",
            {"db_id": db_id, "query": "任意查询", "top_k": 3, "threshold": 0.1},
        )
        print("RETRIEVE on empty db via protocol:", result_text(res8))
        assert json.loads(result_text(res8)) == []

        print("PROTOCOL TEST PASSED")
        return db_id


if __name__ == "__main__":
    created_db_id = asyncio.run(main())
    resp = requests.delete(f"{API_BASE}/api/trash/{created_db_id}", timeout=10)
    resp.raise_for_status()
    print("CLEANUP destroyed trashed db:", resp.json())
