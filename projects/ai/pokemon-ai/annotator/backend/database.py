import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "dataset.db"
DATA_DIR = PROJECT_ROOT / "data"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            system_prompt TEXT NOT NULL DEFAULT '',
            instruction TEXT NOT NULL DEFAULT '',
            label TEXT NOT NULL DEFAULT '',
            task_type TEXT NOT NULL DEFAULT '',
            bounding_boxes TEXT NOT NULL DEFAULT '[]',
            reviewed INTEGER NOT NULL DEFAULT 0,
            validation_set INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS annotations_updated_at
        AFTER UPDATE ON annotations
        BEGIN
            UPDATE annotations SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = NEW.id;
        END
    """)
    conn.commit()
    conn.close()
