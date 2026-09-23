"""Direct functional test for document upload/vectorize/delete tools.

Exercises upload_and_vectorize_document, list_documents and delete_document
against the live backend, then destroys the temporary knowledge base.
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import mcp_servers.knowledge_mcp_server as s

API_BASE = "http://127.0.0.1:8888"
DOC_PATH = r"E:\my_projects\moofile_base\tests\mcp_sample_doc.txt"
DB_NAME = f"mcp_doc_test_{int(time.time())}"


def main() -> None:
    created = s.create_knowledge_base(DB_NAME, "vector")
    db_id = created["id"]
    print("CREATE vector db:", db_id)
    try:
        result = s.upload_and_vectorize_document(DOC_PATH, db_id, wait=True, timeout=120)
        print("UPLOAD+VECTORIZE:", json.dumps(result, ensure_ascii=False)[:400])
        assert result["vectorizeStarted"] is True
        assert result["taskStatus"] == "completed", result.get("taskStatus")
        assert result["docStatus"] == "completed"
        assert result["chunkCount"] > 0, "expected at least one chunk"

        detail = s.get_knowledge_base(db_id)
        print("DB DETAIL: documentCount =", detail["documentCount"], "recordCount =", detail["recordCount"])
        assert detail["documentCount"] == 1
        assert detail["recordCount"] == result["chunkCount"]

        docs = s.list_documents(db_id)
        print("LIST DOCS:", [(d["id"], d["name"], d["chunkCount"]) for d in docs])
        assert len(docs) == 1
        doc_id = docs[0]["id"]

        deleted = s.delete_document(db_id, doc_id)
        print("DELETE DOC:", deleted)
        assert deleted.get("deleted") == 1

        assert s.list_documents(db_id) == []
        detail2 = s.get_knowledge_base(db_id)
        assert detail2["recordCount"] == 0 and detail2["documentCount"] == 0
        print("AFTER DELETE: recordCount =", detail2["recordCount"], "documentCount =", detail2["documentCount"])

        # unsupported extension is rejected early
        try:
            s.upload_and_vectorize_document(r"E:\my_projects\moofile_base\tests\mcp_sample_doc.pdf", db_id)
            raise AssertionError("expected RuntimeError for unsupported extension")
        except RuntimeError as exc:
            print("UNSUPPORTED EXT rejected:", str(exc)[:80])

        # missing local file is rejected early
        try:
            s.upload_and_vectorize_document(r"E:\no_such_file.txt", db_id)
            raise AssertionError("expected RuntimeError for missing file")
        except RuntimeError as exc:
            print("MISSING FILE rejected:", str(exc)[:80])

        print("DOC TESTS PASSED")
    finally:
        resp = requests.delete(f"{API_BASE}/api/trash/{db_id}", timeout=10)
        print("CLEANUP:", resp.json())


if __name__ == "__main__":
    main()
