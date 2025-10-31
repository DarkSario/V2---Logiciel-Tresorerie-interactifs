import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from db.db import get_df_or_sql, get_connection
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("Le module 'matplotlib' est requis pour le tableau de bord. Installe-le : python -m pip install matplotlib")
    print("Note: Si tu utilises tkinter, assure-toi qu'il est installé : sur Linux, tu peux avoir besoin de 'python3-tk'")
    raise

class DashboardModule:
    def __init__(self, master, visualisation_mode=False):
        self.master = master
        self.visualisation_mode = visualisation_mode
        self.top = tk.Toplevel(master)
        self.top.title("Tableau de bord")
        self.top.geometry("1100x650")
        self.create_widgets()
        self.refresh_dashboard()

    def create_widgets(self):
        self.tabs = ttk.Notebook(self.top)
        self.tab_resume = tk.Frame(self.tabs)
        self.tab_evenements = tk.Frame(self.tabs)
        self.tab_finances = tk.Frame(self.tabs)
        self.tab_graphs = tk.Frame(self.tabs)
        self.tabs.add(self.tab_resume, text="Résumé")
        self.tabs.add(self.tab_evenements, text="Événements")
        self.tabs.add(self.tab_finances, text="Finances")
        self.tabs.add(self.tab_graphs, text="Graphiques")
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.text_resume = tk.Text(self.tab_resume, height=10, font=("Arial", 11))
        self.text_resume.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        tk.Label(self.tab_resume, text="5 dernières opérations :", font=("Arial", 10, "bold")).pack()
        self.tree_last_ops = ttk.Treeview(self.tab_resume, columns=("date", "type", "libelle", "montant"), show="headings")
        for col, w in zip(("date", "type", "libelle", "montant"), [90, 120, 250, 95]):
            self.tree_last_ops.heading(col, text=col.capitalize())
            self.tree_last_ops.column(col, width=w)
        self.tree_last_ops.pack(fill=tk.X, expand=False, padx=10, pady=3)

        self.tree_evenements = ttk.Treeview(self.tab_evenements, columns=("evenement", "recettes", "depenses", "solde"), show="headings")
        for col, w in zip(("evenement", "recettes", "depenses", "solde"), [220, 90, 90, 90]):
            self.tree_evenements.heading(col, text=col.capitalize())
            self.tree_evenements.column(col, width=w)
        self.tree_evenements.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tree_finances = ttk.Treeview(self.tab_finances, columns=("categorie", "total"), show="headings")
        for col, w in zip(("categorie", "total"), [300, 120]):
            self.tree_finances.heading(col, text=col.capitalize())
            self.tree_finances.column(col, width=w)
        self.tree_finances.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.graph_frame = tk.Frame(self.tab_graphs)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

    def refresh_dashboard(self):
        self.text_resume.delete("1.0", tk.END)
        self.tree_evenements.delete(*self.tree_evenements.get_children())
        self.tree_finances.delete(*self.tree_finances.get_children())
        self.tree_last_ops.delete(*self.tree_last_ops.get_children())
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        total_membres = len(get_df_or_sql("membres"))
        total_events = len(get_df_or_sql("events"))
        total_stock = len(get_df_or_sql("stock"))
        df_dons = get_df_or_sql("dons_subventions")
        df_evt_recettes = get_df_or_sql("event_recettes")
        total_dons = df_dons["montant"].sum() if not df_dons.empty else 0
        total_evt_recettes = df_evt_recettes["montant"].sum() if not df_evt_recettes.empty else 0
        total_recettes = total_dons + total_evt_recettes

        df_reg = get_df_or_sql("depenses_regulieres")
        df_div = get_df_or_sql("depenses_diverses")
        df_evtdep = get_df_or_sql("event_depenses")
        total_depenses = (
            df_reg["montant"].sum() if not df_reg.empty else 0
        ) + (
            df_div["montant"].sum() if not df_div.empty else 0
        ) + (
            df_evtdep["montant"].sum() if not df_evtdep.empty else 0
        )

        solde = total_recettes - total_depenses
        resume = (
            f"🧑 Membres : {total_membres}\n"
            f"🎉 Événements : {total_events}\n"
            f"📦 Articles en stock : {total_stock}\n"
            f"💰 Dons/subventions : {total_dons:.2f} €\n"
            f"💰 Recettes événements : {total_evt_recettes:.2f} €\n"
            f"💰 Total recettes : {total_recettes:.2f} €\n"
            f"💸 Total dépenses : {total_depenses:.2f} €\n"
            f"💼 Solde actuel : {solde:.2f} €\n"
        )
        self.text_resume.insert("1.0", resume)

        # Dernières opérations (journal général synthétique)
        try:
            conn = get_connection()
            df_ops = pd.read_sql_query(
                """
                SELECT date, 'Recette' as type, source as libelle, montant FROM dons_subventions
                UNION ALL
                SELECT e.date as date, 'Recette évènement', er.source, er.montant
                    FROM event_recettes er
                    JOIN events e ON er.event_id = e.id
                UNION ALL
                SELECT date_depense as date, 'Dépense régulière', categorie, -montant FROM depenses_regulieres
                UNION ALL
                SELECT date_depense as date, 'Dépense diverse', commentaire, -montant FROM depenses_diverses
                UNION ALL
                SELECT e.date as date, 'Dépense évènement', ed.categorie, -ed.montant
                    FROM event_depenses ed
                    JOIN events e ON ed.event_id = e.id
                ORDER BY date DESC
                LIMIT 5
                """, conn
            )
            conn.close()
            for _, row in df_ops.iterrows():
                self.tree_last_ops.insert("", "end", values=(row["date"], row["type"], row["libelle"], f"{row['montant']:.2f}"))
        except Exception:
            pass

        # Événements (synthèse)
        df_evt = get_df_or_sql("events")
        for _, row in df_evt.iterrows():
            name = row["name"] if "name" in row else row.get("evenement", "")
            try:
                id_evt = row["id"]
                recettes = get_df_or_sql(f"SELECT SUM(montant) FROM event_recettes WHERE event_id={id_evt}")["SUM(montant)"].iloc[0] or 0
                depenses = get_df_or_sql(f"SELECT SUM(montant) FROM event_depenses WHERE event_id={id_evt}")["SUM(montant)"].iloc[0] or 0
            except Exception:
                recettes = depenses = 0
            solde_evt = recettes - depenses
            self.tree_evenements.insert("", "end", values=(name, f"{recettes:.2f}", f"{depenses:.2f}", f"{solde_evt:.2f}"))

        # Finances par donateur/source/catégorie (dons + recettes évènement)
        if not df_dons.empty:
            dons_by_type = df_dons.groupby("source")["montant"].sum().reset_index()
            for _, row in dons_by_type.iterrows():
                self.tree_finances.insert("", "end", values=(row["source"], f"{row['montant']:.2f}"))
        if not df_evt_recettes.empty:
            evt_by_type = df_evt_recettes.groupby("source")["montant"].sum().reset_index()
            for _, row in evt_by_type.iterrows():
                self.tree_finances.insert("", "end", values=(f"Evt: {row['source']}", f"{row['montant']:.2f}"))

        self.display_graphs(
            total_dons, total_evt_recettes, total_depenses,
            df_dons, df_evt_recettes, df_reg, df_div, df_evtdep
        )

    def display_graphs(self, total_dons, total_evt_recettes, total_depenses, df_dons, df_evt_recettes, df_reg, df_div, df_evtdep):
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        recettes_labels = []
        recettes_vals = []
        if not df_dons.empty:
            dons_by_source = df_dons.groupby("source")["montant"].sum()
            for s, v in dons_by_source.items():
                label = s if len(str(s)) <= 28 else str(s)[:25] + "..."
                recettes_labels.append(label)
                recettes_vals.append(v)
        if not df_evt_recettes.empty:
            evt_by_source = df_evt_recettes.groupby("source")["montant"].sum()
            for s, v in evt_by_source.items():
                label = f"Evt: {s}" if len(str(s)) <= 23 else f"Evt: {str(s)[:20]}..."
                recettes_labels.append(label)
                recettes_vals.append(v)
        if not recettes_labels:
            recettes_labels = ["Aucune"]
            recettes_vals = [1]

        wedges1, _, autotexts1 = axes[0].pie(
            recettes_vals, labels=None, autopct='%1.1f%%', startangle=90
        )
        axes[0].set_title("Répartition Recettes")
        axes[0].legend(wedges1, recettes_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)

        depenses_labels = []
        depenses_vals = []
        if not df_reg.empty:
            depenses_labels.append("Dépenses régulières")
            depenses_vals.append(df_reg["montant"].sum())
        if not df_div.empty:
            depenses_labels.append("Dépenses diverses")
            depenses_vals.append(df_div["montant"].sum())
        if not df_evtdep.empty:
            depenses_labels.append("Dépenses événements")
            depenses_vals.append(df_evtdep["montant"].sum())
        if not depenses_labels:
            depenses_labels = ["Aucune"]
            depenses_vals = [1]
        wedges2, _, autotexts2 = axes[1].pie(
            depenses_vals, labels=None, autopct='%1.1f%%', startangle=90
        )
        axes[1].set_title("Répartition Dépenses")
        axes[1].legend(wedges2, depenses_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)