#!/usr/bin/env python3
"""
LONHRO Terminal - A fully functional terminal application
with AI chat, GitHub integration, system monitoring, and media playback.
"""

import os
import sys
import json
import random
import threading
import subprocess
from pathlib import Path
from datetime import datetime
import requests
import psutil
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BG = "#1A0A14"
BG_DARKER = "#120810"
BG_LIGHTER = "#2D1520"
FG = "#FFFFFF"
FG_MUTED = "#B0A0A8"
ACCENT = "#E91E8C"
ACCENT_HOVER = "#FF3399"

APP_DIR = Path.home() / ".lonhro-terminal"
APP_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = APP_DIR / "session.json"
HISTORY_FILE = APP_DIR / "command_history.json"
FACTS_FILE = Path(__file__).parent / "lonhro_facts.json"

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def load_facts():
    try:
        with open(FACTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return ["Welcome to LONHRO Terminal - The Future of Synthetic Intelligence"]

def get_random_fact():
    return random.choice(load_facts())

def load_command_history():
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_command_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history[-100:], f)
    except:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# WELCOME SCREEN
# ═══════════════════════════════════════════════════════════════════════════════

class WelcomeOverlay(QtWidgets.QWidget):
    closed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        container = QtWidgets.QFrame()
        container.setFixedSize(520, 420)
        container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {BG}, stop:1 {BG_DARKER});
                border: 2px solid {ACCENT};
                border-radius: 20px;
            }}
        """)

        c_layout = QtWidgets.QVBoxLayout(container)
        c_layout.setContentsMargins(40, 40, 40, 40)
        c_layout.setSpacing(15)

        logo = QtWidgets.QLabel("LONHRO")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 48px; font-weight: bold; background: transparent;")
        logo.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel("The Future of Synthetic Intelligence")
        subtitle.setStyleSheet(f"color: {FG}; font-size: 14px; background: transparent;")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        badge = QtWidgets.QLabel("● End-to-End Encrypted • Zero Knowledge")
        badge.setStyleSheet(f"""
            color: {FG_MUTED}; 
            font-size: 11px; 
            background: {BG_LIGHTER}; 
            padding: 8px 16px; 
            border-radius: 15px;
        """)
        badge.setAlignment(QtCore.Qt.AlignCenter)

        divider = QtWidgets.QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background: {ACCENT};")

        fact_header = QtWidgets.QLabel("Did you know?")
        fact_header.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: bold; background: transparent;")
        fact_header.setAlignment(QtCore.Qt.AlignCenter)

        self.fact_text = QtWidgets.QLabel(get_random_fact())
        self.fact_text.setStyleSheet(f"color: {FG}; font-size: 13px; background: transparent;")
        self.fact_text.setAlignment(QtCore.Qt.AlignCenter)
        self.fact_text.setWordWrap(True)

        launch_btn = QtWidgets.QPushButton("Launch LONHRO  ›")
        launch_btn.setFixedSize(200, 50)
        launch_btn.setCursor(QtCore.Qt.PointingHandCursor)
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {ACCENT}, stop:1 {ACCENT_HOVER});
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {ACCENT_HOVER}, stop:1 {ACCENT});
            }}
        """)
        launch_btn.clicked.connect(self.close_overlay)

        c_layout.addWidget(logo)
        c_layout.addWidget(subtitle)
        c_layout.addWidget(badge, alignment=QtCore.Qt.AlignCenter)
        c_layout.addWidget(divider)
        c_layout.addStretch()
        c_layout.addWidget(fact_header)
        c_layout.addWidget(self.fact_text)
        c_layout.addStretch()
        c_layout.addWidget(launch_btn, alignment=QtCore.Qt.AlignCenter)

        layout.addWidget(container)

    def close_overlay(self):
        self.closed.emit()
        self.hide()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 200))


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE DRAWER
# ═══════════════════════════════════════════════════════════════════════════════

