"""
Module de gestion de la base de données pour le module Buvette.

MODIFICATIONS APPLIQUÉES (PR corrections buvette - copilot/auto-fix-buvette):
- Harmonisation des noms de colonnes pour buvette_mouvements:
  * INSERT et UPDATE utilisent maintenant date_mouvement, type_mouvement, motif
    (au lieu de date, type, commentaire) pour correspondre au schéma DB
  * Les SELECT ajoutent des alias (AS date, AS type, AS commentaire) pour
    maintenir la compatibilité avec le code UI existant

- Ajout de la gestion du stock (PR copilot/auto-fix-buvette):
  * Fonction ensure_stock_column(): migration non destructive pour ajouter la colonne 'stock'
  * Fonction set_article_stock(article_id, stock): mise à jour du stock d'un article
  * Fonction get_article_stock(article_id): récupération du stock actuel d'un article
  * Ces fonctions permettent de suivre les quantités en stock après chaque inventaire
"""

from db.db import get_connection
import sqlite3

def get_conn():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

# ----- ARTICLES -----
def list_articles():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM buvette_articles ORDER BY name").fetchall()
    conn.close()
    return rows

def get_article_by_id(article_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM buvette_articles WHERE id=?", (article_id,)).fetchone()
    conn.close()
    return row

def insert_article(name, categorie, unite, commentaire, contenance, purchase_price=None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buvette_articles (name, categorie, unite, commentaire, contenance, purchase_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, categorie, unite, commentaire, contenance, purchase_price))
    conn.commit()
    conn.close()

def update_article(article_id, name, categorie, unite, commentaire, contenance, purchase_price=None):
    conn = get_conn()
    conn.execute("""
        UPDATE buvette_articles SET name=?, categorie=?, unite=?, commentaire=?, contenance=?, purchase_price=?
        WHERE id=?
    """, (name, categorie, unite, commentaire, contenance, purchase_price, article_id))
    conn.commit()
    conn.close()

def delete_article(article_id):
    conn = get_conn()
    conn.execute("DELETE FROM buvette_articles WHERE id=?", (article_id,))
    conn.commit()
    conn.close()

# ----- ACHATS -----
def list_achats():
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.*, ar.name AS article_name, ar.contenance AS article_contenance
        FROM buvette_achats a
        LEFT JOIN buvette_articles ar ON a.article_id = ar.id
        ORDER BY a.date_achat DESC
    """).fetchall()
    conn.close()
    return rows

def get_achat_by_id(achat_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT a.*, ar.name AS article_name, ar.contenance AS article_contenance
        FROM buvette_achats a
        LEFT JOIN buvette_articles ar ON a.article_id = ar.id
        WHERE a.id=?
    """, (achat_id,)).fetchone()
    conn.close()
    return row

def insert_achat(article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buvette_achats (article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice))
    conn.commit()
    conn.close()

def update_achat(achat_id, article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice):
    conn = get_conn()
    conn.execute("""
        UPDATE buvette_achats SET article_id=?, date_achat=?, quantite=?, prix_unitaire=?,
            fournisseur=?, facture=?, exercice=?
        WHERE id=?
    """, (article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice, achat_id))
    conn.commit()
    conn.close()

def delete_achat(achat_id):
    conn = get_conn()
    conn.execute("DELETE FROM buvette_achats WHERE id=?", (achat_id,))
    conn.commit()
    conn.close()

# ----- MOUVEMENTS -----
def list_mouvements():
    conn = get_conn()
    rows = conn.execute("""
        SELECT m.*, 
               m.date_mouvement AS date, 
               m.type_mouvement AS type,
               m.motif AS commentaire,
               ar.name AS article_name, 
               ar.contenance AS article_contenance
        FROM buvette_mouvements m
        LEFT JOIN buvette_articles ar ON m.article_id = ar.id
        ORDER BY m.date_mouvement DESC
    """).fetchall()
    conn.close()
    return rows

