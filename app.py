# app.py
import sys, os, json, subprocess, threading
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QListWidget, QLabel, QMessageBox, QLineEdit, QTextEdit)
from PySide6.QtCore import Qt
import adb_controller as adb
import ai_helper

SCRCPY_CMD = 'scrcpy'

class GameCaster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RasPi Game Caster')
        self.setMinimumSize(900, 520)
        self.scrcpy_proc = None
        self.device_ip = None
        self.mappings = {}
        self.load_mappings()

        layout = QVBoxLayout()

        top = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText('Phone IP (e.g. 192.168.43.1)')
        top.addWidget(self.ip_input)

        self.connect_btn = QPushButton('Connect (adb)')
        self.connect_btn.clicked.connect(self.connect_device)
        top.addWidget(self.connect_btn)

        self.stream_btn = QPushButton('Start Stream')
        self.stream_btn.clicked.connect(self.toggle_stream)
        top.addWidget(self.stream_btn)

        layout.addLayout(top)

        mid = QHBoxLayout()
        self.game_list = QListWidget()
        self.game_list.addItems(['default', 'Granny 1'])
        mid.addWidget(self.game_list)

        right = QVBoxLayout()
        self.mapping_display = QTextEdit()
        self.mapping_display.setReadOnly(True)
        right.addWidget(self.mapping_display)

        self.analyze_btn = QPushButton('Analyze & Add Mapping (AI)')
        self.analyze_btn.clicked.connect(self.analyze_game)
        right.addWidget(self.analyze_btn)

        self.refresh_map_btn = QPushButton('Show Mapping')
        self.refresh_map_btn.clicked.connect(self.show_mapping)
        right.addWidget(self.refresh_map_btn)

        mid.addLayout(right)
        layout.addLayout(mid)

        bottom = QHBoxLayout()
        self.log = QLabel('Status: idle')
        bottom.addWidget(self.log)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def load_mappings(self):
        try:
            with open('mappings.json', 'r') as f:
                self.mappings = json.load(f)
        except Exception:
            self.mappings = {}

    def save_mappings(self):
        try:
            with open('mappings.json', 'w') as f:
                json.dump(self.mappings, f, indent=2)
        except Exception as e:
            self.log.setText(f'Error saving mappings: {e}')

    def show_mapping(self):
        game = self.game_list.currentItem().text() if self.game_list.currentItem() else 'default'
        m = self.mappings.get(game, self.mappings.get('default', {}))
        pretty = json.dumps(m, indent=2)
        self.mapping_display.setText(pretty)

    def connect_device(self):
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, 'No IP', 'Enter phone IP address')
            return
        self.device_ip = ip
        rc, out, err = adb.connect(ip)
        if rc == 0:
            self.log.setText(f'Connected: {out or err}')
        else:
            self.log.setText(f'Connect failed: {err or out}')

    def toggle_stream(self):
        if self.scrcpy_proc and self.scrcpy_proc.poll() is None:
            self.scrcpy_proc.kill()
            self.scrcpy_proc = None
            self.stream_btn.setText('Start Stream')
            self.log.setText('Stream stopped')
            return
        try:
            cmd = [SCRCPY_CMD, '--stay-awake']
            self.scrcpy_proc = subprocess.Popen(cmd)
            self.stream_btn.setText('Stop Stream')
            self.log.setText('Streaming via scrcpy')
        except FileNotFoundError:
            QMessageBox.critical(self, 'Missing scrcpy', 'scrcpy not found. Install scrcpy on the Pi.')

    def analyze_game(self):
        game = self.game_list.currentItem().text() if self.game_list.currentItem() else None
        if not game:
            QMessageBox.warning(self, 'Pick game', 'Select a game from the list first')
            return
        self.mapping_display.setText('Analyzing... (calls OpenAI)')
        def worker():
            try:
                result = ai_helper.analyze_game(game)
            except Exception as e:
                self.mapping_display.setText(f'AI error: {e}')
                return
            # If AI returned parsed JSON, try to convert to mapping
            if isinstance(result, dict) and 'keys' in result:
                mapping = {}
                for item in result['keys']:
                    key = item.get('key', '').upper()
                    action = item.get('action', 'action')
                    code = item.get('android_keycode')
                    if key:
                        if code:
                            mapping[key] = {'type':'key','android_keycode':code,'desc':action}
                        else:
                            mapping[key] = {'type':'key','desc':action}
                self.mappings[game] = mapping
                self.save_mappings()
                self.mapping_display.setText(json.dumps(mapping, indent=2))
            else:
                # show raw
                self.mapping_display.setText(str(result))
        threading.Thread(target=worker, daemon=True).start()

    def keyPressEvent(self, event):
        key = event.key()
        key_text = event.text().upper()
        if key_text == '':
            key_name = self.qt_key_to_name(key)
        else:
            key_name = key_text
        self.handle_key(key_name, down=True)

    def keyReleaseEvent(self, event):
        key_text = event.text().upper()
        if key_text == '':
            key_name = self.qt_key_to_name(event.key())
        else:
            key_name = key_text
        self.handle_key(key_name, down=False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            self.handle_mouse('LEFT_CLICK', x, y)
        elif event.button() == Qt.RightButton:
            self.handle_mouse('RIGHT_CLICK')

    def handle_key(self, key_name, down=True):
        game = self.game_list.currentItem().text() if self.game_list.currentItem() else 'default'
        mapping = self.mappings.get(game, {}).get(key_name)
        if not mapping:
            mapping = self.mappings.get('default', {}).get(key_name)
        if not mapping:
            self.log.setText(f'No mapping for {key_name}')
            return
        if mapping['type'] == 'key' and down:
            code = mapping.get('android_keycode')
            if code:
                adb.send_keyevent(code)
                self.log.setText(f'Sent key {key_name} -> keycode {code}')

    def handle_mouse(self, action, x=None, y=None):
        if action == 'LEFT_CLICK' and x is not None and y is not None:
            screen_w = QApplication.primaryScreen().size().width()
            screen_h = QApplication.primaryScreen().size().height()
            phone_w, phone_h = 1080, 1920
            phone_x = int(x / screen_w * phone_w)
            phone_y = int(y / screen_h * phone_h)
            adb.tap(phone_x, phone_y)
            self.log.setText(f'Tap at {phone_x},{phone_y}')
        elif action == 'RIGHT_CLICK':
            adb.send_keyevent(4)
            self.log.setText('Sent BACK (right click)')

    def qt_key_to_name(self, qt_key):
        mapping = {
            Qt.Key_Up: 'DPAD_UP',
            Qt.Key_Down: 'DPAD_DOWN',
            Qt.Key_Left: 'DPAD_LEFT',
            Qt.Key_Right: 'DPAD_RIGHT',
            Qt.Key_Escape: 'ESCAPE',
            Qt.Key_Space: 'SPACE'
        }
        return mapping.get(qt_key, str(qt_key))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GameCaster()
    window.show()
    sys.exit(app.exec())
