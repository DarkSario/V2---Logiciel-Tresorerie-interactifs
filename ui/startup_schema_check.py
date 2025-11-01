#!/usr/bin/env python3
"""
Module de vérification automatique du schéma de base de données au démarrage.

Ce module compare le schéma attendu par le code (extrait via analyze_modules_columns.py)
avec le schéma réel de la base de données. Si des colonnes manquent, une fenêtre d'alerte
est affichée avec les écarts et propose à l'utilisateur d'exécuter une mise à jour sûre
ou d'ignorer les différences.

Usage:
    from ui import startup_schema_check
    startup_schema_check.run_check(root_window)
"""

import os
import sys
import sqlite3
import subprocess
import re
import importlib.util
import tkinter as tk
from tkinter import Toplevel, Label, Button, Text, Scrollbar, messagebox
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from difflib import SequenceMatcher

# Constants
ERROR_MESSAGE_MAX_LENGTH = 500

# Ensure UTF-8 encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


def get_expected_schema() -> Dict[str, Set[str]]:
    """
    Obtient le schéma attendu en utilisant le schéma de référence du script update_db_structure.py.
    
    Returns:
        Dictionnaire {table_name: set(column_names)}
    """
    # Importer le schéma de référence depuis update_db_structure.py
    scripts_dir = Path(__file__).parent.parent / "scripts"
    script_path = scripts_dir / "update_db_structure.py"
    
    try:
        # Charger le module de manière dynamique
        spec = importlib.util.spec_from_file_location("update_db_structure", script_path)
        if spec is None or spec.loader is None:
            print(f"Warning: Could not load spec for {script_path}")
            return {}
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Accéder au REFERENCE_SCHEMA
        REFERENCE_SCHEMA = module.REFERENCE_SCHEMA
        
        # Convertir le format {table: {col: (type, default)}} en {table: set(cols)}
        expected = {}
        for table, columns in REFERENCE_SCHEMA.items():
            expected[table] = set(columns.keys())
        
        return expected
    except Exception as e:
        print(f"Warning: Could not import REFERENCE_SCHEMA: {e}")
        return {}


def get_real_schema(db_path: str) -> Dict[str, Set[str]]:
    """
    Obtient le schéma réel de la base de données via PRAGMA table_info.
    
    Args:
        db_path: Chemin vers le fichier de base de données
        
    Returns:
        Dictionnaire {table_name: set(column_names)}
    """
    if not os.path.exists(db_path):
        return {}
    
    schema = {}
    
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        # Obtenir toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Valider le nom de la table pour éviter l'injection SQL
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
                print(f"Warning: Skipping table with invalid name: {table}")
                continue
            
            # Obtenir les colonnes de chaque table via PRAGMA table_info
            # PRAGMA table_info n'accepte pas les paramètres, mais on a validé le nom
            cursor.execute(f"PRAGMA table_info({table})")
            columns = set(row[1] for row in cursor.fetchall())
            schema[table] = columns
        
        conn.close()
        return schema
        
    except Exception as e:
        print(f"Error reading database schema: {e}")
        return {}


def fuzzy_match_column(target_col: str, existing_cols: Set[str], threshold: float = 0.75) -> Optional[str]:
    """
    Trouve une colonne existante qui correspond au nom cible (fuzzy/case-insensitive).
    
    Args:
        target_col: Nom de colonne recherche
        existing_cols: Ensemble des colonnes existantes dans la table
        threshold: Seuil de similarite (0.0 a 1.0)
    
    Returns:
        Nom de la colonne correspondante ou None
    """
    target_lower = target_col.lower()
    
    # 1. Exact match (case-insensitive)
    for col in existing_cols:
        if col.lower() == target_lower:
            return col
    
    # 2. Fuzzy match with SequenceMatcher
    best_match = None
    best_score = 0.0
    
    for col in existing_cols:
        ratio = SequenceMatcher(None, target_lower, col.lower()).ratio()
        if ratio > best_score and ratio >= threshold:
            best_score = ratio
            best_match = col
    
    return best_match


def detect_missing_columns(expected: Dict[str, Set[str]], real: Dict[str, Set[str]]) -> Dict[str, List[Tuple[str, Optional[str]]]]:
    """
    Detecte les colonnes manquantes par rapport au schema attendu.
    
    Args:
        expected: Schema attendu {table: set(columns)}
        real: Schema reel {table: set(columns)}
        
    Returns:
        Dictionnaire {table: [(missing_col, fuzzy_match)]}
        where fuzzy_match is the suggested existing column or None
    """
    missing = {}
    
    for table, expected_cols in expected.items():
        if table not in real:
            # La table n'existe pas, ne pas la signaler
            # (update_db_structure ne cree pas de tables)
            continue
        
        real_cols = real[table]
        missing_cols = expected_cols - real_cols
        
        if missing_cols:
            # Find fuzzy matches for each missing column
            missing_with_matches = []
            for col in sorted(missing_cols):
                fuzzy_match = fuzzy_match_column(col, real_cols)
                missing_with_matches.append((col, fuzzy_match))
            
            missing[table] = missing_with_matches
    
    return missing


