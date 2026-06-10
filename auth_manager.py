import sqlite3
import bcrypt

def init_auth_db():
    conn = sqlite3.connect("database/farmer_auth.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Farmer'
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    # bcrypt generates and handles the salt automatically
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_pw):
    # Checks plain text password against stored hash
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pw)

def create_user(username, password, role='Farmer'):
    init_auth_db()
    conn = sqlite3.connect("database/farmer_auth.db")
    c = conn.cursor()
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users(username, password, role) VALUES (?,?,?)", 
                  (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("database/farmer_auth.db")
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and check_password(password, result[0]):
        return {"username": username, "role": result[1]}
    return None