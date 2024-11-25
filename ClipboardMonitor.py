import pyperclip
import sqlite3
from time import sleep

def save_to_database(text):
    """Saves a clipboard entry to the database."""
    conn = sqlite3.connect("clipboard_history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO history (text) VALUES (?)", (text,))
    conn.commit()
    conn.close()

def monitor_clipboard():
    """Continuously monitors the clipboard for changes."""
    last_clipboard = None  # Keeps track of the last clipboard content
    while True:
        try:
            current_clipboard = pyperclip.paste()  # Get the current clipboard content
            if current_clipboard != last_clipboard and isinstance(current_clipboard, str):
                print(f"New clipboard entry detected: {current_clipboard}")
                save_to_database(current_clipboard)
                last_clipboard = current_clipboard  # Update the last clipboard value
        except Exception as e:
            print(f"Error: {e}")
        sleep(0.5)  # Adjust frequency of checks for performance

if __name__ == "__main__":
    monitor_clipboard()