class SchemaCheckDialog(Toplevel):
    """Fenetre d'alerte pour les colonnes manquantes dans la base de donnees."""
    
    def __init__(self, parent, missing_columns: Dict[str, List[Tuple[str, Optional[str]]]], db_path: str):
        super().__init__(parent)
        
        self.missing_columns = missing_columns
        self.db_path = db_path
        self.user_choice = None  # 'update' ou 'ignore'
        
        self.title("Verification du schema de base de donnees")
        self.geometry("700x500")
        self.resizable(True, True)
        
        # Rendre la fenêtre modale
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Crée les widgets de la fenêtre."""
        
        # En-tête avec icône d'avertissement
        header_frame = tk.Frame(self, bg="#fff3cd", padx=10, pady=10)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        warning_label = Label(
            header_frame,
            text="⚠ Schéma de base de données incomplet",
            font=("Arial", 14, "bold"),
            bg="#fff3cd",
            fg="#856404"
        )
        warning_label.pack()
        
        # Message d'information
        info_text = (
            "Des colonnes attendues par le code sont absentes de la base de données.\n"
            "Cela peut causer des erreurs lors de l'utilisation de l'application.\n\n"
            "Colonnes manquantes par table :"
        )
        
        info_label = Label(self, text=info_text, justify="left", wraplength=650)
        info_label.pack(padx=10, pady=(0, 5), anchor="w")
        
        # Zone de texte avec scrollbar pour afficher les colonnes manquantes
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_widget = Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            height=12
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        # Remplir le texte avec les colonnes manquantes
        self._populate_missing_columns()
        self.text_widget.config(state=tk.DISABLED)
        
        # Message de recommandation
        recommendation_text = (
            "\n💡 Recommandation : Il est fortement conseillé de mettre à jour la base de données.\n"
            "Une sauvegarde automatique sera créée avant toute modification."
        )
        
        recommendation_label = Label(
            self,
            text=recommendation_text,
            justify="left",
            wraplength=650,
            fg="#0056b3"
        )
        recommendation_label.pack(padx=10, pady=10, anchor="w")
        
        # Cadre pour les boutons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=15)
        
        # Bouton "Mettre à jour maintenant"
        update_button = Button(
            button_frame,
            text="Mettre à jour maintenant",
            command=self._on_update,
            bg="#28a745",
            fg="white",
            font=("Arial", 11, "bold"),
            width=22,
            height=2
        )
        update_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Ignorer"
        ignore_button = Button(
            button_frame,
            text="Ignorer (non recommandé)",
            command=self._on_ignore,
            bg="#6c757d",
            fg="white",
            font=("Arial", 11),
            width=22,
            height=2
        )
        ignore_button.pack(side=tk.LEFT, padx=10)
        
        # Protocole de fermeture de la fenêtre
        self.protocol("WM_DELETE_WINDOW", self._on_ignore)
    
    def _populate_missing_columns(self):
        """Remplit le widget texte avec les colonnes manquantes."""
        for table in sorted(self.missing_columns.keys()):
            columns = self.missing_columns[table]
            self.text_widget.insert(tk.END, f"\nTable: {table}\n", "table")
            for col, fuzzy_match in columns:
                if fuzzy_match:
                    # Show proposed mapping
                    self.text_widget.insert(tk.END, f"   + {col}", "column")
                    self.text_widget.insert(tk.END, f" (mappable depuis: {fuzzy_match})\n", "match")
                else:
                    # New column
                    self.text_widget.insert(tk.END, f"   + {col}", "column")
                    self.text_widget.insert(tk.END, " (nouvelle colonne)\n", "new")
        
        # Configuration des tags pour le formatage
        self.text_widget.tag_config("table", font=("Courier", 10, "bold"), foreground="#0056b3")
        self.text_widget.tag_config("column", font=("Courier", 10, "bold"), foreground="#333333")
        self.text_widget.tag_config("match", font=("Courier", 9), foreground="#28a745")
        self.text_widget.tag_config("new", font=("Courier", 9), foreground="#6c757d")
    
    def _on_update(self):
        """Gestionnaire pour le bouton 'Mettre à jour maintenant'."""
        self.user_choice = "update"
        self.destroy()
    
    def _on_ignore(self):
        """Gestionnaire pour le bouton 'Ignorer'."""
        # Confirmer l'action d'ignorer
        confirm = messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir ignorer cette mise à jour ?\n\n"
            "Certaines fonctionnalités pourraient ne pas fonctionner correctement.",
            icon="warning",
            parent=self
        )
        
        if confirm:
            self.user_choice = "ignore"
            self.destroy()


def _extract_report_path_from_output(output: str) -> Optional[str]:
    """
    Extrait le chemin du rapport depuis la sortie du script de migration.
    
    Args:
        output: Sortie stdout du script
        
    Returns:
        Chemin du rapport ou None si non trouvé
    """
    for line in output.split('\n'):
        if line.startswith('REPORT_PATH:'):
            return line.split('REPORT_PATH:', 1)[1].strip()
    return None


def execute_update(db_path: str, parent_window=None) -> Tuple[bool, str]:
    """
    Exécute le script update_db_structure.py pour mettre à jour la base de données.
    
    Args:
        db_path: Chemin vers la base de données
        parent_window: Fenêtre parente pour les messages
        
    Returns:
        Tuple (success, message)
    """
    try:
        # Valider le chemin de la base de données pour éviter l'injection de commandes
        db_path = os.path.abspath(db_path)
        if not os.path.exists(db_path):
            error_msg = f"[ERROR] Le fichier de base de donnees n'existe pas : {db_path}"
            if parent_window:
                messagebox.showerror("Erreur", error_msg, parent=parent_window)
            return False, error_msg
        
        # Construire la commande pour exécuter le script
        script_path = Path(__file__).parent.parent / "scripts" / "update_db_structure.py"
        
        result = subprocess.run(
            [sys.executable, str(script_path), "--db-path", db_path],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=120  # Timeout de 2 minutes pour la migration
        )
        
        # Extraire le chemin du rapport depuis la sortie
        report_path = _extract_report_path_from_output(result.stdout)
        
        if result.returncode == 0:
            success_msg = (
                "[SUCCESS] Mise a jour de la base de donnees terminee avec succes !\n\n"
                "Un rapport detaille a ete genere dans le repertoire reports/.\n"
                "Une sauvegarde de votre base a ete creee automatiquement."
            )
            
            if parent_window:
                # Afficher le rapport dans une fenêtre dédiée
                if report_path and os.path.exists(report_path):
                    show_report = messagebox.askyesno(
                        "Succès",
                        success_msg + "\n\nVoulez-vous consulter le rapport de migration ?",
                        parent=parent_window
                    )
                    
                    if show_report:
                        MigrationReportDialog(parent_window, report_path, is_error=False)
                else:
                    messagebox.showinfo("Succès", success_msg, parent=parent_window)
            
            return True, success_msg
        else:
            error_msg = f"[ERROR] La mise a jour a echoue.\n\nDetails :\n{result.stderr[:ERROR_MESSAGE_MAX_LENGTH]}"
            
            if parent_window:
                # Afficher automatiquement le rapport d'erreur dans une fenêtre dédiée
                if report_path and os.path.exists(report_path):
                    MigrationReportDialog(parent_window, report_path, is_error=True)
                else:
                    # Si pas de rapport disponible, afficher l'erreur basique
                    messagebox.showerror("Erreur de migration", error_msg, parent=parent_window)
            
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "[ERROR] La mise a jour a depasse le delai d'attente."
        if parent_window:
            messagebox.showerror("Erreur", error_msg, parent=parent_window)
        return False, error_msg
    except Exception as e:
        error_msg = f"[ERROR] Impossible d'executer la mise a jour : {e}"
        
        if parent_window:
            messagebox.showerror("Erreur", error_msg, parent=parent_window)
        
        return False, error_msg


class MigrationReportDialog(Toplevel):
    """Fenêtre pour afficher le contenu d'un rapport de migration."""
    
    def __init__(self, parent, report_path: str, is_error: bool = False):
        super().__init__(parent)
        
        self.report_path = report_path
        
        title = "Rapport d'erreur de migration" if is_error else "Rapport de migration"
        self.title(title)
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Rendre la fenêtre modale
        if parent:
            self.transient(parent)
            self.grab_set()
        
        self._create_widgets(is_error)
        self._load_report_content()
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self, is_error: bool):
        """Crée les widgets de la fenêtre."""
        
        # En-tête
        header_color = "#f8d7da" if is_error else "#d4edda"
        text_color = "#721c24" if is_error else "#155724"
        icon = "❌" if is_error else "✅"
        
        header_frame = tk.Frame(self, bg=header_color, padx=10, pady=10)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_text = f"{icon} Rapport de migration de la base de données"
        header_label = Label(
            header_frame,
            text=title_text,
            font=("Arial", 12, "bold"),
            bg=header_color,
            fg=text_color
        )
        header_label.pack()
        
        # Message
        if is_error:
            info_text = (
                "La migration de la base de données a échoué.\n"
                "Veuillez consulter les détails ci-dessous pour comprendre la cause du problème.\n"
                "La base de données a été restaurée à son état précédent."
            )
        else:
            info_text = (
                "La migration de la base de données s'est terminée avec succès.\n"
                "Vous pouvez consulter les détails ci-dessous."
            )
        
        info_label = Label(self, text=info_text, justify="left", wraplength=750)
        info_label.pack(padx=10, pady=(0, 10), anchor="w")
        
        # Zone de texte avec scrollbar pour afficher le rapport
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            state=tk.DISABLED
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        # Cadre pour les boutons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=15)
        
        # Bouton "Ouvrir le fichier"
        open_button = Button(
            button_frame,
            text="Ouvrir le fichier complet",
            command=self._open_file,
            font=("Arial", 10),
            width=20
        )
        open_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton "Fermer"
        close_button = Button(
            button_frame,
            text="Fermer",
            command=self.destroy,
            font=("Arial", 10),
            width=15
        )
        close_button.pack(side=tk.LEFT, padx=5)
    
    def _load_report_content(self):
        """Charge et affiche le contenu du rapport."""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, content)
            self.text_widget.config(state=tk.DISABLED)
        except Exception as e:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, f"Erreur lors de la lecture du rapport :\n{e}")
            self.text_widget.config(state=tk.DISABLED)
    
    def _open_file(self):
        """Ouvre le fichier de rapport avec l'application par défaut."""
        try:
            if sys.platform == "win32":
                os.startfile(self.report_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.report_path], check=False, timeout=5)
            else:
                subprocess.run(["xdg-open", self.report_path], check=False, timeout=5)
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible d'ouvrir le fichier :\n{e}\n\nChemin : {self.report_path}",
                parent=self
            )


