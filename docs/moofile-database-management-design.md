# MooFile Database Management UI Design Specification

- Version: 1.3（v3.2 实现同步版，2026-09-22）
- Author: Product Design
- Target: Vue3 + NaiveUI / React + Ant Design
- Type: Product Design Specification
- v3.1 变更：同步当前 FastAPI/Vue 实现；检索阈值默认 0.3 并移除 Hybrid Search；默认 overlap=20；补充文档下载、JSON 导出、状态轮询和中日英国际化。
- v3.2 变更：新增向量库设置 Tab；上传阶段移除分块参数；原文件归档到各数据库内部；补充名称规则、删除确认、帮助 Markdown 与统计刷新。

## 1. Product Overview

MooFile 是一个支持 JSON 文档存储及 Vector Knowledge Base 的轻量级数据库平台。

系统需要同时支持：

- 普通 JSON 数据库
- 向量知识库数据库

要求：

- 支持大量 JSON 数据管理
- 支持向量知识库管理
- 支持文档生命周期管理
- 支持向量任务管理
- 支持条件筛选
- UI 简洁现代
- 符合开发人员使用习惯

## 2. Information Architecture

```text
Database
│
├── Data
│
├── Documents
│
├── Retrieval Testing
│
├── Statistics
│
└── Settings
```

> v3.0 调整：界面上不再展示「分片设置（Chunks）」与「索引信息（Index Settings）」入口；
> 分片与索引管理能力保留在后端接口，仅作内部/高级使用，不进入主流程 UI。

## 3. Database Types

### 3.1 Normal Database

用途：

存储普通 JSON 数据

支持：

- Create
- Read
- Update
- Delete
- Filter
- Search

### 3.2 Vector Knowledge Base

用途：

- 存储文档
- 管理Chunk
- 生成Embedding
- 执行向量检索

支持：

- Document Upload
- Document Management
- Chunk Management
- Vectorization
- Retrieval Testing

## 4. Global Layout

### 4.1 Header

内容：

- Logo
- Localized Real-time Clock
- Refresh
- Language Selector (中文 / 日本語 / English)
- Help (按当前界面语言渲染根目录 README Markdown)
- User Info

高度：

64px

### 4.2 Sidebar

内容：

- \+ New Database
- Search Database
- Database List

显示：

- Database Name
- Type
- Record Count
- Storage Size

支持：

- Collapse
- Expand

### 4.3 Main Area

根据模块切换内容：

- Data
- Documents
- Retrieval Testing
- Statistics

> v3.0：Chunks / Index Settings 已从主流程 UI 隐藏，仅后端接口保留。

## 5. Database Operations

支持：

- Create Database
- Rename Database
- Delete Database

字段：

- Database Name
- Database Type

名称规则：2–64 位，仅允许英文字母、数字和下划线。新建和重命名均在前端即时提示，后端再次校验并返回可见错误消息。

类型：

- Normal
- Vector Knowledge Base

## 6. Data Module

### Purpose

管理 JSON 数据。

### Supported Operations

- Create Data
- Edit Data
- Delete Data
- Batch Delete
- Search
- Filter
- Export Current Page as JSON
- Export All Records as JSON

> 普通库显示「新增数据」与 JSON 导出；向量库隐藏这两个入口，向量数据由文档向量化流程生成。
> 单条删除提示确认当前数据；批量删除提示确认所选记录数量。

### Display Modes

#### Table View

适合业务用户。

显示：

- _id
- fields
- actions

#### JSON View

适合开发人员。

展示：

```json
{
  "_id": "001",
  "name": "demo",
  "status": true
}
```

支持：

- Copy
- Edit
- Delete

## 7. JSON Editor

采用代码编辑器模式。

推荐组件：

Monaco Editor

支持：

- Syntax Highlight
- Format
- Validate
- Save
- Cancel

### Save Validation

必须验证：

JSON Parse

失败：

Block Save

显示：

- Error Message
- Error Line

## 8. Document Management Module

Vector Database 专属模块。

### Core Principle

上传文档 ≠ 自动向量化

文档上传后：

仅保存文档

不自动执行：

- Chunk
- Embedding
- Index

## 9. Document Lifecycle

### Document Status

- Uploaded
- Parsed
- Waiting Vectorization
- Vectorizing
- Completed
- Failed

### Status Detail

#### Uploaded

文档已上传。

未解析。

颜色：

Gray

#### Parsed

文档解析完成。

颜色：

Blue

#### Waiting Vectorization

等待用户触发。

颜色：

Orange

#### Vectorizing

向量化处理中。

颜色：

Purple

#### Completed

已完成。

颜色：

Green

#### Failed

失败。

颜色：

Red

## 10. Documents Page

展示：

| Column | Description |
| --- | --- |
| Document Name | 文件名 |
| Type | PDF/DOCX/TXT |
| Size | 文件大小 |
| Upload Time | 上传时间 |
| Status | 当前状态 |
| Chunk Count | Chunk数量 |
| Vector Status | 向量状态 |
| Action | 操作 |

### Supported Operations

- Upload
- Delete
- Rename
- Download
- View Detail
- Start Vectorization
- Retry
- Rebuild Index

文档上传或删除成功后列表立即刷新。存在 `vectorizing` 文档时，每 2 秒轮询一次状态，全部结束后停止轮询。
上传入口仅位于文档管理页工具栏，并排列在状态筛选框右侧；数据库详情标题区不显示上传按钮。删除文档前明确提示会同时删除所有关联分片。

