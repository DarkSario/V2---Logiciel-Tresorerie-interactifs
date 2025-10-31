import tkinter as tk
from tkinter import messagebox
import pandas as pd
from db.db import get_connection, get_df_or_sql
from utils.error_handler import handle_errors

# Gérer DataSource si présent
try:
    from db.db import DataSource
    HAS_DATASOURCE = True
except ImportError:
    HAS_DATASOURCE = False

class EditJournalDialog(tk.Toplevel):
    def __init__(self, master, journal_id, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier ligne journal")
        self.journal_id = journal_id
        self.on_save = on_save
        self.geometry("430x380")
        self.resizable(False, False)

        self.date_var = tk.StringVar()
        self.libelle_var = tk.StringVar()
        self.montant_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.categorie_var = tk.StringVar()
        self.commentaire_var = tk.StringVar()

        row = 0
        tk.Label(self, text="Date :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.date_var, width=14).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Libellé :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.libelle_var, width=30).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Montant (€) :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.montant_var, width=12).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Type (dépense/recette) :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.type_var, width=16).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Catégorie :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.categorie_var, width=18).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Commentaire :").grid(row=row, column=0, sticky="nw", padx=12, pady=8)
        self.commentaire_widget = tk.Text(self, height=4, width=30, wrap=tk.WORD)
        self.commentaire_widget.grid(row=row, column=1, pady=2, sticky="w"); row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.journal_id is not None:
            self.prefill_fields()

    def prefill_fields(self):
        try:
            if HAS_DATASOURCE and getattr(DataSource, "is_visualisation", False):
                df = get_df_or_sql("journal")
                row = df[df['id'] == self.journal_id].iloc[0]
            else:
                conn = get_connection()
                row = conn.execute(
                    "SELECT date, libelle, montant, type, categorie, commentaire FROM journal WHERE id=?", (self.journal_id,)
                ).fetchone()
                conn.close()
            if row is not None:
                if not isinstance(row, pd.Series):
                    self.date_var.set(row[0])
                    self.libelle_var.set(row[1])
                    self.montant_var.set(str(row[2]))
                    self.type_var.set(row[3])
                    self.categorie_var.set(row[4] if row[4] else "")
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row[5] if row[5] else "")
                else:
                    self.date_var.set(row["date"])
                    self.libelle_var.set(row["libelle"])
                    self.montant_var.set(str(row["montant"]))
                    self.type_var.set(row["type"])
                    self.categorie_var.set(row["categorie"] if row["categorie"] else "")
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row["commentaire"] if row["commentaire"] else "")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement journal : {e}")

    @handle_errors
    def save(self):
        date = self.date_var.get().strip()
        libelle = self.libelle_var.get().strip()
        montant = self.montant_var.get().strip()
        typ = self.type_var.get().strip()
        categorie = self.categorie_var.get().strip()
        commentaire = self.commentaire_widget.get("1.0", tk.END).strip()
        if not date or not libelle or not montant or not typ:
            messagebox.showerror("Erreur", "Date, libellé, montant et type obligatoires.")
            return
        try:
            montant = float(montant.replace(",", "."))
        except Exception:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        conn = get_connection()
        try:
            if self.journal_id is None:
                conn.execute(
                    "INSERT INTO journal (date, libelle, montant, type, categorie, commentaire) VALUES (?, ?, ?, ?, ?, ?)",
                    (date, libelle, montant, typ, categorie, commentaire)
                )
            else:
                conn.execute(
                    "UPDATE journal SET date=?, libelle=?, montant=?, type=?, categorie=?, commentaire=? WHERE id=?",
                    (date, libelle, montant, typ, categorie, commentaire, self.journal_id)
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()