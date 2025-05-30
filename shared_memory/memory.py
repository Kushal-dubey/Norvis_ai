# shared_memory/memory.py

import sqlite3
from datetime import datetime

class SharedMemory:
    def __init__(self, db_path="shared_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                content TEXT,
                result TEXT,
                extracted_values TEXT,
                timestamp TEXT,
                thread_id TEXT,
                type TEXT
            )
        ''')
        self.conn.commit()

    def log_memory(self, source, type_, extracted_values, content, result, thread_id):
        timestamp = datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO shared_memory (source, content, result, extracted_values, timestamp, thread_id, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (source, content, result, extracted_values, timestamp, thread_id, type_))
        self.conn.commit()

    def fetch_all(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM shared_memory')
        return cursor.fetchall()
