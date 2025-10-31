"""
Module de gestion de la base de données SQLite pour l'application.

MODIFICATIONS APPLIQUÉES (PR copilot/auto-fix-buvette):
- Ajout de la colonne 'stock' (INTEGER DEFAULT 0) au schéma buvette_articles
  pour suivre les quantités en stock de chaque article.
- Migration non destructive dans upgrade_db_structure() pour ajouter la colonne
  'stock' aux bases de données existantes sans perte de données.
- Ajout de la colonne 'commentaire' à buvette_inventaire_lignes si absente.
"""

import sqlite3
import os
import pandas as pd
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

DB_FILE = "association.db"
_db_file = DB_FILE  # Pour gestion dynamique du fichier DB

logger = get_logger("db")

def set_db_file(path):
    """Change dynamiquement le fichier DB à utiliser."""
    global _db_file
    _db_file = path
    logger.info(f"Database file set to: {_db_file}")

def get_db_file():
    return _db_file

def get_connection():
    """Renvoie une connexion SQLite prête à l’emploi, journal_mode=WAL, gestion des erreurs."""
    try:
        conn = sqlite3.connect(_db_file, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except Exception as pragma_exc:
            logger.warning(f"Impossible de définir WAL: {pragma_exc}")
        return conn
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base: {e}")
        raise

def drop_tables(conn):
    """Supprime toutes les tables principales du projet (action irréversible)."""
    tables = [
        "config", "comptes", "membres", "events", "stock", "categories",
        "dons_subventions", "depenses_regulieres", "depenses_diverses",
        "inventaires", "inventaire_lignes", "mouvements_stock", "event_modules",
        "event_module_fields", "event_module_data", "event_payments",
        "event_caisses", "event_caisse_details", "event_recettes",
        "event_depenses", "fournisseurs", "colonnes_modeles",
        "valeurs_modeles_colonnes", "depots_retraits_banque",
        "historique_clotures", "retrocessions_ecoles",
        "buvette_articles", "buvette_achats", "buvette_inventaires",
        "buvette_inventaire_lignes", "buvette_mouvements", "buvette_recettes"
    ]
    cur = conn.cursor()
    for table in tables:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table};")
            logger.debug(f"Table '{table}' supprimée.")
        except Exception as e:
            logger.warning(f"Impossible de supprimer {table}: {e}")
    conn.commit()

