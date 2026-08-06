import sqlite3

conn = sqlite3.connect("travel_insurance.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    destination TEXT,
    travel_date TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER,
    claim_reason TEXT
)
""")
conn.commit()

print("Database Created Successfully")

conn.close()