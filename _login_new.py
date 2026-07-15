# ── Login Dialog (Modern & Beautiful) ────────────────────────
class LoginDialog(QDialog):
    TAB_STYLE = (
        "QTabWidget::pane {"
        "  border: 1px solid #313244; border-radius: 10px;"
        "  background: #1a1a2e; padding: 8px;"
        "}"
        "QTabBar::tab {"
        "  background: #181825; color: #a6adc8;"
        "  padding: 10px 28px; border: 1px solid #313244;"
        "  border-bottom: none; border-radius: 8px 8px 0 0;"
        "  margin-right: 2px; font-size: 13px; font-weight: bold;"
        "}"
        "QTabBar::tab:selected {"
        "  background: #1a1a2e; color: #89b4fa;"
        "  border-bottom: 2px solid #89b4fa;"
        "}"
        "QTabBar::tab:hover { background: #313244; }"
    )

    INPUT_STYLE = (
        "QLineEdit {"
        "  padding: 10px 14px; border-radius: 8px; font-size: 13px;"
        "  background: #11111b; border: 1px solid #313244; color: #cdd6f4;"
        "}"
        "QLineEdit:focus { border: 1px solid #89b4fa; }"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RAIN - 登录")
        screen = QApplication.primaryScreen()
        ss = screen.availableSize()
        w = min(420, int(ss.width() * 0.35))
        h = min(400, int(ss.height() * 0.45))
        self.setMinimumSize(w, h)
        self.setStyleSheet(DARK_STYLE)
        self.username = ""

        main = QVBoxLayout(self)
        main.setSpacing(16)
        main.setContentsMargins(24, 20, 24, 20)

        # ── Logo / Title ──
        logo_area = QVBoxLayout()
        logo_area.setSpacing(4)
        logo = QLabel("RAIN")
        logo.setStyleSheet("font-size:32px;font-weight:900;color:#89b4fa;")
        logo.setAlignment(Qt.AlignCenter)
        logo_area.addWidget(logo)
        sub = QLabel("智能 AI 助手")
        sub.setStyleSheet("font-size:13px;color:#6c7086;")
        sub.setAlignment(Qt.AlignCenter)
        logo_area.addWidget(sub)
        main.addLayout(logo_area)

        # ── Tab panels ──
        self.stack = QTabWidget()
        self.stack.setStyleSheet(self.TAB_STYLE)

        # Login tab
        lt = QWidget()
        ltl = QVBoxLayout(lt)
        ltl.setSpacing(12)
        ltl.setContentsMargins(16, 20, 16, 16)

        self.login_user = QLineEdit()
        self.login_user.setPlaceholderText("👤  用户名")
        self.login_user.setStyleSheet(self.INPUT_STYLE)
        ltl.addWidget(self.login_user)

        self.login_pass = QLineEdit()
        self.login_pass.setEchoMode(QLineEdit.Password)
        self.login_pass.setPlaceholderText("🔒  密码")
        self.login_pass.setStyleSheet(self.INPUT_STYLE)
        self.login_pass.returnPressed.connect(self._do_login)
        ltl.addWidget(self.login_pass)

        self.remember_check = QCheckBox("记住我，下次自动登录")
        self.remember_check.setChecked(True)
        self.remember_check.setStyleSheet(
            "QCheckBox{color:#a6adc8;font-size:12px;spacing:8px;}"
            "QCheckBox::indicator{width:16px;height:16px;border:1px solid #45475a;border-radius:3px;background:#181825;}"
            "QCheckBox::indicator:checked{background:#89b4fa;border-color:#89b4fa;}")
        ltl.addWidget(self.remember_check)
        ltl.addStretch()

        self.stack.addTab(lt, "  登  录  ")

        # Register tab
        rt = QWidget()
        rtl = QVBoxLayout(rt)
        rtl.setSpacing(12)
        rtl.setContentsMargins(16, 20, 16, 16)

        self.reg_user = QLineEdit()
        self.reg_user.setPlaceholderText("👤  设置用户名")
        self.reg_user.setStyleSheet(self.INPUT_STYLE)
        rtl.addWidget(self.reg_user)

        self.reg_pass = QLineEdit()
        self.reg_pass.setEchoMode(QLineEdit.Password)
        self.reg_pass.setPlaceholderText("🔒  设置密码")
        self.reg_pass.setStyleSheet(self.INPUT_STYLE)
        rtl.addWidget(self.reg_pass)

        self.reg_pass2 = QLineEdit()
        self.reg_pass2.setEchoMode(QLineEdit.Password)
        self.reg_pass2.setPlaceholderText("🔒  确认密码")
        self.reg_pass2.setStyleSheet(self.INPUT_STYLE)
        self.reg_pass2.returnPressed.connect(self._do_register)
        rtl.addWidget(self.reg_pass2)
        rtl.addStretch()

        self.stack.addTab(rt, "  注  册  ")

        main.addWidget(self.stack)

        # ── Message ──
        self.msg_label = QLabel("")
        self.msg_label.setStyleSheet("color:#f38ba8;font-size:12px;padding:4px;")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)
        main.addWidget(self.msg_label)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.login_btn = QPushButton("🚀  登  录")
        self.login_btn.setStyleSheet(
            "QPushButton{background:#89b4fa;color:#1e1e2e;border-radius:10px;"
            "padding:12px 0;font-size:14px;font-weight:bold;}"
            "QPushButton:hover{background:#b4befe;}"
            "QPushButton:pressed{background:#74c7ec;}")
        self.login_btn.clicked.connect(self._do_login)
        btn_row.addWidget(self.login_btn)

        self.reg_btn = QPushButton("✨  注  册")
        self.reg_btn.setStyleSheet(
            "QPushButton{background:#a6e3a1;color:#1e1e2e;border-radius:10px;"
            "padding:12px 0;font-size:14px;font-weight:bold;}"
            "QPushButton:hover{background:#94e2d5;}"
            "QPushButton:pressed{background:#74c7ec;}")
        self.reg_btn.clicked.connect(self._do_register)
        self.reg_btn.hide()
        btn_row.addWidget(self.reg_btn)

        main.addLayout(btn_row)

        self.stack.currentChanged.connect(lambda i: self._toggle_btn(i))
        self._init_user_db()

    def _init_user_db(self):
        import sqlite3, hashlib
        dbp = SETTINGS_DIR / "users.db"
        self._udb = sqlite3.connect(str(dbp))
        self._udb.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, created_at TEXT
        )""")
        self._udb.commit()

    def _toggle_btn(self, idx):
        self.login_btn.setVisible(idx == 0)
        self.reg_btn.setVisible(idx == 1)
        self.msg_label.setText("")

    def _hash(self, pw):
        import hashlib
        return hashlib.sha256(f"RAIN_SALT_{pw}".encode()).hexdigest()

    def _do_login(self):
        u = self.login_user.text().strip()
        p = self.login_pass.text().strip()
        if not u or not p:
            self.msg_label.setText("⚠ 请输入用户名和密码")
            return
        row = self._udb.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
        if not row:
            self.msg_label.setText("⚠ 用户不存在，请先注册")
            return
        if row[0] != self._hash(p):
            self.msg_label.setText("⚠ 密码错误")
            return
        self.username = u
        remember_file = SETTINGS_DIR / "remember.json"
        if self.remember_check.isChecked():
            try:
                remember_file.write_text(json.dumps({
                    "user": u, "pass_hash": row[0]
                }), encoding="utf-8")
            except Exception:
                pass
        else:
            try:
                remember_file.unlink(missing_ok=True)
            except Exception:
                pass
        self.accept()

    def _do_register(self):
        u = self.reg_user.text().strip()
        p = self.reg_pass.text().strip()
        p2 = self.reg_pass2.text().strip()
        if not u or not p:
            self.msg_label.setText("⚠ 请填写完整信息")
            return
        if len(u) < 2:
            self.msg_label.setText("⚠ 用户名至少2个字符")
            return
        if len(p) < 4:
            self.msg_label.setText("⚠ 密码至少4个字符")
            return
        if p != p2:
            self.msg_label.setText("⚠ 两次密码不一致")
            return
        row = self._udb.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone()
        if row:
            self.msg_label.setText("⚠ 用户名已存在")
            return
        import datetime
        self._udb.execute("INSERT INTO users VALUES (?,?,?)",
            (u, self._hash(p), datetime.datetime.now().isoformat()))
        self._udb.commit()
        self.username = u
        remember_file = SETTINGS_DIR / "remember.json"
        try:
            remember_file.write_text(json.dumps({
                "user": u, "pass_hash": self._hash(p)
            }), encoding="utf-8")
        except Exception:
            pass
        self.accept()

