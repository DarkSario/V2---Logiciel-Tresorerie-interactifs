import os
import shutil
import zipfile
from datetime import datetime
from tkinter import messagebox
from utils.app_logger import get_logger
from utils.error_handler import handle_exception
from db.db import get_db_file

logger = get_logger("cloture_exercice")

EXPORTS_DIR = "exports"

def export_all_tables_to_csv(db_file=None, export_dir=None):
    """
    Exporte toutes les tables SQLite en CSV dans un dossier donné.
    """
    import sqlite3
    import pandas as pd

    if not db_file:
        db_file = get_db_file()
    if not export_dir:
        export_dir = os.path.join(EXPORTS_DIR, "cloture_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(export_dir, exist_ok=True)

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            path = os.path.join(export_dir, f"{table}.csv")
            df.to_csv(path, index=False, encoding="utf-8")
        conn.close()
        logger.info(f"Export CSV de toutes les tables terminé dans {export_dir}")
        return export_dir
    except Exception as e:
        handle_exception(e, "Erreur lors de l'export CSV des tables")
        return None

def make_zip_export(src_dir):
    """
    Crée une archive ZIP de tout le dossier src_dir.
    """
    try:
        zip_name = src_dir.rstrip(os.sep) + ".zip"
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(src_dir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, src_dir)
                    zipf.write(abs_path, rel_path)
        logger.info(f"Archive ZIP créée : {zip_name}")
        return zip_name
    except Exception as e:
        handle_exception(e, "Erreur lors de la création de l'archive ZIP")
        return None

def run_cloture(reset_db=True, export_pdf_callback=None):
    """
    Processus complet de clôture d'exercice :
    - Export CSV de toutes les tables
    - Création ZIP
    - (optionnel) Génération du bilan PDF
    - (optionnel) Reset de la base
    """
    try:
        db_file = get_db_file()
        export_dir = export_all_tables_to_csv(db_file)
        if not export_dir:
            messagebox.showerror("Erreur", "Échec de l'export CSV.")
            return
        zip_path = make_zip_export(export_dir)
        if not zip_path:
            messagebox.showerror("Erreur", "Échec de la création de l'archive ZIP.")
            return

        if export_pdf_callback:
            # Fonction passée par le module exports pour générer le PDF bilan argumenté
            try:
                export_pdf_callback(export_dir)
            except Exception as e:
                handle_exception(e, "Erreur lors de l'export du PDF de bilan")

        if reset_db:
            from db.db import drop_tables, init_db, get_connection
            if messagebox.askyesno("Réinitialisation", "Voulez-vous réinitialiser la base pour un nouvel exercice ?\nCette opération est IRRÉVERSIBLE."):
                conn = get_connection()
                drop_tables(conn)
                conn.close()
                init_db()
                messagebox.showinfo("Clôture terminée", "La base a été réinitialisée pour un nouvel exercice.")
        else:
            messagebox.showinfo("Clôture terminée", f"Archive et exports générés dans {export_dir}")

    except Exception as e:
        message = handle_exception(e, "Erreur lors de la clôture d'exercice.")
        messagebox.showerror("Erreur", message)