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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set


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
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_path = None
        self.migration_log = []
        self.errors = []
    
    def log(self, message: str, level: str = "INFO"):
        """Ajoute un message au log de migration."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
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
    
    def detect_missing_columns(self, existing_schema: Dict[str, Set[str]]) -> Dict[str, List[Tuple[str, str, str]]]:
        """Détecte les colonnes manquantes par rapport au schéma de référence."""
        missing = {}
        
        for table, expected_columns in REFERENCE_SCHEMA.items():
            if table not in existing_schema:
                self.log(f"Table '{table}' does not exist (will not be created automatically)", "WARNING")
                continue
            
            existing_cols = existing_schema[table]
            table_missing = []
            
            for col_name, (col_type, default_value) in expected_columns.items():
                if col_name not in existing_cols:
                    table_missing.append((col_name, col_type, default_value))
            
            if table_missing:
                missing[table] = table_missing
        
        return missing
    
    def apply_migrations(self, conn: sqlite3.Connection, missing_columns: Dict[str, List[Tuple[str, str, str]]]) -> bool:
        """Applique les migrations pour ajouter les colonnes manquantes."""
        if not missing_columns:
            self.log("No missing columns detected. Database is up to date.")
            return True
        
        self.log(f"Found missing columns in {len(missing_columns)} table(s)")
        
        try:
            cursor = conn.cursor()
            
            # SQLite ne supporte pas les transactions pour ALTER TABLE dans tous les cas,
            # mais on utilise BEGIN pour grouper les opérations
            cursor.execute("BEGIN TRANSACTION")
            
            for table, columns in missing_columns.items():
                self.log(f"Processing table '{table}': {len(columns)} column(s) to add")
                
                for col_name, col_type, default_value in columns:
                    # Construire la commande ALTER TABLE
                    if default_value is None:
                        alter_sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                    else:
                        alter_sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type} DEFAULT {default_value}"
                    
                    try:
                        self.log(f"  Adding column: {col_name} ({col_type})")
                        cursor.execute(alter_sql)
                        self.log(f"  ✓ Successfully added column '{col_name}' to table '{table}'")
                    except sqlite3.OperationalError as e:
                        # La colonne existe peut-être déjà
                        if "duplicate column name" in str(e).lower():
                            self.log(f"  ⚠ Column '{col_name}' already exists in table '{table}'", "WARNING")
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
    
    def generate_report(self, output_file: str, missing_columns: Dict[str, List[Tuple[str, str, str]]], success: bool):
        """Génère un rapport détaillé de la migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
                f.write(f"- Total columns added: {total_columns}\n")
                
                f.write("\n## Changes Applied\n\n")
                for table, columns in missing_columns.items():
                    f.write(f"### Table: `{table}`\n\n")
                    for col_name, col_type, default_value in columns:
                        default_str = f" DEFAULT {default_value}" if default_value else ""
                        f.write(f"- Added column: `{col_name}` ({col_type}{default_str})\n")
                    f.write("\n")
            
            if self.errors:
                f.write("\n## Errors\n\n")
                for error in self.errors:
                    f.write(f"- {error}\n")
            
            f.write("\n## Migration Log\n\n")
            f.write("```\n")
            for log_entry in self.migration_log:
                f.write(f"{log_entry}\n")
            f.write("```\n")
        
        self.log(f"Report generated: {output_file}")
    
    def run_migration(self) -> bool:
        """Exécute le processus complet de migration."""
        self.log("=" * 60)
        self.log("Database Structure Update - Safe Migration")
        self.log("=" * 60)
        self.log(f"Database: {self.db_path}")
        
        if not os.path.exists(self.db_path):
            self.log(f"Database file not found: {self.db_path}", "ERROR")
            return False
        
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
                self.log("✓ Database schema is up to date!")
                success = True
            else:
                # Étape 4: Appliquer les migrations
                self.log("Applying migrations...")
                success = self.apply_migrations(conn, missing_columns)
                
                if success:
                    self.log("✓ Migrations completed successfully!")
                    
                    # Étape 5: Optimiser la base de données
                    self.log("Optimizing database...")
                    self.optimize_database(conn)
                else:
                    self.log("✗ Migration failed, restoring backup...", "ERROR")
                    conn.close()
                    self.restore_backup()
            
            conn.close()
            
        except Exception as e:
            self.log(f"Unexpected error during migration: {e}", "ERROR")
            self.errors.append(f"Unexpected error: {e}")
            
            # Restaurer la sauvegarde en cas d'erreur
            self.log("Restoring backup due to error...", "ERROR")
            self.restore_backup()
            success = False
        
        # Générer le rapport
        report_dir = Path(__file__).parent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"migration_report_{timestamp}.md"
        self.generate_report(str(report_file), missing_columns, success)
        
        self.log("=" * 60)
        if success:
            self.log("Migration completed successfully!")
        else:
            self.log("Migration failed. Check the report for details.", "ERROR")
        self.log("=" * 60)
        
        return success


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Safe database structure migration tool")
    parser.add_argument(
        "--db-path",
        default="association.db",
        help="Path to the database file (default: association.db)"
    )
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.db_path)
    success = migrator.run_migration()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
