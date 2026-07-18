# RAIN Agent - Windows 桌面版

> 基于 Hermes Agent 核心，简化为 Windows 桌面 AI 聊天助手

本版本基于Hermes深度优化，带来安全与性能的双重飞跃：

**安全升级**：创新引入"工作目录"机制，实现运行环境的独立隔离，有效防止数据交叉污染，大幅提升文件与系统的安全性。

**极简安装**：全新封装为Windows标准安装包，支持一键部署，提供极简的安装流程，让新手也能零门槛快速上手。

**性能飞跃**：将基础包与核心依赖库提前预置并深度集成至安装包中，实现真正的"开箱即用"。这不仅免去了繁琐的环境配置与二次下载，更显著提升了软件的启动与运行速度。

本次升级旨在为您提供更安全、便捷、高效的极致使用体验。

由江西磐拓智能科技有限公司制作

## 功能

- 🤖 AI 对话（支持 OpenAI 兼容 API）
- 🔧 工具调用：执行命令、读写文件、浏览目录
- 💾 对话历史（SQLite 本地存储）
- 🧠 代码跨会话长期记忆，可增减；历史代码自动评分、相似度匹配复用
- 🛡 操作权限监测，工作目录外操作弹窗确认
- 🎨 暗色主题界面
- 📦 一键打包为独立 EXE

下个版本将对写代码的核心能力进行优化

## 快速开始

### 方式一：直接运行（需要 Python）

```bat
:: 1. 安装依赖
pip install PyQt5 openai

:: 2. 运行
python RAIN_desktop.py
```

### 方式二：打包为 EXE（推荐）

```bat
:: 一键构建
build.bat
```

生成的 EXE 在 `dist\HermesDesktop\HermesDesktop.exe`，直接双击运行。

### 方式三：创建安装包

```bat
:: 需要先安装 NSIS: https://nsis.sourceforge.io/Download
build.bat  :: 选择 Y 创建安装包
```

安装包: `RAIN_Setup.exe`，百度网盘：https://pan.baidu.com/s/1PBztlPmRCz38coHy-AAOJA?pwd=rpp6 提取码: rpp6

## 设置

首次运行后，点击菜单 **设置 → API设置**，填入：

| 设置 | 说明 | 示例 |
|------|------|------|
| API Key | OpenAI 兼容的 API 密钥 | `sk-...` |
| Base URL | API 端点地址 | `https://api.openai.com/v1` |
| 模型 | 模型名称 | `gpt-4o` |

支持的 API 服务商：
- OpenAI: `https://api.openai.com/v1`
- OpenRouter: `https://openrouter.ai/api/v1`
- DeepSeek: `https://api.deepseek.com/v1`
- 通义千问: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- 任何 OpenAI 兼容 API

## 文件结构

```
RAIN-agent/
├── RAIN_desktop.py    # 主程序
├── requirements.txt     # Python 依赖
├── build.bat           # 一键构建脚本
├── check_env.bat       # 环境检查
├── RAIN_desktop.spec  # PyInstaller 配置
├── installer.nsi       # NSIS 安装包脚本
└── icon.ico            # 应用图标
```

## 联系方式

QQ：258129316
