import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("event_recettes")

def update_vente_sur_place_recette(event_id):
    """Calcule le gain de toutes les caisses et l'ajoute/actualise la recette 'Vente sur place'."""
    try:
        conn = get_connection()
        gain_total = 0
        caisses = conn.execute("SELECT id FROM event_caisses WHERE event_id=?", (event_id,)).fetchall()
        for caisse in caisses:
            cid = caisse["id"]
            r = conn.execute(
                "SELECT SUM(CASE WHEN type='cheque' THEN valeur ELSE valeur*quantite END) AS tot FROM event_caisse_details WHERE caisse_id=? AND moment='debut'", (cid,)
            ).fetchone()
            fond_debut = r["tot"] if r["tot"] else 0
            r = conn.execute(
                "SELECT SUM(CASE WHEN type='cheque' THEN valeur ELSE valeur*quantite END) AS tot FROM event_caisse_details WHERE caisse_id=? AND moment='fin'", (cid,)
            ).fetchone()
            fond_fin = r["tot"] if r["tot"] else 0
            gain_total += (fond_fin - fond_debut)
        exist = conn.execute("SELECT id FROM event_recettes WHERE event_id=? AND source='Vente sur place'", (event_id,)).fetchone()
        if exist:
            conn.execute("UPDATE event_recettes SET montant=? WHERE id=?", (gain_total, exist["id"]))
        else:
            conn.execute("INSERT INTO event_recettes (event_id, source, montant) VALUES (?, 'Vente sur place', ?)", (event_id, gain_total))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur update_vente_sur_place_recette: {e}")

