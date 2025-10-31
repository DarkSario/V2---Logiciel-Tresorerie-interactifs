import tkinter as tk
from tkinter import ttk
import pandas as pd
from db.db import get_connection

class StockStatsModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Statistiques du Stock")
        self.top.geometry("850x480")
        self.show_stats()

    def show_stats(self):
        conn = get_connection()
        df = pd.read_sql_query("""
            SELECT c.name as categorie, COUNT(s.id) as nb_articles, SUM(s.quantite) as total_qte
            FROM stock s
            LEFT JOIN categories c ON s.categorie_id = c.id
            GROUP BY c.name
            ORDER BY c.name
        """, conn)
        conn.close()

        tree = ttk.Treeview(self.top, columns=("categorie", "nb_articles", "total_qte"), show="headings")
        tree.heading("categorie", text="Catégorie")
        tree.heading("nb_articles", text="Nb buvette_articles")
        tree.heading("total_qte", text="Quantité totale")
        tree.column("categorie", width=200)
        tree.column("nb_articles", width=100, anchor="center")
        tree.column("total_qte", width=120, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=18)

        for _, row in df.iterrows():
            tree.insert("", "end", values=(row["categorie"], row["nb_articles"], row["total_qte"]))

        tk.Button(self.top, text="Fermer", command=self.top.destroy).pack(pady=10)