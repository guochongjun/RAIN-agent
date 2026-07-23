# RAIN Desktop — Windows AI 桌面助手

> 基于 Hermes Agent 引擎，集成 PPT 生成、视频制作、代码经验、知识经验、自学习技能收割的 Windows 原生 AI 助手

RAIN Desktop 将 Hermes Agent 强大的 AI 对话能力封装为 Windows 桌面应用，内置 **19 个技能**，涵盖 PPT 生成、前端设计、Web 测试、开发调试、代码审查、视频制作、自学习等场景。

---

## 🎯 核心能力

| 能力 | 说明 |
|------|------|
| 🤖 **AI 对话** | 支持 OpenAI 兼容 API（DeepSeek、通义千问、Kimi等） |
| 🔧 **工具调用** | 执行命令、读写文件、代码执行、网页搜索 |
| 🛡 **权限管控** | 工作目录外增/改/删操作弹窗确认，realpath+commonpath 安全验证 |
| 🧠 **代码经验** | 跨会话代码记忆，LLM 语义检索 + 自动评分复用 + 每轮实时三段注入 |
| 📚 **知识经验** | 🆕 会话级 Q&A 自动提取存储，每轮相似度检索辅助回复，6个月自动清理 |
| 🌟 **自学习收割** | 会话关闭时自动检测黄金路径，生成可复用技能（SKILL.md） |
| 🎬 **视频生成** | LLM脚本→TTS配音→素材搜索→视频合成，全自动6阶段管线 |
| 📊 **PPT生成** | 网页PPT（归藏风格） + 原生PPTX（PPT Master），双引擎驱动 |

---

## 📋 内置技能（20个）

### PPT 生成

| 技能 | 输出 | 风格 | 场景 |
|------|------|------|------|
| **guizang-ppt-skill** | 单文件 HTML | 电子杂志风 / 瑞士国际主义风 | 快速分享、演讲、网页发布 |
| **ppt-master** | 原生 .pptx | 多模板（20+示例） | 正式汇报、企业文档、PowerPoint编辑 |

### 前端与测试

| 技能 | 来源 | 说明 |
|------|------|------|
| **frontend-design** | Anthropic | 前端界面设计，HTML/CSS/React 组件生成 |
| **webapp-testing** | Anthropic | Web 应用测试，Playwright 自动化测试 |

### 开发辅助（Superpowers）

| 技能 | 说明 |
|------|------|
| **brainstorming** | 头脑风暴，创意发散与方案探索 |
| **dispatching-parallel-agents** | 并行代理调度，多任务并发执行 |
| **executing-plans** | 计划执行，按步骤落实开发方案 |
| **finishing-a-development-branch** | 开发分支收尾，合并前检查 |
| **receiving-code-review** | 接收代码审查，处理审查意见 |
| **requesting-code-review** | 请求代码审查，提交前自检 |
| **subagent-driven-development** | 子代理驱动开发，委托子任务 |
| **systematic-debugging** | 系统化调试，4阶段根因分析 |
| **test-driven-development** | 测试驱动开发，红-绿-重构循环 |
| **using-git-worktrees** | Git Worktree 并行分支开发 |
| **using-superpowers** | Superpowers 技能使用指南 |
| **verification-before-completion** | 完成前验证，确保交付质量 |
| **writing-plans** | 编写实现计划，任务分解 |
| **writing-skills** | 编写 Agent 技能文件 |

### 自学习

| 技能 | 说明 |
|------|------|
| **self-learning** | 🆕 元技能 — Agent 自主识别黄金路径并收割为可复用技能 |

### 视频生成

输入主题自动生成短视频：`LLM脚本 → TTS配音 → 素材搜索 → 视频合成 → 输出MP4`

### 模块组合（Dify Module Composer）🆕

| 技能 | 说明 |
|------|------|
| **difymc** | 🆕 Dify模块组合工具 — 将Dify应用/工作流封装为可组合模块，支持语义检索、自动编排、新模块自增长。对应专利《基于智能体的代码功能模块组合方法与系统》 |

> **10 个工具接口**：list_modules / search_modules / get_module / register_module / compose_and_run / execute_module / extract_module / module_relations / get_agent_context / import_from_dify

---

## 🧠 代码经验管线（v3）

每轮对话检测代码意图，自动执行完整管线：

```
用户提问 → 代码意图检测
  ├─ 精确匹配优先（完全相同 → 100%）
  ├─ LLM 语义搜索历史经验库（DeepSeek 语义匹配）
  ├─ 相似度 ≥ 阈值（默认 0.80）→ 三段合并注入 prompt：
  │   ┌───────────────────────────────────────┐
  │   │ 【历史最优代码（经验库）】              │
  │   │ 【本轮之前生成的代码（当前会话）】        │
  │   │ 用户原始问题                            │
  │   └───────────────────────────────────────┘
  └─ 模型基于历史+会话代码优化生成
```

| 特性 | 说明 |
|------|------|
| 触发时机 | **每轮**代码意图（不限首轮） |
| 匹配方式 | 精确匹配优先 → LLM 语义匹配 |
| 注入内容 | 历史代码 + 会话代码 + 用户需求，三段合并 |
| 相似度阈值 | 默认 **0.80**，可在设置中调整 `code_exp_threshold` |
| 自动保存 | 会话关闭时自动测试评分 → LLM总结 → 入库 |
| JSON安全 | `_safe_json_loads` 全局防护，防 int 类型崩溃 |

---

## 📚 知识经验系统（v1）🆕

会话关闭时自动提取问答对存入知识库，新会话按相似度检索辅助回复：

