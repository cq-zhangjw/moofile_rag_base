# MooFile 后端 API 设计书

> 版本：v3.3（2026-09-23，与当前实现同步）
> 技术栈：Python 3.12 + FastAPI 0.141 + moofile 1.2.4 + sentence-transformers 6.0.1 + uvicorn + fastmcp 4.0.5
> 启动入口：`app.py`（端口 **8888**；默认同时后台启动 MCP 服务器，见 §6）
> 前端代理：`web/vite.config.ts` 已将 `/api` 转发至 `http://127.0.0.1:8888`
> 核心封装：`utils/moofile_util.py`（MooFileUtil）
> 本地嵌入模型：`models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`（384 维，中英多语言）

---

## 1. 设计目标与原则

1. **数据库 = 一个完整子目录**。每个数据库对应 `db/<db_id>/`，目录内包含 `db.bson`、`meta.json` 与原始文件目录 `_upload/`，可作为整体备份或迁移。
2. **单文件多类型**。一个 `db.bson` 内通过 `recordType` 字段区分 `record`（普通数据行 / 向量分片）、`doc`（文档元数据）、`task`（任务记录）三类记录，不再拆多个 bson。
3. **文档与知识库强关联**。文档元数据只属于它所在的知识库；删除某库文档不影响其它库（修复了旧版 `document_meta` 仅按 `source` 建索引、跨库串号的缺陷，详见 §7）。
4. **上传 ≠ 向量化**。文档上传后仅入库（状态 `uploaded`），分片与向量化由用户手动触发，过程可追踪、可重试。
5. **统一响应**。所有接口返回 `{code, data, message}`，`code=0` 表示成功。
6. **以 API 为准对齐前端**。前端字段名、状态枚举、分页结构均以后端返回为准。

---

## 2. 目录结构

```
moofile_base/
├── app.py                          # FastAPI 入口：建实例、挂 CORS、注册路由、启动任务线程；默认后台拉起 MCP 服务器（--with_mcp）
├── requirements.txt
├── mcp_servers/
│   └── knowledge_mcp_server.py     # MCP 服务器：知识库 CRUD / 文档上传向量化 / 检索（streamable-http，默认 8010）
├── logs/                           # 运行时日志（如 mcp_server.log）
├── utils/
│   ├── moofile_util.py             # 核心封装：MooFileUtil（CRUD / 向量检索 / 文档操作）
│   ├── vector_util.py              # SentenceTransformer 单例加载 + encode + rerank
│   └── document_loader.py          # 多格式文档加载 + 递归字符切分
├── models/sentence-transformers/    # 本地嵌入模型（离线可用）
├── db/                             # 数据根目录（运行时生成）
│   └── <db_id>/                    # 一个数据库 = 一个子目录
│       ├── db.bson                 # moofile Collection（record/doc/task 三类记录）
│       ├── meta.json               # 库元信息（含向量库 vectorConfig）
│       └── _upload/                # 该库上传的原始文件
├── api/
│   ├── __init__.py
│   ├── config.py                   # 路径常量、模型路径、端口、默认分片参数
│   ├── responses.py                # 统一响应 ok()/error() 与错误码
│   ├── exceptions.py               # 业务异常与 FastAPI 异常处理器
│   ├── schemas.py                  # Pydantic 请求/响应模型
│   ├── store.py                    # 低层封装：按 db_id 打开/关闭 db.bson，读 meta.json
│   ├── services/
│   │   ├── __init__.py
│   │   ├── db_service.py           # 数据库 CRUD + 回收站 + meta.json 读写
│   │   ├── record_service.py       # 普通记录分页/筛选/搜索/字段聚合
│   │   ├── document_service.py     # 文档上传/解析/列表/删除/触发向量化
│   │   ├── chunk_service.py        # 分片列表/重新 Embedding/删除
│   │   ├── task_service.py         # 任务注册 + 后台执行 + 状态推进 + 日志
│   │   ├── vector_service.py       # 嵌入模型单例 + 向量检索 + 阈值过滤
│   │   └── stats_service.py        # 统计聚合（卡片 + 趋势 + 分布）
│   └── routers/
│       ├── __init__.py
│       ├── databases.py             # /api/databases
│       ├── trash.py                # /api/trash
│       ├── records.py              # /api/databases/{id}/records
│       ├── documents.py            # /api/databases/{id}/documents
│       ├── chunks.py               # /api/databases/{id}/chunks
│       ├── tasks.py                # /api/tasks
│       ├── retrieval.py            # /api/databases/{id}/retrieval
│       ├── stats.py                # /api/databases/{id}/stats
│       └── system.py               # /api/system/*
├── docs/
│   ├── api_design.md               # 本文档
│   ├── api_todo.md                 # 开发任务清单
│   └── ...
└── tests/
    ├── api_test_report.md          # API 接口测试报告
    ├── ui_test_report.md           # 前端功能测试报告
    └── run_api_test.py              # API 自动化测试脚本
```

