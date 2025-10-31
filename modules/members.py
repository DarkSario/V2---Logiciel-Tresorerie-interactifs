import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db.db import get_connection
import pandas as pd
from utils.validation import is_email, is_required
from utils.app_logger import get_logger
from utils.error_handler import handle_exception

STATUTS = [
    "Présidente", "Président", "Vice-Présidente", "Vice-Président",
    "Secrétaire", "Secrétaire-Adjointe", "Secrétaire-Adjoint",
    "Trésorière", "Trésorier", "Trésorière-Adjointe", "Trésorier-Adjoint",
    "Membre"
]
COTISATION_ETATS = ["Réglé", "Non réglé", "Exempté"]

logger = get_logger("members_module")

class MembersModule:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Gestion des Membres")
        self.top.geometry("980x520")
        self.create_table()
        self.create_buttons()
        self.refresh_members()

    def create_table(self):
        columns = (
            "id", "name", "prenom", "email", "cotisation", "commentaire",
            "telephone", "statut", "date_adhesion"
        )
        self.tree = ttk.Treeview(self.top, columns=columns, show="headings")
        headings = [
            ("ID", 40), ("Name", 140), ("Prénom", 130), ("Email", 180),
            ("Cotisation", 90), ("Commentaire", 140),
            ("Téléphone", 110), ("Statut", 110), ("Date adhésion", 110)
        ]
        for idx, (col, w) in enumerate(zip(columns, [h[1] for h in headings])):
            self.tree.heading(col, text=headings[idx][0])
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscroll=vsb.set)

    def create_buttons(self):
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(btn_frame, text="Ajouter membre", command=self.add_member).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Modifier", command=self.edit_member).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_member).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Exporter CSV", command=self.export_csv).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Fermer", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

    def refresh_members(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            conn = get_connection()
            df = pd.read_sql_query("SELECT * FROM membres ORDER BY name, prenom", conn)
            self.df = df
            for _, row in df.iterrows():
                self.tree.insert(
                    "", "end",
                    values=(
                        row["id"], row["name"], row["prenom"], row["email"], row.get("cotisation", ""),
                        row.get("commentaire", ""), row.get("telephone", ""), row.get("statut", ""),
                        row.get("date_adhesion", "")
                    )
                )
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'affichage des membres."))

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_member(self):
        EditMemberDialog(self.top, member_id=None, on_save=self.refresh_members)

    def edit_member(self):
        mid = self.get_selected_id()
        if not mid:
            messagebox.showwarning("Sélection", "Sélectionnez un membre à modifier.")
            return
        EditMemberDialog(self.top, member_id=mid, on_save=self.refresh_members)

    def delete_member(self):
        mid = self.get_selected_id()
        if not mid:
            messagebox.showwarning("Sélection", "Sélectionnez un membre à supprimer.")
            return
        if not messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir supprimer ce membre ?"):
            return
        confirm = simpledialog.askstring(
            "Confirmation",
            "Retapez SUPPRIMER pour confirmer la suppression du membre :",
            parent=self.top
        )
        if (confirm or "").strip().upper() != "SUPPRIMER":
            messagebox.showinfo("Annulé", "Suppression annulée.")
            return
        try:
            conn = get_connection()
            conn.execute("DELETE FROM membres WHERE id=?", (mid,))
            conn.commit()
            conn.close()
            logger.info(f"Membre supprimé id {mid}")
            self.refresh_members()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de la suppression du membre."))

    def export_csv(self):
        from tkinter import filedialog
        from utils.csv_helpers import write_csv
        try:
            filepath = filedialog.asksaveasfilename(
                title="Exporter membres en CSV",
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")]
            )
            if not filepath:
                return
            df = getattr(self, "df", None)
            if df is not None and not df.empty:
                write_csv(filepath, df.values.tolist(), header=list(df.columns))
                messagebox.showinfo("Export CSV", f"Export réussi dans {filepath}")
            else:
                messagebox.showwarning("Alerte", "Aucun membre à exporter.")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'export CSV."))

class EditMemberDialog(tk.Toplevel):
    def __init__(self, master, member_id=None, on_save=None):
        super().__init__(master)
        self.title("Membre" if member_id is None else "Modifier membre")
        self.member_id = member_id
        self.on_save = on_save
        self.geometry("420x440")
        self.resizable(False, False)

        self.nom_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.cotisation_var = tk.StringVar()
        self.commentaire_var = tk.StringVar()
        self.tel_var = tk.StringVar()
        self.statut_var = tk.StringVar()
        self.date_var = tk.StringVar()

        tk.Label(self, text="Name :").pack(pady=4)
        tk.Entry(self, textvariable=self.nom_var, width=30).pack()
        tk.Label(self, text="Prénom :").pack(pady=4)
        tk.Entry(self, textvariable=self.prenom_var, width=30).pack()
        tk.Label(self, text="Email :").pack(pady=4)
        tk.Entry(self, textvariable=self.email_var, width=35).pack()
        tk.Label(self, text="Cotisation :").pack(pady=4)
        cotisation_menu = ttk.Combobox(
            self, textvariable=self.cotisation_var, values=COTISATION_ETATS, state="readonly", width=16
        )
        cotisation_menu.pack()
        tk.Label(self, text="Commentaire :").pack(pady=4)
        tk.Entry(self, textvariable=self.commentaire_var, width=35).pack()
        tk.Label(self, text="Téléphone :").pack(pady=4)
        tk.Entry(self, textvariable=self.tel_var, width=18).pack()
        tk.Label(self, text="Statut :").pack(pady=4)
        statut_menu = ttk.Combobox(
            self, textvariable=self.statut_var, values=STATUTS, state="readonly", width=24
        )
        statut_menu.pack()
        tk.Label(self, text="Date adhésion (YYYY-MM-DD) :").pack(pady=4)
        tk.Entry(self, textvariable=self.date_var, width=20).pack()

        tk.Button(self, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=36, pady=16)
        tk.Button(self, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=36, pady=16)

        if self.member_id is not None:
            self.load_member()

    def load_member(self):
        try:
            conn = get_connection()
            row = conn.execute(
                "SELECT name, prenom, email, cotisation, commentaire, telephone, statut, date_adhesion FROM membres WHERE id=?",
                (self.member_id,)
            ).fetchone()
            conn.close()
            if row is not None:
                self.nom_var.set(row[0])
                self.prenom_var.set(row[1])
                self.email_var.set(row[2] if row[2] else "")
                self.cotisation_var.set(row[3] if row[3] else COTISATION_ETATS[1])  # défaut: "Non réglé"
                self.commentaire_var.set(row[4] if row[4] else "")
                self.tel_var.set(row[5] if row[5] else "")
                self.statut_var.set(row[6] if row[6] else STATUTS[0])
                self.date_var.set(row[7] if row[7] else "")
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors du chargement du membre."))

    def save(self):
        name = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        email = self.email_var.get().strip()
        cotisation = self.cotisation_var.get().strip()
        commentaire = self.commentaire_var.get().strip()
        tel = self.tel_var.get().strip()
        statut = self.statut_var.get().strip()
        date_adh = self.date_var.get().strip()
        if not is_required(name) or not is_required(prenom) or not is_required(date_adh):
            messagebox.showerror("Erreur", "Name, prénom et date d'adhésion sont obligatoires.")
            return
        if not cotisation:
            cotisation = COTISATION_ETATS[1]  # défaut: "Non réglé"
        if not statut:
            statut = STATUTS[0]
        if email and not is_email(email):
            messagebox.showerror("Erreur", "Email invalide.")
            return
        try:
            conn = get_connection()
            if self.member_id is not None:
                conn.execute(
                    "UPDATE membres SET name=?, prenom=?, email=?, cotisation=?, commentaire=?, telephone=?, statut=?, date_adhesion=? WHERE id=?",
                    (name, prenom, email, cotisation, commentaire, tel, statut, date_adh, self.member_id)
                )
            else:
                conn.execute(
                    "INSERT INTO membres (name, prenom, email, cotisation, commentaire, telephone, statut, date_adhesion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, prenom, email, cotisation, commentaire, tel, statut, date_adh)
                )
            conn.commit()
            conn.close()
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", handle_exception(e, "Erreur lors de l'enregistrement du membre."))