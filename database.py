"""
database.py – SQLite-Datenbankschicht für PredictEd
Verwaltet die Tabelle "exams" mit allen Prüfungen des Nutzers.
"""

import sqlite3
from pathlib import Path

DB_PFAD = Path(__file__).parent / "predicted_app.db"


def verbindung_herstellen() -> sqlite3.Connection:
    verbindung = sqlite3.connect(DB_PFAD)
    verbindung.row_factory = sqlite3.Row
    return verbindung


def tabellen_erstellen() -> None:
    with verbindung_herstellen() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                fach       TEXT    NOT NULL,
                datum      TEXT    NOT NULL,
                prioritaet TEXT    NOT NULL
                    CHECK(prioritaet IN ('Hoch', 'Mittel', 'Tief')),
                lernstunden REAL   NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def pruefung_eintragen(fach: str, datum: str, prioritaet: str, lernstunden: float = 0.0) -> int:
    with verbindung_herstellen() as conn:
        cursor = conn.execute(
            "INSERT INTO exams (fach, datum, prioritaet, lernstunden) VALUES (?, ?, ?, ?)",
            (fach, datum, prioritaet, lernstunden),
        )
        conn.commit()
        return cursor.lastrowid


def alle_pruefungen_laden() -> list[dict]:
    with verbindung_herstellen() as conn:
        rows = conn.execute("SELECT * FROM exams ORDER BY datum ASC").fetchall()
        return [dict(row) for row in rows]


def pruefung_loeschen(pruefung_id: int) -> None:
    with verbindung_herstellen() as conn:
        conn.execute("DELETE FROM exams WHERE id = ?", (pruefung_id,))
        conn.commit()


def lernstunden_aktualisieren(pruefung_id: int, lernstunden: float) -> None:
    with verbindung_herstellen() as conn:
        conn.execute(
            "UPDATE exams SET lernstunden = ? WHERE id = ?",
            (lernstunden, pruefung_id),
        )
        conn.commit()


tabellen_erstellen()
