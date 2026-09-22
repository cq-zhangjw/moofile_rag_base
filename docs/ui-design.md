# MooFile 前端 UI 设计书（ui-design.md）

> 本文件是 MooFile 数据库管理平台的前端 UI 设计书（Design Specification），粒度到**组件级**：每一个组件的名称、参数（Props）、布局、配色、状态、使用场景与对应 NaiveUI 映射，供前端开发直接参照实现。

| 项目 | 内容 |
| --- | --- |
| 版本 | 1.1 |
| 日期 | 2026-09-22 |
| 状态 | 已实现同步稿 |
| 关联文档 | `docs/moofile-database-management-design.md`（产品需求 / 信息架构，简称 PRD） |
| 参考原型 | `docs/imgs/Designer.png`（高保真原型截图） |
| 目标技术栈 | Vue 3.5 + TypeScript + Vite 6 + NaiveUI 2.41 + Vue Router 4 + Vue I18n 9 + ECharts 5 + @vicons/ionicons5 + Axios |
| 默认浏览器 | Chrome / Edge 最新版，桌面端优先（最低支持宽度 1280px） |

---

## 1. 阅读指南

### 1.1 本设计书能回答的问题

- 这个页面有哪些组件？分别叫什么名字、长什么样、摆在哪？
- 每个组件接受哪些参数、触发哪些事件、有哪几种状态和配色？
- 布局尺寸是多少 px？间距、圆角、阴影、字体字号是多少？
- 每个状态（文档状态 / 任务状态 / 索引状态）用什么颜色和文案？
- 弹窗、抽屉、向导分别怎么打开、怎么关闭、内部结构如何？
- 开发时如何覆盖 NaiveUI 主题、如何组织路由与 i18n？

### 1.2 组件命名约定

- 业务组件统一前缀 `MF`（MooFile）：如 `MFButton`、`MFTable`、`MFStatCard`。
- 页面级容器组件以 `Page` 结尾：如 `DataBrowsePage`。
- 对话框 / 抽屉组件以 `Dialog` / `Drawer` 结尾：如 `JsonEditDialog`、`UploadDocumentDrawer`。
- 每个业务组件给出：**说明 / NaiveUI 映射 / Props / Slots / 事件 / 尺寸 / 配色 / 布局 / 使用场景 / 示例**。未标注 Slots 表示不开放插槽。

### 1.3 配色表约定

各组件配色表中颜色分为四类，统一命名：

- **主色（solid）**：填充色，白字。
- **Hover**：悬停填充色。
- **浅底（soft）**：浅色背景 + 同色系深字，用于标签、状态、选中态。
- **描边（outline）**：边框色。

### 1.4 与 PRD 的对应关系

| PRD 章节 | 本设计书章节 |
| --- | --- |
| 4 全局布局 | §4 全局布局框架 |
| 5 数据库操作 | §6.1 数据库首页 / §7.1 新建数据库向导 |
| 6 数据模块 | §6.3 数据浏览页 / §7.2 JSON 编辑对话框 / §7.3 筛选条件对话框 |
| 7 JSON Editor | §7.2 + §5.10 MFJsonEditor |
| 9-11 文档生命周期 | §6.4 文档管理页 / §8.1 状态机 |
| 12 向量化工作流 | §7.6 向量化配置对话框 |
| 13 Chunks | §6.5 分片设置页 |
| 14 向量任务 | §6.6 向量任务页 / §7.7 任务日志抽屉 |
| 15 索引设置 | §6.7 索引设置页 |
| 16 检索测试 | §6.8 检索测试页 |
| 17 统计 | §6.9 统计页 |
| 18 搜索与筛选 | §5.9 MFFilterBuilder + §7.3 |
| 19 设计风格 | §3 设计令牌 |

---

## 2. 设计原则

1. **开发者向**：信息密度高、快捷键可用、批量操作完备、状态可追踪（符合 MongoDB Atlas / Supabase / ElasticSearch 的交互心智）。
2. **简洁现代**：大面积留白、12px 圆角、柔和阴影、克制用色；主色只用于主操作与选中态，状态色只用于状态表达。
3. **一致性**：所有尺寸、颜色、圆角、字号来自 §3 设计令牌，禁止在页面内硬编码散值。
4. **明确反馈**：所有异步操作必须有 loading / 进度 / 成功 / 失败反馈；破坏性操作必须二次确认（见 §7.4）。
5. **文档 ≠ Chunk ≠ 向量索引**：三类对象在界面中独立管理、独立状态、手动触发向量化（PRD 核心原则，UI 上体现为「上传仅入库」「向量化需显式触发」两条交互铁律）。

### 2.1 两条交互铁律（必须遵守）

- **铁律一**：上传文档后，文档状态为 `Uploaded`（灰色），**绝不自动**进入向量化；只有用户勾选后点击「开始向量化」才进入 `Waiting Vectorization`。
- **铁律二**：所有删除操作（记录 / 文档 / Chunk / 索引 / 数据库）必须弹确认框；删除数据库还必须输入库名（见 §7.4）。

---

## 3. 设计令牌（Design Tokens）

> 全局唯一数据源，实现为 `src/styles/tokens.ts` + NaiveUI `themeOverrides`（代码见 §11.5）。

### 3.1 色彩系统

#### 3.1.1 功能色（Functional Colors）

| 令牌 | 名称 | 值 | Hover | Active/Pressed | 浅底(soft) | 描边(outline) | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `--mf-primary` | 主色 Indigo | `#4F46E5` | `#4338CA` | `#3730A3` | `#EEF2FF` | `#C7D2FE` | 主按钮、选中态、链接、焦点环、Logo |
| `--mf-vector` | 向量紫 | `#7C3AED` | `#6D28D9` | `#5B21B6` | `#F5F3FF` | `#DDD6FE` | 向量知识库类型、向量化相关状态 |
| `--mf-success` | 成功绿 | `#16A34A` | `#15803D` | `#166534` | `#F0FDF4` | `#BBF7D0` | 完成态、成功提示 |
| `--mf-danger` | 危险红 | `#DC2626` | `#B91C1C` | `#991B1B` | `#FEF2F2` | `#FECACA` | 删除、失败态、错误提示 |
| `--mf-warning` | 警告橙 | `#F59E0B` | `#D97706` | `#B45309` | `#FFFBEB` | `#FDE68A` | 待处理、警告提示 |
| `--mf-info` | 信息蓝 | `#2563EB` | `#1D4ED8` | `#1E40AF` | `#EFF6FF` | `#BFDBFE` | 已解析、运行中、信息提示 |
| `--mf-neutral` | 中性灰 | `#6B7280` | `#4B5563` | `#374151` | `#F3F4F6` | `#E5E7EB` | 已上传、暂停、取消、未构建 |

#### 3.1.2 文本色（Text Colors）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--mf-text-1` | `#111827` | 页面标题、表格主文本、弹窗标题（强调度最高） |
| `--mf-text-2` | `#374151` | 正文、表格单元格默认色 |
| `--mf-text-3` | `#6B7280` | 次级说明、标签说明、时间、次要数据 |
| `--mf-text-4` | `#9CA3AF` | 占位符、禁用文案、弱信息 |
| `--mf-text-disabled` | `#D1D5DB` | 禁用控件文字 |

#### 3.1.3 边框与背景（Border & Background）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--mf-border` | `#E5E7EB` | 默认边框、表格分隔线、卡片描边 |
| `--mf-border-strong` | `#D1D5DB` | 输入框 hover、分割强调 |
| `--mf-bg-page` | `#F9FAFB` | 全局页面底色（Main 区域） |
| `--mf-bg-card` | `#FFFFFF` | 卡片、表格、弹窗、抽屉、侧边栏背景 |
| `--mf-bg-hover` | `#F3F4F6` | 行 hover、菜单项 hover、按钮 ghost hover |
| `--mf-bg-selected` | `#EEF2FF` | 表格行选中、侧边栏数据库选中、Tab 选中 |
| `--mf-bg-header` | `#FFFFFF` | Header 背景 |
| `--mf-mask` | `rgba(17,24,39,0.45)` | 弹窗遮罩 |

### 3.2 字体系统

| 令牌 | 值 |
| --- | --- |
| 字体栈（默认） | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif` |
| 字体栈（代码） | `"JetBrains Mono", "Fira Code", Consolas, "Courier New", monospace` |
| 数字（统计卡） | 同代码字体，`font-variant-numeric: tabular-nums` |

字号阶梯（`--mf-fs-*`）：

| 令牌 | 值 | 使用场景 |
| --- | --- | --- |
| `--mf-fs-12` | 12px | 辅助说明、表格内 tag、时间戳、代码块小字 |
| `--mf-fs-13` | 13px | 表格单元格、表单 label、下拉项 |
| `--mf-fs-14` | 14px | 正文默认、按钮文字、输入框文字 |
| `--mf-fs-15` | 15px | 卡片标题、Tab 文字（默认 14，选中加粗） |
| `--mf-fs-16` | 16px | 页面区块标题、侧边栏数据库名 |
| `--mf-fs-18` | 18px | 统计卡数值、对话框标题 |
| `--mf-fs-20` | 20px | 页面主标题（数据库名） |
| `--mf-fs-24` | 24px | 极少用（欢迎页） |

行高：正文 `1.5`；表格 `1.4`；代码块 `1.6`。字重：常规 `400`，强调 `500`，标题 `600`，数值 `600`。

### 3.3 间距与尺寸（4pt 网格）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--mf-space-1` | 4px | 图标与文字间距、tag 内边距 |
| `--mf-space-2` | 8px | 紧凑内边距、chips 间距 |
| `--mf-space-3` | 12px | 表格单元格 padding、工具条间距 |
| `--mf-space-4` | 16px | 卡片内边距、表单行距 |
| `--mf-space-5` | 20px | 弹窗内容边距、区块间距 |
| `--mf-space-6` | 24px | 页面内容 padding、主区块间距 |
| `--mf-space-7` | 32px | 大区块间距 |
| `--mf-space-8` | 40px+ | 页面级留白 |

组件高度阶梯（与 NaiveUI size 对齐）：

| 尺寸 | 高度 | 使用场景 |
| --- | --- | --- |
| `tiny` | 24px | 表格内小操作、tag 高度 |
| `small` | 28px | 紧凑工具栏 |
| `medium`（默认） | 32px | 常规按钮 / 输入框 / 选择器 |
| `large` | 36px | 主操作按钮（新建数据库、上传文档） |
| `xlarge` | 40px | 页面级主按钮、大搜索框 |

### 3.4 圆角（Radius）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--mf-radius-sm` | 6px | 小按钮、tag、输入框、select |
| `--mf-radius-md` | 8px | 默认按钮、卡片、表格行内控件 |
| `--mf-radius-lg` | 12px | **默认卡片圆角**、弹窗、抽屉、统计卡、上传拖拽区 |
| `--mf-radius-xl` | 16px | 大卡片、向导步骤卡片 |
| `--mf-radius-full` | 999px | 胶囊标签、头像、进度圆点 |

