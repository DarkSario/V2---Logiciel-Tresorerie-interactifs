import tkinter as tk
from tkinter import messagebox
from db.db import get_connection
from utils.error_handler import handle_errors

class EditModuleDialog(tk.Toplevel):
    def __init__(self, master, event_id, module_id, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier module")
        self.event_id = event_id
        self.module_id = module_id
        self.on_save = on_save
        self.geometry("400x180")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        row = 0
        tk.Label(self, text="Name du module :").grid(row=row, column=0, sticky="w", padx=12, pady=14)
        tk.Entry(self, textvariable=self.nom_var, width=36).grid(row=row, column=1, pady=2); row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=24)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.module_id is not None:
            self.prefill_fields()

    def prefill_fields(self):
        try:
            conn = get_connection()
            row = conn.execute(
                "SELECT nom_module FROM event_modules WHERE id=?", (self.module_id,)
            ).fetchone()
            conn.close()
            if row is not None:
                self.nom_var.set(row[0])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement module : {e}")

    @handle_errors
    def save(self):
        name = self.nom_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Name du module obligatoire.")
            return
        conn = get_connection()
        try:
            if self.module_id is None:
                conn.execute(
                    "INSERT INTO event_modules (event_id, nom_module) VALUES (?, ?)",
                    (self.event_id, name)
                )
            else:
                conn.execute(
                    "UPDATE event_modules SET nom_module=? WHERE id=?",
                    (name, self.module_id)
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()