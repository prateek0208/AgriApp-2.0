import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database/farm_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  lat REAL,
                  lon REAL,
                  ndvi REAL,
                  moisture INTEGER,
                  soil_type TEXT,
                  yield_forecast INTEGER)''')
    conn.commit()
    conn.close()

def save_scan(lat, lon, ndvi, moisture, soil, yield_f):
    conn = sqlite3.connect('database/farm_records.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scans (timestamp, lat, lon, ndvi, moisture, soil_type, yield_forecast) VALUES (?,?,?,?,?,?,?)",
              (now, lat, lon, ndvi, moisture, soil, yield_f))
    conn.commit()
    conn.close()