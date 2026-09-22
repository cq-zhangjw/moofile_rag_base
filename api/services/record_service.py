"""Record CRUD with pagination, search and 12-operator filtering."""
import re
from typing import Any

from .. import store
from ..exceptions import BadRequestError, NotFoundError


# operators that moofile can push down directly
_PUSH = {
    "eq": "$eq", "ne": "$ne", "gt": "$gt", "gte": "$gte",
    "lt": "$lt", "lte": "$lte",
}


def _to_moofile_value(op: str, value: Any) -> Any:
    if op in ("gt", "gte", "lt", "lte"):
        try:
            return float(value) if "." in str(value) else int(value)
        except (TypeError, ValueError):
            return value
    return value


def build_filter(flt: dict | None) -> tuple[dict, list[dict]]:
    """Return (moofile_query, post_filter_conditions).

    moofile_query: pushed-down Mongo-like filter.
    post_filter_conditions: list of (field, operator, value) evaluated in Python.
    """
    if not flt or not flt.get("conditions"):
        return {}, []

    logic = (flt.get("logic") or "AND").upper()
    push_terms: list[dict] = []
    post_terms: list[dict] = []

    for c in flt["conditions"]:
        field = c.get("field")
        op = c.get("operator")
        value = c.get("value")
        if not field or not op:
            continue
        if op in _PUSH:
            push_terms.append({field: {_PUSH[op]: _to_moofile_value(op, value)}})
        elif op == "exists":
            push_terms.append({field: {"$exists": True}})
        elif op == "not_exists":
            push_terms.append({field: {"$exists": False}})
        else:
            post_terms.append({"field": field, "operator": op, "value": value})

    query: dict = {}
    if push_terms:
        if logic == "OR":
            query = {"$or": push_terms}
        else:
            query = {"$and": push_terms} if len(push_terms) > 1 else push_terms[0]
    return query, post_terms


def _pass_post(doc: dict, conditions: list[dict], logic: str) -> bool:
    if not conditions:
        return True

    def _one(cond: dict) -> bool:
        field, op, value = cond["field"], cond["operator"], cond.get("value")
        actual = doc.get(field)
        if op == "contains":
            return actual is not None and str(value).lower() in str(actual).lower()
        if op == "not_contains":
            return actual is None or str(value).lower() not in str(actual).lower()
        if op == "regex":
            try:
                return actual is not None and re.search(str(value), str(actual)) is not None
            except re.error:
                return False
        if op == "array_contains":
            return isinstance(actual, list) and value in actual
        if op == "eq":
            return actual == value
        if op == "ne":
            return actual != value
        return True

    if logic == "OR":
        return any(_one(c) for c in conditions)
    return all(_one(c) for c in conditions)


def list_records(db_id: str, page: int = 1, page_size: int = 20,
                 search: str = "", flt: dict | None = None) -> dict:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    is_vector = meta.get("type") == "vector"

    query, post = build_filter(flt)
    # only list data rows (not doc/task records)
    base = {"recordType": "record"}
    if query:
        combined = {"$and": [base, query]}
    else:
        combined = base

    logic = (flt or {}).get("logic", "AND")

    with store.open_collection(db_id, is_vector) as col:
        try:
            all_docs = col.find(combined).to_list()
        except Exception:
            # fallback: without pushed filter
            all_docs = [d for d in col.find(base).to_list()
                        if _pass_post(d, post, logic)]
        else:
            all_docs = [d for d in all_docs if _pass_post(d, post, logic)]

        if search:
            kw = search.lower()
            all_docs = [
                d for d in all_docs
                if any(kw in str(v).lower() for k, v in d.items()
                       if k not in ("embedding", "recordType"))
            ]

        total = len(all_docs)
        start = max(0, (page - 1) * page_size)
        rows = all_docs[start:start + page_size]
        rows = [store.strip_vector_field(d) for d in rows]

    return {"list": rows, "total": total, "page": page, "pageSize": page_size}


def list_fields(db_id: str) -> list[str]:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    is_vector = meta.get("type") == "vector"
    skip = {"_id", "recordType", "embedding", "documentId", "embedStatus"}
    fields: list[str] = []
    seen = set()
    with store.open_collection(db_id, is_vector) as col:
        for d in col.find({"recordType": "record"}).to_list():
            for k in d.keys():
                if k in skip or k.startswith("_") or k in seen:
                    continue
                seen.add(k)
                fields.append(k)
    return fields


def create_record(db_id: str, data: dict) -> dict:
    store.require_db(db_id)
    if not isinstance(data, dict):
        raise BadRequestError("记录必须是 JSON 对象")
    meta = store.read_meta(db_id)
    data = dict(data)
    data["recordType"] = "record"
    with store.open_collection(db_id, meta.get("type") == "vector") as col:
        inserted = col.insert(data)
    return inserted


def update_record(db_id: str, rid: str, data: dict) -> dict:
    store.require_db(db_id)
    if not isinstance(data, dict):
        raise BadRequestError("记录必须是 JSON 对象")
    meta = store.read_meta(db_id)
    with store.open_collection(db_id, meta.get("type") == "vector") as col:
        existing = col.find_one({"_id": rid})
        if not existing:
            raise NotFoundError(f"记录不存在: {rid}")
        new_doc = {k: v for k, v in data.items() if k != "_id"}
        new_doc["_id"] = rid
        new_doc["recordType"] = existing.get("recordType", "record")
        col.replace_one({"_id": rid}, new_doc)
    return col_find_one(db_id, rid)


def col_find_one(db_id: str, rid: str) -> dict:
    meta = store.read_meta(db_id)
    with store.open_collection(db_id, meta.get("type") == "vector") as col:
        d = col.find_one({"_id": rid})
    return store.strip_vector_field(d) if d else {}


def delete_records(db_id: str, ids: list[str]) -> int:
    store.require_db(db_id)
    meta = store.read_meta(db_id)
    with store.open_collection(db_id, meta.get("type") == "vector") as col:
        for rid in ids:
            col.delete_one({"_id": rid})
    return len(ids)
