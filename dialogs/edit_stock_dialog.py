import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd

from db.db import get_connection, DataSource, get_df_or_sql

class EditStockDialog(tk.Toplevel):
    def __init__(self, master, stock_id, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier article")
        self.stock_id = stock_id
        self.on_save = on_save
        self.geometry("450x540")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.qte_var = tk.IntVar()
        self.seuil_var = tk.IntVar()
        self.lot_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.commentaire_var = tk.StringVar()
        self.categorie_var = tk.StringVar()
        self.categories = self.fetch_categories()
        cat_names = [cat['name'] for cat in self.categories]

        row = 0
        tk.Label(self, text="Name :").grid(row=row, column=0, sticky="w", padx=12, pady=8); row += 1
        tk.Entry(self, textvariable=self.nom_var, width=32).grid(row=row-1, column=1, pady=2)
        tk.Label(self, text="Catégorie :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        self.cat_cb = ttk.Combobox(self, textvariable=self.categorie_var, values=cat_names, state="readonly", width=25)
        self.cat_cb.grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Quantité :").grid(row=row, column=0, sticky="w", padx=12, pady=8); row += 1
        tk.Entry(self, textvariable=self.qte_var, width=12).grid(row=row-1, column=1, pady=2, sticky="w")
        tk.Label(self, text="Seuil alerte :").grid(row=row, column=0, sticky="w", padx=12, pady=8); row += 1
        tk.Entry(self, textvariable=self.seuil_var, width=12).grid(row=row-1, column=1, pady=2, sticky="w")
        tk.Label(self, text="Lot :").grid(row=row, column=0, sticky="w", padx=12, pady=8); row += 1
        tk.Entry(self, textvariable=self.lot_var, width=16).grid(row=row-1, column=1, pady=2, sticky="w")
        tk.Label(self, text="Date de péremption :").grid(row=row, column=0, sticky="w", padx=12, pady=8); row += 1
        DateEntry(self, textvariable=self.date_var, date_pattern='yyyy-mm-dd').grid(row=row-1, column=1, pady=2, sticky="w")
        tk.Label(self, text="Commentaire :").grid(row=row, column=0, sticky="nw", padx=12, pady=8); row += 1
        self.commentaire_widget = tk.Text(self, height=4, width=32, wrap=tk.WORD)
        self.commentaire_widget.grid(row=row-1, column=1, pady=2, sticky="w")

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.stock_id is not None:
            self.prefill_fields()

    def fetch_categories(self):
        if DataSource.is_visualisation:
            df = get_df_or_sql("categories")
            return df.to_dict("records")
        conn = get_connection()
        df = pd.read_sql_query("SELECT id, name FROM categories ORDER BY name", conn)
        conn.close()
        return df.to_dict("records")

    def prefill_fields(self):
        if DataSource.is_visualisation:
            df = get_df_or_sql("stock")
            row = df[df['id'] == self.stock_id].iloc[0]
        else:
            conn = get_connection()
            row = conn.execute(
                "SELECT name, quantite, seuil_alerte, lot, date_peremption, commentaire, categorie_id FROM stock WHERE id=?",
                (self.stock_id,)
            ).fetchone()
            conn.close()
        if row is not None:
            if not isinstance(row, pd.Series):
                self.nom_var.set(row[0])
                self.qte_var.set(row[1])
                self.seuil_var.set(row[2])
                self.lot_var.set(row[3] if row[3] else "")
                self.date_var.set(row[4] if row[4] else "")
                self.commentaire_widget.delete("1.0", tk.END)
                self.commentaire_widget.insert("1.0", row[5] if row[5] else "")
                cat_id = row[6]
            else:
                self.nom_var.set(row["name"])
                self.qte_var.set(row["quantite"])
                self.seuil_var.set(row["seuil_alerte"])
                self.lot_var.set(row["lot"] if row["lot"] else "")
                self.date_var.set(row["date_peremption"] if row["date_peremption"] else "")
                self.commentaire_widget.delete("1.0", tk.END)
                self.commentaire_widget.insert("1.0", row["commentaire"] if row["commentaire"] else "")
                cat_id = row["categorie_id"]
            for cat in self.categories:
                if cat['id'] == cat_id:
                    self.categorie_var.set(cat['name'])
                    break

    def save(self):
        name = self.nom_var.get().strip()
        quantite = self.qte_var.get()
        seuil = self.seuil_var.get()
        lot = self.lot_var.get().strip()
        date_peremption = self.date_var.get().strip()
        commentaire = self.commentaire_widget.get("1.0", tk.END).strip()
        cat_nom = self.categorie_var.get()
        cat_id = None
        for cat in self.categories:
            if cat['name'] == cat_nom:
                cat_id = cat['id']
                break
        if not name or cat_id is None:
            messagebox.showerror("Erreur", "Name et catégorie obligatoires.")
            return
        conn = get_connection()
        if self.stock_id is None:
            conn.execute(
                """INSERT INTO stock (name, categorie_id, quantite, seuil_alerte, lot, date_peremption, commentaire)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, cat_id, quantite, seuil, lot if lot else None,
                 date_peremption if date_peremption else None, commentaire)
            )
        else:
            conn.execute(
                """UPDATE stock SET name=?, categorie_id=?, quantite=?, seuil_alerte=?, lot=?, date_peremption=?, commentaire=?
                WHERE id=?""",
                (name, cat_id, quantite, seuil, lot if lot else None,
                 date_peremption if date_peremption else None, commentaire, self.stock_id)
            )
        conn.commit()
        if self.on_save:
            self.on_save()
        self.destroy()