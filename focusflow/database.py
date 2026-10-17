import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "focusflow.db"

class Database:
    def __init__(self, path=DB_PATH):
        self.path = str(path)
        self.initialize()

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def initialize(self):
        with self.connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Study', priority TEXT NOT NULL DEFAULT 'Medium',
                due_date TEXT DEFAULT '', completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS notes(
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                content TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS focus_sessions(
                id INTEGER PRIMARY KEY AUTOINCREMENT, minutes INTEGER NOT NULL,
                completed_at TEXT NOT NULL)""")

    def add_task(self, title, category, priority, due_date):
        with self.connect() as c:
            c.execute("INSERT INTO tasks(title,category,priority,due_date,created_at) VALUES(?,?,?,?,?)",
                      (title, category, priority, due_date, datetime.now().isoformat(timespec="seconds")))

    def tasks(self, search="", status="All"):
        q = "SELECT * FROM tasks WHERE title LIKE ?"
        args = [f"%{search}%"]
        if status == "Active": q += " AND completed=0"
        elif status == "Completed": q += " AND completed=1"
        q += " ORDER BY completed ASC, CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, id DESC"
        with self.connect() as c:
            return c.execute(q, args).fetchall()

    def toggle_task(self, task_id):
        with self.connect() as c:
            c.execute("UPDATE tasks SET completed=1-completed WHERE id=?", (task_id,))

    def delete_task(self, task_id):
        with self.connect() as c:
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def task_stats(self):
        with self.connect() as c:
            r = c.execute("""SELECT COUNT(*) total,
              SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) done,
              SUM(CASE WHEN completed=0 THEN 1 ELSE 0 END) active FROM tasks""").fetchone()
            return {"total": r["total"] or 0, "done": r["done"] or 0, "active": r["active"] or 0}

    def save_note(self, title, content, note_id=None):
        with self.connect() as c:
            if note_id:
                c.execute("UPDATE notes SET title=?,content=?,updated_at=? WHERE id=?",
                          (title, content, datetime.now().isoformat(timespec="seconds"), note_id))
            else:
                c.execute("INSERT INTO notes(title,content,updated_at) VALUES(?,?,?)",
                          (title, content, datetime.now().isoformat(timespec="seconds")))

    def notes(self, search=""):
        with self.connect() as c:
            return c.execute("SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC",
                             (f"%{search}%", f"%{search}%")).fetchall()

    def delete_note(self, note_id):
        with self.connect() as c:
            c.execute("DELETE FROM notes WHERE id=?", (note_id,))

    def add_focus_session(self, minutes):
        with self.connect() as c:
            c.execute("INSERT INTO focus_sessions(minutes,completed_at) VALUES(?,?)",
                      (minutes, datetime.now().isoformat(timespec="seconds")))

    def focus_stats(self):
        with self.connect() as c:
            r = c.execute("SELECT COUNT(*) sessions, COALESCE(SUM(minutes),0) minutes FROM focus_sessions").fetchone()
            return {"sessions": r["sessions"], "minutes": r["minutes"]}