def _open_latest_migration_report():
    """Ouvre le dernier rapport de migration généré."""
    try:
        reports_dir = Path(__file__).parent.parent / "reports"
        
        # Trouver le dernier rapport de migration
        reports = list(reports_dir.glob("migration_report_*.md"))
        
        if reports:
            latest_report = max(reports, key=os.path.getmtime)
            
            # Valider que le fichier existe et est bien dans le répertoire reports
            if not latest_report.exists() or not latest_report.is_relative_to(reports_dir):
                print(f"Invalid report path: {latest_report}")
                return
            
            # Ouvrir le fichier avec l'application par défaut du système
            try:
                if sys.platform == "win32":
                    os.startfile(str(latest_report))
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(latest_report)], check=False, timeout=5)
                else:
                    subprocess.run(["xdg-open", str(latest_report)], check=False, timeout=5)
            except (subprocess.TimeoutExpired, OSError) as e:
                print(f"Could not open report with default application: {e}")
                messagebox.showinfo("Rapport", f"Le rapport est disponible ici :\n{latest_report}")
        else:
            messagebox.showwarning("Rapport introuvable", "Aucun rapport de migration trouvé.")
            
    except Exception as e:
        print(f"Could not open migration report: {e}")


def run_check(parent_window=None, db_path: str = "association.db") -> bool:
    """
    Exécute la vérification du schéma de base de données au démarrage.
    
    Cette fonction compare le schéma attendu avec le schéma réel et affiche
    une fenêtre d'alerte si des colonnes manquent. L'utilisateur peut choisir
    de mettre à jour la base de données ou d'ignorer les différences.
    
    Args:
        parent_window: Fenêtre parente Tkinter (optionnel)
        db_path: Chemin vers la base de données (défaut: "association.db")
        
    Returns:
        True si la vérification s'est bien passée (pas de colonnes manquantes ou mise à jour réussie),
        False sinon
    """
    # Vérifier que la base de données existe
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return True  # Pas d'erreur, la base n'existe pas encore
    
    # Obtenir les schémas
    expected_schema = get_expected_schema()
    real_schema = get_real_schema(db_path)
    
    if not expected_schema:
        print("Warning: Could not load expected schema")
        return True  # Continuer sans vérification
    
    # Détecter les colonnes manquantes
    missing_columns = detect_missing_columns(expected_schema, real_schema)
    
    if not missing_columns:
        # Tout est à jour, pas besoin d'afficher de fenêtre
        print("[OK] Database schema is up to date!")
        return True
    
    # Afficher la fenêtre d'alerte
    print(f"Warning: Found missing columns in {len(missing_columns)} table(s)")
    
    dialog = SchemaCheckDialog(parent_window, missing_columns, db_path)
    dialog.wait_window()
    
    # Traiter le choix de l'utilisateur
    if dialog.user_choice == "update":
        success, message = execute_update(db_path, parent_window)
        return success
    else:
        # L'utilisateur a choisi d'ignorer
        print("User chose to ignore schema differences")
        return False


if __name__ == "__main__":
    # Test en mode standalone
    print("Testing startup schema check...")
    
    # Créer une fenêtre Tk simple pour le test
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    
    result = run_check(root)
    
    print(f"Check result: {result}")
    
    root.destroy()
