import tkinter as tk
from tkinter import messagebox
import pandas as pd
from db.db import get_connection, get_df_or_sql
from utils.error_handler import handle_errors

# Optionally handle DataSource if present
try:
    from db.db import DataSource
    HAS_DATASOURCE = True
except ImportError:
    HAS_DATASOURCE = False

class EditMemberDialog(tk.Toplevel):
    def __init__(self, master, member_id, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier membre")
        self.member_id = member_id
        self.on_save = on_save
        self.geometry("400x400")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.classe_var = tk.StringVar()
        self.cotisation_var = tk.StringVar()
        self.commentaire_var = tk.StringVar()

        row = 0
        tk.Label(self, text="Name :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.nom_var, width=28).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Prénom :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.prenom_var, width=28).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="E-mail :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.email_var, width=28).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Classe :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.classe_var, width=14).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Cotisation :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.cotisation_var, width=10).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Commentaire :").grid(row=row, column=0, sticky="nw", padx=12, pady=8)
        self.commentaire_widget = tk.Text(self, height=4, width=28, wrap=tk.WORD)
        self.commentaire_widget.grid(row=row, column=1, pady=2, sticky="w"); row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.member_id is not None:
            self.prefill_fields()

    def prefill_fields(self):
        try:
            if HAS_DATASOURCE and getattr(DataSource, "is_visualisation", False):
                df = get_df_or_sql("membres")
                row = df[df['id'] == self.member_id].iloc[0]
            else:
                conn = get_connection()
                row = conn.execute(
                    "SELECT name, prenom, email, classe, cotisation, commentaire FROM membres WHERE id=?", (self.member_id,)
                ).fetchone()
                conn.close()
            if row is not None:
                if not isinstance(row, pd.Series):
                    self.nom_var.set(row[0])
                    self.prenom_var.set(row[1])
                    self.email_var.set(row[2] if row[2] else "")
                    self.classe_var.set(row[3] if row[3] else "")
                    self.cotisation_var.set(str(row[4]) if row[4] else "")
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row[5] if row[5] else "")
                else:
                    self.nom_var.set(row["name"])
                    self.prenom_var.set(row["prenom"])
                    self.email_var.set(row["email"] if row["email"] else "")
                    self.classe_var.set(row["classe"] if row["classe"] else "")
                    self.cotisation_var.set(str(row["cotisation"]) if row["cotisation"] else "")
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row["commentaire"] if row["commentaire"] else "")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement membre : {e}")

    @handle_errors
    def save(self):
        name = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        email = self.email_var.get().strip()
        classe = self.classe_var.get().strip()
        cotisation = self.cotisation_var.get().strip()
        commentaire = self.commentaire_widget.get("1.0", tk.END).strip()
        if not name or not prenom:
            messagebox.showerror("Erreur", "Name et prénom obligatoires.")
            return
        conn = get_connection()
        try:
            if self.member_id is None:
                conn.execute(
                    "INSERT INTO membres (name, prenom, email, classe, cotisation, commentaire) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, prenom, email, classe, cotisation, commentaire)
                )
            else:
                conn.execute(
                    "UPDATE membres SET name=?, prenom=?, email=?, classe=?, cotisation=?, commentaire=? WHERE id=?",
                    (name, prenom, email, classe, cotisation, commentaire, self.member_id)
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()