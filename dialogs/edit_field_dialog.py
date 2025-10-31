import tkinter as tk
from tkinter import messagebox, ttk
from db.db import get_connection
from utils.error_handler import handle_errors

class EditFieldDialog(tk.Toplevel):
    def __init__(self, master, module_id, field_id, on_save=None, with_modele_colonne=False):
        super().__init__(master)
        self.title("Ajouter/Modifier champ")
        self.module_id = module_id
        self.field_id = field_id
        self.on_save = on_save
        self.with_modele_colonne = with_modele_colonne
        self.geometry("430x260" if with_modele_colonne else "400x210")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.modele_colonne_var = tk.StringVar()
        self.modeles_choices = []

        row = 0
        tk.Label(self, text="Name du champ :").grid(row=row, column=0, sticky="w", padx=12, pady=14)
        tk.Entry(self, textvariable=self.nom_var, width=32).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Type du champ :").grid(row=row, column=0, sticky="w", padx=12, pady=14)
        ttk.Combobox(self, textvariable=self.type_var, values=["TEXT", "INTEGER", "REAL"]).grid(row=row, column=1, pady=2)
        row += 1

        if self.with_modele_colonne:
            tk.Label(self, text="Modèle de colonne (liste de choix) :").grid(row=row, column=0, sticky="w", padx=12, pady=14)
            self.modeles_combo = ttk.Combobox(self, textvariable=self.modele_colonne_var, state="readonly")
            self.modeles_combo.grid(row=row, column=1, pady=2)
            # Préremplir la variable avant populate pour gérer le cas édition
            if self.field_id is not None:
                conn = get_connection()
                row_val = conn.execute("SELECT modele_colonne FROM event_module_fields WHERE id=?", (self.field_id,)).fetchone()
                conn.close()
                if row_val and row_val["modele_colonne"]:
                    self.modele_colonne_var.set(row_val["modele_colonne"])
            self.populate_modeles_combo()
            row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=24)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.field_id is not None:
            self.prefill_fields()

    def populate_modeles_combo(self):
        try:
            conn = get_connection()
            rows = conn.execute("SELECT name FROM colonnes_modeles ORDER BY name").fetchall()
            conn.close()
            self.modeles_choices = [""] + [r["name"] for r in rows]
            current = self.modele_colonne_var.get()
            if current and current not in self.modeles_choices:
                self.modeles_choices.append(current)
            self.modeles_combo["values"] = self.modeles_choices
            if current and current in self.modeles_choices:
                self.modeles_combo.set(current)
            else:
                self.modeles_combo.current(0)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement modèles de colonnes : {e}")

    def prefill_fields(self):
        try:
            conn = get_connection()
            if self.with_modele_colonne:
                row = conn.execute(
                    "SELECT nom_champ, type_champ, modele_colonne FROM event_module_fields WHERE id=?",
                    (self.field_id,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT nom_champ, type_champ FROM event_module_fields WHERE id=?",
                    (self.field_id,)
                ).fetchone()
            conn.close()
            if row is not None:
                self.nom_var.set(row[0])
                self.type_var.set(row[1])
                # self.modele_colonne_var est déjà prérempli avant populate_modeles_combo
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement champ : {e}")

    @handle_errors
    def save(self):
        name = self.nom_var.get().strip()
        typ = self.type_var.get().strip()
        modele_colonne = self.modele_colonne_var.get().strip() if self.with_modele_colonne else None
        if not name or not typ:
            messagebox.showerror("Erreur", "Name et type obligatoires.")
            return
        conn = get_connection()
        try:
            if self.field_id is None:
                if self.with_modele_colonne:
                    conn.execute(
                        "INSERT INTO event_module_fields (module_id, nom_champ, type_champ, modele_colonne) VALUES (?, ?, ?, ?)",
                        (self.module_id, name, typ, modele_colonne if modele_colonne else None)
                    )
                else:
                    conn.execute(
                        "INSERT INTO event_module_fields (module_id, nom_champ, type_champ) VALUES (?, ?, ?)",
                        (self.module_id, name, typ)
                    )
            else:
                if self.with_modele_colonne:
                    conn.execute(
                        "UPDATE event_module_fields SET nom_champ=?, type_champ=?, modele_colonne=? WHERE id=?",
                        (name, typ, modele_colonne if modele_colonne else None, self.field_id)
                    )
                else:
                    conn.execute(
                        "UPDATE event_module_fields SET nom_champ=?, type_champ=? WHERE id=?",
                        (name, typ, self.field_id)
                    )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()