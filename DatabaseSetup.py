import sqlite3

# Database Setup
def setup_database():
    """Creates a database and initializes the clipboard history table."""
    conn = sqlite3.connect("clipboard_history.db")  # Create or connect to the database file
    cursor = conn.cursor()  # Create a cursor to execute SQL commands
    
    # SQL command to create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each entry
            text TEXT UNIQUE,                      -- Clipboard text (unique entries)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- Timestamp of entry
        )
    """)
    
    conn.commit()  # Save changes to the database
    conn.close()   # Close the connection to free resources
    
    print("Database setup completed!")

# Run the function to set up the database
if __name__ == "__main__":
    setup_database()