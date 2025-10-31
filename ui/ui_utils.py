import tkinter as tk
from tkinter import ttk

def clear_treeview(tree):
    for row in tree.get_children():
        tree.delete(row)

def ask_confirm(title, message):
    from tkinter import messagebox
    return messagebox.askyesno(title, message)

def show_info(title, message):
    from tkinter import messagebox
    messagebox.showinfo(title, message)

def show_error(title, message):
    from tkinter import messagebox
    messagebox.showerror(title, message)

def create_popup(title, message):
    popup = tk.Toplevel()
    popup.title(title)
    tk.Label(popup, text=message, padx=20, pady=20).pack()
    tk.Button(popup, text="Fermer", command=popup.destroy).pack(pady=12)
    popup.grab_set()
    popup.wait_window()