---

## 3. 数据模型

### 3.1 库元信息 `db/<db_id>/meta.json`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 库 ID，形如 `db_<name>_<8位hex>`，等于目录名 |
| `name` | string | 库名（唯一；2–64 位英文字母、数字或下划线，前后端统一校验 `^[A-Za-z0-9_]{2,64}$`） |
| `type` | string | `normal`（普通 JSON 库）\| `vector`（向量知识库） |
| `createdAt` | string(ISO) | 创建时间 |
| `updatedAt` | string(ISO) | 更新时间 |
| `trashed` | bool | 是否在回收站 |
| `vectorConfig` | object? | 仅向量库：`model`、`dimensions`、`chunkSize`、`chunkOverlap`、`topK`、`similarityThreshold` |

### 3.2 数据文件 `db/<db_id>/db.bson`

通过 `recordType` 区分三类记录：

#### （1）普通记录 `recordType = "record"`

普通库只存此类；向量库中此类即分片。

| 字段 | 类型 | 说明 |
|------|------|------|
| `_id` | string | moofile 自动生成的主键（hex 字符串） |
| `recordType` | string | 固定 `record` |
| `documentId` | string? | 仅向量分片：所属文档 ID |
| `document` | string? | 仅向量分片：文档名（冗余，便于列表展示） |
| `index` | int? | 仅向量分片：分片序号（从 1 开始） |
| `content` | string? | 仅向量分片：分片文本 |
| `tokens` | int? | 仅向量分片：token 数（按字符长度估算） |
| `page` | int? | 页码 |
| `embedStatus` | string? | 仅向量分片：`done` \| `none` \| `failed` |
| `embedding` | float[]? | 仅向量分片：384 维向量 |
| 其它 | any | 普通库的自由业务字段 |

普通库写入时自动补 `recordType="record"`；普通库列表查询时固定过滤 `recordType="record"`。

#### （2）文档记录 `recordType = "doc"`（仅向量库）

| 字段 | 类型 | 说明 |
|------|------|------|
| `_id` | string | 文档 ID（`id_doc_<8hex>`） |
| `recordType` | string | 固定 `doc` |
| `name` | string | 文件名 |
| `type` | string | 扩展名大写，如 `PDF`/`TXT`/`MD` |
| `size` | int | 字节 |
| `uploadTime` | string(ISO) | |
| `docStatus` | string | `uploaded` \| `parsed` \| `vectorizing` \| `completed` \| `failed` |
| `chunkCount` | int | 已切片数 |
| `vectorStatus` | string | `none` \| `partial` \| `done` \| `failed` |
| `chunkSize` | int? | 实际向量化时使用的切片大小；上传阶段不写入 |
| `overlap` | int? | 实际向量化时使用的重叠大小；上传阶段不写入 |
| `errorMsg` | string? | 失败原因 |

#### （3）任务记录 `recordType = "task"`

任务跟随所在库存储；全局任务列表由后端聚合所有库得到。

