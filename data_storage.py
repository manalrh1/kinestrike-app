# data_storage.py

import sqlite3
from datetime import datetime

DB_FILE = "joueuses.db"

# ======= 1. Initialisation de la base =======
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Table des joueuses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS joueuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            coach_username TEXT NOT NULL,
            date_ajout TEXT NOT NULL
        );
    """)

    # Table des analyses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            joueuse_id INTEGER NOT NULL,
            technique TEXT NOT NULL,
            date_analyse TEXT NOT NULL,
            score_global REAL,
            rapport_pdf_path TEXT,
            video_annotee_path TEXT,
            FOREIGN KEY (joueuse_id) REFERENCES joueuses(id)
        );
    """)

    conn.commit()
    conn.close()

# ======= 2. Ajouter une nouvelle joueuse =======
def ajouter_joueuse(nom, prenom, categorie, coach_username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_ajout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO joueuses (nom, prenom, categorie, coach_username, date_ajout)
        VALUES (?, ?, ?, ?, ?);
    """, (nom, prenom, categorie, coach_username, date_ajout))
    conn.commit()
    conn.close()

# ======= 3. Lister les joueuses d’un coach donné =======
def get_joueuses_par_coach(coach_username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nom, prenom, categorie, date_ajout
        FROM joueuses
        WHERE coach_username = ?
        ORDER BY date_ajout DESC;
    """, (coach_username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ======= 4. Supprimer une joueuse =======
def supprimer_joueuse(joueuse_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM joueuses WHERE id = ?;", (joueuse_id,))
    conn.commit()
    conn.close()

# ======= 5. Enregistrer une analyse =======
def enregistrer_analyse(joueuse_id, technique, score_global, rapport_pdf_path=None, video_annotee_path=None, date_analyse=None):

    if date_analyse is None:
        date_analyse = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analyses (joueuse_id, technique, date_analyse, score_global, rapport_pdf_path, video_annotee_path)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (joueuse_id, technique, date_analyse, score_global, rapport_pdf_path, video_annotee_path))
    conn.commit()
    conn.close()


# ======= 6. Lister les analyses d’une joueuse =======
def get_analyses_par_joueuse(joueuse_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, technique, date_analyse, score_global, rapport_pdf_path, video_annotee_path
        FROM analyses
        WHERE joueuse_id = ?
        ORDER BY date_analyse DESC;
    """, (joueuse_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
def supprimer_analyse(analyse_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?;", (analyse_id,))
    conn.commit()
    conn.close()
def existe_analyse(joueuse_id, technique, date_analyse):
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM analyses
        WHERE joueuse_id = ? AND technique = ? AND date_analyse = ?
    """, (joueuse_id, technique, date_analyse))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
