import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("event_caisse_details")

class EventCaisseDetailsWindow(tk.Toplevel):
    def __init__(self, master, caisse_id):
        super().__init__(master)
        self.caisse_id = caisse_id
        self.title(f"Détails de la caisse {caisse_id}")
        self.geometry("800x450")
        self.create_widgets()
        self.refresh_details()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Nouvelle opération", command=self.add_operation).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_operation).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)

        columns = ("id", "date", "type_op", "montant", "description", "justificatif")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("type_op", text="Type opération")
        self.tree.heading("montant", text="Montant (€)")
        self.tree.heading("description", text="Description")
        self.tree.heading("justificatif", text="Justificatif")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_details(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            ops = conn.execute(
                "SELECT * FROM event_caisse_details WHERE caisse_id = ? ORDER BY date, id", (self.caisse_id,)
            ).fetchall()
            for op in ops:
                self.tree.insert(
                    "", "end",
                    values=(
                        op["id"],
                        op["date"],
                        op["type_op"],
                        f"{op['montant']:.2f}" if op["montant"] is not None else "",
                        op["description"] or "",
                        op["justificatif"] or ""
                    )
                )
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des opérations de caisse."))

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_operation(self):
        OperationDialog(self, caisse_id=self.caisse_id, on_save=self.refresh_details)

    def delete_operation(self):
        oid = self.get_selected_id()
        if not oid:
            messagebox.showwarning("Sélection", "Sélectionne une opération à supprimer.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer cette opération ?"):
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM event_caisse_details WHERE id=? AND caisse_id=?", (oid, self.caisse_id))
            conn.commit()
            conn.close()
            logger.info(f"Opération supprimée id {oid}, caisse_id {self.caisse_id}")
            self.refresh_details()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de l'opération."))

class OperationDialog(tk.Toplevel):
    def __init__(self, master, caisse_id, operation_id=None, on_save=None):
        super().__init__(master)
        self.title("Opération" if operation_id is None else "Éditer opération")
        self.caisse_id = caisse_id
        self.operation_id = operation_id
        self.on_save = on_save
        self.geometry("380x320")
        self.resizable(False, False)

        self.date_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.montant_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.justif_var = tk.StringVar()

        tk.Label(self, text="Date (YYYY-MM-DD) :").pack(pady=6)
        tk.Entry(self, textvariable=self.date_var, width=20).pack()
        tk.Label(self, text="Type opération :").pack(pady=6)
        type_ops = ["Entrée", "Sortie"]
        ttk.Combobox(self, textvariable=self.type_var, values=type_ops, state="readonly", width=15).pack()
        tk.Label(self, text="Montant (€) :").pack(pady=6)
        tk.Entry(self, textvariable=self.montant_var, width=14).pack()
        tk.Label(self, text="Description :").pack(pady=6)
        tk.Entry(self, textvariable=self.desc_var, width=30).pack()
        tk.Label(self, text="Justificatif :").pack(pady=6)
        tk.Entry(self, textvariable=self.justif_var, width=30).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=36, pady=16)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=36, pady=16)

        if self.operation_id:
            self.load_operation()

    def load_operation(self):
        try:
            conn = get_connection()
            op = conn.execute(
                "SELECT * FROM event_caisse_details WHERE id=? AND caisse_id=?",
                (self.operation_id, self.caisse_id)
            ).fetchone()
            conn.close()
            if op:
                self.date_var.set(op["date"])
                self.type_var.set(op["type_op"])
                self.montant_var.set(f"{op['montant']:.2f}" if op["montant"] is not None else "")
                self.desc_var.set(op["description"] or "")
                self.justif_var.set(op["justificatif"] or "")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement de l'opération."))

    def save(self):
        date = self.date_var.get().strip()
        typ = self.type_var.get().strip()
        montant = self.montant_var.get().replace(",", ".").strip()
        desc = self.desc_var.get().strip()
        justif = self.justif_var.get().strip()
        if not date or not typ or not montant:
            messagebox.showerror("Erreur", "Date, type et montant sont obligatoires.")
            return
        try:
            montant_float = float(montant)
        except Exception:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        try:
            conn = get_connection()
            if self.operation_id:
                conn.execute(
                    "UPDATE event_caisse_details SET date=?, type_op=?, montant=?, description=?, justificatif=? WHERE id=? AND caisse_id=?",
                    (date, typ, montant_float, desc, justif, self.operation_id, self.caisse_id)
                )
            else:
                conn.execute(
                    "INSERT INTO event_caisse_details (caisse_id, date, type_op, montant, description, justificatif) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.caisse_id, date, typ, montant_float, desc, justif)
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de l'opération."))