class EventRecettesWindow(tk.Toplevel):
    def __init__(self, master, event_id):
        super().__init__(master)
        self.title("Recettes de l'événement")
        self.geometry("850x400")
        self.event_id = event_id

        try:
            update_vente_sur_place_recette(self.event_id)
        except Exception as e:
            logger.error(f"Erreur lors de l'update automatique 'Vente sur place': {e}")

        self.create_widgets()
        self.refresh_recettes()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Ajouter recette", command=self.add_recette).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Éditer", command=self.edit_recette).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_recette).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)
        self.tree = ttk.Treeview(self, columns=("id", "source", "module", "montant", "commentaire"), show="headings")
        for col, lbl in zip(("id", "source", "module", "montant", "commentaire"),
                            ("ID", "Source", "Module lié", "Montant (€)", "Commentaire")):
            self.tree.heading(col, text=lbl)
            self.tree.column(col, width=120 if col in ("montant", "module") else 170)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_recettes(self):
        try:
            self.tree.delete(*self.tree.get_children())
            conn = get_connection()
            recettes = conn.execute("SELECT * FROM event_recettes WHERE event_id=? ORDER BY source", (self.event_id,)).fetchall()
            for r in recettes:
                module_name = ""
                if r["module_id"]:
                    mod = conn.execute("SELECT nom_module FROM event_modules WHERE id=?", (r["module_id"],)).fetchone()
                    if mod:
                        module_name = mod["nom_module"]
                self.tree.insert("", "end", values=(r["id"], r["source"], module_name, f"{r['montant']:.2f}", r["commentaire"] if r["commentaire"] else ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des recettes."))

    def get_selected_recette_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_recette(self):
        RecetteDialog(self, event_id=self.event_id, on_save=self.refresh_recettes)

    def edit_recette(self):
        rid = self.get_selected_recette_id()
        if not rid:
            messagebox.showwarning("Sélection", "Sélectionne une recette.")
            return
        RecetteDialog(self, event_id=self.event_id, recette_id=rid, on_save=self.refresh_recettes)

    def delete_recette(self):
        rid = self.get_selected_recette_id()
        if not rid:
            messagebox.showwarning("Sélection", "Sélectionne une recette.")
            return
        try:
            conn = get_connection()
            r = conn.execute("SELECT source FROM event_recettes WHERE id=?", (rid,)).fetchone()
            if r and r["source"] == "Vente sur place":
                messagebox.showerror("Erreur", "Impossible de supprimer la recette automatique 'Vente sur place'.")
                conn.close()
                return
            conn.execute("DELETE FROM event_recettes WHERE id=?", (rid,))
            conn.commit()
            conn.close()
            self.refresh_recettes()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de la recette."))

class RecetteDialog(tk.Toplevel):
    def __init__(self, master, event_id, recette_id=None, on_save=None):
        super().__init__(master)
        self.title("Recette" if not recette_id else "Éditer la recette")
        self.event_id = event_id
        self.recette_id = recette_id
        self.on_save = on_save
        self.geometry("460x350")
        self.resizable(False, False)
        self.source_var = tk.StringVar()
        self.montant_var = tk.DoubleVar()
        self.comment_var = tk.StringVar()
        self.module_var = tk.StringVar()
        self.colonne_var = tk.StringVar()
        self.module_choices = []
        self.colonnes_choices = []

        tk.Label(self, text="Source :").pack(pady=4)
        tk.Entry(self, textvariable=self.source_var, width=35).pack()

        tk.Label(self, text="Module lié :").pack(pady=4)
        self.module_menu = ttk.Combobox(self, textvariable=self.module_var, state="readonly")
        self.module_menu.pack()
        self.module_menu.bind("<<ComboboxSelected>>", self.on_module_selected)

        self.colonne_frame = tk.Frame(self)
        self.colonne_label = tk.Label(self.colonne_frame, text="Colonne à sommer :")
        self.colonne_menu = ttk.Combobox(self.colonne_frame, textvariable=self.colonne_var, state="readonly")
        self.colonne_label.pack(side=tk.LEFT)
        self.colonne_menu.pack(side=tk.LEFT)
        self.colonne_frame.pack(pady=4)
        self.colonne_frame.pack_forget()  # cachée par défaut
        self.colonne_menu.bind("<<ComboboxSelected>>", self.update_montant_from_colonne)

        tk.Label(self, text="Montant (€) :").pack(pady=4)
        self.montant_entry = tk.Entry(self, textvariable=self.montant_var, width=20)
        self.montant_entry.pack()

        tk.Label(self, text="Commentaire :").pack(pady=4)
        tk.Entry(self, textvariable=self.comment_var, width=45).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=30, pady=14)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=30, pady=14)

        self.populate_module_menu()
        if self.recette_id:
            self.load_recette()

    def populate_module_menu(self):
        try:
            conn = get_connection()
            mods = conn.execute("SELECT id, nom_module FROM event_modules WHERE event_id=?", (self.event_id,)).fetchall()
            self.module_choices = [("", "Aucun")] + [(str(m["id"]), m["nom_module"]) for m in mods]
            self.module_menu['values'] = [name for _, name in self.module_choices]
            self.module_menu.current(0)
            conn.close()
            self.hide_colonne_menu()
        except Exception as e:
            logger.error(f"Erreur populate_module_menu: {e}")

    def populate_colonne_menu(self, module_id):
        try:
            conn = get_connection()
            fields = conn.execute("SELECT id, nom_champ FROM event_module_fields WHERE module_id=?", (module_id,)).fetchall()
            conn.close()
            self.colonnes_choices = [(str(f["id"]), f["nom_champ"]) for f in fields]
            if not self.colonnes_choices:
                self.hide_colonne_menu()
                return
            self.colonne_menu['values'] = [name for _, name in self.colonnes_choices]
            self.colonne_menu.current(0)
            self.show_colonne_menu()
            self.update_montant_from_colonne()
        except Exception as e:
            logger.error(f"Erreur populate_colonne_menu: {e}")

    def hide_colonne_menu(self):
        self.colonne_frame.pack_forget()

    def show_colonne_menu(self):
        self.colonne_frame.pack(pady=4)

    def on_module_selected(self, event=None):
        idx = self.module_menu.current()
        if idx > 0:
            module_id = int(self.module_choices[idx][0])
            self.populate_colonne_menu(module_id)
            self.montant_entry.config(state="readonly")
        else:
            self.hide_colonne_menu()
            self.montant_entry.config(state="normal")

    def update_montant_from_colonne(self, event=None):
        module_idx = self.module_menu.current()
        colonne_idx = self.colonne_menu.current()
        if module_idx > 0 and colonne_idx >= 0 and self.colonnes_choices:
            module_id = int(self.module_choices[module_idx][0])
            field_id = int(self.colonnes_choices[colonne_idx][0])
            try:
                conn = get_connection()
                rows = conn.execute(
                    "SELECT valeur FROM event_module_data WHERE module_id=? AND field_id=?", (module_id, field_id)
                ).fetchall()
                somme = 0.0
                for r in rows:
                    try:
                        somme += float(r["valeur"])
                    except (TypeError, ValueError):
                        pass
                conn.close()
                self.montant_var.set(round(somme, 2))
            except Exception as e:
                logger.error(f"Erreur update_montant_from_colonne: {e}")

    def load_recette(self):
        try:
            conn = get_connection()
            r = conn.execute("SELECT * FROM event_recettes WHERE id=?", (self.recette_id,)).fetchone()
            conn.close()
            if r:
                self.source_var.set(r["source"])
                self.montant_var.set(r["montant"])
                self.comment_var.set(r["commentaire"] or "")
                if r["module_id"]:
                    for i, (mid, name) in enumerate(self.module_choices):
                        if mid and int(mid) == r["module_id"]:
                            self.module_menu.current(i)
                            self.populate_colonne_menu(int(mid))
                            break
        except Exception as e:
            logger.error(f"Erreur load_recette: {e}")

    def save(self):
        source = self.source_var.get().strip()
        montant = self.montant_var.get()
        comment = self.comment_var.get().strip()
        module_idx = self.module_menu.current()
        module_id = None
        if module_idx > 0:
            module_id = int(self.module_choices[module_idx][0])
        else:
            self.hide_colonne_menu()
        if not source:
            messagebox.showerror("Erreur", "Source obligatoire.")
            return
        if source.lower() == "vente sur place":
            messagebox.showerror("Erreur", "La recette 'Vente sur place' est gérée automatiquement.")
            return
        try:
            conn = get_connection()
            if self.recette_id:
                conn.execute(
                    "UPDATE event_recettes SET source=?, montant=?, commentaire=?, module_id=? WHERE id=?",
                    (source, montant, comment, module_id, self.recette_id)
                )
            else:
                conn.execute(
                    "INSERT INTO event_recettes (event_id, source, montant, commentaire, module_id) VALUES (?, ?, ?, ?, ?)",
                    (self.event_id, source, montant, comment, module_id)
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de la recette."))