def upgrade_db_structure():
    """Migration douce : assure la présence de toutes les colonnes/tables attendues sans perte de données."""
    from tkinter import messagebox
    try:
        conn = get_connection()
        c = conn.cursor()

        # Table comptes
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comptes'")
        if not c.fetchone():
            c.execute("""
                CREATE TABLE IF NOT EXISTS comptes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    solde REAL DEFAULT 0
                )
            """)
        c.execute("SELECT COUNT(*) as n FROM comptes")
        if c.fetchone()["n"] == 0:
            c.execute("SELECT solde_report FROM config ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            if row and row["solde_report"] is not None:
                c.execute("INSERT INTO comptes (name, solde) VALUES (?, ?)", ("Banque Principale", row["solde_report"]))
                conn.commit()

        def add_column_if_not_exists(table, column, definition):
            try:
                c.execute(f"PRAGMA table_info({table});")
                cols = [r[1] for r in c.fetchall()]
                if column not in cols:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition};")
                    logger.info(f"Ajout colonne '{column}' à la table '{table}'.")
            except Exception as e:
                logger.warning(f"Impossible d'ajouter la colonne {column} à {table}: {e}")

        for col, typ in [("cotisation", "TEXT"), ("commentaire", "TEXT"), ("statut", "TEXT"), ("date_adhesion", "TEXT")]:
            add_column_if_not_exists("membres", col, typ)
        for col, typ in [("cloture", "INTEGER DEFAULT 0"), ("solde_report", "REAL DEFAULT 0"), ("but_asso", "TEXT DEFAULT ''")]:
            add_column_if_not_exists("config", col, typ)
        add_column_if_not_exists("event_modules", "id_col_total", "INTEGER")
        for col, typ in [("prix_unitaire", "REAL"), ("modele_colonne", "TEXT")]:
            add_column_if_not_exists("event_module_fields", col, typ)

        advanced_cols = [
            ("fournisseur", "TEXT"), ("date_depense", "TEXT"), ("paye_par", "TEXT"),
            ("membre_id", "INTEGER"), ("statut_remboursement", "TEXT"),
            ("statut_reglement", "TEXT"), ("moyen_paiement", "TEXT"),
            ("numero_cheque", "TEXT"), ("numero_facture", "TEXT")
        ]
        for col, typ in advanced_cols:
            add_column_if_not_exists("event_depenses", col, typ)
        dep_cols = [
            ("categorie", "TEXT"), ("module_id", "INTEGER"), ("montant", "REAL"), ("fournisseur", "TEXT"),
            ("date_depense", "TEXT"), ("paye_par", "TEXT"), ("membre_id", "INTEGER"), ("statut_remboursement", "TEXT"),
            ("statut_reglement", "TEXT"), ("moyen_paiement", "TEXT"), ("numero_cheque", "TEXT"),
            ("numero_facture", "TEXT"), ("commentaire", "TEXT"),
        ]
        for t in ["depenses_regulieres", "depenses_diverses"]:
            for col, typ in dep_cols:
                add_column_if_not_exists(t, col, typ)

        # Migration non destructive : ajouter la colonne 'stock' à buvette_articles si elle n'existe pas
        add_column_if_not_exists("buvette_articles", "stock", "INTEGER DEFAULT 0")
        
        # Ajouter la colonne 'commentaire' à buvette_inventaire_lignes si elle n'existe pas
        add_column_if_not_exists("buvette_inventaire_lignes", "commentaire", "TEXT")

        def create_table_if_not_exists(name, sql):
            try:
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
                if not c.fetchone():
                    c.execute(sql)
                    logger.info(f"Table '{name}' créée.")
            except Exception as e:
                logger.warning(f"Impossible de créer la table {name}: {e}")

        create_table_if_not_exists("retrocessions_ecoles", """
            CREATE TABLE IF NOT EXISTS retrocessions_ecoles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                montant REAL,
                ecole TEXT,
                commentaire TEXT
            )
        """)
        create_table_if_not_exists("fournisseurs", """
            CREATE TABLE IF NOT EXISTS fournisseurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        create_table_if_not_exists("colonnes_modeles", """
            CREATE TABLE IF NOT EXISTS colonnes_modeles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type_modele TEXT NOT NULL
            )
        """)
        create_table_if_not_exists("valeurs_modeles_colonnes", """
            CREATE TABLE IF NOT EXISTS valeurs_modeles_colonnes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modele_id INTEGER,
                valeur TEXT NOT NULL,
                FOREIGN KEY (modele_id) REFERENCES colonnes_modeles(id)
            )
        """)
        create_table_if_not_exists("depots_retraits_banque", """
            CREATE TABLE IF NOT EXISTS depots_retraits_banque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                montant REAL NOT NULL,
                reference TEXT,
                banque TEXT,
                pointe INTEGER DEFAULT 0,
                commentaire TEXT
            )
        """)
        create_table_if_not_exists("historique_clotures", """
            CREATE TABLE IF NOT EXISTS historique_clotures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_cloture TEXT NOT NULL
            )
        """)
        create_table_if_not_exists("buvette_articles", """
            CREATE TABLE IF NOT EXISTS buvette_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie TEXT,
                unite TEXT,
                contenance TEXT,
                commentaire TEXT,
                stock INTEGER DEFAULT 0
            )
        """)
        create_table_if_not_exists("buvette_achats", """
            CREATE TABLE IF NOT EXISTS buvette_achats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                date_achat DATE,
                quantite INTEGER,
                prix_unitaire REAL,
                fournisseur TEXT,
                facture TEXT,
                exercice TEXT,
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id)
            )
        """)
        create_table_if_not_exists("buvette_inventaires", """
            CREATE TABLE IF NOT EXISTS buvette_inventaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_inventaire DATE,
                event_id INTEGER,
                type_inventaire TEXT CHECK(type_inventaire IN ('avant', 'apres', 'hors_evenement')),
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        create_table_if_not_exists("buvette_inventaire_lignes", """
            CREATE TABLE IF NOT EXISTS buvette_inventaire_lignes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventaire_id INTEGER,
                article_id INTEGER,
                quantite INTEGER,
                FOREIGN KEY (inventaire_id) REFERENCES buvette_inventaires(id),
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id)
            )
        """)
        create_table_if_not_exists("buvette_mouvements", """
            CREATE TABLE IF NOT EXISTS buvette_mouvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                date_mouvement DATE,
                type_mouvement TEXT,
                quantite INTEGER,
                motif TEXT,
                event_id INTEGER,
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id),
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        create_table_if_not_exists("buvette_recettes", """
            CREATE TABLE IF NOT EXISTS buvette_recettes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                montant REAL,
                date_recette DATE,
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)

        conn.commit()
        conn.close()
        messagebox.showinfo("Base de données", "La structure de la base a été mise à jour avec succès.")
        logger.info("Structure de la base migrée.")
    except Exception as e:
        handle_exception(e, "Erreur lors de la migration de la base")
        from tkinter import messagebox
        messagebox.showerror("Erreur base", f"Erreur lors de la migration: {e}")

