import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from datetime import datetime
import requests
import psutil
from PySide6 import QtCore, QtGui, QtWidgets

# Optional Imports
HAS_QTERMWIDGET = False
try:
    from qtermwidget import QTermWidget
    HAS_QTERMWIDGET = True
except: HAS_QTERMWIDGET = False

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# Constants & Paths
BG, FG, ACCENT = "#000000", "#FFD6F5", "#FF1493"
APP_DIR = Path.home() / ".pinkblack-terminal"
APP_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = APP_DIR / "session.json"
FACTS_FILE = Path(__file__).parent / "lonhro_facts.json"

class TerminalWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if HAS_QTERMWIDGET:
            self.term = QTermWidget()
            layout.addWidget(self.term)
        else:
            self.output = QtWidgets.QPlainTextEdit(readOnly=True)
            self.output.setStyleSheet("background-color: #0a0a0a; font-family: monospace;")
            layout.addWidget(self.output)
            self._start_shell()

    def _start_shell(self):
        import pty
        master, slave = pty.openpty()
        subprocess.Popen([os.environ.get("SHELL", "/bin/bash")], stdin=slave, stdout=slave, stderr=slave)
        def reader():
            while True:
                data = os.read(master, 1024).decode(errors="ignore")
                if not data: break
                QtCore.QMetaObject.invokeMethod(self.output, "appendPlainText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, data))
        threading.Thread(target=reader, daemon=True).start()

class ChatGPTPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.history = QtWidgets.QPlainTextEdit(readOnly=True)
        self.input = QtWidgets.QLineEdit(placeholderText="Ask AI...")
        self.btn = QtWidgets.QPushButton("Send")
        layout.addWidget(QtWidgets.QLabel("ChatGPT (gpt-4o-mini)"))
        layout.addWidget(self.history)
        layout.addWidget(self.input)
        layout.addWidget(self.btn)
        self.btn.clicked.connect(self.send)

    def send(self):
        prompt = self.input.text().strip()
        key = os.environ.get("OPENAI_API_KEY")
        if not key: 
            self.history.appendPlainText("[Error] OPENAI_API_KEY not set")
            return
        self.history.appendPlainText(f"User: {prompt}")
        self.input.clear()
        threading.Thread(target=self._call, args=(prompt, key), daemon=True).start()

    def _call(self, prompt, key):
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {key}"},
                             json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}, timeout=15)
            text = r.json()["choices"][0]["message"]["content"]
            QtCore.QMetaObject.invokeMethod(self.history, "appendPlainText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"AI: {text}"))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self.history, "appendPlainText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Error: {e}"))

class MediaPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(200)
        layout.addWidget(self.video_widget)
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        
        controls = QtWidgets.QHBoxLayout()
        self.open_btn = QtWidgets.QPushButton("Open File")
        self.play_btn = QtWidgets.QPushButton("Play")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        controls.addWidget(self.open_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        layout.addWidget(self.slider)
        
        self.volume_layout = QtWidgets.QHBoxLayout()
        self.volume_label = QtWidgets.QLabel("Volume:")
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_layout.addWidget(self.volume_label)
        self.volume_layout.addWidget(self.volume_slider)
        layout.addLayout(self.volume_layout)
        
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
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("Pause")
        else:
            self.play_btn.setText("Play")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pink and Black Terminal")
        self.resize(1200, 800)
        self.setup_ui()
        self.load_session()

    def setup_ui(self):
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(ChatGPTPanel(), "AI")
        tabs.addTab(MediaPanel(), "Media")
        
        # GitHub & System Panels
        self.gh = QtWidgets.QListWidget()
        tabs.addTab(self.gh, "GitHub")
        
        splitter.addWidget(TerminalWidget())
        splitter.addWidget(tabs)
        splitter.setStretchFactor(0, 3)
        
        # Bottom Bar
        bottom = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save Session")
        self.kill_btn = QtWidgets.QPushButton("KILL DESKTOP")
        bottom.addWidget(self.save_btn); bottom.addWidget(self.kill_btn)
        
        main_v = QtWidgets.QVBoxLayout()
        main_v.addWidget(splitter)
        main_v.addLayout(bottom)
        
        central = QtWidgets.QWidget(); central.setLayout(main_v)
        self.setCentralWidget(central)
        self.setStyleSheet(f"QWidget {{ background: {BG}; color: {FG}; }} QPushButton {{ background: {ACCENT}; color: #000; }}")
        
        self.save_btn.clicked.connect(self.save_session)
        self.kill_btn.clicked.connect(self.kill_desktop)

    def save_session(self):
        data = {"timestamp": datetime.now().isoformat()}
        with open(SESSION_FILE, "w") as f: json.dump(data, f)
        QtWidgets.QMessageBox.information(self, "Saved", "Workspace saved.")

    def load_session(self):
        if SESSION_FILE.exists(): pass # Restore logic here

    def kill_desktop(self):
        reply = QtWidgets.QMessageBox.question(self, 'Confirm', 'Log out or restart desktop?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            try: subprocess.run(['qdbus', 'org.kde.ksmserver', '/KSMServer', 'logout', '0', '0', '0'])
            except: QtWidgets.QApplication.quit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec())