| 字段 | 类型 | 说明 |
|------|------|------|
| `_id` | string | 任务 ID（`id_task_<8hex>`） |
| `recordType` | string | 固定 `task` |
| `dbId` | string | 所属库 |
| `type` | string | `parse` \| `vectorization` \| `rebuild` \| `delete_index` |
| `target` | string | 目标描述 |
| `status` | string | `pending` \| `running` \| `completed` \| `failed` \| `cancelled` |
| `progress` | float | 0~100 |
| `startAt` / `endAt` | string(ISO)? | |
| `docIds` | string[] | 关联文档 |
| `logs` | string[] | 执行日志（追加式） |

---

## 4. 统一响应与错误码

### 4.1 成功响应

```json
{ "code": 0, "data": {}, "message": "ok" }
```

### 4.2 错误响应

```json
{ "code": 40401, "data": null, "message": "数据库不存在" }
```

| HTTP | code | 含义 |
|------|------|------|
| 200 | 0 | 成功 |
| 400 | 40001 | 请求参数错误 / 校验失败 |
| 404 | 40401 | 数据库不存在 |
| 404 | 40402 | 记录/文档/任务不存在 |
| 409 | 40901 | 名称冲突（同名库已存在） |
| 500 | 50000 | 服务器内部错误 |

---

## 5. API 接口一览

### 5.1 数据库 `/api/databases`

| 方法 | 路径 | 说明 | 请求/响应要点 |
|------|------|------|------|
| GET | `/api/databases` | 列出非回收站库 | `data`: `[{id,name,type,recordCount,documentCount,fieldCount,sizeMB,updatedAt,createdAt}]` |
| POST | `/api/databases` | 创建库 | body `{name, type}`；同名 40901 |
| GET | `/api/databases/{id}` | 库详情（含记录/文档/字段计数与大小） | |
| PUT | `/api/databases/{id}` | 重命名 | body `{name}` |
| DELETE | `/api/databases/{id}` | 软删除（`meta.json.trashed=true`） | |
| GET | `/api/databases/{id}/vector-config` | 读取向量库默认配置 | 仅向量库 |
| PUT | `/api/databases/{id}/vector-config` | 保存模型、分块、Top K 与阈值 | 切换模型会清除旧向量并将文档重置为待向量化 |

> `recordCount` = 该库 `recordType="record"` 数量；向量库返回真实 `documentCount`，普通库返回聚合后的 `fieldCount`；`sizeMB` = 数据库文件大小（MB，保留 2 位小数）。

### 5.2 回收站 `/api/trash`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/trash` | 列出 `trashed=true` 的库 |
| POST | `/api/trash/{id}/restore` | 恢复（`trashed=false`） |
| DELETE | `/api/trash/{id}` | 彻底删除（`shutil.rmtree` 库目录） |
| DELETE | `/api/trash` | 清空回收站 |

### 5.3 普通记录 `/api/databases/{id}/records`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/databases/{id}/records` | 分页+搜索+筛选；query: `page,pageSize,search,filter` |
| GET | `/api/databases/{id}/records/fields` | 聚合字段名列表（不含 `_id`/`embedding`/`recordType`） |
| POST | `/api/databases/{id}/records` | 新增一条（body 为 JSON 对象，自动补 `recordType`） |
| PUT | `/api/databases/{id}/records/{rid}` | 按 `_id` 更新整条 |
| POST | `/api/databases/{id}/records/delete` | 批量删除，body `{ids:[]}` |

**筛选结构**（前端 `FilterGroup`）：

```json
{ "logic": "AND", "conditions": [ {"field":"role","operator":"eq","value":"user"} ] }
```

| 前端 operator | 后端实现 |
|---------------|----------|
| `eq` / `ne` | moofile `$eq` / `$ne` |
| `gt` `gte` `lt` `lte` | moofile `$gt/$gte/$lt/$lte` |
| `exists` / `not_exists` | moofile `$exists` |
| `contains` / `not_contains` | Python 后过滤（`str(value).includes`） |
| `regex` | Python 后过滤（正则匹配） |
| `array_contains` | Python 后过滤（值在数组内） |
| 多条件 `AND/OR` | 组合 moofile `$and`/`$or`，无法下推的条件在 Python 层合并 |