def init_db():
    """Crée toutes les tables du projet si elles sont absentes (pour une base vierge)."""
    try:
        conn = get_connection()
        c = conn.cursor()
        # Schéma complet : Toutes les tables du projet
        c.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercice TEXT,
                date TEXT,
                date_fin TEXT,
                disponible_banque REAL,
                cloture INTEGER DEFAULT 0,
                solde_report REAL DEFAULT 0,
                but_asso TEXT DEFAULT ''
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS comptes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                solde REAL DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS retrocessions_ecoles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                montant REAL,
                ecole TEXT,
                commentaire TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                UNIQUE(name),
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS membres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT,
                telephone TEXT,
                cotisation TEXT,
                commentaire TEXT,
                statut TEXT,
                date_adhesion TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT,
                lieu TEXT,
                description TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie_id INTEGER,
                quantite INTEGER,
                seuil_alerte INTEGER,
                date_peremption TEXT,
                lot TEXT,
                commentaire TEXT,
                FOREIGN KEY (categorie_id) REFERENCES categories(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS dons_subventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                source TEXT,
                montant REAL,
                type TEXT,
                justificatif TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS depenses_regulieres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie TEXT,
                module_id INTEGER,
                montant REAL,
                fournisseur TEXT,
                date_depense TEXT,
                paye_par TEXT,
                membre_id INTEGER,
                statut_remboursement TEXT,
                statut_reglement TEXT,
                moyen_paiement TEXT,
                numero_cheque TEXT,
                numero_facture TEXT,
                commentaire TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS depenses_diverses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie TEXT,
                module_id INTEGER,
                montant REAL,
                fournisseur TEXT,
                date_depense TEXT,
                paye_par TEXT,
                membre_id INTEGER,
                statut_remboursement TEXT,
                statut_reglement TEXT,
                moyen_paiement TEXT,
                numero_cheque TEXT,
                numero_facture TEXT,
                commentaire TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS inventaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_inventaire TEXT NOT NULL,
                event_id INTEGER,
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS inventaire_lignes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventaire_id INTEGER NOT NULL,
                stock_id INTEGER NOT NULL,
                quantite_constatee INTEGER NOT NULL,
                FOREIGN KEY (inventaire_id) REFERENCES inventaires(id),
                FOREIGN KEY (stock_id) REFERENCES stock(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS mouvements_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER,
                date TEXT,
                type TEXT,
                quantite INTEGER,
                prix_achat_total REAL,
                prix_unitaire REAL,
                date_peremption TEXT,
                commentaire TEXT,
                FOREIGN KEY(stock_id) REFERENCES stock(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                nom_module TEXT,
                id_col_total INTEGER,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_module_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                nom_champ TEXT,
                type_champ TEXT,
                prix_unitaire REAL,
                modele_colonne TEXT,
                FOREIGN KEY (module_id) REFERENCES event_modules(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS colonnes_modeles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type_modele TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS valeurs_modeles_colonnes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modele_id INTEGER,
                valeur TEXT NOT NULL,
                FOREIGN KEY (modele_id) REFERENCES colonnes_modeles(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_module_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                row_index INTEGER,
                field_id INTEGER,
                valeur TEXT,
                FOREIGN KEY (module_id) REFERENCES event_modules(id),
                FOREIGN KEY (field_id) REFERENCES event_module_fields(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                nom_payeuse TEXT,
                classe TEXT,
                mode_paiement TEXT,
                banque TEXT,
                numero_cheque TEXT,
                montant REAL,
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_caisses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                nom_caisse TEXT,
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_caisse_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caisse_id INTEGER,
                moment TEXT,
                type TEXT,
                valeur REAL,
                quantite INTEGER,
                FOREIGN KEY (caisse_id) REFERENCES event_caisses(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_recettes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                source TEXT,
                montant REAL,
                commentaire TEXT,
                module_id INTEGER,
                FOREIGN KEY (event_id) REFERENCES events(id),
                FOREIGN KEY (module_id) REFERENCES event_modules(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_depenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                categorie TEXT,
                montant REAL,
                commentaire TEXT,
                module_id INTEGER,
                fournisseur TEXT,
                date_depense TEXT,
                paye_par TEXT,
                membre_id INTEGER,
                statut_remboursement TEXT,
                statut_reglement TEXT,
                moyen_paiement TEXT,
                numero_cheque TEXT,
                numero_facture TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id),
                FOREIGN KEY (module_id) REFERENCES event_modules(id),
                FOREIGN KEY (membre_id) REFERENCES membres(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS fournisseurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS depots_retraits_banque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                montant REAL NOT NULL,
                reference TEXT,
                banque TEXT,
                pointe INTEGER DEFAULT 0,
                commentaire TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS historique_clotures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_cloture TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS buvette_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie TEXT,
                unite TEXT,
                contenance TEXT,
                commentaire TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS buvette_achats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                date_achat DATE,
                quantite INTEGER,
                prix_unitaire REAL,
                fournisseur TEXT,
                facture TEXT,
                exercice TEXT,
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS buvette_inventaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_inventaire DATE,
                event_id INTEGER,
                type_inventaire TEXT CHECK(type_inventaire IN ('avant', 'apres', 'hors_evenement')),
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS buvette_inventaire_lignes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventaire_id INTEGER,
                article_id INTEGER,
                quantite INTEGER,
                FOREIGN KEY (inventaire_id) REFERENCES buvette_inventaires(id),
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS buvette_mouvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                date_mouvement DATE,
                type_mouvement TEXT,
                quantite INTEGER,
                motif TEXT,
                event_id INTEGER,
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id),
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS buvette_recettes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                montant REAL,
                date_recette DATE,
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        c.execute("DROP TABLE IF EXISTS members;")
        conn.commit()
        conn.close()
        logger.info("Tables créées/mises à jour.")
    except Exception as e:
        handle_exception(e, "Erreur lors de l'initialisation de la base")

def is_first_launch():
    """Retourne True si la table config est vide (premier lancement)."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM config")
        res = c.fetchone()
        conn.close()
        return res[0] == 0
    except Exception as e:
        handle_exception(e, "Erreur lors du test de premier lancement")
        return False

def save_init_info(exercice, date, date_fin, disponible_banque):
    """Enregistre les infos d’initialisation d’un nouvel exercice."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO config (exercice, date, date_fin, disponible_banque) VALUES (?, ?, ?, ?)",
            (exercice, date, date_fin, disponible_banque)
        )
        conn.commit()
        c.execute("SELECT solde_report FROM config ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if row and row["solde_report"] is not None:
            c.execute("INSERT OR IGNORE INTO comptes (name, solde) VALUES (?, ?)", ("Banque Principale", row["solde_report"]))
        conn.commit()
        conn.close()
        logger.info(f"Initialisation exercice {exercice} enregistrée.")
    except Exception as e:
        handle_exception(e, "Erreur lors de l'enregistrement de l'initialisation")

def get_df_or_sql(table_or_query):
    """Retourne un DataFrame pandas depuis une table ou une requête SQL."""
    conn = None
    try:
        conn = get_connection()
        # Si c'est une requête SELECT, exécute directement
        if "select" in table_or_query.lower():
            df = pd.read_sql_query(table_or_query, conn)
        else:
            # Vérifie que la table existe
            tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")]
            if table_or_query not in tables:
                raise Exception(f"La table '{table_or_query}' n'existe pas dans la base.")
            df = pd.read_sql_query(f"SELECT * FROM {table_or_query}", conn)
        return df
    except Exception as e:
        handle_exception(e, f"Erreur lors de la récupération des données via pandas/sql (table ou requête: {table_or_query})")
        return pd.DataFrame()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    init_db()