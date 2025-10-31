import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import modules.buvette_db as db

# -------- DIALOGUES ARTICLES ----------
class ArticleDialog(tk.Toplevel):
    def __init__(self, master, article_id=None, on_save=None):
        super().__init__(master)
        self.title("Article buvette")
        self.geometry("350x400")
        self.on_save = on_save
        self.article_id = article_id

        self.nom_var = tk.StringVar()
        self.categorie_var = tk.StringVar()
        self.unite_var = tk.StringVar()
        self.contenance_var = tk.StringVar()
        self.comment_var = tk.StringVar()

        tk.Label(self, text="Name :").pack(pady=4)
        tk.Entry(self, textvariable=self.nom_var, width=30).pack()
        tk.Label(self, text="Catégorie :").pack(pady=4)
        tk.Entry(self, textvariable=self.categorie_var, width=25).pack()
        tk.Label(self, text="Unité (ex: canette, bouteille...) :").pack(pady=4)
        tk.Entry(self, textvariable=self.unite_var, width=18).pack()
        tk.Label(self, text="Contenance :").pack(pady=4)
        contenance_options = ["0.25L", "0.33L", "0.5L", "0.75L", "1L", "1.5L", "2L"]
        self.contenance_cb = ttk.Combobox(self, textvariable=self.contenance_var, state="readonly", width=10)
        self.contenance_cb["values"] = contenance_options
        self.contenance_cb.pack()
        tk.Label(self, text="Commentaire :").pack(pady=4)
        tk.Entry(self, textvariable=self.comment_var, width=35).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=14)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=12)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=12)

        if article_id:
            self.load_article()

    def load_article(self):
        r = db.get_article_by_id(self.article_id)
        if r:
            self.nom_var.set(r["name"])
            self.categorie_var.set(r["categorie"])
            self.unite_var.set(r["unite"])
            self.contenance_var.set(r["contenance"] if r["contenance"] else "")
            self.comment_var.set(r["commentaire"])

    def save(self):
        name = self.nom_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom de l'article est obligatoire.")
            return
        categorie = self.categorie_var.get().strip()
        unite = self.unite_var.get().strip()
        contenance = self.contenance_var.get().strip()
        comment = self.comment_var.get().strip()
        if self.article_id:
            db.update_article(self.article_id, name, categorie, unite, comment, contenance)
        else:
            db.insert_article(name, categorie, unite, comment, contenance)
        if self.on_save:
            self.on_save()
        self.destroy()

