import sys
import sqlite3
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
from pynput.keyboard import Controller as KeyboardController


# this watches the clipboard in the background and notices when you copy something new
class ClipboardMonitor(QThread):
    new_entry = pyqtSignal(str)  # signal to tell when new text is copied

    def run(self):
        recent_value = ""  # keep track of the last thing copied
        while True:
            tmp_value = pyperclip.paste()  # check what's currently in the clipboard
            if tmp_value != recent_value and isinstance(tmp_value, str):  # if it's new text, save it
                recent_value = tmp_value
                self.new_entry.emit(recent_value)  # send the new text out
            self.msleep(100)  # pause a bit so it's not constantly running

# this makes a little widget for each clipboard entry
class ClipboardEntryWidget(QWidget):
    def __init__(self, parent, text, timestamp):
        super().__init__()
        layout = QHBoxLayout()  # horizontal layout for text and timestamp
        self.text_label = QLabel(text)  # shows the clipboard text
        self.text_label.setWordWrap(True)  # make sure long text wraps nicely

        self.timestamp_label = QLabel(timestamp)  # shows when it was copied
        self.timestamp_label.setAlignment(Qt.AlignRight)  # push it to the right
        self.timestamp_label.setStyleSheet("margin-right: 100px;")  # give it some space

        layout.addWidget(self.text_label)
        layout.addWidget(self.timestamp_label)
        self.setLayout(layout)  # set the layout for this widget

# this is the main app window that shows your clipboard history
class ClipboardHistoryUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard History")  # set the window title
        self.setGeometry(100, 100, 500, 400)  # size and position of the window
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # keep it on top of other windows

        main_widget = QWidget()
        layout = QVBoxLayout()  # vertical layout for everything
        self.history_list = QListWidget()  # this will hold all the clipboard items
        self.history_list.keyPressEvent = self.list_key_press  # make custom key handling
        layout.addWidget(self.history_list)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.init_database()  # set up the database to save the history
        self.monitor = ClipboardMonitor()  # create the clipboard watcher
        self.monitor.new_entry.connect(self.add_new_entry)  # connect new entries to adding them
        self.monitor.start()  # start watching the clipboard
        self.load_clipboard_history()  # load existing history from the database

        self.setStyle()  # make it look cute

    def setStyle(self):
        """make the app look light pink and nice"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFCCCB;  /* light pink background */
            }

            QWidget {
                background-color: #FFCCCB;  /* even lighter pink */
            }

            QListWidget {
                background-color: #FFCCCB;  /* same soft pink for the list */
                border: 1px solid #FFCCCB;  /* remove border to keep it clean */
                padding: 5px;
            }
        """)

    # sets up a database file to store the clipboard entries
    def init_database(self):
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE,
            timestamp TEXT
        )
        """)  # create a table if it doesn't already exist
        conn.commit()
        conn.close()

    # loads saved clipboard history from the database into the app
    def load_clipboard_history(self):
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text, timestamp FROM history ORDER BY id DESC LIMIT 50")
        for row in cursor.fetchall():  # go through the results
            self.add_history_item(row[0], row[1])  # add each one to the app
        conn.close()

    # adds new copied text to the database and the app
    def add_new_entry(self, text):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get the current time
        conn = sqlite3.connect("clipboard_history.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO history (text, timestamp) VALUES (?, ?)", (text, timestamp))
        conn.commit()
        conn.close()
        self.add_history_item(text, timestamp)  # show it in the app too

    # adds an item to the list of clipboard entries in the app
    def add_history_item(self, text, timestamp):
        list_widget_item = QListWidgetItem(self.history_list)  # create a new item for the list
        entry_widget = ClipboardEntryWidget(self, text, timestamp)  # create the widget for this entry
        list_widget_item.setSizeHint(entry_widget.sizeHint())
        self.history_list.insertItem(0, list_widget_item)  # add it to the top of the list
        self.history_list.setItemWidget(list_widget_item, entry_widget)  # attach the widget

        self.history_list.scrollToItem(list_widget_item, QAbstractItemView.EnsureVisible)  # scroll to show it

    # lets you use the Enter key to do stuff with the selected clipboard entry
    def list_key_press(self, event):
        if event.key() == Qt.Key_Return:  # check if the Enter key was pressed
            self.use_selected_entry()  # do something with the selected item
        else:
            super(QListWidget, self.history_list).keyPressEvent(event)  # handle other keys normally

# this starts the whole app
if __name__ == "__main__":
    app = QApplication(sys.argv)  # create the app
    window = ClipboardHistoryUI()  # make the main window
    window.show()  # show the window
    sys.exit(app.exec_())  # run the app