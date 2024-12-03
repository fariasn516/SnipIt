import sys
import sqlite3
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

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
    def __init__(self, parent, text):
        super().__init__()
        layout = QHBoxLayout()
        
        # Main text
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)

        layout.addWidget(self.text_label)
        self.setLayout(layout)

class ClipboardHistoryUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard History")
        self.setGeometry(100, 100, 500, 400)

        # Main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Clipboard history list
        self.history_list = QListWidget()
        self.history_list.keyPressEvent = self.list_key_press
        layout.addWidget(self.history_list)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Start monitoring clipboard
        self.monitor = ClipboardMonitor()
        self.monitor.new_entry.connect(self.add_new_entry)
        self.monitor.start()

        self.load_clipboard_history()

    def load_clipboard_history(self):
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM history ORDER BY id ASC LIMIT 50")
        for row in cursor.fetchall():
            text = row[0]
            self.add_history_item(text)
        conn.close()

    def add_new_entry(self, text):
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO history (text) VALUES (?)", (text,))
        conn.commit()
        conn.close()

        self.add_history_item(text)

    def add_history_item(self, text):
        list_widget_item = QListWidgetItem(self.history_list)
        entry_widget = ClipboardEntryWidget(self, text)
        list_widget_item.setSizeHint(entry_widget.sizeHint())
        self.history_list.addItem(list_widget_item)
        self.history_list.setItemWidget(list_widget_item, entry_widget)
        self.history_list.scrollToBottom()

    def list_key_press(self, event):
        if event.key() == Qt.Key_Return:
            current_item = self.history_list.currentItem()
            if current_item:
                widget = self.history_list.itemWidget(current_item)
                text = widget.text_label.text()
                QApplication.clipboard().setText(text)
                print(f"Copied to clipboard: {text}")
                self.close()
        else:
            super(QListWidget, self.history_list).keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipboardHistoryUI()
    window.show()
    sys.exit(app.exec_())