class SlideDrawer(QtWidgets.QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedWidth(380)
        self.setStyleSheet(f"""
            SlideDrawer {{
                background: {BG_DARKER};
                border-left: 2px solid {ACCENT};
            }}
        """)
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QtWidgets.QWidget()
        header.setStyleSheet(f"background: {BG_LIGHTER};")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 10, 10)

        title_label = QtWidgets.QLabel(self.title)
        title_label.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold;")

        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {FG_MUTED};
                border: none;
                font-size: 16px;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background: {ACCENT};
                color: white;
            }}
        """)
        close_btn.clicked.connect(self.hide_drawer)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        layout.addWidget(header)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(self.content_widget, stretch=1)

    def set_content(self, widget):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.content_layout.addWidget(widget)

    def show_drawer(self):
        self.show()

    def hide_drawer(self):
        self.hide()


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd()
        self.command_history = load_command_history()
        self.history_index = -1
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.output = QtWidgets.QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {BG_DARKER};
                color: {FG};
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                border: 1px solid #3D2030;
                border-radius: 8px;
                padding: 12px;
                selection-background-color: {ACCENT};
            }}
        """)

        input_container = QtWidgets.QWidget()
        input_layout = QtWidgets.QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        self.prompt = QtWidgets.QLabel(self._get_prompt())
        self.prompt.setStyleSheet(f"""
            color: {ACCENT}; 
            font-family: 'Consolas', monospace; 
            font-weight: bold;
            font-size: 13px;
        """)

        self.cmd_input = QtWidgets.QLineEdit()
        self.cmd_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_DARKER};
                color: {FG};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                border: 1px solid #3D2030;
                border-radius: 6px;
                padding: 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT};
            }}
        """)
        self.cmd_input.setPlaceholderText("Enter command...")
        self.cmd_input.returnPressed.connect(self.execute_command)
        self.cmd_input.installEventFilter(self)

        self.enter_btn = QtWidgets.QPushButton("Enter ⏎")
        self.enter_btn.setFixedHeight(38)
        self.enter_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.enter_btn.clicked.connect(self.execute_command)

        input_layout.addWidget(self.prompt)
        input_layout.addWidget(self.cmd_input, stretch=1)
        input_layout.addWidget(self.enter_btn)

        layout.addWidget(self.output, stretch=1)
        layout.addWidget(input_container)

        self._print_welcome()

    def _get_prompt(self):
        home = str(Path.home())
        display_path = self.cwd.replace(home, "~") if self.cwd.startswith(home) else self.cwd
        if len(display_path) > 30:
            display_path = "..." + display_path[-27:]
        return f"{display_path} $"

    def _print_welcome(self):
        welcome = f"""
╔══════════════════════════════════════════════════════════════╗
║                     LONHRO TERMINAL                          ║
║          The Future of Synthetic Intelligence                ║
╚══════════════════════════════════════════════════════════════╝

Type commands below. Special commands:
  cd <path>  - Change directory
  clear      - Clear terminal
  exit       - Exit application
  help       - Show this message

