import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import modules.buvette_mouvements_db as db
from modules.db_row_utils import _rows_to_dicts

class MouvementDialog(tk.Toplevel):
    def __init__(self, master, mouvement_id=None, on_save=None):
        super().__init__(master)
        self.title("Mouvement de stock buvette")
        self.geometry("400x420")
        self.on_save = on_save
        self.mouvement_id = mouvement_id

        self.article_var = tk.StringVar()
        self.date_var = tk.StringVar(value=str(date.today()))
        self.type_var = tk.StringVar()
        self.qte_var = tk.IntVar()
        self.motif_var = tk.StringVar()
        self.evt_var = tk.StringVar()

        tk.Label(self, text="Article :").pack(pady=4)
        self.article_cb = ttk.Combobox(self, textvariable=self.article_var, state="readonly", width=28)
        self.articles_dict = {str(r["name"]): r["id"] for r in db.list_articles()}
        self.article_cb["values"] = list(self.articles_dict.keys())
        self.article_cb.pack()

        tk.Label(self, text="Date :").pack(pady=4)
        tk.Entry(self, textvariable=self.date_var).pack()
        tk.Label(self, text="Type mouvement :").pack(pady=4)
        self.type_cb = ttk.Combobox(self, textvariable=self.type_var, state="readonly", width=18)
        self.type_cb["values"] = [
            "casse", "consommation_reunion", "don", "peremption", "autre"
        ]
        self.type_cb.pack()
        tk.Label(self, text="Quantité :").pack(pady=4)
        tk.Entry(self, textvariable=self.qte_var).pack()
        tk.Label(self, text="Motif / commentaire :").pack(pady=4)
        tk.Entry(self, textvariable=self.motif_var).pack()
        tk.Label(self, text="Événement (optionnel) :").pack(pady=4)
        self.evt_cb = ttk.Combobox(self, textvariable=self.evt_var, width=28, state="readonly")
        self.evt_dict = {"": None}
        # Convert Row objects to dicts for safe access
        events = _rows_to_dicts(db.list_events())
        for r in events:
            label = f"{r['id']} - {r['name']}"
            self.evt_dict[label] = r["id"]
        self.evt_cb["values"] = list(self.evt_dict.keys())
        self.evt_cb.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=14)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=12)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=12)

        if mouvement_id:
            self.load_mouvement()

    def load_mouvement(self):
        mvt = db.get_mouvement_by_id(self.mouvement_id)
        if mvt:
            self.article_var.set(self._find_name_by_id(self.articles_dict, mvt["article_id"]))
            self.date_var.set(mvt["date_mouvement"])
            self.type_var.set(mvt["type_mouvement"])
            self.qte_var.set(mvt["quantite"])
            self.motif_var.set(mvt["motif"])
            self.evt_var.set(self._find_name_by_id(self.evt_dict, mvt["event_id"]))

    def _find_name_by_id(self, d, val):
        for k, v in d.items():
            if v == val:
                return k
        return ""

    def save(self):
        nom_article = self.article_var.get()
        if not nom_article or nom_article not in self.articles_dict:
            messagebox.showerror("Erreur", "Article obligatoire.")
            return
        article_id = self.articles_dict[nom_article]
        date_mvt = self.date_var.get()
        type_mvt = self.type_var.get()
        quantite = self.qte_var.get()
        motif = self.motif_var.get()
        evt_label = self.evt_var.get()
        event_id = self.evt_dict.get(evt_label, None)
        if self.mouvement_id:
            db.update_mouvement(self.mouvement_id, article_id, date_mvt, type_mvt, quantite, motif, event_id)
        else:
            db.insert_mouvement(article_id, date_mvt, type_mvt, quantite, motif, event_id)
        if self.on_save:
            self.on_save()
        self.destroy()