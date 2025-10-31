import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection
from modules.model_colonnes import GestionModelColonnes, ask_add_custom_column, get_choix_pour_colonne
from dialogs.add_row_dialog import AddRowDialog
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("event_modules")

class ChoiceDialog(tk.Toplevel):
    def __init__(self, master, label, choices):
        super().__init__(master)
        self.title("Choix")
        self.result = None
        self.var = tk.StringVar()
        tk.Label(self, text=label).pack(padx=10, pady=10)
        cb = ttk.Combobox(self, textvariable=self.var, values=choices, state="readonly")
        cb.pack(padx=10, pady=6)
        if choices:
            cb.current(0)
        btnf = tk.Frame(self)
        btnf.pack(pady=8)
        tk.Button(btnf, text="OK", command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btnf, text="Annuler", command=self.on_cancel).pack(side="right", padx=5)
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())
        self.grab_set()
        self.wait_window(self)

    def on_ok(self):
        self.result = self.var.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

class EventModulesWindow(tk.Toplevel):
    def __init__(self, master, event_id):
        super().__init__(master)
        self.title("Modules/Tableaux personnalisés de l'événement")
        self.geometry("800x500")
        self.event_id = event_id
        self.create_widgets()
        self.refresh_modules()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Nouveau module", command=self.add_module).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Éditer", command=self.edit_module).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_module).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Ouvrir", command=self.open_module).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)

        self.tree = ttk.Treeview(self, columns=("id", "nom_module"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nom_module", text="Nom du module/tableau")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_modules(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            mods = conn.execute("SELECT * FROM event_modules WHERE event_id = ?", (self.event_id,)).fetchall()
            for mod in mods:
                self.tree.insert("", "end", values=(mod["id"], mod["nom_module"]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la récupération des modules personnalisés."))

    def get_selected_module_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_module(self):
        try:
            name = simpledialog.askstring("Module/Tableau", "Nom du module/tableau :")
            if not name:
                return
            conn = get_connection()
            conn.execute(
                "INSERT INTO event_modules (event_id, nom_module) VALUES (?, ?)",
                (self.event_id, name)
            )
            conn.commit()
            conn.close()
            self.refresh_modules()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'ajout du module."))

    def edit_module(self):
        mid = self.get_selected_module_id()
        if not mid:
            messagebox.showwarning("Sélection", "Sélectionne un module.")
            return
        name = simpledialog.askstring("Modifier nom", "Nouveau nom du module/tableau :")
        if not name:
            return
        try:
            conn = get_connection()
            conn.execute("UPDATE event_modules SET nom_module=? WHERE id=?", (name, mid))
            conn.commit()
            conn.close()
            self.refresh_modules()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la modification du module."))

    def delete_module(self):
        mid = self.get_selected_module_id()
        if not mid:
            messagebox.showwarning("Sélection", "Sélectionne un module.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer ce module/tableau ?"):
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM event_modules WHERE id=?", (mid,))
            conn.execute("DELETE FROM event_module_fields WHERE module_id=?", (mid,))
            conn.execute("DELETE FROM event_module_data WHERE module_id=?", (mid,))
            conn.commit()
            conn.close()
            self.refresh_modules()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression du module."))

    def open_module(self):
        mid = self.get_selected_module_id()
        if not mid:
            messagebox.showwarning("Sélection", "Sélectionne un module.")
            return
        ModuleTableWindow(self, module_id=mid)

class TypeChampDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Type du champ :", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", columnspan=2)
        self.type_var = tk.StringVar(value="TEXT")
        types = [("TEXT", "pour du texte (chaînes de caractères)"),
                 ("INTEGER", "pour les nombres entiers"),
                 ("REAL", "pour les nombres décimaux (ex: 3.14)")]
        for i, (val, desc) in enumerate(types):
            tk.Radiobutton(master, text=val, variable=self.type_var, value=val).grid(row=i+1, column=0, sticky="w")
            tk.Label(master, text=desc).grid(row=i+1, column=1, sticky="w")
        return None

    def apply(self):
        self.result = self.type_var.get()

class PrixUnitaireDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Associer un prix unitaire à cette colonne ?", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2)
        tk.Label(master, text="Prix unitaire (€) (laisser vide pour aucun) :").grid(row=1, column=0, sticky="w")
        self.prix_var = tk.StringVar()
        tk.Entry(master, textvariable=self.prix_var, width=10).grid(row=1, column=1)
        return None

    def apply(self):
        try:
            self.result = float(self.prix_var.get().replace(",", "."))
        except Exception:
            self.result = None

class ModuleTableWindow(tk.Toplevel):
    def __init__(self, master, module_id):
        super().__init__(master)
        self.title("Gestion du tableau personnalisé")
        self.geometry("1000x650")
        self.module_id = module_id
        self.editing_entry = None  # Pour l'édition de cellule
        self.id_col_total = self.get_id_col_total()  # id field de la colonne "Montant total" (ou None)
        self.create_widgets()
        self.refresh_fields()
        self.refresh_data()

    def create_widgets(self):
        btnf = tk.Frame(self)
        btnf.pack(fill=tk.X)
        tk.Button(btnf, text="Ajouter colonne", command=self.add_field).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Supprimer colonne", command=self.delete_field).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Éditer colonne", command=self.edit_field).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Définir colonne Montant total", command=self.set_total_column).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Éditer prix", command=self.edit_column_price).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Ajouter ligne", command=self.add_row).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Supprimer ligne", command=self.delete_row).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Exporter PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Exporter Excel", command=self.export_excel).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Modèles de colonnes", command=self.open_model_colonnes).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(btnf, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=4)

        self.fields = []
        self.tree = ttk.Treeview(self, columns=[], show="headings", selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.tree.bind("<Double-1>", self.on_cell_double_click)

    def open_model_colonnes(self):
        GestionModelColonnes(self)

    def refresh_fields(self):
        try:
            conn = get_connection()
            self.fields = conn.execute(
                "SELECT * FROM event_module_fields WHERE module_id = ? ORDER BY id", (self.module_id,)
            ).fetchall()
            conn.close()
            # Update tree columns
            self.tree["columns"] = [f["id"] for f in self.fields]
            for f in self.fields:
                titre = f["nom_champ"]
                if self.id_col_total and int(f["id"]) == self.id_col_total:
                    titre += " (Montant total)"
                else:
                    val_prix = f["prix_unitaire"] if "prix_unitaire" in f.keys() else None
                    if val_prix not in (None, "", 0):
                        try:
                            titre += f" ({float(val_prix):.2f}€)"
                        except Exception:
                            titre += f" ({val_prix}€)"
                self.tree.heading(f["id"], text=titre)
                self.tree.column(f["id"], width=120)
            self.tree["show"] = "headings"
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la récupération des colonnes du module."))

    def refresh_data(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            rows = conn.execute(
                "SELECT row_index FROM event_module_data WHERE module_id = ? GROUP BY row_index ORDER BY row_index", (self.module_id,)
            ).fetchall()
            for row in rows:
                values = []
                for f in self.fields:
                    val = conn.execute(
                        "SELECT valeur FROM event_module_data WHERE module_id = ? AND row_index = ? AND field_id = ?",
                        (self.module_id, row["row_index"], f["id"])
                    ).fetchone()
                    values.append("" if not val else val["valeur"])
                self.tree.insert("", "end", iid=row["row_index"], values=values)
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du rafraîchissement des données du module."))

    def get_id_col_total(self):
        conn = get_connection()
        id_col = conn.execute("SELECT id_col_total FROM event_modules WHERE id=?", (self.module_id,)).fetchone()
        conn.close()
        return id_col["id_col_total"] if id_col and id_col["id_col_total"] else None

    def add_field(self):
        try:
            res = ask_add_custom_column(self)
            if not res:
                return
            name = res["name"]
            typ = res["type"]
            modele_colonne = res.get("modele_colonne")
            dlg_prix = PrixUnitaireDialog(self)
            prix = dlg_prix.result
            conn = get_connection()
            conn.execute(
                "INSERT INTO event_module_fields (module_id, nom_champ, type_champ, prix_unitaire, modele_colonne) VALUES (?, ?, ?, ?, ?)",
                (self.module_id, name, typ, prix, modele_colonne)
            )
            conn.commit()
            conn.close()
            self.refresh_fields()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'ajout de colonne."))

    def delete_field(self):
        try:
            if not self.fields:
                messagebox.showwarning("Suppression", "Aucune colonne à supprimer.")
                return
            ch = [f"{f['nom_champ']} (id {f['id']})" for f in self.fields]
            idx = simpledialog.askinteger("Index colonne à supprimer", f"Index (1-{len(self.fields)}) :\n"+"\n".join(f"{i+1}. {ch[i]}" for i in range(len(ch))))
            if not idx or idx < 1 or idx > len(self.fields):
                return
            field_id = self.fields[idx-1]["id"]
            conn = get_connection()
            conn.execute("DELETE FROM event_module_data WHERE module_id=? AND field_id=?", (self.module_id, field_id))
            conn.execute("DELETE FROM event_module_fields WHERE id=?", (field_id,))
            if self.id_col_total and int(field_id) == self.id_col_total:
                conn.execute("UPDATE event_modules SET id_col_total=NULL WHERE id=?", (self.module_id,))
                self.id_col_total = None
            conn.commit()
            conn.close()
            self.refresh_fields()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de colonne."))

    def edit_field(self):
        try:
            if not self.fields:
                messagebox.showwarning("Éditer colonne", "Aucune colonne à éditer.")
                return
            ch = [f"{f['nom_champ']} (id {f['id']})" for f in self.fields]
            idx = simpledialog.askinteger(
                "Éditer colonne",
                f"Index de la colonne à éditer (1-{len(self.fields)}) :\n" +
                "\n".join(f"{i+1}. {ch[i]}" for i in range(len(ch)))
            )
            if not idx or idx < 1 or idx > len(self.fields):
                return
            field = self.fields[idx-1]
            from dialogs.edit_field_dialog import EditFieldDialog
            def refresh_all():
                self.refresh_fields()
                self.recompute_all_totals()
                self.refresh_data()
            EditFieldDialog(
                self,
                self.module_id,
                field_id=field["id"],
                on_save=refresh_all,
                with_modele_colonne=True
            )
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'édition de colonne."))

    def set_total_column(self):
        try:
            if not self.fields:
                messagebox.showwarning("Montant total", "Ajoute d'abord des colonnes.")
                return
            ch = [f"{f['nom_champ']} (id {f['id']})" for f in self.fields]
            idx = simpledialog.askinteger("Colonne total", f"Quelle colonne doit contenir le montant total ?\nIndex (1-{len(self.fields)}) :\n"+"\n".join(f"{i+1}. {ch[i]}" for i in range(len(ch))))
            if not idx or idx < 1 or idx > len(self.fields):
                return
            field_id = int(self.fields[idx-1]["id"])
            conn = get_connection()
            conn.execute("UPDATE event_modules SET id_col_total=? WHERE id=?", (field_id, self.module_id))
            conn.commit()
            conn.close()
            self.id_col_total = field_id
            self.recompute_all_totals()
            self.refresh_fields()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la définition de la colonne total."))

    def add_row(self):
        try:
            if not self.fields:
                messagebox.showwarning("Champs", "Ajoute d'abord des colonnes.")
                return
            def get_choices(modele_colonne_nom):
                conn = get_connection()
                row = conn.execute("SELECT id FROM colonnes_modeles WHERE name=?", (modele_colonne_nom,)).fetchone()
                if not row:
                    return []
                modele_id = row["id"]
                choix = [v["valeur"] for v in conn.execute("SELECT valeur FROM valeurs_modeles_colonnes WHERE modele_id=?", (modele_id,)).fetchall()]
                conn.close()
                return choix
            dlg = AddRowDialog(self, self.fields, get_choices)
            if not dlg.result:
                return
            conn = get_connection()
            row_idx = conn.execute(
                "SELECT MAX(row_index) as mx FROM event_module_data WHERE module_id = ?", (self.module_id,)
            ).fetchone()
            next_row = 1 if not row_idx or not row_idx["mx"] else row_idx["mx"] + 1
            for f in self.fields:
                val = dlg.result.get(f["id"], "")
                conn.execute(
                    "INSERT INTO event_module_data (module_id, row_index, field_id, valeur) VALUES (?, ?, ?, ?)",
                    (self.module_id, next_row, f["id"], val)
                )
            conn.commit()
            if self.id_col_total:
                self.recompute_total_for_row(next_row)
            conn.close()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'ajout de ligne."))

    def delete_row(self):
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Sélection", "Sélectionne une ligne à supprimer.")
                return
            row_idx = int(sel[0])
            conn = get_connection()
            conn.execute("DELETE FROM event_module_data WHERE module_id=? AND row_index=?", (self.module_id, row_idx))
            conn.commit()
            conn.close()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de ligne."))

    def on_cell_double_click(self, event):
        if self.editing_entry is not None:
            return
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        rowid = self.tree.identify_row(event.y)
        if not rowid or not col:
            return
        col_idx = int(col.replace('#', '')) - 1
        if col_idx < 0 or col_idx >= len(self.fields):
            return
        selected_field = self.fields[col_idx]
        x, y, width, height = self.tree.bbox(rowid, col)
        value = self.tree.set(rowid, selected_field["id"])
        entry = tk.Entry(self.tree, width=16)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()
        entry.select_range(0, tk.END)
        self.editing_entry = entry

        def on_validate(e=None):
            try:
                new_value = entry.get()
                conn = get_connection()
                res = conn.execute(
                    "SELECT id FROM event_module_data WHERE module_id=? AND row_index=? AND field_id=?",
                    (self.module_id, int(rowid), selected_field["id"])
                ).fetchone()
                if res:
                    conn.execute(
                        "UPDATE event_module_data SET valeur=? WHERE id=?",
                        (new_value, res["id"])
                    )
                else:
                    conn.execute(
                        "INSERT INTO event_module_data (module_id, row_index, field_id, valeur) VALUES (?, ?, ?, ?)",
                        (self.module_id, int(rowid), selected_field["id"], new_value)
                    )
                conn.commit()
                conn.close()
                entry.destroy()
                self.editing_entry = None
                if self.id_col_total:
                    self.recompute_total_for_row(int(rowid))
                self.refresh_data()
            except Exception as e:
                entry.destroy()
                self.editing_entry = None
                messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la modification de cellule."))

        def on_cancel(e=None):
            entry.destroy()
            self.editing_entry = None

        entry.bind("<Return>", on_validate)
        entry.bind("<FocusOut>", on_cancel)

    def edit_column_price(self):
        try:
            if not self.fields:
                messagebox.showwarning("Prix unitaire", "Aucune colonne à éditer.")
                return
            ch = [f"{f['nom_champ']} (id {f['id']})" for f in self.fields]
            idx = simpledialog.askinteger(
                "Éditer prix",
                f"Index de la colonne (1-{len(self.fields)}) :\n" +
                "\n".join(f"{i+1}. {ch[i]}" for i in range(len(ch)))
            )
            if not idx or idx < 1 or idx > len(self.fields):
                return
            field_id = self.fields[idx-1]["id"]
            old_price = self.fields[idx-1]["prix_unitaire"]
            new_price = simpledialog.askstring(
                "Prix unitaire",
                f"Nouveau prix unitaire (€) pour {self.fields[idx-1]['nom_champ']} (laisse vide pour aucun) :",
                initialvalue=old_price if old_price not in (None, "") else ""
            )
            if new_price is None:
                return  # Annulé
            conn = get_connection()
            conn.execute("UPDATE event_module_fields SET prix_unitaire=? WHERE id=?", (new_price if new_price else None, field_id))
            conn.commit()
            conn.close()
            self.refresh_fields()
            self.recompute_all_totals()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la modification du prix de colonne."))

    def recompute_total_for_row(self, rowid):
        try:
            if not self.id_col_total:
                return
            conn = get_connection()
            total = 0.0
            for f in self.fields:
                val_prix = f["prix_unitaire"] if "prix_unitaire" in f.keys() else None
                if val_prix not in (None, "", 0):
                    try:
                        prix = float(val_prix)
                    except Exception:
                        prix = 0
                    val_row = conn.execute(
                        "SELECT valeur FROM event_module_data WHERE module_id=? AND row_index=? AND field_id=?",
                        (self.module_id, rowid, f["id"])
                    ).fetchone()
                    try:
                        qte = float(val_row["valeur"]) if val_row and val_row["valeur"] not in (None, "") else 0
                    except Exception:
                        qte = 0
                    total += qte * prix
            res_total = conn.execute(
                "SELECT id FROM event_module_data WHERE module_id=? AND row_index=? AND field_id=?",
                (self.module_id, rowid, self.id_col_total)
            ).fetchone()
            if res_total:
                conn.execute(
                    "UPDATE event_module_data SET valeur=? WHERE id=?",
                    (f"{total:.2f}", res_total["id"])
                )
            else:
                conn.execute(
                    "INSERT INTO event_module_data (module_id, row_index, field_id, valeur) VALUES (?, ?, ?, ?)",
                    (self.module_id, rowid, self.id_col_total, f"{total:.2f}")
                )
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du calcul du total ligne."))

    def recompute_all_totals(self):
        try:
            if not self.id_col_total:
                return
            conn = get_connection()
            rows = conn.execute(
                "SELECT row_index FROM event_module_data WHERE module_id = ? GROUP BY row_index ORDER BY row_index", (self.module_id,)
            ).fetchall()
            conn.close()
            for row in rows:
                self.recompute_total_for_row(row["row_index"])
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du recalcul des totaux."))

    def export_pdf(self):
        try:
            import sys, os
            parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            from exports.exports import export_dataframe_to_pdf
        except ImportError as e:
            messagebox.showerror("Export PDF", "Le module d'export PDF n'est pas disponible.")
            return

        try:
            conn = get_connection()
            fields = conn.execute(
                "SELECT * FROM event_module_fields WHERE module_id = ? ORDER BY id", (self.module_id,)
            ).fetchall()
            rows = conn.execute(
                "SELECT row_index FROM event_module_data WHERE module_id = ? GROUP BY row_index ORDER BY row_index", (self.module_id,)
            ).fetchall()
            headers = [f["nom_champ"] for f in fields]
            data = []
            for row in rows:
                values = []
                for f in fields:
                    val = conn.execute(
                        "SELECT valeur FROM event_module_data WHERE module_id=? AND row_index=? AND field_id=?",
                        (self.module_id, row["row_index"], f["id"])
                    ).fetchone()
                    values.append("" if not val else val["valeur"])
                data.append(values)
            import pandas as pd
            df = pd.DataFrame(data, columns=headers)
            conn.close()
            export_dataframe_to_pdf(df, title="Export PDF - Module personnalisé")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'export PDF du module personnalisé."))

    def export_excel(self):
        try:
            import sys, os
            parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            from exports.exports import export_dataframe_to_excel
        except ImportError as e:
            from tkinter import messagebox
            messagebox.showerror("Export Excel", "Le module d'export Excel n'est pas disponible.")
            return

        try:
            conn = get_connection()
            fields = conn.execute(
                "SELECT * FROM event_module_fields WHERE module_id = ? ORDER BY id", (self.module_id,)
            ).fetchall()
            rows = conn.execute(
                "SELECT row_index FROM event_module_data WHERE module_id = ? GROUP BY row_index ORDER BY row_index", (self.module_id,)
            ).fetchall()
            headers = [f["nom_champ"] for f in fields]
            data = []
            for row in rows:
                values = []
                for f in fields:
                    val = conn.execute(
                        "SELECT valeur FROM event_module_data WHERE module_id=? AND row_index=? AND field_id=?",
                        (self.module_id, row["row_index"], f["id"])
                    ).fetchone()
                    values.append("" if not val else val["valeur"])
                data.append(values)
            import pandas as pd
            df = pd.DataFrame(data, columns=headers)
            conn.close()
            export_dataframe_to_excel(df, title="Export Excel - Module personnalisé")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'export Excel du module personnalisé."))