```
会话关闭 → LLM提取Q&A对 → knowledge_items 表
     ↓
每轮对话 → TF-IDF搜索 → 相似度 ≥ 阈值 → 注入历史答案到系统消息
     ↓
启动时 → 清理 last_accessed < 6个月 的过期条目
```

| 特性 | 说明 |
|------|------|
| 触发时机 | 会话关闭时 LLM 提取最近 20 轮对话的 Q&A 对 |
| 检索方式 | TF-IDF 向量相似度，每轮对话自动检索 |
| 相似度阈值 | 默认 **0.80**，可在设置中调整 `knowledge_exp_threshold` |
| 注入内容 | 匹配的历史答案注入系统消息，与当前会话回答合并 |
| 过期清理 | **6个月**未被调用的条目自动删除，启动时执行 |
| 手动管理 | 设置菜单 → 📋 知识经验管理（查看/删除/清理） |
| 存储位置 | `%LOCALAPPDATA%\RAIN\code_experience.db` → `knowledge_items` 表 |

---

## 🌟 自学习技能收割

会话关闭时自动执行晋升规则检测，满足条件则收割为技能：

| 晋升条件 | 检测方式 |
|----------|----------|
| ✅ 可验证通过 | 代码评分 ≥ 50（Python测试）或 ≥ 10（HTML基础） |
| ✅ 失败模式 | 会话中出现 Error/Traceback/失败 等关键词 |
| ✅ 排除死路 | 用户说过"不对/不行/重新/修正"等纠正词 |

收割产出：`skills/learned-*/SKILL.md`，含代码 + gotchas + 死路，下次会话自动加载。

---

## 📦 安装与构建

### 快速安装

下载安装包运行即可，无需配置 Python 环境：

- **全量安装**：`RAIN_Setup.exe`（~849MB，含Python运行环境+19个技能）
- **增量更新**：`RAIN_Hotfix_Update.exe`（~45MB，覆盖安装现有RAIN）
- **模块组合**：`dify-module-composer.zip` （Dify Module Composer）
百度网盘：https://pan.baidu.com/s/1PBztlPmRCz38coHy-AAOJA?pwd=rpp6

### 开发者构建

```powershell
# 一键构建（增量+全量）
powershell -ExecutionPolicy Bypass -File build_all.ps1

# 仅构建增量包
"C:\Program Files (x86)\NSIS\makensis.exe" hotfix.nsi

# 仅构建全量包（需先更新 dist/hermes-agent.7z）
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

> `build_all.ps1` 和 `hotfix.nsi` 已改为**动态扫描** `skills/` 目录，新增技能无需手动修改脚本。

---

## ⚙️ 设置

首次运行后，菜单 **设置**：

| 设置项 | 说明 | 默认值 |
|--------|------|--------|
| API Key | OpenAI 兼容密钥 | — |
| Base URL | API 端点 | `https://api.deepseek.com` |
| 模型 | 模型名称 | `deepseek-v4-flash` |
| 🧠 代码经验库 | 启用/阈值/自动保存/复核 | 启用 / 0.80 |
| 📚 知识经验库 | 启用/相似度阈值 | 启用 / 0.80 |

---

## 🗂 文件结构

```
win_desktop/
├── RAIN_desktop.py          # 主程序（代码经验v3、知识经验v1、自学习收割、权限检测）
├── code_experience_db.py    # 数据库（code_experiences + knowledge_items + golden_paths）
├── code_tester.py           # 代码测试评分引擎
├── code_ops_monitor.py      # 操作权限监测系统
├── rain_video_maker.py      # AI视频生成引擎
├── .rain_permissions.json   # 权限规则定义
├── skills/                  # 🔥 内置技能（19个，自动发现）
│   ├── guizang-ppt-skill/   #   归藏PPT（网页HTML）
│   ├── ppt-master/          #   PPT Master（原生PPTX）
│   ├── self-learning/       #   🆕 自学习元技能
│   ├── frontend-design/     #   前端设计
│   ├── webapp-testing/      #   Web应用测试
│   ├── brainstorming/       #   头脑风暴
│   ├── systematic-debugging/#   系统化调试
│   ├── test-driven-development/ # TDD
│   ├── writing-plans/       #   编写计划
│   ├── writing-skills/      #   编写技能
│   ├── dispatching-parallel-agents/  # 并行代理
│   ├── executing-plans/     #   计划执行
│   ├── finishing-a-development-branch/ # 分支收尾
│   ├── receiving-code-review/   # 接收审查
│   ├── requesting-code-review/  # 请求审查
│   ├── subagent-driven-development/ # 子代理开发
│   ├── using-git-worktrees/   # Git Worktree
│   ├── using-superpowers/     # 技能指南
│   └── verification-before-completion/ # 完成验证
├── dify-module-composer/    # 🆕 Dify模块组合工具
│   ├── difymc_server.py     #   MCP工具服务器 + CLI
│   ├── difymc/              #   核心库（schema/client/library/composer/extractor）
│   ├── modules/             #   模块存储（JSON）
│   └── mcp_config.yaml      #   MCP配置模板
├── build_all.ps1            # 全量+增量一键构建（动态扫描skills+difymc）
├── hotfix.nsi               # 增量热修复（File /r 递归复制skills）
├── installer.nsi            # 全量安装包
├── vendor/                  # 工具链（7z、Git Bash、FFmpeg）
└── icon.ico                 # 应用图标
```

---

## 🛡 权限控制

| 操作 | 行为 |
|------|------|
| 读取（read_file/search_files/session_search/vision_analyze） | 🟢 直接放通 |
| 写入/删除/终端/代码执行 涉及工作目录外 | 🟡 弹窗确认 |
| locked_down / RAIN_DENIED | 🔴 直接拒绝 |

---

## 📧 联系方式

江西磐拓智能科技有限公司  
QQ：258129316
