import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection, DataSource, get_df_or_sql
from dialogs.edit_field_dialog import EditFieldDialog
from utils.error_handler import handle_exception
from utils.app_logger import get_logger

logger = get_logger("event_module_fields")

class EventModuleFieldsWindow(tk.Toplevel):
    def __init__(self, master, module_id):
        super().__init__(master)
        self.title("Champs du module personnalisé")
        self.module_id = module_id
        self.create_widgets()
        self.refresh_fields()

    def create_widgets(self):
        columns = ("id", "nom_champ", "type_champ", "prix_unitaire", "modele_colonne")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=60)
        self.tree.heading("nom_champ", text="Nom")
        self.tree.column("nom_champ", width=180)
        self.tree.heading("type_champ", text="Type")
        self.tree.column("type_champ", width=80)
        self.tree.heading("prix_unitaire", text="Prix unitaire (€)")
        self.tree.column("prix_unitaire", width=120)
        self.tree.heading("modele_colonne", text="Modèle colonne")
        self.tree.column("modele_colonne", width=140)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="Ajouter", command=self.add_field).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Modifier", command=self.edit_field).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_field).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Éditer prix", command=self.edit_field_price).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=6)

    def refresh_fields(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            if getattr(DataSource, "is_visualisation", False):
                df = get_df_or_sql("event_module_fields")
                dict_items = df[df["module_id"] == self.module_id].to_dict("records")
            else:
                conn = get_connection()
                dict_items = conn.execute(
                    "SELECT id, nom_champ, type_champ, prix_unitaire, modele_colonne FROM event_module_fields WHERE module_id=? ORDER BY id", (self.module_id,)
                ).fetchall()
                conn.close()
            for item in dict_items:
                prix = item["prix_unitaire"] if isinstance(item, dict) else item[3]
                prix_aff = f"{float(prix):.2f}" if prix not in (None, "", 0) else ""
                modele = item["modele_colonne"] if isinstance(item, dict) else item[4]
                vals = [
                    item["id"] if isinstance(item, dict) else item[0],
                    item["nom_champ"] if isinstance(item, dict) else item[1],
                    item["type_champ"] if isinstance(item, dict) else item[2],
                    prix_aff,
                    modele or ""
                ]
                self.tree.insert("", "end", values=vals)
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des champs du module."))

    def get_selected_field_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un champ.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_field(self):
        try:
            EditFieldDialog(self, self.module_id, None, on_save=self.refresh_fields, with_modele_colonne=True)
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'ajout d'un champ."))

    def edit_field(self):
        fid = self.get_selected_field_id()
        if fid is not None:
            try:
                EditFieldDialog(self, self.module_id, fid, on_save=self.refresh_fields, with_modele_colonne=True)
            except Exception as e:
                messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la modification du champ."))

    def delete_field(self):
        fid = self.get_selected_field_id()
        if fid is not None and messagebox.askyesno("Suppression", "Supprimer ce champ ?"):
            try:
                conn = get_connection()
                conn.execute("DELETE FROM event_module_fields WHERE id=?", (fid,))
                conn.commit()
                conn.close()
                self.refresh_fields()
            except Exception as e:
                messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression du champ."))

    def edit_field_price(self):
        fid = self.get_selected_field_id()
        if fid is None:
            return
        try:
            conn = get_connection()
            champ = conn.execute("SELECT nom_champ, prix_unitaire FROM event_module_fields WHERE id=?", (fid,)).fetchone()
            conn.close()
            if champ is None:
                return
            old_price = champ["prix_unitaire"]
            new_price = simpledialog.askstring(
                "Prix unitaire",
                f"Nouveau prix unitaire (€) pour « {champ['nom_champ']} » (laisser vide pour aucun) :",
                initialvalue=str(old_price) if old_price not in (None, "") else ""
            )
            if new_price is None:
                return  # Annulé
            conn = get_connection()
            conn.execute("UPDATE event_module_fields SET prix_unitaire=? WHERE id=?", (new_price if new_price else None, fid))
            conn.commit()
            conn.close()
            self.refresh_fields()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la modification du prix du champ."))