**分页响应**：`data: {list:[...], total:N, page:1, pageSize:20}`。

### 5.4 文档 `/api/databases/{id}/documents`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/databases/{id}/documents` | 列表；query `search,status` |
| POST | `/api/databases/{id}/documents/upload` | 上传（multipart 仅 `file`）；原文件写入该库 `_upload/`，记录状态为 `uploaded` |
| POST | `/api/databases/{id}/documents/delete` | 批量删除；body `{ids:[]}`（同时删分片） |
| GET | `/api/databases/{id}/documents/{docId}/download` | 下载上传时保存的原始文件 |
| POST | `/api/databases/{id}/documents/vectorize` | 触发向量化；body `{docIds:[], model, chunkSize, overlap}` |

> 上传后仅写 `doc` 记录，不设置分块参数、不做切片/Embedding；`vectorize` 才提交 `model/chunkSize/overlap` 并创建后台任务。对话框默认值来自该库 `vectorConfig`，当前不提供 Metadata Fields 配置。

### 5.5 分片 `/api/databases/{id}/chunks`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/databases/{id}/chunks` | 分页；query `page,pageSize,search,docId`；返回 `{list,total}` |
| POST | `/api/databases/{id}/chunks/{chunkId}/reembed` | 重建该分片向量 |
| POST | `/api/databases/{id}/chunks/delete` | 批量删除；body `{ids:[]}` |

> 前端“分片设置”页签在 v3.0 按 UI 调整需求隐藏，但接口保留可用。

### 5.6 任务 `/api/tasks`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks` | 列表；query `dbId,type,status`（不传 dbId 聚合全部库） |
| POST | `/api/tasks/{taskId}/cancel?dbId=` | 取消任务 |
| POST | `/api/tasks/{taskId}/retry?dbId=` | 重试任务 |
| GET | `/api/tasks/{taskId}/logs?dbId=` | 任务日志 `data: []` |

### 5.7 检索 `/api/databases/{id}/retrieval`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/databases/{id}/retrieval` | 向量检索；body `{query, topK?, threshold?}`，省略时使用该库 `vectorConfig` |

**响应**：`data: [{rank, score, source, chunkIndex, content, documentId}]`，按相似度降序、按 `threshold` 过滤。查询文本必须使用该库 `vectorConfig.model` 编码，保证与文档向量处于同一 embedding 空间。前端初始 Top K/阈值读取库配置，最多展示 4 张结果卡并在结果区内部滚动。当前仅实现向量检索，不提供 Hybrid Search。

### 5.8 统计 `/api/databases/{id}/stats`

`data`：

```json
{
  "cards": {"documentCount":0,"chunkCount":0,"vectorCount":0,"storageMB":0.0,"failedDocs":0,"failedTasks":0},
  "dates": ["...7天日期..."],
  "uploads": [0], "vectorized": [0],
  "distribution": [{"name":"已完成","value":1,"color":"#16A34A"}]
}
```

### 5.9 系统 `/api/system`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/system/health` | 健康检查 `{status, model, dims}` |
| GET | `/api/system/storage` | 存储用量 `{usedGB, quotaGB, percent}` |
| GET | `/api/system/models` | 可用嵌入模型列表 |
| GET | `/api/system/help?locale=zh\|ja\|en` | 返回对应根目录 README 的 Markdown；英文使用 `README.md` |

---

## 6. MCP 服务器（streamable-http）

> 代码：`mcp_servers/knowledge_mcp_server.py`（基于 FastMCP 4.0.5）
> 端点：`http://127.0.0.1:8010/mcp`（Streamable HTTP 协议）

### 6.1 定位与启动方式

MCP 服务器通过 `requests` 调用本设计书 §5 中的 REST 接口，把知识库能力以 MCP 工具形式暴露给 MCP 客户端（如 AI 客户端/智能体），便于通过工具调用直接管理知识库。它不直接读写数据文件，后端 REST API 是唯一数据通道。

