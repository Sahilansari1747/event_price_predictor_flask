import sqlite3

def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

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

    conn.commit()
    conn.close()
    print("✅ Tables created in booking.db")

if __name__ == '__main__':
    init_db()