"""
Script de migration pour la base de données Log-Interactif-treso.
- Permet de mettre à jour ou migrer le schéma de la base SQLite.
- À lancer manuellement en cas de mise à jour de structure.

Usage :
    python scripts/migration.py
"""

import sqlite3
import sys
import os

DB_PATH = os.environ.get("DB_PATH", "./data/database.db")

MIGRATIONS = [
    # Exemple : Ajout d'une colonne 'description' à la table events
    {
        "desc": "Ajout colonne 'description' à events si absente",
        "sql": [
            "ALTER TABLE events ADD COLUMN description TEXT"
        ],
        "check": "PRAGMA table_info(events);",
        "trigger": lambda columns: not any(c[1]=="description" for c in columns)
    },
    # Ajout du prix d'achat unitaire pour les articles de buvette
    {
        "desc": "Ajout colonne 'purchase_price' à buvette_articles si absente",
        "sql": [
            "ALTER TABLE buvette_articles ADD COLUMN purchase_price REAL"
        ],
        "check": "PRAGMA table_info(buvette_articles);",
        "trigger": lambda columns: not any(c[1]=="purchase_price" for c in columns)
    },
    # Ajouter d'autres migrations ici sous forme de dict
    # ...
]

def get_columns(conn, table):
    return conn.execute(f"PRAGMA table_info({table});").fetchall()

def run_migrations(conn):
    for mig in MIGRATIONS:
        print(f"> Vérification : {mig['desc']}")
        check = mig["check"].split("(")[1].split(")")[0]
        columns = get_columns(conn, check)
        if mig["trigger"](columns):
            print(f"  - Migration nécessaire, exécution SQL : {mig['sql'][0]}")
            for sql in mig["sql"]:
                try:
                    conn.execute(sql)
                    print(f"    ✓ {sql}")
                except Exception as e:
                    print(f"    ⚠️  Erreur : {e}")
        else:
            print("  - Déjà à jour, rien à faire.")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Base introuvable : {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    try:
        run_migrations(conn)
        conn.commit()
        print("✅ Migration terminée.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()