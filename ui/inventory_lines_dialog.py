"""
Detailed Inventory Lines Dialog for Buvette.

This dialog provides a comprehensive interface for creating detailed inventories with:
- Treeview showing inventory lines with article details
- Add/remove article lines
- Sub-dialog to add articles (existing or new)
- Automatic stock update on save
- Purchase price tracking

This is a separate interface from the existing simple inventory dialog.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date
from lib.db_articles import (
    get_all_articles,
    get_article_by_id,
    get_article_by_name,
    create_article,
    update_article_stock,
    update_article_purchase_price
)
from modules.buvette_inventaire_db import (
    insert_inventaire,
    update_inventaire,
    list_events,
    list_lignes_inventaire
)
from db.db import get_connection
from utils.app_logger import get_logger
from utils.db_helpers import row_to_dict
from modules.db_row_utils import _row_to_dict, _rows_to_dicts
from modules.inventory_lines_dialog import load_inventory_lines

logger = get_logger("inventory_lines_dialog")

class InventoryLinesDialog(tk.Toplevel):
    """
    Dialog for creating a detailed inventory with dynamic lines.
    
    This provides a more advanced interface than the simple inventory dialog,
    with support for:
    - Adding existing articles or creating new ones
    - Tracking quantities counted during inventory
    - Automatic stock updates
    - Purchase price management
    """
    
    def __init__(self, master, edit_inventory=None):
        """
        Initialize the detailed inventory dialog.
        
        Args:
            master: Parent window
            edit_inventory: Optional dict with inventory data for edit mode (keys: id, date_inventaire, type_inventaire, event_id, commentaire)
        """
        super().__init__(master)
        self.edit_inventory = edit_inventory
        self.inventory_id = edit_inventory["id"] if edit_inventory else None
        
        if edit_inventory:
            self.title("Modifier inventaire détaillé")
        else:
            self.title("Nouvel inventaire détaillé")
        self.geometry("950x700")
        
        # Variables for header fields
        self.date_var = tk.StringVar(value=str(date.today()))
        self.type_var = tk.StringVar(value="hors_evenement")
        self.evt_var = tk.StringVar()
        self.comment_var = tk.StringVar()
        
        # Inventory lines data: list of dicts with keys: article_id, name, categorie, contenance, quantite, purchase_price
        self.inventory_lines = []
        
        self._create_header_section()
        self._create_lines_section()
        self._create_button_section()
        
        # Load existing inventory data if in edit mode
        if edit_inventory:
            self._load_inventory_data()
        
    def _create_header_section(self):
        """Create the header section with date, type, event, and comment fields."""
        frm = tk.Frame(self)
        frm.pack(padx=16, pady=12, fill=tk.X)
        
        tk.Label(frm, text="Inventaire détaillé", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Row 0: Date and Type
        row0 = tk.Frame(frm)
        row0.pack(fill=tk.X, pady=2)
        
        tk.Label(row0, text="Date :").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row0, textvariable=self.date_var, width=15).pack(side=tk.LEFT)
        
        tk.Label(row0, text="Type :").pack(side=tk.LEFT, padx=(30, 5))
        type_combo = ttk.Combobox(
            row0,
            textvariable=self.type_var,
            values=["avant", "apres", "hors_evenement"],
            width=16,
            state="readonly"
        )
        type_combo.pack(side=tk.LEFT)
        
        # Row 1: Event
        row1 = tk.Frame(frm)
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="Événement :").pack(side=tk.LEFT, padx=(0, 5))
        self.evt_cb = ttk.Combobox(row1, textvariable=self.evt_var, width=40, state="readonly")
        try:
            events = list_events()
            # Convert Row objects to dicts for safe access
            events = _rows_to_dicts(events)
            self.evt_cb["values"] = [""] + [f"{r['id']} - {r['name']}" for r in events]
        except Exception as e:
            logger.warning(f"Could not load events: {e}")
            self.evt_cb["values"] = [""]
        self.evt_cb.pack(side=tk.LEFT)
        
        # Row 2: Comment
        row2 = tk.Frame(frm)
        row2.pack(fill=tk.X, pady=2)
        
        tk.Label(row2, text="Commentaire :").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(row2, textvariable=self.comment_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_lines_section(self):
        """Create the lines section with Treeview and buttons."""
        frame = tk.Frame(self)
        frame.pack(padx=16, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Articles inventoriés", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Treeview for article lines
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Columns: name, categorie, contenance, quantite, purchase_price
        self.lines_tree = ttk.Treeview(
            tree_frame,
            columns=("name", "categorie", "contenance", "quantite", "purchase_price"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.lines_tree.yview)
        
        # Configure columns
        self.lines_tree.column("name", width=200, anchor="w")
        self.lines_tree.column("categorie", width=150, anchor="w")
        self.lines_tree.column("contenance", width=100, anchor="center")
        self.lines_tree.column("quantite", width=100, anchor="center")
        self.lines_tree.column("purchase_price", width=120, anchor="center")
        
        # Set headings
        self.lines_tree.heading("name", text="Article")
        self.lines_tree.heading("categorie", text="Catégorie")
        self.lines_tree.heading("contenance", text="Contenance")
        self.lines_tree.heading("quantite", text="Quantité comptée")
        self.lines_tree.heading("purchase_price", text="Prix achat (€)")
        
        self.lines_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Buttons for add/remove
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        tk.Button(
            btn_frame, 
            text="Ajouter article", 
            command=self._add_article_line,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame, 
            text="Supprimer ligne", 
            command=self._remove_line,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="Modifier ligne",
            command=self._edit_line,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_button_section(self):
        """Create the bottom button section."""
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=16)
        tk.Button(
            btn_frame, 
            text="Enregistrer", 
            command=self._save,
            width=14,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            btn_frame, 
            text="Annuler", 
            command=self.destroy,
            width=14
        ).pack(side=tk.LEFT, padx=10)
    
    def _add_article_line(self):
        """Open sub-dialog to add an article line."""
        AddArticleLineDialog(self, self._on_article_added)
    
    def _on_article_added(self, article_data):
        """
        Callback when an article line is added.
        
        Args:
            article_data: Dict with keys: article_id, name, categorie, contenance, quantite, purchase_price
        """
        # Check if article already exists in the list
        for i, line in enumerate(self.inventory_lines):
            if line["article_id"] == article_data["article_id"]:
                # Update existing line
                self.inventory_lines[i] = article_data
                self._refresh_tree()
                return
        
        # Add new line
        self.inventory_lines.append(article_data)
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh the treeview with current inventory lines."""
        # Clear tree
        for item in self.lines_tree.get_children():
            self.lines_tree.delete(item)
        
        # Add lines
        for line in self.inventory_lines:
            purchase_price_display = ""
            if line.get("purchase_price") is not None:
                purchase_price_display = f"{line['purchase_price']:.2f}"
            
            self.lines_tree.insert(
                "", 
                "end",
                values=(
                    line["name"],
                    line.get("categorie", ""),
                    line.get("contenance", ""),
                    line["quantite"],
                    purchase_price_display
                )
            )
    
    def _remove_line(self):
        """Remove the selected line from inventory."""
        selection = self.lines_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une ligne à supprimer.")
            return
        
        # Get the index of selected item
        item = selection[0]
        index = self.lines_tree.index(item)
        
        # Remove from data
        if 0 <= index < len(self.inventory_lines):
            del self.inventory_lines[index]
            self._refresh_tree()
    
    def _edit_line(self):
        """Edit the selected line."""
        selection = self.lines_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une ligne à modifier.")
            return
        
        # Get the index of selected item
        item = selection[0]
        index = self.lines_tree.index(item)
        
        if 0 <= index < len(self.inventory_lines):
            line_data = self.inventory_lines[index]
            # Open edit dialog with current data
            AddArticleLineDialog(self, self._on_article_added, edit_data=line_data)
    
    def _load_inventory_data(self):
        """Load existing inventory data for edit mode."""
        if not self.edit_inventory:
            return
        
        try:
            # Load header data
            self.date_var.set(self.edit_inventory.get("date_inventaire", ""))
            self.type_var.set(self.edit_inventory.get("type_inventaire", "hors_evenement"))
            self.comment_var.set(self.edit_inventory.get("commentaire", ""))
            
            # Load event if present
            event_id = self.edit_inventory.get("event_id")
            if event_id:
                # Try to find and select the event in combobox
                for val in self.evt_cb["values"]:
                    if val and str(event_id) in val:
                        self.evt_var.set(val)
                        break
            
            # Load inventory lines using robust helper with error reporting
            lines = load_inventory_lines(self.inventory_id)
            
            for line_dict in lines:
                # line_dict is already a dict from load_inventory_lines
                article_id = line_dict.get("article_id")
                if not article_id:
                    logger.warning(f"Skipping line with missing article_id: {line_dict}")
                    continue
                
                # Get article details
                article = get_article_by_id(article_id)
                if article:
                    # Convert article Row to dict for safe .get() access
                    article_dict = _row_to_dict(article)
                    
                    article_data = {
                        "article_id": article_id,
                        "name": article_dict.get("name", ""),
                        "categorie": article_dict.get("categorie", ""),
                        "contenance": article_dict.get("contenance", ""),
                        "quantite": line_dict.get("quantite", 0),
                        "purchase_price": article_dict.get("purchase_price")
                    }
                    self.inventory_lines.append(article_data)
            
            self._refresh_tree()
            
        except Exception as e:
            logger.error(f"Error loading inventory data: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'inventaire: {e}")
    
    def _save(self):
        """Save the inventory to database."""
        # Validate
        date_str = self.date_var.get().strip()
        if not date_str:
            messagebox.showerror("Erreur", "La date est obligatoire.")
            return
        
        type_inv = self.type_var.get().strip()
        if type_inv not in ["avant", "apres", "hors_evenement"]:
            messagebox.showerror("Erreur", "Le type d'inventaire doit être: avant, apres ou hors_evenement.")
            return
        
        if not self.inventory_lines:
            messagebox.showwarning("Attention", "L'inventaire ne contient aucun article.")
            return
        
        # Get event_id if selected
        evt_id = None
        evt_str = self.evt_var.get().strip()
        if evt_str:
            try:
                evt_id = int(evt_str.split(" - ")[0])
            except:
                pass
        
        comment = self.comment_var.get().strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.inventory_id:
                # Edit mode: Update existing inventory
                from modules.buvette_inventaire_db import update_inventaire, delete_ligne_inventaire
                
                # Update inventory header
                update_inventaire(self.inventory_id, date_str, evt_id, type_inv, comment)
                
                # Delete existing lines
                cursor.execute("DELETE FROM buvette_inventaire_lignes WHERE inventaire_id=?", (self.inventory_id,))
                
                inv_id = self.inventory_id
            else:
                # Insert mode: Create new inventory
                inv_id = insert_inventaire(date_str, evt_id, type_inv, comment)
            
            # Insert/update inventory lines and update stock
            for line in self.inventory_lines:
                article_id = line["article_id"]
                quantite = line["quantite"]
                
                # Insert line (with commentaire column for consistency)
                cursor.execute("""
                    INSERT INTO buvette_inventaire_lignes (inventaire_id, article_id, quantite, commentaire)
                    VALUES (?, ?, ?, ?)
                """, (inv_id, article_id, quantite, ""))
                
                # Update article stock (stock = quantity counted)
                update_article_stock(article_id, quantite)
                
                # Update purchase price if provided
                if line.get("purchase_price") is not None:
                    update_article_purchase_price(article_id, line["purchase_price"])
            
            conn.commit()
            conn.close()
            
            action = "modifié" if self.inventory_id else "enregistré"
            messagebox.showinfo(
                "Succès", 
                f"Inventaire {action} avec succès!\n{len(self.inventory_lines)} article(s) traité(s)."
            )
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error saving inventory: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {e}")


