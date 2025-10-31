import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection

class HistoriqueCloturesModule(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestion des dates de clôture")
        self.geometry("480x350")
        self.resizable(False, False)
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)
        self.tree = ttk.Treeview(frame, columns=("id", "date_cloture"), show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("date_cloture", text="Date de clôture")
        self.tree.column("id", width=60)
        self.tree.column("date_cloture", width=180)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=8)

        btns = tk.Frame(frame)
        btns.pack(fill=tk.X, pady=10)
        tk.Button(btns, text="Ajouter", command=self.add_cloture).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Modifier", command=self.edit_cloture).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Supprimer", command=self.delete_cloture).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=6)

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        clotures = conn.execute("SELECT id, date_cloture FROM historique_clotures ORDER BY date_cloture DESC").fetchall()
        for c in clotures:
            self.tree.insert("", "end", values=(c["id"], c["date_cloture"]))
        conn.close()

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une clôture.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_cloture(self):
        date = simpledialog.askstring("Ajouter une clôture", "Date de clôture (YYYY-MM-DD) :")
        if not date:
            return
        conn = get_connection()
        conn.execute("INSERT INTO historique_clotures (date_cloture) VALUES (?)", (date,))
        conn.commit()
        conn.close()
        self.refresh_list()

    def edit_cloture(self):
        cid = self.get_selected_id()
        if not cid:
            return
        conn = get_connection()
        old = conn.execute("SELECT date_cloture FROM historique_clotures WHERE id=?", (cid,)).fetchone()
        conn.close()
        if not old:
            return
        new_date = simpledialog.askstring("Modifier clôture", "Nouvelle date (YYYY-MM-DD) :", initialvalue=old["date_cloture"])
        if not new_date or new_date == old["date_cloture"]:
            return
        conn = get_connection()
        conn.execute("UPDATE historique_clotures SET date_cloture=? WHERE id=?", (new_date, cid))
        conn.commit()
        conn.close()
        self.refresh_list()

    def delete_cloture(self):
        cid = self.get_selected_id()
        if not cid:
            return
        if not messagebox.askyesno("Supprimer", "Supprimer cette clôture ?"):
            return
        conn = get_connection()
        conn.execute("DELETE FROM historique_clotures WHERE id=?", (cid,))
        conn.commit()
        conn.close()
        self.refresh_list()