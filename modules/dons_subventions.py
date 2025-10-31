import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection
from utils.validation import is_required, is_number

class DonsSubventionsModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Dons et Subventions")
        self.top.geometry("700x400")
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        columns = ("id", "type", "source", "montant", "date", "justificatif")
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings")
        for col, text, w in zip(
            columns,
            ["ID", "Type", "Source", "Montant (€)", "Date", "Justificatif"],
            [50, 80, 180, 100, 100, 150]
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="Ajouter Don/Subvention", command=self.add_don_subvention).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Supprimer sélection", command=self.delete_selected).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=8)

    def add_don_subvention(self):
        AddDonSubventionDialog(self.top, self.refresh_list)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne à supprimer.")
            return
        item = self.tree.item(sel[0])
        id_ = item["values"][0]
        if not messagebox.askyesno("Confirmer", "Supprimer ce don/subvention ?"):
            return
        conn = get_connection()
        conn.row_factory = None
        conn.execute("DELETE FROM dons_subventions WHERE id = ?", (id_,))
        conn.commit()
        conn.close()
        self.refresh_list()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        conn.row_factory = None
        items = conn.execute(
            "SELECT id, type, source, montant, date, justificatif FROM dons_subventions ORDER BY date DESC, id DESC"
        ).fetchall()
        conn.close()
        for item in items:
            self.tree.insert("", "end", values=item)

class AddDonSubventionDialog(tk.Toplevel):
    def __init__(self, master, on_save):
        super().__init__(master)
        self.title("Ajouter un Don/Subvention")
        self.resizable(False, False)
        self.on_save = on_save

        tk.Label(self, text="Type (Don/Subvention) *").grid(row=0, column=0, sticky="e", pady=4, padx=6)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(self, textvariable=self.type_var, values=["Don", "Subvention"], width=20, state="readonly")
        self.type_combo.grid(row=0, column=1, pady=4)
        self.type_combo.current(0)

        tk.Label(self, text="Source (name, organisme) *").grid(row=1, column=0, sticky="e", pady=4, padx=6)
        self.source_var = tk.StringVar()
        tk.Entry(self, textvariable=self.source_var, width=28).grid(row=1, column=1, pady=4)

        tk.Label(self, text="Montant (€) *").grid(row=2, column=0, sticky="e", pady=4, padx=6)
        self.montant_var = tk.StringVar()
        tk.Entry(self, textvariable=self.montant_var, width=15).grid(row=2, column=1, pady=4)

        tk.Label(self, text="Date (YYYY-MM-DD) *").grid(row=3, column=0, sticky="e", pady=4, padx=6)
        self.date_var = tk.StringVar()
        tk.Entry(self, textvariable=self.date_var, width=15).grid(row=3, column=1, pady=4)

        tk.Label(self, text="Justificatif (facultatif)").grid(row=4, column=0, sticky="e", pady=4, padx=6)
        self.justif_var = tk.StringVar()
        tk.Entry(self, textvariable=self.justif_var, width=28).grid(row=4, column=1, pady=4)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=12)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=12)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.LEFT, padx=12)

    def save(self):
        type_ = self.type_var.get().strip()
        source = self.source_var.get().strip()
        montant_str = self.montant_var.get().replace(",", ".").strip()
        try:
            montant = float(montant_str)
        except Exception:
            montant = None
        date = self.date_var.get().strip()
        justificatif = self.justif_var.get().strip()
        if not is_required(type_) or not is_required(source) or montant is None or not is_required(date):
            messagebox.showerror("Erreur", "Champs obligatoires manquants ou montant invalide.")
            return
        conn = get_connection()
        conn.row_factory = None
        conn.execute(
            "INSERT INTO dons_subventions (type, source, montant, date, justificatif) VALUES (?, ?, ?, ?, ?)",
            (type_, source, montant, date, justificatif)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Ajouté", "Don/Subvention enregistré.")
        self.destroy()
        if self.on_save:
            self.on_save()