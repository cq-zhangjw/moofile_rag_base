# Vite + Svelte + shadcn-svelte 最小化 Demo + Vue3 语法对比总结

> 原文链接：https://blog.csdn.net/qq_36991535/article/details/161600830
> 发布时间：2026-06-01 20:41:10
> 作者：Anesthesia丶

## 一、环境准备

确保已安装：

- Node.js >= 18.0.0
- npm / pnpm / yarn（推荐 pnpm）

## 二、创建 Svelte + Vite 项目

```bash
# 1. 创建项目
npm create vite@latest my-shadcn-svelte-demo -- --template svelte

# 2. 进入项目
cd my-shadcn-svelte-demo

# 3. 安装依赖
npm install
```

## 三、安装 Tailwind CSS（shadcn-svelte 必需）

shadcn-svelte 基于 Tailwind，必须先配置：

> **注意：这里必须使用 `tailwindcss@3`，如果不带版本 `@3`，默认会安装 `tailwindcss@4`，会导致无法生成配置文件。**

```bash
# 安装依赖
npm install -D tailwindcss@3 postcss autoprefixer

# 生成配置文件
npx tailwindcss init -p
```

### 1. 修改 `tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 2. 修改 `src/app.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3. 在 `src/routes/+layout.svelte` 引入样式

```svelte
<script>
  import '../app.css';
</script>

<slot />
```

## 四、安装 shadcn-svelte

```bash
# 安装 shadcn-svelte
npm install -D shadcn-svelte
```

### 初始化配置

```bash
npx shadcn-svelte@latest init
```

按回车使用**默认配置**即可：

- 组件目录：`$lib/components/ui`
- 工具类路径：`$lib/utils.ts`

## 五、添加一个 shadcn 组件（测试用）

我们安装最常用的 **Button** 组件验证：

```bash
npx shadcn-svelte@latest add button
```

## 六、编写最小化 Demo 页面

替换 `src/routes/+page.svelte`：

```svelte
<script>
  // 引入 shadcn 按钮组件
  import { Button } from '$lib/components/ui/button';
</script>

<div class="min-h-screen flex items-center justify-center flex-col gap-4">
  <h1 class="text-2xl font-bold">Vite + Svelte + shadcn-svelte</h1>

  <!-- 使用 shadcn 按钮 -->
  <Button>我是 shadcn 按钮</Button>
  <Button variant="destructive">危险按钮</Button>
  <Button variant="outline">轮廓按钮</Button>
</div>
```

## 七、启动项目

```bash
npm run dev
```

打开 `http://localhost:5173`

看到页面 + 可正常点击的 shadcn 按钮 = 搭建成功！

## 项目结构（最小化）

```
src/
├── lib/
│   ├── components/
│   │   └── ui/          # shadcn 组件存放位置
│   └── utils.ts         # shadcn 工具函数
├── routes/
│   ├── +layout.svelte   # 全局布局（引入样式）
│   └── +page.svelte     # 首页
└── app.css              # Tailwind 样式
```

## 八、Svelte vs Vue3 语法核心区别

### 1. 最本质区别

- **Vue3**：虚拟 DOM + 响应式系统（需要 `ref/reactive`）
- **Svelte**：编译时框架，**无虚拟 DOM**，**不用写响应式 API**，代码更少

### 2. 变量定义（最大区别）

**Vue3：**

```vue
<script setup>
import { ref } from 'vue'
const count = ref(0) // 必须用 ref
</script>
```

**Svelte：**

```svelte
<script>
  let count = 0 // 直接写，自动响应式
</script>
```

Svelte 胜：不用导入、不用包裹，天然响应式。

### 3. 模板渲染

**Vue3：**

```vue
<template>
  <div>{{ count }}</div>
</template>
```

**Svelte：**

```svelte
<div>{count}</div>
```

语法几乎一样，只是 Svelte **不需要 `<template>` 根标签**。

### 4. 事件绑定

**Vue3：**

```vue
<button @click="count++">点击</button>
```

**Svelte：**

```svelte
<button on:click={() => count++}>点击</button>
```

- Vue：`@click`
- Svelte：`on:click`

### 5. 条件渲染

**Vue3：**

```vue
<div v-if="count > 0">大于0</div>
<div v-else>小于0</div>
```

**Svelte：**

```svelte
{#if count > 0}
  <div>大于0</div>
{:else}
  <div>小于0</div>
{/if}
```

Svelte 更接近原生模板语法。

### 6. 循环渲染

**Vue3：**

```vue
<div v-for="item in list" :key="item">{{ item }}</div>
```

**Svelte：**

```svelte
{#each list as item (item)}
  <div>{item}</div>
{/each}
```

- Vue 必须写 `key`
- Svelte `(item)` 是 key，**不强制但推荐**

### 7. Props 传值

**Vue3：**

```vue
<script setup>
const props = defineProps({ title: String })
</script>
```

**Svelte：**

```svelte
<script>
  export let title;
</script>
```

Svelte 极简：直接 `export let` 就是 props。

### 8. 计算属性

**Vue3：**

```js
import { computed } from 'vue'
const double = computed(() => count * 2)
```

**Svelte：**

```svelte
$: double = count * 2
```

一行搞定，**`$:` 自动依赖追踪**。

### 9. 监听属性

**Vue3：**

```js
import { watch } from 'vue'
watch(count, (val) => { console.log(val) })
```

**Svelte：**

```svelte
$: console.log(count)
```

还是 `$:`，不用 API，不用导入。

### 10. 双向绑定

**Vue3：**

```vue
<input v-model="count" />
```

**Svelte：**

```svelte
<input bind:value={count} />
```

### 11. 样式作用域

**Vue3：**自动 scoped，无需处理。

**Svelte：**

```svelte
<style>
  /* 自动作用域，不用写 scoped */
</style>
```

## 总结

Vue 转 Svelte，记住这 3 条就够了：

1. **let 变量 = 自动响应式**
2. **`$:` = 计算属性 + 监听器**
3. **`export let` = props**
