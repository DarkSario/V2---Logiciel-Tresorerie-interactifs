#!/usr/bin/env python3
"""
Script de mise à jour sûre de la structure de base de données.

Ce script compare le schéma attendu (extrait du code ou du rapport d'analyse)
avec le schéma réel de la base de données et effectue des migrations sûres
pour ajouter les colonnes manquantes.

Fonctionnalités:
- Détection automatique des colonnes manquantes
- Sauvegarde timestampée avant toute modification
- Transactions avec rollback en cas d'erreur
- Restauration automatique de la sauvegarde si échec
- Activation WAL mode et optimisation des pragmas
- Rapport détaillé de migration

Usage:
    python scripts/update_db_structure.py [--db-path path/to/database.db]
"""

import sqlite3
import os
import sys
import shutil
import argparse
import traceback
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import yaml
from difflib import SequenceMatcher

# Force UTF-8 encoding for stdout/stderr on Windows to avoid encoding errors
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


# Schéma de référence basé sur l'analyse du code et init_db.py
# Format: {table_name: {column_name: (type, default_value)}}
REFERENCE_SCHEMA = {
    "config": {
        "id": ("INTEGER", None),
        "exercice": ("TEXT", "''"),
        "date": ("TEXT", "''"),
        "but_asso": ("TEXT", "''"),
        "cloture": ("INTEGER", "0"),
        "solde_report": ("REAL", "0.0"),
        "disponible_banque": ("REAL", "0.0"),
    },
    "comptes": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "solde": ("REAL", "0.0"),
    },
    "membres": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "prenom": ("TEXT", "''"),
        "email": ("TEXT", "''"),
        "classe": ("TEXT", "''"),
        "cotisation": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
        "telephone": ("TEXT", "''"),
        "statut": ("TEXT", "''"),
        "date_adhesion": ("TEXT", "''"),
    },
    "events": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "date": ("TEXT", "''"),
        "lieu": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
        "description": ("TEXT", "''"),
    },
    "event_modules": {
        "id": ("INTEGER", None),
        "event_id": ("INTEGER", "0"),
        "nom_module": ("TEXT", "''"),
        "id_col_total": ("INTEGER", None),
    },
    "event_module_fields": {
        "id": ("INTEGER", None),
        "module_id": ("INTEGER", "0"),
        "nom_champ": ("TEXT", "''"),
        "type_champ": ("TEXT", "''"),
        "prix_unitaire": ("REAL", None),
        "modele_colonne": ("TEXT", None),
    },
    "event_module_data": {
        "module_id": ("INTEGER", "0"),
        "row_index": ("INTEGER", "0"),
        "field_id": ("INTEGER", "0"),
        "valeur": ("TEXT", "''"),
    },
    "event_payments": {
        "id": ("INTEGER", None),
        "event_id": ("INTEGER", "0"),
        "montant": ("REAL", "0.0"),
        "date": ("TEXT", "''"),
        "type": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "event_caisses": {
        "id": ("INTEGER", None),
        "event_id": ("INTEGER", "0"),
        "nom_caisse": ("TEXT", "''"),
        "montant_initial": ("REAL", "0.0"),
        "montant_final": ("REAL", "0.0"),
    },
    "event_caisse_details": {
        "id": ("INTEGER", None),
        "caisse_id": ("INTEGER", "0"),
        "type": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "description": ("TEXT", "''"),
    },
    "event_recettes": {
        "id": ("INTEGER", None),
        "event_id": ("INTEGER", "0"),
        "libelle": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "categorie": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "event_depenses": {
        "id": ("INTEGER", None),
        "event_id": ("INTEGER", "0"),
        "libelle": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "categorie": ("TEXT", "''"),
        "fournisseur": ("TEXT", "''"),
        "date_depense": ("TEXT", "''"),
        "paye_par": ("TEXT", "''"),
        "membre_id": ("INTEGER", None),
        "statut_remboursement": ("TEXT", "''"),
        "statut_reglement": ("TEXT", "''"),
        "moyen_paiement": ("TEXT", "''"),
        "numero_cheque": ("TEXT", "''"),
        "numero_facture": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
        "module_id": ("INTEGER", None),
    },
    "dons_subventions": {
        "id": ("INTEGER", None),
        "donateur": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "date": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "depenses_regulieres": {
        "id": ("INTEGER", None),
        "libelle": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "date": ("TEXT", "''"),
        "categorie": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
        "fournisseur": ("TEXT", "''"),
        "date_depense": ("TEXT", "''"),
        "paye_par": ("TEXT", "''"),
        "membre_id": ("INTEGER", None),
        "statut_remboursement": ("TEXT", "''"),
        "statut_reglement": ("TEXT", "''"),
        "moyen_paiement": ("TEXT", "''"),
        "numero_cheque": ("TEXT", "''"),
        "numero_facture": ("TEXT", "''"),
        "module_id": ("INTEGER", None),
    },
    "depenses_diverses": {
        "id": ("INTEGER", None),
        "libelle": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "date": ("TEXT", "''"),
        "categorie": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
        "fournisseur": ("TEXT", "''"),
        "date_depense": ("TEXT", "''"),
        "paye_par": ("TEXT", "''"),
        "membre_id": ("INTEGER", None),
        "statut_remboursement": ("TEXT", "''"),
        "statut_reglement": ("TEXT", "''"),
        "moyen_paiement": ("TEXT", "''"),
        "numero_cheque": ("TEXT", "''"),
        "numero_facture": ("TEXT", "''"),
        "module_id": ("INTEGER", None),
    },
    "categories": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "parent_id": ("INTEGER", None),
    },
    "stock": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "categorie_id": ("INTEGER", None),
        "quantite": ("INTEGER", "0"),
        "seuil_alerte": ("INTEGER", "0"),
        "date_peremption": ("TEXT", "''"),
        "lot": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "inventaires": {
        "id": ("INTEGER", None),
        "date": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "inventaire_lignes": {
        "id": ("INTEGER", None),
        "inventaire_id": ("INTEGER", "0"),
        "stock_id": ("INTEGER", "0"),
        "quantite": ("INTEGER", "0"),
        "ecart": ("INTEGER", "0"),
    },
    "mouvements_stock": {
        "id": ("INTEGER", None),
        "stock_id": ("INTEGER", "0"),
        "date": ("TEXT", "''"),
        "type": ("TEXT", "''"),
        "quantite": ("INTEGER", "0"),
        "commentaire": ("TEXT", "''"),
    },
    "fournisseurs": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
    },
    "colonnes_modeles": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "type_modele": ("TEXT", "''"),
    },
    "valeurs_modeles_colonnes": {
        "id": ("INTEGER", None),
        "modele_id": ("INTEGER", "0"),
        "valeur": ("TEXT", "''"),
    },
    "depots_retraits_banque": {
        "id": ("INTEGER", None),
        "date": ("TEXT", "''"),
        "type": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "reference": ("TEXT", "''"),
        "banque": ("TEXT", "''"),
        "pointe": ("INTEGER", "0"),
        "commentaire": ("TEXT", "''"),
    },
    "historique_clotures": {
        "id": ("INTEGER", None),
        "date_cloture": ("TEXT", "''"),
    },
    "retrocessions_ecoles": {
        "id": ("INTEGER", None),
        "date": ("TEXT", "''"),
        "montant": ("REAL", "0.0"),
        "ecole": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "buvette_articles": {
        "id": ("INTEGER", None),
        "name": ("TEXT", "''"),
        "categorie": ("TEXT", "''"),
        "unite": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
        "contenance": ("REAL", None),
        "stock": ("INTEGER", "0"),
        "purchase_price": ("REAL", None),
    },
    "buvette_achats": {
        "id": ("INTEGER", None),
        "article_id": ("INTEGER", "0"),
        "date_achat": ("TEXT", "''"),
        "quantite": ("REAL", "0.0"),
        "prix_unitaire": ("REAL", "0.0"),
        "fournisseur": ("TEXT", "''"),
        "facture": ("TEXT", "''"),
        "exercice": ("TEXT", "''"),
    },
    "buvette_inventaires": {
        "id": ("INTEGER", None),
        "date_inventaire": ("TEXT", "''"),
        "event_id": ("INTEGER", None),
        "type_inventaire": ("TEXT", "''"),
        "commentaire": ("TEXT", "''"),
    },
    "buvette_inventaire_lignes": {
        "id": ("INTEGER", None),
        "inventaire_id": ("INTEGER", "0"),
        "article_id": ("INTEGER", "0"),
        "quantite": ("REAL", "0.0"),
        "commentaire": ("TEXT", "''"),
    },
    "buvette_mouvements": {
        "id": ("INTEGER", None),
        "date_mouvement": ("TEXT", "''"),
        "article_id": ("INTEGER", "0"),
        "type_mouvement": ("TEXT", "''"),
        "quantite": ("REAL", "0.0"),
        "motif": ("TEXT", "''"),
        "event_id": ("INTEGER", None),
    },
    "buvette_recettes": {
        "id": ("INTEGER", None),
        "event_id": ("INTEGER", "0"),
        "montant": ("REAL", "0.0"),
        "date": ("TEXT", "''"),
    },
}


class DatabaseMigrator:
    """Gestionnaire de migration de base de données."""
    
    # SQL reserved words that need quoting (subset of most common ones)
    SQL_RESERVED_WORDS = {
        'add', 'all', 'alter', 'and', 'as', 'asc', 'between', 'by', 'case', 'check',
        'column', 'constraint', 'create', 'cross', 'default', 'delete', 'desc',
        'distinct', 'drop', 'else', 'end', 'exists', 'foreign', 'from', 'full',
        'group', 'having', 'in', 'index', 'inner', 'insert', 'into', 'is', 'join',
        'key', 'left', 'like', 'limit', 'not', 'null', 'on', 'or', 'order', 'outer',
        'primary', 'references', 'right', 'select', 'set', 'table', 'then', 'to',
        'union', 'unique', 'update', 'values', 'when', 'where'
    }
    
    def __init__(self, db_path: str, use_yaml_hints: bool = True, fuzzy_threshold: float = 0.75):
        self.db_path = db_path
        self.backup_path = None
        self.migration_log = []
        self.errors = []
        self.report_path = None
        self.use_yaml_hints = use_yaml_hints
        self.schema_hints = None
        self.column_mappings = {}  # Track old_name -> new_name mappings
        self.fuzzy_threshold = fuzzy_threshold  # Configurable fuzzy matching threshold
    
    def log(self, message: str, level: str = "INFO"):
        """Ajoute un message au log de migration."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def load_schema_hints(self, yaml_path: Optional[str] = None) -> bool:
        """Charge le fichier schema_hints.yaml ou le génère s'il n'existe pas."""
        if yaml_path is None:
            repo_root = Path(__file__).parent.parent
            yaml_path = repo_root / "db" / "schema_hints.yaml"
        else:
            yaml_path = Path(yaml_path)
        
        if not yaml_path.exists():
            self.log(f"Schema hints file not found at {yaml_path}", "WARNING")
            self.log("Attempting to generate schema hints by running analyze_modules_columns.py...")
            
            try:
                # Run the analyze script to generate the YAML
                script_path = Path(__file__).parent / "analyze_modules_columns.py"
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    self.log(f"Failed to generate schema hints: {result.stderr}", "ERROR")
                    return False
                
                self.log("Schema hints generated successfully")
            except Exception as e:
                self.log(f"Error generating schema hints: {e}", "ERROR")
                return False
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.schema_hints = yaml.safe_load(f)
            
            self.log(f"Loaded schema hints from {yaml_path}")
            return True
        except Exception as e:
            self.log(f"Error loading schema hints: {e}", "WARNING")
            return False
    
    def fuzzy_match_column(self, target_col: str, existing_cols: Set[str], threshold: Optional[float] = None) -> Optional[str]:
        """
        Trouve une colonne existante qui correspond au nom cible (fuzzy/case-insensitive).
        
        Args:
            target_col: Nom de colonne recherché
            existing_cols: Ensemble des colonnes existantes dans la table
            threshold: Seuil de similarité (0.0 à 1.0), uses instance default if None
        
        Returns:
            Nom de la colonne correspondante ou None
        """
        if threshold is None:
            threshold = self.fuzzy_threshold
        
        target_lower = target_col.lower()
        
        # 1. Exact match (case-insensitive)
        for col in existing_cols:
            if col.lower() == target_lower:
                return col
        
        # 2. Fuzzy match with SequenceMatcher
        best_match = None
        best_score = 0.0
        
        for col in existing_cols:
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, target_lower, col.lower()).ratio()
            
            if ratio > best_score and ratio >= threshold:
                best_score = ratio
                best_match = col
        
        return best_match
    
    def quote_identifier(self, identifier: str) -> str:
        """
        Quote SQL identifier if it's a reserved word or contains special characters.
        
        Args:
            identifier: Column or table name
            
        Returns:
            Quoted identifier if needed, otherwise original
        """
        # Quote if it's a reserved word
        if identifier.lower() in self.SQL_RESERVED_WORDS:
            return f'"{identifier}"'
        
        # Quote if it contains special characters
        if not identifier.replace('_', '').isalnum():
            return f'"{identifier}"'
        
        return identifier
    
    def get_column_type_from_hints(self, table: str, column: str) -> Optional[str]:
        """Récupère le type d'une colonne depuis les hints YAML."""
        if not self.schema_hints or "tables" not in self.schema_hints:
            return None
        
        if table not in self.schema_hints["tables"]:
            return None
        
        table_info = self.schema_hints["tables"][table]
        if "expected_columns" not in table_info:
            return None
        
        if column not in table_info["expected_columns"]:
            return None
        
        return table_info["expected_columns"][column].get("type", "TEXT")
    
    def create_backup(self) -> bool:
        """Crée une sauvegarde timestampée de la base de données."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_path = f"{self.db_path}.{timestamp}.bak"
            
            self.log(f"Creating backup: {self.backup_path}")
            shutil.copy2(self.db_path, self.backup_path)
            self.log(f"Backup created successfully: {self.backup_path}")
            return True
        except Exception as e:
            self.log(f"Failed to create backup: {e}", "ERROR")
            self.errors.append(f"Backup error: {e}")
            return False
    
    def restore_backup(self) -> bool:
        """Restaure la base de données depuis la sauvegarde."""
        if not self.backup_path or not os.path.exists(self.backup_path):
            self.log("No backup available to restore", "ERROR")
            return False
        
        try:
            self.log(f"Restoring from backup: {self.backup_path}")
            shutil.copy2(self.backup_path, self.db_path)
            self.log("Database restored successfully")
            return True
        except Exception as e:
            self.log(f"Failed to restore backup: {e}", "ERROR")
            self.errors.append(f"Restore error: {e}")
            return False
    
    def get_existing_schema(self, conn: sqlite3.Connection) -> Dict[str, Set[str]]:
        """Récupère le schéma actuel de la base de données."""
        schema = {}
        
        cursor = conn.cursor()
        
        # Obtenir toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Obtenir les colonnes de chaque table
            cursor.execute(f"PRAGMA table_info({table})")
            columns = set(row[1] for row in cursor.fetchall())
            schema[table] = columns
        
        return schema
    
    def check_rename_column_support(self, conn: sqlite3.Connection) -> bool:
        """Vérifie si SQLite supporte ALTER TABLE RENAME COLUMN (version 3.25.0+)."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            
            # Parse version (e.g., "3.35.5")
            major, minor, patch = map(int, version.split('.'))
            
            # RENAME COLUMN supported since 3.25.0
            supports_rename = (major > 3) or (major == 3 and minor >= 25)
            
            self.log(f"SQLite version: {version}, RENAME COLUMN support: {supports_rename}")
            return supports_rename
        except Exception as e:
            self.log(f"Could not determine SQLite version: {e}", "WARNING")
            return False
    
    def detect_missing_columns(self, existing_schema: Dict[str, Set[str]]) -> Dict[str, List[Tuple[str, str, str, Optional[str]]]]:
        """
        Détecte les colonnes manquantes par rapport au schéma de référence.
        
        Returns:
            Dict mapping table -> List of (col_name, col_type, default_value, fuzzy_match)
            where fuzzy_match is the name of an existing column that closely matches, or None
        """
        missing = {}
        
        # Combine REFERENCE_SCHEMA and YAML hints
        expected_schema = {}
        
        # Start with REFERENCE_SCHEMA
        for table, columns in REFERENCE_SCHEMA.items():
            expected_schema[table] = {}
            for col_name, (col_type, default_value) in columns.items():
                expected_schema[table][col_name] = (col_type, default_value)
        
        # Add columns from YAML hints if available
        if self.schema_hints and "tables" in self.schema_hints:
            for table, table_info in self.schema_hints["tables"].items():
                if "expected_columns" not in table_info:
                    continue
                
                if table not in expected_schema:
                    expected_schema[table] = {}
                
                for col_name, col_info in table_info["expected_columns"].items():
                    if col_name not in expected_schema[table]:
                        col_type = col_info.get("type", "TEXT")
                        # Infer default based on type
                        if col_type == "INTEGER":
                            default_value = "0"
                        elif col_type == "REAL":
                            default_value = "0.0"
                        else:
                            default_value = "''"
                        
                        expected_schema[table][col_name] = (col_type, default_value)
        
        # Now check for missing columns
        for table, expected_columns in expected_schema.items():
            if table not in existing_schema:
                self.log(f"Table '{table}' does not exist (will not be created automatically)", "WARNING")
                continue
            
            existing_cols = existing_schema[table]
            table_missing = []
            
            for col_name, (col_type, default_value) in expected_columns.items():
                if col_name not in existing_cols:
                    # Try fuzzy matching to find a similar column
                    fuzzy_match = self.fuzzy_match_column(col_name, existing_cols, threshold=0.75)
                    
                    if fuzzy_match:
                        self.log(f"Column '{col_name}' not found in '{table}', but found similar column '{fuzzy_match}'", "INFO")
                    
                    table_missing.append((col_name, col_type, default_value, fuzzy_match))
            
            if table_missing:
                missing[table] = table_missing
        
        return missing
    
    def apply_migrations(self, conn: sqlite3.Connection, missing_columns: Dict[str, List[Tuple[str, str, str, Optional[str]]]]) -> bool:
        """Applique les migrations pour ajouter les colonnes manquantes."""
        if not missing_columns:
            self.log("No missing columns detected. Database is up to date.")
            return True
        
        self.log(f"Found missing columns in {len(missing_columns)} table(s)")
        
        # Check if RENAME COLUMN is supported
        supports_rename = self.check_rename_column_support(conn)
        
        try:
            cursor = conn.cursor()
            
            # SQLite ne supporte pas toujours les transactions pour ALTER TABLE,
            # mais on utilise BEGIN pour grouper les opérations
            cursor.execute("BEGIN TRANSACTION")
            
            for table, columns in missing_columns.items():
                self.log(f"Processing table '{table}': {len(columns)} column(s) to add")
                
                for col_name, col_type, default_value, fuzzy_match in columns:
                    # Case 1: Fuzzy match found - try to rename or copy
                    if fuzzy_match:
                        self.log(f"  Column '{col_name}' has fuzzy match '{fuzzy_match}'")
                        
                        if supports_rename and fuzzy_match.lower() != col_name.lower():
                            # Try to rename the column
                            rename_sql = f"ALTER TABLE {table} RENAME COLUMN {fuzzy_match} TO {col_name}"
                            
                            try:
                                self.log(f"  Attempting to rename '{fuzzy_match}' to '{col_name}'...")
                                cursor.execute(rename_sql)
                                self.log(f"  [OK] Successfully renamed column '{fuzzy_match}' to '{col_name}'")
                                self.column_mappings[f"{table}.{fuzzy_match}"] = f"{table}.{col_name}"
                                continue
                            except sqlite3.OperationalError as e:
                                self.log(f"  [WARNING] RENAME failed: {e}. Will try ADD + COPY instead.", "WARNING")
                        
                        # If rename not supported or failed, do ADD + COPY
                        quoted_col = self.quote_identifier(col_name)
                        
                        if default_value is None:
                            alter_sql = f"ALTER TABLE {table} ADD COLUMN {quoted_col} {col_type}"
                        else:
                            alter_sql = f"ALTER TABLE {table} ADD COLUMN {quoted_col} {col_type} DEFAULT {default_value}"
                        
                        try:
                            self.log(f"  Adding new column '{col_name}' ({col_type})")
                            cursor.execute(alter_sql)
                            
                            # Copy data from fuzzy_match column to new column
                            # Quote identifiers in case they're reserved words
                            quoted_new = self.quote_identifier(col_name)
                            quoted_old = self.quote_identifier(fuzzy_match)
                            copy_sql = f"UPDATE {table} SET {quoted_new} = {quoted_old}"
                            self.log(f"  Copying data from '{fuzzy_match}' to '{col_name}'...")
                            cursor.execute(copy_sql)
                            
                            self.log(f"  [OK] Added column '{col_name}' and copied data from '{fuzzy_match}'")
                            self.column_mappings[f"{table}.{fuzzy_match}"] = f"{table}.{col_name} (copied)"
                            
                        except sqlite3.OperationalError as e:
                            error_msg = str(e).lower()
                            if "duplicate" in error_msg and "column" in error_msg:
                                self.log(f"  [WARNING] Column '{col_name}' already exists", "WARNING")
                            else:
                                raise
                    
                    # Case 2: No fuzzy match - just add the column
                    else:
                        # Quote column name if it's a reserved word
                        quoted_col = self.quote_identifier(col_name)
                        
                        if default_value is None:
                            alter_sql = f"ALTER TABLE {table} ADD COLUMN {quoted_col} {col_type}"
                        else:
                            alter_sql = f"ALTER TABLE {table} ADD COLUMN {quoted_col} {col_type} DEFAULT {default_value}"
                        
                        try:
                            self.log(f"  Adding column: {col_name} ({col_type})")
                            cursor.execute(alter_sql)
                            self.log(f"  [OK] Successfully added column '{col_name}' to table '{table}'")
                        except sqlite3.OperationalError as e:
                            error_msg = str(e).lower()
                            if "duplicate" in error_msg and "column" in error_msg:
                                self.log(f"  [WARNING] Column '{col_name}' already exists in table '{table}'", "WARNING")
                            else:
                                raise
            
            # Commit toutes les modifications
            conn.commit()
            self.log("All migrations applied successfully")
            return True
            
        except Exception as e:
            self.log(f"Migration failed: {e}", "ERROR")
            self.errors.append(f"Migration error: {e}")
            
            try:
                conn.rollback()
                self.log("Transaction rolled back")
            except Exception as rb_error:
                self.log(f"Rollback failed: {rb_error}", "ERROR")
            
            return False
    
    def optimize_database(self, conn: sqlite3.Connection):
        """Optimise la base de données (WAL mode, pragmas)."""
        try:
            cursor = conn.cursor()
            
            # Activer le mode WAL (Write-Ahead Logging)
            self.log("Enabling WAL mode...")
            try:
                cursor.execute("PRAGMA journal_mode=WAL")
                result = cursor.fetchone()
                self.log(f"Journal mode set to: {result[0]}")
            except Exception as e:
                self.log(f"Could not enable WAL mode: {e}", "WARNING")
            
            # Définir synchronous à NORMAL pour de meilleures performances
            self.log("Setting synchronous mode to NORMAL...")
            try:
                cursor.execute("PRAGMA synchronous=NORMAL")
                self.log("Synchronous mode set to NORMAL")
            except Exception as e:
                self.log(f"Could not set synchronous mode: {e}", "WARNING")
            
            # Analyser la base de données pour optimiser les requêtes
            self.log("Running ANALYZE...")
            try:
                cursor.execute("ANALYZE")
                self.log("Database analysis complete")
            except Exception as e:
                self.log(f"Could not analyze database: {e}", "WARNING")
            
        except Exception as e:
            self.log(f"Database optimization warning: {e}", "WARNING")
    
    def generate_report(self, output_file: str, missing_columns: Dict[str, List[Tuple[str, str, str, Optional[str]]]], success: bool):
        """Génère un rapport détaillé de la migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Créer le répertoire reports s'il n'existe pas
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Database Migration Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Database:** {self.db_path}\n")
            f.write(f"**Status:** {'SUCCESS' if success else 'FAILED'}\n")
            
            if self.backup_path:
                f.write(f"**Backup:** {self.backup_path}\n")
            
            f.write("\n## Summary\n\n")
            
            if not missing_columns:
                f.write("No missing columns detected. Database schema is up to date.\n")
            else:
                total_columns = sum(len(cols) for cols in missing_columns.values())
                f.write(f"- Tables requiring updates: {len(missing_columns)}\n")
                f.write(f"- Total columns to add: {total_columns}\n")
                
                if success:
                    f.write("\n[OK] All columns were successfully added.\n")
                else:
                    f.write("\n[FAILED] Migration failed. Changes have been rolled back.\n")
                
                f.write("\n## Changes Applied\n\n")
                for table, columns in missing_columns.items():
                    f.write(f"### Table: `{table}`\n\n")
                    for col_name, col_type, default_value, fuzzy_match in columns:
                        default_str = f" DEFAULT {default_value}" if default_value else ""
                        status_icon = "[OK]" if success else "[FAILED]"
                        
                        if fuzzy_match:
                            mapping_key = f"{table}.{fuzzy_match}"
                            if mapping_key in self.column_mappings:
                                mapping_action = self.column_mappings[mapping_key]
                                f.write(f"- {status_icon} Column: `{col_name}` ({col_type}{default_str}) - Mapped from `{fuzzy_match}` ({mapping_action})\n")
                            else:
                                f.write(f"- {status_icon} Column: `{col_name}` ({col_type}{default_str}) - Fuzzy match: `{fuzzy_match}`\n")
                        else:
                            f.write(f"- {status_icon} Column: `{col_name}` ({col_type}{default_str})\n")
                    f.write("\n")
                
                # Add column mapping summary if any mappings were made
                if self.column_mappings:
                    f.write("\n## Column Mappings\n\n")
                    f.write("The following columns were renamed or had their data copied:\n\n")
                    for old_ref, new_ref in self.column_mappings.items():
                        f.write(f"- `{old_ref}` → `{new_ref}`\n")
                    f.write("\n")
            
            if self.errors:
                f.write("\n## Errors\n\n")
                for error in self.errors:
                    f.write(f"- [ERROR] {error}\n")
                
                f.write("\n### Recovery Actions\n\n")
                if self.backup_path and os.path.exists(self.backup_path):
                    f.write(f"[OK] Database was restored from backup: {self.backup_path}\n")
                else:
                    f.write("[WARNING] No backup was available for restore.\n")
            
            f.write("\n## Migration Log\n\n")
            f.write("```\n")
            for log_entry in self.migration_log:
                f.write(f"{log_entry}\n")
            f.write("```\n")
            
            if not success:
                f.write("\n## Recommended Actions\n\n")
                f.write("1. Review the errors listed above\n")
                f.write("2. Check database file permissions\n")
                f.write("3. Ensure no other processes are accessing the database\n")
                f.write("4. If the issue persists, please report it with this file\n")
        
        self.log(f"Report generated: {output_file}")
    
    def run_migration(self) -> bool:
        """Exécute le processus complet de migration."""
        self.log("=" * 60)
        self.log("Database Structure Update - Smart Migration with Fuzzy Matching")
        self.log("=" * 60)
        self.log(f"Database: {self.db_path}")
        
        if not os.path.exists(self.db_path):
            self.log(f"Database file not found: {self.db_path}", "ERROR")
            return False
        
        # Étape 0: Charger les schema hints si activé
        if self.use_yaml_hints:
            self.load_schema_hints()
        
        # Étape 1: Créer une sauvegarde
        if not self.create_backup():
            self.log("Migration aborted: could not create backup", "ERROR")
            return False
        
        success = False
        missing_columns = {}
        
        try:
            # Étape 2: Analyser le schéma existant
            self.log("Analyzing current database schema...")
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            
            existing_schema = self.get_existing_schema(conn)
            self.log(f"Found {len(existing_schema)} tables in database")
            
            # Étape 3: Détecter les colonnes manquantes
            self.log("Detecting missing columns...")
            missing_columns = self.detect_missing_columns(existing_schema)
            
            if not missing_columns:
                self.log("[SUCCESS] Database schema is up to date!")
                success = True
            else:
                # Étape 4: Appliquer les migrations
                self.log("Applying migrations...")
                success = self.apply_migrations(conn, missing_columns)
                
                if success:
                    self.log("[SUCCESS] Migrations completed successfully!")
                    
                    # Étape 5: Optimiser la base de données
                    self.log("Optimizing database...")
                    self.optimize_database(conn)
                else:
                    self.log("[FAILED] Migration failed, restoring backup...", "ERROR")
                    conn.close()
                    self.restore_backup()
            
            conn.close()
            
        except Exception as e:
            error_trace = traceback.format_exc()
            self.log(f"Unexpected error during migration: {e}", "ERROR")
            self.errors.append(f"Unexpected error: {e}\n{error_trace}")
            
            # Restaurer la sauvegarde en cas d'erreur
            self.log("Restoring backup due to error...", "ERROR")
            self.restore_backup()
            success = False
        
        # Générer le rapport dans le répertoire reports/
        report_dir = Path(__file__).parent.parent / "reports"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status_suffix = "success" if success else "failed"
        report_file = report_dir / f"migration_report_{status_suffix}_{timestamp}.md"
        self.report_path = str(report_file)
        self.generate_report(self.report_path, missing_columns, success)
        
        self.log("=" * 60)
        if success:
            self.log("Migration completed successfully!")
        else:
            self.log("Migration failed. Check the report for details.", "ERROR")
        self.log("=" * 60)
        
        return success


def get_latest_migration_report(reports_dir: Optional[str] = None) -> Optional[str]:
    """
    Récupère le chemin du dernier rapport de migration généré.
    
    Args:
        reports_dir: Répertoire des rapports (défaut: reports/ à la racine du projet)
        
    Returns:
        Chemin du dernier rapport ou None si aucun rapport trouvé
    """
    if reports_dir is None:
        reports_dir = Path(__file__).parent.parent / "reports"
    else:
        reports_dir = Path(reports_dir)
    
    if not reports_dir.exists():
        return None
    
    # Trouver tous les rapports de migration
    reports = list(reports_dir.glob("migration_report_*.md"))
    
    if not reports:
        return None
    
    # Retourner le plus récent
    latest_report = max(reports, key=lambda p: p.stat().st_mtime)
    return str(latest_report)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Smart database structure migration tool with fuzzy column matching")
    parser.add_argument(
        "--db-path",
        default="association.db",
        help="Path to the database file (default: association.db)"
    )
    parser.add_argument(
        "--no-yaml-hints",
        action="store_true",
        help="Disable loading schema hints from YAML (use only REFERENCE_SCHEMA)"
    )
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.db_path, use_yaml_hints=not args.no_yaml_hints)
    success = migrator.run_migration()
    
    # Afficher le chemin du rapport pour que l'appelant puisse le récupérer
    if migrator.report_path:
        print(f"\nREPORT_PATH:{migrator.report_path}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
