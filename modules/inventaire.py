import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
try:
    import pandas as pd
except ModuleNotFoundError:
    print("Le module 'pandas' est requis pour la gestion des inventaires. Installe-le : python -m pip install pandas")
    raise
from db.db import get_connection

class InventaireModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Nouvel inventaire")
        self.top.geometry("900x600")
        self.create_widgets()
        self.load_stock()

    def create_widgets(self):
        form = tk.Frame(self.top)
        form.pack(fill=tk.X, pady=6)
        tk.Label(form, text="Date de l'inventaire (YYYY-MM-DD) :").grid(row=0, column=0, sticky="e", padx=8, pady=2)
        self.date_var = tk.StringVar()
        tk.Entry(form, textvariable=self.date_var, width=16).grid(row=0, column=1, sticky="w")

        tk.Label(form, text="Événement lié (optionnel) :").grid(row=0, column=2, sticky="e", padx=8, pady=2)
        self.evt_var = tk.StringVar()
        self.evt_cb = ttk.Combobox(form, textvariable=self.evt_var, width=26, state="readonly")
        self.evt_cb.grid(row=0, column=3, sticky="w")
        self.evt_cb["values"] = self.get_events()
        self.evt_cb.set("")

        tk.Label(form, text="Commentaire :").grid(row=1, column=0, sticky="e", padx=8, pady=2)
        self.comment_var = tk.StringVar()
        tk.Entry(form, textvariable=self.comment_var, width=60).grid(row=1, column=1, columnspan=3, sticky="w")

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Enregistrer inventaire", command=self.save_inventaire).pack(side=tk.LEFT, padx=12)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=12)

        # Tableau des buvette_articles
        columns = ("stock_id", "name", "categorie", "quantite_stock", "quantite_constatee")
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings", selectmode="browse")
        for col, text, w in zip(
            columns,
            ["ID stock", "Name article", "Catégorie", "Quantité stock", "Qté constatée"],
            [60, 220, 160, 100, 120]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.edit_qte_constatee)

    def get_events(self):
        conn = get_connection()
        evts = conn.execute("SELECT name FROM events ORDER BY date DESC").fetchall()
        conn.close()
        return [e["name"] for e in evts]

    def load_stock(self):
        conn = get_connection()
        self.stock_df = pd.read_sql_query("""
            SELECT s.id as stock_id, s.name, c.name as categorie, s.quantite
            FROM stock s LEFT JOIN categories c ON s.categorie_id = c.id
            ORDER BY s.name
        """, conn)
        conn.close()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in self.stock_df.iterrows():
            self.tree.insert(
                "", "end",
                values=(row["stock_id"], row["name"], row["categorie"], row["quantite"], row["quantite"])
            )

    def edit_qte_constatee(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        qte = item["values"][4]
        qte_new = simpledialog.askinteger("Saisie", "Nouvelle quantité constatée :", initialvalue=qte)
        if qte_new is not None:
            vals = list(item["values"])
            vals[4] = qte_new
            self.tree.item(sel[0], values=vals)

    def save_inventaire(self):
        date = self.date_var.get().strip()
        evt_name = self.evt_var.get().strip()
        comment = self.comment_var.get().strip()
        if not date:
            messagebox.showerror("Erreur", "Date obligatoire.")
            return
        conn = get_connection()
        evt_id = None
        if evt_name:
            row = conn.execute("SELECT id FROM events WHERE name=?", (evt_name,)).fetchone()
            if row:
                evt_id = row["id"]
        # Insert inventaire
        conn.execute(
            "INSERT INTO inventaires (date_inventaire, event_id, commentaire) VALUES (?, ?, ?)",
            (date, evt_id, comment)
        )
        inv_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Insert lignes
        for row_id in self.tree.get_children():
            vals = self.tree.item(row_id)["values"]
            stock_id = vals[0]
            qte_constatee = vals[4]
            conn.execute(
                "INSERT INTO inventaire_lignes (inventaire_id, stock_id, quantite_constatee) VALUES (?, ?, ?)",
                (inv_id, stock_id, qte_constatee)
            )
        conn.commit()
        conn.close()
        messagebox.showinfo("OK", "Inventaire enregistré !")
        self.top.destroy()