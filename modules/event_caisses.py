import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("event_caisses")

class EventCaissesWindow(tk.Toplevel):
    def __init__(self, master, event_id):
        super().__init__(master)
        self.title(f"Caisses de l'événement {event_id}")
        self.geometry("700x400")
        self.event_id = event_id
        self.create_widgets()
        self.refresh_caisses()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Nouvelle caisse", command=self.add_caisse).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Éditer", command=self.edit_caisse).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_caisse).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)

        columns = ("id", "nom", "solde_initial", "responsable")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Nom de la caisse")
        self.tree.heading("solde_initial", text="Solde initial (€)")
        self.tree.heading("responsable", text="Responsable")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_caisses(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            caisses = conn.execute(
                "SELECT * FROM event_caisses WHERE event_id = ? ORDER BY id", (self.event_id,)
            ).fetchall()
            for caisse in caisses:
                self.tree.insert(
                    "", "end",
                    values=(
                        caisse["id"],
                        caisse["nom"],
                        f"{caisse['solde_initial']:.2f}" if caisse["solde_initial"] is not None else "",
                        caisse["responsable"] or ""
                    )
                )
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des caisses."))

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_caisse(self):
        CaisseDialog(self, event_id=self.event_id, on_save=self.refresh_caisses)

    def edit_caisse(self):
        cid = self.get_selected_id()
        if not cid:
            messagebox.showwarning("Sélection", "Sélectionne une caisse à éditer.")
            return
        CaisseDialog(self, event_id=self.event_id, caisse_id=cid, on_save=self.refresh_caisses)

    def delete_caisse(self):
        cid = self.get_selected_id()
        if not cid:
            messagebox.showwarning("Sélection", "Sélectionne une caisse à supprimer.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer cette caisse ?"):
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM event_caisses WHERE id=? AND event_id=?", (cid, self.event_id))
            conn.commit()
            conn.close()
            logger.info(f"Caisse supprimée id {cid}, event_id {self.event_id}")
            self.refresh_caisses()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de la caisse."))

class CaisseDialog(tk.Toplevel):
    def __init__(self, master, event_id, caisse_id=None, on_save=None):
        super().__init__(master)
        self.title("Caisse" if caisse_id is None else "Éditer caisse")
        self.event_id = event_id
        self.caisse_id = caisse_id
        self.on_save = on_save
        self.geometry("340x260")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.solde_var = tk.StringVar()
        self.resp_var = tk.StringVar()

        tk.Label(self, text="Nom de la caisse :").pack(pady=8)
        tk.Entry(self, textvariable=self.nom_var, width=30).pack()
        tk.Label(self, text="Solde initial (€) :").pack(pady=8)
        tk.Entry(self, textvariable=self.solde_var, width=15).pack()
        tk.Label(self, text="Responsable :").pack(pady=8)
        tk.Entry(self, textvariable=self.resp_var, width=25).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=30, pady=18)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=30, pady=18)

        if self.caisse_id:
            self.load_caisse()

    def load_caisse(self):
        try:
            conn = get_connection()
            caisse = conn.execute(
                "SELECT nom, solde_initial, responsable FROM event_caisses WHERE id=? AND event_id=?",
                (self.caisse_id, self.event_id)
            ).fetchone()
            conn.close()
            if caisse:
                self.nom_var.set(caisse["nom"])
                self.solde_var.set(f"{caisse['solde_initial']:.2f}" if caisse["solde_initial"] is not None else "")
                self.resp_var.set(caisse["responsable"] or "")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement de la caisse."))

    def save(self):
        nom = self.nom_var.get().strip()
        solde = self.solde_var.get().replace(",", ".").strip()
        resp = self.resp_var.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom de la caisse est obligatoire.")
            return
        try:
            solde_float = float(solde) if solde else 0.0
        except Exception:
            messagebox.showerror("Erreur", "Solde initial invalide.")
            return
        try:
            conn = get_connection()
            if self.caisse_id:
                conn.execute(
                    "UPDATE event_caisses SET nom=?, solde_initial=?, responsable=? WHERE id=? AND event_id=?",
                    (nom, solde_float, resp, self.caisse_id, self.event_id)
                )
            else:
                conn.execute(
                    "INSERT INTO event_caisses (event_id, nom, solde_initial, responsable) VALUES (?, ?, ?, ?)",
                    (self.event_id, nom, solde_float, resp)
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de la caisse."))