import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect('database/farm_data.db')
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
    conn.commit()
    conn.close()

def add_record(location, n, p, k, ph, rainfall, crop, price):
    """Saves a new prediction record."""
    conn = sqlite3.connect('database/farm_data.db')
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
    conn = sqlite3.connect('database/farm_data.db')
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id ASC", conn)
    conn.close()
    return df