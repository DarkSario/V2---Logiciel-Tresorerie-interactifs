import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox
from db.db import get_connection
from utils.error_handler import handle_errors

class DepenseDialog(tk.Toplevel):
    """
    Fenêtre générique d'ajout/édition de dépense, ultra-paramétrable.
    Voir l'exemple d'utilisation dans les modules.
    """
    def __init__(self, master, table, depense_id=None, event_id=None, on_save=None, fields=None,
                 module_choices=None, fournisseur_choices=None, membre_choices=None):
        super().__init__(master)
        self.title("Dépense" if depense_id is None else "Éditer la dépense")
        self.table = table
        self.depense_id = depense_id
        self.event_id = event_id
        self.on_save = on_save
        self.fields = fields or {}
        self.module_choices = module_choices or [("", "Aucun")]
        self.fournisseur_choices = fournisseur_choices or []
        self.membre_choices = membre_choices or []
        self.geometry("600x520")
        self.resizable(False, False)

        frame = tk.Frame(self)
        frame.pack(padx=18, pady=12, fill="both", expand=True)
        self.vars = {}

        row = 0
        if self.fields.get("categorie", False):
            tk.Label(frame, text="Catégorie :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["categorie"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["categorie"], width=32).grid(row=row, column=1, sticky="ew"); row += 1
        if self.fields.get("description", False):
            tk.Label(frame, text="Description :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["description"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["description"], width=32).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("module_id", False):
            tk.Label(frame, text="Module lié :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["module_id"] = tk.StringVar()
            module_menu = ttk.Combobox(frame, textvariable=self.vars["module_id"], state="readonly")
            module_menu['values'] = [n for _, n in self.module_choices]
            module_menu.current(0)
            module_menu.grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("montant", False):
            tk.Label(frame, text="Montant (€) :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["montant"] = tk.StringVar(value="0.0")
            tk.Entry(frame, textvariable=self.vars["montant"], width=20).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("fournisseur", False):
            tk.Label(frame, text="Fournisseur :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["fournisseur"] = tk.StringVar()
            fournisseur_menu = ttk.Combobox(frame, textvariable=self.vars["fournisseur"], values=self.fournisseur_choices)
            fournisseur_menu.grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("date_depense", False):
            tk.Label(frame, text="Date de la dépense :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["date_depense"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["date_depense"], width=18).grid(row=row, column=1, sticky="ew"); row += 1
        if self.fields.get("date", False):
            tk.Label(frame, text="Date :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["date"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["date"], width=18).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("echeance", False):
            tk.Label(frame, text="Échéance :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["echeance"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["echeance"], width=18).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("paye_par", False):
            tk.Label(frame, text="Payé par :").grid(row=row, column=0, sticky="w", pady=4)
            self.paye_par_var = tk.StringVar(value="Association")
            paye_frame = tk.Frame(frame)
            paye_frame.grid(row=row, column=1, sticky="w")
            tk.Radiobutton(paye_frame, text="Association", variable=self.paye_par_var, value="Association", command=self.toggle_paye_par).pack(side=tk.LEFT)
            tk.Radiobutton(paye_frame, text="Membre", variable=self.paye_par_var, value="Membre", command=self.toggle_paye_par).pack(side=tk.LEFT)
            row += 1

            self.statut_reglement_var = tk.StringVar(value="Réglé")
            self.statut_remb_var = tk.StringVar(value="Non remboursé")
            self.statut_reglement_frame = tk.Frame(frame)
            tk.Label(self.statut_reglement_frame, text="Statut règlement :").pack(side=tk.LEFT)
            ttk.Combobox(self.statut_reglement_frame, textvariable=self.statut_reglement_var, values=["Réglé", "Non réglé"], state="readonly", width=14).pack(side=tk.LEFT)
            self.statut_reglement_frame.grid(row=row, column=1, sticky="w")
            self.statut_remb_frame = tk.Frame(frame)
            tk.Label(self.statut_remb_frame, text="Statut remboursement :").pack(side=tk.LEFT)
            ttk.Combobox(self.statut_remb_frame, textvariable=self.statut_remb_var, values=["Non remboursé", "Remboursé"], state="readonly", width=16).pack(side=tk.LEFT)
            self.statut_remb_frame.grid(row=row, column=1, sticky="w")
            self.statut_remb_frame.grid_remove()
            row += 1

            self.membre_var = tk.StringVar()
            self.membre_frame = tk.Frame(frame)
            tk.Label(self.membre_frame, text="Membre :").pack(side=tk.LEFT)
            self.membre_menu = ttk.Combobox(self.membre_frame, textvariable=self.membre_var, values=[n for _, n in self.membre_choices], state="readonly", width=16)
            self.membre_menu.pack(side=tk.LEFT)
            self.membre_frame.grid(row=row, column=1, sticky="w")
            self.membre_frame.grid_remove()
            row += 1

        if self.fields.get("moyen_paiement", False):
            tk.Label(frame, text="Moyen de paiement :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["moyen_paiement"] = tk.StringVar()
            moyen_menu = ttk.Combobox(frame, textvariable=self.vars["moyen_paiement"], values=["Espèces", "Chèque", "Virement", "Prélèvement", "Carte bancaire", "Carte Asso"], state="readonly")
            moyen_menu.grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("numero_cheque", False):
            tk.Label(frame, text="Numéro de chèque :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["numero_cheque"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["numero_cheque"], width=20).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("numero_facture", False):
            tk.Label(frame, text="Numéro de facture :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["numero_facture"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["numero_facture"], width=20).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("justificatif", False):
            tk.Label(frame, text="Justificatif :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["justificatif"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["justificatif"], width=28).grid(row=row, column=1, sticky="ew"); row += 1

        if self.fields.get("commentaire", False):
            tk.Label(frame, text="Commentaire :").grid(row=row, column=0, sticky="w", pady=4)
            self.vars["commentaire"] = tk.StringVar()
            tk.Entry(frame, textvariable=self.vars["commentaire"], width=50).grid(row=row, column=1, sticky="ew"); row += 1

        btns = tk.Frame(self)
        btns.pack(pady=18)
        tk.Button(btns, text="Enregistrer", command=self.save, width=15).pack(side=tk.LEFT, padx=14)
        tk.Button(btns, text="Annuler", command=self.destroy, width=15).pack(side=tk.RIGHT, padx=14)

        self.load_data()
        if self.fields.get("paye_par", False):
            self.toggle_paye_par()

    def toggle_paye_par(self):
        if self.paye_par_var.get() == "Membre":
            self.membre_frame.grid()
            self.statut_remb_frame.grid()
            self.statut_reglement_frame.grid_remove()
        else:
            self.membre_frame.grid_remove()
            self.statut_remb_frame.grid_remove()
            self.statut_reglement_frame.grid()

    def load_data(self):
        if not self.depense_id:
            return
        conn = get_connection()
        try:
            row = conn.execute(f"SELECT * FROM {self.table} WHERE id=?", (self.depense_id,)).fetchone()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement dépense: {e}")
            conn.close()
            return
        conn.close()
        if not row:
            return
        for k in self.vars:
            self.vars[k].set(row[k] if k in row.keys() else "")
        if self.fields.get("paye_par", False):
            self.paye_par_var.set(row["paye_par"] if "paye_par" in row.keys() else "Association")
            self.statut_reglement_var.set(row["statut_reglement"] if "statut_reglement" in row.keys() else "Réglé")
            self.statut_remb_var.set(row["statut_remboursement"] if "statut_remboursement" in row.keys() else "Non remboursé")
            if "membre_id" in row.keys() and row["membre_id"] and self.membre_choices:
                for i, (mid, name) in enumerate(self.membre_choices):
                    if mid and int(mid) == row["membre_id"]:
                        self.membre_menu.current(i)
                        break

    @handle_errors
    def save(self):
        # Champs obligatoires
        if self.fields.get("categorie") and not self.vars["categorie"].get().strip():
            messagebox.showerror("Erreur", "Catégorie obligatoire.")
            return
        if self.fields.get("description") and not self.vars["description"].get().strip():
            messagebox.showerror("Erreur", "Description obligatoire.")
            return
        if self.fields.get("montant"):
            try:
                montant = float(self.vars["montant"].get().replace(",", "."))
                if montant <= 0:
                    raise Exception
            except Exception:
                messagebox.showerror("Erreur", "Montant invalide.")
                return
        # Champs date obligatoires (corrige IntegrityError)
        # Pour depenses_diverses ou depenses_regulieres, la clé est souvent "date_depense"
        if (self.table in ("depenses_diverses", "depenses_regulieres")):
            date_val = self.vars.get("date_depense", self.vars.get("date", None))
            if date_val is None or not date_val.get().strip():
                messagebox.showerror("Erreur", "La date de la dépense est obligatoire.")
                return
        if self.fields.get("date") and not self.vars["date"].get().strip():
            messagebox.showerror("Erreur", "La date est obligatoire.")
            return

        values = {}
        for k, var in self.vars.items():
            values[k] = var.get().strip()
            if k == "montant":
                values[k] = float(values[k].replace(",", "."))

        if self.fields.get("paye_par", False):
            values["paye_par"] = self.paye_par_var.get()
            values["statut_remboursement"] = self.statut_remb_var.get() if self.paye_par_var.get() == "Membre" else ""
            values["statut_reglement"] = self.statut_reglement_var.get() if self.paye_par_var.get() == "Association" else ""
            if self.paye_par_var.get() == "Membre" and self.membre_choices:
                idx = self.membre_menu.current()
                values["membre_id"] = self.membre_choices[idx][0] if idx >= 0 else None
            else:
                values["membre_id"] = None

        if self.event_id is not None:
            values["event_id"] = self.event_id

        # Correction pour mapping date_depense vers date (pour depenses_regulieres)
        if self.table == "depenses_regulieres":
            if "date_depense" in values and "date" not in values:
                values["date"] = values.pop("date_depense")

        conn = get_connection()
        try:
            if self.depense_id:
                sets = ", ".join([f"{k}=?" for k in values])
                req = f"UPDATE {self.table} SET {sets} WHERE id=?"
                conn.execute(req, list(values.values()) + [self.depense_id])
            else:
                champs = ", ".join(values.keys())
                q = ", ".join(["?"] * len(values))
                req = f"INSERT INTO {self.table} ({champs}) VALUES ({q})"
                conn.execute(req, list(values.values()))
            conn.commit()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Erreur", f"Erreur d'intégrité : {e}")
            return
        except sqlite3.OperationalError as e:
            messagebox.showerror("Erreur", f"Erreur opérationnelle : {e}")
            return
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()