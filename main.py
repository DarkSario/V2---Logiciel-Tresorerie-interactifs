import tkinter as tk
import os
import sys
from tkinter import messagebox, Toplevel, Label, Button
from tkcalendar import DateEntry

from db.db import (
    init_db, is_first_launch, save_init_info, get_connection,
    upgrade_db_structure, get_db_file
)
from ui import startup_schema_check
from modules.events import EventsWindow
from modules.stock import StockModule
from modules.buvette import BuvetteModule
from modules.members import MembersModule
from modules.dons_subventions import DonsSubventionsModule
from modules.depenses_regulieres import DepensesRegulieresModule
from modules.depenses_diverses import DepensesDiversesModule
from modules.journal import JournalModule
from modules.cloture_exercice import ClotureExerciceModule
from modules.exports import ExportsWindow
from dashboard.dashboard import DashboardModule
from modules.fournisseurs import FournisseursWindow
from utils import backup_restore
from modules.depots_retraits_banque import DepotsRetraitsBanqueModule
from modules.solde_ouverture import SoldeOuvertureDialog
from modules.historique_clotures import HistoriqueCloturesModule
from modules.retrocessions_ecoles import RetrocessionsEcolesModule
from utils.error_handler import handle_errors

DB_FILE = "association.db"

if not os.path.exists(DB_FILE):
    init_db()

# ==== Logique métier isolée ====

def get_current_exercice_info():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT exercice, date FROM config ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return row["exercice"], row["date"]
    else:
        return None, None

def update_exercice_info(exercice, date, disponible_banque):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE config SET exercice=?, date=?, disponible_banque=? WHERE id=(SELECT id FROM config ORDER BY id DESC LIMIT 1)",
        (exercice, date, disponible_banque)
    )
    conn.commit()
    conn.close()

