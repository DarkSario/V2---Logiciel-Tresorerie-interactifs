"""
Article Dialog for Buvette Articles Management.

This dialog allows creating and editing buvette articles with all their properties
including the purchase price per unit. This is a standalone UI component that can
be used independently from the main buvette module.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from lib.db_articles import (
    get_article_by_id, 
    create_article, 
    get_article_by_name
)
from modules.buvette_db import update_article

class ArticleDialog(tk.Toplevel):
    """
    Dialog for creating/editing a buvette article.
    
    Features:
    - Name, category, unit, capacity fields
    - Purchase price per unit field (new feature)
    - Comment field
    - Validation and save to database
    """
    
    def __init__(self, master, article_id=None, on_save=None):
        """
        Initialize the article dialog.
        
        Args:
            master: Parent window
            article_id: ID of article to edit (None for new article)
            on_save: Callback function to call after successful save
        """
        super().__init__(master)
        self.title("Article buvette")
        self.geometry("380x450")
        self.on_save = on_save
        self.article_id = article_id
        
        # Variables for form fields
        self.nom_var = tk.StringVar()
        self.categorie_var = tk.StringVar()
        self.unite_var = tk.StringVar()
        self.contenance_var = tk.StringVar()
        self.purchase_price_var = tk.DoubleVar()
        self.comment_var = tk.StringVar()
        
        self._create_form()
        
        # Load existing article if editing
        if article_id:
            self._load_article()
    
    def _create_form(self):
        """Create the form fields."""
        # Name field
        tk.Label(self, text="Nom :").pack(pady=(10, 4))
        tk.Entry(self, textvariable=self.nom_var, width=30).pack()
        
        # Category field
        tk.Label(self, text="Catégorie :").pack(pady=(8, 4))
        tk.Entry(self, textvariable=self.categorie_var, width=25).pack()
        
        # Unit field
        tk.Label(self, text="Unité (ex: canette, bouteille...) :").pack(pady=(8, 4))
        tk.Entry(self, textvariable=self.unite_var, width=18).pack()
        
        # Capacity field with dropdown
        tk.Label(self, text="Contenance :").pack(pady=(8, 4))
        contenance_options = ["0.25L", "0.33L", "0.5L", "0.75L", "1L", "1.5L", "2L"]
        self.contenance_cb = ttk.Combobox(
            self, 
            textvariable=self.contenance_var, 
            values=contenance_options,
            state="readonly", 
            width=10
        )
        self.contenance_cb.pack()
        
        # Purchase price field (NEW FEATURE)
        tk.Label(self, text="Prix achat / unité (€) :").pack(pady=(8, 4))
        purchase_price_entry = tk.Entry(self, textvariable=self.purchase_price_var, width=15)
        purchase_price_entry.pack()
        
        # Comment field
        tk.Label(self, text="Commentaire :").pack(pady=(8, 4))
        tk.Entry(self, textvariable=self.comment_var, width=35).pack()
        
        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Enregistrer", command=self._save, width=12).pack(side=tk.LEFT, padx=12)
        tk.Button(btn_frame, text="Annuler", command=self.destroy, width=12).pack(side=tk.RIGHT, padx=12)
    
    def _load_article(self):
        """Load article data if editing existing article."""
        try:
            article = get_article_by_id(self.article_id)
            if article:
                self.nom_var.set(article["name"] if article["name"] else "")
                self.categorie_var.set(article["categorie"] if article["categorie"] else "")
                self.unite_var.set(article["unite"] if article["unite"] else "")
                self.contenance_var.set(article["contenance"] if article["contenance"] else "")
                self.comment_var.set(article["commentaire"] if article["commentaire"] else "")
                
                # Load purchase price if it exists
                if "purchase_price" in article.keys() and article["purchase_price"] is not None:
                    self.purchase_price_var.set(article["purchase_price"])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'article: {e}")
    
    def _save(self):
        """Save the article to database."""
        # Validate name (required field)
        name = self.nom_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom de l'article est obligatoire.")
            return
        
        # Get other fields
        categorie = self.categorie_var.get().strip()
        unite = self.unite_var.get().strip()
        contenance = self.contenance_var.get().strip()
        comment = self.comment_var.get().strip()
        
        # Get purchase price, handling empty or invalid input
        try:
            purchase_price = self.purchase_price_var.get()
            # If it's 0.0 and the field was empty, set to None
            if purchase_price == 0.0:
                try:
                    # Check if field is actually empty
                    raw_value = self.purchase_price_var.get()
                    if raw_value == 0.0:
                        purchase_price = None
                except:
                    purchase_price = None
        except tk.TclError:
            # TclError occurs when the DoubleVar field is empty or contains invalid data
            purchase_price = None
        
        try:
            if self.article_id:
                # Update existing article
                update_article(
                    self.article_id, 
                    name, 
                    categorie, 
                    unite, 
                    comment, 
                    contenance, 
                    purchase_price
                )
            else:
                # Create new article
                # Check if article with same name already exists
                existing = get_article_by_name(name)
                if existing:
                    messagebox.showerror(
                        "Erreur", 
                        f"Un article avec le nom '{name}' existe déjà."
                    )
                    return
                
                create_article(
                    name, 
                    categorie, 
                    unite, 
                    contenance, 
                    comment, 
                    stock=0,  # Initial stock is 0
                    purchase_price=purchase_price
                )
            
            # Call callback if provided
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {e}")
