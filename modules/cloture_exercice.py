import tkinter as tk
from tkinter import messagebox, filedialog
import zipfile
import os
import pandas as pd

from db.db import get_connection
from exports.exports import (
    export_bilan_reporte_pdf,
    export_bilan_argumente_pdf,
    export_bilan_argumente_word
)
from dialogs.cloture_confirm_dialog import ClotureConfirmDialog

class ClotureExerciceModule:
    def __init__(self, master, visualisation_mode=False):
        self.master = master
        self.visualisation_mode = visualisation_mode
        self.top = tk.Toplevel(master)
        self.top.title("Clôture de l'exercice")
        self.top.geometry("520x420")
        self.create_widgets()

    def create_widgets(self):
        row = 0
        tk.Label(self.top, text="Clôture d'exercice annuel", font=("Arial", 15, "bold")).grid(row=row, column=0, columnspan=2, pady=14)
        row += 1
        tk.Label(self.top, text="• Cette opération va :\n"
                               "- Exporter toutes les tables de la base sous forme CSV\n"
                               "- Générer une archive ZIP pour archivage ou visualisation\n"
                               "- Permettre l'édition d'un bilan PDF rédigé\n"
                               "- Permettre l'édition d'un bilan FIN D'EXERCICE argumenté PDF ou Word\n"
                               "- (Optionnel) Réinitialiser les données pour le nouvel exercice\n\n"
                               "⚠️ Cette opération est IRRÉVERSIBLE", fg="red").grid(row=row, column=0, columnspan=2, pady=8)
        row += 1
        tk.Button(self.top, text="Exporter l'exercice en ZIP", command=self.export_zip, width=36).grid(row=row, column=0, columnspan=2, pady=18)
        row += 1
        tk.Button(self.top, text="Exporter le bilan PDF rédigé", command=self.export_bilan_pdf, width=36).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        tk.Button(self.top, text="Exporter le bilan FIN D'EXERCICE (argumenté PDF)", command=export_bilan_argumente_pdf, width=36).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        tk.Button(self.top, text="Exporter le bilan FIN D'EXERCICE (argumenté Word)", command=export_bilan_argumente_word, width=36).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        tk.Button(self.top, text="Réinitialiser la base de données", command=self.cloture_confirm, width=36, fg="red").grid(row=row, column=0, columnspan=2, pady=14)
        row += 1
        tk.Button(self.top, text="Fermer", command=self.top.destroy, width=16).grid(row=row, column=1, pady=6, sticky="e")


    def export_zip(self):
        tables = [
            "events", "event_modules", "event_module_fields", "event_module_data",
            "members", "dons_subventions", "depenses_regulieres", "depenses_diverses",
            "journal", "categories", "stock"
        ]
        file_path = filedialog.asksaveasfilename(
            title="Enregistrer l'exercice (ZIP)",
            defaultextension=".zip",
            filetypes=[("Archive ZIP", "*.zip")]
        )
        if not file_path:
            return
        tmp_dir = "tmp_cloture_export"
        os.makedirs(tmp_dir, exist_ok=True)
        conn = get_connection()
        for tab in tables:
            df = pd.read_sql_query(f"SELECT * FROM {tab}", conn)
            df.to_csv(os.path.join(tmp_dir, f"{tab}.csv"), index=False, encoding="utf-8")
        conn.close()
        with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for tab in tables:
                zf.write(os.path.join(tmp_dir, f"{tab}.csv"), arcname=f"{tab}.csv")
        # Clean temp
        for tab in tables:
            try:
                os.remove(os.path.join(tmp_dir, f"{tab}.csv"))
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass
        messagebox.showinfo("Clôture", f"Archive exportée :\n{file_path}")

    def export_bilan_pdf(self):
        # Tu peux adapter ici pour rassembler les synthèses nécessaires
        # Par exemple, synthèse événements, dépenses, dons...
        # Ici, on mocke des DataFrames pour la démonstration
        synth_evt = pd.DataFrame([
            {"evenement": "Marché de Noël", "recettes": 1200, "depenses": 400, "solde": 800},
            {"evenement": "Vente de gâteaux", "recettes": 450, "depenses": 100, "solde": 350}
        ])
        synth_dep = pd.DataFrame([
            {"origine": "Marché de Noël", "categorie": "Fournitures", "total": 300},
            {"origine": "Vente de gâteaux", "categorie": "Ingrédients", "total": 100}
        ])
        recap = {"synth_evt": synth_evt, "synth_dep": synth_dep}
        exercice = "2023-2024"
        date = "2023-09-01"
        date_fin = "2024-08-31"
        export_bilan_reporte_pdf(recap, self.top, exercice, date, date_fin)

    def cloture_confirm(self):
        ClotureConfirmDialog(self.top)