# -------- DIALOGUES ACHATS ----------
class AchatDialog(tk.Toplevel):
    def __init__(self, master, achat_id=None, on_save=None):
        super().__init__(master)
        self.title("Achat buvette")
        self.geometry("420x440")
        self.on_save = on_save
        self.achat_id = achat_id

        self.article_var = tk.StringVar()
        self.date_var = tk.StringVar(value=str(date.today()))
        self.qte_var = tk.IntVar()
        self.pu_var = tk.DoubleVar()
        self.fournisseur_var = tk.StringVar()
        self.facture_var = tk.StringVar()
        self.exercice_var = tk.StringVar()
        self.contenance_display_var = tk.StringVar()

        tk.Label(self, text="Article :").pack(pady=4)
        article_list = db.list_articles_names()
        self.articles_dict = {f"{r['name']} (id={r['id']})": r["id"] for r in article_list}
        self.articles_contenance = {f"{r['name']} (id={r['id']})": r["contenance"] for r in article_list}
        self.article_cb = ttk.Combobox(self, textvariable=self.article_var, state="readonly", width=28)
        self.article_cb["values"] = list(self.articles_dict.keys())
        self.article_cb.pack()

        tk.Label(self, text="Contenance :").pack(pady=4)
        self.contenance_display = tk.Entry(self, textvariable=self.contenance_display_var, width=14, state="readonly")
        self.contenance_display.pack()

        def update_contenance_display(*args):
            selected_article = self.article_var.get()
            contenance_val = self.articles_contenance.get(selected_article, "")
            self.contenance_display_var.set(contenance_val if contenance_val else "")
        self.article_var.trace_add("write", update_contenance_display)
        update_contenance_display()

        tk.Label(self, text="Date achat :").pack(pady=4)
        tk.Entry(self, textvariable=self.date_var).pack()
        tk.Label(self, text="Quantité :").pack(pady=4)
        tk.Entry(self, textvariable=self.qte_var).pack()
        tk.Label(self, text="Prix unitaire (€) :").pack(pady=4)
        tk.Entry(self, textvariable=self.pu_var).pack()
        tk.Label(self, text="Fournisseur :").pack(pady=4)
        tk.Entry(self, textvariable=self.fournisseur_var).pack()
        tk.Label(self, text="Facture n° :").pack(pady=4)
        tk.Entry(self, textvariable=self.facture_var).pack()
        tk.Label(self, text="Exercice :").pack(pady=4)
        tk.Entry(self, textvariable=self.exercice_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if achat_id:
            self.load_achat()

    def load_achat(self):
        r = db.get_achat_by_id(self.achat_id)
        if r:
            article_key = None
            for k, v in self.articles_dict.items():
                if v == r["article_id"]:
                    article_key = k
                    break
            if article_key:
                self.article_var.set(article_key)
                self.contenance_display_var.set(self.articles_contenance.get(article_key, ""))
            self.date_var.set(r["date_achat"])
            self.qte_var.set(r["quantite"])
            self.pu_var.set(r["prix_unitaire"])
            self.fournisseur_var.set(r["fournisseur"])
            self.facture_var.set(r["facture"])
            self.exercice_var.set(r["exercice"])

    def save(self):
        article_key = self.article_var.get()
        if not article_key or article_key not in self.articles_dict:
            messagebox.showerror("Erreur", "Article obligatoire.")
            return
        article_id = self.articles_dict[article_key]
        champs = (
            article_id,
            self.date_var.get(),
            self.qte_var.get(),
            self.pu_var.get(),
            self.fournisseur_var.get(),
            self.facture_var.get(),
            self.exercice_var.get()
        )
        if self.achat_id:
            db.update_achat(self.achat_id, *champs)
        else:
            db.insert_achat(*champs)
        if self.on_save:
            self.on_save()
        self.destroy()

# -------- DIALOGUES MOUVEMENTS ----------
class MouvementDialog(tk.Toplevel):
    def __init__(self, master, on_done, mvt=None):
        super().__init__(master)
        self.title("Mouvement")
        self.on_done = on_done
        self.mvt = mvt

        self.article_var = tk.StringVar()
        self.date_var = tk.StringVar(value=mvt["date"] if mvt else "")
        self.type_var = tk.StringVar(value=mvt["type"] if mvt else "")
        self.quantite_var = tk.IntVar(value=mvt["quantite"] if mvt else 0)
        self.comment_var = tk.StringVar(value=mvt["commentaire"] if mvt else "")
        self.contenance_display_var = tk.StringVar()

        tk.Label(self, text="Article :").pack(pady=4)
        article_list = db.list_articles_names()
        self.articles_dict = {f"{r['name']} (id={r['id']})": r["id"] for r in article_list}
        self.articles_contenance = {f"{r['name']} (id={r['id']})": r["contenance"] for r in article_list}
        self.article_cb = ttk.Combobox(self, textvariable=self.article_var, state="readonly", width=28)
        self.article_cb["values"] = list(self.articles_dict.keys())
        self.article_cb.pack()

        tk.Label(self, text="Contenance :").pack(pady=4)
        self.contenance_display = tk.Entry(self, textvariable=self.contenance_display_var, width=14, state="readonly")
        self.contenance_display.pack()

        def update_contenance_display(*args):
            selected_article = self.article_var.get()
            contenance_val = self.articles_contenance.get(selected_article, "")
            self.contenance_display_var.set(contenance_val if contenance_val else "")
        self.article_var.trace_add("write", update_contenance_display)
        update_contenance_display()

        tk.Label(self, text="Date :").pack(pady=4)
        tk.Entry(self, textvariable=self.date_var).pack()
        tk.Label(self, text="Type (entrée/sortie) :").pack(pady=4)
        tk.Entry(self, textvariable=self.type_var).pack()
        tk.Label(self, text="Quantité :").pack(pady=4)
        tk.Entry(self, textvariable=self.quantite_var).pack()
        tk.Label(self, text="Commentaire :").pack(pady=4)
        tk.Entry(self, textvariable=self.comment_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if mvt:
            self.load_mvt()

    def load_mvt(self):
        if self.mvt:
            article_key = None
            for k, v in self.articles_dict.items():
                if v == self.mvt["article_id"]:
                    article_key = k
                    break
            if article_key:
                self.article_var.set(article_key)
                self.contenance_display_var.set(self.articles_contenance.get(article_key, ""))
            self.date_var.set(self.mvt["date"])
            self.type_var.set(self.mvt["type"])
            self.quantite_var.set(self.mvt["quantite"])
            self.comment_var.set(self.mvt["commentaire"])

    def save(self):
        article_key = self.article_var.get()
        if not article_key or article_key not in self.articles_dict:
            messagebox.showerror("Erreur", "Article obligatoire.")
            return
        article_id = self.articles_dict[article_key]
        date = self.date_var.get()
        type_mvt = self.type_var.get()
        quantite = self.quantite_var.get()
        comment = self.comment_var.get()
        if not date or not article_id or not type_mvt or not quantite:
            messagebox.showwarning("Saisie", "Tous les champs sont obligatoires.")
            return
        try:
            if self.mvt:
                db.update_mouvement(self.mvt["id"], date, article_id, type_mvt, quantite, comment)
            else:
                db.insert_mouvement(date, article_id, type_mvt, quantite, comment)
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement du mouvement : {e}")

# -------- DIALOGUES INVENTAIRE LIGNES ----------
class LigneInventaireDialog(tk.Toplevel):
    def __init__(self, master, on_done, inventaire_id, ligne=None):
        super().__init__(master)
        self.title("Ligne inventaire")
        self.on_done = on_done
        self.inventaire_id = inventaire_id
        self.ligne = ligne

        self.article_var = tk.StringVar()
        self.quantite_var = tk.IntVar(value=ligne["quantite"] if ligne else 0)
        self.comment_var = tk.StringVar(value=ligne["commentaire"] if ligne else "")
        self.contenance_display_var = tk.StringVar()

        tk.Label(self, text="Article :").pack(pady=4)
        article_list = db.list_articles_names()
        self.articles_dict = {f"{r['name']} (id={r['id']})": r["id"] for r in article_list}
        self.articles_contenance = {f"{r['name']} (id={r['id']})": r["contenance"] for r in article_list}
        self.article_cb = ttk.Combobox(self, textvariable=self.article_var, state="readonly", width=28)
        self.article_cb["values"] = list(self.articles_dict.keys())
        self.article_cb.pack()

        tk.Label(self, text="Contenance :").pack(pady=4)
        self.contenance_display = tk.Entry(self, textvariable=self.contenance_display_var, width=14, state="readonly")
        self.contenance_display.pack()

        def update_contenance_display(*args):
            selected_article = self.article_var.get()
            contenance_val = self.articles_contenance.get(selected_article, "")
            self.contenance_display_var.set(contenance_val if contenance_val else "")
        self.article_var.trace_add("write", update_contenance_display)
        update_contenance_display()

        tk.Label(self, text="Quantité :").pack(pady=4)
        tk.Entry(self, textvariable=self.quantite_var).pack()
        tk.Label(self, text="Commentaire :").pack(pady=4)
        tk.Entry(self, textvariable=self.comment_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if ligne:
            self.load_ligne()

    def load_ligne(self):
        if self.ligne:
            article_key = None
            for k, v in self.articles_dict.items():
                if v == self.ligne["article_id"]:
                    article_key = k
                    break
            if article_key:
                self.article_var.set(article_key)
                self.contenance_display_var.set(self.articles_contenance.get(article_key, ""))
            self.quantite_var.set(self.ligne["quantite"])
            self.comment_var.set(self.ligne["commentaire"])

    def save(self):
        article_key = self.article_var.get()
        if not article_key or article_key not in self.articles_dict:
            messagebox.showerror("Erreur", "Article obligatoire.")
            return
        article_id = self.articles_dict[article_key]
        quantite = self.quantite_var.get()
        comment = self.comment_var.get()
        if not article_id:
            messagebox.showwarning("Saisie", "Article obligatoire.")
            return
        try:
            if self.ligne:
                db.update_ligne_inventaire(self.ligne["id"], article_id, quantite, comment)
            else:
                db.insert_ligne_inventaire(self.inventaire_id, article_id, quantite, comment)
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement de la ligne d'inventaire : {e}")