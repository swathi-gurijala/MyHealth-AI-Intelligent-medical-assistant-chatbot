import sqlite3
from pathlib import Path
from typing import List

from .models import HistoryEntry

DB_PATH = Path(__file__).resolve().parent.parent / "myhealth.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            summary TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


def add_history(user_id: str, timestamp: str, interaction_type: str, summary: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO history (user_id, timestamp, interaction_type, summary) VALUES (?, ?, ?, ?)",
        (user_id, timestamp, interaction_type, summary),
    )
    conn.commit()
    conn.close()


def get_history(user_id: str) -> List[HistoryEntry]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT timestamp, interaction_type, summary FROM history WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    return [
        HistoryEntry(timestamp=row[0], interaction_type=row[1], summary=row[2])
        for row in rows
    ]
