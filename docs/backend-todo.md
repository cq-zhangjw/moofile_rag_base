# MooFile 后端开发任务清单（backend-todo.md）

> **归档说明（2026-09-22）**：本文件不再作为活动清单维护。后端完成状态与后续变更统一记录在 `docs/api_todo.md`；此处仅保留阶段历史。
>
> 依据：`docs/api_design.md` v3.2。技术栈：FastAPI + moofile 1.2.4 + sentence-transformers。
> 启动入口：`app.py`（端口 8888）。数据根目录：`db/<db_id>/`。
> 状态：**历史阶段已完成**。v3.2 的向量配置、库内上传目录、帮助文档与刷新行为见 `docs/api_todo.md`。

## 阶段 A · 工程骨架

- [x] A1 创建 `app.py` 入口：FastAPI 实例 + CORS + 路由注册 + 启动事件
- [x] A2 创建 `api/config.py`：DB_DIR、模型路径、端口、默认 chunkSize/overlap
- [x] A3 创建 `api/schemas.py` Pydantic 请求模型
- [x] A4 创建 `api/services/db_service.py`：数据库 CRUD + 回收站 + 元数据集合管理

## 阶段 B · 记录与数据浏览

- [x] B1 `api/services/record_service.py`：分页查询 + 筛选（12 操作符）+ 搜索
- [x] B2 `api/routers/records.py`：GET/POST/PUT/DELETE records + fields
- [x] B3 集成 moofile Collection：每库单文件 `db.bson` CRUD

## 阶段 C · 文档与分片（向量库）

- [x] C1 `api/services/document_service.py`：文档上传/列表/删除/下载；上传仅入库
- [x] C2 `api/services/chunk_service.py`：分片分页查询 + 重新 Embedding
- [x] C3 `api/services/vector_service.py`：SentenceTransformer 单例 + encode + vector_search
- [x] C4 `api/routers/documents.py` + `api/routers/chunks.py`

## 阶段 D · 任务调度

- [x] D1 `api/services/task_service.py`：任务创建 + 后台工作线程 + 状态推进
- [x] D2 `api/routers/tasks.py`：列表/取消/重试/日志
- [x] D3 任务完成后联动更新文档/分片状态

## 阶段 E · 索引/检索/统计/系统

- [x] E1 `api/routers/databases.py`：数据库 CRUD 路由
- [x] E2 `api/routers/trash.py`：回收站路由
- [x] E3 `api/routers/retrieval.py`：语义检索接口
- [x] E4 `api/routers/stats.py`：统计聚合接口
- [x] E5 模型切换与重建索引通过现有文档/任务/系统服务协作完成（无独立 `index.py` 路由）
- [x] E6 `api/routers/system.py`：健康检查/存储/模型列表

## 阶段 F · 测试与联调

- [x] F1 启动后端，curl 验证每个接口（health/storage/databases/records/stats/tasks 均 200）
- [x] F2 前端 vite proxy 配置 + 替换 mock 为真实 axios 调用
- [x] F3 端到端验证：创建库 → 插入记录 → 数据浏览动态列 → 任务中心 → 回收站
- [x] F4 CORS 已配置，错误码统一，空态正常
