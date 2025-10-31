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
            from reportlab.lib.styles import getSampleStyleSheet
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []
            elements.append(Paragraph(f"Bilan de l'événement : {event['name']}", styles["Title"]))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Date : {event['date']} | Lieu : {event['lieu']}", styles["Normal"]))
            elements.append(Paragraph(f"Description : {event['description']}", styles["Normal"]))
            elements.append(Spacer(1, 16))
            # Recettes
            elements.append(Paragraph("Recettes", styles["Heading2"]))
            if not recettes.empty:
                data = [recettes.columns.tolist()] + recettes.values.tolist()
                t = Table(data)
                t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune recette.", styles["Normal"]))
            elements.append(Spacer(1, 12))
            # Dépenses
            elements.append(Paragraph("Dépenses", styles["Heading2"]))
            if not depenses.empty:
                data = [depenses.columns.tolist()] + depenses.values.tolist()
                t = Table(data)
                t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)]))
                elements.append(t)
            else:
                elements.append(Paragraph("Aucune dépense.", styles["Normal"]))
            elements.append(Spacer(1, 12))
            # Caisses
            elements.append(Paragraph("Caisses", styles["Heading2"]))
            if not caisses_details_df.empty:
                data = [caisses_details_df.columns.tolist()] + caisses_details_df.values.tolist()
                t = Table(data)
                t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)]))
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
    depenses = pd.read_sql_query(
        "SELECT * FROM depenses_regulieres UNION ALL SELECT * FROM depenses_diverses UNION ALL SELECT * FROM event_depenses", conn
    )
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
            from reportlab.lib.styles import getSampleStyleSheet
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [Paragraph("Toutes les dépenses", styles["Title"]), Spacer(1, 12)]
            data = [depenses.columns.tolist()] + depenses.values.tolist()
            t = Table(data)
            t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)]))
            elements.append(t)
            doc.build(elements)
            messagebox.showinfo("Export", f"Export PDF terminé :\n{filename}")
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
            from reportlab.lib.styles import getSampleStyleSheet
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [Paragraph("Toutes les subventions", styles["Title"]), Spacer(1, 12)]
            data = [subventions.columns.tolist()] + subventions.values.tolist()
            t = Table(data)
            t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)]))
            elements.append(t)
            doc.build(elements)
            messagebox.showinfo("Export", f"Export PDF terminé :\n{filename}")
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
    
def export_dataframe_to_excel(df, title="Export Excel"):
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], title=title)
    if not filename:
        return
    df.to_excel(filename, index=False)
    messagebox.showinfo("Export", f"Export Excel terminé :\n{filename}")

def export_dataframe_to_csv(df, title="Export CSV"):
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title=title)
    if not filename:
        return
    df.to_csv(filename, index=False, encoding="utf-8")
    messagebox.showinfo("Export", f"Export CSV terminé :\n{filename}")

def export_dataframe_to_pdf(df, title="Export PDF"):
    filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title=title)
    if not filename:
        return
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
        data = [list(df.columns)] + df.astype(str).values.tolist()
        t = Table(data)
        t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.black)]))
        elements.append(t)
        doc.build(elements)
        messagebox.showinfo("Export", f"Export PDF terminé :\n{filename}")
    except ImportError:
        messagebox.showerror("Export", "Le module reportlab n'est pas installé.")
        
def export_bilan_reporte_pdf(recap, parent, exercice, date, date_fin):
    """
    Génère un PDF de bilan de clôture à partir des DataFrames fournis dans recap
    - recap["synth_evt"] : DataFrame avec recap des événements
    - recap["synth_dep"] : DataFrame avec recap des dépenses
    """
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        messagebox.showerror("Export", "Le module reportlab n'est pas installé.")
        return

    file_path = filedialog.asksaveasfilename(
        title="Enregistrer le bilan PDF",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        parent=parent
    )
    if not file_path:
        return

    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f"Bilan de clôture d'exercice {exercice}", styles["Title"]))
    elements.append(Paragraph(f"Période : {date} au {date_fin}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Synthèse événements
    synth_evt = recap.get("synth_evt")
    if synth_evt is not None and not synth_evt.empty:
        elements.append(Paragraph("Synthèse par événement", styles["Heading2"]))
        data = [list(synth_evt.columns)] + synth_evt.astype(str).values.tolist()
        t = Table(data)
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    # Synthèse dépenses
    synth_dep = recap.get("synth_dep")
    if synth_dep is not None and not synth_dep.empty:
        elements.append(Paragraph("Synthèse dépenses", styles["Heading2"]))
        data = [list(synth_dep.columns)] + synth_dep.astype(str).values.tolist()
        t = Table(data)
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("Document généré automatiquement.", styles["Normal"]))

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    doc.build(elements)
    messagebox.showinfo("Export", f"Bilan PDF exporté :\n{file_path}")
    
def export_bilan_argumente_pdf():
    from exports.export_bilan_argumente import export_bilan_argumente_pdf as real_export_pdf
    real_export_pdf()

def export_bilan_argumente_word():
    from exports.export_bilan_argumente import export_bilan_argumente_word as real_export_word
    real_export_word()