class AddArticleLineDialog(tk.Toplevel):
    """
    Sub-dialog to add an article line to the inventory.
    
    Allows:
    - Selecting an existing article
    - Creating a new article
    - Entering quantity counted
    - Optionally entering/updating purchase price
    """
    
    def __init__(self, master, callback, edit_data=None):
        """
        Initialize the add article line dialog.
        
        Args:
            master: Parent window
            callback: Function to call with article data when done
            edit_data: Optional dict with existing line data for editing
        """
        super().__init__(master)
        self.title("Ajouter/Modifier article inventaire")
        self.geometry("450x500")
        self.callback = callback
        self.edit_data = edit_data
        
        # Variables
        self.mode_var = tk.StringVar(value="existing")  # "existing" or "new"
        self.article_var = tk.StringVar()
        self.new_name_var = tk.StringVar()
        self.new_categorie_var = tk.StringVar()
        self.new_contenance_var = tk.StringVar()
        self.quantite_var = tk.IntVar(value=0)
        self.purchase_price_var = tk.DoubleVar()
        
        # Article lookup dict
        self.articles_dict = {}
        
        self._create_ui()
        
        # Load existing data if editing
        if edit_data:
            self._load_edit_data()
    
    def _create_ui(self):
        """Create the UI elements."""
        # Mode selection
        mode_frame = tk.LabelFrame(self, text="Mode", padx=10, pady=10)
        mode_frame.pack(padx=15, pady=10, fill=tk.X)
        
        tk.Radiobutton(
            mode_frame,
            text="Sélectionner un article existant",
            variable=self.mode_var,
            value="existing",
            command=self._on_mode_change
        ).pack(anchor="w")
        
        tk.Radiobutton(
            mode_frame,
            text="Créer un nouvel article",
            variable=self.mode_var,
            value="new",
            command=self._on_mode_change
        ).pack(anchor="w")
        
        # Existing article section
        self.existing_frame = tk.LabelFrame(self, text="Article existant", padx=10, pady=10)
        self.existing_frame.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(self.existing_frame, text="Sélectionner un article :").pack(anchor="w", pady=2)
        self.article_cb = ttk.Combobox(
            self.existing_frame,
            textvariable=self.article_var,
            state="readonly",
            width=35
        )
        self.article_cb.pack(fill=tk.X, pady=2)
        self._load_articles()
        
        # New article section
        self.new_frame = tk.LabelFrame(self, text="Nouvel article", padx=10, pady=10)
        self.new_frame.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
        self.new_frame.pack_forget()  # Hidden by default
        
        tk.Label(self.new_frame, text="Nom :").pack(anchor="w", pady=2)
        tk.Entry(self.new_frame, textvariable=self.new_name_var, width=30).pack(fill=tk.X, pady=2)
        
        tk.Label(self.new_frame, text="Catégorie :").pack(anchor="w", pady=2)
        tk.Entry(self.new_frame, textvariable=self.new_categorie_var, width=25).pack(fill=tk.X, pady=2)
        
        tk.Label(self.new_frame, text="Contenance :").pack(anchor="w", pady=2)
        contenance_options = ["0.25L", "0.33L", "0.5L", "0.75L", "1L", "1.5L", "2L"]
        self.new_contenance_cb = ttk.Combobox(
            self.new_frame,
            textvariable=self.new_contenance_var,
            values=contenance_options,
            state="readonly",
            width=10
        )
        self.new_contenance_cb.pack(anchor="w", pady=2)
        
        # Quantity and price section
        qty_frame = tk.LabelFrame(self, text="Quantité et prix", padx=10, pady=10)
        qty_frame.pack(padx=15, pady=5, fill=tk.X)
        
        tk.Label(qty_frame, text="Quantité comptée :").pack(anchor="w", pady=2)
        tk.Entry(qty_frame, textvariable=self.quantite_var, width=15).pack(anchor="w", pady=2)
        
        tk.Label(qty_frame, text="Prix d'achat / unité (€) :").pack(anchor="w", pady=2)
        tk.Entry(qty_frame, textvariable=self.purchase_price_var, width=15).pack(anchor="w", pady=2)
        
        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Valider", command=self._validate, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Annuler", command=self.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def _load_articles(self):
        """Load existing articles into combobox."""
        try:
            articles = get_all_articles()
            # Convert all Row objects to dicts for safe access
            articles_dicts = _rows_to_dicts(articles)
            
            article_list = []
            self.articles_dict = {}
            
            for art_dict in articles_dicts:
                display_str = f"{art_dict.get('name', '')}"
                if art_dict.get("contenance"):
                    display_str += f" ({art_dict['contenance']})"
                article_list.append(display_str)
                self.articles_dict[display_str] = art_dict
            
            self.article_cb["values"] = article_list
            
        except Exception as e:
            logger.error(f"Error loading articles: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement des articles: {e}")
    
    def _on_mode_change(self):
        """Handle mode change between existing and new article."""
        if self.mode_var.get() == "existing":
            self.existing_frame.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
            self.new_frame.pack_forget()
        else:
            self.existing_frame.pack_forget()
            self.new_frame.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
    
    def _load_edit_data(self):
        """Load existing line data for editing."""
        if self.edit_data:
            # Set quantity
            self.quantite_var.set(self.edit_data.get("quantite", 0))
            
            # Set purchase price if available
            if self.edit_data.get("purchase_price") is not None:
                self.purchase_price_var.set(self.edit_data["purchase_price"])
            
            # Try to select the article
            for display_str, art in self.articles_dict.items():
                if art["id"] == self.edit_data["article_id"]:
                    self.article_var.set(display_str)
                    break
    
    def _validate(self):
        """Validate and return the article data."""
        try:
            quantite = self.quantite_var.get()
            if quantite < 0:
                messagebox.showerror("Erreur", "La quantité ne peut pas être négative.")
                return
            
            # Get purchase price
            try:
                purchase_price = self.purchase_price_var.get()
                if purchase_price == 0.0:
                    purchase_price = None
            except tk.TclError:
                purchase_price = None
            
            article_id = None
            article_name = ""
            article_categorie = ""
            article_contenance = ""
            
            if self.mode_var.get() == "existing":
                # Existing article
                selected = self.article_var.get()
                if not selected:
                    messagebox.showerror("Erreur", "Veuillez sélectionner un article.")
                    return
                
                article = self.articles_dict[selected]
                article_id = article["id"]
                article_name = article["name"]
                article_categorie = article["categorie"] if article["categorie"] else ""
                article_contenance = article["contenance"] if article["contenance"] else ""
                
            else:
                # New article
                article_name = self.new_name_var.get().strip()
                if not article_name:
                    messagebox.showerror("Erreur", "Le nom de l'article est obligatoire.")
                    return
                
                # Check if article already exists
                existing = get_article_by_name(article_name)
                if existing:
                    # Convert Row to dict for safe access
                    existing_dict = _row_to_dict(existing)
                    if messagebox.askyesno(
                        "Article existant",
                        f"Un article avec le nom '{article_name}' existe déjà. Voulez-vous l'utiliser?"
                    ):
                        article_id = existing_dict.get("id")
                        article_categorie = existing_dict.get("categorie", "")
                        article_contenance = existing_dict.get("contenance", "")
                    else:
                        return
                else:
                    # Create new article
                    article_categorie = self.new_categorie_var.get().strip()
                    article_contenance = self.new_contenance_var.get().strip()
                    
                    article_id = create_article(
                        name=article_name,
                        categorie=article_categorie,
                        unite="unité",
                        contenance=article_contenance,
                        commentaire="",
                        stock=0,
                        purchase_price=purchase_price
                    )
            
            # Return article data
            article_data = {
                "article_id": article_id,
                "name": article_name,
                "categorie": article_categorie,
                "contenance": article_contenance,
                "quantite": quantite,
                "purchase_price": purchase_price
            }
            
            self.callback(article_data)
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error validating article line: {e}")
            messagebox.showerror("Erreur", f"Erreur: {e}")