- **随后端自动启动**：`python app.py` 默认（`--with_mcp true`）在后台拉起 MCP 服务器；`python app.py --with_mcp false` 或环境变量 `MOOFILE_WITH_MCP=false` 可关闭。
- **防重复启动**：启动前探测 MCP 端口，若已有实例在监听则直接复用，不会拉起第二个进程。
- **生命周期**：MCP 服务器是独立子进程，日志写入 `logs/mcp_server.log`；后端进程退出时自动终止该子进程。
- **手动启动**：`python mcp_servers/knowledge_mcp_server.py`。

### 6.2 配置（环境变量）

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MOOFILE_API_BASE` | `http://127.0.0.1:8888` | 后端 REST API 地址 |
| `MOOFILE_API_TIMEOUT` | `10` | 请求超时（秒） |
| `MOOFILE_MCP_HOST` | `127.0.0.1` | MCP 服务器绑定地址 |
| `MOOFILE_MCP_PORT` | `8010` | MCP 服务器端口（`app.py` 拉起子进程时同样读取该变量） |

### 6.3 工具清单

所有工具调用后端接口并解包统一响应 `{code, data, message}`；业务失败（库不存在、同名冲突、文件类型不支持等）会转为 MCP ToolError 返回给客户端。

| 工具 | 对应 REST 接口 | 说明 |
| --- | --- | --- |
| `create_knowledge_base(name, db_type)` | POST `/api/databases` | 创建知识库（`normal`/`vector`） |
| `get_knowledge_base(db_id)` | GET `/api/databases/{id}` | 按 db_id 查库详情 |
| `list_knowledge_bases()` | GET `/api/databases` | 列出非回收站库 |
| `rename_knowledge_base(db_id, new_name)` | PUT `/api/databases/{id}` | 重命名（重命名可能生成新 db_id） |
| `delete_knowledge_base(db_id)` | DELETE `/api/databases/{id}` | 软删除（进回收站） |
| `get_db_id_by_name(db_name)` | GET `/api/databases` | 按名称（大小写不敏感）解析 db_id |
| `upload_and_vectorize_document(local_path, db_id, ...)` | POST 文档 upload + vectorize | 上传本地文档并触发向量化；`wait=true` 时轮询任务至结束并返回分片数 |
| `list_documents(db_id)` | GET `/api/databases/{id}/documents` | 列出库内文档 |
| `delete_document(db_id, doc_id)` | POST `/api/databases/{id}/documents/delete` | 删除文档及其分片 |
| `retrieve_knowledge(db_id, query, top_k?, threshold?)` | POST `/api/databases/{id}/retrieval` | 语义检索（RAG）；省略 `top_k`/`threshold` 时使用库内 `vectorConfig` 默认值 |

> 说明：`upload_and_vectorize_document` 仅支持后端向量化 worker 可解析的文本类型（`.txt`/`.md`/`.markdown`/`.csv`/`.html`/`.htm`/`.json`/`.log`）。上传接口虽接受更多扩展名，但其余类型会在向量化阶段失败。

---

## 7. 关键修复：文档与知识库的关联性

**问题**：旧版 `utils/moofile_util.py` 的 `get_document_id(source)` 只按 `source` 在**全局** `document_meta` 表分配文档 ID：

```python
# 旧（缺陷）
result = self.query_data("document_meta", {"source": source}, ["id"])
```

后果：
- 两个不同知识库上传同名文件 → 得到**同一个 document_id**，分片互相串库；
- `delete_document_data` 删除某库文档时按全局 `{id: document_id}` 删 meta，会误删其它库同 source 的记录。

**修复**（已落地于 `utils/moofile_util.py`）：
- 文档身份升级为复合键 `(db_name, source)`：`get_document_id(source, db_name)`；
- `document_meta` 索引改为 `["source", "db_name"]`，写入记录带 `db_name` 字段；
- `insert_document_data` 切片时把 `db_name` 透传给 `get_document_id`；
- `delete_document_data` 清理 meta 时加 `db_name` 条件，跨库隔离。

在 v3.0 后端实现中，文档元数据直接存放在各知识库自己的 `db/<db_id>/db.bson`（`recordType="doc"`），从根本上做到**文档只属于自己的知识库**；`MooFileUtil` 的全局表路径作为底层兼容能力同样完成了上述修复。

