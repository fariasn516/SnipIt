import datetime
import pyperclip
import sqlite3
from time import sleep

# saves clipboard text and the time it was copied to a database
def save_to_database(text):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get current time
    conn = sqlite3.connect("clipboard_history.db")  # connect to the database (or create it)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO history (text, timestamp) VALUES (?, ?)", (text, timestamp))  # add text and time
    conn.commit()  # save the changes
    conn.close()  # close the connection

# keeps checking the clipboard for new stuff
def monitor_clipboard():
    last_clipboard = None  # remembers the last thing copied
    while True:
        try:
            current_clipboard = pyperclip.paste()  # get whatever's currently in the clipboard
            if current_clipboard != last_clipboard and isinstance(current_clipboard, str):  # check if it's new
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # get the current time
                print(f"New clipboard entry detected: {current_clipboard} at {timestamp}")  # print the new text and time
                save_to_database(current_clipboard)  # save it to the database
                last_clipboard = current_clipboard  # update the last clipboard text
        except Exception as e:
            print(f"Error: {e}")  # if something breaks, print the error
        sleep(0.5)  # wait a bit before checking again

# run the clipboard monitor if this file is executed
if __name__ == "__main__":
    monitor_clipboard()