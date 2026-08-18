import sqlite3
from core.paths import get_path
import pandas as pd
from datetime import datetime

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(get_path('data', 'farm_data.db'))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            location TEXT,
            nitrogen INTEGER,
            phosphorus INTEGER,
            potassium INTEGER,
            ph REAL,
            rainfall REAL,
            predicted_crop TEXT,
            predicted_price REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            location TEXT,
            crop TEXT,
            lang TEXT,
            alert_type TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_record(location, n, p, k, ph, rainfall, crop, price):
    """Saves a new prediction record."""
    conn = sqlite3.connect(get_path('data', 'farm_data.db'))
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO history (timestamp, location, nitrogen, phosphorus, potassium, ph, rainfall, predicted_crop, predicted_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ts, location, n, p, k, ph, rainfall, crop, price))
    conn.commit()
    conn.close()

def get_history():
    """Returns all records as a Pandas DataFrame."""
    conn = sqlite3.connect(get_path('data', 'farm_data.db'))
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id ASC", conn)
    conn.close()
    return df

# --- SUBSCRIBER MANAGEMENT ---

def add_subscriber(phone, location, crop, lang="en", alert_type="Full"):
    """Adds a new subscriber to receive automated WhatsApp alerts."""
    try:
        conn = sqlite3.connect(get_path('data', 'farm_data.db'))
        cursor = conn.cursor()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT OR REPLACE INTO subscribers (phone, location, crop, lang, alert_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (phone, location, crop, lang, alert_type, ts))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding subscriber: {e}")
        return False

def remove_subscriber(phone):
    """Removes a subscriber."""
    try:
        conn = sqlite3.connect(get_path('data', 'farm_data.db'))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM subscribers WHERE phone = ?', (phone,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error removing subscriber: {e}")
        return False

def get_subscribers():
    """Returns all subscribers as a list of dicts."""
    conn = sqlite3.connect(get_path('data', 'farm_data.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def is_subscribed(phone):
    """Check if a number is subscribed."""
    conn = sqlite3.connect(get_path('data', 'farm_data.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM subscribers WHERE phone = ?', (phone,))
    res = cursor.fetchone()
    conn.close()
    return res is not None
