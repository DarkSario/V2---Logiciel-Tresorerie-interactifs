import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import pandas as pd
from dialogs.edit_field_dialog import EditFieldDialog
from db.db import get_connection, get_df_or_sql
from utils.error_handler import handle_errors

# Optionally handle DataSource if present
try:
    from db.db import DataSource
    HAS_DATASOURCE = True
except ImportError:
    HAS_DATASOURCE = False

class EditEventDialog(tk.Toplevel):
    def __init__(self, master, event_id, on_save=None):
        super().__init__(master)
        self.title("Ajouter/Modifier événement")
        self.event_id = event_id
        self.on_save = on_save
        self.geometry("400x340")
        self.resizable(False, False)

        self.name_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.lieu_var = tk.StringVar()
        self.commentaire_var = tk.StringVar()

        row = 0
        tk.Label(self, text="Name :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.name_var, width=32).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Date :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        DateEntry(self, textvariable=self.date_var, date_pattern='yyyy-mm-dd').grid(row=row, column=1, pady=2, sticky="w"); row += 1
        tk.Label(self, text="Lieu :").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        tk.Entry(self, textvariable=self.lieu_var, width=32).grid(row=row, column=1, pady=2); row += 1
        tk.Label(self, text="Commentaire :").grid(row=row, column=0, sticky="nw", padx=12, pady=8)
        self.commentaire_widget = tk.Text(self, height=5, width=32, wrap=tk.WORD)
        self.commentaire_widget.grid(row=row, column=1, pady=2, sticky="w"); row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=16)
        tk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.RIGHT, padx=16)

        if self.event_id is not None:
            self.prefill_fields()

    def prefill_fields(self):
        try:
            if HAS_DATASOURCE and getattr(DataSource, "is_visualisation", False):
                df = get_df_or_sql("events")
                row = df[df['id'] == self.event_id].iloc[0]
            else:
                conn = get_connection()
                row = conn.execute(
                    "SELECT name, date, lieu, commentaire FROM events WHERE id=?", (self.event_id,)
                ).fetchone()
                conn.close()
            if row is not None:
                if not isinstance(row, pd.Series):
                    self.name_var.set(row[0])
                    self.date_var.set(row[1])
                    self.lieu_var.set(row[2] if row[2] else "")
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row[3] if row[3] else "")
                else:
                    self.name_var.set(row["name"])
                    self.date_var.set(row["date"])
                    self.lieu_var.set(row["lieu"] if row["lieu"] else "")
                    self.commentaire_widget.delete("1.0", tk.END)
                    self.commentaire_widget.insert("1.0", row["commentaire"] if row["commentaire"] else "")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement de l'événement : {e}")

    @handle_errors
    def save(self):
        name = self.name_var.get().strip()
        date = self.date_var.get().strip()
        lieu = self.lieu_var.get().strip()
        commentaire = self.commentaire_widget.get("1.0", tk.END).strip()
        if not name or not date:
            messagebox.showerror("Erreur", "Name et date obligatoires.")
            return
        conn = get_connection()
        try:
            if self.event_id is None:
                conn.execute(
                    "INSERT INTO events (name, date, lieu, commentaire) VALUES (?, ?, ?, ?)",
                    (name, date, lieu, commentaire)
                )
            else:
                conn.execute(
                    "UPDATE events SET name=?, date=?, lieu=?, commentaire=? WHERE id=?",
                    (name, date, lieu, commentaire, self.event_id)
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()