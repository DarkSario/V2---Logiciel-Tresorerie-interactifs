import tkinter as tk
from tkinter import messagebox
from db.db import get_connection

class SoldeOuvertureDialog(tk.Toplevel):
    def __init__(self, master, on_save=None):
        super().__init__(master)
        self.title("Solde d'ouverture bancaire")
        self.geometry("380x180")
        self.resizable(False, False)
        self.on_save = on_save

        tk.Label(self, text="Solde d'ouverture bancaire en début d'exercice :", font=("Arial", 12)).pack(pady=16)
        self.solde_var = tk.StringVar()
        tk.Entry(self, textvariable=self.solde_var, font=("Arial", 14), width=16, justify="center").pack(pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=20)

        self.load_solde()

    def load_solde(self):
        conn = get_connection()
        row = conn.execute("SELECT solde_report FROM config ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        if row and row[0] is not None:
            self.solde_var.set(f"{row[0]:.2f}")
        else:
            self.solde_var.set("0.00")

    def save(self):
        val = self.solde_var.get().replace(",", ".").strip()
        try:
            float_val = float(val)
        except Exception:
            messagebox.showerror("Erreur", "Veuillez saisir un montant valide.")
            return
        conn = get_connection()
        conn.execute("UPDATE config SET solde_report=? WHERE id=(SELECT MAX(id) FROM config)", (float_val,))
        conn.commit()
        conn.close()
        messagebox.showinfo("OK", "Solde d'ouverture mis à jour.")
        if self.on_save:
            self.on_save()
        self.destroy()