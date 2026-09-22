# MooFile 前端开发任务清单（ui_todo.md）

> 依据：`docs/ui-design.md`（UI 设计书 v1.0）。技术栈：Vue 3.5 + NaiveUI 2.41 + Vite 6 + vue-router + vue-i18n + ECharts。
> 后端：已开发完成（FastAPI，入口 `app.py`，端口 8888），前端通过 `/api` 代理直连真实后端；`web/src/mock/services.ts` 为真实 API 服务层。
> 目录：`web/src/`。完成标准：每阶段 `vite build` 通过，关键页面可在浏览器实际渲染（截图核对）。
> 状态：**v3.2 已完成**。本清单已于 2026-09-22 按真实 API、当前页面结构和三语言实现同步。

## 阶段 A · 工程清理与基础设施

- [x] A1 清理脚手架残留：重写 `main.ts`（按需注册全部 NaiveUI 组件）、`App.vue`（ConfigProvider+Message/Dialog/Notification Provider）、`router/index.js`
- [x] A2 完成 `zh`/`ja`/`en` 三语言；优先级为用户保存选择 > 浏览器语言 > 英文回退，三份词典 key 一致
- [x] A3 设计令牌 `styles/tokens.ts`：色彩/字体/间距/圆角/阴影/动效/Z-index/断点（对应设计书 §3）
- [x] A4 NaiveUI 主题覆盖 `styles/theme.ts`（对应设计书 §11.5）
- [x] A5 常量层 `constants/status.ts`：文档/任务/索引状态色表、12 个筛选操作符枚举、Embedding 模型列表
- [x] A6 `mock/store.ts` 保留响应式状态，`mock/services.ts` 已切换为真实 FastAPI 服务层
- [x] A7 全局样式 `style.css`：reset、滚动条、代码字体、选中态

## 阶段 B · 全局布局（设计书 §4）

- [x] B1 `layouts/AppLayout.vue`：Header 64px + Sidebar 280/64 + Main 三栏
- [x] B2 Header：Logo、实时时钟（v3.0 由"系统状态"改为当前时间动态显示）、刷新按钮、用户菜单（头像下拉）
- [x] B3 Sidebar：新建数据库按钮、搜索框（前端过滤）、数据库列表（类型标签/记录数/大小/相对时间/选中态/hover 操作）、回收站入口徽标（v3.0 已移除底部存储空间卡片）
- [x] B4 Sidebar 折叠/展开 + <1024px 自动折叠

## 阶段 C · 通用业务组件（设计书 §5）

- [x] C1 `StatusTag.vue`：文档/任务/索引 状态→颜色映射胶囊标签
- [x] C2 `TypeTag.vue`：普通表（灰）/ 向量知识库（紫）
- [x] C3 `StatCard.vue`：统计卡（标题/数值/可选图标/可点击跳转）
- [x] C4 `JsonEditor.vue`：textarea + 工具栏（格式化/校验/复制）+ JSON.parse 校验状态条
- [x] C5 `FilterBuilder.vue`：字段+操作符+值条件行、AND/OR、添加条件/分组、查询预览代码块
- [x] C6 `StorageCard.vue`：组件保留供系统页复用，当前侧边栏不显示
- [x] C7 `PageToolbar` 内联组合：筛选 chips（可删除/清空）、分段控件（表格/JSON 视图）

## 阶段 D · 页面（设计书 §6）

- [x] D1 欢迎页 `WelcomeView.vue`（路由 `/`）：空主区欢迎 + 新建按钮 + 3 特性卡
- [x] D2 数据库详情外壳：自定义路由 Tab 下划线与 query 持久化；向量库五个 Tab（文档/数据/检索/统计/设置）；计数和统计卡按类型区分
- [x] D3 数据浏览页：普通库支持当前页/全部 JSON 导出；向量库隐藏导出；单条与批量删除均有确认
- [x] D4 文档管理页：上传入口位于状态筛选右侧；上传/删除后刷新、向量化中每 2 秒轮询并刷新统计、文档删除提示关联片段
- [x] D5 分片 API 与组件能力保留，但主流程不显示独立分片 Tab
- [x] D6 任务页 `db/TasksPage.vue`：类型/状态筛选、任务表格列、进度条实时推进、日志/重试/取消
- [x] D7 索引 API 与模型切换能力保留，但主流程不显示独立索引 Tab
- [x] D8 检索测试页：Question/TopK/Threshold（默认 0.3），移除无后端实现的 Hybrid Search，最多 4 张结果卡并内部滚动
- [x] D9 统计页 `db/StatsPage.vue`：6 统计卡 + ECharts 双轴图（近 7 日上传/向量化）+ 状态环形图
- [x] D10 回收站页 `TrashPage.vue`：表格 + 恢复/彻底删除/清空回收站