### 3.5 阴影（Shadow）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--mf-shadow-none` | `none` | 默认 |
| `--mf-shadow-sm` | `0 1px 2px rgba(17,24,39,0.05)` | 卡片默认、表格头 |
| `--mf-shadow-md` | `0 4px 6px -1px rgba(17,24,39,0.07), 0 2px 4px -2px rgba(17,24,39,0.05)` | 悬浮卡片、下拉面板 |
| `--mf-shadow-lg` | `0 10px 15px -3px rgba(17,24,39,0.08), 0 4px 6px -4px rgba(17,24,39,0.04)` | 弹窗、抽屉 |
| `--mf-shadow-xl` | `0 20px 25px -5px rgba(17,24,39,0.10), 0 8px 10px -6px rgba(17,24,39,0.05)` | 通知、悬浮提示 |

### 3.6 动效（Motion）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--mf-dur-fast` | 100ms | hover、active、按压反馈 |
| `--mf-dur-base` | 200ms | 颜色过渡、表格行 hover、Tab 切换 |
| `--mf-dur-slow` | 300ms | 弹窗 / 抽屉 / 下拉展开收起 |
| 缓动 | `cubic-bezier(0.4, 0, 0.2, 1)` | 全部过渡 |
| 进度条 | 线性 `ease-out` | 上传 / 向量化进度 |

### 3.7 Z-index 层级

| 层级 | 值 | 元素 |
| --- | --- | --- |
| sticky | 100 | Header、表格吸顶列 |
| dropdown/popover | 1000 | 下拉、Tooltip、Popover |
| overlay | 1200 | 遮罩层 |
| modal | 1300 | 对话框 |
| message | 1400 | 全局消息 |
| drawer | 1500 | 抽屉 |
| notification | 1600 | 通知 |

### 3.8 响应式断点

| 断点 | 宽度 | 行为 |
| --- | --- | --- |
| desktop（主目标） | ≥ 1280px | 完整布局：侧边栏 280px + 主区 |
| narrow desktop | 1024–1279px | 侧边栏收窄至 240px；统计卡 3 列 |
| tablet | 768–1023px | 侧边栏折叠为图标栏（64px）；统计卡 2 列 |
| mobile | < 768px | 侧边栏变抽屉（Drawer 从左侧滑出）；表格横向滚动 |

---

## 4. 全局布局框架（AppLayout）

