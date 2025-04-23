import sqlite3

def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    # Create booked_events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booked_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            event_type TEXT,
            guest_count INTEGER,
            venue_area REAL,
            food_type TEXT,
            decoration TEXT,
            entertainment TEXT,
            duration REAL,
            price REAL,
            event_date TEXT
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Tables 'booked_events' and 'users' are created or already exist.")

# Run when executed directly
if __name__ == '__main__':
    init_db()