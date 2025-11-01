"""
Module de gestion du module Buvette (UI).

MODIFICATIONS APPLIQUÉES (PR corrections buvette - copilot/auto-fix-buvette):
- InventaireDialog: ajout de columnconfigure(1, weight=1) et sticky='ew' pour layout amélioré
- InventaireDialog: remplacement du champ 'Type inventaire' Entry par Combobox (avant/apres/hors_evenement)
- InventaireDialog.save: validation stricte du type d'inventaire
- LignesInventaireDialog.refresh_lignes(): affichage de article_name au lieu de article_id
- LigneInventaireDialog: utilisation de Combobox pour sélectionner un article
- LigneInventaireDialog.save: appel automatique de set_article_stock() après enregistrement pour MAJ immédiate
- MouvementDialog: utilisation de Combobox pour sélectionner un article
- AchatDialog: utilisation de Combobox pour sélectionner un article
- refresh_bilan(): protection des agrégations contre les valeurs None
- BuvetteModule.__init__: appel de ensure_stock_column() au démarrage pour garantir la colonne stock existe
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules.buvette_db import (
    list_articles, insert_article, update_article, delete_article,
    list_achats, insert_achat, update_achat, delete_achat,
    get_article_by_id, get_achat_by_id,
    list_mouvements, insert_mouvement, update_mouvement, delete_mouvement, get_mouvement_by_id,
    list_articles_names, set_article_stock, ensure_stock_column
)
import modules.buvette_inventaire_db as inv_db
from utils.app_logger import get_logger
from utils.error_handler import handle_exception
from utils.db_helpers import row_to_dict, row_get_safe

logger = get_logger("buvette_module")

class BuvetteModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Gestion Buvette")
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Assurer que la colonne 'stock' existe dans buvette_articles (migration non destructive)
        try:
            ensure_stock_column()
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification de la colonne stock: {e}")

        self.create_tab_articles()
        self.create_tab_achats()
        self.create_tab_inventaires()
        self.create_tab_mouvements()
        self.create_tab_bilan()

    # ------------------ TAB ARTICLES ------------------
    def create_tab_articles(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Articles")

        self.articles_tree = ttk.Treeview(frame, columns=("name", "categorie", "unite", "contenance", "purchase_price", "commentaire"), show="headings")
        self.articles_tree.heading("name", text="Name")
        self.articles_tree.heading("categorie", text="Catégorie")
        self.articles_tree.heading("unite", text="Unité")
        self.articles_tree.heading("contenance", text="Contenance")
        self.articles_tree.heading("purchase_price", text="Prix achat/unité (€)")
        self.articles_tree.heading("commentaire", text="Commentaire")
        self.articles_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)

        self.refresh_articles()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        tk.Button(btn_frame, text="Ajouter", command=self.add_article).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Modifier", command=self.edit_article).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Supprimer", command=self.del_article).pack(fill=tk.X, pady=2)

    def refresh_articles(self):
        try:
            for row in self.articles_tree.get_children():
                self.articles_tree.delete(row)
            for a in list_articles():
                # Use safe access helper to tolerate missing columns
                purchase_price = row_get_safe(a, "purchase_price")
                purchase_price_display = ""
                if purchase_price is not None:
                    try:
                        purchase_price_display = f"{float(purchase_price):.2f}"
                    except (ValueError, TypeError):
                        pass
                
                self.articles_tree.insert(
                    "", "end", iid=row_get_safe(a, "id", 0),
                    values=(
                        row_get_safe(a, "name", ""),
                        row_get_safe(a, "categorie", ""),
                        row_get_safe(a, "unite", ""),
                        row_get_safe(a, "contenance", ""),
                        purchase_price_display,
                        row_get_safe(a, "commentaire", "")
                    )
                )
        except Exception as e:
            logger.exception("Error refreshing articles list")
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des articles. Vérifiez que la structure de la base de données est à jour."))

    def add_article(self):
        ArticleDialog(self.top, self.refresh_articles)

    def edit_article(self):
        sel = self.articles_tree.focus()
        if sel:
            article = get_article_by_id(sel)
            ArticleDialog(self.top, self.refresh_articles, article)
        else:
            messagebox.showwarning("Sélection", "Sélectionner un article à modifier.")

    def del_article(self):
        sel = self.articles_tree.focus()
        if sel:
            if messagebox.askyesno("Suppression", "Supprimer cet article ?"):
                try:
                    delete_article(sel)
                    self.refresh_articles()
                except Exception as e:
                    messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de l'article."))
        else:
            messagebox.showwarning("Sélection", "Sélectionner un article à supprimer.")

    # ------------------ TAB ACHATS ------------------
    def create_tab_achats(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Achats")

        self.achats_tree = ttk.Treeview(frame, columns=("article_name", "contenance", "date_achat", "quantite", "prix_unitaire", "fournisseur", "facture", "exercice"), show="headings")
        self.achats_tree.heading("article_name", text="Article")
        self.achats_tree.heading("contenance", text="Contenance")
        self.achats_tree.heading("date_achat", text="Date")
        self.achats_tree.heading("quantite", text="Quantité")
        self.achats_tree.heading("prix_unitaire", text="PU (€)")
        self.achats_tree.heading("fournisseur", text="Fournisseur")
        self.achats_tree.heading("facture", text="Facture")
        self.achats_tree.heading("exercice", text="Exercice")
        self.achats_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)

        self.refresh_achats()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        tk.Button(btn_frame, text="Ajouter", command=self.add_achat).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Modifier", command=self.edit_achat).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Supprimer", command=self.del_achat).pack(fill=tk.X, pady=2)

    def refresh_achats(self):
        try:
            for row in self.achats_tree.get_children():
                self.achats_tree.delete(row)
            for ach in list_achats():
                self.achats_tree.insert(
                    "", "end", iid=ach["id"],
                    values=(
                        ach["article_name"],
                        ach["article_contenance"] if "article_contenance" in ach.keys() and ach["article_contenance"] is not None else "",
                        ach["date_achat"],
                        ach["quantite"],
                        ach["prix_unitaire"],
                        ach["fournisseur"],
                        ach["facture"],
                        ach["exercice"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des achats."))

    def add_achat(self):
        AchatDialog(self.top, self.refresh_achats)

    def edit_achat(self):
        sel = self.achats_tree.focus()
        if sel:
            achat = get_achat_by_id(sel)
            AchatDialog(self.top, self.refresh_achats, achat)
        else:
            messagebox.showwarning("Sélection", "Sélectionner un achat à modifier.")

    def del_achat(self):
        sel = self.achats_tree.focus()
        if sel:
            if messagebox.askyesno("Suppression", "Supprimer cet achat ?"):
                try:
                    delete_achat(sel)
                    self.refresh_achats()
                except Exception as e:
                    messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de l'achat."))
        else:
            messagebox.showwarning("Sélection", "Sélectionner un achat à supprimer.")

    # ------------------ TAB INVENTAIRES ------------------
    def create_tab_inventaires(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Inventaires")

        self.inventaires_tree = ttk.Treeview(frame, columns=("date", "nom", "commentaire"), show="headings")
        self.inventaires_tree.heading("date", text="Date")
        self.inventaires_tree.heading("nom", text="Nom inventaire")
        self.inventaires_tree.heading("commentaire", text="Commentaire")
        self.inventaires_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)

        self.refresh_inventaires()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        # Removed simple 'Ajouter' button - functionality replaced by detailed inventory dialog below
        tk.Button(btn_frame, text="Modifier", command=self.edit_inventaire).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Supprimer", command=self.del_inventaire).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Voir lignes", command=self.show_lignes_inventaire).pack(fill=tk.X, pady=2)
        # Separator
        ttk.Separator(btn_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        # New detailed inventory button (replaces simple "Ajouter")
        tk.Button(btn_frame, text="Nouvel inventaire\ndétaillé", command=self.add_detailed_inventaire, bg="#4CAF50", fg="white").pack(fill=tk.X, pady=2)

    def refresh_inventaires(self):
        try:
            for row in self.inventaires_tree.get_children():
                self.inventaires_tree.delete(row)
            for inv in inv_db.list_inventaires():
                self.inventaires_tree.insert("", "end", iid=inv["id"], values=(inv["date_inventaire"], inv["type_inventaire"], inv["commentaire"]))
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des inventaires."))

    def add_inventaire(self):
        InventaireDialog(self.top, self.refresh_inventaires)

    def edit_inventaire(self):
        """Open the detailed inventory dialog for editing an existing inventory."""
        sel = self.inventaires_tree.focus()
        if sel:
            inv = None
            for i in inv_db.list_inventaires():
                if str(i["id"]) == str(sel):
                    inv = i
                    break
            if inv:
                # Open detailed dialog with edit mode
                from ui.inventory_lines_dialog import InventoryLinesDialog
                dialog = InventoryLinesDialog(self.top, edit_inventory=inv)
                # Make dialog modal and wait for it to close before refreshing
                dialog.grab_set()
                self.top.wait_window(dialog)
                # Refresh inventory list after dialog closes
                self.refresh_inventaires()
        else:
            messagebox.showwarning("Sélection", "Sélectionner un inventaire à modifier.")

    def del_inventaire(self):
        sel = self.inventaires_tree.focus()
        if sel:
            if messagebox.askyesno("Suppression", "Supprimer cet inventaire ?"):
                try:
                    inv_db.delete_inventaire(sel)
                    self.refresh_inventaires()
                except Exception as e:
                    messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de l'inventaire."))
        else:
            messagebox.showwarning("Sélection", "Sélectionner un inventaire à supprimer.")

    def show_lignes_inventaire(self):
        sel = self.inventaires_tree.focus()
        if sel:
            LignesInventaireDialog(self.top, sel)
        else:
            messagebox.showwarning("Sélection", "Sélectionner un inventaire pour voir les lignes.")

    def add_detailed_inventaire(self):
        """Open the detailed inventory dialog."""
        from ui.inventory_lines_dialog import InventoryLinesDialog
        dialog = InventoryLinesDialog(self.top)
        # Make dialog modal and wait for it to close before refreshing
        dialog.grab_set()
        self.top.wait_window(dialog)
        # Refresh inventory list after dialog closes
        self.refresh_inventaires()

    # ------------------ TAB MOUVEMENTS ------------------
    def create_tab_mouvements(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mouvements")

        self.mouvements_tree = ttk.Treeview(frame, columns=("date", "article_name", "contenance", "type", "quantite", "commentaire"), show="headings")
        self.mouvements_tree.heading("date", text="Date")
        self.mouvements_tree.heading("article_name", text="Article")
        self.mouvements_tree.heading("contenance", text="Contenance")
        self.mouvements_tree.heading("type", text="Type")
        self.mouvements_tree.heading("quantite", text="Quantité")
        self.mouvements_tree.heading("commentaire", text="Commentaire")
        self.mouvements_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=3, pady=3)

        self.refresh_mouvements()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        tk.Button(btn_frame, text="Ajouter", command=self.add_mouvement).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Modifier", command=self.edit_mouvement).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Supprimer", command=self.del_mouvement).pack(fill=tk.X, pady=2)

    def refresh_mouvements(self):
        try:
            for row in self.mouvements_tree.get_children():
                self.mouvements_tree.delete(row)
            for mvt in list_mouvements():
                self.mouvements_tree.insert(
                    "", "end", iid=mvt["id"],
                    values=(mvt["date"], mvt["article_name"], mvt["article_contenance"] if "article_contenance" in mvt.keys() and mvt["article_contenance"] is not None else "", mvt["type"], mvt["quantite"], mvt["commentaire"])
                )
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des mouvements."))

    def add_mouvement(self):
        MouvementDialog(self.top, self.refresh_mouvements)

    def edit_mouvement(self):
        sel = self.mouvements_tree.focus()
        if sel:
            mvt = get_mouvement_by_id(sel)
            MouvementDialog(self.top, self.refresh_mouvements, mvt)
        else:
            messagebox.showwarning("Sélection", "Sélectionner un mouvement à modifier.")

    def del_mouvement(self):
        sel = self.mouvements_tree.focus()
        if sel:
            if messagebox.askyesno("Suppression", "Supprimer ce mouvement ?"):
                try:
                    delete_mouvement(sel)
                    self.refresh_mouvements()
                except Exception as e:
                    messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression du mouvement."))
        else:
            messagebox.showwarning("Sélection", "Sélectionner un mouvement à supprimer.")

    # ------------------ TAB BILAN ------------------
    def create_tab_bilan(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Bilan")

        self.bilan_text = tk.Text(frame, height=26, width=120, wrap=tk.WORD)
        self.bilan_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        tk.Button(frame, text="Rafraîchir bilan", command=self.refresh_bilan).pack(pady=3)
        self.refresh_bilan()

    def refresh_bilan(self):
        try:
            # Protection contre None pour les agrégations
            achats = sum(int(a["quantite"] or 0) for a in list_achats())
            mvts_entree = sum(int(m["quantite"] or 0) for m in list_mouvements() if m["type"] == "entrée")
            mvts_sortie = sum(int(m["quantite"] or 0) for m in list_mouvements() if m["type"] == "sortie")
            invs = sum(int(l["quantite"] or 0) for inv in inv_db.list_inventaires() for l in inv_db.list_lignes_inventaire(inv["id"]))
            txt = f"Total achats : {achats}\n"
            txt += f"Total mouvements entrée : {mvts_entree}\n"
            txt += f"Total mouvements sortie : {mvts_sortie}\n"
            txt += f"Total inventaire (toutes lignes) : {invs}\n"
            self.bilan_text.delete(1.0, tk.END)
            self.bilan_text.insert(tk.END, txt)
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du calcul du bilan."))

# ------------------ DIALOGS ------------------

class ArticleDialog(tk.Toplevel):
    def __init__(self, master, on_done, article=None):
        super().__init__(master)
        self.title("Article")
        self.on_done = on_done
        self.article = article

        tk.Label(self, text="Name").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar(value=article["name"] if article else "")
        tk.Entry(self, textvariable=self.name_var).grid(row=0, column=1)

        tk.Label(self, text="Catégorie").grid(row=1, column=0, sticky="w")
        self.categorie_var = tk.StringVar(value=article["categorie"] if article else "")
        tk.Entry(self, textvariable=self.categorie_var).grid(row=1, column=1)

        tk.Label(self, text="Unité").grid(row=2, column=0, sticky="w")
        self.unite_var = tk.StringVar(value=article["unite"] if article else "")
        tk.Entry(self, textvariable=self.unite_var).grid(row=2, column=1)

        tk.Label(self, text="Contenance").grid(row=3, column=0, sticky="w")
        contenance_options = ["0.25L", "0.33L", "0.5L", "0.75L", "1L", "1.5L", "2L"]
        self.contenance_var = tk.StringVar(value=article["contenance"] if article and "contenance" in article else contenance_options[0])
        ttk.Combobox(self, textvariable=self.contenance_var, values=contenance_options, state="readonly").grid(row=3, column=1)

        tk.Label(self, text="Commentaire").grid(row=4, column=0, sticky="w")
        self.commentaire_var = tk.StringVar(value=article["commentaire"] if article else "")
        tk.Entry(self, textvariable=self.commentaire_var).grid(row=4, column=1)

        tk.Button(self, text="Enregistrer", command=self.save).grid(row=5, column=0, columnspan=2, pady=8)

    def save(self):
        name = self.name_var.get()
        categorie = self.categorie_var.get()
        unite = self.unite_var.get()
        contenance = self.contenance_var.get()
        commentaire = self.commentaire_var.get()
        if not name:
            messagebox.showwarning("Saisie", "Le nom est obligatoire.")
            return
        try:
            if self.article:
                update_article(self.article["id"], name, categorie, unite, commentaire, contenance)
            else:
                insert_article(name, categorie, unite, commentaire, contenance)
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de l'article."))

# ... autres classes inchangées ...
class AchatDialog(tk.Toplevel):
    def __init__(self, master, on_done, achat=None):
        super().__init__(master)
        self.title("Achat")
        self.on_done = on_done
        self.achat = achat

        from modules.buvette_db import list_articles_names
        tk.Label(self, text="Article").grid(row=0, column=0, sticky="w")
        articles = list_articles_names()
        self.article_options = [f"{a['name']} (id={a['id']})" for a in articles]
        self.article_id_map = {f"{a['name']} (id={a['id']})": a['id'] for a in articles}
        self.article_contenance_map = {f"{a['name']} (id={a['id']})": a['contenance'] for a in articles}
        default_article = None
        if achat:
            for opt in self.article_options:
                if self.article_id_map[opt] == achat["article_id"]:
                    default_article = opt
                    break
        self.article_var = tk.StringVar(value=default_article if default_article else (self.article_options[0] if self.article_options else ""))
        self.article_combo = ttk.Combobox(self, textvariable=self.article_var, values=self.article_options, state="readonly")
        self.article_combo.grid(row=0, column=1)

        # Affichage de la contenance de l'article sélectionné (lecture seule)
        tk.Label(self, text="Contenance").grid(row=1, column=0, sticky="w")
        self.contenance_var = tk.StringVar(value=self.article_contenance_map.get(self.article_var.get(), ""))
        self.contenance_entry = tk.Entry(self, textvariable=self.contenance_var, state="readonly")
        self.contenance_entry.grid(row=1, column=1)

        def update_contenance(*_):
            self.contenance_var.set(self.article_contenance_map.get(self.article_var.get(), ""))
        self.article_var.trace_add("write", update_contenance)

        tk.Label(self, text="Date").grid(row=2, column=0, sticky="w")
        self.date_var = tk.StringVar(value=achat["date_achat"] if achat else "")
        tk.Entry(self, textvariable=self.date_var).grid(row=2, column=1)

        tk.Label(self, text="Quantité").grid(row=3, column=0, sticky="w")
        self.quantite_var = tk.IntVar(value=achat["quantite"] if achat else 0)
        tk.Entry(self, textvariable=self.quantite_var).grid(row=3, column=1)

        tk.Label(self, text="PU (€)").grid(row=4, column=0, sticky="w")
        self.prix_unitaire_var = tk.DoubleVar(value=achat["prix_unitaire"] if achat else 0.0)
        tk.Entry(self, textvariable=self.prix_unitaire_var).grid(row=4, column=1)

        tk.Label(self, text="Fournisseur").grid(row=5, column=0, sticky="w")
        self.fournisseur_var = tk.StringVar(value=achat["fournisseur"] if achat else "")
        tk.Entry(self, textvariable=self.fournisseur_var).grid(row=5, column=1)

        tk.Label(self, text="Facture").grid(row=6, column=0, sticky="w")
        self.facture_var = tk.StringVar(value=achat["facture"] if achat else "")
        tk.Entry(self, textvariable=self.facture_var).grid(row=6, column=1)

        tk.Label(self, text="Exercice").grid(row=7, column=0, sticky="w")
        self.exercice_var = tk.StringVar(value=achat["exercice"] if achat else "")
        tk.Entry(self, textvariable=self.exercice_var).grid(row=7, column=1)

        tk.Button(self, text="Enregistrer", command=self.save).grid(row=8, column=0, columnspan=2, pady=8)

    def save(self):
        article_selection = self.article_var.get()
        article_id = self.article_id_map.get(article_selection)
        # contenance = self.article_contenance_map.get(article_selection) # lecture seule, utile si tu veux l'utiliser
        date_achat = self.date_var.get()
        quantite = self.quantite_var.get()
        prix_unitaire = self.prix_unitaire_var.get()
        fournisseur = self.fournisseur_var.get()
        facture = self.facture_var.get()
        exercice = self.exercice_var.get()
        if not article_id or not date_achat:
            messagebox.showwarning("Saisie", "Article et Date sont obligatoires.")
            return
        try:
            if self.achat:
                update_achat(self.achat["id"], article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice)
            else:
                insert_achat(article_id, date_achat, quantite, prix_unitaire, fournisseur, facture, exercice)
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de l'achat."))
            
class InventaireDialog(tk.Toplevel):
    def __init__(self, master, on_done, inventaire=None):
        super().__init__(master)
        self.title("Inventaire")
        self.on_done = on_done
        self.inventaire = inventaire
        
        # Configure grid pour layout extensible
        self.columnconfigure(1, weight=1)

        tk.Label(self, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar(value=inventaire["date_inventaire"] if inventaire else "")
        tk.Entry(self, textvariable=self.date_var).grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Type inventaire").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        type_options = ["avant", "apres", "hors_evenement"]
        self.nom_var = tk.StringVar(value=inventaire["type_inventaire"] if inventaire else "hors_evenement")
        ttk.Combobox(self, textvariable=self.nom_var, values=type_options, state="readonly").grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Commentaire").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.commentaire_var = tk.StringVar(value=inventaire["commentaire"] if inventaire else "")
        tk.Entry(self, textvariable=self.commentaire_var).grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        tk.Button(self, text="Enregistrer", command=self.save).grid(row=3, column=0, columnspan=2, pady=8)

    def save(self):
        date = self.date_var.get()
        type_inventaire = self.nom_var.get()
        commentaire = self.commentaire_var.get()
        if not date or not type_inventaire:
            messagebox.showwarning("Saisie", "Date et type sont obligatoires.")
            return
        
        # Valider que le type est bien dans les valeurs acceptées
        if type_inventaire not in ('avant', 'apres', 'hors_evenement'):
            messagebox.showwarning("Saisie", "Le type doit être 'avant', 'apres' ou 'hors_evenement'.")
            return
        
        event_id = None  # No event linked for now
        
        try:
            if self.inventaire:
                inv_db.update_inventaire(self.inventaire["id"], date, event_id, type_inventaire, commentaire)
            else:
                # Capture inv_id for potential future use (e.g., adding lignes immediately after creation)
                inv_id = inv_db.insert_inventaire(date, event_id, type_inventaire, commentaire)
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de l'inventaire."))

class LignesInventaireDialog(tk.Toplevel):
    def __init__(self, master, inventaire_id):
        super().__init__(master)
        self.title("Lignes de l'inventaire")
        self.inventaire_id = inventaire_id
        self.create_widgets()
        self.refresh_lignes()

    def create_widgets(self):
        self.lignes_tree = ttk.Treeview(self, columns=("article_id", "quantite", "commentaire"), show="headings")
        self.lignes_tree.heading("article_id", text="Article")
        self.lignes_tree.heading("quantite", text="Quantité")
        self.lignes_tree.heading("commentaire", text="Commentaire")
        self.lignes_tree.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="Ajouter", command=self.add_ligne).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Modifier", command=self.edit_ligne).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Supprimer", command=self.del_ligne).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=6)

    def refresh_lignes(self):
        try:
            for row in self.lignes_tree.get_children():
                self.lignes_tree.delete(row)
            for l in inv_db.list_lignes_inventaire(self.inventaire_id):
                # Convert Row to dict for safe .get() access
                ligne_dict = row_to_dict(l)
                # Afficher article_name au lieu de article_id pour meilleure lisibilité
                article_display = ligne_dict["article_name"] if ligne_dict.get("article_name") else f"ID:{ligne_dict['article_id']}"
                self.lignes_tree.insert("", "end", iid=ligne_dict["id"], values=(article_display, ligne_dict["quantite"], ligne_dict["commentaire"]))
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des lignes d'inventaire."))

    def add_ligne(self):
        LigneInventaireDialog(self, self.refresh_lignes, self.inventaire_id)

    def edit_ligne(self):
        sel = self.lignes_tree.focus()
        if sel:
            ligne = None
            for l in inv_db.list_lignes_inventaire(self.inventaire_id):
                if str(l["id"]) == str(sel):
                    ligne = l
                    break
            if ligne:
                LigneInventaireDialog(self, self.refresh_lignes, self.inventaire_id, ligne)
        else:
            messagebox.showwarning("Sélection", "Sélectionner une ligne à modifier.")

    def del_ligne(self):
        sel = self.lignes_tree.focus()
        if sel:
            if messagebox.askyesno("Suppression", "Supprimer cette ligne ?"):
                try:
                    inv_db.delete_ligne_inventaire(sel)
                    self.refresh_lignes()
                except Exception as e:
                    messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de la ligne d'inventaire."))
        else:
            messagebox.showwarning("Sélection", "Sélectionner une ligne à supprimer.")

class LigneInventaireDialog(tk.Toplevel):
    def __init__(self, master, on_done, inventaire_id, ligne=None):
        super().__init__(master)
        self.title("Ligne inventaire")
        self.on_done = on_done
        self.inventaire_id = inventaire_id
        self.ligne = ligne

        # Utiliser Combobox pour sélectionner un article
        tk.Label(self, text="Article").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        articles = list_articles_names()
        self.article_options = [f"{a['name']} ({a['contenance'] or 'N/A'})" for a in articles]
        self.article_id_map = {f"{a['name']} ({a['contenance'] or 'N/A'})": a['id'] for a in articles}
        
        # Sélectionner l'article par défaut si en mode édition
        default_article = None
        if ligne:
            for opt in self.article_options:
                if self.article_id_map[opt] == ligne["article_id"]:
                    default_article = opt
                    break
        
        self.article_var = tk.StringVar(value=default_article if default_article else (self.article_options[0] if self.article_options else ""))
        self.article_combo = ttk.Combobox(self, textvariable=self.article_var, values=self.article_options, state="readonly", width=30)
        self.article_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Quantité").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.quantite_var = tk.IntVar(value=ligne["quantite"] if ligne else 0)
        tk.Entry(self, textvariable=self.quantite_var).grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Commentaire").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.comment_var = tk.StringVar(value=ligne["commentaire"] if ligne else "")
        tk.Entry(self, textvariable=self.comment_var).grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        tk.Button(self, text="Enregistrer", command=self.save).grid(row=3, column=0, columnspan=2, pady=8)

    def save(self):
        article_selection = self.article_var.get()
        article_id = self.article_id_map.get(article_selection)
        quantite = self.quantite_var.get()
        comment = self.comment_var.get()
        if not article_id:
            messagebox.showwarning("Saisie", "Article obligatoire.")
            return
        try:
            if self.ligne:
                inv_db.update_ligne_inventaire(self.ligne["id"], article_id, quantite, comment)
            else:
                inv_db.insert_ligne_inventaire(self.inventaire_id, article_id, quantite, comment)
            
            # Mettre à jour le stock de l'article immédiatement après l'enregistrement de la ligne d'inventaire
            try:
                set_article_stock(article_id, quantite)
            except Exception as stock_err:
                logger.warning(f"Erreur lors de la mise à jour du stock pour l'article {article_id}: {stock_err}")
            
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de la ligne d'inventaire."))

class MouvementDialog(tk.Toplevel):
    def __init__(self, master, on_done, mvt=None):
        super().__init__(master)
        self.title("Mouvement")
        self.on_done = on_done
        self.mvt = mvt

        tk.Label(self, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar(value=mvt["date"] if mvt else "")
        tk.Entry(self, textvariable=self.date_var).grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        # Utiliser Combobox pour sélectionner un article
        tk.Label(self, text="Article").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        articles = list_articles_names()
        self.article_options = [f"{a['name']} ({a['contenance'] or 'N/A'})" for a in articles]
        self.article_id_map = {f"{a['name']} ({a['contenance'] or 'N/A'})": a['id'] for a in articles}
        
        # Sélectionner l'article par défaut si en mode édition
        default_article = None
        if mvt:
            for opt in self.article_options:
                if self.article_id_map[opt] == mvt["article_id"]:
                    default_article = opt
                    break
        
        self.article_var = tk.StringVar(value=default_article if default_article else (self.article_options[0] if self.article_options else ""))
        self.article_combo = ttk.Combobox(self, textvariable=self.article_var, values=self.article_options, state="readonly", width=30)
        self.article_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Type").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.type_var = tk.StringVar(value=mvt["type"] if mvt else "entrée")
        type_combo = ttk.Combobox(self, textvariable=self.type_var, values=["entrée", "sortie"], state="readonly")
        type_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Quantité").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        self.quantite_var = tk.IntVar(value=mvt["quantite"] if mvt else 0)
        tk.Entry(self, textvariable=self.quantite_var).grid(row=3, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(self, text="Commentaire").grid(row=4, column=0, sticky="w", padx=5, pady=3)
        self.comment_var = tk.StringVar(value=mvt["commentaire"] if mvt else "")
        tk.Entry(self, textvariable=self.comment_var).grid(row=4, column=1, sticky="ew", padx=5, pady=3)

        tk.Button(self, text="Enregistrer", command=self.save).grid(row=5, column=0, columnspan=2, pady=8)

    def save(self):
        date = self.date_var.get()
        article_selection = self.article_var.get()
        article_id = self.article_id_map.get(article_selection)
        type_mvt = self.type_var.get()
        quantite = self.quantite_var.get()
        comment = self.comment_var.get()
        if not date or not article_id or not type_mvt or not quantite:
            messagebox.showwarning("Saisie", "Tous les champs sont obligatoires.")
            return
        try:
            if self.mvt:
                update_mouvement(self.mvt["id"], date, article_id, type_mvt, quantite, comment)
            else:
                insert_mouvement(date, article_id, type_mvt, quantite, comment)
            self.on_done()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement du mouvement."))