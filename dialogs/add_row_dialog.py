import tkinter as tk
from tkinter import ttk
from utils.error_handler import handle_errors

class AddRowDialog(tk.Toplevel):
    def __init__(self, master, fields, get_choices_func):
        super().__init__(master)
        self.title("Ajouter une ligne")
        self.result = None
        self.entries = {}
        self.geometry(f"400x{100+40*len(fields)}")
        frm = tk.Frame(self)
        frm.pack(padx=12, pady=12, fill="both", expand=True)
        for i, f in enumerate(fields):
            tk.Label(frm, text=f["nom_champ"]).grid(row=i, column=0, sticky="w", pady=6, padx=3)
            if f.get("modele_colonne"):
                try:
                    choix = get_choices_func(f["modele_colonne"])
                except Exception as e:
                    choix = []
                var = tk.StringVar()
                cb = ttk.Combobox(frm, textvariable=var, values=choix, state="readonly")
                cb.grid(row=i, column=1, sticky="ew", padx=3)
                if choix:
                    cb.current(0)
                self.entries[f["id"]] = var
            else:
                var = tk.StringVar()
                e = tk.Entry(frm, textvariable=var)
                e.grid(row=i, column=1, sticky="ew", padx=3)
                self.entries[f["id"]] = var
            frm.columnconfigure(1, weight=1)
        btnf = tk.Frame(self)
        btnf.pack(pady=8)
        tk.Button(btnf, text="Ajouter", command=self.validate).pack(side="left", padx=8)
        tk.Button(btnf, text="Annuler", command=self.destroy).pack(side="right", padx=8)
        self.bind("<Return>", lambda e: self.validate())
        self.grab_set()
        self.focus_set()
        self.wait_window(self)

    @handle_errors
    def validate(self):
        vals = {fid: var.get() for fid, var in self.entries.items()}
        self.result = vals
        self.destroy()