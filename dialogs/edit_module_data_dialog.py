import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection, get_df_or_sql
from utils.error_handler import handle_errors

# Optionally handle DataSource if present
try:
    from db.db import DataSource
    HAS_DATASOURCE = True
except ImportError:
    HAS_DATASOURCE = False

def get_modele_colonne(fid):
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT modele_colonne FROM event_module_fields WHERE id=?", (fid,)
        ).fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        pass
    return None

def get_choix_for_modele(modele_colonne):
    try:
        conn = get_connection()
        res = conn.execute(
            "SELECT valeur FROM valeurs_modeles_colonnes WHERE modele_id=(SELECT id FROM colonnes_modeles WHERE name=?)",
            (modele_colonne,)
        ).fetchall()
        conn.close()
        return [r["valeur"] for r in res]
    except Exception:
        return []

class EditModuleDataDialog(tk.Toplevel):
    def __init__(self, master, module_id, row_index, fields, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier ligne de données")
        self.module_id = module_id
        self.row_index = row_index
        self.fields = fields
        self.on_save = on_save
        self.widgets = []
        self.vars = []
        self.geometry("520x%s" % (100 + 40*len(fields)))
        self.resizable(False, False)

        # Ajout dynamique des champs avec ComboBox si modèle, sinon Entry
        for i, (fid, label, *rest) in enumerate(self._fields_with_modele()):
            modele_colonne = rest[0] if rest else None
            tk.Label(self, text=label+" :").grid(row=i, column=0, sticky="w", padx=12, pady=8)
            var = tk.StringVar()
            if modele_colonne:
                choix = get_choix_for_modele(modele_colonne)
                widget = ttk.Combobox(self, textvariable=var, values=choix, state="readonly")
                if choix:
                    var.set(choix[0])
            else:
                widget = tk.Entry(self, textvariable=var, width=38)
            widget.grid(row=i, column=1, pady=2)
            self.widgets.append(widget)
            self.vars.append(var)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(self.fields), column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.row_index is not None:
            self.prefill_fields()

    def _fields_with_modele(self):
        # Retourne (field_id, label, modele_colonne) pour chaque champ
        for f in self.fields:
            if len(f) >= 3:
                yield (f[0], f[1], f[2])
            else:
                modele = get_modele_colonne(f[0])
                yield (f[0], f[1], modele)

    def prefill_fields(self):
        try:
            if HAS_DATASOURCE and getattr(DataSource, "is_visualisation", False):
                df = get_df_or_sql("event_module_data")
                df = df[(df["module_id"] == self.module_id) & (df["row_index"] == self.row_index)]
                values = {row["field_id"]: row["valeur"] for _, row in df.iterrows()}
            else:
                conn = get_connection()
                rows = conn.execute(
                    "SELECT field_id, valeur FROM event_module_data WHERE module_id=? AND row_index=?",
                    (self.module_id, self.row_index)
                ).fetchall()
                conn.close()
                values = {fid: v for fid, v in rows}
            for i, (fid, _, *_) in enumerate(self._fields_with_modele()):
                self.vars[i].set(values.get(fid, ""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement des données du module : {e}")

    @handle_errors
    def save(self):
        vals = [v.get().strip() for v in self.vars]
        if any(not v for v in vals):
            if not messagebox.askyesno("Champs vides", "Certains champs sont vides. Continuer ?"):
                return
        conn = get_connection()
        try:
            if self.row_index is None:
                rowidx = conn.execute(
                    "SELECT MAX(row_index) FROM event_module_data WHERE module_id=?", (self.module_id,)
                ).fetchone()[0]
                rowidx = (rowidx or 0) + 1
            else:
                rowidx = self.row_index
                conn.execute("DELETE FROM event_module_data WHERE module_id=? AND row_index=?", (self.module_id, rowidx))
            for i, (fid, _, *_) in enumerate(self._fields_with_modele()):
                conn.execute(
                    "INSERT INTO event_module_data (module_id, row_index, field_id, valeur) VALUES (?, ?, ?, ?)",
                    (self.module_id, rowidx, fid, vals[i])
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()