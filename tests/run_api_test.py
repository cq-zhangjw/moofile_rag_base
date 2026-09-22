"""Automated API test for MooFile backend.

Run with the server up:  python app.py  (in another terminal)
Then:  python tests/run_api_test.py
Exits non-zero if any critical assertion fails.
"""
import json
import sys
import time
import urllib.request
import urllib.parse

BASE = "http://127.0.0.1:8888"

results = []  # (name, ok, detail)


def call(method, path, body=None, raw=False):
    url = BASE + path
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
            if raw:
                return resp.status, payload
            return resp.status, json.loads(payload)
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8")
        try:
            return e.code, json.loads(payload)
        except Exception:
            return e.code, {"raw": payload}


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")


def main():
    # 1. health
    s, r = call("GET", "/api/system/health")
    check("health", s == 200 and r["code"] == 0 and r["data"]["dims"] == 384)

    # 2. storage
    s, r = call("GET", "/api/system/storage")
    check("storage", s == 200 and r["code"] == 0 and "usedGB" in r["data"])

    # 3. models
    s, r = call("GET", "/api/system/models")
    check("models", s == 200 and len(r["data"]) >= 1)

    # 4. list databases (empty or existing)
    s, r = call("GET", "/api/databases")
    check("list databases initial", s == 200 and r["code"] == 0 and isinstance(r["data"], list))

    # 5. create normal db
    s, r = call("POST", "/api/databases", {"name": "test_user_db", "type": "normal"})
    check("create normal db", s == 200 and r["code"] == 0 and r["data"]["type"] == "normal",
          r.get("message", ""))
    normal_id = r["data"]["id"]

    # 6. create vector db
    s, r = call("POST", "/api/databases", {"name": "test_kb_db", "type": "vector"})
    check("create vector db", r["code"] == 0 and r["data"]["type"] == "vector")
    vec_id = r["data"]["id"]

    # 7. duplicate name -> conflict
    s, r = call("POST", "/api/databases", {"name": "test_user_db", "type": "normal"})
    check("duplicate name conflict", r["code"] == 40901, f"code={r.get('code')}")

    # 8. get db
    s, r = call("GET", f"/api/databases/{normal_id}")
    check("get db", r["code"] == 0 and r["data"]["name"] == "test_user_db")

    # 9. rename db
    s, r = call("PUT", f"/api/databases/{normal_id}", {"name": "test_user_db2"})
    check("rename db", r["code"] == 0 and r["data"]["name"] == "test_user_db2")

    # 10. insert records
    for i in range(25):
        call("POST", f"/api/databases/{normal_id}/records",
             {"name": f"user{i}", "age": 20 + i, "role": "admin" if i % 5 == 0 else "user"})
    s, r = call("GET", f"/api/databases/{normal_id}/records?page=1&pageSize=10")
    check("list records paged", r["code"] == 0 and r["data"]["total"] == 25 and len(r["data"]["list"]) == 10)

    # 11. filter operator eq
    flt = urllib.parse.quote(json.dumps({"logic": "AND", "conditions": [{"field": "role", "operator": "eq", "value": "admin"}]}))
    s, r = call("GET", f"/api/databases/{normal_id}/records?filter={flt}")
    check("filter eq role=admin", r["code"] == 0 and r["data"]["total"] == 5, f"total={r['data']['total']}")

    # 12. filter gt
    flt = urllib.parse.quote(json.dumps({"logic": "AND", "conditions": [{"field": "age", "operator": "gt", "value": 40}]}))
    s, r = call("GET", f"/api/databases/{normal_id}/records?filter={flt}")
    check("filter gt age>40", r["code"] == 0 and r["data"]["total"] == 4, f"total={r['data']['total']}")

    # 13. search
    s, r = call("GET", f"/api/databases/{normal_id}/records?search=user2")
    check("search user2", r["code"] == 0 and r["data"]["total"] >= 1)

    # 14. fields
    s, r = call("GET", f"/api/databases/{normal_id}/records/fields")
    check("fields", r["code"] == 0 and set(["name", "age", "role"]).issubset(set(r["data"])))

    # 15. update record
    rid = r  # placeholder
    s, r = call("GET", f"/api/databases/{normal_id}/records?page=1&pageSize=1")
    rid = r["data"]["list"][0]["_id"]
    s, r = call("PUT", f"/api/databases/{normal_id}/records/{rid}",
                {"name": "renamed", "age": 99, "role": "user"})
    check("update record", r["code"] == 0)

    # 16. batch delete records
    s, r = call("POST", f"/api/databases/{normal_id}/records/delete", {"ids": [rid]})
    check("delete record", r["code"] == 0 and r["data"]["deleted"] == 1)

    # 17. upload a document (text) to vector db
    sample_text = ("Python 是一种解释型编程语言。\n" * 30) + ("向量数据库通过嵌入相似度做语义检索。\n" * 30)
    import io
    boundary = "----mootfiletest"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"note.txt\"\r\n"
        f"Content-Type: text/plain\r\n\r\n{sample_text}\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"chunkSize\"\r\n\r\n80\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overlap\"\r\n\r\n10\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    req = urllib.request.Request(
        BASE + f"/api/databases/{vec_id}/documents/upload",
        data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    check("upload document", r["code"] == 0 and r["data"]["docStatus"] == "uploaded", r.get("message", ""))
    doc_id = r["data"]["id"]

    # 18. list documents
    s, r = call("GET", f"/api/databases/{vec_id}/documents")
    check("list documents", r["code"] == 0 and len(r["data"]) >= 1)

    # 19. start vectorization
    s, r = call("POST", f"/api/databases/{vec_id}/documents/vectorize",
                {"docIds": [doc_id], "chunkSize": 80, "overlap": 10, "metadata": ["source"]})
    check("start vectorization", r["code"] == 0 and len(r["data"]) >= 1)
    task_id = r["data"][0]["id"]

    # 20. poll task until completed (max ~60s)
    done = False
    for _ in range(40):
        s, r = call("GET", f"/api/tasks?dbId={vec_id}&type=vectorization")
        if r["data"] and r["data"][0]["status"] in ("completed", "failed"):
            done = r["data"][0]["status"] == "completed"
            break
        time.sleep(1.5)
    check("vectorization completes", done, f"status={r['data'][0]['status'] if r['data'] else 'none'}")

    # 21. chunks now exist
    s, r = call("GET", f"/api/databases/{vec_id}/chunks?page=1&pageSize=50")
    check("chunks after vectorize", r["code"] == 0 and r["data"]["total"] >= 1, f"total={r['data']['total']}")

    # 22. retrieval
    s, r = call("POST", f"/api/databases/{vec_id}/retrieval",
                {"query": "什么是向量检索", "topK": 3, "threshold": 0.0, "hybrid": False})
    check("retrieval", r["code"] == 0 and len(r["data"]) >= 1, f"hits={len(r['data'])}")
    if r["data"]:
        check("retrieval shape", all("rank" in x and "score" in x and "content" in x for x in r["data"]))

    # 23. reembed a chunk
    s, r = call("GET", f"/api/databases/{vec_id}/chunks?page=1&pageSize=1")
    cid = r["data"]["list"][0]["id"]
    s, r = call("POST", f"/api/databases/{vec_id}/chunks/{cid}/reembed")
    check("reembed chunk", r["code"] == 0 and r["data"]["reembedded"])

    # 24. task logs
    s, r = call("GET", f"/api/tasks/{task_id}/logs?dbId={vec_id}")
    check("task logs", r["code"] == 0 and isinstance(r["data"], list) and len(r["data"]) >= 1)

    # 25. stats
    s, r = call("GET", f"/api/databases/{vec_id}/stats")
    check("stats", r["code"] == 0 and "cards" in r["data"] and r["data"]["cards"]["chunkCount"] >= 1)

    # 26. trash flow: soft delete normal db, list trash, restore, soft again, destroy
    s, r = call("DELETE", f"/api/databases/{normal_id}")
    check("soft delete db", r["code"] == 0)
    s, r = call("GET", "/api/trash")
    check("list trash", r["code"] == 0 and any(d["id"] == normal_id for d in r["data"]))
    s, r = call("POST", f"/api/trash/{normal_id}/restore")
    check("restore trash", r["code"] == 0)
    s, r = call("DELETE", f"/api/databases/{normal_id}")
    s, r = call("DELETE", f"/api/trash/{normal_id}")
    check("destroy db", r["code"] == 0)

    # 27. delete vector db (soft + destroy)
    s, r = call("DELETE", f"/api/databases/{vec_id}")
    s, r = call("DELETE", f"/api/trash/{vec_id}")
    check("destroy vector db", r["code"] == 0)

    # summary
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n==== {passed}/{total} passed ====")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
