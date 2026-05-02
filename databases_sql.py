import sqlite3

DB_NAME = "predicted_inputs.db"


# Init DB
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
# Tabelle für Prüfungen (Lernplan)
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

    # Tabelle für gesperrte Zeitfenster (Lernplan)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zeitfenster (
        zeitfenster_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wochentag TEXT NOT NULL,
        von TEXT NOT NULL,
        bis TEXT NOT NULL,
        beschreibung TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    DB.commit()
    DB.close()


# User 
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


# Add Input
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


# get all inputs
def get_inputs():
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()

    cursor.execute("SELECT * FROM input")
    rows = cursor.fetchall()

    DB.close()
    return rows


# get inputs just for one user
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

# Tinas Lernplan-Funktionen

def add_pruefung(user_id, fach, datum, ects):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()
    cursor.execute("""
        INSERT INTO pruefungen (user_id, fach, datum, ects)
        VALUES (?, ?, ?, ?)
    """, (user_id, fach, datum, ects))
    DB.commit()
    DB.close()

def get_pruefungen(user_id):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()
    cursor.execute("SELECT * FROM pruefungen WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    DB.close()
    return rows

def delete_pruefung(pruefung_id):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()
    cursor.execute("DELETE FROM pruefungen WHERE pruefung_id = ?", (pruefung_id,))
    DB.commit()
    DB.close()

def add_zeitfenster(user_id, wochentag, von, bis, beschreibung):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()
    cursor.execute("""
        INSERT INTO zeitfenster (user_id, wochentag, von, bis, beschreibung)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, wochentag, von, bis, beschreibung))
    DB.commit()
    DB.close()

def get_zeitfenster(user_id):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()
    cursor.execute("SELECT * FROM zeitfenster WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    DB.close()
    return rows

def delete_zeitfenster(zeitfenster_id):
    DB = sqlite3.connect(DB_NAME)
    cursor = DB.cursor()
    cursor.execute("DELETE FROM zeitfenster WHERE zeitfenster_id = ?", (zeitfenster_id,))
    DB.commit()
    DB.close()
