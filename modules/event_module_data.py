import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from db.db import get_connection, DataSource, get_df_or_sql
from utils.error_handler import handle_exception
from utils.app_logger import get_logger

logger = get_logger("event_module_data")

def ask_choice_value(parent, champ, choix):
    class ChoiceDialog(simpledialog.Dialog):
        def body(self, master):
            tk.Label(master, text=f"Valeur pour {champ} :").pack()
            self.var = tk.StringVar()
            self.combo = ttk.Combobox(master, textvariable=self.var, values=choix, state="readonly")
            self.combo.pack()
            if choix:
                self.combo.current(0)
            return self.combo
        def apply(self):
            self.result = self.var.get()
    d = ChoiceDialog(parent)
    return d.result

class EventModuleDataWindow(tk.Toplevel):
    def __init__(self, master, module_id):
        super().__init__(master)
        self.title("Données du module personnalisé")
        self.module_id = module_id
        try:
            self.fields = self.load_fields()
            self.create_widgets()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'initialisation de la fenêtre de données du module."))

    def load_fields(self):
        try:
            conn = get_connection()
            df = pd.read_sql_query(
                "SELECT id, nom_champ, modele_colonne FROM event_module_fields WHERE module_id=?",
                conn, params=(self.module_id,)
            )
            conn.close()
            return df.to_records(index=False)
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement des colonnes du module."))
            return []

    def create_widgets(self):
        cols = ["row_index"] + [f[1] for f in self.fields]
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="Ajouter", command=self.add_row).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Modifier", command=self.edit_row).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_row).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=6)

    def load_data(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            df = pd.read_sql_query("SELECT * FROM event_module_data WHERE module_id=? ORDER BY row_index", conn, params=(self.module_id,))
            conn.close()
            grouped = {}
            for _, row in df.iterrows():
                idx = row["row_index"]
                if idx not in grouped:
                    grouped[idx] = {}
                grouped[idx][row["field_id"]] = row["valeur"]
            for idx in sorted(grouped):
                vals = [idx] + [grouped[idx].get(f[0], "") for f in self.fields]
                self.tree.insert("", "end", values=vals)
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des données du module."))

    def get_selected_row_index(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_row(self):
        try:
            # Détermine le prochain row_index
            conn = get_connection()
            res = conn.execute("SELECT MAX(row_index) FROM event_module_data WHERE module_id=?", (self.module_id,)).fetchone()
            next_idx = (res[0] or 0) + 1
            conn.close()

            row_values = []
            for field in self.fields:
                field_id, nom_champ, modele_colonne = field
                if modele_colonne:
                    # Récupère les valeurs du modèle
                    conn = get_connection()
                    res = conn.execute(
                        "SELECT valeur FROM valeurs_modeles_colonnes WHERE modele_id=(SELECT id FROM colonnes_modeles WHERE name=?)",
                        (modele_colonne,)
                    ).fetchall()
                    conn.close()
                    choix = [r["valeur"] for r in res]
                    valeur = ask_choice_value(self, nom_champ, choix)
                else:
                    valeur = simpledialog.askstring("Saisie", f"Valeur pour {nom_champ} :", parent=self)
                if valeur is None:
                    return  # Annulé
                row_values.append((field_id, valeur))

            # Enregistre chaque valeur dans event_module_data
            conn = get_connection()
            for field_id, valeur in row_values:
                conn.execute(
                    "INSERT INTO event_module_data (module_id, row_index, field_id, valeur) VALUES (?, ?, ?, ?)",
                    (self.module_id, next_idx, field_id, valeur)
                )
            conn.commit()
            conn.close()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'ajout d'une ligne."))

    def edit_row(self):
        messagebox.showinfo("Non implémenté", "L'édition des lignes n'est pas encore implémentée !")

    def delete_row(self):
        rowidx = self.get_selected_row_index()
        if rowidx is not None and messagebox.askyesno("Suppression", f"Supprimer la ligne {rowidx} ?"):
            try:
                conn = get_connection()
                conn.execute("DELETE FROM event_module_data WHERE module_id=? AND row_index=?", (self.module_id, rowidx))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de la ligne."))