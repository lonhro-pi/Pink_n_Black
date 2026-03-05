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

# Optional Imports
HAS_QTERMWIDGET = False
try:
    from qtermwidget import QTermWidget
    HAS_QTERMWIDGET = True
except:
    HAS_QTERMWIDGET = False

# Constants & Paths - Lonhro color scheme
BG = "#1A0A14"
BG_DARKER = "#120810"
FG = "#FFFFFF"
FG_MUTED = "#B0A0A8"
ACCENT = "#E91E8C"
ACCENT_HOVER = "#FF3399"
APP_DIR = Path.home() / ".lonhro-terminal"
APP_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = APP_DIR / "session.json"
FACTS_FILE = Path(__file__).parent / "lonhro_facts.json"

def load_facts():
    try:
        with open(FACTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return ["Welcome to LONHRO Terminal"]

def get_random_fact():
    facts = load_facts()
    return random.choice(facts)


class SlideDrawer(QtWidgets.QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)
        self.setStyleSheet(f"""
            SlideDrawer {{
                background: {BG_DARKER};
                border-left: 2px solid {ACCENT};
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold; padding: 15px;")
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {FG_MUTED};
                border: none;
                font-size: 18px;
            }}
            QPushButton:hover {{
                color: {ACCENT};
            }}
        """)
        close_btn.clicked.connect(self.hide_drawer)
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(close_btn)
        
        header_widget = QtWidgets.QWidget()
        header_widget.setLayout(header)
        layout.addWidget(header_widget)
        
        self.content = QtWidgets.QVBoxLayout()
        self.content.setContentsMargins(15, 0, 15, 15)
        layout.addLayout(self.content)
        
        self._animation = QtCore.QPropertyAnimation(self, b"maximumWidth")
        self._animation.setDuration(200)
        self.hide()

    def add_widget(self, widget):
        self.content.addWidget(widget)

    def add_stretch(self):
        self.content.addStretch()

    def show_drawer(self):
        self.show()
        self._animation.setStartValue(0)
        self._animation.setEndValue(350)
        self._animation.start()

    def hide_drawer(self):
        self._animation.setStartValue(350)
        self._animation.setEndValue(0)
        self._animation.start()
        self._animation.finished.connect(self.hide)


class WelcomeOverlay(QtWidgets.QWidget):
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        container = QtWidgets.QFrame()
        container.setFixedSize(500, 400)
        container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {BG}, stop:1 {BG_DARKER});
                border: 2px solid {ACCENT};
                border-radius: 20px;
            }}
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        logo = QtWidgets.QLabel("LONHRO")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 42px; font-weight: bold;")
        logo.setAlignment(QtCore.Qt.AlignCenter)
        
        subtitle = QtWidgets.QLabel("The Future of Synthetic Intelligence")
        subtitle.setStyleSheet(f"color: {FG}; font-size: 16px;")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        divider = QtWidgets.QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background: {ACCENT};")
        
        fact_label = QtWidgets.QLabel("Did you know?")
        fact_label.setStyleSheet(f"color: {FG_MUTED}; font-size: 12px;")
        fact_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.fact_text = QtWidgets.QLabel(get_random_fact())
        self.fact_text.setStyleSheet(f"color: {FG}; font-size: 14px;")
        self.fact_text.setAlignment(QtCore.Qt.AlignCenter)
        self.fact_text.setWordWrap(True)
        
        launch_btn = QtWidgets.QPushButton("Launch Terminal  ›")
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #FF3399);
                color: #FFFFFF;
                border: none;
                border-radius: 25px;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF3399, stop:1 {ACCENT});
            }}
        """)
        launch_btn.setCursor(QtCore.Qt.PointingHandCursor)
        launch_btn.clicked.connect(self.close_overlay)
        
        container_layout.addWidget(logo)
        container_layout.addWidget(subtitle)
        container_layout.addWidget(divider)
        container_layout.addStretch()
        container_layout.addWidget(fact_label)
        container_layout.addWidget(self.fact_text)
        container_layout.addStretch()
        container_layout.addWidget(launch_btn, alignment=QtCore.Qt.AlignCenter)
        
        layout.addWidget(container)

    def close_overlay(self):
        self.closed.emit()
        self.hide()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 180))


class TerminalWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        if HAS_QTERMWIDGET:
            self.term = QTermWidget()
            layout.addWidget(self.term)
        else:
            self.output = QtWidgets.QPlainTextEdit(readOnly=True)
            self.output.setStyleSheet(f"""
                background-color: {BG_DARKER};
                color: {FG};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                border: 1px solid #3D2030;
                border-radius: 6px;
                padding: 10px;
            """)
            layout.addWidget(self.output)
            
            input_layout = QtWidgets.QHBoxLayout()
            self.prompt_label = QtWidgets.QLabel(f"{os.getcwd()} $")
            self.prompt_label.setStyleSheet(f"color: {ACCENT}; font-family: 'Consolas', monospace; font-weight: bold;")
            self.cmd_input = QtWidgets.QLineEdit()
            self.cmd_input.setStyleSheet(f"""
                background-color: {BG_DARKER};
                color: {FG};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                border: 1px solid #3D2030;
                border-radius: 6px;
                padding: 8px;
            """)
            self.cmd_input.setPlaceholderText("Enter command...")
            self.cmd_input.returnPressed.connect(self.run_command)
            
            input_layout.addWidget(self.prompt_label)
            input_layout.addWidget(self.cmd_input)
            layout.addLayout(input_layout)
            
            self.process = None
            self.cwd = os.getcwd()
            self.command_history = []
            self.history_index = -1
            self.cmd_input.installEventFilter(self)
            
            self.output.appendPlainText(f"LONHRO Terminal - Type commands below\n{'='*50}\n")

    def eventFilter(self, obj, event):
        if obj == self.cmd_input and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Up:
                if self.command_history and self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.cmd_input.setText(self.command_history[-(self.history_index + 1)])
                return True
            elif event.key() == QtCore.Qt.Key_Down:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.cmd_input.setText(self.command_history[-(self.history_index + 1)])
                elif self.history_index == 0:
                    self.history_index = -1
                    self.cmd_input.clear()
                return True
        return super().eventFilter(obj, event)

    def run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        
        self.command_history.append(cmd)
        self.history_index = -1
        self.cmd_input.clear()
        
        self.output.appendPlainText(f"\n{self.cwd} $ {cmd}")
        
        if cmd.startswith("cd "):
            path = cmd[3:].strip()
            try:
                if path == "~":
                    path = str(Path.home())
                elif path.startswith("~/"):
                    path = str(Path.home() / path[2:])
                elif not os.path.isabs(path):
                    path = os.path.join(self.cwd, path)
                path = os.path.normpath(path)
                if os.path.isdir(path):
                    self.cwd = path
                    os.chdir(path)
                    self.prompt_label.setText(f"{self.cwd} $")
                else:
                    self.output.appendPlainText(f"cd: no such directory: {path}")
            except Exception as e:
                self.output.appendPlainText(f"cd: {e}")
            return
        
        if cmd == "clear":
            self.output.clear()
            return
        
        if cmd == "exit":
            QtWidgets.QApplication.quit()
            return
        
        threading.Thread(target=self._execute_command, args=(cmd,), daemon=True).start()

    def _execute_command(self, cmd):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
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
                QtCore.Q_ARG(str, "Command timed out after 30 seconds")
            )
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(
                self.output, "appendPlainText",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"Error: {e}")
            )


class ChatGPTPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.history = QtWidgets.QPlainTextEdit(readOnly=True)
        self.history.setMinimumHeight(200)
        self.input = QtWidgets.QLineEdit(placeholderText="Ask AI...")
        self.btn = QtWidgets.QPushButton("Send")
        
        layout.addWidget(self.history)
        layout.addWidget(self.input)
        layout.addWidget(self.btn)
        
        self.btn.clicked.connect(self.send)
        self.input.returnPressed.connect(self.send)

    def send(self):
        prompt = self.input.text().strip()
        if not prompt:
            return
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            self.history.appendPlainText("[Error] OPENAI_API_KEY not set")
            return
        self.history.appendPlainText(f"You: {prompt}")
        self.input.clear()
        threading.Thread(target=self._call, args=(prompt, key), daemon=True).start()

    def _call(self, prompt, key):
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions",
                              headers={"Authorization": f"Bearer {key}"},
                              json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}, timeout=15)
            text = r.json()["choices"][0]["message"]["content"]
            QtCore.QMetaObject.invokeMethod(self.history, "appendPlainText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"AI: {text}\n"))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self.history, "appendPlainText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Error: {e}"))


class GitHubPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.repo_input = QtWidgets.QLineEdit(placeholderText="owner/repo (e.g. torvalds/linux)")
        self.repo_input.returnPressed.connect(self.fetch_repo)
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.fetch_btn = QtWidgets.QPushButton("Repo Info")
        self.issues_btn = QtWidgets.QPushButton("Issues")
        self.commits_btn = QtWidgets.QPushButton("Commits")
        btn_layout.addWidget(self.fetch_btn)
        btn_layout.addWidget(self.issues_btn)
        btn_layout.addWidget(self.commits_btn)
        
        self.info_list = QtWidgets.QListWidget()
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px;")
        
        layout.addWidget(self.repo_input)
        layout.addLayout(btn_layout)
        layout.addWidget(self.info_list)
        layout.addWidget(self.status_label)
        
        self.fetch_btn.clicked.connect(self.fetch_repo)
        self.issues_btn.clicked.connect(self.fetch_issues)
        self.commits_btn.clicked.connect(self.fetch_commits)

    def fetch_repo(self):
        repo = self.repo_input.text().strip()
        if not repo:
            self.status_label.setText("Enter a repository (owner/repo)")
            return
        self.info_list.clear()
        self.status_label.setText("Fetching repository info...")
        threading.Thread(target=self._fetch_repo, args=(repo,), daemon=True).start()

    def _fetch_repo(self, repo):
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}", timeout=10)
            if r.status_code == 404:
                QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "Repository not found"))
                return
            data = r.json()
            items = [
                f"📁 Name: {data.get('name', 'N/A')}",
                f"📝 Description: {data.get('description', 'No description')[:50]}",
                f"⭐ Stars: {data.get('stargazers_count', 0):,}",
                f"🍴 Forks: {data.get('forks_count', 0):,}",
                f"👀 Watchers: {data.get('watchers_count', 0):,}",
                f"💻 Language: {data.get('language', 'N/A')}",
                f"🐛 Open Issues: {data.get('open_issues_count', 0):,}",
                f"📅 Created: {data.get('created_at', 'N/A')[:10]}",
                f"🔄 Updated: {data.get('updated_at', 'N/A')[:10]}",
                f"📜 License: {data.get('license', {}).get('name', 'N/A') if data.get('license') else 'N/A'}",
            ]
            for item in items:
                QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, item))
            QtCore.QMetaObject.invokeMethod(self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Loaded: {repo}"))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Error: {e}"))
            QtCore.QMetaObject.invokeMethod(self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "Failed to fetch"))

    def fetch_issues(self):
        repo = self.repo_input.text().strip()
        if not repo:
            self.status_label.setText("Enter a repository first")
            return
        self.info_list.clear()
        self.status_label.setText("Fetching issues...")
        threading.Thread(target=self._fetch_issues, args=(repo,), daemon=True).start()

    def _fetch_issues(self, repo):
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=10", timeout=10)
            issues = r.json()
            if not issues:
                QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "No open issues"))
                return
            for issue in issues[:10]:
                title = issue.get('title', 'No title')[:40]
                number = issue.get('number', '?')
                user = issue.get('user', {}).get('login', 'unknown')
                QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"#{number} {title}... (@{user})"))
            QtCore.QMetaObject.invokeMethod(self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Showing {len(issues[:10])} issues"))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Error: {e}"))

    def fetch_commits(self):
        repo = self.repo_input.text().strip()
        if not repo:
            self.status_label.setText("Enter a repository first")
            return
        self.info_list.clear()
        self.status_label.setText("Fetching commits...")
        threading.Thread(target=self._fetch_commits, args=(repo,), daemon=True).start()

    def _fetch_commits(self, repo):
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/commits?per_page=10", timeout=10)
            commits = r.json()
            if not commits:
                QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "No commits found"))
                return
            for commit in commits[:10]:
                msg = commit.get('commit', {}).get('message', 'No message').split('\n')[0][:35]
                sha = commit.get('sha', '?')[:7]
                author = commit.get('commit', {}).get('author', {}).get('name', 'unknown')[:15]
                QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"{sha} {msg}... ({author})"))
            QtCore.QMetaObject.invokeMethod(self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Showing {len(commits[:10])} commits"))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self.info_list, "addItem", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Error: {e}"))


class SystemInfoPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.info_list = QtWidgets.QListWidget()
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.auto_refresh = QtWidgets.QCheckBox("Auto (5s)")
        self.auto_refresh.setStyleSheet(f"color: {FG};")
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.auto_refresh)
        btn_layout.addStretch()
        
        layout.addWidget(self.info_list)
        layout.addLayout(btn_layout)
        
        self.refresh_btn.clicked.connect(self.refresh)
        self.auto_refresh.toggled.connect(self.toggle_auto_refresh)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        
        self.refresh()

    def toggle_auto_refresh(self, checked):
        if checked:
            self.timer.start(5000)
        else:
            self.timer.stop()

    def refresh(self):
        self.info_list.clear()
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        
        net = psutil.net_io_counters()
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        self.info_list.addItem("═══ CPU ═══")
        self.info_list.addItem(f"  Usage: {cpu_percent}%")
        self.info_list.addItem(f"  Cores: {cpu_count}")
        if cpu_freq:
            self.info_list.addItem(f"  Frequency: {cpu_freq.current:.0f} MHz")
        
        self.info_list.addItem("═══ Memory ═══")
        self.info_list.addItem(f"  RAM: {mem.percent}% ({mem.used // (1024**3):.1f}GB / {mem.total // (1024**3):.1f}GB)")
        self.info_list.addItem(f"  Available: {mem.available // (1024**3):.1f}GB")
        self.info_list.addItem(f"  Swap: {swap.percent}% ({swap.used // (1024**3):.1f}GB / {swap.total // (1024**3):.1f}GB)")
        
        self.info_list.addItem("═══ Disk ═══")
        self.info_list.addItem(f"  Usage: {disk.percent}%")
        self.info_list.addItem(f"  Used: {disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB")
        self.info_list.addItem(f"  Free: {disk.free // (1024**3):.1f}GB")
        
        self.info_list.addItem("═══ Network ═══")
        self.info_list.addItem(f"  Sent: {net.bytes_sent // (1024**2):.1f} MB")
        self.info_list.addItem(f"  Received: {net.bytes_recv // (1024**2):.1f} MB")
        
        self.info_list.addItem("═══ System ═══")
        self.info_list.addItem(f"  Platform: {sys.platform}")
        self.info_list.addItem(f"  Python: {sys.version.split()[0]}")
        self.info_list.addItem(f"  Uptime: {str(uptime).split('.')[0]}")


class MediaPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(150)
        layout.addWidget(self.video_widget)
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        
        controls = QtWidgets.QHBoxLayout()
        self.open_btn = QtWidgets.QPushButton("Open")
        self.play_btn = QtWidgets.QPushButton("▶")
        self.stop_btn = QtWidgets.QPushButton("■")
        self.open_btn.setFixedWidth(60)
        self.play_btn.setFixedWidth(40)
        self.stop_btn.setFixedWidth(40)
        controls.addWidget(self.open_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        controls.addStretch()
        layout.addLayout(controls)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        layout.addWidget(self.slider)
        
        vol_layout = QtWidgets.QHBoxLayout()
        vol_layout.addWidget(QtWidgets.QLabel("Vol:"))
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        vol_layout.addWidget(self.volume_slider)
        layout.addLayout(vol_layout)
        
        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.toggle_play)
        self.stop_btn.clicked.connect(self.stop)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.slider.sliderMoved.connect(self.seek)
        self.player.playbackStateChanged.connect(self.update_button)
        
        self.audio_output.setVolume(0.5)

    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Media", "",
            "Media Files (*.mp4 *.mp3 *.wav *.avi *.mkv *.webm *.ogg *.flac);;All Files (*)"
        )
        if path:
            self.player.setSource(QtCore.QUrl.fromLocalFile(path))
            self.player.play()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop(self):
        self.player.stop()

    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    def update_position(self, position):
        self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(False)

    def update_duration(self, duration):
        self.slider.setRange(0, duration)

    def seek(self, position):
        self.player.setPosition(position)

    def update_button(self, state):
        self.play_btn.setText("❚❚" if state == QMediaPlayer.PlayingState else "▶")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LONHRO Terminal")
        self.resize(1200, 800)
        self.setup_ui()
        self.apply_styles()
        self.show_welcome()

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        left_panel = QtWidgets.QVBoxLayout()
        left_panel.setContentsMargins(10, 10, 10, 10)
        
        toolbar = QtWidgets.QHBoxLayout()
        self.ai_btn = QtWidgets.QPushButton("AI Chat")
        self.github_btn = QtWidgets.QPushButton("GitHub")
        self.system_btn = QtWidgets.QPushButton("System")
        self.media_btn = QtWidgets.QPushButton("Media")
        
        for btn in [self.ai_btn, self.github_btn, self.system_btn, self.media_btn]:
            btn.setFixedHeight(36)
            toolbar.addWidget(btn)
        toolbar.addStretch()
        
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setFixedHeight(36)
        toolbar.addWidget(self.save_btn)
        
        left_panel.addLayout(toolbar)
        
        self.terminal = TerminalWidget()
        left_panel.addWidget(self.terminal)
        
        left_container = QtWidgets.QWidget()
        left_container.setLayout(left_panel)
        main_layout.addWidget(left_container, stretch=1)
        
        self.ai_drawer = SlideDrawer("AI Chat")
        self.ai_drawer.add_widget(ChatGPTPanel())
        self.ai_drawer.add_stretch()
        
        self.github_drawer = SlideDrawer("GitHub")
        self.github_drawer.add_widget(GitHubPanel())
        self.github_drawer.add_stretch()
        
        self.system_drawer = SlideDrawer("System Info")
        self.system_drawer.add_widget(SystemInfoPanel())
        self.system_drawer.add_stretch()
        
        self.media_drawer = SlideDrawer("Media Player")
        self.media_drawer.add_widget(MediaPanel())
        self.media_drawer.add_stretch()
        
        main_layout.addWidget(self.ai_drawer)
        main_layout.addWidget(self.github_drawer)
        main_layout.addWidget(self.system_drawer)
        main_layout.addWidget(self.media_drawer)
        
        self.ai_btn.clicked.connect(lambda: self.toggle_drawer(self.ai_drawer))
        self.github_btn.clicked.connect(lambda: self.toggle_drawer(self.github_drawer))
        self.system_btn.clicked.connect(lambda: self.toggle_drawer(self.system_drawer))
        self.media_btn.clicked.connect(lambda: self.toggle_drawer(self.media_drawer))
        self.save_btn.clicked.connect(self.save_session)
        
        self.welcome = WelcomeOverlay(self)
        self.welcome.closed.connect(self.on_welcome_closed)

    def toggle_drawer(self, drawer):
        for d in [self.ai_drawer, self.github_drawer, self.system_drawer, self.media_drawer]:
            if d != drawer and d.isVisible():
                d.hide_drawer()
        
        if drawer.isVisible():
            drawer.hide_drawer()
        else:
            drawer.show_drawer()

    def show_welcome(self):
        self.welcome.setGeometry(self.rect())
        self.welcome.show()

    def on_welcome_closed(self):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'welcome'):
            self.welcome.setGeometry(self.rect())

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {BG};
                color: {FG};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #FF3399);
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF3399, stop:1 {ACCENT});
            }}
            QLineEdit, QPlainTextEdit, QListWidget {{
                background: {BG_DARKER};
                color: {FG};
                border: 1px solid #3D2030;
                border-radius: 6px;
                padding: 8px;
            }}
            QLineEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {ACCENT};
            }}
            QSlider::groove:horizontal {{
                background: #3D2030;
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {ACCENT};
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ACCENT};
                border-radius: 3px;
            }}
            QScrollBar:vertical {{
                background: {BG_DARKER};
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: #3D2030;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ACCENT};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #3D2030;
            }}
            QListWidget::item:hover {{
                background: #2D1520;
            }}
        """)

    def save_session(self):
        data = {"timestamp": datetime.now().isoformat()}
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)
        QtWidgets.QMessageBox.information(self, "Saved", "Session saved.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
