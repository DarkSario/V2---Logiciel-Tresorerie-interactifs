import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection
import sqlite3

def get_conn():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

def list_evenements():
    conn = get_conn()
    rows = conn.execute("SELECT id, name, date FROM events ORDER BY date DESC").fetchall()
    conn.close()
    return rows

def get_inventaire_par_evenement(event_id, typ):
    conn = get_conn()
    inv = conn.execute("""
        SELECT * FROM buvette_inventaires
        WHERE event_id=? AND type_inventaire=?
        ORDER BY date_inventaire ASC
        LIMIT 1
    """, (event_id, typ)).fetchone()
    conn.close()
    return inv

def get_lignes_inventaire(inv_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, a.name as article_name, a.categorie, a.unite
        FROM buvette_inventaire_lignes l
        LEFT JOIN buvette_articles a ON l.article_id = a.id
        WHERE l.inventaire_id=?
        ORDER BY a.name
    """, (inv_id,)).fetchall()
    conn.close()
    return rows

def get_prix_moyen_achat(article_id, jusqua_date=None):
    conn = get_conn()
    q = "SELECT SUM(quantite*prix_unitaire) as total, SUM(quantite) as qte FROM buvette_achats WHERE article_id=?"
    params = [article_id]
    if jusqua_date:
        q += " AND date_achat<=?"
        params.append(jusqua_date)
    row = conn.execute(q, params).fetchone()
    conn.close()
    if row and row["qte"]:
        return row["total"]/row["qte"]
    return 0.0

def get_recette_buvette(event_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT SUM(montant) as recette
        FROM buvette_recettes
        WHERE event_id=?
    """, (event_id,)).fetchone()
    conn.close()
    return row["recette"] or 0.0

class BuvetteBilanDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Bilan Buvette par événement")
        self.geometry("900x600")
        self.create_widgets()

    def create_widgets(self):
        frm_select = tk.Frame(self)
        frm_select.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(frm_select, text="Événement :").pack(side=tk.LEFT)
        self.event_combo = ttk.Combobox(frm_select, state="readonly", width=50)
        events = list_evenements()
        self.events = {f"{ev['date']} - {ev['name']}": ev['id'] for ev in events}
        self.event_combo["values"] = list(self.events.keys())
        self.event_combo.pack(side=tk.LEFT, padx=4)
        tk.Button(frm_select, text="Voir bilan", command=self.display_bilan).pack(side=tk.LEFT, padx=12)

        self.text = tk.Text(self, height=30, width=120)
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    def display_bilan(self):
        evt_label = self.event_combo.get()
        if not evt_label or evt_label not in self.events:
            messagebox.showwarning("Événement", "Sélectionnez un événement.")
            return
        event_id = self.events[evt_label]

        inv_avant = get_inventaire_par_evenement(event_id, "avant")
        inv_apres = get_inventaire_par_evenement(event_id, "apres")

        bilan_txt = f"BILAN BUVETTE - {evt_label}\n"
        bilan_txt += "\n--- Inventaire AVANT ---\n"
        if inv_avant:
            lignes_avant = get_lignes_inventaire(inv_avant["id"])
            for l in lignes_avant:
                bilan_txt += f"{l['article_name']}: {l['quantite']} {l['unite']} ({l['categorie']})\n"
        else:
            bilan_txt += "Aucun inventaire avant.\n"

        bilan_txt += "\n--- Inventaire APRES ---\n"
        if inv_apres:
            lignes_apres = get_lignes_inventaire(inv_apres["id"])
            for l in lignes_apres:
                bilan_txt += f"{l['article_name']}: {l['quantite']} {l['unite']} ({l['categorie']})\n"
        else:
            bilan_txt += "Aucun inventaire après.\n"

        bilan_txt += "\n--- Recette Buvette ---\n"
        recette = get_recette_buvette(event_id)
        bilan_txt += f"Total recettes buvette : {recette:.2f} €\n"

        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, bilan_txt)