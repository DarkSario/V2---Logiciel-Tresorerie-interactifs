import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_connection
from modules.event_modules import EventModulesWindow
from modules.event_payments import PaymentsWindow
from modules.event_caisses import EventCaissesWindow
from modules.event_recettes import EventRecettesWindow
from modules.event_depenses import EventDepensesWindow
from utils.app_logger import get_logger
from utils.error_handler import handle_exception
from utils.date_helpers import parse_date, today

logger = get_logger("events_module")

class EventsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gestion des événements")
        self.geometry("1100x500")
        self.minsize(900, 300)
        self.create_widgets()
        self.refresh_events()

    def create_widgets(self):
        # --- Barre du haut ---
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(top_frame, text="Nouvel événement", command=self.add_event).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="Éditer", command=self.edit_event).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="Supprimer", command=self.delete_event).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="Fermer", command=self.destroy).pack(side=tk.RIGHT, padx=5, pady=5)

        # --- Tableau au centre ---
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=0)

        columns = ("id", "name", "date", "lieu", "description", "recettes", "depenses", "gain")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        headings = [
            ("id", "ID"),
            ("name", "Name"),
            ("date", "Date"),
            ("lieu", "Lieu"),
            ("description", "Description"),
            ("recettes", "Recettes (€)"),
            ("depenses", "Dépenses (€)"),
            ("gain", "Gain (€)")
        ]
        for col, lbl in headings:
            self.tree.heading(col, text=lbl)
            if col == "id":
                self.tree.column(col, width=50, anchor="center", stretch=False)
            elif col in ("recettes", "depenses", "gain"):
                self.tree.column(col, width=100, anchor="e", stretch=False)
            else:
                self.tree.column(col, width=140, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Barre du bas façon dashboard ---
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 10))
        btn_style = {"font": ("Arial", 10, "bold"), "height": 2, "width": 20}

        tk.Button(bottom_frame, text="Modules personnalisés", command=self.open_modules, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Paiements", command=self.open_payments, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Caisses événement", command=self.open_caisses, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Recettes événement", command=self.open_recettes, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Dépenses événement", command=self.open_depenses, **btn_style).pack(side=tk.LEFT, padx=6)

    def refresh_events(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            events = conn.execute("SELECT * FROM events ORDER BY date DESC").fetchall()
            for ev in events:
                event_id = ev["id"]
                recettes = conn.execute(
                    "SELECT COALESCE(SUM(montant), 0) FROM event_recettes WHERE event_id = ?", (event_id,)
                ).fetchone()[0]
                depenses = conn.execute(
                    "SELECT COALESCE(SUM(montant), 0) FROM event_depenses WHERE event_id = ?", (event_id,)
                ).fetchone()[0]
                gain = recettes - depenses
                self.tree.insert(
                    "", "end",
                    values=(
                        ev["id"],
                        ev["name"],
                        ev["date"],
                        ev["lieu"],
                        ev["description"],
                        f"{recettes:.2f}",
                        f"{depenses:.2f}",
                        f"{gain:.2f}"
                    )
                )
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des événements."))

    def get_selected_event_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_event(self):
        EventDialog(self, on_save=self.refresh_events)

    def edit_event(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        EventDialog(self, event_id=eid, on_save=self.refresh_events)

    def delete_event(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer cet événement ?"):
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM events WHERE id = ?", (eid,))
            conn.commit()
            conn.close()
            logger.info(f"Événement supprimé id {eid}")
            self.refresh_events()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression de l'événement."))

    def open_modules(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        EventModulesWindow(self, event_id=eid)

    def open_payments(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        PaymentsWindow(self, event_id=eid)
        
    def open_caisses(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        EventCaissesWindow(self, event_id=eid)    

    def open_recettes(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        EventRecettesWindow(self, event_id=eid)

    def open_depenses(self):
        eid = self.get_selected_event_id()
        if not eid:
            messagebox.showwarning("Sélection", "Sélectionne un événement.")
            return
        EventDepensesWindow(self, event_id=eid)        

class EventDialog(tk.Toplevel):
    def __init__(self, master, event_id=None, on_save=None):
        super().__init__(master)
        self.title("Événement" if not event_id else "Éditer l'événement")
        self.event_id = event_id
        self.on_save = on_save
        self.geometry("420x320")
        self.resizable(False, False)

        self.name_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.lieu_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        tk.Label(self, text="Name :").pack(pady=6)
        tk.Entry(self, textvariable=self.name_var, width=40).pack()
        tk.Label(self, text="Date (yyyy-mm-dd) :").pack(pady=6)
        tk.Entry(self, textvariable=self.date_var, width=20).pack()
        tk.Label(self, text="Lieu :").pack(pady=6)
        tk.Entry(self, textvariable=self.lieu_var, width=30).pack()
        tk.Label(self, text="Description :").pack(pady=6)
        tk.Entry(self, textvariable=self.desc_var, width=45).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=36, pady=16)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=36, pady=16)

        if self.event_id:
            self.load_event()

    def load_event(self):
        try:
            conn = get_connection()
            ev = conn.execute("SELECT * FROM events WHERE id = ?", (self.event_id,)).fetchone()
            conn.close()
            if ev:
                self.name_var.set(ev["name"])
                self.date_var.set(ev["date"])
                self.lieu_var.set(ev["lieu"])
                self.desc_var.set(ev["description"])
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement de l'événement."))

    def save(self):
        name = self.name_var.get().strip()
        date = self.date_var.get().strip() or today()
        lieu = self.lieu_var.get().strip()
        desc = self.desc_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom de l'événement est obligatoire.")
            return
        if not parse_date(date):
            messagebox.showerror("Erreur", "Date invalide (format attendu : YYYY-MM-DD).")
            return
        try:
            conn = get_connection()
            if self.event_id:
                conn.execute(
                    "UPDATE events SET name=?, date=?, lieu=?, description=? WHERE id=?",
                    (name, date, lieu, desc, self.event_id)
                )
            else:
                conn.execute(
                    "INSERT INTO events (name, date, lieu, description) VALUES (?, ?, ?, ?)",
                    (name, date, lieu, desc)
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement de l'événement."))