## 阶段 E · 对话框与抽屉（设计书 §7）

- [x] E1 新建数据库向导 `NewDatabaseWizardDialog.vue`：3 步（类型选择双卡/名称表单校验/确认摘要）
- [x] E2 JSON 编辑 `JsonEditDialog.vue`：工具栏 + 校验状态条 + 编辑区 + 非法 JSON 阻断保存
- [x] E3 筛选条件 `FilterDialog.vue`：全部/任意逻辑、条件行、添加分组、查询预览、应用筛选
- [x] E4 删除数据库 `DeleteDatabaseDialog.vue`：警示 + 影响清单（动态数字）+ 输入库名校验 + danger 按钮
- [x] E5 上传文档 `UploadDocumentDrawer.vue`：真实 multipart 上传与超限提示；上传阶段不显示或提交分块参数
- [x] E6 向量化配置 `VectorizeConfigDialog.vue`：列出所有选中文档 + 模型/Chunk Size/Overlap；移除未使用的 Metadata Fields
- [x] E7 任务日志 `TaskLogDrawer.vue`：元信息 + 深色日志流（运行中自动追加）
- [x] E8 文档详情 `DocumentDetailDrawer.vue`：元信息 + 预览 + 分片摘要 + 操作
- [x] E9 更换模型 `ModelChangeDialog.vue`：模型选择 + warning Alert + 确认重建索引
- [x] E10 重命名小弹窗（侧栏 hover 重命名）
- [x] E11 新建/重命名名称统一为英文字母、数字、下划线，非法输入显示行内与消息提示
- [x] E12 Header 帮助按钮按当前语言渲染 `README.md` / `README_ZH.md` / `README_JP.md`
- [x] E13 向量设置页保存模型、Chunk、Overlap、Top K 与阈值，模型变化显示重建风险

## 阶段 F · 联调与验收

- [x] F1 `npm run build` 与 `npx vue-tsc --noEmit` 通过（仅保留既有 chunk-size warning）
- [x] F2 浏览器核对：欢迎页、普通库、向量库、文档、检索、统计、任务、回收站及弹窗可渲染
- [x] F3 交互走查：Tab 下划线/持久化、上传刷新、状态轮询、下载、JSON 导出、任务进度均已验证
- [x] F4 状态色映射与设计书 §8 逐项一致；空态/加载态/错误 message 正常
- [x] F5 三语言自动检测、运行时切换与刷新后持久化已用浏览器验证
- [x] F6 完成 `README.md`、`README_ZH.md`、`README_JP.md` 与 docs 同步

## 完成定义（Definition of Done）

1. 全部 A–E 项勾选；
2. `npm run build` 通过且 `npm run dev` 可直接打开首页；
3. 关键交互链路（D3/F3）在浏览器实测走通；
4. 视觉与 `docs/imgs/Designer.png` 原型、`ui-design.md` §3 令牌一致（主色 #4F46E5、圆角 12px、Header 64px/Sidebar 280px）。

## 验收记录

- 构建：`npm run build` 通过；`npx vue-tsc --noEmit` 零错误；Vite 仅提示既有大分包 warning
- dev server：`npm run dev`（端口以 Vite 输出为准）
- 已验证页面：
  - 欢迎页 `/`：Header/可滚动 Sidebar/三语言切换
  - 普通库：记录数/字段数/默认索引/大小/更新时间，单数据 Tab，新增与 JSON 导出
  - 向量库：文档数/记录数/配置维度/大小/更新时间，文档/数据/检索/统计/设置 5 Tab
  - 文档管理：状态轮询、下载、上传与向量化联动
  - 检索测试：Question/TopK/Threshold 0.3 + 最多 4 张可滚动结果卡，无 Hybrid
  - 统计信息：6 统计卡 + ECharts 柱状图 + 环形图
  - 任务中心 `/tasks`：5 任务/状态色/进度条/筛选
  - 回收站 `/trash`：2 条已删除数据库/恢复/彻底删除
- 已修复 bug：
  1. `v-model:visible` 不能用表达式（MFSidebar renameTarget/deleteTarget）→ 改为独立 ref
  2. dialogs 下 `../../` 路径错误 → 改为 `../`
  3. 同路由不同 dbId 子组件复用不刷新 → 加 `:key`
  4. n-modal/n-drawer 关闭事件不触发 → 补 `@update:show` 转发
  5. trash 初始为空但 badge 硬编码 2 → 种子 2 条 + badge 改动态
  6. TasksPage/RetrievalPage 未挂路由 → tasks 加全局路由，retrieval 加 Tab
  7. 任务表行变量遮蔽 i18n `t` → 重命名行参数并通过类型检查
  8. 静态中文文案 → 全量迁移为 zh/ja/en locale key
