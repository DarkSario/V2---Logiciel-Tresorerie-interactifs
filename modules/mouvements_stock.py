import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection
import pandas as pd

class MouvementsStockModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Historique des mouvements de stock")
        self.top.geometry("1000x550")
        self.create_table()
        self.refresh_mouvements()

    def create_table(self):
        columns = ("id", "date", "name", "type", "quantite", "prix_achat_total", "prix_unitaire", "date_peremption", "commentaire")
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings")
        for col, text, w in zip(
            columns,
            ["ID", "Date", "Article", "Type", "Quantité", "Prix total", "Prix unitaire", "Date péremption", "Commentaire"],
            [40, 100, 160, 70, 80, 90, 90, 110, 220]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscroll=vsb.set)
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

    def refresh_mouvements(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        df = pd.read_sql_query("""
            SELECT m.id, m.date, s.name, m.type, m.quantite, m.prix_achat_total, m.prix_unitaire, m.date_peremption, m.commentaire
            FROM mouvements_stock m
            LEFT JOIN stock s ON m.stock_id = s.id
            ORDER BY m.date DESC, m.id DESC
        """, conn)
        for _, row in df.iterrows():
            self.tree.insert(
                "", "end",
                values=(
                    row["id"], row["date"], row["name"], row["type"], row["quantite"],
                    f"{row['prix_achat_total']:.2f}" if pd.notnull(row['prix_achat_total']) else "",
                    f"{row['prix_unitaire']:.2f}" if pd.notnull(row['prix_unitaire']) else "",
                    row["date_peremption"] if pd.notnull(row["date_peremption"]) else "",
                    row["commentaire"] if pd.notnull(row["commentaire"]) else ""
                )
            )