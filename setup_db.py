import sqlite3

conn = sqlite3.connect('period_tracker.db')
cursor = conn.cursor()

# Drop old tables if they exist (to ensure a clean slate)
cursor.execute('DROP TABLE IF EXISTS user_cycles')
cursor.execute('DROP TABLE IF EXISTS users')

# Create users table
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create user_cycles table
cursor.execute('''
    CREATE TABLE user_cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        last_period_date DATE NOT NULL,
        cycle_length INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

conn.commit()
conn.close()
print("✅ Database and tables created successfully.")
