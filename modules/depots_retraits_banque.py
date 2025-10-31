import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_df_or_sql, get_connection
import pandas as pd
from datetime import date

class DepotsRetraitsBanqueModule:
    def __init__(self, master):
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("Suivi des Dépôts/Retraits à la Banque")
        self.top.geometry("900x500")
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        frm_btn = tk.Frame(self.top)
        frm_btn.pack(fill=tk.X, pady=4)

        tk.Button(frm_btn, text="Ajouter Mouvement", command=self.ajouter_mouvement).pack(side=tk.LEFT, padx=5)
        tk.Button(frm_btn, text="Supprimer sélection", command=self.supprimer_selection).pack(side=tk.LEFT, padx=5)
        tk.Button(frm_btn, text="Exporter Excel", command=self.exporter_excel).pack(side=tk.LEFT, padx=5)
        tk.Label(frm_btn, text="Filtrer par banque:").pack(side=tk.LEFT, padx=10)
        self.var_banque = tk.StringVar()
        self.cmb_banque = ttk.Combobox(frm_btn, textvariable=self.var_banque, width=15, state="readonly")
        self.cmb_banque.pack(side=tk.LEFT)
        self.cmb_banque.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        tk.Button(frm_btn, text="Tout afficher", command=lambda: self.var_banque.set('')).pack(side=tk.LEFT, padx=3)

        self.tree = ttk.Treeview(
            self.top,
            columns=("id", "date", "type", "montant", "reference", "banque", "pointe", "commentaire"),
            show="headings", selectmode="browse"
        )
        for col, w in zip(
            ("id", "date", "type", "montant", "reference", "banque", "pointe", "commentaire"),
            [0, 90, 120, 90, 110, 90, 60, 250]
        ):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w)
        self.tree["displaycolumns"] = ("date", "type", "montant", "reference", "banque", "pointe", "commentaire")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.tree.bind("<Double-1>", self.toggle_pointage)

    def refresh_table(self):
        banque = self.var_banque.get()
        query = "SELECT * FROM depots_retraits_banque"
        if banque:
            query += " WHERE banque = ?"
            df = pd.read_sql_query(query, get_connection(), params=(banque,))
        else:
            df = get_df_or_sql("depots_retraits_banque")

        banques = sorted(get_df_or_sql("SELECT DISTINCT banque FROM depots_retraits_banque WHERE banque IS NOT NULL AND banque!=''")["banque"].unique().tolist())
        self.cmb_banque["values"] = [""] + banques

        self.tree.delete(*self.tree.get_children())
        for _, row in df.iterrows():
            self.tree.insert(
                "", "end", iid=row["id"],
                values=(
                    row["id"],
                    row["date"],
                    row["type"],
                    f"{row['montant']:.2f}",
                    row.get("reference", ""),
                    row.get("banque", ""),
                    "Oui" if row.get("pointe", 0) else "Non",
                    row.get("commentaire", "")
                )
            )

    def ajouter_mouvement(self):
        win = tk.Toplevel(self.top)
        win.title("Ajouter un dépôt/retrait")
        win.transient(self.top)

        tk.Label(win, text="Date (AAAA-MM-JJ):").grid(row=0, column=0, sticky="e")
        ent_date = tk.Entry(win)
        ent_date.insert(0, date.today().isoformat())
        ent_date.grid(row=0, column=1)

        tk.Label(win, text="Type:").grid(row=1, column=0, sticky="e")
        cmb_type = ttk.Combobox(win, values=["Dépôt chèque", "Dépôt espèces", "Retrait espèces"], state="readonly")
        cmb_type.grid(row=1, column=1)
        cmb_type.set("Dépôt chèque")

        tk.Label(win, text="Montant (€):").grid(row=2, column=0, sticky="e")
        ent_montant = tk.Entry(win)
        ent_montant.grid(row=2, column=1)

        tk.Label(win, text="Référence (bordereau, etc.):").grid(row=3, column=0, sticky="e")
        ent_reference = tk.Entry(win)
        ent_reference.grid(row=3, column=1)

        tk.Label(win, text="Banque:").grid(row=4, column=0, sticky="e")
        ent_banque = tk.Entry(win)
        ent_banque.grid(row=4, column=1)

        tk.Label(win, text="Commentaire:").grid(row=5, column=0, sticky="e")
        ent_comment = tk.Entry(win)
        ent_comment.grid(row=5, column=1)

        def valider():
            try:
                montant = float(ent_montant.get().replace(",", "."))
                if not ent_date.get():
                    raise ValueError("Date obligatoire")
                if montant == 0:
                    raise ValueError("Montant nul")
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    """INSERT INTO depots_retraits_banque (date, type, montant, reference, banque, commentaire)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        ent_date.get(),
                        cmb_type.get(),
                        montant,
                        ent_reference.get(),
                        ent_banque.get(),
                        ent_comment.get(),
                    ),
                )
                conn.commit()
                conn.close()
                win.destroy()
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(win, text="Enregistrer", command=valider).grid(row=6, column=0, columnspan=2, pady=8)

    def supprimer_selection(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Suppression", "Sélectionnez une ligne à supprimer.")
            return
        if messagebox.askyesno("Suppression", "Supprimer cet enregistrement ?"):
            id_ = sel[0]
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM depots_retraits_banque WHERE id=?", (id_,))
            conn.commit()
            conn.close()
            self.refresh_table()

    def toggle_pointage(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        id_ = int(item)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT pointe FROM depots_retraits_banque WHERE id=?", (id_,))
        row = c.fetchone()
        if row:
            new_val = 0 if row[0] else 1
            c.execute("UPDATE depots_retraits_banque SET pointe=? WHERE id=?", (new_val, id_))
            conn.commit()
        conn.close()
        self.refresh_table()

    def exporter_excel(self):
        df = get_df_or_sql("depots_retraits_banque")
        try:
            df.to_excel("depots_retraits_banque.xlsx", index=False)
            messagebox.showinfo("Export", "Export Excel effectué dans le fichier depots_retraits_banque.xlsx")
        except Exception as e:
            messagebox.showerror("Export", "Erreur export : " + str(e))