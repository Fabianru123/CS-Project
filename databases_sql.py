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


#==================================================
# Add demo data for the "student" account (ChatGPT)
#==================================================

def add_demo_data_if_empty(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if the user already has data.
    cursor.execute("""
        SELECT COUNT(*)
        FROM input
        WHERE user_id = ?
    """, (user_id,))

    count = cursor.fetchone()[0]

    # Add demo data only if there is no data yet.
    if count == 0:

        demo_inputs = [

            (user_id, 4, 5, 3, 4, 5, 4, 5, 2, 4, 3, 4, 5, 4, 82),
            (user_id, 5, 4, 4, 5, 4, 5, 4, 2, 5, 4, 5, 4, 5, 88),
            (user_id, 3, 4, 2, 3, 4, 3, 4, 3, 3, 2, 3, 4, 3, 71)

        ]

        cursor.executemany("""

            INSERT INTO input (
                user_id,
                pschlaf,
                plernzeit,
                pstress,
                pbild,
                pgesund,
                philfe,
                ppausen,
                pfail,
                pfreetime,
                pgoout,
                ppendel,
                pfood,
                psport,
                score
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, demo_inputs)

    conn.commit()
    conn.close()
