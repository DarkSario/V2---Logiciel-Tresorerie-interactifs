import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from db.db import get_connection

class HistoriqueInventairesModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Historique des inventaires")
        self.top.geometry("900x500")
        self.create_table()
        self.refresh_inventaires()

    def create_table(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        style.configure("Treeview", font=('Consolas', 11), rowheight=22)
        style.configure("oddrow", background="#F2F2F2")
        style.configure("evenrow", background="#FFFFFF")

        columns = ("id", "date", "evenement", "nb_lignes", "commentaire")
        self.tree = ttk.Treeview(
            self.top, columns=columns, show="headings", selectmode="browse"
        )
        for col, text, w in zip(
            columns,
            ["ID", "Date", "Événement", "Nb buvette_articles", "Commentaire"],
            [40, 120, 160, 100, 340]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscroll=vsb.set)
        self.tree.bind("<Double-1>", self.show_lignes_inventaire)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(btn_frame, text="Afficher les lignes", command=self.show_lignes_inventaire).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

    def refresh_inventaires(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        df = pd.read_sql_query(
            """
            SELECT i.id, i.date_inventaire as date, e.name as evenement, i.commentaire,
                (SELECT COUNT(*) FROM inventaire_lignes WHERE inventaire_id = i.id) as nb_lignes
            FROM inventaires i
            LEFT JOIN events e ON i.event_id = e.id
            ORDER BY i.date_inventaire DESC, i.id DESC
            """, conn
        )
        self.df = df
        for idx, (_, row) in enumerate(df.iterrows()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "", "end",
                values=(
                    row['id'],
                    row['date'][:10] if pd.notnull(row['date']) else "",
                    row['evenement'] if pd.notnull(row['evenement']) else "",
                    row['nb_lignes'],
                    row['commentaire'] if pd.notnull(row['commentaire']) else ""
                ),
                tags=(tag,)
            )

    def show_lignes_inventaire(self, event=None):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez un inventaire à afficher.")
            return
        item = self.tree.item(sel[0])
        inv_id = item["values"][0]
        LignesInventaireDialog(self.top, inv_id)

class LignesInventaireDialog(tk.Toplevel):
    def __init__(self, master, inventaire_id):
        super().__init__(master)
        self.title(f"Lignes de l'inventaire n°{inventaire_id}")
        self.geometry("750x400")
        self.create_table()
        self.refresh_lignes(inventaire_id)

    def create_table(self):
        columns = ("stock_id", "name", "categorie", "quantite_constatee")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, text, w in zip(
            columns,
            ["ID stock", "Name article", "Catégorie", "Qté constatée"],
            [60, 220, 160, 100]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh_lignes(self, inventaire_id):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        lignes = conn.execute(
            """
            SELECT l.stock_id, s.name, c.name as categorie, l.quantite_constatee
            FROM inventaire_lignes l
            LEFT JOIN stock s ON l.stock_id = s.id
            LEFT JOIN categories c ON s.categorie_id = c.id
            WHERE l.inventaire_id = ?
            ORDER BY s.name
            """, (inventaire_id,)
        ).fetchall()
        for l in lignes:
            self.tree.insert("", "end", values=(l["stock_id"], l["name"], l["categorie"], l["quantite_constatee"]))
        conn.close()