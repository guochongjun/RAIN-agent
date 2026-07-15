# ── Settings Dialog (Tabbed & Beautiful) ────────────────────
class SettingsDialog(QDialog):
    PROVIDERS = [
        ("openai", "OpenAI", "https://api.openai.com/v1"),
        ("openrouter", "OpenRouter", "https://openrouter.ai/api/v1"),
        ("deepseek", "DeepSeek", "https://api.deepseek.com/v1"),
        ("dashscope", "通义千问 (DashScope)", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        ("google", "Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai"),
        ("anthropic", "Anthropic", "https://api.anthropic.com/v1"),
    ]

    TAB_STYLE = (
        "QTabWidget::pane {"
        "  border: 1px solid #313244; border-radius: 0 0 10px 10px;"
        "  background: #1a1a2e; padding: 6px;"
        "}"
        "QTabWidget::tab-bar { left: 4px; }"
        "QTabBar::tab {"
        "  background: #181825; color: #6c7086;"
        "  padding: 8px 18px; border: 1px solid #313244;"
        "  border-bottom: none; border-radius: 8px 8px 0 0;"
        "  margin-right: 2px; font-size: 12px; font-weight: bold;"
        "}"
        "QTabBar::tab:selected {"
        "  background: #1a1a2e; color: #89b4fa;"
        "  border-bottom: 2px solid #89b4fa;"
        "}"
        "QTabBar::tab:hover { background: #313244; color: #cdd6f4; }"
    )

    INPUT_STYLE = (
        "QLineEdit,QSpinBox,QDoubleSpinBox,QComboBox {"
        "  padding: 8px 12px; border-radius: 6px; font-size: 13px;"
        "  background: #11111b; border: 1px solid #313244; color: #cdd6f4;"
        "}"
        "QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus,QComboBox:focus {"
        "  border: 1px solid #89b4fa;"
        "}"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RAIN 设置")
        screen = QApplication.primaryScreen()
        ss = screen.availableSize()
        w = min(560, int(ss.width() * 0.42))
        self.setMinimumSize(w, min(500, int(ss.height() * 0.55)))
        self.setStyleSheet(DARK_STYLE)

        main = QVBoxLayout(self)
        main.setSpacing(10)
        main.setContentsMargins(16, 10, 16, 12)

        # ── Tab widget ──
        tabs = QTabWidget()
        tabs.setStyleSheet(self.TAB_STYLE)

        # ────── Tab 1: API ──────
        t1 = QWidget()
        t1l = QFormLayout(t1)
        t1l.setSpacing(10)
        t1l.setContentsMargins(16, 16, 16, 8)

        self.provider_combo = QComboBox()
        for pid, pname, _ in self.PROVIDERS:
            self.provider_combo.addItem(pname, pid)
        idx = self.provider_combo.findData(settings.get("provider"))
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        t1l.addRow("服务商", self.provider_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("输入 API Key...")
        t1l.addRow("API Key", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.openai.com/v1")
        t1l.addRow("Base URL", self.base_url_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("如 deepseek-chat / gpt-4o")
        t1l.addRow("模型", self.model_input)

        self._on_provider_changed()
        tabs.addTab(t1, "  🌐 API  ")

        # ────── Tab 2: Parameters ──────
        t2 = QWidget()
        t2l = QFormLayout(t2)
        t2l.setSpacing(10)
        t2l.setContentsMargins(16, 16, 16, 8)

        self.max_iter = QSpinBox()
        self.max_iter.setRange(1, 100)
        self.max_iter.setValue(settings.get("max_iterations"))
        t2l.addRow("最大轮数", self.max_iter)

        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(256, 128000)
        self.max_tokens.setValue(settings.get("max_tokens"))
        t2l.addRow("Max Tokens", self.max_tokens)

        self.temp = QDoubleSpinBox()
        self.temp.setRange(0, 2.0)
        self.temp.setSingleStep(0.1)
        self.temp.setValue(settings.get("temperature"))
        t2l.addRow("Temperature", self.temp)
        tabs.addTab(t2, "  ⚙️ 参数  ")

        # ────── Tab 3: Tools ──────
        t3 = QWidget()
        t3l = QFormLayout(t3)
        t3l.setSpacing(10)
        t3l.setContentsMargins(16, 16, 16, 8)

        self.tools_combo = QComboBox()
        self.tools_combo.addItem("全部工具 (推荐)", "all")
        self.tools_combo.addItem("仅聊天 (无工具)", "none")
        self.tools_combo.addItem("安全模式 (只读)", "safe")
        self.tools_combo.addItem("开发模式 (terminal+file)", "development")
        self.tools_combo.addItem("研究模式 (web+vision)", "research")
        idx = self.tools_combo.findData(settings.get("enabled_toolsets"))
        if idx >= 0:
            self.tools_combo.setCurrentIndex(idx)
        t3l.addRow("工具集", self.tools_combo)
        tabs.addTab(t3, "  🔧 工具  ")

        # ────── Tab 4: Workspace ──────
        t4 = QWidget()
        t4l = QVBoxLayout(t4)
        t4l.setSpacing(10)
        t4l.setContentsMargins(16, 16, 16, 8)

        wh = QHBoxLayout()
        self.workspace_input = QLineEdit()
        self.workspace_input.setPlaceholderText("留空=EXE目录，或点击浏览选择...")
        self.workspace_input.setText(settings.get("workspace_dir", ""))
        self.workspace_input.setStyleSheet(self.INPUT_STYLE)
        wh.addWidget(self.workspace_input)
        browse_btn = QPushButton("📂 浏览")
        browse_btn.setStyleSheet(
            "QPushButton{background:#45475a;color:#cdd6f4;border-radius:6px;padding:8px 14px;font-size:12px;}"
            "QPushButton:hover{background:#585b70;}")
        browse_btn.clicked.connect(self._browse_workspace)
        wh.addWidget(browse_btn)
        t4l.addLayout(wh)

        tip = QLabel("技能、脚本、生成文件等放在此目录\nAI 可自由读写，无需授权确认")
        tip.setStyleSheet("color:#6c7086;font-size:11px;padding:4px 0;")
        tip.setWordWrap(True)
        t4l.addWidget(tip)
        t4l.addStretch()
        tabs.addTab(t4, "  📁 目录  ")

        # ────── Tab 5: System Prompt ──────
        t5 = QWidget()
        t5l = QVBoxLayout(t5)
        t5l.setContentsMargins(16, 16, 16, 8)
        self.sys_prompt = QPlainTextEdit()
        self.sys_prompt.setPlainText(settings.get("system_prompt"))
        self.sys_prompt.setPlaceholderText("自定义 AI 的系统提示词...")
        self.sys_prompt.setMinimumHeight(80)
        self.sys_prompt.setStyleSheet(
            "QPlainTextEdit{background:#11111b;border:1px solid #313244;border-radius:8px;"
            "padding:10px;font-size:12px;color:#cdd6f4;}")
        t5l.addWidget(self.sys_prompt)
        tabs.addTab(t5, "  💬 提示词  ")

        main.addWidget(tabs)

        # Apply input styling to all form fields
        for w in self.findChildren((QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)):
            if w is not self.workspace_input:
                w.setStyleSheet(self.INPUT_STYLE)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(
            "QPushButton{background:#313244;color:#a6adc8;border-radius:8px;"
            "padding:9px 24px;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#45475a;color:#cdd6f4;}")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("💾 保存设置")
        save_btn.setStyleSheet(
            "QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:8px;"
            "padding:9px 28px;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#b4befe;}")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        main.addLayout(btn_row)

    def _on_provider_changed(self):
        pid = self.provider_combo.currentData()
        self.api_key_input.setText(settings.get(f"{pid}_key", "") or settings.get("api_key", ""))
        for pvid, _, url in self.PROVIDERS:
            if pvid == pid:
                saved_url = settings.get("base_url", "")
                self.base_url_input.setText(saved_url if saved_url and saved_url != "https://api.openai.com/v1" else url)
                break
        self.model_input.setText(settings.get("model", ""))

    def _save(self):
        pid = self.provider_combo.currentData()
        settings.set("provider", pid)
        settings.set("api_key", self.api_key_input.text().strip())
        settings.set(f"{pid}_key", self.api_key_input.text().strip())
        settings.set("base_url", self.base_url_input.text().strip())
        settings.set("model", self.model_input.text().strip())
        settings.set("max_iterations", self.max_iter.value())
        settings.set("max_tokens", self.max_tokens.value())
        settings.set("temperature", self.temp.value())
        settings.set("enabled_toolsets", self.tools_combo.currentData())
        settings.set("system_prompt", self.sys_prompt.toPlainText().strip())
        settings.set("workspace_dir", self.workspace_input.text().strip())
        self.accept()

    def _browse_workspace(self):
        from PyQt5.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, "选择工作目录", self.workspace_input.text() or os.path.expanduser("~"))
        if d:
            self.workspace_input.setText(d)

