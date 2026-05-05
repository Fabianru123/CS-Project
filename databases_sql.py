#========================================================================================
# Database Module: Manages SQLite setup, user identification, and storage of user inputs
#========================================================================================

import sqlite3

DB_NAME = "predicted_inputs.db"


#================
# Database Setup
#================

def init_db():
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    # Table users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE NOT NULL
    )
    """)

    # Table input
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


     # Table exam results
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


#=================
# User Management
#=================

# Retrieves an existing user ID or creates a new user if not found
def get_or_create_user(user_name):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (user_name,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        cursor.execute("INSERT INTO users (user_name) VALUES (?)", (user_name,))
        DB.commit()
        user_id = cursor.lastrowid

    DB.close()
    return user_id


#==================
# Input Management
#==================

# Stores a new set of user inputs and the corresponding score.
def add_input(user_id, age, studien, pschlaf, plernzeit, pstress, pbild,
              pgesund, philfe, ppausen, pfail, pfreetime, pgoout,
              ppendel, pfood, psport, score):

    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

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


#================
# Data Retrieval
#================

def get_inputs():
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("SELECT * FROM input")
    rows = cursor.fetchall()

    DB.close()
    return rows


# Returns all stored inputs for a specific user
def get_inputs_by_user(user_id):
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


#=======================
# EXAM RESULT MANAGEMENT
#=======================

def add_exam_result(user_id, exam_name, grade, ects):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("""
        INSERT INTO exam_results (
            user_id, exam_name, grade, ects
        )
        VALUES (?, ?, ?, ?)
    """,
    (user_id, exam_name, grade, ects))

    DB.commit()
    DB.close()

# Returns all stored inputs for a specific user
def get_exam_results_by_user(user_id):
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