# ==== Main Application UI ====

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion Association Les Interactifs des Ecoles")
        if is_first_launch():
            self.init_first_launch()
        
        # Vérification automatique du schéma de base de données
        if os.path.exists(DB_FILE):
            try:
                startup_schema_check.run_check(self, DB_FILE)
            except Exception as e:
                print(f"Warning: Schema check failed: {e}")
        
        self.create_menu()
        self.create_home_buttons()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status_var, anchor="e")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_dbfile_status()
        backup_restore.set_status_callback(self.update_dbfile_status)

    def update_dbfile_status(self):
        dbfile = get_db_file()
        self.status_var.set(f"Base de données : {dbfile}")
        self.title(f"Gestion Association Les Interactifs des Ecoles [{dbfile}]")

    def init_first_launch(self):
        dialog = Toplevel(self)
        dialog.title("Initialisation")
        dialog.grab_set()
        dialog.resizable(False, False)

        Label(dialog, text="Name de l'exercice (ex: 2024-2025) :").pack(padx=10, pady=(12,2), anchor="w")
        exercice_var = tk.StringVar()
        tk.Entry(dialog, textvariable=exercice_var).pack(padx=10, pady=2, anchor="w")

        Label(dialog, text="Date de début de l'exercice :").pack(padx=10, pady=(12,2), anchor="w")
        date_var = tk.StringVar()
        date_entry = DateEntry(dialog, textvariable=date_var, date_pattern='yyyy-mm-dd', width=18)
        date_entry.pack(padx=10, pady=2, anchor="w")

        Label(dialog, text="Disponible sur le compte bancaire (€) :").pack(padx=10, pady=(12,2), anchor="w")
        banque_var = tk.DoubleVar()
        tk.Entry(dialog, textvariable=banque_var).pack(padx=10, pady=2, anchor="w")

        def valider():
            exercice = exercice_var.get()
            date = date_var.get()
            try:
                disponible_banque = float(banque_var.get())
            except Exception:
                disponible_banque = None
            if exercice and date and disponible_banque is not None:
                save_init_info(exercice, date, None, disponible_banque)
                dialog.destroy()
                messagebox.showinfo("Bienvenue", "Initialisation effectuée !")
            else:
                messagebox.showwarning("Attention", "Toutes les informations doivent être saisies pour l'initialisation.")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="OK", command=valider, width=10).pack(side="left", padx=10)
        Button(btn_frame, text="Annuler", command=dialog.destroy, width=10).pack(side="right", padx=10)
        dialog.wait_window()

    @handle_errors
    def edit_exercice(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM config ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showwarning("Aucun exercice", "Aucune information d'exercice trouvée.")
            return

        dialog = Toplevel(self)
        dialog.title("Modifier l'exercice")
        dialog.grab_set()
        dialog.resizable(False, False)

        Label(dialog, text="Name de l'exercice (ex: 2024-2025) :").pack(padx=10, pady=(12,2), anchor="w")
        exercice_var = tk.StringVar(value=row["exercice"])
        tk.Entry(dialog, textvariable=exercice_var).pack(padx=10, pady=2, anchor="w")

        Label(dialog, text="Date de début de l'exercice :").pack(padx=10, pady=(12,2), anchor="w")
        date_var = tk.StringVar(value=row["date"])
        date_entry = DateEntry(dialog, textvariable=date_var, date_pattern='yyyy-mm-dd', width=18)
        date_entry.pack(padx=10, pady=2, anchor="w")

        Label(dialog, text="Disponible sur le compte bancaire (€) :").pack(padx=10, pady=(12,2), anchor="w")
        banque_var = tk.DoubleVar(value=row["disponible_banque"] if row["disponible_banque"] is not None else 0)
        tk.Entry(dialog, textvariable=banque_var).pack(padx=10, pady=2, anchor="w")

        def valider():
            exercice = exercice_var.get()
            date = date_var.get()
            try:
                disponible_banque = float(banque_var.get())
            except Exception:
                disponible_banque = None
            if exercice and date and disponible_banque is not None:
                update_exercice_info(exercice, date, disponible_banque)
                dialog.destroy()
                messagebox.showinfo("Succès", "Exercice modifié !")
                self.create_home_buttons()
            else:
                messagebox.showwarning("Attention", "Toutes les informations doivent être saisies pour la modification.")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Enregistrer", command=valider, width=12).pack(side="left", padx=10)
        Button(btn_frame, text="Annuler", command=dialog.destroy, width=12).pack(side="right", padx=10)
        dialog.wait_window()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        modules_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Modules", menu=modules_menu)
        modules_menu.add_command(label="Événements", command=handle_errors(lambda: EventsWindow(self)))
        modules_menu.add_command(label="Stock", command=handle_errors(lambda: StockModule(self)))
        modules_menu.add_command(label="Buvette", command=handle_errors(lambda: BuvetteModule(self)))
        modules_menu.add_command(label="Membres", command=handle_errors(lambda: MembersModule(self)))
        modules_menu.add_command(label="Dons/Subventions", command=handle_errors(lambda: DonsSubventionsModule(self)))
        modules_menu.add_command(label="Dépenses Régulières", command=handle_errors(lambda: DepensesRegulieresModule(self)))
        modules_menu.add_command(label="Dépenses Diverses", command=handle_errors(lambda: DepensesDiversesModule(self)))
        modules_menu.add_separator()
        modules_menu.add_command(label="Rétrocessions aux écoles", command=handle_errors(lambda: RetrocessionsEcolesModule(self)))
        modules_menu.add_separator()
        modules_menu.add_command(label="Gérer les fournisseurs", command=handle_errors(lambda: FournisseursWindow(self)))
        modules_menu.add_separator()
        modules_menu.add_command(label="Clôture Exercice", command=handle_errors(lambda: ClotureExerciceModule(self)))

        menubar.add_command(label="Exports", command=handle_errors(lambda: ExportsWindow(self)))
        menubar.add_command(label="Tableau de Bord", command=handle_errors(lambda: DashboardModule(self)))
        menubar.add_command(label="Journal Général", command=handle_errors(lambda: JournalModule(self)))

        # Sous-menu Administration
        params_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Administration", menu=params_menu)
        params_menu.add_command(label="Éditer exercice", command=self.edit_exercice)
        params_menu.add_command(label="Solde d'ouverture bancaire", command=handle_errors(lambda: SoldeOuvertureDialog(self)))
        params_menu.add_command(label="Gestion des clôtures", command=handle_errors(lambda: HistoriqueCloturesModule(self)))
        params_menu.add_command(label="Sauvegarder la base...", command=handle_errors(backup_restore.backup_database))
        params_menu.add_command(label="Restaurer la base...", command=handle_errors(backup_restore.restore_database))
        params_menu.add_command(label="Ouvrir une autre base...", command=handle_errors(backup_restore.open_database))
        params_menu.add_separator()
        params_menu.add_command(label="Réinitialiser les données", command=handle_errors(self.reset_data))
        params_menu.add_command(label="Mettre à jour la structure de la base", command=handle_errors(self.menu_upgrade_db_structure))

        menubar.add_command(label="Quitter", command=self.quit)

    @handle_errors
    def menu_upgrade_db_structure(self):
        # Message d'information pour la migration
        migration_message = (
            "Voulez-vous mettre à jour/adapter la structure de la base de données ?\n\n"
            "Cette opération va :\n"
            "- Créer une sauvegarde automatique timestampée\n"
            "- Ajouter les colonnes manquantes sans perte de données\n"
            "- Optimiser la base de données (WAL mode)\n"
            "- Générer un rapport détaillé\n\n"
            "Souhaitez-vous continuer ?"
        )
        
        if messagebox.askyesno("Mise à jour", migration_message):
            # Utiliser le nouveau script de migration sûr
            try:
                import subprocess
                db_path = get_db_file()
                result = subprocess.run(
                    [sys.executable, "scripts/update_db_structure.py", "--db-path", db_path],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                if result.returncode == 0:
                    messagebox.showinfo(
                        "Succès",
                        "Mise à jour de la structure terminée avec succès !\n\n"
                        "Un rapport détaillé a été généré dans le répertoire scripts/.\n"
                        "Une sauvegarde de votre base a été créée automatiquement."
                    )
                else:
                    messagebox.showerror(
                        "Erreur",
                        f"La mise à jour a échoué.\n\nDétails :\n{result.stderr[:500]}"
                    )
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'exécuter la mise à jour : {e}")

    @handle_errors
    def reset_data(self):
        confirm = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment réinitialiser toutes les données ?\nCette action est irréversible."
        )
        if confirm:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            messagebox.showinfo(
                "Réinitialisation",
                "Données effacées. L'application va redémarrer pour une nouvelle initialisation."
            )
            self.destroy()
            os.execl(sys.executable, sys.executable, *os.sys.argv)

    def create_home_buttons(self):
        for widget in self.winfo_children():
            if not isinstance(widget, tk.Menu) and not (hasattr(self, "status_label") and widget is self.status_label):
                widget.destroy()
        tk.Label(self, text="Les Interactifs des Ecoles", font=("Arial", 18, "bold")).pack(pady=(25,2))

        # Ajoute l'exercice en cours et sa date de début
        exercice, date = get_current_exercice_info()
        if exercice and date:
            info_exercice = f"Exercice en cours : {exercice} (Début : {date})"
        else:
            info_exercice = "Aucun exercice en cours"
        tk.Label(self, text=info_exercice, font=("Arial", 13, "italic"), fg="blue").pack(pady=(2,20))

        # Frame pour les boutons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)

        buttons = [
            ("Événements", lambda: EventsWindow(self)),
            ("Stock", lambda: StockModule(self)),
            ("Buvette", lambda: BuvetteModule(self)),
            ("Membres", lambda: MembersModule(self)),
            ("Dons/Subventions", lambda: DonsSubventionsModule(self)),
            ("Dépenses Régulières", lambda: DepensesRegulieresModule(self)),
            ("Dépenses Diverses", lambda: DepensesDiversesModule(self)),
            ("Rétrocessions aux écoles", lambda: RetrocessionsEcolesModule(self)),
            ("Dépôts/Retraits Banque", lambda: DepotsRetraitsBanqueModule(self)),
            ("Clôture Exercice", lambda: ClotureExerciceModule(self)),
            ("Exports / Bilans", lambda: ExportsWindow(self)),
        ]

        cols = 3
        for idx, (label, action) in enumerate(buttons):
            btn = tk.Button(
                btn_frame, text=label, command=handle_errors(action),
                width=20, height=3, font=("Arial", 12, "bold")
            )
            row, col = divmod(idx, cols)
            btn.grid(row=row, column=col, padx=12, pady=12)

        self.update_idletasks()
        self.geometry("")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()