### 4.1 布局总览（ASCII 线框）

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Header  (64px, 白底, 底部 1px 边框)                                        │
│  [MooFile logo]                   [本地时间] [刷新] [语言] [Admin ▾]      │
├───────────────┬──────────────────────────────────────────────────────────┤
│ Sidebar       │ Main (bg #F9FAFB, padding 24px)                          │
│ 280px / 64px  │  ┌────────────────────────────────────────────────────┐  │
│ [＋新建数据库] │  │ 页面内容（按路由切换）                                │  │
│ [搜索数据库…] │  │  DataBrowsePage / DocumentsPage / RetrievalPage     │  │
│ 数据库列表     │  │  StatsPage / TasksPage / TrashPage                 │  │
│  ├ 普通库…     │  │                                                    │  │
│  ├ 向量库…     │  └────────────────────────────────────────────────────┘  │
│ 回收站         │                                                          │
│                │                                                          │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### 4.2 Header（`MFHeader`）

| 项 | 规格 |
| --- | --- |
| 说明 | 全局顶栏，全路由固定，粘性置顶 |
| 布局 | Flex：左 = Logo 区（宽 280px，与侧边栏同步折叠），中 = 弹性留白，右 = 本地化实时时钟 + 刷新 + 帮助 + 语言 + 用户 |
| 高度 | 64px（固定） |
| 内边距 | 左右 24px（折叠时左 16px） |
| 背景 / 边框 | `#FFFFFF` / 底边 `1px solid #E5E7EB` |
| 阴影 | `--mf-shadow-sm` |
| Z-index | 100（sticky） |

子组件明细：

| 子组件 | 名称 | 规格 |
| --- | --- | --- |
| `MFLogo` | Logo + 产品名 | 左侧；图标 28×28，主色圆角 8px 底 + 白色「M」字形；文字「MooFile」16px/600/`#111827`，与图标间距 10px |
| `MFClock` | 实时时钟 | 使用当前 locale 格式化日期、星期与时间，每秒更新 |
| `MFIconButton(刷新)` | 刷新按钮 | 图标按钮 `Refresh`（ionicons5），32×32，图标 16px/`#374151`；hover 背景 `#F3F4F6` 旋转 180° 过渡；点击触发当前路由页数据刷新并显示全局 loading |
| `MFIconButton(帮助)` | 帮助按钮 | 打开 Markdown 弹窗；按当前界面语言加载根目录 `README_ZH.md`、`README_JP.md` 或 `README.md`，每次打开重新获取内容 |
| `MFLanguageSelector` | 语言选择 | `中文 / 日本語 / English`；切换后立即更新页面并保存到 `moofile.locale` |
| `MFUserMenu` | 用户菜单 | 头像（`n-avatar` 圆形 30px，首字母，背景主色渐变）+ 用户名「Admin」13px；下拉 `n-dropdown`：账号设置 / 退出登录 |

### 4.3 Sidebar（`MFSidebar`）

| 项 | 规格 |
| --- | --- |
| 说明 | 数据库导航侧栏，展示数据库列表和回收站 |
| 宽度 | 展开 280px / 折叠 64px（<1024px 自动折叠，可手动切换） |
| 背景 / 边框 | `#FFFFFF` / 右边框 `1px solid #E5E7EB` |
| 内边距 | 16px 12px；容器设置 `min-height: 0`，数据库列表内部 `overflow-y: auto`，保证长列表可滚动 |
| 切换动画 | 宽度 200ms 过渡 |

自上而下区块（间距 24px）：

#### 4.3.1 新建数据库按钮（`MFButton` 变体）

| 项 | 规格 |
| --- | --- |
| 说明 | 打开新建数据库向导（§7.1） |
| 样式 | 主色填充、`large`（36px）、圆角 `--mf-radius-md`、全宽、前置 `Add` 图标 16px |
| 文案 | 「＋ 新建数据库」，14px/500/白字 |
| 折叠态 | 只显示图标，居中 |
| 触发 | 打开 `NewDatabaseWizardDialog` |

#### 4.3.2 搜索数据库（`MFInput` 变体）

| 项 | 规格 |
| --- | --- |
| 说明 | 过滤数据库列表（前端即时过滤，不请求接口） |
| NaiveUI | `n-input`，size `medium`，prefix 搜索图标，clearable |
| 占位符 | 「搜索数据库...」13px/`#9CA3AF` |
| 背景 | `#F9FAFB`（浅灰底，区别于白卡片），focus 白底 + 主色描边 |
| 空结果 | 列表区显示 `MFEmpty`「未找到匹配的数据库」（高度 120px） |

#### 4.3.3 数据库列表（`MFDatabaseList`）

| 项 | 规格 |
| --- | --- |
| 区块标题 | 「数据库列表」12px/`#6B7280`/500，上方留白 16px |
| 数据项 | 每个数据库一行，高 56px，圆角 `--mf-radius-md`，内边距 8px 12px |
| 悬停态 | 背景 `#F3F4F6`；右侧浮现操作按钮（重命名 / 删除 图标） |
| 选中态 | 背景 `#EEF2FF`（主色浅底）+ 左侧 3px 主色竖条（绝对定位，圆角） |

数据库项内部结构（左→右）：

```text
┌──────────────────────────────────────────────┐
│ 名称                [普通表|向量知识库]        │
│ 1,245条 · 2.4 MB          2分钟前  [⋮]        │
└──────────────────────────────────────────────┘
```

| 字段 | 规格 |
| --- | --- |
| 名称 | 14px/500/`#111827`，超长省略（单行 `ellipsis`） |
| 类型标签 | `MFTypeTag`：普通表 = 中性灰 tag；向量知识库 = 向量紫 tag（§5.2） |
| 记录数 · 大小 | 13px/`#6B7280`，如「1,245条 · 2.4 MB」 |
| 更新时间 | 12px/`#9CA3AF`，相对时间（2分钟前 / 1小时前 / 昨天 / 2天前）；>7 天显示绝对时间 |
| 更多操作 | 悬停显示 `⋮`（`n-dropdown`）：重命名 / 删除（普通库）/ 移入回收站（向量库） |
| 点击行为 | 跳转 `/db/:id`（默认打开该库的「数据浏览」Tab） |

排序规则：默认按更新时间倒序（最新在上）；普通库与向量库混排（不做分组，用类型标签区分）。

#### 4.3.4 回收站入口（`MFTrashEntry`）

| 项 | 规格 |
| --- | --- |
| 说明 | 进入回收站页面（§6.10） |
| 样式 | 图标 `TrashBinOutline` + 「回收站」14px/`#374151`，行高 40px，hover 背景 `#F3F4F6` |
| 徽标 | 右侧 `n-badge`：回收站内数据库数量，主色小圆点 + 数字（>99 显示 99+） |

#### 4.3.5 存储空间卡片（`MFStorageCard`）

> 当前侧边栏不显示该卡片。组件与 `/api/system/storage` 保留供未来系统页复用。

| 项 | 规格 |
| --- | --- |
| 说明 | 展示配额用量与占比 |
| 容器 | 白卡片，圆角 `--mf-radius-lg`，阴影 `--mf-shadow-sm`，内边距 12px 16px |
| 第一行 | 「存储空间」12px/`#6B7280`/500 |
| 第二行 | 「914 MB / 5 GB」13px/`#374151`/500 |
| 进度条 | `n-progress` line，高度 6px，圆角 3px，百分比 17%，已完成段主色 `#4F46E5`，轨迹 `#E5E7EB` |
| 第三行 | 「17%」12px/`#6B7280`；>90% 时进度条与文字变警告色 `#F59E0B` |

### 4.4 Main 区域（`MFMain`）

| 项 | 规格 |
| --- | --- |
| 容器 | `n-layout-content`，背景 `#F9FAFB`，内边距 24px（<1024px 时 16px） |
| 内容 | 按路由渲染页面组件（路由表见 §11.4），页面切换使用 `<transition fade 200ms>` |
| 滚动 | 主区独立滚动（Header / Sidebar 固定） |
| 空状态 | 未选择数据库时显示欢迎页（§6.1.2） |

---

## 5. 通用组件规范（组件库）

> 以下为全局复用的基础组件。所有组件均以 NaiveUI 为基础封装，统一主题（§11.5），业务上禁止绕过封装直接裸用 NaiveUI 组件（保证风格收敛）。

### 5.1 MFButton（按钮）

| 项 | 规格 |
| --- | --- |
| 说明 | 全局按钮，封装 `n-button`，统一样式与图标规则 |
| NaiveUI 映射 | `n-button`（`color`/`text-color`/`border-radius` 由主题覆盖） |

Props：

| Prop | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'danger' \| 'danger-ghost'` | `'secondary'` | primary=主色实心；secondary=白底描边；ghost=透明无边框（hover 灰底）；danger=红色实心；danger-ghost=白底红描边 |
| `size` | `'tiny' \| 'small' \| 'medium' \| 'large' \| 'xlarge'` | `'medium'` | 高度见 §3.3 |
| `icon` | `Component \| null` | `null` | ionicons5 图标组件，置于文字前 |
| `loading` | `boolean` | `false` | 显示 loading 旋转，禁用点击 |
| `disabled` | `boolean` | `false` | 禁用态：文字 `#D1D5DB`，背景 `#F3F4F6`，描边 `#E5E7EB` |
| `block` | `boolean` | `false` | 全宽 |
| `round` | `boolean` | `false` | 胶囊形 |
| `htmlType` | `'button' \| 'submit'` | `'button'` | 表单提交 |

变体配色：

| 变体 | 默认 | Hover | Active | 文字 |
| --- | --- | --- | --- | --- |
| primary | `#4F46E5` | `#4338CA` | `#3730A3` | `#FFFFFF` |
| secondary | `#FFFFFF` 描边 `#D1D5DB` | 背景 `#F3F4F6` | 背景 `#E5E7EB` | `#374151` |
| ghost | 透明 | 背景 `#F3F4F6` | 背景 `#E5E7EB` | `#374151` |
| danger | `#DC2626` | `#B91C1C` | `#991B1B` | `#FFFFFF` |
| danger-ghost | `#FFFFFF` 描边 `#FECACA` | 背景 `#FEF2F2` | 背景 `#FECACA` | `#DC2626` |

圆角统一 `--mf-radius-md`（8px）；图标与文字间距 6px；图标按钮（无文字）尺寸 = 高度 + 图标 16px。

事件：`@click`。所有异步操作在 `click` 内先 `loading=true`。

示例：

```vue
<MFButton variant="primary" icon="Add" size="large" @click="openCreate">
  新建数据库
</MFButton>
```

### 5.2 MFTypeTag / MFStatusTag（标签）

| 项 | 规格 |
| --- | --- |
| 说明 | 状态 / 类型标签；`MFTypeTag` 用于数据库类型，`MFStatusTag` 用于所有业务状态 |
| NaiveUI 映射 | `n-tag`（`type`/`bordered` 由封装统一） |
| 通用样式 | 高度 22px（`tiny`），圆角 `--mf-radius-full`（胶囊），内边距 0 10px，字号 12px/500 |

Props（`MFStatusTag`）：

| Prop | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `status` | `string` | — | 状态 key，映射到 §8 状态表（文档/任务/索引） |
| `icon` | `Component \| null` | 部分状态内置 | 前置小图标 12px |
| `loading` | `boolean` | `false` | 显示 12px spinner（用于 Running / Vectorizing 等） |

`MFTypeTag` 仅两个枚举：

| 枚举 | 浅底 | 描边 | 文字 |
| --- | --- | --- | --- |
| 普通表 | `#F3F4F6` | `#E5E7EB` | `#374151` |
| 向量知识库 | `#F5F3FF` | `#DDD6FE` | `#7C3AED`（前置 8px 紫色圆点） |

### 5.3 MFInput（输入框）

| 项 | 规格 |
| --- | --- |
| 说明 | 封装 `n-input`，统一尺寸/圆角/状态色 |
| NaiveUI 映射 | `n-input` |

Props：

| Prop | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | 高度 28/32/36 |
| `placeholder` | `string` | `''` | 占位 13px/`#9CA3AF` |
| `prefixIcon` / `suffixIcon` | `Component` | — | 前后缀图标 |
| `clearable` | `boolean` | `false` | 可清空 |
| `disabled` | `boolean` | `false` | 背景 `#F9FAFB`，文字 `#D1D5DB` |
| `inputProps` | `object` | — | 透传 |

视觉规格：背景 `#FFFFFF`，描边 `1px solid #D1D5DB`，圆角 `--mf-radius-sm`（6px）；focus 描边 `#4F46E5` + 2px 半透明主色外环 `box-shadow: 0 0 0 2px rgba(79,70,229,0.15)`；hover 描边 `#9CA3AF`。

事件：`@update:value`、`@enter`（回车提交）、`@clear`。

### 5.4 MFSelect（下拉选择器）

| 项 | 规格 |
| --- | --- |
| 说明 | 封装 `n-select`，用于操作符、Embedding 模型、分页条数等 |
| Props | `options: Array<{label, value, disabled?}>`；`size`；`placeholder`；`clearable`；`multiple`；`disabled` |
| 视觉 | 同 MFInput：白底、描边 `#D1D5DB`、圆角 6px；下拉面板圆角 8px、阴影 `--mf-shadow-md`、项高 32px、hover 背景 `#F3F4F6`、选中项背景 `#EEF2FF` 文字主色 |
| 事件 | `@update:value` |

### 5.5 MFSegmented（分段控件）

| 项 | 规格 |
| --- | --- |
| 说明 | 视图切换（表格视图 / JSON 视图）；NaiveUI 无原生 Segmented，用 `n-radio-group`(button) 实现或自绘 |
| 视觉 | 容器白底描边 `#D1D5DB` 圆角 8px，内边距 2px；选中项主色实心圆角 6px 白字 13px/500；未选中项灰字 `#374151` |
| 高度 | 32px |
| Props | `options: Array<{label, value, icon?}>`；`v-model:value` |
| 事件 | `@update:value` |

### 5.6 MFTable（数据表格）

| 项 | 规格 |
| --- | --- |
| 说明 | 全站统一表格，封装 `n-data-table`，固定列宽策略、行高、斑马纹、空态 |
| NaiveUI 映射 | `n-data-table` |

Props：

| Prop | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `columns` | `DataTableColumn[]` | `[]` | 列定义（见下方列规范） |
| `data` | `object[]` | `[]` | 数据源 |
| `loading` | `boolean` | `false` | 行骨架屏（`n-skeleton`，6 行） |
| `rowKey` | `(row) => string` | — | 行唯一键 |
| `rowSelection` | `object \| undefined` | — | 多选（批量操作列），勾选列宽 44px |
| `scrollX` | `number` | 自动 | 内容超宽时横向滚动 |
| `pagination` | `false \| object` | `false` | 建议关闭内部分页，使用 `MFPagination`（§5.7） |
| `minHeight` | `number` | `320` | 空态居中显示高度 |

视觉规格：

| 项 | 值 |
| --- | --- |
| 容器 | 白卡片，圆角 `--mf-radius-lg`，阴影 `--mf-shadow-sm`，内边距 0（表头贴边） |
| 表头行 | 高 44px，背景 `#F9FAFB`，文字 13px/500/`#374151`，底部边框 `#E5E7EB` |
| 数据行 | 高 48px（内容多时可 56px），单元格 13px/`#374151`，上下边框 `#F3F4F6` |
| 行 hover | 背景 `#F9FAFB` |
| 行选中 | 背景 `#EEF2FF` |
| 斑马纹 | 不使用（hover 反馈已足够） |
| 单元格内边距 | 12px 16px |
| 省略 | 长文本列统一 `ellipsis` + `n-tooltip` 全文提示 |

列规范（所有列必须声明 width 或 minWidth）：

| 列类型 | width 建议 | 说明 |
| --- | --- | --- |
| 勾选列 | 44px | 固定 |
| 主键/ID | 160–220px | 代码字体 12px，前 10 字符 + `…` |
| 文本列 | 160–280px | ellipsis + tooltip |
| 数字列 | 90–120px | 右对齐，`tabular-nums` |
| 状态列 | 110px | `MFStatusTag` |
| 时间列 | 150px | `YYYY-MM-DD HH:mm:ss`，12px/`#6B7280` |
| 操作列 | 180–240px | 右对齐，文字按钮组（见 §5.8） |

### 5.7 MFPagination（分页）

| 项 | 规格 |
| --- | --- |
| 说明 | 统一分页条，位于表格卡片底部，右侧对齐 |
| NaiveUI 映射 | `n-pagination` |
| 布局 | 左：「共 N 条」13px/`#6B7280`；右：页码（5 个可见，超出折叠为 `…`，共 X 页）+「50 条/页」下拉（20/50/100）+「跳至 [n] 页」 |
| 页码 | 40×32px，圆角 6px；当前页主色实心白字；hover 灰底 |
| 高度 | 56px（含上下内边距），顶部边框 `#E5E7EB` |

Props：`total`、`page`(v-model)、`pageSize`(v-model)、`pageSizeOptions: [20,50,100]`、`showSizePicker`、`showQuickJumper`。

### 5.8 MFTextButton（表格内文字按钮）

| 项 | 规格 |
| --- | --- |
| 说明 | 表格操作列按钮组；每项为文字 + 可选图标，间距 12px |
| 常规 | 13px/`#4F46E5`，hover 下划线 + `#4338CA` |
| 危险类（删除/重建） | 13px/`#DC2626`，hover `#B91C1C` |
| 禁用 | `#D1D5DB` |
| 规则 | 单行操作 ≤ 4 个；超过时折叠进「更多」`n-dropdown` |

### 5.9 MFFilterBuilder（筛选条件构建器）

| 项 | 规格 |
| --- | --- |
| 说明 | 组合条件筛选（字段 + 操作符 + 值），支持 AND/OR 与分组；在筛选对话框（§7.3）与数据页内联 chips（§6.3.2）中复用 |
| NaiveUI 映射 | 组合 `n-select` / `n-input` / `n-input-number` / `n-radio-group` |

核心数据结构：

```ts
interface FilterGroup {
  logic: 'AND' | 'OR';        // 组内逻辑
  conditions: FilterCondition[];
  groups?: FilterGroup[];     // 嵌套子分组（≤2 层）
}
interface FilterCondition {
  field: string;              // 字段名（支持 _id/任意 JSON 字段）
  operator: OperatorKey;      // §8.3 操作符
  value: string | number | boolean | string[];
}
```

操作符枚举（§8.3）——UI 文案映射：

| OperatorKey | 中文文案 | 值控件 |
| --- | --- | --- |
| `eq` | 等于 | `n-input`（可 `n-switch` 切换布尔 / `n-input-number` 数字） |
| `ne` | 不等于 | 同上 |
| `contains` | 包含 | `n-input` |
| `not_contains` | 不包含 | `n-input` |
| `gt` | 大于 | `n-input-number` |
| `gte` | 大于等于 | `n-input-number` |
| `lt` | 小于 | `n-input-number` |
| `lte` | 小于等于 | `n-input-number` |
| `exists` | 存在 | 无值控件（自动隐藏值输入框） |
| `not_exists` | 不存在 | 无值控件 |
| `regex` | 正则匹配 | `n-input`（等宽字体，带校验：非法正则红框提示） |
| `array_contains` | 数组包含 | `n-select` multiple |

UI 结构（对话框内，§7.3）：逻辑选择「满足以下 全部 / 任意 条件（AND / OR）」→ 条件行列表 → 「＋ 添加条件」「＋ 添加分组」→ 「生成的查询（预览）」只读代码块 → 底部「取消 / 应用筛选」。

### 5.10 MFJsonEditor（JSON 编辑器）

| 项 | 规格 |
| --- | --- |
| 说明 | JSON 编辑核心组件；默认实现 `monaco-editor`（`json` 语言），打包按需加载；无 Monaco 时降级为 `n-input type=textarea` + 高亮（`highlight.js`） |
| 依赖 | `monaco-editor`（需新增依赖，见 §11.6） |
| 容器 | 白底描边 `#E5E7EB` 圆角 8px，高 320–480px（对话框内自适应），overflow auto |

Props：

| Prop | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `modelValue` | `string` | `''` | JSON 文本 |
| `readonly` | `boolean` | `false` | 只读模式（详情查看） |
| `height` | `number` | `360` | 高度 px |
| `showLineNumbers` | `boolean` | `true` | 行号 |
| `tabSize` | `number` | `2` | 缩进 |

内置能力（工具栏按钮由外层 Dialog 提供）：

| 能力 | 行为 |
| --- | --- |
| 语法高亮 | JSON key 主色 / 字符串绿 / 数字橙 / 布尔紫（Monaco 默认主题微调） |
| 格式化 | `formatDocument`，2 空格缩进 |
| 校验 | JSON.parse 校验；失败时行内波浪线 + 底部错误条「第 N 行：错误信息」，阻断保存 |
| 复制 | `navigator.clipboard`，成功 message「已复制到剪贴板」 |

事件：`@update:modelValue`、`@validate`（返回 `{ok, message?, line?}`）。

### 5.11 MFModal（对话框）

| 项 | 规格 |
| --- | --- |
| 说明 | 统一模态框；封装 `n-modal` |
| 遮罩 | `rgba(17,24,39,0.45)`，点击遮罩关闭（`maskClosable` 默认 true，表单类可关闭） |
| 动画 | 300ms 缩放 + 淡入 |
| 圆角 | `--mf-radius-lg`（12px） |
| 阴影 | `--mf-shadow-lg` |

尺寸规范（宽度）：

| 预设 | 宽度 | 用途 |
| --- | --- | --- |
| `small` | 400px | 重命名、简短确认 |
| `medium` | 480px | 删除确认（§7.4）、消息弹窗 |
| `large` | 640px | 新建向导（§7.1）、筛选（§7.3）、向量化配置（§7.6） |
| `xlarge` | 800px | JSON 编辑（§7.2） |

结构（自上而下）：

```text
┌──────────────────────────────────────┐
│ 标题 18px/600          [× 关闭 24px]  │ ← header，padding 20px 24px
├──────────────────────────────────────┤
│ 内容区（padding 0 24px，可滚动）       │ ← body，max-height 70vh
├──────────────────────────────────────┤
│          [次要按钮] [主按钮]          │ ← footer，右对齐，padding 16px 24px
└──────────────────────────────────────┘
```

Props：`title`、`width`（预设或数字）、`maskClosable`、`closable`、`showFooter`、`confirmText`、`cancelText`、`confirmLoading`、`danger`（footer 主按钮变 danger）。

### 5.12 MFDrawer（抽屉）

| 项 | 规格 |
| --- | --- |
| 说明 | 右侧滑出面板，用于上传文档（§7.5）、任务日志（§7.7） |
| NaiveUI | `n-drawer` + `n-drawer-content` |
| 尺寸 | 宽度 420px（上传）/ 560px（日志），可传 `width` |
| 动画 | 300ms 从右滑入 |
| 头部 | 标题 16px/600 + 关闭按钮；底边框 `#E5E7EB` |
| 底部 | 操作栏（次要 + 主按钮），顶边框 `#E5E7EB`，padding 16px 24px |

### 5.13 MFStatCard（统计卡）

| 项 | 规格 |
| --- | --- |
| 说明 | 概览统计卡（数据库详情头部、统计页） |
| 容器 | 白卡片，圆角 `--mf-radius-lg`，阴影 `--mf-shadow-sm`，内边距 16px 20px，高度 84px |
| 内部 | 上：标题 12px/`#6B7280`/500；下：数值 18px/600/`#111827`（数字用 `tabular-nums`） |
| 可选图标 | 左上角 18px 图标（颜色与语义对应） |
| 可点击 | 部分卡（记录数 / 文档数）hover 上浮 2px + 阴影 `--mf-shadow-md`，点击跳转对应 Tab |

Props：`title`、`value`、`icon?`、`color?`、`to?`（跳转 Tab）、`suffix?`（如 dims / MB）。

### 5.14 MFTabs（模块 Tab）

| 项 | 规格 |
| --- | --- |
| 说明 | 数据库详情内的模块切换；向量库为文档管理 / 数据浏览 / 检索测试 / 统计信息 / 设置，普通库仅数据浏览 |
| 实现 | `nav` + route-controlled buttons；不用 `n-tabs`，避免路由切换时指示条定位漂移 |
| 视觉 | Tab 文字 14px/`#374151`，选中/hover 主色；活动按钮通过 `::after` 绘制底部 2px 主色指示条；高度 42px |
| 徽标 | 文档管理 Tab 可带计数徽标（如失败文档数 >0 显示红点） |
| 事件 | `@update:value` 同步 URL query `?tab=` |

### 5.15 MFEmpty / MFSkeleton / MFSpin（空态与加载）

| 项 | 规格 |
| --- | --- |
| `MFEmpty` | 封装 `n-empty`；图标 48px 灰 `#D1D5DB`，文案 13px/`#6B7280`；支持 `action` 插槽（如「上传文档」「新建数据库」按钮）；高度默认 240px 居中 |
| `MFSkeleton` | 表格加载 6 行骨架（表头 + 5 行 × 4 列），圆角 4px，闪烁动画 1.2s |
| `MFSpin` | 全屏加载用 `n-spin`（遮罩白 0.6 + 主色转圈 28px）；区块加载用 18px 转圈 |

### 5.16 MFProgress（进度）

| 项 | 规格 |
| --- | --- |
| 说明 | 上传 / 向量化 / 重建索引进度 |
| NaiveUI | `n-progress`（`type="line"`） |
| 视觉 | 高度 6px，圆角 3px，已完段主色 `#4F46E5`（上传失败段红），轨迹 `#E5E7EB`；百分比文字 12px/`#6B7280` 靠右 |
| 状态色 | 完成 `#16A34A` / 失败 `#DC2626` / 运行 `#4F46E5`（>0 时 1.2s 流动动画可选） |

### 5.17 MFCodeBlock（代码块）

| 项 | 规格 |
| --- | --- |
| 说明 | 只读代码展示（筛选查询预览、JSON 视图、检索结果内容） |
| 视觉 | 背景 `#F9FAFB`，描边 `#E5E7EB`，圆角 8px，内边距 12px 16px，代码字体 12px/1.6/`#374151`；右上角复制按钮 |
| 高亮 | JSON / MongoDB 查询语法高亮（`highlight.js`），key 主色 |

### 5.18 消息与通知（MFMessage / MFNotification）

| 项 | 规格 |
| --- | --- |
| 说明 | 全局轻提示，封装 `n-message` / `n-notification` |
| Message | 顶部居中，圆角 8px，阴影 `--mf-shadow-lg`，3s 自动消失；成功主色左条 / 错误红 / 警告橙 / 信息蓝 |
| Notification | 右上角，宽 360px，圆角 12px，用于任务完成 / 失败等需要停留的事件（10s + 手动关闭） |
| 统一文案 | 成功「操作成功」/「已保存」/「已删除」；失败「操作失败：{原因}」 |

### 5.19 其他基础组件速查

| 组件 | NaiveUI | 规格要点 |
| --- | --- | --- |
| `MFIcon` | `n-icon` | 统一 16px/`#374151`；禁用 12px `#9CA3AF`；继承 NaiveUI icon 尺寸 |
| `MFTooltip` | `n-tooltip` | 深色 `#111827` 底白字 12px，圆角 6px，箭头，显示延迟 100ms |
| `MFDropdown` | `n-dropdown` | 面板白底圆角 8px 阴影 `--mf-shadow-md`，项高 36px，危险项红字 |
| `MFPopconfirm` | `n-popconfirm` | 用于行内轻量确认（重命名前、单条删除前），按钮：取消/确认 |
| `MFBadge` | `n-badge` | 主色圆点；红色用于失败计数；数字 >99 折叠为 99+ |
| `MFAvatar` | `n-avatar` | 圆形 30px，主色渐变底白字首字母 |
| `MFDivider` | `n-divider` | 竖分割线高 16px 灰 `#D1D5DB`（Header 内用户区） |
| `MFSwitch` | `n-switch` | 开=`#4F46E5`，关=`#D1D5DB`；用于自动刷新等二元设置 |
| `MFSlider` | `n-slider` | 主色滑块，轨道 `#E5E7EB`；TopK / Threshold |
| `MFInputNumber` | `n-input-number` | 与 MFInput 同视觉 |
| `MFAlert` | `n-alert` | 上传提示条：信息蓝浅底 / 警告橙浅底 / 错误红浅底，圆角 8px |

---

## 6. 页面设计（按路由）

> 路由表见 §11.4。所有页面统一：内容容器 padding 24px、背景 `#F9FAFB`、区块间距 24px。

### 6.1 数据库首页

#### 6.1.1 数据库列表页（`/`，即侧边栏 + 空主区）

未选中数据库时主区显示欢迎页：

| 区块 | 内容 |
| --- | --- |
| 标题 | 「欢迎使用 MooFile」24px/600/`#111827`，居中 |
| 副标题 | 「轻量级 JSON 数据库 + 向量知识库管理平台」14px/`#6B7280` |
| 操作 | `MFButton` primary large「＋ 新建数据库」 |
| 特性展示 | 3 列特性卡（圆角 12px 白卡）：JSON 文档存储 / 向量知识库 / 任务可追踪，每卡图标 + 标题 + 一行说明 |

#### 6.1.2 数据库详情头部（`DatabaseHeader`，全详情页共用）

位于主区顶部，所有详情 Tab 共享，结构：

```text
┌────────────────────────────────────────────────────────────────┐
│ support_knowledge  [向量知识库]                   [重命名][删除数据库]│
│ (20px/600)          (MFTypeTag)         按钮组（右侧）            │
├────────────────────────────────────────────────────────────────┤
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│
│ │ 文档数  │ │ 记录数  │ │向量维度 │ │数据库大小│ │ 更新时间 ││
│ │  128   │ │15,682  │ │384 dims│ │256.00 MB│ │ 2024…  ││
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘│
└────────────────────────────────────────────────────────────────┘
```

| 区块 | 规格 |
| --- | --- |
| 标题行 | 数据库名 20px/600 + `MFTypeTag`；向量库显示重命名/删除，普通库显示新增数据/重命名/删除 |
| 统计卡行 | 5 张 `MFStatCard`，默认 5 列；窄屏 3 列换行 |
| 向量库统计 | 文档数 / 记录数（分片数）/ 向量维度 384 / 数据库大小（2 位小数 MB）/ 更新时间 |
| 普通库统计 | 记录数 / 字段数 / 默认索引 / 数据库大小（2 位小数 MB）/ 更新时间；不显示独立统计页 |
| 操作可见性 | 上传文档入口仅在向量库文档页工具栏；新增数据仅普通库显示；向量库不显示新增数据与记录导出 |

#### 6.1.3 模块 Tabs（`MFModuleTabs`）

位于统计卡下方。向量库显示 `文档管理 | 数据浏览 | 检索测试 | 统计信息 | 设置`，默认文档管理；普通库仅显示 `数据浏览`。选择通过 `?tab=documents|data|retrieval|stats|settings` 持久化，刷新时保持有效路由状态。

### 6.2 数据浏览页（`DataBrowsePage`，`/db/:id?tab=data`）

#### 6.2.1 页面结构

```text
[工具条 ①]
[筛选 chips ②]
[表格 / JSON 视图 ③]
[分页 ④]
```

#### 6.2.2 ① 工具条（`DataToolbar`）

```text
[筛选条件 (2)] [字段筛选] | [搜索内容...        ] [搜索][重置]     [导出]  [表格视图|JSON视图]
```

| 元素 | 规格 |
| --- | --- |
| `MFBadge`+按钮「筛选条件」 | 点击打开筛选对话框（§7.3）；徽标显示已启用条件数，>0 时主色 |
| 按钮「字段筛选」 | secondary 按钮；下拉选择当前库已有字段（`n-dropdown`），选择后自动加入筛选器 |
| 搜索框 | `MFInput`，宽 280px，placeholder「搜索内容...」，回车触发搜索；搜索命中全文/字段模糊匹配 |
| 搜索 / 重置 | `MFButton` primary / ghost |
| 导出 | 仅普通库显示；菜单支持「导出当前页」和「导出全部」，输出 JSON；向量库隐藏 |
| 视图切换 | `MFSegmented`：「表格视图」（图标 `Table`）/「JSON 视图」（图标 `Code`） |

#### 6.2.3 ② 筛选条件 chips（`FilterChips`）

| 元素 | 规格 |
| --- | --- |
| 容器 | 高度 36px，圆角 8px，白底描边 `#E5E7EB`，内边距 4px 8px，`flex wrap` gap 8px |
| Chip | 白底描边 `#C7D2FE` 圆角 6px，文字 12px/`#4F46E5`（格式：`字段 操作符 值`），右侧 `×` 关闭图标；hover 背景 `#EEF2FF` |
| 清空全部 | 文字按钮 12px/`#6B7280`，hover `#DC2626`，置于最右 |
| 数量上限 | 一行放不下时换行；>8 个时显示「+N」折叠 |

#### 6.2.4 ③ 表格视图（`MFTable`）

列定义（向量库默认）：

| 列 | width | 渲染 |
| --- | --- | --- |
| 勾选 | 44px | 批量操作（批量删除） |
| `_id` | 200px | 代码字体 12px，截断前 12 字符 + tooltip 全文 |
| `source` | 200px | ellipsis + tooltip（来源文档名） |
| `page` | 80px | 数字右对齐 |
| `chunk_index` | 100px | 数字右对齐 |
| `content` | 260px | ellipsis 两行（`-webkit-line-clamp: 2`），点击弹出详情 |
| `tokens` | 90px | 数字右对齐 |
| `embedding` | 220px | 代码字体 12px `[0.018, -0.224, 0.091, …] 384 dims`，省略 + tooltip |
| `status` | 110px | `MFStatusTag`（已索引 green / 未索引 gray / 失败 red） |
| 操作 | 160px | `MFTextButton`：编辑 / 删除 |

行内操作行为：

| 操作 | 行为 |
| --- | --- |
| 编辑 | 打开 `JsonEditDialog`（§7.2），载入该行完整 JSON |
| 删除 | `MFPopconfirm`「确认删除当前数据吗？」确认后删除，message 成功反馈 |
| 勾选批量 | 工具条浮现批量操作条：`已选 N 条 [批量删除] [取消]`；批量删除再次确认所选数量 |

#### 6.2.5 ③ JSON 视图（`JsonViewPanel`）

| 项 | 规格 |
| --- | --- |
| 说明 | 开发人员视图；展示当前页 20 条记录的 JSON 数组 |
| 布局 | `MFCodeBlock` 全宽，代码字体 12px，行号 |
| 行内操作 | 每条记录右上角悬浮操作：复制 / 编辑 / 删除（图标按钮 28×28 白底，hover 灰底） |
| 数据量 | 分页同表格视图，每页 20/50/100 条 |

#### 6.2.6 ④ 分页

`MFPagination`（§5.7），数据来自接口分页元信息 `{total, page, pageSize}`。

### 6.3 文档管理页（`DocumentsPage`，`/db/:id?tab=documents`，仅向量库）

#### 6.3.1 工具条

```text
[搜索文档名...      ] [状态筛选 ▾] [上传文档 primary]        [开始向量化 (N)]
```

| 元素 | 规格 |
| --- | --- |
| 上传文档 | `MFButton` primary；位于状态筛选框右侧，打开 `UploadDocumentDrawer`（§7.5） |
| 搜索 | 同数据页搜索框（按文档名过滤） |
| 批量操作 | 勾选 ≥1 行后可用：`n-dropdown`：开始向量化 / 移入回收站；危险项红字 |
| 状态筛选 | `MFSelect`（全部状态/已上传/已解析/待向量化/向量化中/已完成/失败）宽 140px |

#### 6.3.2 文档表格（`MFTable`）

列定义：

| 列 | width | 渲染 |
| --- | --- | --- |
| 勾选 | 44px | 多选 |
| 文档名 | 260px | 文件图标（PDF 红 / DOCX 蓝 / TXT 灰 / MD 紫 / PPTX 橙）+ 名称 ellipsis |
| 类型 | 80px | 大写扩展名 `PDF/DOCX/TXT/MD/PPTX` 12px/`#6B7280` |
| 大小 | 100px | 右对齐，`2.4 MB`（B/KB/MB/GB 自适应） |
| 上传时间 | 150px | `YYYY-MM-DD HH:mm:ss` 12px |
| 状态 | 120px | `MFStatusTag`（§8.1 色表） |
| Chunk 数 | 100px | 数字；未解析显示 `–` |
| 向量状态 | 120px | `MFStatusTag`（未向量化 gray / 已向量化 green / 向量化中 purple+spinner / 失败 red） |
| 操作 | 240px | 详情 / 下载 / 开始向量化 / 更多▾（重命名 / 删除） |

操作行为：

| 操作 | 行为 |
| --- | --- |
| 详情 | 打开文档详情抽屉（§7.8） |
| 下载 | 下载原文件，loading 反馈 |
| 开始向量化 | 状态为「已解析 / 待向量化 / 失败」时可用；打开 `VectorizeConfigDialog`（§7.6）并默认选中该文档 |
| 重命名 | `MFModal` small：输入新名称，校验重名/空值 |
| 删除 | `MFPopconfirm`「确认删除该文档及其所有关联片段吗？」→ 确认删除 |

状态不可逆操作提示：状态为 `Vectorizing` 的行禁用删除/重命名（tooltip「向量化进行中，暂不可操作」）。

上传或删除成功后立即重新加载文档列表；存在 `vectorizing` 文档时每 2 秒轮询一次，全部离开向量化状态后自动停止。

#### 6.3.3 空态

无文档时 `MFEmpty`：「暂无文档」+ 操作按钮「上传文档」。

### 6.4 分片设置页（`ChunksPage`，`/db/:id?tab=chunks`，仅向量库）

> 当前主流程不渲染该页面或 Tab；以下内容仅作为后端分片 API 的高级管理设想保留。

#### 6.4.1 工具条

```text
[按文档筛选 ▾] [搜索内容...] [搜索][重置]   [导出全部]
```

| 元素 | 规格 |
| --- | --- |
| 文档筛选 | `MFSelect` 宽 220px，选项 = 文档列表（可搜索） |
| 导出 | 当前实现未提供分片导出；如未来开放页面，应通过后端新增专用导出接口 |

#### 6.4.2 Chunk 表格（`MFTable`）

列定义：

| 列 | width | 渲染 |
| --- | --- | --- |
| Chunk ID | 200px | 代码字体 12px 截断 + tooltip |
| 文档 | 220px | 来源文档名 ellipsis |
| 序号 | 90px | `chunk_index` 右对齐 |
| 内容 | 320px | 两行省略 + tooltip；关键字命中高亮（搜索词主色背景） |
| Tokens | 90px | 右对齐 |
| Embedding 状态 | 130px | `MFStatusTag`（已生成 green / 未生成 gray / 失败 red） |
| 操作 | 200px | 查看 / 重新 Embedding / 删除 |

| 操作 | 行为 |
| --- | --- |
| 查看 | 打开 chunk 详情抽屉：完整 content + 元数据（source/page/offset）+ token 数 |
| 重新 Embedding | `MFPopconfirm`「将重新生成该分片向量」→ 创建向量化任务，chunk 状态变向量化中 |
| 删除 | `MFPopconfirm`「删除该分片及其向量」 |

### 6.5 向量任务页（`TasksPage`，`/db/:id?tab=tasks`，仅向量库）

> PRD §14 新增模块。注意：侧边栏主区 Tabs 不含「向量任务」独立 Tab，任务入口固定在文档/分片操作处；本页作为独立路由 `/db/:id/tasks`，从「查看全部任务」入口进入，或在 Tabs 右侧添加「任务」图标入口。

#### 6.5.1 工具条

```text
[全部类型 ▾] [全部状态 ▾] [刷新]   （右侧）[自动刷新: 开关 30s]
```

#### 6.5.2 任务表格（`MFTable`）

列定义：

| 列 | width | 渲染 |
| --- | --- | --- |
| 任务 ID | 200px | 代码字体 12px |
| 类型 | 140px | 图标 + 文案：解析文档 / 向量化 / 重建索引 / 删除索引 |
| 目标 | 240px | 文档名 / 库名 ellipsis |
| 状态 | 120px | `MFStatusTag`（§8.2 色表），Running 带 spinner |
| 开始时间 | 150px | `YYYY-MM-DD HH:mm:ss` |
| 结束时间 | 150px | 未结束显示 `–` |
| 进度 | 120px | 运行中显示 `MFProgress`（如 45%），否则 `–` |
| 操作 | 200px | 查看日志 / 重试（失败/取消时）/ 取消（运行中） |

| 操作 | 行为 |
| --- | --- |
| 查看日志 | 打开 `TaskLogDrawer`（§7.7） |
| 重试 | 创建同配置新任务，旧任务保留为失败记录 |
| 取消 | `MFPopconfirm`「取消后任务中断，已处理部分保留」 |

### 6.6 索引设置页（`IndexSettingsPage`，`/db/:id?tab=index`）

> 当前主流程不渲染该页面或 Tab；模型切换通过现有对话框和任务接口协作完成。

#### 6.6.1 索引信息卡

| 项 | 规格 |
| --- | --- |
| 容器 | 白卡圆角 12px，内边距 20px 24px |
| 信息行 | 栅格 3 列：Embedding Model（代码字体，如 `text-embedding-3-small`）/ 向量数 / 维度；第二行：存储占用 / 索引版本（`v3`）/ 创建时间 |
| 状态 | 顶部右侧 `MFStatusTag`（索引状态：未构建/构建中/已完成/失败） |

#### 6.6.2 操作区

| 按钮 | 规格 | 行为 |
| --- | --- | --- |
| 重建索引 | `MFButton` secondary | `MFPopconfirm`「重建将重新生成全部向量，耗时取决于文档数」→ 创建 `Index Rebuild` 任务 |
| 删除索引 | `MFButton` danger-ghost | `MFModal` medium 确认（影响清单 + 输入库名）→ 创建 `Delete Index` 任务 |
| 更换模型 | `MFButton` secondary | 打开 `ModelChangeDialog`（§7.9） |

重建/删除索引进行中：操作按钮禁用 + 显示 `MFProgress`（任务进度轮询）。

### 6.7 检索测试页（`RetrievalPage`，`/db/:id/retrieval`，仅向量库）

#### 6.7.1 页面布局（两栏）

```text
┌──────────────────────┬──────────────────────────────────┐
│ 查询配置（左栏 360px） │ 检索结果（右栏，flex 1）           │
│  Question textarea   │  ResultList                      │
│  TopK / Threshold    │  每项：排名+分数+内容+来源          │
│  [开始检索 primary]   │                                  │
└──────────────────────┴──────────────────────────────────┘
```

#### 6.7.2 查询配置卡（`RetrievalConfigCard`）

| 元素 | 规格 |
| --- | --- |
| Question | `n-input` type=textarea，高 120px，placeholder「输入问题，例如：AgentBase 是什么？」；空值禁用检索 |
| TopK | `MFSlider` 1–50，默认 10，右侧数值显示 |
| Similarity Threshold | `MFSlider` 0–1，步进 0.05，默认 0.3 |
| 开始检索 | `MFButton` primary block large + 搜索图标；检索中 loading，耗时显示在按钮下方 |

当前后端只提供向量语义检索，前端不展示 Hybrid Search。

#### 6.7.3 结果列表（`RetrievalResultList`）

| 项 | 规格 |
| --- | --- |
| 空态 | 「输入问题并点击开始检索」；无结果显示「未找到匹配内容」 |
| 结果项卡片 | 白卡圆角 12px，padding 16px 20px，间距 12px |
| 可视范围 | 单卡固定高 140px，结果容器最多完整展示 4 张卡（`max-height: 596px`），更多结果在容器内纵向滚动 |
| 第一行 | 排名徽章（1~3 名主色实心，其余灰底）+ 相似度分数 13px/600（≥0.7 绿 / ≥0.5 主色 / <0.5 灰）+ 分数条（`MFProgress` 主色，宽 120px） |
| 第二行 | 来源文档名（主色链接，点击打开文档详情）+ chunk_index |
| 第三行 | 内容全文 13px/`#374151`，命中词高亮（主色浅底 `#EEF2FF`） |
| 底部 | 复制内容（文字按钮）+ 元数据（page/source 等） |

### 6.8 统计页（`StatsPage`，`/db/:id?tab=stats`）

#### 6.8.1 统计卡行

6 张 `MFStatCard`：文档数 / Chunk 数 / 向量数 / 存储用量 / 失败文档（danger 色，>0 时红）/ 失败任务（danger 色）。栅格 3 列（<1280px 2 列）。

### 6.9 向量设置页（`VectorSettingsPage`，`/db/:id?tab=settings`）

仅向量库显示。页面读取并保存 `meta.json.vectorConfig`，包含 Embedding Model、向量维度（只读）、Chunk Size、Chunk Overlap、Top K 与 Similarity Threshold。检索页和向量化对话框以这些值为默认配置。

切换 Embedding Model 时显示警告：保存后会清除不兼容的向量记录，并将文档重置为待向量化状态。保存成功后触发全局刷新，使侧栏、详情统计和当前页面保持一致。

#### 6.8.2 图表区（`ECharts` 两个卡片）

| 卡片 | 图表 | 规格 |
| --- | --- | --- |
| 近 7 日文档上传与向量化 | 双轴柱线组合：柱=每日上传文档数（主色 `#4F46E5`），线=向量化完成数（向量紫 `#7C3AED`） | 高 280px，tooltip axis，图例右上 |
| 文档状态分布 | 环形图：Uploaded/Parsed/Waiting/Vectorizing/Completed/Failed，配色 = §8.1 状态色 | 高 280px，中心显示总数，图例右侧 |

图表规范：无边框白卡，标题 15px/600，颜色严格用状态色，数字 `tabular-nums`，空数据时显示 `MFEmpty`「暂无统计数据」。

### 6.9 回收站页（`TrashPage`，`/trash`）

| 项 | 规格 |
| --- | --- |
| 表格 | 列：数据库名 / 类型 / 记录数 / 大小 / 删除时间 / 操作（恢复 / 彻底删除） |
| 恢复 | 文字按钮主色；确认后移回数据库列表 |
| 彻底删除 | 文字按钮红；`MFModal` medium 确认（输入库名，同 §7.4 逻辑） |
| 空态 | 「回收站为空」 |
| 清空回收站 | 顶部右侧 danger 按钮，`MFModal` 输入「清空」确认 |

---

## 7. 对话框 / 抽屉详设

### 7.1 新建数据库向导（`NewDatabaseWizardDialog`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFModal` large（640px），标题「新建数据库」，`maskClosable=false`（防误关丢输入） |
| 步骤条 | 顶部 3 步：选择类型 → 基本信息 → 确认；`n-steps`，当前步主色圆点，完成步绿色对勾 |

**Step 1 选择类型**：两张类型卡片（并排，gap 16px）：

| 卡片 | 普通表（JSON） | 向量知识库 |
| --- | --- | --- |
| 选中态 | 主色描边 2px + `#EEF2FF` 浅底 | 向量紫描边 2px + `#F5F3FF` 浅底 |
| 未选中 | 描边 `#E5E7EB` 白底，hover 描边 `#C7D2FE` + 阴影 md | 同左 |
| 标题 | 图标 + 「普通表 (JSON)」16px/600 | 图标 + 「向量知识库」16px/600 |
| 说明 | 「存储结构化的 JSON 文档数据，支持灵活的字段查询。」13px/`#6B7280` | 「存储文档并自动分片，构建向量索引，支持语义搜索。」 |
| 特性清单 | √ JSON 文档存储 / √ 灵活的字段结构 / √ 条件查询与索引 | √ 文档分片处理 / √ 向量索引构建 / √ 语义相似度搜索 |
| 底部 | 下一步（disabled 直到选中） | 同左 |

**Step 2 基本信息**：表单（`n-form`，label 13px/`#374151`）：

| 字段 | 控件 | 校验规则 |
| --- | --- | --- |
| 数据库名称 | `MFInput` xlarge，placeholder「请输入数据库名称」 | 必填；2–64 字符；仅英文字母、数字和下划线；提示「已存在同名数据库」 |

**Step 3 确认**：摘要卡（白底 `#F9FAFB` 圆角 8px）：类型图标 + 类型名 / 数据库名称 / 提示文案（向量库：「创建后将获得完整的文档管理、分片与向量检索能力」）。

底部按钮（各步骤统一）：`取消`(ghost) —— `上一步`(secondary，Step2/3 显示) —— `下一步/创建`(primary，loading)。创建成功 message「数据库创建成功」，自动选中新库并跳转。

### 7.2 新增 / 编辑 JSON 对话框（`JsonEditDialog`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFModal` xlarge（800px），标题「新增 / 编辑 JSON 数据」，`maskClosable=false` |
| 工具栏 | 顶部行：`格式化` / `校验` / `复制`（ghost 按钮 28px，图标+文字 13px） |
| 校验状态条 | 位于工具栏下：`√ JSON 格式正确`（成功绿 13px）或 `✕ 第 {line} 行：{error}`（危险红 13px + 红色警示图标） |
| 编辑区 | `MFJsonEditor`，高 400px（§5.10） |
| 底部 | `取消`(ghost) / `保存`(primary，disabled until 校验通过；保存中 loading) |
| 新增模式 | 编辑区预填 `{}`，`_id` 留空由服务端生成；编辑模式载入记录完整 JSON |
| 保存 | 校验通过才可保存；失败 message「JSON 格式错误，已阻止保存」 |

### 7.3 筛选条件对话框（`FilterDialog`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFModal` large（640px），标题「筛选条件」 |

结构：

```text
满足以下 [全部 ▾] 条件 (AND)      ← n-select: 全部/任意
────────────
status    [等于 ▾]   [已索引      ]  [×]
content   [包含 ▾]   [AgentBase   ]  [×]
[＋ 添加条件]  [＋ 添加分组]
────────────
生成的查询 (预览)
{ "$and": [ {"status": "已索引"}, {"content": {"$regex": "AgentBase", "$options": "i"}} ] }
────────────
[取消]  [应用筛选]
```

| 元素 | 规格 |
| --- | --- |
| 逻辑选择 | `MFSelect`（全部条件=AND / 任意条件=OR），宽 120px；切换逻辑时预览与 chips 同步 |
| 条件行 | 高 40px，三个控件：字段 `MFSelect`(200px) + 操作符 `MFSelect`(130px) + 值控件(flex 1) + 删除图标（hover 红）；行间距 8px |
| 添加条件 / 添加分组 | 文字按钮 13px 主色，带 `+` 图标；分组 ≤ 2 层，分组行内缩进 16px 且左侧竖线 |
| 查询预览 | `MFCodeBlock`（§5.17），实时生成 MongoDB 风格查询 JSON；非法（字段空/正则错）显示红色边框 |
| 应用筛选 | primary；条件数为 0 时禁用；应用后：chips 更新、表格请求带 `filter` 参数、关闭弹窗 |

### 7.4 删除数据库确认对话框（`DeleteDatabaseDialog`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFModal` medium（480px），`maskClosable=false`，无 `×` 关闭 |
| 警示区 | 顶部：危险红警示图标（48px `AlertCircle`）+ 标题「此操作不可恢复！」16px/600/`#DC2626` |
| 影响清单 | 标题「删除数据库 “support_knowledge” 将会：」13px/`#374151`；4 行要点（13px/`#6B7280`，前置 `•`）：删除所有 15,682 条记录 / 删除 128 个文档及其分片 / 删除向量索引及相关数据 / 释放约 256 MB 存储空间（数字动态取当前值） |
| 确认输入 | label「请输入数据库名称以确认删除：」；`MFInput` danger 态（focus 红描边），placeholder = 库名 |
| 底部 | `取消`(ghost) / `确认删除`(danger primary，disabled until 输入与库名完全一致) |
| 成功后 | message「数据库已删除」，列表移除该项，主区回欢迎页 |

### 7.5 上传文档抽屉（`UploadDocumentDrawer`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFDrawer`（420px），标题「上传文档到知识库」，`maskClosable=false` |

结构：

```text
[拖拽区]  拖拽文件到这里，或 点击选择文件
          支持 PDF、DOCX、TXT、MD、PPTX · 单个文件不超过 50MB
──────────────────────────
已选择 (2)                      [清空全部]
  📄 AI-Agent基盘开发_定例会.html  2.4 MB   [×]
  📄 APMS本部的AI事例发表会.mp4   98.6 MB   [×]  (超 50MB 红字警告)
──────────────────────────
进度区（上传中显示）： 文件名        45%  [进度条]
[取消]  [开始上传]
```

| 元素 | 规格 |
| --- | --- |
| 拖拽区 | `n-upload-dragger`：高 160px，虚线描边 `#C7D2FE` 圆角 12px，hover/拖入时主色实线 + 浅底 `#EEF2FF`；图标 32px 主色 |
| 格式提示 | 12px/`#6B7280`；超限文件行内红字「超过 50MB，无法上传」+ 禁用删除按钮 |
| 已选列表 | 每项 48px：文件类型图标 + 名称（13px ellipsis）+ 大小（12px 灰）+ `×`；数量徽标「已选择 (N)」 |
| 开始上传 | primary block；点击后逐文件上传（并发 3），每文件行显示 `MFProgress`；全部完成 message「N 个文档上传成功」；关闭抽屉 |
| 上传完成 | 原文件保存到 `db/<db_id>/_upload/`，文档状态 = `Uploaded`（灰），**不触发向量化**（铁律一） |

上传请求只包含文件；Chunk Size 与 Chunk Overlap 在开始向量化时配置。

### 7.6 向量化配置对话框（`VectorizeConfigDialog`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFModal` large（640px），标题「开始向量化」，`maskClosable=false` |
| 选中文档 | 顶部摘要条：`已选择 N 个文档` + 文档名 chips（可移除） |
| 配置表单 | 见下表 |
| 底部 | `取消` / `开始向量化`(primary，loading；创建任务后关闭并 message「已创建 N 个向量化任务」) |

| 字段 | 控件 | 规则 |
| --- | --- | --- |
| Embedding Model | `MFSelect` 宽 100%：`text-embedding-3-small` / `text-embedding-3-large` / `bge-large` / `gte-large` | 必选，默认取库配置 |
| Chunk Size | `MFInputNumber` 100–2000 | 默认 500，越界 clamp |
| Chunk Overlap | `MFInputNumber` 0–500 | 默认 20；强制 `< Chunk Size`（违反时红字提示 + 禁用提交） |
| 选中文档确认 | 摘要区列出文档数量与所有文档名，列表超高时内部滚动 |

当前不提供 Metadata Fields 配置，提交参数仅包含 `docIds/model/chunkSize/overlap`。

### 7.7 任务日志抽屉（`TaskLogDrawer`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFDrawer`（560px），标题「任务日志 · {taskId}」 |
| 元信息 | 顶部 2 行：类型/目标/状态（`MFStatusTag`）/ 开始-结束时间 |
| 日志区 | `n-log` 深色（`#111827` 底）代码字体 12px，时间戳 `HH:mm:ss.SSS`，INFO 灰 / WARN 橙 / ERROR 红，行号 |
| 运行中 | 日志尾部自动滚动 + 顶部「LIVE」红点闪烁；可暂停自动滚动 |
| 底部 | `导出日志`(secondary) / `关闭`(primary) |

### 7.8 文档详情抽屉（`DocumentDetailDrawer`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFDrawer`（560px），标题 = 文档名 |
| 内容 | 元信息网格（类型/大小/上传时间/状态/Chunk 数/向量状态）+ 预览区（TXT/MD 全文预览，PDF 显示首页缩略提示）+ 分片摘要（前 5 个 chunk 的 index + 内容片段，点击跳转分片页并定位） |
| 底部 | `下载` / `开始向量化`（按状态可用）/ `关闭` |

### 7.9 更换模型对话框（`ModelChangeDialog`）

| 项 | 规格 |
| --- | --- |
| 容器 | `MFModal` medium（480px），标题「更换 Embedding 模型」 |
| 内容 | `MFSelect` 模型列表 + `MFAlert` warning：「更换模型后现有向量与新模型不兼容，需重建索引（耗时较长）。」 |
| 底部 | `取消` / `确认更换`(primary，确认后创建 `Index Rebuild` 任务) |

---

## 8. 状态体系（单一事实来源）

> 所有状态文案、颜色、图标在此定义。前端实现为 `src/constants/status.ts`，禁止页面内散写。

### 8.1 文档生命周期状态机

```text
                 ┌────────────┐
  上传 ────────▶ │  Uploaded  │ 已上传（灰）
                 └─────┬──────┘
                       │ 解析任务完成
                       ▼
                 ┌────────────┐
                 │   Parsed   │ 已解析（蓝）
                 └─────┬──────┘
                       │ 用户触发「开始向量化」
                       ▼
        ┌──────────────────────────┐
        │ Waiting Vectorization    │ 待向量化（橙）
        └────────────┬─────────────┘
                     │ 任务开始
                     ▼
        ┌──────────────────────────┐
        │       Vectorizing        │ 向量化中（紫 + spinner）
        └──────┬───────────┬───────┘
               │成功        │失败
               ▼            ▼
     ┌──────────────┐  ┌────────┐
     │  Completed   │  │ Failed │
     └──────────────┘  └────────┘
  任意处理态失败 ──▶ Failed（红，可重试/重建索引回到 Waiting）
```

| 状态 key | 中文 | 配色（浅底/描边/文字） | 图标/附加 |
| --- | --- | --- | --- |
| `uploaded` | 已上传 | `#F3F4F6` / `#E5E7EB` / `#374151` | — |
| `parsed` | 已解析 | `#EFF6FF` / `#BFDBFE` / `#2563EB` | — |
| `waiting` | 待向量化 | `#FFFBEB` / `#FDE68A` / `#D97706` | — |
| `vectorizing` | 向量化中 | `#F5F3FF` / `#DDD6FE` / `#7C3AED` | 12px spinner |
| `completed` | 已完成 | `#F0FDF4` / `#BBF7D0` / `#16A34A` | 对勾 |
| `failed` | 失败 | `#FEF2F2` / `#FECACA` / `#DC2626` | 警示图标，hover 显示失败原因 tooltip |

### 8.2 任务状态

| 状态 key | 中文 | 配色 | 附加 |
| --- | --- | --- | --- |
| `pending` | 等待中 | 灰（同 uploaded） | — |
| `running` | 运行中 | 蓝 `#2563EB` | spinner + 行内进度条 |
| `completed` | 已完成 | 绿 | 对勾 |
| `failed` | 失败 | 红 | tooltip 失败原因；可重试 |
| `cancelled` | 已取消 | 灰 `#9CA3AF` / `#F3F4F6` | 可重试 |

### 8.3 查询操作符枚举（与筛选 UI 一一对应）

| key | 中文 | key | 中文 |
| --- | --- | --- | --- |
| `eq` | 等于 | `lte` | 小于等于 |
| `ne` | 不等于 | `exists` | 存在 |
| `contains` | 包含 | `not_exists` | 不存在 |
| `not_contains` | 不包含 | `regex` | 正则匹配 |
| `gt` | 大于 | `array_contains` | 数组包含 |
| `gte` | 大于等于 | — | — |
| `lt` | 小于 | — | — |

### 8.4 索引状态

| key | 中文 | 配色 |
| --- | --- | --- |
| `not_built` | 未构建 | 灰 |
| `building` | 构建中 | 蓝 + spinner |
| `ready` | 已完成 | 绿 |
| `failed` | 失败 | 红 |

### 8.5 空 / 加载 / 错误态规范

| 场景 | 表现 |
| --- | --- |
| 首屏加载 | `MFSpin` 区块级 18px 居中；表格 6 行 `MFSkeleton` |
| 数据为空 | `MFEmpty` + 引导操作按钮 |
| 请求失败 | `MFAlert` error 置于页面顶部（可关闭）+ message；数据区保留旧数据 |
| 操作失败 | message「操作失败：{原因}」；涉及任务的创建失败用 notification |
| 未授权/库被删 | 重定向到欢迎页 + notification 提示 |

---

## 9. 交互与动效细则

| 场景 | 规格 |
| --- | --- |
| 按钮 hover/active | 100ms 颜色过渡；active 下压 1px |
| 表格行 hover | 背景 `#F9FAFB`，200ms |
| 弹窗/抽屉 | 300ms 缩放/滑入 + 淡入（`cubic-bezier(0.4,0,0.2,1)`） |
| Tab 切换 | 内容 200ms fade；切页重新请求该 Tab 数据 |
| 搜索 | 输入防抖 300ms 后触发（搜索按钮/回车立即触发） |
| 列表搜索 | 前端即时过滤（防抖 150ms） |
| 任务进度轮询 | 存在 running 任务时 2s 轮询；无则停止 |
| 自动刷新开关 | 任务页可选 30s 自动刷新（默认关） |
| 键盘 | 弹窗内 `Esc` 关闭（表单类需二次 Esc）；`Enter` 提交表单；筛选对话框 `Ctrl+Enter` 应用 |
| 拖拽上传 | 拖入高亮（虚线变实线 + 浅底）；离开恢复；松手加入列表 |
| 长文本 | 表格统一 ellipsis + tooltip；内容列两行截断 |
| 聚焦可见性 | 所有可交互元素 focus 显示主色 2px 外环（无障碍） |

---

## 10. 国际化（i18n）规范

> 项目已集成 vue-i18n。所有 UI 文案（含状态、操作符、错误）必须走 i18n，支持 `zh`、`ja`、`en` 三种语言。

```text
common.     (actions: save/cancel/delete/edit/search/reset/export/refresh…, messages: success/fail…)
header.     (systemStatus.normal/abnormal, refresh, userMenu.*)
sidebar.    (newDatabase, searchPlaceholder, databaseList, trash, storage.*)
wizard.     (step.*, type.normal/vector, features.*, name.*)
data.       (toolbar.*, filter.*, view.table/json, columns.*, rowActions.*, pagination.*)
document.   (upload.*, columns.*, status.*, actions.*, drawer.*)
chunk.      (columns.*, actions.*)
task.       (columns.*, status.*, actions.*, log.*)
index.      (info.*, actions.*)
retrieval.  (config.*, result.*)
stats.      (cards.*, charts.*)
trash.      (columns.*, actions.*)
validate.   (required, namePattern, duplicate, jsonError, overlapLessThanChunk, nameMismatch…)
```

- 状态文案映射：`document.status.{key}` / `task.status.{key}` / `index.status.{key}`。
- 操作符映射：`filter.operator.{key}`。
- 初始语言优先级：`localStorage['moofile.locale']` > `navigator.languages` 中首个支持项 > 英文。
- 用户主动切换后立即更新 `<html lang>`、NaiveUI locale/dateLocale、时钟、数字与日期，并持久化选择。
- 三份词典必须保持相同 key 结构；语言选择器的语言名称使用各自原生写法。
- 数字、日期和相对时间统一使用当前 locale 的 `Intl` 格式化。

---

## 11. 开发实施指引

### 11.1 目录结构（建议）

```text
web/src/
├── main.ts / App.vue / style.css
├── i18n.ts                  # zh / ja / en locale 配置与选择优先级
├── router/index.ts          # 路由表（§11.4）
├── api/                     # axios 实例 + 各模块 API（db/data/document/chunk/task/index/retrieval/stats）
├── styles/
│   ├── tokens.ts            # §3 设计令牌
│   └── theme.ts             # NaiveUI themeOverrides（§11.5）
├── constants/
│   ├── status.ts            # §8 状态/操作符/索引状态枚举
│   └── models.ts            # embedding 模型、分页大小等常量
├── components/              # MF* 通用组件（§5）
├── layouts/
│   ├── AppLayout.vue        # §4 全局布局
│   └── parts/               # MFHeader / MFSidebar / MFMain
├── views/
│   ├── db/                  # DataBrowsePage / DocumentsPage / RetrievalPage / StatsPage / VectorSettingsPage
│   │                        # TasksPage；ChunksPage / IndexSettingsPage 当前不公开
│   ├── WelcomeView.vue
│   └── TrashPage.vue
└── dialogs/                 # NewDatabaseWizard / JsonEditDialog / FilterDialog
                             # DeleteDatabaseDialog / UploadDocumentDrawer
                             # VectorizeConfigDialog / TaskLogDrawer / DocumentDetailDrawer / ModelChangeDialog
```

### 11.2 命名与编码规约

- 组件：PascalCase；Props 用 camelCase；事件 `@update:value` 双向绑定统一 `v-model:value`。
- 样式：组件内 `<style scoped>` + CSS 变量（`var(--mf-*)`）；禁止魔法数字。
- 颜色：只允许引用 tokens 或状态常量，禁止在模板里写十六进制。
- 请求：axios 封装统一 loading / 错误 message / 401 跳登录。

### 11.3 数据流与状态管理

- 无需引入 Pinia（当前依赖无 Pinia）；数据库详情数据由页面组件持有，跨 Tab 共享通过「父容器 `DatabaseDetailShell.vue`」下发 props。
- 轮询任务：`useTaskPolling` composable（`{enabled, interval, onData}`），组件卸载自动清理。
- 全局轻状态（侧边栏折叠、当前库）用 `provide/inject`。

### 11.4 路由表

| 路径 | 组件 | 说明 |
| --- | --- | --- |
| `/` | `WelcomeView` | 欢迎页 |
| `/db/:id` | `DatabaseDetailShell` → 子路由 | 详情外壳（Header + Tabs） |
| `/db/:id`（`?tab=data`） | `DataBrowsePage` | 默认 Tab |
| `/db/:id?tab=documents` | `DocumentsPage` | 向量库 |
| `/db/:id/tasks` | `TasksPage` | 向量库 |
| `/db/:id?tab=retrieval` | `RetrievalPage` | 向量库 |
| `/db/:id?tab=stats` | `StatsPage` | 向量库 |
| `/db/:id?tab=settings` | `VectorSettingsPage` | 向量库 |
| `/trash` | `TrashPage` | 回收站 |

路由守卫：`/db/:id` 校验库存在且用户有权限；不存在 → 重定向 `/` + notification。

### 11.5 NaiveUI 主题覆盖（`theme.ts` 核心示例）

```ts
import type { GlobalThemeOverrides } from 'naive-ui'

export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#4F46E5',
    primaryColorHover: '#4338CA',
    primaryColorPressed: '#3730A3',
    primaryColorSuppl: '#4F46E5',
    infoColor: '#2563EB',
    successColor: '#16A34A',
    warningColor: '#F59E0B',
    errorColor: '#DC2626',
    bodyColor: '#F9FAFB',
    cardColor: '#FFFFFF',
    modalColor: '#FFFFFF',
    popoverColor: '#FFFFFF',
    textColorBase: '#111827',
    textColor1: '#111827',
    textColor2: '#374151',
    textColor3: '#6B7280',
    textColorDisabled: '#D1D5DB',
    borderColor: '#E5E7EB',
    dividerColor: '#E5E7EB',
    borderRadius: '8px',
    borderRadiusSmall: '6px',
    fontSize: '14px',
    fontFamily: `Inter, -apple-system, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif`,
    fontFamilyMono: `"JetBrains Mono", Consolas, monospace`,
    boxShadow1: '0 1px 2px rgba(17,24,39,0.05)',
    boxShadow2: '0 4px 6px -1px rgba(17,24,39,0.07), 0 2px 4px -2px rgba(17,24,39,0.05)',
    boxShadow3: '0 10px 15px -3px rgba(17,24,39,0.08), 0 4px 6px -4px rgba(17,24,39,0.04)',
  },
  Button: { heightMedium: '32px', heightLarge: '36px', fontWeight: '500' },
  DataTable: {
    thColor: '#F9FAFB',
    tdColorHover: '#F9FAFB',
    tdColorStriped: '#FFFFFF',
    thFontWeight: '500',
    tdFontSize: '13px',
    thFontSize: '13px',
  },
  Tabs: { tabFontSize: '14px', tabBorderColor: '#E5E7EB', tabTextColor: '#6B7280' },
  Tag: { borderRadius: '999px' },
  Modal: { borderRadius: '12px' },
  Drawer: { borderRadius: '12px 0 0 12px' },
  Input: { border: '1px solid #D1D5DB', borderHover: '1px solid #9CA3AF' },
  Pagination: { itemColorActive: '#4F46E5' },
  Progress: { railColor: '#E5E7EB' },
}
```

### 11.6 依赖建议（需新增）

| 依赖 | 用途 | 说明 |
| --- | --- | --- |
| `monaco-editor` | JSON 编辑器（§5.10） | 体积大，`vite-plugin-monaco-editor` 按需引入 json 语言；可降级 textarea |
| `dayjs` | 相对时间/格式化 | 或原生 `Intl` |
| `pako`（可选） | 导出压缩 | 非必需 |

现有依赖直接复用：`naive-ui`、`@vicons/ionicons5`（图标）、`echarts`（统计图）、`vue-i18n`、`axios`。

---

## 12. 组件清单总表（开发速查）

| 组件 | 类型 | 页面/场景 | 关键 NaiveUI |
| --- | --- | --- | --- |
| `MFButton` | 通用 | 全局 | `n-button` |
| `MFIconButton` | 通用 | Header 刷新、行操作 | `n-button` quaternary |
| `MFTypeTag` / `MFStatusTag` | 通用 | 类型/状态 | `n-tag` |
| `MFInput` / `MFSelect` | 通用 | 搜索/下拉 | `n-input` / `n-select` |
| `MFSegmented` | 通用 | 视图切换 | 自绘 / `n-radio-group` |
| `MFTable` / `MFPagination` | 通用 | 全部列表页 | `n-data-table` / `n-pagination` |
| `MFTextButton` | 通用 | 表格操作列 | `n-button` text |
| `MFFilterBuilder` | 复合 | 数据页/筛选对话框 | `n-select` 等 |
| `MFJsonEditor` | 复合 | JSON 编辑/查看 | `monaco-editor` |
| `MFModal` / `MFDrawer` | 通用 | 全部弹层 | `n-modal` / `n-drawer` |
| `MFStatCard` | 复合 | 详情头部/统计页 | 自绘 |
| `MFTabs` | 通用 | 详情模块切换 | route-controlled buttons |
| `MFEmpty` / `MFSkeleton` / `MFSpin` | 通用 | 空/加载 | `n-empty` / `n-skeleton` / `n-spin` |
| `MFProgress` | 通用 | 上传/任务/存储 | `n-progress` |
| `MFCodeBlock` | 复合 | JSON 视图/查询预览 | 自绘 + `highlight.js` |
| `MFStorageCard` | 复合 | 预留给系统页，当前侧边栏不显示 | `n-progress` |
| `MFClock` / `MFLanguageSelector` / `MFUserMenu` | 复合 | Header | `n-dropdown` / `n-avatar` |
| `NewDatabaseWizardDialog` | 页面级 | 新建数据库 | `n-modal` + `n-steps` |
| `JsonEditDialog` | 页面级 | 新增/编辑 JSON | `n-modal` + `MFJsonEditor` |
| `FilterDialog` | 页面级 | 筛选配置 | `n-modal` + `MFFilterBuilder` |
| `DeleteDatabaseDialog` | 页面级 | 删除数据库 | `n-modal` danger |
| `UploadDocumentDrawer` | 页面级 | 上传文档 | `n-drawer` + `n-upload-dragger` |
| `VectorizeConfigDialog` | 页面级 | 开始向量化 | `n-modal` |
| `TaskLogDrawer` / `DocumentDetailDrawer` / `ModelChangeDialog` | 页面级 | 任务/文档/模型 | `n-drawer` / `n-modal` |
| `VectorSettingsPage` | 页面级 | 向量库默认配置 | `n-form` |

---

## 13. 交付验收清单（前端实现后自检）

- [ ] 设计令牌全部落地为 CSS 变量 + NaiveUI themeOverrides，页面无魔法色值/尺寸
- [ ] Header 64px / Sidebar 280px（折叠 64px）/ 主区 24px padding，三区滚动行为正确
- [ ] 数据库列表选中态（`#EEF2FF` + 3px 主色竖条）与 hover 操作正确
- [ ] 数据页：表格视图/JSON 视图切换、筛选 chips、分页（20/50/100、跳页）可用
- [ ] JSON 编辑器：格式化/校验/复制可用，非法 JSON 阻断保存并提示行号
- [ ] 筛选：AND/OR 切换、添加条件/分组、查询预览实时更新、应用后表格带参刷新
- [ ] 删除数据库：影响清单数字与实际一致，名称不匹配时确认按钮禁用
- [ ] 上传文档：入口位于状态筛选右侧；拖拽/多选/超限拦截可用；请求仅提交文件，完成后状态为「已上传」且未触发向量化（铁律一）
- [ ] 向量化配置 → 任务创建 → 任务页进度轮询 → 文档状态流转（Waiting→Vectorizing→Completed/Failed）
- [x] 检索测试：TopK/阈值生效，默认阈值 0.3；无 Hybrid；最多 4 张卡并内部滚动
- [ ] 向量设置：模型/Chunk/Overlap/TopK/阈值持久化；检索与向量化读取默认值；模型变化明确提示重建影响
- [ ] 统计页 ECharts 配色与 §8 状态色一致，空数据显示空态
- [ ] 全部状态色映射与 §8 表逐项一致
- [x] i18n：zh/ja/en 三语 key 一致；浏览器默认与用户持久化优先级正确；数字/时间本地化
- [x] Help：按当前界面语言渲染对应根目录 README Markdown，切换语言后再次打开内容同步
- [ ] 破坏性操作均有二次确认；键盘 Esc/Enter 行为符合 §9


