import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from db.db import get_connection
from utils.validation import is_required

class CategoriesModule:
    def __init__(self, master):
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("Gestion des Catégories")
        self.top.geometry("700x400")
        self.create_table()
        self.create_buttons()
        self.refresh_categories()

    def create_table(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        style.configure("Treeview", font=('Consolas', 11), rowheight=24)
        style.configure("oddrow", background="#F2F2F2")
        style.configure("evenrow", background="#FFFFFF")

        self.tree = ttk.Treeview(
            self.top, columns=("id", "name", "parent"), show="headings", selectmode="browse"
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("parent", text="Catégorie parente")
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=180)
        self.tree.column("parent", width=180)
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscroll=vsb.set)

    def refresh_categories(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        df = pd.read_sql_query("""
            SELECT c.id, c.name, p.name as parent
            FROM categories c
            LEFT JOIN categories p ON c.parent_id = p.id
            ORDER BY COALESCE(p.name, c.name), c.name
        """, conn)
        self.df = df
        for idx, (_, row) in enumerate(df.iterrows()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                row['id'], row['name'], row['parent'] if pd.notnull(row['parent']) else ""
            ), tags=(tag,))

    def create_buttons(self):
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(btn_frame, text="Ajouter", command=self.add_category).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Modifier", command=self.edit_category).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_category).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

    def add_category(self):
        data = self.category_form()
        if not data:
            return
        if not is_required(data['name']):
            messagebox.showerror("Erreur", "Le name est obligatoire.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (name, parent_id) VALUES (?, ?)", (data['name'], data['parent_id']))
        conn.commit()
        self.refresh_categories()

    def edit_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Sélectionnez une catégorie à modifier.")
            return
        item = self.tree.item(selected[0])
        cat_id = item['values'][0]
        row = self.df[self.df['id'] == cat_id].iloc[0]
        data = self.category_form(row)
        if not data:
            return
        if not is_required(data['name']):
            messagebox.showerror("Erreur", "Le name est obligatoire.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE categories SET name=?, parent_id=? WHERE id=?",
            (data['name'], data['parent_id'], cat_id)
        )
        conn.commit()
        self.refresh_categories()

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Sélectionnez une catégorie à supprimer.")
            return
        item = self.tree.item(selected[0])
        cat_id = item['values'][0]
        name = item['values'][1]
        # Vérifier si cette catégorie a des enfants ou des buvette_articles liés
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM categories WHERE parent_id=?", (cat_id,))
        nb_children = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM stock WHERE categorie_id=?", (cat_id,))
        nb_stock = cur.fetchone()[0]
        if nb_children > 0:
            messagebox.showerror("Erreur", "Impossible de supprimer une catégorie qui a des sous-catégories.")
            return
        if nb_stock > 0:
            messagebox.showerror("Erreur", "Impossible de supprimer une catégorie liée à des buvette_articles en stock.")
            return
        if messagebox.askyesno("Confirmation", f"Supprimer la catégorie '{name}' ?"):
            cur.execute("DELETE FROM categories WHERE id=?", (cat_id,))
            conn.commit()
            self.refresh_categories()

    def category_form(self, row=None):
        form = tk.Toplevel(self.top)
        form.title("Saisie Catégorie")
        conn = get_connection()
        df_cat = pd.read_sql_query("SELECT id, name FROM categories WHERE parent_id IS NULL", conn)
        # Préremplissage
        values = [
            row['name'] if row is not None else "",
            row['parent'] if row is not None else "",  # Catégorie parente
        ]
        tk.Label(form, text="Name").grid(row=0, column=0, sticky="w", pady=3, padx=5)
        nom_entry = tk.Entry(form, width=30)
        nom_entry.grid(row=0, column=1, pady=3, padx=5)
        nom_entry.insert(0, values[0])

        tk.Label(form, text="Catégorie parente (optionnel)").grid(row=1, column=0, sticky="w", pady=3, padx=5)
        parent_var = tk.StringVar()
        parent_cb = ttk.Combobox(form, textvariable=parent_var, values=list(df_cat['name']), state="readonly", width=27)
        parent_cb.grid(row=1, column=1, pady=3, padx=5)
        if values[1] and values[1] in df_cat['name'].values:
            parent_cb.set(values[1])
        else:
            parent_cb.set("")

        result = {}
        def validate():
            result['name'] = nom_entry.get().strip()
            parent_nom = parent_var.get().strip()
            if not result['name']:
                messagebox.showerror("Erreur", "Le name est obligatoire.")
                return
            if parent_nom:
                parent_row = df_cat[df_cat['name'] == parent_nom]
                if not parent_row.empty:
                    result['parent_id'] = int(parent_row.iloc[0]['id'])
                else:
                    result['parent_id'] = None
            else:
                result['parent_id'] = None
            form.destroy()
        tk.Button(form, text="Valider", command=validate).grid(row=2, column=0, pady=10)
        tk.Button(form, text="Annuler", command=lambda: form.destroy()).grid(row=2, column=1, pady=10)
        form.grab_set()
        form.wait_window()
        if result:
            return result
        else:
            return None