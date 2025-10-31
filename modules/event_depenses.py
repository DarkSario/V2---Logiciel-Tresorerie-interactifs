import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("event_depenses")

class EventDepensesWindow(tk.Toplevel):
    def __init__(self, master, event_id):
        super().__init__(master)
        self.title(f"Dépenses de l'événement {event_id}")
        self.geometry("860x480")
        self.event_id = event_id
        self.create_widgets()
        self.refresh_depenses()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Nouvelle dépense", command=self.add_depense).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Éditer", command=self.edit_depense).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_depense).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)

        columns = ("id", "date", "fournisseur", "categorie", "montant", "description", "justificatif")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("fournisseur", text="Fournisseur")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("montant", text="Montant (€)")
        self.tree.heading("description", text="Description")
        self.tree.heading("justificatif", text="Justificatif")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_depenses(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            depenses = conn.execute(
                "SELECT * FROM event_depenses WHERE event_id = ? ORDER BY date, id", (self.event_id,)
            ).fetchall()
            for dep in depenses:
                self.tree.insert(
                    "", "end",
                    values=(
                        dep["id"],
                        dep["date"],
                        dep["fournisseur"] or "",
                        dep["categorie"] or "",
                        f"{dep['montant']:.2f}" if dep["montant"] is not None else "",
                        dep["description"] or "",
                        dep["justificatif"] or ""
                    )
                )
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des dépenses."))

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_depense(self):
        DepenseDialog(self, event_id=self.event_id, on_save=self.refresh_depenses)

    def edit_depense(self):
        did = self.get_selected_id()
        if not did:
            messagebox.showwarning("Sélection", "Sélectionne une dépense à éditer.")
            return
        DepenseDialog(self, event_id=self.event_id, depense_id=did, on_save=self.refresh_depenses)

    def delete_depense(self):
        did = self.get_selected_id()
        if not did:
            messagebox.showwarning("Sélection", "Sélectionne une dépense à supprimer.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer cette dépense ?"):
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM event_depenses WHERE id=? AND event_id=?", (did, self.event_id))
            conn.commit()
            conn.close()
            logger.info(f"Dépense supprimée id {did}, event_id {self.event_id}")
            self.refresh_depenses()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de la dépense."))

class DepenseDialog(tk.Toplevel):
    def __init__(self, master, event_id, depense_id=None, on_save=None):
        super().__init__(master)
        self.title("Dépense" if depense_id is None else "Éditer dépense")
        self.event_id = event_id
        self.depense_id = depense_id
        self.on_save = on_save
        self.geometry("410x370")
        self.resizable(False, False)

        self.date_var = tk.StringVar()
        self.fournisseur_var = tk.StringVar()
        self.categorie_var = tk.StringVar()
        self.montant_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.justif_var = tk.StringVar()

        tk.Label(self, text="Date (YYYY-MM-DD) :").pack(pady=6)
        tk.Entry(self, textvariable=self.date_var, width=20).pack()
        tk.Label(self, text="Fournisseur :").pack(pady=6)
        tk.Entry(self, textvariable=self.fournisseur_var, width=32).pack()
        tk.Label(self, text="Catégorie :").pack(pady=6)
        tk.Entry(self, textvariable=self.categorie_var, width=28).pack()
        tk.Label(self, text="Montant (€) :").pack(pady=6)
        tk.Entry(self, textvariable=self.montant_var, width=14).pack()
        tk.Label(self, text="Description :").pack(pady=6)
        tk.Entry(self, textvariable=self.desc_var, width=36).pack()
        tk.Label(self, text="Justificatif :").pack(pady=6)
        tk.Entry(self, textvariable=self.justif_var, width=36).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=36, pady=16)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=36, pady=16)

        if self.depense_id:
            self.load_depense()

    def load_depense(self):
        try:
            conn = get_connection()
            dep = conn.execute(
                "SELECT * FROM event_depenses WHERE id=? AND event_id=?",
                (self.depense_id, self.event_id)
            ).fetchone()
            conn.close()
            if dep:
                self.date_var.set(dep["date"])
                self.fournisseur_var.set(dep["fournisseur"] or "")
                self.categorie_var.set(dep["categorie"] or "")
                self.montant_var.set(f"{dep['montant']:.2f}" if dep["montant"] is not None else "")
                self.desc_var.set(dep["description"] or "")
                self.justif_var.set(dep["justificatif"] or "")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement de la dépense."))

    def save(self):
        date = self.date_var.get().strip()
        fournisseur = self.fournisseur_var.get().strip()
        categorie = self.categorie_var.get().strip()
        montant = self.montant_var.get().replace(",", ".").strip()
        desc = self.desc_var.get().strip()
        justif = self.justif_var.get().strip()
        if not date or not montant:
            messagebox.showerror("Erreur", "Date et montant sont obligatoires.")
            return
        try:
            montant_float = float(montant)
        except Exception:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        try:
            conn = get_connection()
            if self.depense_id:
                conn.execute(
                    "UPDATE event_depenses SET date=?, fournisseur=?, categorie=?, montant=?, description=?, justificatif=? WHERE id=? AND event_id=?",
                    (date, fournisseur, categorie, montant_float, desc, justif, self.depense_id, self.event_id)
                )
            else:
                conn.execute(
                    "INSERT INTO event_depenses (event_id, date, fournisseur, categorie, montant, description, justificatif) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.event_id, date, fournisseur, categorie, montant_float, desc, justif)
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de la dépense."))