import tkinter as tk
from tkinter import messagebox
import pandas as pd
from db.db import get_connection, get_df_or_sql
from utils.error_handler import handle_errors

# Note: DataSource.is_visualisation n'était pas défini dans le code fourni.
# Pour compatibilité, on vérifie sa présence sinon on considère False.
try:
    from db.db import DataSource
    HAS_DATASOURCE = True
except ImportError:
    HAS_DATASOURCE = False

class EditDonDialog(tk.Toplevel):
    def __init__(self, master, don_id, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier don ou subvention")
        self.don_id = don_id
        self.on_save = on_save
        self.geometry("400x320")
        self.resizable(False, False)

        self.donateur_var = tk.StringVar()
        self.montant_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.commentaire_var = tk.StringVar()

        row = 0
        tk.Label(self, text="Donateur/financeur :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.donateur_var, width=28).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Montant (€) :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.montant_var, width=10).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Date :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.date_var, width=14).grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Commentaire :").grid(row=row, column=0, sticky="nw", padx=12, pady=8)
        self.commentaire_widget = tk.Text(self, height=4, width=28, wrap=tk.WORD)
        self.commentaire_widget.grid(row=row, column=1, pady=2, sticky="w"); row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.don_id is not None:
            self.prefill_fields()

    def prefill_fields(self):
        try:
            if HAS_DATASOURCE and getattr(DataSource, "is_visualisation", False):
                df = get_df_or_sql("dons_subventions")
                row = df[df['id'] == self.don_id].iloc[0]
            else:
                conn = get_connection()
                row = conn.execute(
                    "SELECT donateur, montant, date, commentaire FROM dons_subventions WHERE id=?", (self.don_id,)
                ).fetchone()
                conn.close()
            if row is not None:
                if not isinstance(row, pd.Series):
                    self.donateur_var.set(row[0])
                    self.montant_var.set(str(row[1]))
                    self.date_var.set(row[2])
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row[3] if row[3] else "")
                else:
                    self.donateur_var.set(row["donateur"])
                    self.montant_var.set(str(row["montant"]))
                    self.date_var.set(row["date"])
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row["commentaire"] if row["commentaire"] else "")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement du don : {e}")

    @handle_errors
    def save(self):
        donateur = self.donateur_var.get().strip()
        montant = self.montant_var.get().strip()
        date = self.date_var.get().strip()
        commentaire = self.commentaire_widget.get("1.0", tk.END).strip()
        if not donateur or not montant or not date:
            messagebox.showerror("Erreur", "Name, montant et date obligatoires.")
            return
        try:
            montant = float(montant.replace(",", "."))
        except Exception:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        conn = get_connection()
        try:
            if self.don_id is None:
                conn.execute(
                    "INSERT INTO dons_subventions (donateur, montant, date, commentaire) VALUES (?, ?, ?, ?)",
                    (donateur, montant, date, commentaire)
                )
            else:
                conn.execute(
                    "UPDATE dons_subventions SET donateur=?, montant=?, date=?, commentaire=? WHERE id=?",
                    (donateur, montant, date, commentaire, self.don_id)
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()