def get_mouvement_by_id(mvt_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT m.*, 
               m.date_mouvement AS date, 
               m.type_mouvement AS type,
               m.motif AS commentaire,
               ar.name AS article_name, 
               ar.contenance AS article_contenance
        FROM buvette_mouvements m
        LEFT JOIN buvette_articles ar ON m.article_id = ar.id
        WHERE m.id=?
    """, (mvt_id,)).fetchone()
    conn.close()
    return row

def insert_mouvement(date_mouvement, article_id, type_mouvement, quantite, motif):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buvette_mouvements (date_mouvement, article_id, type_mouvement, quantite, motif)
        VALUES (?, ?, ?, ?, ?)
    """, (date_mouvement, article_id, type_mouvement, quantite, motif))
    conn.commit()
    conn.close()

def update_mouvement(mvt_id, date_mouvement, article_id, type_mouvement, quantite, motif):
    conn = get_conn()
    conn.execute("""
        UPDATE buvette_mouvements SET date_mouvement=?, article_id=?, type_mouvement=?, quantite=?, motif=?
        WHERE id=?
    """, (date_mouvement, article_id, type_mouvement, quantite, motif, mvt_id))
    conn.commit()
    conn.close()

def delete_mouvement(mvt_id):
    conn = get_conn()
    conn.execute("DELETE FROM buvette_mouvements WHERE id=?", (mvt_id,))
    conn.commit()
    conn.close()

# ----- INVENTAIRE LIGNES -----
def list_lignes_inventaire(inventaire_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, ar.name AS article_name, ar.contenance AS article_contenance
        FROM buvette_inventaire_lignes l
        LEFT JOIN buvette_articles ar ON l.article_id = ar.id
        WHERE l.inventaire_id=?
        ORDER BY l.id
    """, (inventaire_id,)).fetchall()
    conn.close()
    return rows

def insert_ligne_inventaire(inventaire_id, article_id, quantite, commentaire):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buvette_inventaire_lignes (inventaire_id, article_id, quantite, commentaire)
        VALUES (?, ?, ?, ?)
    """, (inventaire_id, article_id, quantite, commentaire))
    conn.commit()
    conn.close()

def update_ligne_inventaire(ligne_id, article_id, quantite, commentaire):
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

# ----- UTILITY -----
def list_articles_names():
    conn = get_conn()
    rows = conn.execute("SELECT id, name, contenance FROM buvette_articles ORDER BY name").fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "contenance": r["contenance"]} for r in rows]

def ensure_stock_column():
    """
    Migration non destructive: Ajoute la colonne 'stock' à buvette_articles si elle n'existe pas.
    Cette fonction doit être appelée au démarrage de l'application ou lors de la mise à jour de la DB.
    """
    conn = get_conn()
    try:
        # Vérifier si la colonne stock existe déjà
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns = [row["name"] for row in cursor.fetchall()]
        
        if "stock" not in columns:
            conn.execute("ALTER TABLE buvette_articles ADD COLUMN stock INTEGER DEFAULT 0")
            conn.commit()
            return True  # Colonne ajoutée
        return False  # Colonne existait déjà
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def set_article_stock(article_id, stock):
    """
    Met à jour le stock d'un article.
    Cette fonction est appelée après l'enregistrement d'un inventaire pour mettre à jour
    le stock de l'article immédiatement.
    
    Args:
        article_id: ID de l'article
        stock: Nouvelle valeur du stock (quantité en unités)
    """
    conn = get_conn()
    try:
        conn.execute("UPDATE buvette_articles SET stock=? WHERE id=?", (stock, article_id))
        conn.commit()
    finally:
        conn.close()

def get_article_stock(article_id):
    """
    Récupère le stock actuel d'un article.
    
    Args:
        article_id: ID de l'article
        
    Returns:
        int: Stock actuel de l'article (0 si la colonne n'existe pas ou si l'article n'existe pas)
    """
    conn = get_conn()
    try:
        # Vérifier si la colonne stock existe
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns = [row["name"] for row in cursor.fetchall()]
        
        if "stock" in columns:
            row = conn.execute("SELECT stock FROM buvette_articles WHERE id=?", (article_id,)).fetchone()
            return row["stock"] if row and row["stock"] is not None else 0
        else:
            return 0
    finally:
        conn.close()