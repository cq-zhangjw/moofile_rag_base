import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.document_loader import DocLoader, TextSpliter
from utils.moofile_util import MooFileUtil


def print_check(name, actual, expected):
    """Print a readable validation result and return whether it passed."""
    passed = actual == expected
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: actual={actual!r}, expected={expected!r}")
    return passed


def create_and_load_txt_documents(source_dir):
    """Generate TXT files, load them, and split them into document chunks."""
    loader = DocLoader()
    loaded_documents = loader.txt_loader(f"{PROJECT_ROOT}/data/ChinaGDC资料一览.txt")
    chunks = TextSpliter.text_split_by_char(
        loaded_documents,
        chunk_size=500,
        chunk_overlap=10,
    )
    return [
        {"page_content": document.page_content, "metadata": dict(document.metadata)}
        for document in chunks
    ]


def test_vector_table_crud():
    """Run TXT loading, vector CRUD, and semantic search operations."""
    print("\n=== Vector table CRUD test ===")
    checks = []
    model_path = PROJECT_ROOT / "models/sentence-transformers/granite-embedding-107m-multilingual"

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        source_dir = root / "txt_sources"
        source_dir.mkdir()

        util = MooFileUtil(
            str(root / "database"),
            is_vector=True,
            embedding_model=str(model_path),
        )
        table_name = "knowledge"
        indexes = ["document_id", "chunk_id"]
        util.create_database(table_name)

        documents = create_and_load_txt_documents(source_dir)
        print(f"TXT files generated: 12")
        print(f"Document chunks generated: {len(documents)}")

        util.insert_document_data(table_name, documents, indexes)
        stored_count = util.count_data(table_name, {}, indexes)
        checks.append(print_check("inserted chunk count", stored_count, len(documents)))
        checks.append(print_check("embedding dimensions", len(documents[0]["embedding"]), 384))

        results = util.vector_search(
            table_name,
            "Power Platform",
            indexes,
            top_k=5,
        )
        checks.append(print_check("vector search result count", len(results), 5))
        print("Top vector search results:")
        for position, (record, score) in enumerate(results, start=1):
            print(f"  {position}. score={score:.4f}, text={record['page_content'][:80]!r}")

        target = documents[0]
        replacement = "Python can automate tests and process large text collections."
        util.update_document_data(
            table_name,
            {"chunk_id": target["chunk_id"]},
            replacement,
            indexes,
        )
        updated = util.query_data(
            table_name,
            {"chunk_id": target["chunk_id"]},
            indexes,
        )[0]
        checks.append(print_check("updated text", updated["page_content"], replacement))
        checks.append(print_check("updated embedding dimensions", len(updated["embedding"]), 384))

        document_id = target["document_id"]
        chunks_to_delete = util.count_data(
            table_name,
            {"document_id": document_id},
            indexes,
        )
        print(f"Chunks associated with {document_id}: {chunks_to_delete}")
        util.delete_document_data(table_name, document_id, indexes)
        remaining_chunks = util.count_data(
            table_name,
            {"document_id": document_id},
            indexes,
        )
        metadata_count = util.count_data(
            "document_meta",
            {"id": document_id},
            ["id"],
        )
        checks.append(print_check("document chunks deleted", remaining_chunks, 0))
        checks.append(print_check("document metadata deleted", metadata_count, 0))

    passed = all(checks)
    print(f"\nVector table result: {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    if not test_vector_table_crud():
        raise SystemExit(1)
