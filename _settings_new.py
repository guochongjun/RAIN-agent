# ── Settings Dialog (Flat & Modern) ─────────────────────────
class SettingsDialog(QDialog):
    PROVIDERS = [
        ("openai", "OpenAI", "https://api.openai.com/v1"),
        ("openrouter", "OpenRouter", "https://openrouter.ai/api/v1"),
        ("deepseek", "DeepSeek", "https://api.deepseek.com/v1"),
        ("dashscope", "通义千问 (DashScope)", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        ("google", "Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai"),
        ("anthropic", "Anthropic", "https://api.anthropic.com/v1"),
    ]

    GROUP_STYLE = (
        "QGroupBox {"
        "  background: #1a1a2e; border: 1px solid #313244; border-radius: 10px;"
        "  margin-top: 14px; padding: 20px 16px 14px 16px;"
        "  font-size: 13px; font-weight: bold; color: #89b4fa;"
        "}"
        "QGroupBox::title {"
        "  subcontrol-origin: margin; left: 14px; padding: 0 10px;"
        "  background: #1a1a2e; border-radius: 6px;"
        "}"
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
        self.setMinimumWidth(w)
        self.setMinimumHeight(min(680, int(ss.height() * 0.70)))
        self.setStyleSheet(DARK_STYLE)

        main = QVBoxLayout(self)
        main.setSpacing(12)
        main.setContentsMargins(20, 14, 20, 14)

        # Scroll area for small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{width:6px;background:#181825;border-radius:3px;}"
            "QScrollBar::handle:vertical{background:#45475a;border-radius:3px;min-height:30px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}"
        )
        body_w = QWidget()
        body_w.setStyleSheet("background:transparent;")
        body = QVBoxLayout(body_w)
        body.setSpacing(12)

        # ── API ──
        g1 = QGroupBox("  🌐  API 设置")
        g1.setStyleSheet(self.GROUP_STYLE)
        l1 = QFormLayout(g1)
        l1.setSpacing(10)

        self.provider_combo = QComboBox()
        for pid, pname, _ in self.PROVIDERS:
            self.provider_combo.addItem(pname, pid)
        idx = self.provider_combo.findData(settings.get("provider"))
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        l1.addRow("服务商", self.provider_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("输入 API Key...")
        l1.addRow("API Key", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.openai.com/v1")
        l1.addRow("Base URL", self.base_url_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("如 deepseek-chat / gpt-4o")
        l1.addRow("模型", self.model_input)

        self._on_provider_changed()
        body.addWidget(g1)

        # ── Parameters ──
        g2 = QGroupBox("  ⚙️  模型参数")
        g2.setStyleSheet(self.GROUP_STYLE)
        l2 = QFormLayout(g2)
        l2.setSpacing(10)

        self.max_iter = QSpinBox()
        self.max_iter.setRange(1, 100)
        self.max_iter.setValue(settings.get("max_iterations"))
        l2.addRow("最大轮数", self.max_iter)

        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(256, 128000)
        self.max_tokens.setValue(settings.get("max_tokens"))
        l2.addRow("Max Tokens", self.max_tokens)

        self.temp = QDoubleSpinBox()
        self.temp.setRange(0, 2.0)
        self.temp.setSingleStep(0.1)
        self.temp.setValue(settings.get("temperature"))
        l2.addRow("Temperature", self.temp)
        body.addWidget(g2)

        # ── Tools ──
        g3 = QGroupBox("  🔧  工具配置")
        g3.setStyleSheet(self.GROUP_STYLE)
        l3 = QFormLayout(g3)
        l3.setSpacing(10)

        self.tools_combo = QComboBox()
        self.tools_combo.addItem("全部工具 (推荐)", "all")
        self.tools_combo.addItem("仅聊天 (无工具)", "none")
        self.tools_combo.addItem("安全模式 (只读)", "safe")
        self.tools_combo.addItem("开发模式 (terminal+file)", "development")
        self.tools_combo.addItem("研究模式 (web+vision)", "research")
        idx = self.tools_combo.findData(settings.get("enabled_toolsets"))
        if idx >= 0:
            self.tools_combo.setCurrentIndex(idx)
        l3.addRow("工具集", self.tools_combo)
        body.addWidget(g3)

        # ── Workspace ──
        g4 = QGroupBox("  📁  工作目录")
        g4.setStyleSheet(self.GROUP_STYLE)
        l4 = QFormLayout(g4)
        l4.setSpacing(10)

        wh = QHBoxLayout()
        self.workspace_input = QLineEdit()
        self.workspace_input.setPlaceholderText("留空=EXE目录，或点击浏览选择...")
        self.workspace_input.setText(settings.get("workspace_dir", ""))
        wh.addWidget(self.workspace_input)
        browse_btn = QPushButton("📂 浏览")
        browse_btn.setStyleSheet(
            "QPushButton{background:#45475a;color:#cdd6f4;border-radius:6px;padding:8px 14px;font-size:12px;}"
            "QPushButton:hover{background:#585b70;}")
        browse_btn.clicked.connect(self._browse_workspace)
        wh.addWidget(browse_btn)
        l4.addRow("路径", wh)
        tip = QLabel("技能、脚本、生成文件等放在此目录，AI 可自由读写")
        tip.setStyleSheet("color:#6c7086;font-size:11px;margin-top:2px;")
        l4.addRow("", tip)
        body.addWidget(g4)

        # ── System Prompt ──
        g5 = QGroupBox("  💬  系统提示词")
        g5.setStyleSheet(self.GROUP_STYLE)
        l5 = QVBoxLayout(g5)
        self.sys_prompt = QPlainTextEdit()
        self.sys_prompt.setPlainText(settings.get("system_prompt"))
        self.sys_prompt.setPlaceholderText("自定义 AI 的系统提示词...")
        self.sys_prompt.setMinimumHeight(90)
        self.sys_prompt.setStyleSheet(
            "QPlainTextEdit{background:#11111b;border:1px solid #313244;border-radius:8px;padding:10px;font-size:12px;color:#cdd6f4;}")
        l5.addWidget(self.sys_prompt)
        body.addWidget(g5)

        # Apply input styling to all
        for w in self.findChildren((QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)):
            w.setStyleSheet(self.INPUT_STYLE)

        body.addStretch()
        scroll.setWidget(body_w)
        main.addWidget(scroll)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(
            "QPushButton{background:#313244;color:#a6adc8;border-radius:8px;padding:10px 28px;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#45475a;color:#cdd6f4;}")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("💾 保存设置")
        save_btn.setObjectName("sendBtn")
        save_btn.setStyleSheet(
            "QPushButton#sendBtn{background:#89b4fa;color:#1e1e2e;border-radius:8px;padding:10px 32px;font-size:13px;font-weight:bold;}"
            "QPushButton#sendBtn:hover{background:#b4befe;}")
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

