# RAIN Desktop — Windows AI 桌面助手

> 基于 Hermes Agent 引擎，集成 PPT 生成、视频制作、代码经验、开发辅助的 Windows 原生 AI 助手

RAIN Desktop 将 Hermes Agent 强大的 AI 对话能力封装为 Windows 桌面应用，内置 **18 个技能**，涵盖 PPT 生成、前端设计、Web 测试、开发调试、代码审查、视频制作等场景。

---

## 🎯 核心能力

| 能力 | 说明 |
|------|------|
| 🤖 **AI 对话** | 支持 OpenAI 兼容 API（DeepSeek、通义千问、Kimi等） |
| 🔧 **工具调用** | 执行命令、读写文件、代码执行、网页搜索 |
| 🛡 **权限管控** | 工作目录外增/改/删操作弹窗确认，realpath+commonpath 安全验证 |
| 🧠 **代码经验** | 跨会话代码记忆，LLM 语义检索 + 自动评分复用 |
| 🎬 **视频生成** | LLM脚本→TTS配音→素材搜索→视频合成，全自动6阶段管线 |
| 📊 **PPT生成** | 网页PPT（归藏风格） + 原生PPTX（PPT Master），双引擎驱动 |

---

## 📋 内置技能（18个）

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

### 视频生成

输入主题自动生成短视频：`LLM脚本 → TTS配音 → 素材搜索 → 视频合成 → 输出MP4`

---

## 📦 安装与构建

### 快速安装

下载安装包运行即可，无需配置 Python 环境：

- **全量安装**：`RAIN_Setup.exe`（~849MB，含Python运行环境+18个技能）
- **增量更新**：`RAIN_Hotfix_Update.exe`（~45MB，覆盖安装现有RAIN）

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

首次运行后，菜单 **设置 → API设置**：

| 设置 | 说明 | 示例 |
|------|------|------|
| API Key | OpenAI 兼容密钥 | `sk-...` |
| Base URL | API 端点 | `https://api.openai.com/v1` |
| 模型 | 模型名称 | `gpt-4o` / `deepseek-chat` |

---

## 🗂 文件结构

```
win_desktop/
├── RAIN_desktop.py          # 主程序（权限检测、代码经验管线、身份识别）
├── code_experience_db.py    # 代码经验向量数据库
├── code_tester.py           # 代码测试评分引擎
├── code_ops_monitor.py      # 操作权限监测系统
├── rain_video_maker.py      # AI视频生成引擎
├── .rain_permissions.json   # 权限规则定义
├── skills/                  # 🔥 内置技能（18个，自动发现）
│   ├── guizang-ppt-skill/   #   归藏PPT（网页HTML）
│   ├── ppt-master/          #   PPT Master（原生PPTX）
│   ├── frontend-design/     #   前端设计
│   ├── webapp-testing/      #   Web应用测试
│   ├── brainstorming/       #   头脑风暴
│   ├── systematic-debugging/#   系统化调试
│   ├── test-driven-development/ # TDD
│   ├── writing-plans/       #   编写计划
│   ├── writing-skills/      #   编写技能
│   └── ... (共18个)
├── build_all.ps1            # 全量+增量一键构建（动态扫描skills）
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
