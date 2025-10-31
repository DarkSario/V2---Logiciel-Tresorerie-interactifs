import tkinter as tk

class InventaireDialog(tk.Toplevel):
    def __init__(self, master, name, quantite_actuelle):
        super().__init__(master)
        self.title("Inventaire article")
        self.geometry("330x160")
        self.result = None
        self.name = name
        self.quantite_actuelle = quantite_actuelle

        tk.Label(self, text=f"Article : {name}", font=("Arial", 12)).pack(pady=8)
        tk.Label(self, text=f"Quantité actuelle : {quantite_actuelle}").pack(pady=6)
        tk.Label(self, text="Nouvelle quantité :").pack()
        self.qte_var = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.qte_var, width=12, font=("Arial", 12))
        entry.pack(pady=6)
        entry.focus_set()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Valider", command=self.on_valider).pack(side=tk.LEFT, padx=12)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=12)

        self.bind("<Return>", lambda e: self.on_valider())

    def on_valider(self):
        self.result = self.qte_var.get().strip()
        self.destroy()