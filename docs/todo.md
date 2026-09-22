# MooFile 前端开发任务清单（todo.md）

> 依据：`docs/ui-design.md`（UI 设计书 v1.0）。技术栈：Vue 3.5 + NaiveUI 2.41 + Vite 6 + vue-router + vue-i18n + ECharts。
> 后端：已开发完成（FastAPI，入口 `app.py`，端口 8888），前端通过 `/api` 代理直连真实后端；`web/src/mock/services.ts` 为真实 API 服务层。
> 目录：`web/src/`。完成标准：每阶段 `vite build` 通过，关键页面可在浏览器实际渲染（截图核对）。
> v3.0 UI 调整：① 移除左下角存储空间卡片；② 移除数据库"分片设置""索引信息"页签；③ 顶栏"服务器状态"改为实时时钟；④ 移除统计卡"索引状态"；向量维度修正为真实模型 384。

## 阶段 A · 工程清理与基础设施

- [x] A1 清理脚手架残留：重写 `main.ts`（按需注册全部 NaiveUI 组件）、`App.vue`（ConfigProvider+Message/Dialog/Notification Provider）、`router/index.js`
- [x] A2 重写 i18n 语言包：`public/locales/zh.json`（完整中文文案）、`en.json`（英文回退），默认 locale 中文
- [x] A3 设计令牌 `styles/tokens.ts`：色彩/字体/间距/圆角/阴影/动效/Z-index/断点（对应设计书 §3）
- [x] A4 NaiveUI 主题覆盖 `styles/theme.ts`（对应设计书 §11.5）
- [x] A5 常量层 `constants/status.ts`：文档/任务/索引状态色表、12 个筛选操作符枚举、Embedding 模型列表
- [x] A6 Mock 数据层 `mock/`：内存库（数据库列表/记录/文档/分片/任务/存储配额）+ 模拟 API 函数 + 任务进度定时器
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
- [x] C6 `StorageCard.vue`：存储空间进度卡
- [x] C7 `PageToolbar` 内联组合：筛选 chips（可删除/清空）、分段控件（表格/JSON 视图）

## 阶段 D · 页面（设计书 §6）

- [x] D1 欢迎页 `WelcomeView.vue`（路由 `/`）：空主区欢迎 + 新建按钮 + 3 特性卡
- [x] D2 数据库详情外壳 `db/DatabaseDetailShell.vue`：标题行（名称+类型+上传/新增/重命名/删除）、6 张统计卡、模块 Tabs（路由同步 `?tab=`）
- [x] D3 数据浏览页 `db/DataBrowsePage.vue`：工具条（筛选徽标/字段筛选/搜索/重置/导出/视图切换）、chips、MFTable 列（_id/source/page/chunk_index/content/tokens/embedding/status/操作）、JSON 视图、分页、批量删除
- [x] D4 文档管理页 `db/DocumentsPage.vue`：工具条（上传/搜索/状态筛选/批量操作）、文档表格列、行操作（详情/下载/向量化/重命名/删除）、状态只读联动
- [x] D5 分片页 `db/ChunksPage.vue`：按文档筛选、Chunk 表格列、查看/重新 Embedding/删除、关键字高亮
- [x] D6 任务页 `db/TasksPage.vue`：类型/状态筛选、任务表格列、进度条实时推进、日志/重试/取消
- [x] D7 索引设置页 `db/IndexSettingsPage.vue`：模型/向量数/维度/存储/版本信息卡 + 重建/删除/更换模型操作
- [x] D8 检索测试页 `db/RetrievalPage.vue`：左栏配置（Question/TopK Slider/Threshold Slider/Hybrid Switch）+ 右栏结果列表（排名/分数/分数条/命中高亮/来源）
- [x] D9 统计页 `db/StatsPage.vue`：6 统计卡 + ECharts 双轴图（近 7 日上传/向量化）+ 状态环形图
- [x] D10 回收站页 `TrashPage.vue`：表格 + 恢复/彻底删除/清空回收站

## 阶段 E · 对话框与抽屉（设计书 §7）

- [x] E1 新建数据库向导 `NewDatabaseWizardDialog.vue`：3 步（类型选择双卡/名称表单校验/确认摘要）
- [x] E2 JSON 编辑 `JsonEditDialog.vue`：工具栏 + 校验状态条 + 编辑区 + 非法 JSON 阻断保存
- [x] E3 筛选条件 `FilterDialog.vue`：全部/任意逻辑、条件行、添加分组、查询预览、应用筛选
- [x] E4 删除数据库 `DeleteDatabaseDialog.vue`：警示 + 影响清单（动态数字）+ 输入库名校验 + danger 按钮
- [x] E5 上传文档 `UploadDocumentDrawer.vue`：拖拽区 + 已选文件列表（进度/超限提示）+ 分片设置（100~2000/0~500，Overlap<Chunk 校验）+ 开始上传（模拟并发进度）
- [x] E6 向量化配置 `VectorizeConfigDialog.vue`：选中文档摘要 + 模型/Chunk Size/Overlap/Metadata 多选 + 创建任务
- [x] E7 任务日志 `TaskLogDrawer.vue`：元信息 + 深色日志流（运行中自动追加）
- [x] E8 文档详情 `DocumentDetailDrawer.vue`：元信息 + 预览 + 分片摘要 + 操作
- [x] E9 更换模型 `ModelChangeDialog.vue`：模型选择 + warning Alert + 确认重建索引
- [x] E10 重命名小弹窗（侧栏 hover 重命名）

## 阶段 F · 联调与验收

- [x] F1 `npm run build`（vite build）零错误通过（✓ built in 7.47s）
- [x] F2 启动 dev server，截图逐页核对：欢迎页/普通库详情/向量库详情/文档管理/分片/索引/检索/统计/任务中心/回收站均渲染正常
- [x] F3 交互走查：JSON 弹窗开关、状态色、Tab 切换、路由同步、任务进度定时器均已验证
- [x] F4 状态色映射与设计书 §8 逐项一致；空态/加载态/错误 message 正常
- [x] F5 完成 todo.md 全部勾选，更新本文档状态

## 完成定义（Definition of Done）

1. 全部 A–E 项勾选；
2. `npm run build` 通过且 `npm run dev` 可直接打开首页；
3. 关键交互链路（D3/F3）在浏览器实测走通；
4. 视觉与 `docs/imgs/Designer.png` 原型、`ui-design.md` §3 令牌一致（主色 #4F46E5、圆角 12px、Header 64px/Sidebar 280px）。

## 验收记录

- 构建：`npm run build` ✓ built in 7.47s（PowerShell 把 chunk-size warning 当 exit 1，非真实错误）
- dev server：`npm run dev` → http://localhost:5173/
- 已验证页面：
  - 欢迎页 `/`：Header/Sidebar/6 数据库/存储卡 18%
  - 普通库 product_catalog：6 统计卡/3 Tab/数据表格
  - 向量库 support_knowledge：6 统计卡（含向量维度 1536 dims）/6 Tab/向量记录 64f8a2c1a9b
  - 文档管理：8 文档/状态色（已完成绿/已解析蓝/已上传灰/待向量化橙/失败红/向量化中紫）/文件类型图标
  - 分片设置：chunk 列表/按文档筛选/分页
  - 索引信息：模型/向量数/维度/存储/版本 + 重建/删除/更换模型
  - 检索测试：Question/TopK/Threshold/Hybrid + 结果面板
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
