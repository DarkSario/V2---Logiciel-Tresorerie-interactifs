import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pandas as pd
from db.db import get_connection

class FournisseursWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestion des fournisseurs")
        self.geometry("430x400")
        self.resizable(False, False)
        self.create_widgets()
        self.refresh_fournisseurs()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tree = ttk.Treeview(frame, columns=("id", "name"), show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nom du fournisseur")
        self.tree.column("id", width=50)
        self.tree.column("name", width=260)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=8)

        btns = tk.Frame(frame)
        btns.pack(fill=tk.X, pady=8)
        tk.Button(btns, text="Ajouter", command=self.add_fournisseur).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Renommer", command=self.edit_fournisseur).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Supprimer", command=self.delete_fournisseur).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Ajout Liste", command=self.add_fournisseurs_mass).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=4)

    def refresh_fournisseurs(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        fournisseurs = conn.execute("SELECT * FROM fournisseurs ORDER BY name").fetchall()
        for f in fournisseurs:
            self.tree.insert("", "end", values=(f["id"], f["name"]))
        conn.close()

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionne un fournisseur.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_fournisseur(self):
        name = tk.simpledialog.askstring("Ajouter fournisseur", "Nom du fournisseur :")
        if not name:
            return
        conn = get_connection()
        try:
            conn.execute("INSERT INTO fournisseurs (name) VALUES (?)", (name.strip(),))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter : {e}")
        conn.close()
        self.refresh_fournisseurs()

    def add_fournisseurs_mass(self):
        win = tk.Toplevel(self)
        win.title("Ajout de fournisseurs en masse")
        win.geometry("320x330")
        tk.Label(win, text="Collez ici la liste des fournisseurs (un par ligne) :", font=("Arial", 11)).pack(pady=8)
        txt = tk.Text(win, width=36, height=12, font=("Arial", 11))
        txt.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        txt.focus_set()
        def valider():
            lines = txt.get("1.0", "end-1c").splitlines()
            fournisseurs = [l.strip() for l in lines if l.strip()]
            if not fournisseurs:
                messagebox.showinfo("Aucun fournisseur", "Aucun nom à ajouter.")
                return
            conn = get_connection()
            c = conn.cursor()
            n_inserted = 0
            for name in fournisseurs:
                try:
                    c.execute("INSERT OR IGNORE INTO fournisseurs (name) VALUES (?)", (name,))
                    n_inserted += c.rowcount
                except Exception:
                    pass
            conn.commit()
            conn.close()
            messagebox.showinfo("Import", f"{n_inserted} fournisseurs importés.")
            self.refresh_fournisseurs()
            win.destroy()
        tk.Button(win, text="Ajouter à la base", command=valider, font=("Arial", 11, "bold"), bg="#4c9ed9", fg="white").pack(pady=12)
        win.grab_set()
        win.wait_window()

    def edit_fournisseur(self):
        fid = self.get_selected_id()
        if not fid:
            return
        conn = get_connection()
        old = conn.execute("SELECT name FROM fournisseurs WHERE id=?", (fid,)).fetchone()
        conn.close()
        if not old:
            return
        new_nom = tk.simpledialog.askstring("Renommer fournisseur", "Nouveau name :", initialvalue=old["name"])
        if not new_nom or new_nom.strip() == old["name"]:
            return
        conn = get_connection()
        try:
            conn.execute("UPDATE fournisseurs SET name=? WHERE id=?", (new_nom.strip(), fid))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de renommer : {e}")
        conn.close()
        self.refresh_fournisseurs()

    def delete_fournisseur(self):
        fid = self.get_selected_id()
        if not fid:
            return
        if not messagebox.askyesno("Supprimer", "Êtes-vous sûr de vouloir supprimer ce fournisseur ?"):
            return
        confirm = simpledialog.askstring("Confirmation", "Retapez SUPPRIMER pour confirmer la suppression du fournisseur :", parent=self)
        if (confirm or "").strip().upper() != "SUPPRIMER":
            messagebox.showinfo("Annulé", "Suppression annulée.")
            return
        conn = get_connection()
        try:
            conn.execute("DELETE FROM fournisseurs WHERE id=?", (fid,))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer : {e}")
        conn.close()
        self.refresh_fournisseurs()