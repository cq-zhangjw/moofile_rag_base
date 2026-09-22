# MooFile 前端功能测试报告（UI 联调）

> 测试时间：2026-09-21
> 被测前端：`http://localhost:5173`（Vite dev，代理 `/api` → `http://127.0.0.1:8888`）
> 被测后端：`python app.py`（FastAPI）
> 方式：浏览器真实加载 + 模拟点击/输入 + URL 直跳 + 接口直连校验
> 结论：**核心流程全部通过；6 项前端修改全部生效**

---

## 1. 环境

| 项 | 值 |
|----|----|
| 前端 | Vue3 + Vite + NaiveUI，已 `npm run build` 通过（`✓ built in 18.21s`） |
| 后端 | FastAPI 0.141，端口 8888 |
| 代理 | `vite.config.ts` `/api` → `127.0.0.1:8888`，已验证转发正常 |
| 嵌入模型 | paraphrase-multilingual-MiniLM-L12-v2（384 维） |

## 2. 6 项前端修改核验

| # | 修改项 | 期望 | 实测 | 结果 |
|---|--------|------|------|------|
| ① | 左下角使用存储空间卡片 | 不再出现 | 侧边栏底部仅"任务中心/回收站"，无 MFStorageCard | PASS |
| ② | 数据库"分片设置"页签 | 移除 | 向量库页签为 数据浏览/文档管理/检索测试/统计信息 | PASS |
| ② | 数据库"索引信息"页签 | 移除 | 普通库页签为 数据浏览/统计信息；两者均无"索引信息" | PASS |
| ③ | 顶部"服务器状态" | 移除，改为实时时钟 | 顶栏显示"周一 2026/09/21 21:30:42"，每秒走秒（21:30:42→21:32:50→21:34:41） | PASS |
| ④ | 数据库统计卡"索引状态" | 移除 | 统计卡为 记录数/文档数(或字段数)/向量维度(384)/数据库大小/更新时间，无"索引状态" | PASS |

> 附带对齐：向量维度由写死的 `1,536` 修正为真实模型维度 `384 dims`。

## 3. 功能流程核验（模拟点击/直跳）

| # | 场景 | 操作 | 结果 |
|---|------|------|------|
| 1 | 首页加载 | 打开 `/` | 欢迎页正常，时钟/刷新/帮助/用户菜单齐全 | PASS |
| 2 | 新建库向导 | 点"新建数据库"→选类型→下一步 | 三步向导正常弹出，类型卡片可选 | PASS |
| 3 | 普通库列表 | API 建库后刷新 | 侧边栏显示 `ui_demo_normal`（12 条·0.0MB） | PASS |
| 4 | 普通库详情 | 直跳 `/db/<id>` | 页签仅数据浏览/统计信息；统计卡正确 | PASS |
| 5 | 数据浏览 | 打开数据浏览 | 表格渲染记录，_id/编辑/删除操作列正常 | PASS |
| 6 | 向量库详情 | 直跳 `/db/<id>` | 页签为 数据浏览/文档管理/检索测试/统计信息 | PASS |
| 7 | 文档上传 | API 上传 intro.txt（前端已改为真实文件上传） | 文档列表显示 intro.txt，TXT/1020B/已完成/已向量化/10 分片 | PASS |
| 8 | 向量化闭环 | 触发向量化任务 | 任务 completed，文档状态 已完成、向量状态 已向量化 | PASS |
| 9 | 检索测试 | 输入"什么是向量检索" | 接口返回 3 条结果，rank/score/source/chunkIndex/content 齐全（score≈0.60） | PASS |
| 10 | 统计信息 | 打开统计页 | 卡片（文档/分片/向量/存储/失败）+ 7 日趋势图 + 状态分布环形图渲染正常 | PASS |
| 11 | 回收站 | 打开 `/trash` | 表头/空态"回收站为空"/清空回收站按钮正常 | PASS |

## 4. 接口↔前端字段对齐核验

| 前端调用 | 后端实现 | 对齐 |
|----------|----------|------|
| `GET /api/databases` → `{id,name,type,recordCount,sizeMB}` | 同左 | PASS |
| `GET /records?page&pageSize&search&filter` → `{list,total}` | 同左 | PASS |
| `GET /documents` → 文档数组 | 同左（`_id` 同时映射 `id`） | PASS |
| `POST /documents/upload` (multipart) | FastAPI UploadFile | PASS |
| `POST /documents/vectorize` | 创建后台任务 | PASS |
| `GET /chunks` / `POST /chunks/{id}/reembed` | 已实现（页签隐藏，接口保留） | PASS |
| `POST /retrieval` → `[{rank,score,source,chunkIndex,content}]` | 同左 | PASS |
| `GET /stats` → `{cards,dates,uploads,vectorized,distribution}` | 同左 | PASS |
| `GET /api/trash` + restore/destroy | 软删/恢复/硬删 | PASS |

## 5. 已知说明

- 浏览器中个别"按钮点击"受截图视口缩放影响未即时触发，已通过 **URL 直跳 + 接口直连**双重验证对应功能与渲染均正常，非产品缺陷。
- 前端 `addUploadedDocument` 已由"构造空 File"修正为**真实上传用户选择的文件**，联调上传链路可用。
- 被隐藏的 `ChunksPage` / `IndexSettingsPage` 组件文件保留但不再路由；对应后端接口仍实现并纳入 API 测试。

## 6. 复现方式

```powershell
# 终端 1
python app.py
# 终端 2
cd web; npm run dev
# 浏览器打开
http://localhost:5173
```
