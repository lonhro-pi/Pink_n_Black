#!/usr/bin/env python3
"""
Pink_n_Black Terminal - Main Application
"""

import os
import sys
import json
import threading
import subprocess
import random
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QUrl, QTimer, QProcess, Slot, Signal
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QLabel, QPlainTextEdit, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QMessageBox,
    QSlider, QComboBox
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData
from PySide6.QtMultimediaWidgets import QVideoWidget

import requests
import psutil

# ────────────────────────────────────────────────
#  CONFIG & CONSTANTS
# ────────────────────────────────────────────────

APP_DIR = Path.home() / ".pinknblack"
APP_DIR.mkdir(parents=True, exist_ok=True)

# Theme colors
BG_COLOR = "#000000"
FG_COLOR = "#FFD6F5"      # light pink
ACCENT_COLOR = "#FF1493"  # hot pink

# Small built-in Lonhro facts (you can also load from JSON later)
LONHRO_FACTS = [
    "Lonhro won 26 races from 35 starts, including 11 Group 1 victories.",
    "He was known for his aggressive racing style and looking back at rivals.",
    "The famous 'That's racing!' moment came after his 2003 George Main Stakes win.",
    "Lonhro raced successfully from age 2 through to age 6 — incredible longevity.",
    "He developed a huge public following and received a guard of honour when he retired.",
    "Many consider him one of the greatest middle-distance horses in Australian racing history."
]

# ────────────────────────────────────────────────
#  TERMINAL WIDGET (PTY fallback)
# ────────────────────────────────────────────────

class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Monospace", 11))
        self.output.setStyleSheet(f"background-color: {BG_COLOR}; color: {FG_COLOR}; border: none;")

        self.input = QLineEdit()
        self.input.setStyleSheet(f"background-color: #111111; color: {FG_COLOR}; border: 1px solid {ACCENT_COLOR};")
        self.input.returnPressed.connect(self.execute_command)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.process = QProcess(self)
        self.process.setProgram(os.environ.get("SHELL", "/bin/bash"))
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.start()

    @Slot()
    def handle_output(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.output.appendPlainText(data)
        self.output.ensureCursorVisible()

    @Slot()
    def execute_command(self):
        cmd = self.input.text() + "\n"
        self.output.appendPlainText(f"> {cmd.strip()}")
        self.process.write(cmd.encode())
        self.input.clear()

# ────────────────────────────────────────────────
#  CHATGPT PANEL
# ────────────────────────────────────────────────

class ChatGPTPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.history = QPlainTextEdit()
        self.history.setReadOnly(True)
        self.history.setStyleSheet(f"background-color: #111111; color: {FG_COLOR};")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask ChatGPT something...")
        self.input.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)

        hbox = QHBoxLayout()
        hbox.addWidget(self.input)
        hbox.addWidget(self.send_btn)

        self.layout.addWidget(QLabel("ChatGPT (gpt-4o-mini)"))
        self.layout.addWidget(self.history)
        self.layout.addLayout(hbox)

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        self.history.appendPlainText(f"\nYou: {text}")
        self.input.clear()
        self.history.appendPlainText("\nThinking...")

        threading.Thread(target=self.call_api, args=(text,), daemon=True).start()

    def call_api(self, prompt):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.append_response("[Error] OPENAI_API_KEY not set in environment")
            return

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.7
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=30)
            r.raise_for_status()
            response = r.json()["choices"][0]["message"]["content"].strip()
            self.append_response(response)
        except Exception as e:
            self.append_response(f"[Error] {str(e)}")

    def append_response(self, text):
        def update():
            self.history.appendPlainText(f"\nAssistant: {text}")
            self.history.ensureCursorVisible()
        QApplication.postEvent(self, update)

# ────────────────────────────────────────────────
#  GITHUB SEARCH PANEL
# ────────────────────────────────────────────────

class GitHubPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search GitHub repositories...")
        self.search_input.returnPressed.connect(self.search)

        self.btn = QPushButton("Search")
        self.btn.clicked.connect(self.search)

        self.results = QListWidget()

        hbox = QHBoxLayout()
        hbox.addWidget(self.search_input)
        hbox.addWidget(self.btn)

        self.layout.addWidget(QLabel("GitHub Search"))
        self.layout.addLayout(hbox)
        self.layout.addWidget(self.results)

    def search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.results.clear()
        self.results.addItem("Searching...")

        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        try:
            r = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": 15},
                timeout=12
            )
            r.raise_for_status()
            items = r.json().get("items", [])

            def update():
                self.results.clear()
                if not items:
                    self.results.addItem("No results found.")
                    return
                for repo in items:
                    name = repo["full_name"]
                    stars = repo["stargazers_count"]
                    desc = repo["description"] or "No description"
                    desc = (desc[:80] + "...") if len(desc) > 80 else desc
                    self.results.addItem(f"{name}  ★ {stars:,}  —  {desc}")
            QApplication.postEvent(self, update)
        except Exception as e:
            def err():
                self.results.clear()
                self.results.addItem(f"Error: {str(e)}")
            QApplication.postEvent(self, err)

# ────────────────────────────────────────────────
#  MEDIA PLAYER PANEL (QtMultimedia)
# ────────────────────────────────────────────────

class MediaPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.video_widget.hide()  # shown only when video is loaded

        self.status_label = QLabel("No media loaded")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.open_btn = QPushButton("Open File")
        self.open_btn.clicked.connect(self.open_file)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.player.play)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.player.pause)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.player.stop)

        controls = QHBoxLayout()
        controls.addWidget(self.open_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)

        self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.status_label)
        self.layout.addLayout(controls)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Media File",
            "", "Media Files (*.mp4 *.mkv *.avi *.mp3 *.wav *.flac)"
        )
        if not path:
            return

        video_extensions = (".mp4", ".avi", ".mkv", ".mov", ".wmv")

        url = QUrl.fromLocalFile(path)
        self.player.setSource(url)
        self.status_label.setText(f"Loaded: {os.path.basename(path)}")


        if path.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):

        self.video_widget.show()
        else:
        self.video_widget.hide()
