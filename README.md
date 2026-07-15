# Hermes Desktop - Windows 桌面版

> 基于 Hermes Agent 核心，简化为 Windows 桌面 AI 聊天助手

## 功能

- 🤖 AI 对话（支持 OpenAI 兼容 API）
- 🔧 工具调用：执行命令、读写文件、浏览目录
- 💾 对话历史（SQLite 本地存储）
- 🎨 暗色主题界面
- 📦 一键打包为独立 EXE

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

安装包: `HermesDesktop_Setup.exe`，百度网盘：https://pan.baidu.com/s/1PBztlPmRCz38coHy-AAOJA?pwd=rpp6 提取码: rpp6

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
win_desktop/
├── RAIN_desktop.py    # 主程序
├── requirements.txt     # Python 依赖
├── build.bat           # 一键构建脚本
├── check_env.bat       # 环境检查
├── RAIN_desktop.spec  # PyInstaller 配置
├── installer.nsi       # NSIS 安装包脚本
└── icon.ico            # 应用图标
```
