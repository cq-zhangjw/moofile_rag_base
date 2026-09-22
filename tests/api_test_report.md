# MooFile API 测试报告

> 测试时间：2026-09-21
> 被测服务：`http://127.0.0.1:8888`（`python app.py`）
> 测试脚本：`tests/run_api_test.py`
> 结论：**31 / 31 全部通过（100%）**

---

## 1. 测试环境

| 项 | 值 |
|----|----|
| 后端框架 | FastAPI 0.141 + uvicorn 0.53 |
| 存储引擎 | moofile 1.2.4（BSON Collection） |
| 嵌入模型 | paraphrase-multilingual-MiniLM-L12-v2（384 维，本地离线） |
| Python | 3.12（项目 `.venv`） |
| 数据库目录 | `db/<db_id>/`（db.bson + meta.json） |

## 2. 统一响应校验

所有接口均返回 `{code, data, message}`，`code=0` 为成功；资源不存在返回 `code=40401`，参数错误 `40001`，名称冲突 `40901`。

## 3. 用例明细

| # | 接口 | 方法 | 用例 | 结果 |
|---|------|------|------|------|
| 1 | `/api/system/health` | GET | 健康检查，模型 dims=384 | PASS |
| 2 | `/api/system/storage` | GET | 返回 usedGB/quotaGB/percent | PASS |
| 3 | `/api/system/models` | GET | 返回可用模型列表 | PASS |
| 4 | `/api/databases` | GET | 初始列表为数组 | PASS |
| 5 | `/api/databases` | POST | 创建普通库 | PASS |
| 6 | `/api/databases` | POST | 创建向量库 | PASS |
| 7 | `/api/databases` | POST | 同名冲突 → 40901 | PASS |
| 8 | `/api/databases/{id}` | GET | 读取库详情 | PASS |
| 9 | `/api/databases/{id}` | PUT | 重命名库 | PASS |
| 10 | `/api/databases/{id}/records` | GET | 分页（25 条取第 1 页 10 条） | PASS |
| 11 | `/api/databases/{id}/records` | GET | filter `role eq admin` → 5 条 | PASS |
| 12 | `/api/databases/{id}/records` | GET | filter `age gt 40` → 4 条 | PASS |
| 13 | `/api/databases/{id}/records` | GET | search `user2` 模糊命中 | PASS |
| 14 | `/api/databases/{id}/records/fields` | GET | 聚合字段 name/age/role | PASS |
| 15 | `/api/databases/{id}/records/{rid}` | PUT | 更新记录 | PASS |
| 16 | `/api/databases/{id}/records/delete` | POST | 批量删除记录 | PASS |
| 17 | `/api/databases/{id}/documents/upload` | POST | multipart 上传 note.txt | PASS |
| 18 | `/api/databases/{id}/documents` | GET | 文档列表 | PASS |
| 19 | `/api/databases/{id}/documents/vectorize` | POST | 触发向量化任务 | PASS |
| 20 | `/api/tasks` | GET | 轮询任务至 completed | PASS |
| 21 | `/api/databases/{id}/chunks` | GET | 向量化后产生 15 个分片 | PASS |
| 22 | `/api/databases/{id}/retrieval` | POST | 语义检索命中 3 条 | PASS |
| 23 | `/api/databases/{id}/retrieval` | POST | 返回结构含 rank/score/content | PASS |
| 24 | `/api/databases/{id}/chunks/{cid}/reembed` | POST | 重建单分片向量 | PASS |
| 25 | `/api/tasks/{tid}/logs` | GET | 任务日志列表非空 | PASS |
| 26 | `/api/databases/{id}/stats` | GET | 统计 cards/chunkCount≥1 | PASS |
| 27 | `/api/databases/{id}` | DELETE | 软删除入库回收站 | PASS |
| 28 | `/api/trash` | GET | 回收站列表含该库 | PASS |
| 29 | `/api/trash/{id}/restore` | POST | 恢复 | PASS |
| 30 | `/api/trash/{id}` | DELETE | 彻底删除 | PASS |
| 31 | `/api/trash/{id}` | DELETE | 删除向量库 | PASS |

## 4. 关键验证点

- **筛选下推与后过滤**：`eq/gt` 走 moofile 原生查询，`search` 在服务端做内容模糊，均正确分页。
- **文档→分片→向量化闭环**：上传文档仅置 `uploaded`；手动触发 `vectorize` 后，后台线程切片（chunkSize=80/overlap=10）并逐片生成 384 维向量，文档状态流转至 `completed`，`chunkCount=15`。
- **语义检索**：`vector_search` 返回 `(doc, score)`，接口按 `rank/score/source/chunkIndex/content` 结构化返回，并支持 `threshold` 过滤。
- **回收站软/硬删除**：软删除仅标记 `trashed=true`，可恢复；硬删除 `rmtree` 库目录，数据彻底清除。
- **文档-知识库关联修复**：文档记录存储于各库自身 `db.bson`（`recordType=doc`），删除某库文档不影响其它库（见 `docs/api_design.md` §6）。

## 5. 复现方式

```powershell
# 终端 1
python app.py
# 终端 2
python tests/run_api_test.py
```

预期输出末尾：`==== 31/31 passed ====`，进程退出码 0。
