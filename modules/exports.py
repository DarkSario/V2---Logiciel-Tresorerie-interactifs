import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from db.db import get_connection

# ========== EXPORTS BILAN EVENEMENT ==========

def export_bilan_evenement(event_id, format="xlsx", filename=None):
    conn = get_connection()
    # Récup info événement
    event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        messagebox.showerror("Erreur", "Événement introuvable.")
        return

    # Données recettes
    recettes = pd.read_sql_query(
        "SELECT source, montant, commentaire, module_id FROM event_recettes WHERE event_id=?",
        conn, params=(event_id,)
    )
    # Données dépenses
    depenses = pd.read_sql_query(
        "SELECT categorie, montant, fournisseur, date_depense, paye_par, membre_id, commentaire FROM event_depenses WHERE event_id=?",
        conn, params=(event_id,)
    )
    # Données caisses
    caisses = pd.read_sql_query(
        "SELECT id, nom_caisse, commentaire FROM event_caisses WHERE event_id=?",
        conn, params=(event_id,)
    )
    # Détail fond de caisse
    caisses_details = []
    for _, caisse in caisses.iterrows():
        cid = caisse["id"]
        debut = conn.execute(
            "SELECT SUM(CASE WHEN type='cheque' THEN valeur ELSE valeur*quantite END) as total FROM event_caisse_details WHERE caisse_id=? AND moment='debut'", (cid,)
        ).fetchone()["total"] or 0.0
        fin = conn.execute(
            "SELECT SUM(CASE WHEN type='cheque' THEN valeur ELSE valeur*quantite END) as total FROM event_caisse_details WHERE caisse_id=? AND moment='fin'", (cid,)
        ).fetchone()["total"] or 0.0
        caisses_details.append({
            "Caisse": caisse["nom_caisse"],
            "Fond début (€)": f"{debut:.2f}",
            "Fond fin (€)": f"{fin:.2f}",
            "Gain (€)": f"{fin-debut:.2f}",
            "Commentaire": caisse["commentaire"],
        })
    caisses_details_df = pd.DataFrame(caisses_details)

    conn.close()

    if filename is None:
        ext = "." + format
        filename = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv"), ("PDF", "*.pdf")],
            title="Exporter bilan événement",
            initialfile=f"Bilan_{event['name'].replace(' ', '_')}{ext}"
        )
    if not filename:
        return

    if format == "xlsx":
        with pd.ExcelWriter(filename) as writer:
            pd.DataFrame([dict(event)]).to_excel(writer, sheet_name="Événement", index=False)
            recettes.to_excel(writer, sheet_name="Recettes", index=False)
            depenses.to_excel(writer, sheet_name="Dépenses", index=False)
            caisses_details_df.to_excel(writer, sheet_name="Caisses", index=False)
        messagebox.showinfo("Export", f"Bilan événement exporté :\n{filename}")
    elif format == "csv":
        recettes.to_csv(filename.replace(".csv", "_recettes.csv"), index=False, encoding="utf-8")
        depenses.to_csv(filename.replace(".csv", "_depenses.csv"), index=False, encoding="utf-8")
        caisses_details_df.to_csv(filename.replace(".csv", "_caisses.csv"), index=False, encoding="utf-8")
        messagebox.showinfo("Export", f"Bilans CSV exportés.")
    elif format == "pdf":
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Justify', alignment=4))

            elements = []

            # Titre principal
            elements.append(Paragraph(f"<b>Bilan de l'événement : {event['name']}</b>", styles["Title"]))
            elements.append(Paragraph(f"<i>Date : {event['date']} | Lieu : {event['lieu']}</i>", styles["Normal"]))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"{event['description']}", styles["BodyText"]))
            elements.append(Spacer(1, 16))

            # === TABLEAU SYNTHÉTIQUE (Recette/Dépense/Gain) ===
            total_recettes = recettes["montant"].sum() if not recettes.empty else 0.0
            total_depenses = depenses["montant"].sum() if not depenses.empty else 0.0
            gain = total_recettes - total_depenses

            synth_data = [
                ["Recettes (€)", "Dépenses (€)", "Gain (€)"],
                [f"{total_recettes:.2f}", f"{total_depenses:.2f}", f"{gain:.2f}"]
            ]
            synth_table = Table(synth_data, hAlign="LEFT", colWidths=[90, 90, 90])
            synth_table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 1, colors.black),
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#cce6ff")),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("FONTSIZE", (0,0), (-1,-1), 11),
                ("BOTTOMPADDING", (0,0), (-1,0), 6)
            ]))
            elements.append(synth_table)
            elements.append(Spacer(1, 18))

            # Recettes
            elements.append(Paragraph("<b>Recettes</b>", styles["Heading2"]))
            if not recettes.empty:
                recettes_data = [recettes.columns.tolist()] + [
                    [
                        Paragraph(str(row[0]), styles["Normal"]),
                        Paragraph(str(row[1]), styles["Normal"]),
                        Paragraph(str(row[2]), styles["Normal"]),
                        Paragraph(str(row[3]), styles["Normal"])
                    ] for row in recettes.values
                ]
                t = Table(recettes_data, hAlign="LEFT", colWidths=[110, 70, 220, 60])
                t.setStyle(TableStyle([
                    ("GRID", (0,0), (-1,-1), 0.7, colors.grey),
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e0e0e0")),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("ALIGN", (0,0), (-1,0), "CENTER"),
                    ("ALIGN", (1,1), (1,-1), "RIGHT"),  # montant à droite
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("LEFTPADDING", (0,0), (-1,-1), 6),
                    ("RIGHTPADDING", (0,0), (-1,-1), 6),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune recette.", styles["Normal"]))
            elements.append(Spacer(1, 16))

            # Dépenses
            elements.append(Paragraph("<b>Dépenses</b>", styles["Heading2"]))
            if not depenses.empty:
                depenses_data = [depenses.columns.tolist()] + [
                    [
                        Paragraph(str(row[0]), styles["Normal"]),  # categorie
                        Paragraph(str(row[1]), styles["Normal"]),  # montant
                        Paragraph(str(row[2]), styles["Normal"]),  # fournisseur
                        Paragraph(str(row[3]), styles["Normal"]),  # date_depense
                        Paragraph(str(row[4]), styles["Normal"]),  # paye_par
                        Paragraph(str(row[5]), styles["Normal"]),  # membre_id
                        Paragraph(str(row[6]), styles["Normal"])   # commentaire
                    ] for row in depenses.values
                ]
                t = Table(depenses_data, hAlign="LEFT", colWidths=[75, 60, 90, 60, 60, 50, 160])
                t.setStyle(TableStyle([
                    ("GRID", (0,0), (-1,-1), 0.7, colors.grey),
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e0e0e0")),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("ALIGN", (1,1), (1,-1), "RIGHT"),  # montant à droite
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("FONTSIZE", (0,0), (-1,-1), 8),
                    ("LEFTPADDING", (0,0), (-1,-1), 4),
                    ("RIGHTPADDING", (0,0), (-1,-1), 4),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune dépense.", styles["Normal"]))
            elements.append(Spacer(1, 18))

            # Caisses
            elements.append(Paragraph("<b>Caisses</b>", styles["Heading2"]))
            if not caisses_details_df.empty:
                caisses_data = [caisses_details_df.columns.tolist()] + [
                    [
                        Paragraph(str(row[0]), styles["Normal"]),
                        Paragraph(str(row[1]), styles["Normal"]),
                        Paragraph(str(row[2]), styles["Normal"]),
                        Paragraph(str(row[3]), styles["Normal"]),
                        Paragraph(str(row[4]), styles["Normal"])
                    ] for row in caisses_details_df.values
                ]
                t = Table(caisses_data, hAlign="LEFT", colWidths=[110, 60, 60, 60, 180])
                t.setStyle(TableStyle([
                    ("GRID", (0,0), (-1,-1), 0.7, colors.grey),
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e0e0e0")),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("ALIGN", (1,1), (3,-1), "RIGHT"),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("LEFTPADDING", (0,0), (-1,-1), 4),
                    ("RIGHTPADDING", (0,0), (-1,-1), 4),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune caisse.", styles["Normal"]))

            doc.build(elements)
            messagebox.showinfo("Export", f"Bilan PDF exporté :\n{filename}")
        except ImportError:
            messagebox.showerror("Export", "Le module reportlab n'est pas installé.")

# ========== EXPORTS GLOBAUX DÉPENSES / SUBVENTIONS ==========

def export_depenses_global(format="xlsx", filename=None):
    conn = get_connection()
    depenses = pd.read_sql_query("""
        SELECT 
            date_depense as date,
            categorie,
            montant,
            fournisseur,
            paye_par,
            membre_id,
            commentaire,
            'Régulière' as type_depense
        FROM depenses_regulieres
        UNION ALL
        SELECT 
            date_depense as date,
            categorie,
            montant,
            fournisseur,
            paye_par,
            membre_id,
            commentaire,
            'Diverse' as type_depense
        FROM depenses_diverses
    """, conn)
    conn.close()
    if filename is None:
        ext = "." + format
        filename = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv"), ("PDF", "*.pdf")],
            title="Exporter toutes les dépenses",
            initialfile="Toutes_depenses" + ext
        )
    if not filename:
        return
    if format == "xlsx":
        depenses.to_excel(filename, index=False)
        messagebox.showinfo("Export", f"Export Excel terminé :\n{filename}")
    elif format == "csv":
        depenses.to_csv(filename, index=False, encoding="utf-8")
        messagebox.showinfo("Export", f"Export CSV terminé :\n{filename}")
    elif format == "pdf":
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Justify', alignment=4))

            elements = []
            elements.append(Paragraph("<b>Toutes les dépenses</b>", styles["Title"]))
            elements.append(Spacer(1, 14))

            if not depenses.empty:
                data = [depenses.columns.tolist()] + [
                    [
                        Paragraph(str(row[0]), styles["Normal"]), # date
                        Paragraph(str(row[1]), styles["Normal"]), # categorie
                        Paragraph(str(row[2]), styles["Normal"]), # montant
                        Paragraph(str(row[3]), styles["Normal"]), # fournisseur
                        Paragraph(str(row[4]), styles["Normal"]), # paye_par
                        Paragraph(str(row[5]), styles["Normal"]), # membre_id
                        Paragraph(str(row[6]), styles["Normal"]), # commentaire
                        Paragraph(str(row[7]), styles["Normal"])  # type_depense
                    ]
                    for row in depenses.values
                ]
                # Largeurs proportionnelles : les 6 premières colonnes restent fixes, la colonne "commentaire" et "type_depense" adaptatives
                t = Table(
                    data,
                    hAlign="LEFT",
                    colWidths=[55, 75, 55, 90, 60, 45, "*", 60]  # "*" donne tout l'espace restant à "commentaire"
                )
                t.setStyle(TableStyle([
                    ("GRID", (0,0), (-1,-1), 0.7, colors.grey),
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#cce6ff")),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("ALIGN", (2,1), (2,-1), "RIGHT"),    # montant à droite
                    ("ALIGN", (0,0), (-1,0), "CENTER"),   # en-têtes centrées
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("LEFTPADDING", (0,0), (-1,-1), 5),
                    ("RIGHTPADDING", (0,0), (-1,-1), 5),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
                    ("BOTTOMPADDING", (0,0), (-1,0), 6),
                    ("TOPPADDING", (0,0), (-1,0), 6)
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune dépense.", styles["Normal"]))

            doc.build(elements)
            messagebox.showinfo("Export", f"Export PDF terminé :\n{filename}")
        except ImportError:
            messagebox.showerror("Export", "Le module reportlab n'est pas installé.")

def export_subventions_global(format="xlsx", filename=None):
    conn = get_connection()
    subventions = pd.read_sql_query("SELECT * FROM dons_subventions", conn)
    conn.close()
    if filename is None:
        ext = "." + format
        filename = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv"), ("PDF", "*.pdf")],
            title="Exporter toutes les subventions",
            initialfile="Toutes_subventions" + ext
        )
    if not filename:
        return
    if format == "xlsx":
        subventions.to_excel(filename, index=False)
        messagebox.showinfo("Export", f"Export Excel terminé :\n{filename}")
    elif format == "csv":
        subventions.to_csv(filename, index=False, encoding="utf-8")
        messagebox.showinfo("Export", f"Export CSV terminé :\n{filename}")
    elif format == "pdf":
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Justify', alignment=4))

            elements = []
            elements.append(Paragraph("<b>Toutes les subventions et dons</b>", styles["Title"]))
            elements.append(Spacer(1, 12))

            if not subventions.empty:
                data = [subventions.columns.tolist()] + [
                    [Paragraph(str(col), styles["Normal"]) for col in row]
                    for row in subventions.values
                ]
                t = Table(data, hAlign="LEFT", colWidths=[65, 120, 70, 70, 110, 80])
                t.setStyle(TableStyle([
                    ("GRID", (0,0), (-1,-1), 0.7, colors.grey),
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e0e0e0")),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("ALIGN", (2,1), (2,-1), "RIGHT"),  # montant à droite
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("LEFTPADDING", (0,0), (-1,-1), 4),
                    ("RIGHTPADDING", (0,0), (-1,-1), 4),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune subvention ni don.", styles["Normal"]))

            doc.build(elements)
            messagebox.showinfo("Export", f"Export PDF terminé :\n{filename}")
        except ImportError:
            messagebox.showerror("Export", "Le module reportlab n'est pas installé.")

# ========== EXPORTS MULTI-EVENEMENTS EN LOT ==========

def export_tous_bilans_evenements(format="xlsx", dossier=None):
    conn = get_connection()
    events = conn.execute("SELECT id, name FROM events ORDER BY date DESC").fetchall()
    conn.close()
    if dossier is None:
        dossier = filedialog.askdirectory(title="Choisir le dossier d'export pour tous les bilans événements")
    if not dossier:
        return
    for ev in events:
        name = ev["name"].replace(" ", "_")
        fname = f"{dossier}/Bilan_{name}.{format}"
        export_bilan_evenement(ev["id"], format=format, filename=fname)
    messagebox.showinfo("Export", f"Tous les bilans événements exportés dans :\n{dossier}")
    
class ExportsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Exports et Bilans")
        self.geometry("640x520")
        self.resizable(False, False)
        self.create_widgets()
        self.populate_events()

    def create_widgets(self):
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=16)

        # Sélection d'un événement
        tk.Label(frm, text="Bilan par événement :", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        sel_frame = tk.Frame(frm)
        sel_frame.pack(anchor="w", pady=(0, 10))
        self.event_var = tk.StringVar()
        self.event_cb = ttk.Combobox(sel_frame, textvariable=self.event_var, state="readonly", width=38)
        self.event_cb.pack(side="left")
        tk.Button(sel_frame, text="Exporter Excel", command=lambda: export_bilan_evenement(self.get_selected_event_id(), "xlsx")).pack(side="left", padx=3)
        tk.Button(sel_frame, text="Exporter CSV", command=lambda: export_bilan_evenement(self.get_selected_event_id(), "csv")).pack(side="left", padx=3)
        tk.Button(sel_frame, text="Exporter PDF", command=lambda: export_bilan_evenement(self.get_selected_event_id(), "pdf")).pack(side="left", padx=3)

        # Export tous bilans événements
        tk.Label(frm, text="Exporter tous les bilans événements :", font=("Arial", 12, "bold")).pack(anchor="w", pady=(16, 4))
        all_ev_frame = tk.Frame(frm)
        all_ev_frame.pack(anchor="w", pady=(0, 10))
        tk.Button(all_ev_frame, text="Tous en Excel", command=lambda: export_tous_bilans_evenements("xlsx")).pack(side="left", padx=3)
        tk.Button(all_ev_frame, text="Tous en CSV", command=lambda: export_tous_bilans_evenements("csv")).pack(side="left", padx=3)
        tk.Button(all_ev_frame, text="Tous en PDF", command=lambda: export_tous_bilans_evenements("pdf")).pack(side="left", padx=3)

        # Export global dépenses
        tk.Label(frm, text="Exporter toutes les dépenses :", font=("Arial", 12, "bold")).pack(anchor="w", pady=(16, 4))
        dep_frame = tk.Frame(frm)
        dep_frame.pack(anchor="w", pady=(0, 10))
        tk.Button(dep_frame, text="Excel", command=lambda: export_depenses_global("xlsx")).pack(side="left", padx=3)
        tk.Button(dep_frame, text="CSV", command=lambda: export_depenses_global("csv")).pack(side="left", padx=3)
        tk.Button(dep_frame, text="PDF", command=lambda: export_depenses_global("pdf")).pack(side="left", padx=3)

        # Export global subventions/dons
        tk.Label(frm, text="Exporter tous les dons/subventions :", font=("Arial", 12, "bold")).pack(anchor="w", pady=(16, 4))
        sub_frame = tk.Frame(frm)
        sub_frame.pack(anchor="w", pady=(0, 10))
        tk.Button(sub_frame, text="Excel", command=lambda: export_subventions_global("xlsx")).pack(side="left", padx=3)
        tk.Button(sub_frame, text="CSV", command=lambda: export_subventions_global("csv")).pack(side="left", padx=3)
        tk.Button(sub_frame, text="PDF", command=lambda: export_subventions_global("pdf")).pack(side="left", padx=3)

        # Bouton fermer
        tk.Button(frm, text="Fermer", command=self.destroy).pack(side="bottom", pady=8)

    def populate_events(self):
        conn = get_connection()
        events = conn.execute("SELECT id, name, date FROM events ORDER BY date DESC").fetchall()
        conn.close()
        self.event_list = [(str(ev["id"]), f"{ev['date']} - {ev['name']}") for ev in events]
        self.event_cb["values"] = [ev[1] for ev in self.event_list]
        if self.event_list:
            self.event_cb.current(0)

    def get_selected_event_id(self):
        idx = self.event_cb.current()
        if idx < 0 or not self.event_list:
            messagebox.showwarning("Sélection", "Sélectionnez un événement.")
            return None
        return int(self.event_list[idx][0])