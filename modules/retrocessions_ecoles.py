import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection

class RetrocessionsEcolesModule(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Rétrocessions aux écoles")
        self.geometry("560x420")
        self.resizable(False, False)
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tree = ttk.Treeview(frame, columns=("id", "date", "ecole", "montant", "commentaire"), show="headings", selectmode="browse")
        for col, txt, w in zip(
            ("id", "date", "ecole", "montant", "commentaire"),
            ["ID", "Date", "École", "Montant (€)", "Commentaire"],
            [40, 90, 140, 100, 160]
        ):
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=6)

        btns = tk.Frame(frame)
        btns.pack(fill=tk.X, pady=10)
        tk.Button(btns, text="Ajouter", command=self.add_retro).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Modifier", command=self.edit_retro).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Supprimer", command=self.delete_retro).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=6)

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, date, ecole, montant, commentaire FROM retrocessions_ecoles ORDER BY date DESC"
        ).fetchall()
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["date"], r["ecole"], f"{r['montant']:.2f}", r["commentaire"]))
        conn.close()

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_retro(self):
        self.edit_retro_form()

    def edit_retro(self):
        cid = self.get_selected_id()
        if not cid:
            return
        conn = get_connection()
        old = conn.execute("SELECT * FROM retrocessions_ecoles WHERE id=?", (cid,)).fetchone()
        conn.close()
        if not old:
            return
        self.edit_retro_form(old)

    def edit_retro_form(self, data=None):
        win = tk.Toplevel(self)
        win.title("Rétrocession" + (" - Modifier" if data else " - Ajouter"))
        win.geometry("350x290")
        win.grab_set()

        tk.Label(win, text="Date (YYYY-MM-DD)").pack(pady=(16,2))
        date_var = tk.StringVar(value=data["date"] if data else "")
        tk.Entry(win, textvariable=date_var).pack()

        tk.Label(win, text="École").pack(pady=(12,2))
        ecole_var = tk.StringVar(value=data["ecole"] if data else "")
        tk.Entry(win, textvariable=ecole_var).pack()

        tk.Label(win, text="Montant (€)").pack(pady=(12,2))
        montant_var = tk.StringVar(value=f"{data['montant']:.2f}" if data else "")
        tk.Entry(win, textvariable=montant_var).pack()

        tk.Label(win, text="Commentaire").pack(pady=(12,2))
        comm_var = tk.StringVar(value=data["commentaire"] if data else "")
        tk.Entry(win, textvariable=comm_var).pack()

        def valider():
            date = date_var.get().strip()
            ecole = ecole_var.get().strip()
            montant = montant_var.get().replace(",", ".").strip()
            commentaire = comm_var.get().strip()
            try:
                montant_float = float(montant)
            except Exception:
                messagebox.showerror("Erreur", "Montant invalide.")
                return
            if not (date and ecole):
                messagebox.showerror("Erreur", "Date et école obligatoires.")
                return
            conn = get_connection()
            if data:
                conn.execute("UPDATE retrocessions_ecoles SET date=?, ecole=?, montant=?, commentaire=? WHERE id=?",
                             (date, ecole, montant_float, commentaire, data["id"]))
            else:
                conn.execute("INSERT INTO retrocessions_ecoles (date, ecole, montant, commentaire) VALUES (?, ?, ?, ?)",
                             (date, ecole, montant_float, commentaire))
            conn.commit()
            conn.close()
            win.destroy()
            self.refresh_list()

        tk.Button(win, text="Valider", command=valider).pack(pady=16)
        tk.Button(win, text="Annuler", command=win.destroy).pack()
        win.wait_window()

    def delete_retro(self):
        cid = self.get_selected_id()
        if not cid:
            return
        if not messagebox.askyesno("Supprimer", "Supprimer cette rétrocession ?"):
            return
        conn = get_connection()
        conn.execute("DELETE FROM retrocessions_ecoles WHERE id=?", (cid,))
        conn.commit()
        conn.close()
        self.refresh_list()