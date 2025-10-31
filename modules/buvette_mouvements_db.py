from db.db import get_connection
import sqlite3

def get_conn():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

# ----- MOUVEMENTS -----
def list_mouvements():
    conn = get_conn()
    rows = conn.execute("""
        SELECT m.*, a.name AS article_name, e.name AS event_name, e.date AS event_date
        FROM buvette_mouvements m
        LEFT JOIN buvette_articles a ON m.article_id = a.id
        LEFT JOIN events e ON m.event_id = e.id
        ORDER BY m.date_mouvement DESC
    """).fetchall()
    conn.close()
    return rows

def get_mouvement_by_id(mvt_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT m.*, a.name AS article_name, e.name AS event_name, e.date AS event_date
        FROM buvette_mouvements m
        LEFT JOIN buvette_articles a ON m.article_id = a.id
        LEFT JOIN events e ON m.event_id = e.id
        WHERE m.id=?
    """, (mvt_id,)).fetchone()
    conn.close()
    return row

def insert_mouvement(article_id, date_mouvement, type_mouvement, quantite, motif, event_id):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buvette_mouvements (article_id, date_mouvement, type_mouvement, quantite, motif, event_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (article_id, date_mouvement, type_mouvement, quantite, motif, event_id))
    conn.commit()
    conn.close()

def update_mouvement(mvt_id, article_id, date_mouvement, type_mouvement, quantite, motif, event_id):
    conn = get_conn()
    conn.execute("""
        UPDATE buvette_mouvements SET article_id=?, date_mouvement=?, type_mouvement=?, quantite=?, motif=?, event_id=?
        WHERE id=?
    """, (article_id, date_mouvement, type_mouvement, quantite, motif, event_id, mvt_id))
    conn.commit()
    conn.close()

def delete_mouvement(mvt_id):
    conn = get_conn()
    conn.execute("DELETE FROM buvette_mouvements WHERE id=?", (mvt_id,))
    conn.commit()
    conn.close()

# ----- UTILITY -----
def list_articles():
    conn = get_conn()
    rows = conn.execute("SELECT id, name FROM buvette_articles ORDER BY name").fetchall()
    conn.close()
    return rows

def list_events():
    conn = get_conn()
    rows = conn.execute("SELECT id, name FROM events ORDER BY date DESC").fetchall()
    conn.close()
    return rows