## 11. Upload Document

支持：

- Drag Drop
- Select Files
- Batch Upload

支持格式：

- PDF
- DOCX
- TXT
- Markdown

### Upload Result

完成后：

- Save Document
- Status = Uploaded
- Original File = `db/<db_id>/_upload/<filename>`

不触发向量化。
上传阶段只选择文件，不显示或提交 Chunk Size / Chunk Overlap。

## 12. Vectorization Workflow

用户手动选择：

Documents

然后：

Start Vectorization

### Batch Operation

支持：

- Single Document
- Multiple Documents

### Configuration Dialog

配置项：

#### Embedding Model

例如：

- text-embedding-3-small
- text-embedding-3-large
- bge-large
- gte-large

#### Chunk Size

范围：

100~2000

默认：

500

#### Chunk Overlap

范围：

0~500

默认：

20

约束：

Overlap < Chunk Size

当前配置仅包含 Embedding Model、Chunk Size 与 Chunk Overlap，不提供 Metadata Fields 选择。确认区必须显示已选文档数量和文档名。

### 12.1 Vector Settings

向量库公开「设置」Tab，配置持久化到 `meta.json.vectorConfig`：

- Default Embedding Model / Dimensions
- Default Chunk Size / Chunk Overlap
- Top K
- Similarity Threshold

上传不使用分块配置；开始向量化对话框以库配置作为默认值。检索页同样读取 Top K 与阈值，并使用同一个 Embedding Model 编码查询。切换模型会删除不兼容的旧向量并要求重新向量化文档。

## 13. Chunks Module

> v3.0：该模块已从主流程 UI 隐藏（「分片设置」页签移除）。后端 `/api/databases/{id}/chunks` 接口仍保留。

### Purpose:

查看和管理Chunk

### Chunk Table

列：

| Column | Description |
| --- | --- |
| Chunk ID | 唯一ID |
| Document | 来源文档 |
| Chunk Index | 分片序号 |
| Content | Chunk内容 |
| Tokens | Token数 |
| Embedding Status | 状态 |
| Action | 操作 |

### Supported Actions

- View Chunk
- Delete Chunk
- Re-Embedding
- Export

## 14. Vector Tasks Module

新增模块。

用于任务管理。

### Task Types

- Parse Document
- Vectorization
- Index Rebuild
- Delete Index

### Task Status

- Pending
- Running
- Completed
- Failed
- Cancelled

### Task Table

显示：

| Column | Description |
| --- | --- |
| Task ID | 唯一ID |
| Type | 类型 |
| Target | 目标 |
| Status | 状态 |
| Start Time | 开始时间 |
| End Time | 结束时间 |

### Supported Actions

- View Log
- Retry
- Cancel

## 15. Index Settings Module

> v3.0：该模块已从主流程 UI 隐藏（「索引信息」页签移除）。后端索引相关接口保留但不在界面暴露。

当前模型与检索默认值统一由公开的「设置」Tab 管理；本节仅保留历史索引管理设想。

用于管理向量索引。

显示：

- Embedding Model
- Vector Count
- Dimensions
- Storage Used
- Index Version

支持：

- Rebuild Index
- Delete Index
- Change Model

## 16. Retrieval Testing Module

用于测试向量查询。

### Input Area

输入：

Question

例如：

AgentBase是什么？

### Query Options

显示：

- TopK
- Similarity Threshold（0~1，步进 0.05，默认 0.3）

当前版本只实现向量语义检索，不提供关键词与向量混合的 Hybrid Search。

### Return Result

显示：

- Rank
- Score
- Chunk Content
- Source Document

结果区最多显示 4 张结果卡；超出可视高度时在结果区内部纵向滚动。

## 17. Statistics Module

显示：

- Document Count
- Chunk Count
- Vector Count
- Storage Usage
- Failed Documents
- Failed Tasks

## 18. Search And Filter

支持：

- Field
- Operator
- Value

### Operators

- Equals
- Not Equals
- Contains
- Not Contains
- Greater Than
- Greater Than Equals
- Less Than
- Less Than Equals
- Exists
- Not Exists
- Regex
- Array Contains

### Combination

支持：

- AND
- OR

## 19. Design Style

### Theme：

Modern Developer Platform

参考：

- MongoDB Atlas
- Supabase
- ElasticSearch
- Azure AI Search
- GitHub

### Colors

#### Primary:

#4F46E5

#### Vector:

#7C3AED

#### Success:

#16A34A

#### Danger:

#DC2626

#### Warning:

#F59E0B

### Radius

12px

### Shadow

Soft Shadow

## 20. Future Extension

后续预留模块：

- Tag Management
- Collection Management
- Version History
- Permission Control
- Data Import
- Data Export
- Multi-Tenant
- Audit Log
- Knowledge Graph
- Reranker Settings

## Final Product Goal

```text
Document Management
        ↓
Chunk Management
        ↓
Vectorization Management
        ↓
Retrieval Testing
        ↓
Knowledge Base Operation
```

核心原则：

Document ≠ Chunk ≠ Vector Index

三者独立管理

用户手动触发向量化

所有向量化过程可追踪、可重试、可审计

这版已经是可直接驱动 AI 编码的 PRD + UI 设计规范级文档，后续生成 Vue3 + NaiveUI 或 React Admin 时基本不需要再补充产品定义。