---

## 8. 任务后台执行模型

- 任务在 `task_service` 注册为 `pending`，立即返回任务 ID；
- 后台线程依次推进：`pending → running → completed/failed/cancelled`，实时更新 `progress` 与 `logs`，并联动更新文档 `docStatus`/`vectorStatus` 与分片 `embedStatus`；
- 向量化任务流程：加载文件 → 切片（chunkSize/overlap）→ 逐片 `encode` → 写入分片记录（含 embedding）→ 更新文档统计。
- 取消：置 `cancelled`，后台循环在切片间隙检查并退出。

---

## 9. 与前端的对齐约定

| 前端期望 | 后端返回 |
|----------|----------|
| 列表项主键 | 统一同时返回 `_id` 与 `id`（前端 `id = id \|\| _id`） |
| 文档/任务/分片 | 补 `dbId` 字段 |
| 分页接口 | `{list, total}` |
| 空结果 | 返回空数组/空对象，不抛错 |
| 跨域 | FastAPI 启用 CORS，允许本地前端源 |

### 9.1 v3.0 UI 调整带来的接口影响

按前端调整需求，以下入口在界面上隐藏，但后端接口保持可用（接口测试仍需覆盖）：
- 数据库详情页隐藏「分片设置」「索引信息」页签；
- 统计卡隐藏「索引状态」；
- 侧边栏移除「使用存储空间」卡片（`/api/system/storage` 仍保留供系统页使用）；
- 顶栏「服务运行正常」移除，改为前端本地实时时钟（不占接口）。

### 9.2 v3.1 前端联动约定

- 文档上传成功后，文档页立即刷新；存在 `vectorizing` 文档时每 2 秒轮询文档状态，完成后停止；
- 重命名后同步刷新侧栏与详情；向量化轮询同时刷新文档数、记录数、大小等数据库统计；
- 向量库公开 Tabs 为「文档管理 / 数据浏览 / 检索测试 / 统计信息 / 设置」；设置写入 `meta.json.vectorConfig`；
- 文档删除必须提示会连带删除关联片段，数据单条/批量删除均需二次确认；
- 普通库仅提供数据浏览，并支持导出当前页或全部记录为 JSON；向量库隐藏「新增数据」和记录导出入口；
- 数据库详情 Tab 由路由控制并保持当前选择，使用自定义选中下划线；
- UI 支持 `zh`、`ja`、`en`。语言优先级为：用户保存在 `moofile.locale` 的选择 > 浏览器语言 > 英文回退。

---

## 10. 版本记录

- v1.0：全局 `_meta/databases.bson` 注册表 + 每库多文件（data/documents/tasks.bson）。
- v2.0：数据库=子目录；单文件 `db.bson` 用 `recordType` 区分；`meta.json`。
- v3.0：落地完整实现；修复文档-知识库关联；补齐全部接口；对齐前端字段与状态枚举；按 UI 调整隐藏分片/索引入口。
- v3.1：补充文档下载、真实文档/字段计数与两位小数大小；检索默认阈值改为 0.3 并移除 Hybrid Search；默认 overlap 改为 20；同步三语言与前端刷新/导出行为。
- v3.2（2026-09-22）：上传文件迁入各库 `_upload/` 且上传阶段不再设置分块参数；新增数据库级 `vectorConfig` 与设置 Tab；检索使用同库模型；名称规则改为字母/数字/下划线；补充删除确认、帮助 Markdown、重命名与向量化统计刷新；模型改为首次向量使用时按需加载。
- v3.3（当前）：新增 MCP 服务器（§6）：基于 FastMCP 的 streamable-http 端点 `http://127.0.0.1:8010/mcp`，暴露知识库 CRUD、文档上传/向量化/删除与语义检索 10 个工具；`app.py` 新增 `--with_mcp` 参数（默认 true）后台拉起 MCP 子进程，支持端口复用检测与退出自动回收，日志写入 `logs/mcp_server.log`。
