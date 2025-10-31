import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection
from dialogs.depense_dialog import DepenseDialog

class DepensesRegulieresModule:
    def __init__(self, master):
        self.columns = (
            "id", "categorie", "module_id", "montant", "fournisseur", "date_depense",
            "paye_par", "membre_id", "statut_remboursement", "statut_reglement",
            "moyen_paiement", "numero_cheque", "numero_facture", "commentaire"
        )
        self.top = tk.Toplevel(master)
        self.top.title("Dépenses Régulières")
        self.top.geometry("900x500")
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        self.tree = ttk.Treeview(self.top, columns=self.columns, show="headings")
        headers = [
            ("id", "ID"), ("categorie", "Catégorie"), ("module_id", "Module lié"),
            ("montant", "Montant (€)"), ("fournisseur", "Fournisseur"),
            ("date_depense", "Date de la dépense"),
            ("paye_par", "Payé par"), ("membre_id", "Membre"),
            ("statut_remboursement", "Statut remboursement"),
            ("statut_reglement", "Statut règlement"),
            ("moyen_paiement", "Moyen paiement"), ("numero_cheque", "N° chèque"),
            ("numero_facture", "N° facture"), ("commentaire", "Commentaire")
        ]
        for col, text in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="Ajouter Dépense Régulière", command=self.add_depense).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Éditer sélection", command=self.edit_depense).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Supprimer sélection", command=self.delete_selected).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=8)

    def get_module_choices(self):
        conn = get_connection()
        modules = conn.execute("SELECT id, nom_module FROM event_modules ORDER BY nom_module").fetchall()
        conn.close()
        return [("", "Aucun")] + [(str(m["id"]), m["nom_module"]) for m in modules]

    def get_fournisseur_choices(self):
        conn = get_connection()
        fournisseurs = conn.execute("SELECT name FROM fournisseurs ORDER BY name").fetchall()
        conn.close()
        return [f["name"] for f in fournisseurs]

    def get_membre_choices(self):
        conn = get_connection()
        membres = conn.execute("SELECT id, name, prenom FROM membres ORDER BY name, prenom").fetchall()
        conn.close()
        return [(str(m["id"]), f"{m['prenom']} {m['name']}") for m in membres]

    def add_depense(self):
        DepenseDialog(
            self.top,
            table="depenses_regulieres",
            module_choices=self.get_module_choices(),
            fournisseur_choices=self.get_fournisseur_choices(),
            membre_choices=self.get_membre_choices(),
            on_save=self.refresh_list,
            fields={
                "categorie": True,
                "module_id": True,
                "montant": True,
                "fournisseur": True,
                "date_depense": True,
                "paye_par": True,
                "moyen_paiement": True,
                "numero_cheque": True,
                "numero_facture": True,
                "commentaire": True,
            }
        )

    def edit_depense(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne à éditer.")
            return
        item = self.tree.item(sel[0])
        depense_id = item["values"][0]
        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment modifier cette dépense ?"):
            return
        DepenseDialog(
            self.top,
            table="depenses_regulieres",
            depense_id=depense_id,
            module_choices=self.get_module_choices(),
            fournisseur_choices=self.get_fournisseur_choices(),
            membre_choices=self.get_membre_choices(),
            on_save=self.refresh_list,
            fields={
                "categorie": True,
                "module_id": True,
                "montant": True,
                "fournisseur": True,
                "date_depense": True,
                "paye_par": True,
                "moyen_paiement": True,
                "numero_cheque": True,
                "numero_facture": True,
                "commentaire": True,
            }
        )

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne à supprimer.")
            return
        item = self.tree.item(sel[0])
        id_ = item["values"][0]
        if not messagebox.askyesno("Confirmer", "Supprimer cette dépense régulière ?"):
            return
        conn = get_connection()
        conn.execute("DELETE FROM depenses_regulieres WHERE id = ?", (id_,))
        conn.commit()
        conn.close()
        self.refresh_list()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        items = conn.execute(
            "SELECT id, categorie, module_id, montant, fournisseur, date_depense, paye_par, membre_id, statut_remboursement, statut_reglement, moyen_paiement, numero_cheque, numero_facture, commentaire FROM depenses_regulieres ORDER BY date_depense DESC, id DESC"
        ).fetchall()
        for item in items:
            module_name = ""
            membre_nom = ""
            if item["module_id"]:
                mod = conn.execute("SELECT nom_module FROM event_modules WHERE id=?", (item["module_id"],)).fetchone()
                if mod:
                    module_name = mod["nom_module"]
            if item["membre_id"]:
                mem = conn.execute("SELECT name, prenom FROM membres WHERE id=?", (item["membre_id"],)).fetchone()
                if mem:
                    membre_nom = f"{mem['prenom']} {mem['name']}"
            self.tree.insert(
                "", "end",
                values=[
                    item["id"], item["categorie"], module_name, f"{item['montant']:.2f}",
                    item["fournisseur"] or "", item["date_depense"] or "", item["paye_par"] or "",
                    membre_nom, item["statut_remboursement"] or "", item["statut_reglement"] or "",
                    item["moyen_paiement"] or "", item["numero_cheque"] or "",
                    item["numero_facture"] or "", item["commentaire"] or ""
                ]
            )
        conn.close()