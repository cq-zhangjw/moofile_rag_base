import os
from moofile import Collection
from sentence_transformers import SentenceTransformer

# ---------- 1. 初始化嵌入模型 ----------
# 该模型输出 384 维向量，支持 50+ 语言[citation:2][citation:5]
# model = SentenceTransformer('models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model = SentenceTransformer('models/sentence-transformers/granite-embedding-107m-multilingual')


# ---------- 2. 打开/创建知识库 ----------
# 数据库文件位于当前目录/db/knowledge.bson
db_dir = os.path.join(os.path.dirname(os.path.dirname((__file__))), "db/knowledge1")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "knowledge.bson")

# 声明向量索引维度为 384（与模型输出一致）[citation:1]
with Collection(db_path, indexes=["source"], vector_indexes={"embedding": 384}) as db:

    # ---------- 3. 增加 (Create) ----------
    print("=== 增加知识条目 ===")
    
    documents = [
        {"title": "Python 基础", "content": "Python 是一种解释型、面向对象的高级编程语言。", "source": "manual"},
        {"title": "机器学习入门", "content": "机器学习是人工智能的一个分支，让计算机从数据中学习规律。", "source": "manual"},
        {"title": "向量数据库", "content": "向量数据库专门用于存储和检索高维向量，支持语义相似度搜索。", "source": "manual"},
    ]
    
    for doc in documents:
        # 手动将 content 转为向量
        vector = model.encode(doc["content"]).tolist()
        doc["embedding"] = vector  # 存入向量字段
        db.insert(doc)
        print(f"已插入: {doc['title']}")

    # ---------- 4. 查询 (Read) ----------
    print("\n=== 语义查询 ===")
    
    query_text = "自然语言处理是什么？"
    query_vector = model.encode(query_text).tolist()
    
    # 使用 vector_search 进行相似度检索[citation:1][citation:6]
    results = db.find({}).vector_search("embedding", query_vector, limit=2).to_list()
    
    for doc, score in results:
        print(f"\n相似度: {score:.4f}")
        print(f"标题: {doc['title']}")
        print(f"内容: {doc['content']}")

    # ---------- 5. 修改 (Update) ----------
    print("\n=== 修改知识条目 ===")
    
    # 更新标题
    db.update_one({"title": "Python 基础"}, set={"title": "Python 语言基础"})
    updated = db.find_one({"title": "Python 语言基础"})
    print(f"更新后标题: {updated['title']}")

    # 如果内容变了，需要重新计算向量
    new_content = "Python 是一种解释型、面向对象、动态类型的高级编程语言。"
    new_vector = model.encode(new_content).tolist()
    db.update_one({"title": "Python 语言基础"}, set={"content": new_content, "embedding": new_vector})
    print("已更新内容并重新计算向量")

    # ---------- 6. 删除 (Delete) ----------
    print("\n=== 删除知识条目 ===")
    
    db.delete_one({"title": "机器学习入门"})
    remaining = db.find({}).to_list()
    print(f"删除后剩余 {len(remaining)} 条记录:")
    for doc in remaining:
        print(f"  - {doc['title']}")

print(f"\n数据库文件: {db_path}")