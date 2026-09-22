import os
from moofile import Collection

# 确保 db 目录存在
db_dir = os.path.join(os.path.dirname(os.path.dirname((__file__))), "db/user")
os.makedirs(db_dir, exist_ok=True)

# 数据库文件路径
db_path = os.path.join(db_dir, "users.bson")

# 打开/创建 user 集合，并创建 email 索引以加速查询 [citation:5]
with Collection(db_path, indexes=["email"]) as db:
    
    # ---------- 1. 增加 (Create) ----------
    print("=== 增加 ===")
    user1 = db.insert({"name": "张三", "email": "zhangsan@example.com", "age": 28, "role": "admin"})
    print(f"插入用户: {user1['_id']}, {user1['name']}")

    user2 = db.insert({"name": "李四", "email": "lisi@example.com", "age": 32, "role": "user"})
    print(f"插入用户: {user2['_id']}, {user2['name']}")

    # 批量插入 [citation:5]
    db.insert_many([
        {"name": "王五", "email": "wangwu@example.com", "age": 25, "role": "user"},
        {"name": "赵六", "email": "zhaoliu@example.com", "age": 35, "role": "user"},
    ])
    print("批量插入 2 个用户")

    # ---------- 2. 查询 (Read) ----------
    print("\n=== 查询 ===")
    
    # 查询所有用户
    all_users = db.find({}).to_list()
    print(f"全部用户 ({len(all_users)} 条):")
    for u in all_users:
        print(f"  - {u['name']} ({u['email']}), 年龄: {u['age']}, 角色: {u['role']}")

    # 条件查询：年龄大于 30 [citation:5]
    older = db.find({"age": {"$gt": 30}}).to_list()
    print(f"\n年龄 > 30 的用户:")
    for u in older:
        print(f"  - {u['name']}, 年龄: {u['age']}")

    # 按 email 精确查询单条 [citation:5]
    found = db.find_one({"email": "lisi@example.com"})
    print(f"\n按 email 查找: {found['name']}")

    # ---------- 3. 修改 (Update) ----------
    print("\n=== 修改 ===")
    
    # 更新单条：将张三年龄改为 29 [citation:1]
    db.update_one({"email": "zhangsan@example.com"}, set={"age": 29})
    updated = db.find_one({"email": "zhangsan@example.com"})
    print(f"张三年龄已更新为: {updated['age']}")

    # 批量更新：所有角色为 user 的人状态改为 active [citation:1]
    db.update_many({"role": "user"}, set={"status": "active"})
    active_users = db.find({"status": "active"}).to_list()
    print(f"已激活的用户: {[u['name'] for u in active_users]}")

    # ---------- 4. 删除 (Delete) ----------
    print("\n=== 删除 ===")
    
    # 删除单条：删除赵六 [citation:1]
    db.delete_one({"email": "zhaoliu@example.com"})
    remaining = db.find({}).to_list()
    print(f"删除赵六后剩余 {len(remaining)} 条记录")

    # 批量删除：删除所有年龄小于 30 的用户 [citation:1]
    db.delete_many({"age": {"$lt": 30}})
    final = db.find({}).to_list()
    print(f"清理后剩余用户: {[u['name'] for u in final]}")

print(f"\n数据库文件位于: {db_path}")