import sqlite3
from datetime import date

class DatabaseHandler:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        try:
            self.conn = sqlite3.connect('mood_tracker.db')
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            print("Подключено к SQLite")
            return True
        except Exception as e:
            print(f"Ошибка БД: {e}")
            self.conn = None
            return False
    
    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                entry_date DATE NOT NULL,
                mood_score INTEGER,
                work_hours REAL,
                sleep_hours REAL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, entry_date)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                reminder_time TEXT DEFAULT '20:00:00',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        cur.close()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_or_create_user(self, tg_id, username, first_name):
        if not self.conn:
            return None
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE telegram_id = ?", (tg_id,))
        row = cur.fetchone()
        if row:
            user_id = row[0]
        else:
            cur.execute("INSERT INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)", (tg_id, username, first_name))
            user_id = cur.lastrowid
        self.conn.commit()
        cur.close()
        return user_id
    
    def save_entry(self, user_id, date_val, mood, work, sleep, comment):
        if not self.conn:
            print("Нет подключения при сохранении")
            return
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO mood_entries (user_id, entry_date, mood_score, work_hours, sleep_hours, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, entry_date) DO UPDATE SET
                mood_score = excluded.mood_score,
                work_hours = excluded.work_hours,
                sleep_hours = excluded.sleep_hours,
                comment = excluded.comment
        """, (user_id, date_val, mood, work, sleep, comment))
        self.conn.commit()
        print(f"Сохранено: user_id={user_id}, date={date_val}, mood={mood}, work={work}, sleep={sleep}")
        cur.close()
    
    def get_weekly(self, user_id):
        if not self.conn:
            return []
        cur = self.conn.cursor()
        cur.execute("SELECT entry_date, mood_score, work_hours, sleep_hours, comment FROM mood_entries WHERE user_id = ? AND entry_date >= date('now', '-7 days') ORDER BY entry_date DESC", (user_id,))
        rows = cur.fetchall()
        cur.close()
        return [dict(row) for row in rows]
    
    def get_monthly(self, user_id):
        if not self.conn:
            return []
        cur = self.conn.cursor()
        cur.execute("SELECT entry_date, mood_score, work_hours, sleep_hours, comment FROM mood_entries WHERE user_id = ? AND entry_date >= date('now', '-30 days') ORDER BY entry_date DESC", (user_id,))
        rows = cur.fetchall()
        cur.close()
        return [dict(row) for row in rows]
    
    def get_all(self, user_id):
        if not self.conn:
            return []
        cur = self.conn.cursor()
        cur.execute("SELECT entry_date, mood_score, work_hours, sleep_hours FROM mood_entries WHERE user_id = ? ORDER BY entry_date", (user_id,))
        rows = cur.fetchall()
        cur.close()
        return [dict(row) for row in rows]
    
    def delete_all(self, user_id):
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute("DELETE FROM mood_entries WHERE user_id = ?", (user_id,))
        self.conn.commit()
        cur.close()
    
    def get_reminder_time(self, user_id):
        if not self.conn:
            return '20:00:00'
        cur = self.conn.cursor()
        cur.execute("SELECT reminder_time FROM user_settings WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return row[0]
        return '20:00:00'
    
    def set_reminder_time(self, user_id, reminder_time):
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO user_settings (user_id, reminder_time) VALUES (?, ?)", (user_id, reminder_time))
        self.conn.commit()
        cur.close()