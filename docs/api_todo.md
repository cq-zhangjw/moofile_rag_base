# MooFile 后端开发任务清单（api_todo.md）

> 依据：`docs/api_design.md` v3.2。技术栈：FastAPI + moofile 1.2.4 + sentence-transformers。
> 启动入口：`app.py`（端口 8888）。数据根目录：`db/<db_id>/`。
> 核心封装：`utils/moofile_util.py`（已修复文档-知识库关联）。
> 状态：**v3.2 已完成**。本文件是后端任务状态的唯一来源；旧版 `backend-todo.md` 仅保留为归档索引。

状态标记：[x] 已完成 / [ ] 待开发

---

## 阶段 A · 工程骨架与配置

- [x] A1 创建 `app.py`：FastAPI 实例 + CORS + 注册所有 router + 启动任务线程；嵌入模型首次使用时按需加载
- [x] A2 创建 `api/config.py`：`BASE_DIR`、`DB_DIR`、`MODEL_PATH`、`PORT=8888`、默认 chunkSize=500/overlap=20、向量维度=384
- [x] A3 创建 `api/responses.py`：`ok(data)` / `error(code,msg)` 统一响应与错误码常量
- [x] A4 创建 `api/exceptions.py`：业务异常类 + 全局异常处理器（映射到统一响应）
- [x] A5 创建 `api/schemas.py`：Pydantic 模型（创建库/重命名/记录/筛选组/文档上传/向量化/检索/批量删除）
- [x] A6 创建 `api/store.py`：`open_collection(db_id)`、`read_meta/write_meta/list_db_dirs`、`ensure_db`

## 阶段 B · 数据库与回收站

- [x] B1 `api/services/db_service.py`：create/list/get/rename/delete(软)；list trash/restore/destroy/empty
- [x] B2 `api/services/db_service.py`：计算 `recordCount`、`documentCount`、`fieldCount` 与两位小数 `sizeMB`
- [x] B3 `api/routers/databases.py`：CRUD 路由
- [x] B4 `api/routers/trash.py`：回收站路由

## 阶段 C · 普通记录

- [x] C1 `api/services/record_service.py`：分页、`search`（内容模糊）、`filter`（12 操作符，可下推 moofile 的下推、其余 Python 后过滤）
- [x] C2 `api/services/record_service.py`：`fields()` 聚合字段名（排除 `_id`/`embedding`/`recordType`）
- [x] C3 新增 / 整条更新 / 批量删除
- [x] C4 `api/routers/records.py`：路由 + `/fields` + `/delete`

## 阶段 D · 文档与分片（向量库）

- [x] D1 `api/services/vector_service.py`：模型单例、`encode(text)`、`vector_search(db_id, text, top_k, threshold)`
- [x] D2 `api/services/document_service.py`：上传落盘（multipart）、写 `doc` 记录（uploaded）、原文件下载
- [x] D3 `api/services/document_service.py`：列表（search/status）、批量删除（连带删分片）
- [x] D4 `api/services/chunk_service.py`：分片分页（docId/search）、reembed、批量删除
- [x] D5 `api/routers/documents.py` + `api/routers/chunks.py`

## 阶段 E · 任务调度

- [x] E1 `api/services/task_service.py`：任务注册（pending）、后台线程执行、状态机推进、progress/logs
- [x] E2 向量化任务：加载文件 → 递归切片 → 逐片 encode → 写分片记录 → 更新文档统计
- [x] E3 取消 / 重试 / 日志查询；任务完成联动文档与分片状态
- [x] E4 `api/routers/tasks.py`：列表（支持 dbId 聚合）/ cancel / retry / logs

## 阶段 F · 检索 / 统计 / 系统

- [x] F1 `api/routers/retrieval.py`：POST retrieval（纯向量检索、threshold 过滤，返回 rank/score/source/chunkIndex/content）
- [x] F2 `api/services/stats_service.py`：cards（document/chunk/vector/storage/failed）+ 近 7 日趋势 + 状态分布
- [x] F3 `api/routers/stats.py`
- [x] F4 `api/routers/system.py`：health / storage / models

## 阶段 G · API 测试与联调

- [x] G1 编写 `tests/run_api_test.py`：覆盖主要接口的正向用例
- [x] G2 启动 `app.py`，运行 API 测试
- [x] G3 生成 `tests/api_test_report.md`（用例、请求、期望、实际、结论）
- [x] G4 前端 `web` 构建并与后端联调，按 API 调整前端字段/调用
- [x] G5 完成前端 UI 联动修改（见下）
- [x] G6 功能测试并生成 `tests/ui_test_report.md`

## 阶段 H · 前端 UI 修改清单

- [x] H1 移除左下角「使用存储空间」卡片
- [x] H2 移除数据库详情页「分片设置」「索引信息」页签
- [x] H3 顶栏改为本地化实时时钟并增加语言选择器
- [x] H4 移除数据库详情统计卡「索引状态」，按库类型展示真实文档数/字段数
- [x] H5 联调校验：路由跳转、上传刷新、2 秒状态轮询、下载、向量化、检索、导出、回收站
- [x] H6 前端构建与 `vue-tsc --noEmit` 通过
- [x] H7 检索默认阈值 0.3，移除 Hybrid Search，结果区最多 4 张卡并滚动
- [x] H8 默认 overlap 20，向量化确认展示已选文档，移除 Metadata Fields
- [x] H9 向量库隐藏新增/导出；普通库支持当前页/全部 JSON 导出
- [x] H10 完成 `zh`/`ja`/`en` 国际化，保存用户选择并优先于浏览器语言

## 阶段 I · 文档全体修正

- [x] I1 同步修订 `docs/api_design.md` 与实际实现一致
- [x] I2 修订 `docs/moofile-database-management-design.md` 与当前公开 UI 流程一致
- [x] I3 修订 `docs/backend-todo.md` / `docs/ui_todo.md` 状态并消除重复来源
- [x] I4 新增根目录英文、中文、日文 README

## 阶段 J · v3.2 向量配置与交互同步

- [x] J1 数据库名称统一为 2–64 位英文字母、数字或下划线，并向前端返回可见校验错误
- [x] J2 原文件改存 `db/<db_id>/_upload/`，上传接口仅接收文件，分块参数延后到向量化阶段
- [x] J3 新增 `GET/PUT /api/databases/{id}/vector-config`，保存模型、维度、Chunk、Top K 与阈值
- [x] J4 检索使用数据库保存的 embedding 模型与默认 Top K/阈值，避免查询与文档向量空间不一致
- [x] J5 新增帮助 Markdown 接口，按 `zh/ja/en` 返回对应根目录 README
- [x] J6 补充删除确认、重命名刷新、向量化统计刷新并同步设计书和 README
