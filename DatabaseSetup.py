import sqlite3

def setup_database():
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
    
    print("Database setup completed!")

# run the function to set up the database
if __name__ == "__main__":
    setup_database()