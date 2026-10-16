"""SQLite connection and table setup for the student records application."""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "students.db")))


def get_connection() -> sqlite3.Connection:
    """Open a database connection that returns rows by column name."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create the students table if it does not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                date_of_birth TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT
            )
            """
        )
