import tkinter as tk
from tkinter import messagebox
from db.db import get_connection
from utils.error_handler import handle_errors

class ClotureConfirmDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Confirmer la réinitialisation")
        self.geometry("400x210")
        tk.Label(self, text="⚠️ Êtes-vous sûr de vouloir réinitialiser la base ?", fg="red", font=("Arial", 13, "bold")).pack(pady=18)
        tk.Label(self, text="Toutes les données de l'exercice courant seront supprimées.\nCette action est IRRÉVERSIBLE.", fg="red").pack(pady=8)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=24)
        tk.Button(btn_frame, text="Oui, réinitialiser", fg="red", command=self.do_cloture).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

    @handle_errors
    def do_cloture(self):
        conn = get_connection()
        to_truncate = [
            "events", "event_modules", "event_module_fields", "event_module_data",
            "members", "dons_subventions", "depenses_regulieres", "depenses_diverses",
            "journal", "stock"
        ]
        for tab in to_truncate:
            try:
                conn.execute(f"DELETE FROM {tab}")
            except Exception as e:
                # On continue malgré l'échec sur une table (ex: si elle n'existe pas)
                pass
        conn.commit()
        conn.close()
        messagebox.showinfo("Clôture", "Données réinitialisées. Nouvel exercice prêt.")
        self.destroy()