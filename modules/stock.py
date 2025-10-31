import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from db.db import get_connection

class StockModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Gestion du Stock")
        self.top.geometry("1050x600")
        self.create_table()
        self.create_buttons()
        self.refresh_stock()

    def create_table(self):
        columns = ("id", "name", "categorie", "quantite", "seuil_alerte", "date_peremption", "lot", "commentaire")
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings")
        for col, text, w in zip(
            columns,
            ["ID", "Name", "Catégorie", "Quantité", "Seuil alerte", "Date péremption", "Lot", "Commentaire"],
            [40, 160, 120, 80, 95, 100, 95, 220]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscroll=vsb.set)

    def create_buttons(self):
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(btn_frame, text="Ajouter article", command=self.add_stock).pack(side=tk.LEFT, padx=7)
        tk.Button(btn_frame, text="Modifier", command=self.edit_stock).pack(side=tk.LEFT, padx=7)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_stock).pack(side=tk.LEFT, padx=7)
        tk.Button(btn_frame, text="Mouvement stock", command=self.open_mouvements).pack(side=tk.LEFT, padx=7)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=7)

    def refresh_stock(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        df = pd.read_sql_query("""
            SELECT s.id, s.name, c.name as categorie, s.quantite, s.seuil_alerte, s.date_peremption, s.lot, s.commentaire
            FROM stock s
            LEFT JOIN categories c ON s.categorie_id = c.id
            ORDER BY s.name
        """, conn)
        self.df = df
        for idx, (_, row) in enumerate(df.iterrows()):
            self.tree.insert(
                "", "end",
                values=(
                    row["id"], row["name"], row["categorie"], row["quantite"],
                    row["seuil_alerte"], row["date_peremption"], row["lot"], row["commentaire"]
                )
            )

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_stock(self):
        StockDialog(self.top, on_save=self.refresh_stock)

    def edit_stock(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning("Sélection", "Sélectionnez un article à modifier.")
            return
        row = self.df[self.df['id'] == sid].iloc[0]
        StockDialog(self.top, stock=row, on_save=self.refresh_stock)

    def delete_stock(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning("Sélection", "Sélectionnez un article à supprimer.")
            return
        if not messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer cet article ?"):
            return
        confirm = simpledialog.askstring("Confirmation", "Retapez SUPPRIMER pour confirmer la suppression de l'article :", parent=self.top)
        if (confirm or "").strip().upper() != "SUPPRIMER":
            messagebox.showinfo("Annulé", "Suppression annulée.")
            return
        conn = get_connection()
        conn.execute("DELETE FROM stock WHERE id=?", (sid,))
        conn.commit()
        conn.close()
        self.refresh_stock()

    def open_mouvements(self):
        from modules.mouvements_stock import MouvementsStockModule
        MouvementsStockModule(self.top)

class StockDialog(tk.Toplevel):
    def __init__(self, master, stock=None, on_save=None):
        super().__init__(master)
        self.title("Article" if stock is None else "Modifier article")
        self.stock = stock
        self.on_save = on_save
        self.geometry("420x440")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.cat_var = tk.StringVar()
        self.qte_var = tk.IntVar()
        self.seuil_var = tk.IntVar()
        self.date_peremp_var = tk.StringVar()
        self.lot_var = tk.StringVar()
        self.comment_var = tk.StringVar()

        tk.Label(self, text="Name :").pack(pady=5)
        tk.Entry(self, textvariable=self.nom_var, width=30).pack()
        tk.Label(self, text="Catégorie :").pack(pady=5)
        self.cat_cb = ttk.Combobox(self, textvariable=self.cat_var, state="readonly", width=25)
        self.cat_cb.pack()
        self.cat_cb["values"] = self.get_categories()
        tk.Label(self, text="Quantité :").pack(pady=5)
        tk.Entry(self, textvariable=self.qte_var, width=12).pack()
        tk.Label(self, text="Seuil alerte :").pack(pady=5)
        tk.Entry(self, textvariable=self.seuil_var, width=12).pack()
        tk.Label(self, text="Date péremption :").pack(pady=5)
        tk.Entry(self, textvariable=self.date_peremp_var, width=15).pack()
        tk.Label(self, text="Lot :").pack(pady=5)
        tk.Entry(self, textvariable=self.lot_var, width=18).pack()
        tk.Label(self, text="Commentaire :").pack(pady=5)
        tk.Entry(self, textvariable=self.comment_var, width=38).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=36, pady=17)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=36, pady=17)

        if self.stock is not None:
            self.load_stock()

    def get_categories(self):
        conn = get_connection()
        cats = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        conn.close()
        return [c["name"] for c in cats]

    def load_stock(self):
        s = self.stock
        self.nom_var.set(s["name"])
        self.cat_var.set(s["categorie"])
        self.qte_var.set(s["quantite"])
        self.seuil_var.set(s["seuil_alerte"])
        self.date_peremp_var.set(s["date_peremption"])
        self.lot_var.set(s["lot"])
        self.comment_var.set(s["commentaire"])

    def save(self):
        name = self.nom_var.get().strip()
        cat = self.cat_var.get().strip()
        qte = self.qte_var.get()
        seuil = self.seuil_var.get()
        datep = self.date_peremp_var.get().strip()
        lot = self.lot_var.get().strip()
        comment = self.comment_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Name obligatoire.")
            return
        conn = get_connection()
        cat_id = None
        if cat:
            row = conn.execute("SELECT id FROM categories WHERE name=?", (cat,)).fetchone()
            if row:
                cat_id = row["id"]
        if self.stock is not None:
            conn.execute(
                "UPDATE stock SET name=?, categorie_id=?, quantite=?, seuil_alerte=?, date_peremption=?, lot=?, commentaire=? WHERE id=?",
                (name, cat_id, qte, seuil, datep, lot, comment, self.stock["id"])
            )
        else:
            conn.execute(
                "INSERT INTO stock (name, categorie_id, quantite, seuil_alerte, date_peremption, lot, commentaire) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, cat_id, qte, seuil, datep, lot, comment)
            )
        conn.commit()
        conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()