from db.db import get_connection
import sqlite3

def get_conn():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

def list_evenements():
    """Liste tous les événements pour lesquels il existe des inventaires buvette."""
    conn = get_conn()
    rows = conn.execute("SELECT id, name, date FROM events ORDER BY date DESC").fetchall()
    conn.close()
    return rows

def get_inventaire_par_evenement(event_id, typ):
    """
    Récupère l'inventaire 'avant' ou 'après' pour un événement.
    typ = 'avant' ou 'apres'
    """
    conn = get_conn()
    inv = conn.execute("""
        SELECT * FROM buvette_inventaires
        WHERE event_id=? AND type_inventaire=?
        ORDER BY date_inventaire ASC
        LIMIT 1
    """, (event_id, typ)).fetchone()
    conn.close()
    return inv

def get_lignes_inventaire(inv_id):
    """
    Récupère les lignes d'inventaire (avec info article) pour un inventaire donné.
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, a.name as article_name, a.categorie, a.unite
        FROM buvette_inventaire_lignes l
        LEFT JOIN buvette_articles a ON l.article_id = a.id
        WHERE l.inventaire_id=?
        ORDER BY a.name
    """, (inv_id,)).fetchall()
    conn.close()
    return rows

def get_prix_moyen_achat(article_id, jusqua_date=None):
    """
    Calcule le prix moyen pondéré d'achat d'un article jusqu'à une date donnée.
    """
    conn = get_conn()
    q = "SELECT SUM(quantite*prix_unitaire) as total, SUM(quantite) as qte FROM buvette_achats WHERE article_id=?"
    params = [article_id]
    if jusqua_date:
        q += " AND date_achat<=?"
        params.append(jusqua_date)
    row = conn.execute(q, params).fetchone()
    conn.close()
    if row and row["qte"]:
        return row["total"]/row["qte"]
    return 0.0

def get_recette_buvette(event_id):
    """
    Récupère la somme totale des recettes buvette pour un événement.
    """
    conn = get_conn()
    row = conn.execute("""
        SELECT SUM(montant) as recette
        FROM buvette_recettes
        WHERE event_id=?
    """, (event_id,)).fetchone()
    conn.close()
    return row["recette"] or 0.0