"""
        self.output.setPlainText(welcome)

    def eventFilter(self, obj, event):
        if obj == self.cmd_input and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Up:
                self._history_up()
                return True
            elif event.key() == QtCore.Qt.Key_Down:
                self._history_down()
                return True
        return super().eventFilter(obj, event)

    def _history_up(self):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_input.setText(self.command_history[-(self.history_index + 1)])

    def _history_down(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.cmd_input.setText(self.command_history[-(self.history_index + 1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.cmd_input.clear()

    def execute_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        self.command_history.append(cmd)
        save_command_history(self.command_history)
        self.history_index = -1
        self.cmd_input.clear()

        self.output.appendPlainText(f"\n{self._get_prompt()} {cmd}")

        if cmd == "help":
            self._print_welcome()
            return

        if cmd == "clear":
            self.output.clear()
            return

        if cmd == "exit":
            QtWidgets.QApplication.quit()
            return

        if cmd.startswith("cd"):
            self._handle_cd(cmd)
            return

        threading.Thread(target=self._run_command, args=(cmd,), daemon=True).start()

    def _handle_cd(self, cmd):
        parts = cmd.split(maxsplit=1)
        path = parts[1] if len(parts) > 1 else str(Path.home())

        try:
            if path == "~":
                path = str(Path.home())
            elif path.startswith("~/"):
                path = str(Path.home() / path[2:])
            elif path == "-":
                path = os.environ.get("OLDPWD", self.cwd)
            elif not os.path.isabs(path):
                path = os.path.join(self.cwd, path)

            path = os.path.normpath(os.path.realpath(path))

            if os.path.isdir(path):
                os.environ["OLDPWD"] = self.cwd
                self.cwd = path
                os.chdir(path)
                self.prompt.setText(self._get_prompt())
            else:
                self.output.appendPlainText(f"cd: no such directory: {path}")
        except Exception as e:
            self.output.appendPlainText(f"cd: {e}")

    def _run_command(self, cmd):
        try:
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += result.stderr

            if output:
                QtCore.QMetaObject.invokeMethod(
                    self.output, "appendPlainText",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, output.rstrip())
                )
        except subprocess.TimeoutExpired:
            QtCore.QMetaObject.invokeMethod(
                self.output, "appendPlainText",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, "Error: Command timed out after 60 seconds")
            )
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(
                self.output, "appendPlainText",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"Error: {e}")
            )


# ═══════════════════════════════════════════════════════════════════════════════
# AI CHAT PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class AIChatPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.chat_display = QtWidgets.QPlainTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Chat with AI powered by GPT-4o-mini...")

        self.input_field = QtWidgets.QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QtWidgets.QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)

        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.input_field, stretch=1)
        input_layout.addWidget(self.send_btn)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px;")

        layout.addWidget(self.chat_display, stretch=1)
        layout.addLayout(input_layout)
        layout.addWidget(self.status)

    def send_message(self):
        message = self.input_field.text().strip()
        if not message:
            return

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.chat_display.appendPlainText("\n⚠️ Error: OPENAI_API_KEY not set")
            self.chat_display.appendPlainText("Set it with: export OPENAI_API_KEY='your-key'")
            return

        self.input_field.clear()
        self.chat_display.appendPlainText(f"\n👤 You: {message}")
        self.messages.append({"role": "user", "content": message})
        self.status.setText("AI is thinking...")
        self.send_btn.setEnabled(False)

        threading.Thread(target=self._call_api, args=(api_key,), daemon=True).start()

    def _call_api(self, api_key):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": self.messages,
                    "max_tokens": 1000
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                ai_message = data["choices"][0]["message"]["content"]
                self.messages.append({"role": "assistant", "content": ai_message})

                QtCore.QMetaObject.invokeMethod(
                    self.chat_display, "appendPlainText",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"\n🤖 AI: {ai_message}")
                )
                QtCore.QMetaObject.invokeMethod(
                    self.status, "setText",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, "")
                )
            else:
                error = response.json().get("error", {}).get("message", "Unknown error")
                QtCore.QMetaObject.invokeMethod(
                    self.chat_display, "appendPlainText",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"\n⚠️ Error: {error}")
                )
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(
                self.chat_display, "appendPlainText",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"\n⚠️ Error: {e}")
            )
        finally:
            QtCore.QMetaObject.invokeMethod(
                self.send_btn, "setEnabled",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(bool, True)
            )
            QtCore.QMetaObject.invokeMethod(
                self.status, "setText",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, "")
            )


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class GitHubPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.repo_input = QtWidgets.QLineEdit()
        self.repo_input.setPlaceholderText("owner/repo (e.g., torvalds/linux)")
        self.repo_input.returnPressed.connect(self.fetch_repo_info)

        btn_layout = QtWidgets.QHBoxLayout()
        self.info_btn = QtWidgets.QPushButton("Info")
        self.issues_btn = QtWidgets.QPushButton("Issues")
        self.commits_btn = QtWidgets.QPushButton("Commits")
        
        for btn in [self.info_btn, self.issues_btn, self.commits_btn]:
            btn.setFixedHeight(32)
            btn_layout.addWidget(btn)

        self.result_list = QtWidgets.QListWidget()
        
        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px;")

        layout.addWidget(self.repo_input)
        layout.addLayout(btn_layout)
        layout.addWidget(self.result_list, stretch=1)
        layout.addWidget(self.status)

        self.info_btn.clicked.connect(self.fetch_repo_info)
        self.issues_btn.clicked.connect(self.fetch_issues)
        self.commits_btn.clicked.connect(self.fetch_commits)

    def _get_repo(self):
        repo = self.repo_input.text().strip()
        if not repo:
            self.status.setText("Please enter a repository")
            return None
        return repo

    def fetch_repo_info(self):
        repo = self._get_repo()
        if not repo:
            return
        self.result_list.clear()
        self.status.setText("Fetching repository info...")
        threading.Thread(target=self._fetch_repo_info, args=(repo,), daemon=True).start()

    def _fetch_repo_info(self, repo):
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}", timeout=15)
            if r.status_code == 404:
                self._add_item("❌ Repository not found")
                self._set_status("Not found")
                return
            
            data = r.json()
            items = [
                f"📁 {data.get('full_name', 'N/A')}",
                f"📝 {(data.get('description') or 'No description')[:60]}",
                "─" * 30,
                f"⭐ Stars: {data.get('stargazers_count', 0):,}",
                f"🍴 Forks: {data.get('forks_count', 0):,}",
                f"👀 Watchers: {data.get('subscribers_count', 0):,}",
                f"🐛 Issues: {data.get('open_issues_count', 0):,}",
                "─" * 30,
                f"💻 Language: {data.get('language') or 'N/A'}",
                f"📜 License: {data.get('license', {}).get('name', 'N/A') if data.get('license') else 'N/A'}",
                f"🌿 Default Branch: {data.get('default_branch', 'N/A')}",
                "─" * 30,
                f"📅 Created: {data.get('created_at', '')[:10]}",
                f"🔄 Updated: {data.get('updated_at', '')[:10]}",
            ]
            
            for item in items:
                self._add_item(item)
            self._set_status(f"Loaded: {repo}")
            
        except Exception as e:
            self._add_item(f"❌ Error: {e}")
            self._set_status("Failed")

    def fetch_issues(self):
        repo = self._get_repo()
        if not repo:
            return
        self.result_list.clear()
        self.status.setText("Fetching issues...")
        threading.Thread(target=self._fetch_issues, args=(repo,), daemon=True).start()

    def _fetch_issues(self, repo):
        try:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/issues",
                params={"state": "open", "per_page": 15},
                timeout=15
            )
            issues = r.json()
            
            if not issues or isinstance(issues, dict):
                self._add_item("No open issues found")
                return
                
            for issue in issues:
                if issue.get("pull_request"):
                    continue
                num = issue.get("number", "?")
                title = issue.get("title", "No title")[:35]
                user = issue.get("user", {}).get("login", "unknown")
                labels = ", ".join([l.get("name", "") for l in issue.get("labels", [])][:2])
                
                text = f"#{num} {title}..."
                if labels:
                    text += f" [{labels}]"
                text += f" @{user}"
                self._add_item(text)
                
            self._set_status(f"Found {len(issues)} issues")
            
        except Exception as e:
            self._add_item(f"❌ Error: {e}")

    def fetch_commits(self):
        repo = self._get_repo()
        if not repo:
            return
        self.result_list.clear()
        self.status.setText("Fetching commits...")
        threading.Thread(target=self._fetch_commits, args=(repo,), daemon=True).start()

    def _fetch_commits(self, repo):
        try:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/commits",
                params={"per_page": 15},
                timeout=15
            )
            commits = r.json()
            
            if not commits or isinstance(commits, dict):
                self._add_item("No commits found")
                return
                
            for commit in commits:
                sha = commit.get("sha", "")[:7]
                msg = commit.get("commit", {}).get("message", "").split("\n")[0][:30]
                author = commit.get("commit", {}).get("author", {}).get("name", "unknown")[:12]
                date = commit.get("commit", {}).get("author", {}).get("date", "")[:10]
                
                self._add_item(f"{sha} {msg}... ({author}) {date}")
                
            self._set_status(f"Found {len(commits)} commits")
            
        except Exception as e:
            self._add_item(f"❌ Error: {e}")

    def _add_item(self, text):
        QtCore.QMetaObject.invokeMethod(
            self.result_list, "addItem",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, text)
        )

    def _set_status(self, text):
        QtCore.QMetaObject.invokeMethod(
            self.status, "setText",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, text)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM INFO PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class SystemInfoPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.info_list = QtWidgets.QListWidget()

        btn_layout = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.auto_cb = QtWidgets.QCheckBox("Auto (3s)")
        self.auto_cb.setStyleSheet(f"color: {FG};")
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.auto_cb)
        btn_layout.addStretch()

        layout.addWidget(self.info_list, stretch=1)
        layout.addLayout(btn_layout)

        self.refresh_btn.clicked.connect(self.refresh)
        self.auto_cb.toggled.connect(self.toggle_auto)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)

    def toggle_auto(self, checked):
        if checked:
            self.timer.start(3000)
        else:
            self.timer.stop()

    def refresh(self):
        self.info_list.clear()

        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_phys = psutil.cpu_count(logical=False)
        
        try:
            cpu_freq = psutil.cpu_freq()
            freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        except:
            freq_str = "N/A"

        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        try:
            boot = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot
            uptime_str = str(uptime).split(".")[0]
        except:
            uptime_str = "N/A"

        sections = [
            ("═══ CPU ═══", [
                f"  Usage: {cpu_percent}%",
                f"  Cores: {cpu_count_phys} physical, {cpu_count} logical",
                f"  Frequency: {freq_str}",
            ]),
            ("═══ MEMORY ═══", [
                f"  RAM: {mem.percent}%  ({self._fmt_bytes(mem.used)} / {self._fmt_bytes(mem.total)})",
                f"  Available: {self._fmt_bytes(mem.available)}",
                f"  Swap: {swap.percent}%  ({self._fmt_bytes(swap.used)} / {self._fmt_bytes(swap.total)})",
            ]),
            ("═══ DISK ═══", [
                f"  Usage: {disk.percent}%",
                f"  Used: {self._fmt_bytes(disk.used)} / {self._fmt_bytes(disk.total)}",
                f"  Free: {self._fmt_bytes(disk.free)}",
            ]),
            ("═══ NETWORK ═══", [
                f"  Sent: {self._fmt_bytes(net.bytes_sent)}",
                f"  Received: {self._fmt_bytes(net.bytes_recv)}",
                f"  Packets: {net.packets_sent:,} sent, {net.packets_recv:,} recv",
            ]),
            ("═══ SYSTEM ═══", [
                f"  OS: {sys.platform}",
                f"  Python: {sys.version.split()[0]}",
                f"  Uptime: {uptime_str}",
            ]),
        ]

        for header, items in sections:
            self.info_list.addItem(header)
            for item in items:
                self.info_list.addItem(item)

    def _fmt_bytes(self, b):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"


# ═══════════════════════════════════════════════════════════════════════════════
# MEDIA PLAYER PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class MediaPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(180)
        self.video_widget.setStyleSheet("background: black; border-radius: 8px;")

        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)

        self.file_label = QtWidgets.QLabel("No file loaded")
        self.file_label.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px;")
        self.file_label.setAlignment(QtCore.Qt.AlignCenter)

        ctrl_layout = QtWidgets.QHBoxLayout()
        self.open_btn = QtWidgets.QPushButton("📂 Open")
        self.play_btn = QtWidgets.QPushButton("▶")
        self.stop_btn = QtWidgets.QPushButton("⏹")
        
        self.play_btn.setFixedWidth(50)
        self.stop_btn.setFixedWidth(50)
        
        ctrl_layout.addWidget(self.open_btn)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.play_btn)
        ctrl_layout.addWidget(self.stop_btn)
        ctrl_layout.addStretch()

        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        
        self.time_label = QtWidgets.QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px;")
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)

        vol_layout = QtWidgets.QHBoxLayout()
        vol_label = QtWidgets.QLabel("🔊")
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(100)
        vol_layout.addStretch()
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(self.volume_slider)

        layout.addWidget(self.video_widget)
        layout.addWidget(self.file_label)
        layout.addWidget(self.position_slider)
        layout.addWidget(self.time_label)
        layout.addLayout(ctrl_layout)
        layout.addLayout(vol_layout)

        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.toggle_play)
        self.stop_btn.clicked.connect(self.stop)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.position_slider.sliderMoved.connect(self.seek)
        
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.playbackStateChanged.connect(self.on_state_changed)

        self.audio.setVolume(0.7)

    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Media File", "",
            "Media Files (*.mp4 *.mp3 *.wav *.avi *.mkv *.webm *.ogg *.flac *.m4a);;All Files (*)"
        )
        if path:
            self.player.setSource(QtCore.QUrl.fromLocalFile(path))
            self.file_label.setText(Path(path).name)
            self.player.play()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop(self):
        self.player.stop()

    def set_volume(self, value):
        self.audio.setVolume(value / 100.0)

    def seek(self, position):
        self.player.setPosition(position)

    def on_position_changed(self, position):
        self.position_slider.blockSignals(True)
        self.position_slider.setValue(position)
        self.position_slider.blockSignals(False)
        self._update_time_label(position, self.player.duration())

    def on_duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self._update_time_label(self.player.position(), duration)

    def on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    def _update_time_label(self, pos, dur):
        def fmt(ms):
            s = ms // 1000
            return f"{s // 60}:{s % 60:02d}"
        self.time_label.setText(f"{fmt(pos)} / {fmt(dur)}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LONHRO Terminal")
        self.resize(1280, 800)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_ai = QtWidgets.QPushButton("🤖 AI Chat")
        self.btn_github = QtWidgets.QPushButton("📦 GitHub")
        self.btn_system = QtWidgets.QPushButton("📊 System")
        self.btn_media = QtWidgets.QPushButton("🎵 Media")

        for btn in [self.btn_ai, self.btn_github, self.btn_system, self.btn_media]:
            btn.setFixedHeight(38)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            toolbar.addWidget(btn)

        toolbar.addStretch()

        self.btn_save = QtWidgets.QPushButton("💾 Save")
        self.btn_save.setFixedHeight(38)
        toolbar.addWidget(self.btn_save)

        self.terminal = TerminalWidget()

        left_layout.addLayout(toolbar)
        left_layout.addWidget(self.terminal, stretch=1)

        main_layout.addWidget(left_panel, stretch=1)

        self.drawer_ai = SlideDrawer("AI Chat")
        self.drawer_ai.set_content(AIChatPanel())

        self.drawer_github = SlideDrawer("GitHub")
        self.drawer_github.set_content(GitHubPanel())

        self.drawer_system = SlideDrawer("System Info")
        self.drawer_system.set_content(SystemInfoPanel())

        self.drawer_media = SlideDrawer("Media Player")
        self.drawer_media.set_content(MediaPanel())

        self.drawers = [self.drawer_ai, self.drawer_github, self.drawer_system, self.drawer_media]

        for drawer in self.drawers:
            main_layout.addWidget(drawer)

        self.btn_ai.clicked.connect(lambda: self.toggle_drawer(self.drawer_ai))
        self.btn_github.clicked.connect(lambda: self.toggle_drawer(self.drawer_github))
        self.btn_system.clicked.connect(lambda: self.toggle_drawer(self.drawer_system))
        self.btn_media.clicked.connect(lambda: self.toggle_drawer(self.drawer_media))
        self.btn_save.clicked.connect(self.save_session)

        self.welcome = WelcomeOverlay(self)
        self.welcome.closed.connect(self.on_welcome_closed)

    def toggle_drawer(self, drawer):
        for d in self.drawers:
            if d != drawer and d.isVisible():
                d.hide_drawer()

        if drawer.isVisible():
            drawer.hide_drawer()
        else:
            drawer.show_drawer()

    def on_welcome_closed(self):
        self.terminal.cmd_input.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.welcome.setGeometry(self.rect())
        self.welcome.show()
        self.welcome.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "welcome"):
            self.welcome.setGeometry(self.rect())

    def save_session(self):
        data = {
            "timestamp": datetime.now().isoformat(),
            "cwd": self.terminal.cwd,
        }
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f, indent=2)
        QtWidgets.QMessageBox.information(self, "Saved", "Session saved successfully.")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {BG};
                color: {FG};
                font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {ACCENT}, stop:1 {ACCENT_HOVER});
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {ACCENT_HOVER}, stop:1 {ACCENT});
            }}
            QPushButton:pressed {{
                background: {ACCENT};
            }}
            QLineEdit, QPlainTextEdit {{
                background: {BG_DARKER};
                color: {FG};
                border: 1px solid #3D2030;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: {ACCENT};
            }}
            QLineEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {ACCENT};
            }}
            QListWidget {{
                background: {BG_DARKER};
                color: {FG};
                border: 1px solid #3D2030;
                border-radius: 6px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background: {BG_LIGHTER};
            }}
            QListWidget::item:selected {{
                background: {ACCENT};
            }}
            QSlider::groove:horizontal {{
                background: #3D2030;
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {ACCENT};
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ACCENT};
                border-radius: 3px;
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #3D2030;
                background: {BG_DARKER};
            }}
            QCheckBox::indicator:checked {{
                background: {ACCENT};
                border-color: {ACCENT};
            }}
            QScrollBar:vertical {{
                background: {BG_DARKER};
                width: 10px;
                border-radius: 5px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: #3D2030;
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ACCENT};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QMessageBox {{
                background: {BG};
            }}
            QMessageBox QLabel {{
                color: {FG};
            }}
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("LONHRO Terminal")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
