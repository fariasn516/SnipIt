import sys
import sqlite3
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
from pynput.keyboard import Controller as KeyboardController

class ClipboardMonitor(QThread):
    new_entry = pyqtSignal(str)

    def run(self):
        recent_value = ""
        while True:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value and isinstance(tmp_value, str):
                recent_value = tmp_value
                self.new_entry.emit(recent_value)
            self.msleep(100)

class ClipboardEntryWidget(QWidget):
    def __init__(self, parent, text, timestamp):
        super().__init__()
        layout = QHBoxLayout()
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        
        self.timestamp_label = QLabel(timestamp)
        self.timestamp_label.setAlignment(Qt.AlignRight)

        self.timestamp_label.setStyleSheet("margin-right: 100px;")  

        layout.addWidget(self.text_label)
        layout.addWidget(self.timestamp_label)
        self.setLayout(layout)

class ClipboardHistoryUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard History")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        main_widget = QWidget()
        layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.keyPressEvent = self.list_key_press
        layout.addWidget(self.history_list)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.init_database()
        self.monitor = ClipboardMonitor()
        self.monitor.new_entry.connect(self.add_new_entry)
        self.monitor.start()
        self.load_clipboard_history()

        self.setStyle()

    def setStyle(self):
        """Apply custom styles (light pink and coquette colors)"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFCCCB;  /* Light pink background */
            }

            QWidget {
                background-color: #FFCCCB;  /* Lightest pink for widgets */
            }

            QListWidget {
                background-color: #FFCCCB;  /* Soft pink for the history list */
                border: 1px solid #FFCCCB;  /* Light border around the list */
                padding: 5px;
            }
        """)

    def init_database(self):
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE,
            timestamp TEXT
        )
        """)
        conn.commit()
        conn.close()

    def load_clipboard_history(self):
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text, timestamp FROM history ORDER BY id DESC LIMIT 50")
        for row in cursor.fetchall():
            self.add_history_item(row[0], row[1]) 
        conn.close()

    def add_new_entry(self, text):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO history (text, timestamp) VALUES (?, ?)", (text, timestamp))
        conn.commit()
        conn.close()
        self.add_history_item(text, timestamp)  

    def add_history_item(self, text, timestamp):
        list_widget_item = QListWidgetItem(self.history_list)
        entry_widget = ClipboardEntryWidget(self, text, timestamp)
        list_widget_item.setSizeHint(entry_widget.sizeHint())
        self.history_list.insertItem(0, list_widget_item)
        self.history_list.setItemWidget(list_widget_item, entry_widget)

        self.history_list.scrollToItem(list_widget_item, QAbstractItemView.EnsureVisible)

    def list_key_press(self, event):
        if event.key() == Qt.Key_Return:
            self.use_selected_entry()
        else:
            super(QListWidget, self.history_list).keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipboardHistoryUI()
    window.show()
    sys.exit(app.exec_())
