import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import modules.buvette_inventaire_db as db
import modules.buvette_db as buvette_db
from utils.app_logger import get_logger

logger = get_logger("buvette_inventaire_dialogs")

class InventaireDialog(tk.Toplevel):
    """Dialog for creating/editing buvette inventory with dynamic article lines."""
    
    def __init__(self, master, on_save=None, inventaire_id=None):
        super().__init__(master)
        self.title("Inventaire Buvette")
        self.geometry("900x700")
        self.on_save = on_save
        
        # Handle both inventaire_id (int) and inventaire (dict) for backward compatibility
        if inventaire_id is not None:
            if isinstance(inventaire_id, dict):
                # If a dict is passed, extract the id
                self.inventaire_id = inventaire_id.get("id")
            else:
                # It's an int
                self.inventaire_id = inventaire_id
        else:
            self.inventaire_id = None
        
        # Variables for header fields
        self.date_var = tk.StringVar(value=str(date.today()))
        self.type_var = tk.StringVar()
        self.evt_var = tk.StringVar()
        self.comment_var = tk.StringVar()
        
        # Create UI
        self._create_header_section()
        self._create_lines_section()
        self._create_button_section()
        
        # Load data if editing
        if self.inventaire_id:
            self._load_inventaire()
    
    def _create_header_section(self):
        """Create the header section with date, type, event, and comment fields."""
        frm = tk.Frame(self)
        frm.pack(padx=16, pady=8, fill=tk.X)
        
        # Row 0: Date and Type
        tk.Label(frm, text="Date :").grid(row=0, column=0, sticky="e", padx=(0, 5))
        tk.Entry(frm, textvariable=self.date_var, width=15).grid(row=0, column=1, sticky="w")
        
        tk.Label(frm, text="Type :").grid(row=0, column=2, sticky="e", padx=(20, 5))
        type_combo = ttk.Combobox(
            frm, 
            textvariable=self.type_var, 
            values=["avant", "apres", "hors_evenement"],
            width=16,
            state="readonly"
        )
        type_combo.grid(row=0, column=3, sticky="w")
        
        # Row 1: Event
        tk.Label(frm, text="Événement :").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=(5, 0))
        self.evt_cb = ttk.Combobox(frm, textvariable=self.evt_var, width=40, state="readonly")
        try:
            events = db.list_events()
            self.evt_cb["values"] = [""] + [f"{r['id']} - {r['name']}" for r in events]
        except Exception as e:
            logger.warning(f"Could not load events: {e}")
            self.evt_cb["values"] = [""]
        self.evt_cb.grid(row=1, column=1, columnspan=3, sticky="w", pady=(5, 0))
        
        # Row 2: Comment
        tk.Label(frm, text="Commentaire :").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=(5, 0))
        tk.Entry(frm, textvariable=self.comment_var, width=60).grid(
            row=2, column=1, columnspan=3, sticky="ew", pady=(5, 0)
        )
    
    def _create_lines_section(self):
        """Create the lines section with Treeview and add/remove buttons."""
        frame = tk.Frame(self)
        frame.pack(padx=16, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Articles inventoriés", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Treeview for article lines
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Columns: article_id (hidden), name, categorie, contenance, quantite
        self.lines_tree = ttk.Treeview(
            tree_frame,
            columns=("article_id", "name", "categorie", "contenance", "quantite"),
            show="headings",
            displaycolumns=("name", "categorie", "contenance", "quantite"),  # Hide article_id
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lines_tree.yview)
        
        # Configure columns
        self.lines_tree.column("article_id", width=50)  # Hidden via displaycolumns
        self.lines_tree.column("name", width=200, anchor="w")
        self.lines_tree.column("categorie", width=150, anchor="w")
        self.lines_tree.column("contenance", width=100, anchor="w")
        self.lines_tree.column("quantite", width=100, anchor="center")
        
        # Set headings (article_id won't be shown due to displaycolumns)
        self.lines_tree.heading("article_id", text="ID")
        self.lines_tree.heading("name", text="Article")
        self.lines_tree.heading("categorie", text="Catégorie")
        self.lines_tree.heading("contenance", text="Contenance")
        self.lines_tree.heading("quantite", text="Quantité")
        
        self.lines_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Buttons for add/remove
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(btn_frame, text="Ajouter ligne", command=self._add_line).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Supprimer ligne", command=self._remove_line).pack(side=tk.LEFT, padx=5)
    
    def _create_button_section(self):
        """Create the bottom button section."""
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=16)
        tk.Button(btn_frame, text="Enregistrer", command=self._save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Annuler", command=self.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def _add_line(self):
        """Open dialog to add a new line."""
        AddLineDialog(self, self._refresh_after_line_add)
    
    def _refresh_after_line_add(self, article_id, article_name, categorie, contenance, quantite):
        """Callback after adding a line."""
        # Check if article already exists in tree
        for item in self.lines_tree.get_children():
            values = self.lines_tree.item(item)["values"]
            if values[0] == article_id:
                # Update existing line
                self.lines_tree.item(item, values=(article_id, article_name, categorie, contenance, quantite))
                return
        
        # Add new line
        self.lines_tree.insert("", "end", values=(article_id, article_name, categorie, contenance, quantite))
    
    def _remove_line(self):
        """Remove selected line from tree."""
        selected = self.lines_tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une ligne à supprimer.")
            return
        
        if messagebox.askyesno("Confirmation", "Supprimer cette ligne ?"):
            for item in selected:
                self.lines_tree.delete(item)
    
    def _load_inventaire(self):
        """Load existing inventory data."""
        try:
            inv = db.get_inventaire_by_id(self.inventaire_id)
            if not inv:
                messagebox.showerror("Erreur", "Inventaire introuvable.")
                self.destroy()
                return
            
            # Load header data
            self.date_var.set(inv["date_inventaire"] or "")
            self.type_var.set(inv["type_inventaire"] or "")
            self.comment_var.set(inv["commentaire"] or "")
            if inv.get("event_id"):
                self.evt_var.set(f"{inv['event_id']} - {inv.get('event_name', '')}")
            
            # Load lines
            try:
                lignes = db.list_lignes_inventaire(self.inventaire_id)
                for ligne in lignes:
                    article_id = ligne["article_id"]
                    quantite = ligne["quantite"]
                    
                    # Get article details
                    try:
                        article = buvette_db.get_article_by_id(article_id)
                        if article:
                            self.lines_tree.insert("", "end", values=(
                                article_id,
                                article["name"],
                                article.get("categorie", ""),
                                article.get("contenance", ""),
                                quantite
                            ))
                    except Exception as e:
                        logger.warning(f"Could not load article {article_id}: {e}")
                        # Add line with minimal info
                        self.lines_tree.insert("", "end", values=(
                            article_id, f"Article #{article_id}", "", "", quantite
                        ))
            except Exception as e:
                logger.warning(f"Could not load inventory lines: {e}")
                messagebox.showwarning("Avertissement", f"Impossible de charger les lignes : {e}")
        
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement : {e}")
            self.destroy()
    
    def _save(self):
        """Save inventory and lines."""
        # Validate required fields
        type_inv = self.type_var.get()
        if not type_inv:
            messagebox.showerror("Erreur", "Le type d'inventaire est obligatoire.")
            return
        
        if type_inv not in ["avant", "apres", "hors_evenement"]:
            messagebox.showerror("Erreur", "Type d'inventaire invalide.")
            return
        
        date_inv = self.date_var.get()
        if not date_inv:
            messagebox.showerror("Erreur", "La date est obligatoire.")
            return
        
        commentaire = self.comment_var.get()
        evt = self.evt_var.get()
        event_id = None
        if evt and " - " in evt:
            try:
                event_id = int(evt.split(" - ")[0])
            except ValueError:
                pass
        
        try:
            # Insert or update inventory
            if self.inventaire_id:
                db.update_inventaire(self.inventaire_id, date_inv, event_id, type_inv, commentaire)
                inv_id = self.inventaire_id
            else:
                inv_id = db.insert_inventaire(date_inv, event_id, type_inv, commentaire)
            
            # Save lines
            for item in self.lines_tree.get_children():
                values = self.lines_tree.item(item)["values"]
                article_id = values[0]
                quantite = values[4]
                
                # Upsert line
                db.upsert_ligne_inventaire(inv_id, article_id, quantite)
            
            # Update article stock if quantite field exists
            self._update_article_stock()
            
            messagebox.showinfo("Succès", "Inventaire enregistré avec succès.")
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
        
        except Exception as e:
            logger.error(f"Error saving inventory: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
    
    def _update_article_stock(self):
        """Update article stock based on inventory quantities (if quantite field exists)."""
        try:
            # Check if buvette_articles has a quantite field
            conn = db.get_conn()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(buvette_articles)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "quantite" not in columns:
                logger.info("buvette_articles table does not have quantite field, skipping stock update")
                conn.close()
                return
            
            # Update stock for each line
            for item in self.lines_tree.get_children():
                values = self.lines_tree.item(item)["values"]
                article_id = values[0]
                quantite = values[4]
                
                cursor.execute(
                    "UPDATE buvette_articles SET quantite=? WHERE id=?",
                    (quantite, article_id)
                )
            
            conn.commit()
            conn.close()
            logger.info("Article stock updated successfully")
        
        except Exception as e:
            logger.warning(f"Could not update article stock: {e}")


class AddLineDialog(tk.Toplevel):
    """Dialog for adding a line to inventory."""
    
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Ajouter une ligne")
        self.geometry("500x250")
        self.callback = callback
        
        # Variables
        self.article_var = tk.StringVar()
        self.quantite_var = tk.IntVar(value=0)
        self.create_new_var = tk.BooleanVar(value=False)
        
        # New article fields
        self.new_name_var = tk.StringVar()
        self.new_categorie_var = tk.StringVar()
        self.new_contenance_var = tk.StringVar()
        
        self._create_widgets()
        self._toggle_fields()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        frame = tk.Frame(self, padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Checkbox to create new article
        tk.Checkbutton(
            frame,
            text="Créer un nouvel article",
            variable=self.create_new_var,
            command=self._toggle_fields
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Select existing article
        self.select_label = tk.Label(frame, text="Article :")
        self.select_label.grid(row=1, column=0, sticky="e", padx=(0, 5))
        
        self.article_combo = ttk.Combobox(frame, textvariable=self.article_var, width=40, state="readonly")
        try:
            articles = buvette_db.list_articles()
            self.article_combo["values"] = [
                f"{a['id']} - {a['name']} ({a.get('contenance', '')})" for a in articles
            ]
        except Exception as e:
            logger.warning(f"Could not load articles: {e}")
            self.article_combo["values"] = []
        self.article_combo.grid(row=1, column=1, sticky="w")
        
        # New article fields
        self.name_label = tk.Label(frame, text="Nom :")
        self.name_label.grid(row=2, column=0, sticky="e", padx=(0, 5), pady=(5, 0))
        self.name_entry = tk.Entry(frame, textvariable=self.new_name_var, width=40)
        self.name_entry.grid(row=2, column=1, sticky="w", pady=(5, 0))
        
        self.categorie_label = tk.Label(frame, text="Catégorie :")
        self.categorie_label.grid(row=3, column=0, sticky="e", padx=(0, 5), pady=(5, 0))
        self.categorie_entry = tk.Entry(frame, textvariable=self.new_categorie_var, width=40)
        self.categorie_entry.grid(row=3, column=1, sticky="w", pady=(5, 0))
        
        self.contenance_label = tk.Label(frame, text="Contenance :")
        self.contenance_label.grid(row=4, column=0, sticky="e", padx=(0, 5), pady=(5, 0))
        self.contenance_entry = tk.Entry(frame, textvariable=self.new_contenance_var, width=40)
        self.contenance_entry.grid(row=4, column=1, sticky="w", pady=(5, 0))
        
        # Quantity
        tk.Label(frame, text="Quantité :").grid(row=5, column=0, sticky="e", padx=(0, 5), pady=(10, 0))
        tk.Entry(frame, textvariable=self.quantite_var, width=15).grid(row=5, column=1, sticky="w", pady=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        tk.Button(btn_frame, text="Ajouter", command=self._add, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Annuler", command=self.destroy, width=12).pack(side=tk.LEFT, padx=5)
    
    def _toggle_fields(self):
        """Toggle between existing article selection and new article creation."""
        if self.create_new_var.get():
            # Show new article fields
            self.select_label.config(state="disabled")
            self.article_combo.config(state="disabled")
            self.name_label.config(state="normal")
            self.name_entry.config(state="normal")
            self.categorie_label.config(state="normal")
            self.categorie_entry.config(state="normal")
            self.contenance_label.config(state="normal")
            self.contenance_entry.config(state="normal")
        else:
            # Show existing article selection
            self.select_label.config(state="normal")
            self.article_combo.config(state="readonly")
            self.name_label.config(state="disabled")
            self.name_entry.config(state="disabled")
            self.categorie_label.config(state="disabled")
            self.categorie_entry.config(state="disabled")
            self.contenance_label.config(state="disabled")
            self.contenance_entry.config(state="disabled")
    
    def _add(self):
        """Add the line."""
        quantite = self.quantite_var.get()
        
        try:
            if self.create_new_var.get():
                # Create new article
                name = self.new_name_var.get().strip()
                if not name:
                    messagebox.showerror("Erreur", "Le nom de l'article est obligatoire.")
                    return
                
                categorie = self.new_categorie_var.get().strip()
                contenance = self.new_contenance_var.get().strip()
                
                # Insert new article using existing function
                try:
                    buvette_db.insert_article(
                        name=name, 
                        categorie=categorie, 
                        unite="", 
                        commentaire="", 
                        contenance=contenance
                    )
                    # Get the newly created article's ID
                    articles = buvette_db.list_articles()
                    article = next((a for a in articles if a["name"] == name), None)
                    if not article:
                        messagebox.showerror("Erreur", "Article créé mais introuvable.")
                        return
                    article_id = article["id"]
                except Exception as e:
                    logger.error(f"Error creating article: {e}")
                    messagebox.showerror("Erreur", f"Erreur lors de la création de l'article : {e}")
                    return
            else:
                # Use existing article
                article_str = self.article_var.get()
                if not article_str:
                    messagebox.showerror("Erreur", "Veuillez sélectionner un article.")
                    return
                
                article_id = int(article_str.split(" - ")[0])
                article = buvette_db.get_article_by_id(article_id)
                if not article:
                    messagebox.showerror("Erreur", "Article introuvable.")
                    return
                
                name = article["name"]
                categorie = article.get("categorie", "")
                contenance = article.get("contenance", "")
            
            # Call callback with article data
            self.callback(article_id, name, categorie, contenance, quantite)
            self.destroy()
        
        except Exception as e:
            logger.error(f"Error adding line: {e}")
            messagebox.showerror("Erreur", f"Erreur : {e}")