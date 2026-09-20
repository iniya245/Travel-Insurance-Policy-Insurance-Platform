import sqlite3

DB_NAME = "travel_insurance.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insurance_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        coverage REAL NOT NULL,
        premium REAL NOT NULL,
        duration INTEGER NOT NULL,
        benefits TEXT,
        exclusions TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        application_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (plan_id) REFERENCES insurance_plans(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_number TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL,
        start_date TEXT,
        end_date TEXT,
        coverage REAL,
        premium REAL,
        status TEXT DEFAULT 'Active',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (plan_id) REFERENCES insurance_plans(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        claim_amount REAL,
        approved_amount REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        admin_remark TEXT,
        claim_date TEXT,
        FOREIGN KEY (policy_id) REFERENCES policies(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS renewals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id INTEGER NOT NULL,
        old_end_date TEXT,
        new_end_date TEXT,
        premium REAL,
        status TEXT DEFAULT 'Pending',
        renewal_date TEXT,
        FOREIGN KEY (policy_id) REFERENCES policies(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        policy_id INTEGER,
        amount REAL NOT NULL,
        payment_type TEXT,
        status TEXT DEFAULT 'Success',
        transaction_id TEXT,
        payment_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (policy_id) REFERENCES policies(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        discount REAL DEFAULT 0,
        status TEXT DEFAULT 'Active'
    )
    """)

    conn.commit()
    conn.close()

    print("Database Created Successfully")


if __name__ == "__main__":
    init_database()