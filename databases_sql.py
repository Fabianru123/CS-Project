# =============================================================================
# Database Module
# Handles SQLite database setup, user management, input storage, exam results,
# and study plan exams.
# =============================================================================

import sqlite3

DB_NAME = "predicted_inputs.db"


# =============================================================================
# Database Setup
# =============================================================================

def init_db():
    """Creates the required database tables if they do not already exist."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Create the users table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE NOT NULL
    )
    """)

    # Create the input table for storing user questionnaire results.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS input (
        input_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        age INTEGER,
        studien TEXT,
        pschlaf INTEGER,
        plernzeit INTEGER,
        pstress INTEGER,
        pbild INTEGER,
        pgesund INTEGER,
        philfe INTEGER,
        ppausen INTEGER,
        pfail INTEGER,
        pfreetime INTEGER,
        pgoout INTEGER,
        ppendel INTEGER,
        pfood INTEGER,
        psport INTEGER,
        score REAL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # Create the exam results table.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_results (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exam_name TEXT, 
    grade REAL,
    ects REAL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    
    """)

    DB.commit()
    DB.close()


# =============================================================================
# User Management
# =============================================================================

def get_or_create_user(user_name):
    """Returns an existing user ID or creates a new user."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Check whether the user already exists.
    cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (user_name,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        # Add a new user and store the generated ID.
        cursor.execute("INSERT INTO users (user_name) VALUES (?)", (user_name,))
        DB.commit()
        user_id = cursor.lastrowid

    DB.close()
    return user_id


# =============================================================================
# Input Management
# =============================================================================

def add_input(user_id, age, studien, pschlaf, plernzeit, pstress, pbild,
              pgesund, philfe, ppausen, pfail, pfreetime, pgoout,
              ppendel, pfood, psport, score):
    """Stores a new set of user inputs and the corresponding score."""

    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Insert the questionnaire results into the input table.
    cursor.execute("""
        INSERT INTO input (
            user_id, age, studien, pschlaf, plernzeit, pstress, pbild,
            pgesund, philfe, ppausen, pfail, pfreetime, pgoout,
            ppendel, pfood, psport, score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (user_id, age, studien, pschlaf, plernzeit, pstress, pbild,
        pgesund, philfe, ppausen, pfail, pfreetime, pgoout,
        ppendel, pfood, psport, score))

    DB.commit()
    DB.close()


# =============================================================================
# Data Retrieval
# =============================================================================

def get_inputs():
    """Returns all stored user inputs."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("SELECT * FROM input")
    rows = cursor.fetchall()

    DB.close()
    return rows


def get_inputs_by_user(user_id):
    """Returns all stored inputs for a specific user."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("""
        SELECT *
        FROM input
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()

    DB.close()
    return rows


# =============================================================================
# Exam Result Management
# =============================================================================

def add_exam_result(user_id, exam_name, grade, ects):
    """Stores a new exam result for a specific user."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Insert the exam result into the exam_results table.
    cursor.execute("""
        INSERT INTO exam_results (
            user_id, exam_name, grade, ects
        )
        VALUES (?, ?, ?, ?)
    """,
    (user_id, exam_name, grade, ects))

    DB.commit()
    DB.close()


def get_exam_results_by_user(user_id):
    """Returns all exam results for a specific user."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("""
        SELECT *
        FROM exam_results
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()

    DB.close()
    return rows


def delete_exam_result(exam_id):
    """Deletes an exam result from the database by its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM exam_results
        WHERE exam_id = ?
    """, (exam_id,))

    conn.commit()
    conn.close()


# =============================================================================
# Study Plan: Exams
# =============================================================================

def add_pruefung(user_id, fach, datum, ects):
    """Adds a new exam for a user to the database."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Create the study plan exams table if it does not exist yet.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pruefungen (
            pruefung_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fach TEXT NOT NULL,
            datum TEXT NOT NULL,
            ects INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Insert the new exam into the study plan table.
    cursor.execute("""
        INSERT INTO pruefungen (user_id, fach, datum, ects)
        VALUES (?, ?, ?, ?)
    """, (user_id, fach, datum, ects))

    DB.commit()
    DB.close()


def get_pruefungen(user_id):
    """Returns all exams for a specific user."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Ensure that the study plan exams table exists before reading from it.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pruefungen (
            pruefung_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fach TEXT NOT NULL,
            datum TEXT NOT NULL,
            ects INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("SELECT * FROM pruefungen WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()

    DB.close()
    return rows


def delete_pruefung(pruefung_id):
    """Deletes an exam from the database by its ID."""
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("DELETE FROM pruefungen WHERE pruefung_id = ?", (pruefung_id,))

    DB.commit()
    DB.close()


#========================================================
# Complete demo data for the "student" account (ChatGPT)
#========================================================

def add_demo_data_if_empty(user_id):
    """Adds complete demo data for the demo user 'student'."""

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Make sure the study plan table exists.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pruefungen (
            pruefung_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fach TEXT NOT NULL,
            datum TEXT NOT NULL,
            ects INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Remove old demo data to avoid wrong/duplicated values.
    cursor.execute("DELETE FROM input WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM exam_results WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM pruefungen WHERE user_id = ?", (user_id,))

    # Demo score history with age, study program and different timestamps.
    demo_inputs = [
        (user_id, "2026-04-20 09:00:00", 21, "BWL", 3, 3, 2, 3, 4, 3, 3, 3, 3, 2, 4, 3, 3, 68),
        (user_id, "2026-04-30 09:00:00", 21, "BWL", 4, 4, 3, 4, 4, 4, 4, 2, 4, 3, 4, 4, 4, 78),
        (user_id, "2026-05-09 09:00:00", 21, "BWL", 5, 4, 4, 4, 5, 4, 5, 2, 5, 3, 5, 4, 5, 88)
    ]

    cursor.executemany("""
        INSERT INTO input (
            user_id, created_at, age, studien,
            pschlaf, plernzeit, pstress, pbild,
            pgesund, philfe, ppausen, pfail,
            pfreetime, pgoout, ppendel, pfood,
            psport, score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_inputs)

    # Demo past exam results for profile page.
    demo_exam_results = [
        (user_id, "2026-03-12 10:00:00", "Mathematik", 5.25, 4.0),
        (user_id, "2026-03-20 10:00:00", "BWL", 5.50, 5.0),
        (user_id, "2026-04-05 10:00:00", "VWL", 5.00, 5.0),
        (user_id, "2026-04-18 10:00:00", "Recht", 5.75, 4.0)
    ]

    cursor.executemany("""
        INSERT INTO exam_results (
            user_id, created_at, exam_name, grade, ects
        )
        VALUES (?, ?, ?, ?, ?)
    """, demo_exam_results)

    # Demo upcoming exams for Lernplan page.
    demo_pruefungen = [
        (user_id, "Corporate Finance", "2026-05-22", 5),
        (user_id, "Marketing", "2026-05-28", 4),
        (user_id, "Operations Management", "2026-06-04", 5),
        (user_id, "Wirtschaftsrecht", "2026-06-12", 4)
    ]

    cursor.executemany("""
        INSERT INTO pruefungen (
            user_id, fach, datum, ects
        )
        VALUES (?, ?, ?, ?)
    """, demo_pruefungen)

    # Add a few other users so the comparison chart is not empty.
    other_users = [
        ("demo_anna", 22, "VWL", 74),
        ("demo_luca", 20, "BWL", 81),
        ("demo_sofia", 23, "International Affairs", 69)
    ]

    for name, age, studien, score in other_users:
        cursor.execute("INSERT OR IGNORE INTO users (user_name) VALUES (?)", (name,))
        cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (name,))
        other_user_id = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM input WHERE user_id = ?", (other_user_id,))
        already_exists = cursor.fetchone()[0]

        if already_exists == 0:
            cursor.execute("""
                INSERT INTO input (
                    user_id, created_at, age, studien,
                    pschlaf, plernzeit, pstress, pbild,
                    pgesund, philfe, ppausen, pfail,
                    pfreetime, pgoout, ppendel, pfood,
                    psport, score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                other_user_id, "2026-05-08 09:00:00", age, studien,
                4, 4, 3, 4, 4, 3, 4, 2, 4, 3, 4, 4, 4, score
            ))

    conn.commit()
    conn.close()
