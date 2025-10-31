import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

logger = get_logger("event_payments")

class PaymentsWindow(tk.Toplevel):
    def __init__(self, master, event_id):
        super().__init__(master)
        self.title("Paiements de l'événement")
        self.geometry("900x500")
        self.event_id = event_id
        self.create_widgets()
        self.refresh_payments()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Ajouter paiement", command=self.add_payment).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Éditer", command=self.edit_payment).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_payment).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)

        cols = ("id", "nom_payeuse", "classe", "mode_paiement", "banque", "numero_cheque", "montant", "commentaire")
        labels = ("ID", "Name", "Classe", "Mode", "Banque", "N° Chèque", "Montant", "Commentaire")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, l in zip(cols, labels):
            self.tree.heading(c, text=l)
            self.tree.column(c, width=120 if c=="montant" else 110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=7, pady=7)

    def refresh_payments(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            pays = conn.execute(
                "SELECT * FROM event_payments WHERE event_id = ? ORDER BY id DESC", (self.event_id,)
            ).fetchall()
            for p in pays:
                self.tree.insert("", "end", values=(
                    p["id"], p["nom_payeuse"], p["classe"], p["mode_paiement"], p["banque"], p["numero_cheque"], p["montant"], p["commentaire"]
                ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des paiements."))

    def get_selected_payment_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_payment(self):
        PaymentDialog(self, event_id=self.event_id, on_save=self.refresh_payments)

    def edit_payment(self):
        pid = self.get_selected_payment_id()
        if not pid:
            messagebox.showwarning("Sélection", "Sélectionne un paiement.")
            return
        PaymentDialog(self, event_id=self.event_id, payment_id=pid, on_save=self.refresh_payments)

    def delete_payment(self):
        pid = self.get_selected_payment_id()
        if not pid:
            messagebox.showwarning("Sélection", "Sélectionne un paiement.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer ce paiement ?"):
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM event_payments WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            self.refresh_payments()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression du paiement."))

class PaymentDialog(tk.Toplevel):
    def __init__(self, master, event_id, payment_id=None, on_save=None):
        super().__init__(master)
        self.title("Paiement")
        self.event_id = event_id
        self.payment_id = payment_id
        self.on_save = on_save
        self.geometry("500x420")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.classe_var = tk.StringVar()
        self.mode_var = tk.StringVar()
        self.banque_var = tk.StringVar()
        self.numero_var = tk.StringVar()
        self.montant_var = tk.DoubleVar()
        self.comment_var = tk.StringVar()

        tk.Label(self, text="Name payeur.se :").pack(pady=5)
        tk.Entry(self, textvariable=self.nom_var, width=40).pack()
        tk.Label(self, text="Classe :").pack(pady=5)
        tk.Entry(self, textvariable=self.classe_var, width=20).pack()
        tk.Label(self, text="Mode paiement (C/E/autre) :").pack(pady=5)
        tk.Entry(self, textvariable=self.mode_var, width=8).pack()
        tk.Label(self, text="Banque :").pack(pady=5)
        tk.Entry(self, textvariable=self.banque_var, width=20).pack()
        tk.Label(self, text="N° chèque :").pack(pady=5)
        tk.Entry(self, textvariable=self.numero_var, width=20).pack()
        tk.Label(self, text="Montant :").pack(pady=5)
        tk.Entry(self, textvariable=self.montant_var, width=10).pack()
        tk.Label(self, text="Commentaire :").pack(pady=5)
        tk.Entry(self, textvariable=self.comment_var, width=35).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=36, pady=16)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=36, pady=16)

        if self.payment_id:
            self.load_payment()

    def load_payment(self):
        try:
            conn = get_connection()
            p = conn.execute("SELECT * FROM event_payments WHERE id=?", (self.payment_id,)).fetchone()
            conn.close()
            if p:
                self.nom_var.set(p["nom_payeuse"])
                self.classe_var.set(p["classe"])
                self.mode_var.set(p["mode_paiement"])
                self.banque_var.set(p["banque"])
                self.numero_var.set(p["numero_cheque"])
                self.montant_var.set(p["montant"])
                self.comment_var.set(p["commentaire"])
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement du paiement."))

    def save(self):
        d = dict(
            name=self.nom_var.get().strip(),
            classe=self.classe_var.get().strip(),
            mode=self.mode_var.get().strip(),
            banque=self.banque_var.get().strip(),
            numero=self.numero_var.get().strip(),
            montant=self.montant_var.get(),
            comment=self.comment_var.get().strip()
        )
        if not d["name"]:
            messagebox.showerror("Erreur", "Name obligatoire.")
            return
        if not d["mode"]:
            messagebox.showerror("Erreur", "Mode de paiement obligatoire.")
            return
        try:
            conn = get_connection()
            if self.payment_id:
                conn.execute(
                    "UPDATE event_payments SET nom_payeuse=?, classe=?, mode_paiement=?, banque=?, numero_cheque=?, montant=?, commentaire=? WHERE id=?",
                    (d["name"], d["classe"], d["mode"], d["banque"], d["numero"], d["montant"], d["comment"], self.payment_id)
                )
            else:
                conn.execute(
                    "INSERT INTO event_payments (event_id, nom_payeuse, classe, mode_paiement, banque, numero_cheque, montant, commentaire) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.event_id, d["name"], d["classe"], d["mode"], d["banque"], d["numero"], d["montant"], d["comment"])
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement du paiement."))