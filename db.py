import sqlite3
from datetime import datetime

def get_db():
    return sqlite3.connect('productivity.db')

def setup():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            reminder_time TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date DATE,
            mood INTEGER,
            study_hours REAL,
            sleep_hours REAL,
            comment TEXT
        )
        
    ''')
    cur.execute('''
         INSERT INTO records (user_id, date, mood, study_hours, sleep_hours, comment)
        VALUES (6555013493, '2026-06-16', 3, 6.0, 6.5, 'Адам')
        


    ''')
    conn.commit()
    conn.close()

def create_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def add_record(user_id, mood, study, sleep, comment):
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cur.execute('''
        INSERT INTO records (user_id, date, mood, study_hours, sleep_hours, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, today, mood, study, sleep, comment))
    conn.commit()
    conn.close()

def get_records_by_period(user_id, days):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT date, mood, study_hours, sleep_hours, comment
        FROM records
        WHERE user_id = ? AND date >= date('now', ?)
        ORDER BY date DESC
    ''', (user_id, f'-{days} days'))
    data = cur.fetchall()
    conn.close()
    return data

def get_all_records(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT date, mood, study_hours, sleep_hours, comment
        FROM records
        WHERE user_id = ?
        ORDER BY date DESC
    ''', (user_id,))
    data = cur.fetchall()
    conn.close()
    return data

def clear_user_data(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM records WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def save_reminder_time(user_id, time_str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE users SET reminder_time = ? WHERE user_id = ?', (time_str, user_id))
    conn.commit()
    conn.close()

def get_reminder_time(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT reminder_time FROM users WHERE user_id = ?', (user_id,))
    data = cur.fetchone()
    conn.close()
    return data[0] if data else None

def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT user_id, reminder_time FROM users WHERE reminder_time IS NOT NULL')
    data = cur.fetchall()
    conn.close()
    return data

setup()
