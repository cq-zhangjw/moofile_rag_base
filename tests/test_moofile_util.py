import tempfile
import unittest
from pathlib import Path

from utils.document_loader import DocLoader, TextSpliter
from utils.moofile_util import MooFileUtil


class TestMooFileUtilTableCrud(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.util = MooFileUtil(self.temp_dir.name)
        self.table_name = "users"
        self.indexes = ["email", "role"]
        self.util.create_database(self.table_name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_regular_table_crud_with_batch_data(self):
        records = [
            {
                "name": f"user-{index:02d}",
                "email": f"user-{index:02d}@example.com",
                "age": 20 + index,
                "role": "admin" if index % 5 == 0 else "user",
            }
            for index in range(30)
        ]

        self.util.insert_data(self.table_name, records, self.indexes)
        self.assertEqual(self.util.count_data(self.table_name, {}, self.indexes), 30)
        self.assertEqual(
            len(self.util.query_data(self.table_name, {"role": "admin"}, self.indexes)),
            6,
        )

        self.util.update_data(
            self.table_name,
            {"role": "user"},
            {"status": "active"},
            self.indexes,
        )
        self.assertEqual(
            self.util.count_data(
                self.table_name, {"status": "active"}, self.indexes
            ),
            24,
        )

        self.util.delete_data(
            self.table_name, {"age": {"$lt": 25}}, self.indexes
        )
        self.assertEqual(self.util.count_data(self.table_name, {}, self.indexes), 25)

    def test_database_file_lifecycle(self):
        self.assertEqual(self.util.list_databases(), [self.table_name])

        copied_path = self.util.copy_database(self.table_name, "users_copy")
        self.assertTrue(Path(copied_path).is_file())
        self.assertEqual(
            self.util.list_databases(), [self.table_name, "users_copy"]
        )

        renamed_path = self.util.rename_database("users_copy", "users_archive")
        self.assertTrue(Path(renamed_path).is_file())
        self.assertFalse(self.util.database_exists("users_copy"))

        self.util.delete_database("users_archive")
        self.assertEqual(self.util.list_databases(), [self.table_name])


class TestMooFileUtilVectorCrud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_path = str(
            Path("models/sentence-transformers/granite-embedding-107m-multilingual")
            .resolve()
        )

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source_dir = self.root / "txt_sources"
        self.source_dir.mkdir()
        self.util = MooFileUtil(
            str(self.root / "database"),
            is_vector=True,
            embedding_model=self.model_path,
        )
        self.table_name = "knowledge"
        self.indexes = ["document_id", "chunk_id"]
        self.util.create_database(self.table_name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _load_txt_documents(self):
        topics = [
            ("python", "Python 适合自动化、数据分析和后端开发。"),
            ("database", "数据库负责可靠地存储、查询和更新结构化数据。"),
            ("vector", "向量数据库通过嵌入相似度实现自然语言语义检索。"),
            ("network", "计算机网络使用协议在不同设备之间传输数据。"),
        ]
        loader = DocLoader()
        loaded_docs = []
        for index in range(12):
            topic, sentence = topics[index % len(topics)]
            path = self.source_dir / f"document_{index:02d}_{topic}.txt"
            path.write_text(
                "\n".join(f"第{part}段：{sentence}" for part in range(1, 5)),
                encoding="utf-8",
            )
            loaded_docs.extend(loader.txt_loader(str(path)))

        chunks = TextSpliter.text_split_by_recursive_char(
            loaded_docs, chunk_size=55, chunk_overlap=5
        )
        return [
            {"page_content": doc.page_content, "metadata": dict(doc.metadata)}
            for doc in chunks
        ]

    def test_txt_document_vector_crud_and_search(self):
        documents = self._load_txt_documents()
        self.assertGreaterEqual(len(documents), 24)

        self.util.insert_document_data(
            self.table_name, documents, self.indexes
        )
        self.assertEqual(
            self.util.count_data(self.table_name, {}, self.indexes),
            len(documents),
        )
        self.assertEqual(len(documents[0]["embedding"]), 384)

        results = self.util.vector_search(
            self.table_name, "如何使用向量进行语义搜索？", self.indexes, top_k=5
        )
        self.assertEqual(len(results), 5)
        self.assertTrue(
            any("向量数据库" in record["page_content"] for record, _ in results)
        )

        target = documents[0]
        replacement = "Python 可以编写自动化测试并处理大量文本数据。"
        self.util.update_document_data(
            self.table_name,
            {"chunk_id": target["chunk_id"]},
            replacement,
            self.indexes,
        )
        updated = self.util.query_data(
            self.table_name, {"chunk_id": target["chunk_id"]}, self.indexes
        )[0]
        self.assertEqual(updated["page_content"], replacement)
        self.assertEqual(len(updated["embedding"]), 384)

        document_id = target["document_id"]
        expected_deleted = self.util.count_data(
            self.table_name, {"document_id": document_id}, self.indexes
        )
        self.util.delete_document_data(
            self.table_name, document_id, self.indexes
        )
        self.assertGreater(expected_deleted, 0)
        self.assertEqual(
            self.util.count_data(
                self.table_name, {"document_id": document_id}, self.indexes
            ),
            0,
        )
        self.assertEqual(
            self.util.count_data("document_meta", {"id": document_id}, ["id"]),
            0,
        )


if __name__ == "__main__":
    unittest.main()