"""
database.py – SQLite-Datenbankschicht für PredictEd
Verwaltet die Tabelle "exams" mit allen Prüfungen des Nutzers.
"""

import sqlite3
from pathlib import Path

# Datenbankdatei liegt im selben Verzeichnis wie dieses Skript
DB_PFAD = Path(__file__).parent / "predicted_app.db"


def verbindung_herstellen() -> sqlite3.Connection:
    """Gibt eine Verbindung zur SQLite-Datenbank zurück."""
    verbindung = sqlite3.connect(DB_PFAD)
    # Spaltennamen als Dictionary-Keys zurückgeben
    verbindung.row_factory = sqlite3.Row
    return verbindung


def tabellen_erstellen() -> None:
    """Erstellt alle benötigten Tabellen, falls sie noch nicht existieren."""
    with verbindung_herstellen() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                fach       TEXT    NOT NULL,          -- z. B. "Mathematik"
                datum      TEXT    NOT NULL,          -- ISO-Format: YYYY-MM-DD
                prioritaet TEXT    NOT NULL           -- "Hoch" | "Mittel" | "Tief"
                    CHECK(prioritaet IN ('Hoch', 'Mittel', 'Tief')),
                lernstunden REAL   NOT NULL DEFAULT 0 -- berechnete Gesamtstunden
            )
        """)
        conn.commit()


def pruefung_eintragen(fach: str, datum: str, prioritaet: str, lernstunden: float = 0.0) -> int:
    """
    Fügt eine neue Prüfung in die Datenbank ein.
    Gibt die ID des neuen Eintrags zurück.
    """
    with verbindung_herstellen() as conn:
        cursor = conn.execute(
            "INSERT INTO exams (fach, datum, prioritaet, lernstunden) VALUES (?, ?, ?, ?)",
            (fach, datum, prioritaet, lernstunden),
        )
        conn.commit()
        return cursor.lastrowid


def alle_pruefungen_laden() -> list[dict]:
    """Gibt alle Prüfungen sortiert nach Datum zurück."""
    with verbindung_herstellen() as conn:
        rows = conn.execute(
            "SELECT * FROM exams ORDER BY datum ASC"
        ).fetchall()
        # sqlite3.Row in normale Dictionaries umwandeln
        return [dict(row) for row in rows]


def pruefung_loeschen(pruefung_id: int) -> None:
    """Löscht eine Prüfung anhand ihrer ID."""
    with verbindung_herstellen() as conn:
        conn.execute("DELETE FROM exams WHERE id = ?", (pruefung_id,))
        conn.commit()


def lernstunden_aktualisieren(pruefung_id: int, lernstunden: float) -> None:
    """Aktualisiert die berechneten Lernstunden einer Prüfung."""
    with verbindung_herstellen() as conn:
        conn.execute(
            "UPDATE exams SET lernstunden = ? WHERE id = ?",
            (lernstunden, pruefung_id),
        )
        conn.commit()


# Tabellen beim ersten Import automatisch anlegen
tabellen_erstellen()
