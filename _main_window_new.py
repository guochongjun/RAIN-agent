# ── Main Window (Beautiful) ────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, username=""):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {username}" if username else f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(700, 450)
        screen = QApplication.primaryScreen()
        ss = screen.availableSize()
        dw = max(800, int(ss.width() * 0.60))
        dh = max(600, int(ss.height() * 0.65))
        self.setMinimumSize(800, 600)
        self.resize(settings.get("window_w", dw), settings.get("window_h", dh))
        self.move(settings.get("window_x"), settings.get("window_y"))

        self.worker: RAINWorker = None
        self._response_buffer = ""
        self._assistant_block_started = False
        self._current_tool_block = ""
        self.current_sid = None
        self._heartbeat_count = 0

        # Heartbeat timer to confirm event loop is alive
        self._hb_timer = QTimer(self)
        self._hb_timer.timeout.connect(self._heartbeat)
        self._hb_timer.start(5000)

        self._build_ui()
        self._build_menu()
        self._build_statusbar()
        self._init_db()
        self._refresh_sessions()
        self._new_session()

        # Start file system guard for non-workspace monitoring
        fs_guard.alert.connect(self._on_fs_alert)
        fs_guard.start()

    def _on_fs_alert(self, action, path):
        self._append_system(f"🛡 监控: 检测到外部{action}操作\n{path}")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        ml = QHBoxLayout(central)
        ml.setContentsMargins(4, 4, 4, 4)
        ml.setSpacing(4)

        # ── Left sidebar ──
        left = QWidget()
        left.setFixedWidth(190)
        left.setStyleSheet("QWidget{background:#11111b;border-radius:10px;}")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 10, 8, 10)
        ll.setSpacing(8)

        history_label = QLabel("  📋  对话历史")
        history_label.setStyleSheet("color:#89b4fa;font-size:12px;font-weight:bold;padding:2px;")
        ll.addWidget(history_label)

        self.session_list = QListWidget()
        self.session_list.setStyleSheet(
            "QListWidget{background:#181825;border:1px solid #313244;border-radius:8px;"
            "padding:4px;font-size:12px;color:#cdd6f4;outline:none;}"
            "QListWidget::item{padding:8px 10px;border-radius:6px;}"
            "QListWidget::item:hover{background:#313244;}"
            "QListWidget::item:selected{background:#45475a;color:#89b4fa;}")
        self.session_list.itemClicked.connect(self._on_session_click)
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._on_session_right_click)
        ll.addWidget(self.session_list)

        new_btn = QPushButton("＋ 新对话")
        new_btn.setStyleSheet(
            "QPushButton{background:#313244;color:#cdd6f4;border-radius:8px;"
            "padding:8px;font-size:12px;font-weight:bold;}"
            "QPushButton:hover{background:#45475a;}")
        new_btn.clicked.connect(self._new_session)
        ll.addWidget(new_btn)

        self.engine_label = QLabel()
        self.engine_label.setWordWrap(True)
        self.engine_label.setStyleSheet("color:#6c7086;font-size:10px;padding:4px;")
        self._update_engine_label()
        ll.addWidget(self.engine_label)

        ml.addWidget(left)

        # ── Right: Chat ──
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Microsoft YaHei", 11))
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setLineWrapMode(QTextEdit.WidgetWidth)
        self.chat_display.setStyleSheet(
            "QTextEdit{background:#11111b;border:1px solid #313244;border-radius:10px;"
            "padding:10px;color:#cdd6f4;}")
        rl.addWidget(self.chat_display)

        # ── Input bar ──
        input_bar = QWidget()
        input_bar.setStyleSheet("QWidget{background:#181825;border-radius:10px;}")
        il = QHBoxLayout(input_bar)
        il.setContentsMargins(8, 6, 6, 6)
        il.setSpacing(6)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入消息，Enter 发送...")
        self.input_box.setFont(QFont("Microsoft YaHei", 11))
        self.input_box.setStyleSheet(
            "QLineEdit{background:#11111b;border:1px solid #313244;border-radius:8px;"
            "padding:10px 14px;color:#cdd6f4;font-size:13px;}"
            "QLineEdit:focus{border:1px solid #89b4fa;}")
        self.input_box.returnPressed.connect(self._send)
        il.addWidget(self.input_box)

        self.send_btn = QPushButton("🚀 发送")
        self.send_btn.setStyleSheet(
            "QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:8px;"
            "padding:10px 20px;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#b4befe;}"
            "QPushButton:pressed{background:#74c7ec;}")
        self.send_btn.clicked.connect(self._send)
        self.send_btn.setFixedWidth(90)
        il.addWidget(self.send_btn)

        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet(
            "QPushButton{background:#f38ba8;color:#1e1e2e;border-radius:8px;"
            "padding:10px 16px;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#fab387;}")
        self.stop_btn.clicked.connect(self._stop)
        self.stop_btn.setFixedWidth(76)
        self.stop_btn.hide()
        il.addWidget(self.stop_btn)

        rl.addWidget(input_bar)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(3)
        self.progress.setStyleSheet(
            "QProgressBar{border:none;background:transparent;}"
            "QProgressBar::chunk{background:#89b4fa;border-radius:2px;}")
        self.progress.hide()
        rl.addWidget(self.progress)

        ml.addWidget(right)

    def _build_menu(self):
        mb = self.menuBar()
        mb.setStyleSheet(
            "QMenuBar{background:#11111b;color:#cdd6f4;border-bottom:1px solid #313244;"
            "padding:2px 8px;font-size:13px;}"
            "QMenuBar::item{padding:6px 12px;border-radius:6px;}"
            "QMenuBar::item:selected{background:#313244;}"
            "QMenu{background:#1a1a2e;color:#cdd6f4;border:1px solid #313244;border-radius:8px;"
            "padding:4px;}"
            "QMenu::item{padding:8px 28px;border-radius:6px;font-size:12px;}"
            "QMenu::item:selected{background:#313244;color:#89b4fa;}"
            "QMenu::separator{height:1px;background:#313244;margin:4px 12px;}")

        f = mb.addMenu("  文件  ")
        a = QAction("📄 新对话", self)
        a.setShortcut(QKeySequence("Ctrl+N"))
        a.triggered.connect(self._new_session)
        f.addAction(a)
        a = QAction("💾 导出对话", self)
        a.setShortcut(QKeySequence("Ctrl+S"))
        a.triggered.connect(self._export)
        f.addAction(a)
        f.addSeparator()
        a = QAction("🚪 退出", self)
        a.setShortcut(QKeySequence("Ctrl+Q"))
        a.triggered.connect(self._logout)
        f.addAction(a)

        s = mb.addMenu("  设置  ")
        s.addAction("🔑 API & 模型设置...", self._show_settings)
        s.addSeparator()
        s.addAction("🗑 清除对话数据", self._clear_data)

        h = mb.addMenu("  帮助  ")
        h.addAction("ℹ 关于", self._about)

    def _build_statusbar(self):
        self.sb = QStatusBar()
        self.sb.setStyleSheet(
            "QStatusBar{background:#11111b;color:#a6adc8;border-top:1px solid #313244;"
            "font-size:11px;padding:2px 8px;}")
        self.setStatusBar(self.sb)
        self.sb_label = QLabel("就绪 | 设置 API Key 后开始对话")
        self.sb_label.setStyleSheet("color:#a6adc8;")
        self.sb.addWidget(self.sb_label)
        if self.username:
            user_label = QLabel(f"👤 {self.username}")
            user_label.setStyleSheet("color:#89b4fa;font-weight:bold;")
            self.sb.addPermanentWidget(user_label)
