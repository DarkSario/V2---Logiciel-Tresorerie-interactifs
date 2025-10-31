from db.db import get_connection
import sqlite3

def get_conn():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

# ----- INVENTAIRES -----
def list_inventaires():
    conn = get_conn()
    rows = conn.execute("""
        SELECT i.*, e.name as event_name, e.date as event_date
        FROM buvette_inventaires i
        LEFT JOIN events e ON i.event_id = e.id
        ORDER BY date_inventaire DESC
    """).fetchall()
    conn.close()
    return rows

def get_inventaire_by_id(inv_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT i.*, e.name as event_name, e.date as event_date
        FROM buvette_inventaires i
        LEFT JOIN events e ON i.event_id = e.id
        WHERE i.id=?
    """, (inv_id,)).fetchone()
    conn.close()
    return row

def insert_inventaire(date_inventaire, event_id, type_inventaire, commentaire):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
        VALUES (?, ?, ?, ?)
    """, (date_inventaire, event_id, type_inventaire, commentaire))
    inv_id = cur.lastrowid
    conn.commit()
    conn.close()
    return inv_id

def update_inventaire(inv_id, date_inventaire, event_id, type_inventaire, commentaire):
    conn = get_conn()
    conn.execute("""
        UPDATE buvette_inventaires SET date_inventaire=?, event_id=?, type_inventaire=?, commentaire=?
        WHERE id=?
    """, (date_inventaire, event_id, type_inventaire, commentaire, inv_id))
    conn.commit()
    conn.close()

def delete_inventaire(inv_id):
    conn = get_conn()
    conn.execute("DELETE FROM buvette_inventaires WHERE id=?", (inv_id,))
    conn.commit()
    conn.close()

# ----- LIGNES D'INVENTAIRE -----
def list_lignes_inventaire(inventaire_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, a.name as article_name
        FROM buvette_inventaire_lignes l
        LEFT JOIN buvette_articles a ON l.article_id = a.id
        WHERE l.inventaire_id=?
        ORDER BY a.name
    """, (inventaire_id,)).fetchall()
    conn.close()
    return rows

def insert_ligne_inventaire(inventaire_id, article_id, quantite, commentaire=None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buvette_inventaire_lignes (inventaire_id, article_id, quantite, commentaire)
        VALUES (?, ?, ?, ?)
    """, (inventaire_id, article_id, quantite, commentaire))
    conn.commit()
    conn.close()

def update_ligne_inventaire(ligne_id, article_id, quantite, commentaire=None):
    conn = get_conn()
    conn.execute("""
        UPDATE buvette_inventaire_lignes SET article_id=?, quantite=?, commentaire=?
        WHERE id=?
    """, (article_id, quantite, commentaire, ligne_id))
    conn.commit()
    conn.close()

def delete_ligne_inventaire(ligne_id):
    conn = get_conn()
    conn.execute("DELETE FROM buvette_inventaire_lignes WHERE id=?", (ligne_id,))
    conn.commit()
    conn.close()

def upsert_ligne_inventaire(inventaire_id, article_id, quantite, commentaire=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM buvette_inventaire_lignes WHERE inventaire_id=? AND article_id=?
    """, (inventaire_id, article_id))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE buvette_inventaire_lignes SET quantite=?, commentaire=?
            WHERE inventaire_id=? AND article_id=?
        """, (quantite, commentaire, inventaire_id, article_id))
    else:
        cur.execute("""
            INSERT INTO buvette_inventaire_lignes (inventaire_id, article_id, quantite, commentaire)
            VALUES (?, ?, ?, ?)
        """, (inventaire_id, article_id, quantite, commentaire))
    conn.commit()
    conn.close()

# ----- EVENEMENTS UTILITY -----
def list_events():
    conn = get_conn()
    rows = conn.execute("SELECT id, name FROM events ORDER BY date DESC").fetchall()
    conn.close()
    return rows