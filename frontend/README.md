# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

## 架构示例

```text
src/
├── assets/          # 静态资源（图片、图标、样式）
├── components/      # 通用基础组件（按钮、弹窗、输入框）
│   └── Markdown/    # 专门渲染 Agent 回答的 Markdown 组件
├── composables/     # 组合式函数（如 useSSE 处理流式打字机效果）
├── router/          # 路由配置（聊天、工作流、知识库）
├── stores/          # Pinia 状态管理
│   ├── chat.ts      # 聊天记录、当前会话
│   └── agent.ts     # 当前 Agent 的配置（Prompt、Temperature 等）
├── views/           # 页面级组件
│   ├── ChatView.vue       # 核心对话窗口
│   ├── AgentConfig.vue    # Agent 编排/配置页
│   └── KnowledgeView.vue  # 知识库管理页
├── App.vue
└──
```
