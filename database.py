import sqlite3
import random
import time

def init_db():
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, phone TEXT UNIQUE, name TEXT, 
                  verified INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS otps
                 (phone TEXT PRIMARY KEY, otp_code TEXT, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def generate_otp(phone):
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    
    otp = str(random.randint(100000, 999999))
    c.execute("DELETE FROM otps WHERE phone=?", (phone,))
    c.execute("INSERT INTO otps (phone, otp_code) VALUES (?, ?)", (phone, otp))
    
    conn.commit()
    conn.close()
    return otp

def verify_otp(phone, otp_code):
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    
    c.execute("SELECT otp_code FROM otps WHERE phone=?", (phone,))
    result = c.fetchone()
    
    if result and result[0] == otp_code:
        c.execute("UPDATE users SET verified=1 WHERE phone=?", (phone,))
        c.execute("DELETE FROM otps WHERE phone=?", (phone,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def add_user(user_id, phone, name):
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (user_id, phone, name, verified) VALUES (?, ?, ?, 0)", 
                 (user_id, phone, name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    
    conn.close()

def search_phone(phone):
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    
    c.execute("SELECT name FROM users WHERE phone=? AND verified=1", (phone,))
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else None

def get_user_by_phone(phone):
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    
    c.execute("SELECT user_id, name FROM users WHERE phone=?", (phone,))
    result = c.fetchone()
    conn.close()
    
    return result if result else None
