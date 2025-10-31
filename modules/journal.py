import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from db.db import get_connection
from exports.exports import (
    export_dataframe_to_excel,
    export_dataframe_to_pdf,
    export_dataframe_to_csv
)

class JournalModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Journal Général")
        self.top.geometry("1200x700")
        self.create_widgets()
        self.refresh_journal()

    def create_widgets(self):
        # Zone filtres/recherche/export
        filter_frame = tk.Frame(self.top)
        filter_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(filter_frame, text="Recherche :").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=32)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self.apply_filter())
        tk.Button(filter_frame, text="Filtrer", command=self.apply_filter).pack(side=tk.LEFT, padx=4)
        tk.Button(filter_frame, text="Effacer", command=self.clear_filter).pack(side=tk.LEFT, padx=4)
        tk.Button(filter_frame, text="Exporter Excel", command=self.export_excel).pack(side=tk.RIGHT, padx=4)
        tk.Button(filter_frame, text="Exporter PDF", command=self.export_pdf).pack(side=tk.RIGHT, padx=4)
        tk.Button(filter_frame, text="Exporter CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=4)

        # Tableau principal
        columns = ("date", "type", "libelle", "montant", "justificatif")
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings")
        for col, text, w, anchor in zip(
            columns,
            ["Date", "Type", "Libellé", "Montant (€)", "Justificatif/Commentaire"],
            [100, 150, 290, 120, 470],
            ["center", "w", "w", "e", "w"]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor=anchor)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)

        # Scrollbars
        vsb = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.top, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        # Ligne de total et solde progressif
        self.total_var = tk.StringVar()
        self.recette_var = tk.StringVar()
        self.depense_var = tk.StringVar()
        self.solde_ouv_var = tk.StringVar()
        total_frame = tk.Frame(self.top)
        total_frame.pack(fill=tk.X, padx=6, pady=3)
        tk.Label(total_frame, textvariable=self.solde_ouv_var, anchor="e", fg="orange").pack(side=tk.LEFT, padx=(0, 15))
        tk.Label(total_frame, textvariable=self.recette_var, anchor="e", fg="green").pack(side=tk.LEFT)
        tk.Label(total_frame, textvariable=self.depense_var, anchor="e", fg="red").pack(side=tk.LEFT, padx=(15,0))
        tk.Label(total_frame, textvariable=self.total_var, anchor="e", fg="blue").pack(side=tk.RIGHT)

        # Double-clic pour détail
        self.tree.bind("<Double-1>", self.show_detail)

        # Bouton fermer
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

    def refresh_journal(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        # Récupérer le solde d'ouverture
        solde_ouverture = 0.0
        try:
            row = conn.execute("SELECT solde_report FROM config ORDER BY id DESC LIMIT 1").fetchone()
            if row and row[0] is not None:
                solde_ouverture = float(row[0])
        except Exception:
            pass
        df = pd.read_sql_query("""
            SELECT date, 'Recette' as type, source as libelle, montant, justificatif FROM dons_subventions
            UNION ALL
            SELECT e.date as date, 'Recette évènement', er.source, er.montant, er.commentaire
                FROM event_recettes er
                JOIN events e ON er.event_id = e.id
            UNION ALL
            SELECT date_depense as date, 'Dépense régulière', categorie, -montant, commentaire AS justificatif FROM depenses_regulieres
            UNION ALL
            SELECT date_depense as date, 'Dépense diverse', commentaire, -montant, commentaire AS justificatif FROM depenses_diverses
            UNION ALL
            SELECT e.date as date, 'Dépense évènement', ed.categorie, -ed.montant, ed.commentaire
                FROM event_depenses ed
                JOIN events e ON ed.event_id = e.id
            ORDER BY date
        """, conn)
        # Ajout du solde progressif avec solde d'ouverture
        df = df.copy()
        try:
            df["montant"] = df["montant"].astype(float)
        except Exception:
            pass
        df["Solde"] = df["montant"].cumsum() + solde_ouverture
        self.df = df
        self.solde_ouverture = solde_ouverture
        self.populate_table(self.df)
        conn.close()

    def populate_table(self, df):
        self.tree.delete(*self.tree.get_children())
        total = self.solde_ouverture
        total_recettes = 0
        total_depenses = 0
        for _, row in df.iterrows():
            montant = row["montant"]
            try:
                montant_float = float(montant)
            except Exception:
                montant_float = 0
            total += montant_float
            if montant_float > 0:
                total_recettes += montant_float
            else:
                total_depenses += montant_float  # négatif
            # Couleur selon type
            tags = []
            if montant_float > 0:
                tags.append("recette")
            elif montant_float < 0:
                tags.append("depense")
            self.tree.insert(
                "", "end",
                values=(row["date"], row["type"], row["libelle"], f"{montant_float:.2f}", row["justificatif"]),
                tags=tags
            )
        self.tree.tag_configure('depense', background="#ffeaea")
        self.tree.tag_configure('recette', background="#eaffea")
        self.solde_ouv_var.set(f"Solde d'ouverture : {self.solde_ouverture:.2f} €")
        self.total_var.set(f"Solde global : {total:.2f} €")
        self.recette_var.set(f"Total recettes : {total_recettes:.2f} €")
        self.depense_var.set(f"Total dépenses : {abs(total_depenses):.2f} €")

    def apply_filter(self):
        term = self.search_var.get().lower()
        if not term:
            self.populate_table(self.df)
            return
        mask = self.df.apply(lambda row: row.astype(str).str.lower().str.contains(term).any(), axis=1)
        filtered = self.df[mask]
        self.populate_table(filtered)

    def clear_filter(self):
        self.search_var.set("")
        self.populate_table(self.df)

    def export_excel(self):
        if hasattr(self, 'df') and not self.df.empty:
            export_dataframe_to_excel(self.df, title="Export Excel - Journal Général")

    def export_pdf(self):
        if hasattr(self, 'df') and not self.df.empty:
            export_dataframe_to_pdf(self.df, title="Export PDF - Journal Général")

    def export_csv(self):
        if hasattr(self, 'df') and not self.df.empty:
            export_dataframe_to_csv(self.df, title="Export CSV - Journal Général")

    def show_detail(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            vals = self.tree.item(item)['values']
            cols = ["Date", "Type", "Libellé", "Montant (€)", "Justificatif/Commentaire"]
            tk.messagebox.showinfo("Détail écriture", "\n".join(f"{c} : {v}" for c, v in zip(cols, vals)))