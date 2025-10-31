import os
import shutil
from tkinter import filedialog, messagebox
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("backup_restore")

BACKUP_DIR = "backups"
DEFAULT_DB_FILE = "association.db"

def backup_database(db_file=DEFAULT_DB_FILE):
    """Crée une copie de sauvegarde de la base au format .bak dans BACKUP_DIR."""
    try:
        if not os.path.exists(db_file):
            messagebox.showerror("Erreur", f"Base de données non trouvée : {db_file}")
            return
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backup_name = f"{os.path.splitext(os.path.basename(db_file))[0]}_backup.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        shutil.copy2(db_file, backup_path)
        logger.info(f"Backup créé : {backup_path}")
        messagebox.showinfo("Sauvegarde", f"Sauvegarde réussie dans {backup_path}")
    except Exception as e:
        message = handle_exception(e, "Erreur lors de la sauvegarde de la base.")
        messagebox.showerror("Erreur", message)

def restore_database(db_file=DEFAULT_DB_FILE):
    """Permet de restaurer la base à partir d'un fichier .bak choisi par l'utilisateur."""
    try:
        bak_path = filedialog.askopenfilename(
            title="Sélectionnez le fichier de sauvegarde à restaurer",
            filetypes=[("Fichiers de sauvegarde", "*.bak"), ("Tout", "*.*")]
        )
        if not bak_path:
            return
        if os.path.exists(db_file):
            if not messagebox.askyesno("Confirmation", f"Écraser la base {db_file} par la sauvegarde {os.path.basename(bak_path)} ?"):
                return
        shutil.copy2(bak_path, db_file)
        logger.info(f"Base restaurée depuis {bak_path} -> {db_file}")
        messagebox.showinfo("Restauration", f"Base restaurée avec succès depuis {bak_path}")
    except Exception as e:
        message = handle_exception(e, "Erreur lors de la restauration de la base.")
        messagebox.showerror("Erreur", message)

def open_database():
    """Permet de choisir et d'utiliser une autre base SQLite existante."""
    try:
        db_path = filedialog.askopenfilename(
            title="Sélectionnez un fichier de base de données SQLite",
            filetypes=[("Bases SQLite", "*.db *.sqlite *.sqlite3"), ("Tout", "*.*")]
        )
        if not db_path:
            return
        from db.db import set_db_file
        set_db_file(db_path)
        logger.info(f"Base de données active changée pour {db_path}")
        messagebox.showinfo("Changement de base", f"Base de données changée pour {db_path}")
        # Peut appeler un callback UI pour rafraîchir la barre de statut si besoin
    except Exception as e:
        message = handle_exception(e, "Erreur lors du changement de base.")
        messagebox.showerror("Erreur", message)

def set_status_callback(callback):
    """Permet à l'UI de s'abonner pour être notifiée lors d'un changement de base."""
    global _status_callback
    _status_callback = callback

    # Appelle le callback une première fois pour initialiser l'état
    try:
        if callback:
            callback()
    except Exception:
        pass