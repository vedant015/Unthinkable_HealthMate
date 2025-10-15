import sqlite3
import time

class ConversationStore:
    def __init__(self, db_path='conversations.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Messages table
            c.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ts INTEGER NOT NULL
                )
            ''')
            # Sessions table
            c.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
            ''')
            conn.commit()
    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM messages')
            c.execute('DELETE FROM sessions')
            conn.commit()
    # Create new chat session
    def create_session(self, session_id, name="New Chat"):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO sessions (session_id, name, created_at) VALUES (?, ?, ?)',
                      (session_id, name, int(time.time())))
            conn.commit()

    # Get all sessions
    def get_sessions(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT session_id, name, created_at FROM sessions ORDER BY created_at DESC')
            rows = c.fetchall()
            return [{'session_id': r[0], 'name': r[1], 'created_at': r[2]} for r in rows]

    # Rename session title (only if name is still "New Chat")
    def rename_session(self, session_id, new_name):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT name FROM sessions WHERE session_id = ?', (session_id,))
            row = c.fetchone()
            if row and row[0] == "New Chat":  # rename only if default
                c.execute('UPDATE sessions SET name = ? WHERE session_id = ?', (new_name, session_id))
                conn.commit()

    # Add message to conversation
    def append(self, session_id, role, content):
        ts = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO messages (session_id, role, content, ts) VALUES (?, ?, ?, ?)',
                      (session_id, role, content, ts))
            conn.commit()

    # Get messages for a session
    def get_messages(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
            rows = c.fetchall()
            return [{'role': r[0], 'content': r[1]} for r in rows]

    # Format for LLM input
    def get_messages_for_llm(self, session_id):
        return self.get_messages(session_id)
