import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from db.db import get_connection, DataSource, get_df_or_sql
from dialogs.inventaire_dialog import InventaireDialog

class StockInventaireModule:
    def __init__(self, master, visualisation_mode=False):
        self.master = master
        self.visualisation_mode = visualisation_mode
        self.top = tk.Toplevel(master)
        self.top.title("Inventaire rapide du stock")
        self.top.geometry("950x500")
        self.create_table()
        self.create_buttons()
        self.load_stock()

    def create_table(self):
        columns = ("id", "name", "categorie", "quantite", "nouvelle_quantite")
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings")
        for col, w in zip(columns, [45, 180, 130, 90, 110]):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def create_buttons(self):
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(btn_frame, text="Inventorier", command=self.inventorier, state=tk.DISABLED if self.visualisation_mode else tk.NORMAL).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

    def load_stock(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if DataSource.is_visualisation:
            df = get_df_or_sql("stock")
            cat_df = get_df_or_sql("categories")
            df = df.merge(cat_df, left_on="categorie_id", right_on="id", how="left", suffixes=('', '_cat'))
            df['categorie'] = df['nom_cat'].fillna('')
        else:
            conn = get_connection()
            query = """
                SELECT s.id, s.name, c.name as categorie, s.quantite
                FROM stock s
                LEFT JOIN categories c ON s.categorie_id = c.id
                ORDER BY s.name
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(row["id"], row["name"], row.get("categorie", ""), row["quantite"], ""))

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un article.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def inventorier(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un article à inventorier.")
            return
        item = self.tree.item(sel[0])
        stock_id = item["values"][0]
        name = item["values"][1]
        quantite = item["values"][3]
        dialog = InventaireDialog(self.top, name, quantite)
        self.top.wait_window(dialog)
        if dialog.result is not None:
            nouvelle_qte = dialog.result
            try:
                nouvelle_qte = int(nouvelle_qte)
            except Exception:
                messagebox.showerror("Erreur", "Quantité invalide.")
                return
            conn = get_connection()
            conn.execute("UPDATE stock SET quantite=? WHERE id=?", (nouvelle_qte, stock_id))
            conn.commit()
            conn.close()
            self.load_stock()
            messagebox.showinfo("Inventaire", f"Quantité de « {name} » mise à jour.")