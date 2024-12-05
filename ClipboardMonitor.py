import datetime
import pyperclip
import sqlite3
from time import sleep

def save_to_database(text):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("clipboard_history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO history (text, timestamp) VALUES (?, ?)", (text, timestamp))
    conn.commit()
    conn.close()

def monitor_clipboard():
    """Continuously monitors the clipboard for changes."""
    last_clipboard = None 
    while True:
        try:
            current_clipboard = pyperclip.paste()  
            if current_clipboard != last_clipboard and isinstance(current_clipboard, str):
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                print(f"New clipboard entry detected: {current_clipboard} at {timestamp}")
                save_to_database(current_clipboard) 
                last_clipboard = current_clipboard 
        except Exception as e:
            print(f"Error: {e}")
        sleep(0.5)  

if __name__ == "__main__":
    monitor_clipboard()