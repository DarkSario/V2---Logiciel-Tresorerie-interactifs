"""
Module pour la gestion centralisée des modèles de colonnes et de leurs listes de choix.
Utilise les tables colonnes_modeles et valeurs_modeles_colonnes pour cohérence avec le reste de l'application.
"""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from db.db import get_connection

def create_tables_if_needed():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS colonnes_modeles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type_modele TEXT DEFAULT 'TEXT'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS valeurs_modeles_colonnes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modele_id INTEGER,
            valeur TEXT,
            FOREIGN KEY(modele_id) REFERENCES colonnes_modeles(id)
        )
    """)
    conn.commit()
    conn.close()

def get_colonnes_connues():
    conn = get_connection()
    res = conn.execute("SELECT * FROM colonnes_modeles ORDER BY name").fetchall()
    conn.close()
    return res

def get_choix_pour_colonne(modele_id):
    conn = get_connection()
    res = conn.execute("SELECT valeur FROM valeurs_modeles_colonnes WHERE modele_id=? ORDER BY valeur", (modele_id,)).fetchall()
    conn.close()
    return [r['valeur'] for r in res]

def ajouter_modele_colonne(name, typ, valeurs):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO colonnes_modeles (name, type_modele) VALUES (?, ?)", (name, typ))
    modele_id = cur.execute("SELECT id FROM colonnes_modeles WHERE name=?", (name,)).fetchone()["id"]
    # Efface anciennes valeurs
    cur.execute("DELETE FROM valeurs_modeles_colonnes WHERE modele_id=?", (modele_id,))
    for v in valeurs:
        cur.execute("INSERT INTO valeurs_modeles_colonnes (modele_id, valeur) VALUES (?, ?)", (modele_id, v))
    conn.commit()
    conn.close()

class GestionModelColonnes(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gestion des modèles de colonnes")
        self.geometry("650x420")
        self.minsize(400, 200)
        self.maxsize(900, 600)
        create_tables_if_needed()
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_list()
        btns = tk.Frame(self)
        btns.pack(fill="x")
        tk.Button(btns, text="Ajouter un modèle", command=self.ajouter).pack(side="left", padx=5, pady=8)
        tk.Button(btns, text="Fermer", command=self.destroy).pack(side="right", padx=5, pady=8)

    def refresh_list(self):
        for w in self.frame.winfo_children():
            w.destroy()
        tk.Label(self.frame, text="Modèles existants :", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 6))
        colonnes = get_colonnes_connues()
        for c in colonnes:
            frm = tk.Frame(self.frame)
            frm.pack(fill="x", pady=2, anchor="w")
            tk.Label(frm, text=f"{c['name']} ({c['type_modele']})", anchor="w").pack(side="left")
            choix = get_choix_pour_colonne(c["id"])
            if choix:
                tk.Button(frm, text="Voir la liste", command=lambda cid=c["id"]: self.voir_liste_choix(cid)).pack(side="left", padx=4)
            tk.Button(frm, text="Modifier", command=lambda cid=c['id']: self.modifier(cid)).pack(side="left", padx=2)
            tk.Button(frm, text="Supprimer", command=lambda cid=c['id']: self.supprimer(cid)).pack(side="left", padx=2)

    def ajouter(self):
        ModeleColonneDialog(self, callback=self.refresh_list)

    def modifier(self, modele_id):
        ModeleColonneDialog(self, modele_id=modele_id, callback=self.refresh_list)

    def supprimer(self, modele_id):
        if messagebox.askyesno("Suppression", "Supprimer ce modèle ?"):
            conn = get_connection()
            conn.execute("DELETE FROM colonnes_modeles WHERE id=?", (modele_id,))
            conn.execute("DELETE FROM valeurs_modeles_colonnes WHERE modele_id=?", (modele_id,))
            conn.commit()
            conn.close()
            self.refresh_list()

    def voir_liste_choix(self, modele_id):
        choix = get_choix_pour_colonne(modele_id)
        txt = "\n".join(choix) if choix else "(Aucun choix enregistré)"
        top = tk.Toplevel(self)
        top.title("Liste des choix")
        top.geometry("350x300")
        tk.Label(top, text="Valeurs possibles :", font=("Arial", 10, "bold")).pack(pady=8)
        text = tk.Text(top, height=15, width=40)
        text.pack(padx=8, pady=8)
        text.insert("1.0", txt)
        text.config(state="disabled")
        tk.Button(top, text="Fermer", command=top.destroy).pack(pady=8)

class ModeleColonneDialog(tk.Toplevel):
    def __init__(self, master, modele_id=None, callback=None):
        super().__init__(master)
        self.callback = callback
        self.modele_id = modele_id
        self.title("Ajout/modification modèle colonne")
        self.geometry("400x240")
        self.nom_var = tk.StringVar()
        self.type_var = tk.StringVar(value="TEXT")
        self.valeurs_var = tk.StringVar()
        if modele_id:
            self.load_colonne(modele_id)
        tk.Label(self, text="Name colonne :").pack()
        tk.Entry(self, textvariable=self.nom_var).pack(fill="x", padx=8)
        tk.Label(self, text="Type :").pack()
        ttk.Combobox(self, textvariable=self.type_var, values=["TEXT", "INTEGER", "REAL"]).pack(fill="x", padx=8)
        tk.Label(self, text="Valeurs possibles (séparées par ;) :").pack()
        tk.Entry(self, textvariable=self.valeurs_var).pack(fill="x", padx=8)
        btns = tk.Frame(self)
        btns.pack(fill="x", pady=8)
        tk.Button(btns, text="Valider", command=self.valider).pack(side="left", padx=6)
        tk.Button(btns, text="Annuler", command=self.destroy).pack(side="right", padx=6)

    def load_colonne(self, modele_id):
        conn = get_connection()
        c = conn.execute("SELECT * FROM colonnes_modeles WHERE id=?", (modele_id,)).fetchone()
        self.nom_var.set(c["name"])
        self.type_var.set(c["type_modele"])
        choix = get_choix_pour_colonne(modele_id)
        self.valeurs_var.set(";".join(choix))
        conn.close()

    def valider(self):
        name = self.nom_var.get().strip()
        typ = self.type_var.get()
        valeurs = [v.strip() for v in self.valeurs_var.get().split(";") if v.strip()]
        if not name:
            messagebox.showerror("Erreur", "Name requis")
            return
        ajouter_modele_colonne(name, typ, valeurs)
        if self.callback:
            self.callback()
        self.destroy()

# Fenêtre d’ajout de colonne avec menu déroulant pour les modèles connus
def ask_add_custom_column(parent):
    create_tables_if_needed()
    colonnes = get_colonnes_connues()
    noms_colonnes = [c["name"] for c in colonnes]
    dlg = AddCustomColumnDialog(parent, noms_colonnes, colonnes)
    parent.wait_window(dlg)
    return dlg.result if hasattr(dlg, "result") else None

class AddCustomColumnDialog(tk.Toplevel):
    def __init__(self, master, noms_colonnes, colonnes):
        super().__init__(master)
        self.title("Ajouter une colonne")
        self.geometry("400x250")
        self.result = None
        self.colonnes = colonnes
        self.nom_var = tk.StringVar()
        self.type_var = tk.StringVar(value="TEXT")
        self.choix_var = tk.StringVar()
        self.choix_values = []
        self.choice_combobox = None
        self.selected_modele_colonne = None

        tk.Label(self, text="Name de colonne :").pack(anchor="w")
        self.combo_nom = ttk.Combobox(self, textvariable=self.nom_var, values=noms_colonnes)
        self.combo_nom.pack(fill="x", padx=8, pady=2)
        self.combo_nom.bind("<<ComboboxSelected>>", self.on_nom_selected)
        self.combo_nom.bind("<KeyRelease>", self.on_nom_typed)

        tk.Label(self, text="Type :").pack(anchor="w")
        self.combo_type = ttk.Combobox(self, textvariable=self.type_var, values=["TEXT", "INTEGER", "REAL"])
        self.combo_type.pack(fill="x", padx=8, pady=2)

        self.choix_frame = tk.Frame(self)
        self.choix_frame.pack(fill="x", padx=4, pady=4)

        btns = tk.Frame(self)
        btns.pack(fill="x", pady=8)
        tk.Button(btns, text="Valider", command=self.on_validate).pack(side="left", padx=6)
        tk.Button(btns, text="Annuler", command=self.destroy).pack(side="right", padx=6)
        tk.Button(btns, text="Gérer les modèles", command=lambda: GestionModelColonnes(self)).pack(side="right", padx=6)

    def clear_choix(self):
        for w in self.choix_frame.winfo_children():
            w.destroy()
        self.choix_values = []
        self.choice_combobox = None
        self.selected_modele_colonne = None

    def on_nom_selected(self, event=None):
        name = self.nom_var.get()
        self.clear_choix()
        col = next((c for c in self.colonnes if c["name"] == name), None)
        if col:
            self.type_var.set(col["type_modele"])
            self.selected_modele_colonne = col["name"]  # Correction : mémorise le modèle de colonne sélectionné
            choix = get_choix_pour_colonne(col["id"])
            if choix:
                tk.Label(self.choix_frame, text="Valeur à choisir :", font=("Arial", 10, "bold")).pack(anchor="w")
                self.choice_combobox = ttk.Combobox(self.choix_frame, values=choix, textvariable=self.choix_var)
                self.choice_combobox.pack(fill="x", padx=6, pady=2)
                self.choix_values = choix
        else:
            self.type_var.set("TEXT")
            self.selected_modele_colonne = None

    def on_nom_typed(self, event=None):
        # Si saisie libre (name non connu), effacer champ choix
        if self.nom_var.get() not in [c["name"] for c in self.colonnes]:
            self.clear_choix()
            self.type_var.set("TEXT")
            self.selected_modele_colonne = None

    def on_validate(self):
        name = self.nom_var.get().strip()
        typ = self.type_var.get().strip()
        valeur_choisie = self.choix_var.get().strip() if self.choice_combobox else None
        if not name:
            messagebox.showerror("Erreur", "Name de colonne requis")
            return
        result = {"name": name, "type": typ}
        # Correction : toujours transmettre le modele_colonne si c'est un modèle connu
        if self.selected_modele_colonne:
            result["modele_colonne"] = self.selected_modele_colonne
        else:
            result["modele_colonne"] = None
        if self.choice_combobox and valeur_choisie:
            result["valeur_choisie"] = valeur_choisie
        self.result = result
        self.destroy()