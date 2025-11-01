#!/usr/bin/env python3
"""
Script d'analyse stricte des modules pour détecter les tables et colonnes utilisées.

Ce script parcourt le code Python du projet (modules/, ui/, scripts/, lib/)
et extrait UNIQUEMENT les identifiants SQL valides des requêtes SQL pour
produire un rapport détaillé des schémas attendus par le code.

Contraintes:
- Utilise un regex strict ^[A-Za-z_][A-Za-z0-9_]*$ pour valider les identifiants SQL
- N'extrait QUE depuis les patterns SQL: INSERT INTO, UPDATE SET, SELECT FROM
- Ignore les tokens de code, appels de fonction, texte UI
- Génère des rapports UTF-8
- Collecte les identifiants invalides pour rapport

Usage:
    python scripts/analyze_modules_columns.py
    
Sortie:
    reports/SQL_SCHEMA_HINTS.md - Rapport lisible avec tables et colonnes détectées
    db/schema_hints.yaml - Manifest machine-readable avec colonnes attendues et types inférés
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple

# Force UTF-8 encoding for stdout/stderr
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Valid SQL identifier pattern: starts with letter or underscore, followed by letters, digits, or underscores
SQL_IDENTIFIER_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class StrictSQLAnalyzer:
    """Analyseur strict de code Python pour extraire UNIQUEMENT les identifiants SQL valides."""
    
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.table_columns = defaultdict(lambda: {
            "columns": set(),
            "files": set(),
            "column_types": {}
        })
        self.skipped_identifiers = defaultdict(set)  # Track invalid identifiers
        
        # Patterns pour inférer les types de colonnes
        self.type_patterns = {
            'REAL': [
                r'(prix|montant|solde|total|cout|tarif|taux|valeur)(_\w+)?$',
                r'(disponible|contenance|quantite)(_\w+)?$',
            ],
            'INTEGER': [
                r'^id(_\w+)?$',
                r'(_id|_count|seuil)$',
                r'^(stock|nombre|count)(_\w+)?$',
            ],
            'TEXT': [
                r'(nom|name|prenom|email|adresse|ville|pays)(_\w+)?$',
                r'(commentaire|description|libelle|categorie)(_\w+)?$',
                r'(type|statut|mode|reference|numero|lot)(_\w+)?$',
                r'(fournisseur|donateur|ecole|banque)(_\w+)?$',
                r'(lieu|unite|facture|motif)(_\w+)?$',
            ],
            'DATE': [
                r'date(_\w+)?$',
            ],
        }
    
    def is_valid_sql_identifier(self, identifier: str) -> bool:
        """Vérifie si un identifiant est un identifiant SQL valide."""
        if not identifier:
            return False
        return SQL_IDENTIFIER_PATTERN.match(identifier) is not None
    
    def infer_column_type(self, column_name: str) -> str:
        """Infère le type SQL d'une colonne basé sur son nom."""
        column_lower = column_name.lower()
        
        # Test patterns for each type
        for sql_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, column_lower, re.IGNORECASE):
                    return sql_type
        
        # Default to TEXT if no pattern matches
        return 'TEXT'
    
    def add_table_column(self, table: str, column: str, filepath: str):
        """
        Ajoute une colonne à une table après validation stricte.
        
        Args:
            table: Nom de la table
            column: Nom de la colonne
            filepath: Fichier source
        """
        # Validate table name
        if not self.is_valid_sql_identifier(table):
            self.skipped_identifiers[filepath].add(f"table:{table}")
            return
        
        # Validate column name
        if not self.is_valid_sql_identifier(column):
            self.skipped_identifiers[filepath].add(f"column:{column} (table:{table})")
            return
        
        # Add to tracking
        self.table_columns[table]["columns"].add(column)
        self.table_columns[table]["files"].add(filepath)
        
        # Infer type if not already set
        if column not in self.table_columns[table]["column_types"]:
            self.table_columns[table]["column_types"][column] = self.infer_column_type(column)
    
    def analyze_file(self, filepath: Path):
        """Analyse un fichier Python pour extraire les références SQL strictes."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return
        
        relative_path = str(filepath.relative_to(self.repo_root))
        
        # Extract SQL references using strict patterns
        self._extract_insert_statements(content, relative_path)
        self._extract_update_statements(content, relative_path)
        self._extract_select_statements(content, relative_path)
        self._extract_create_table_statements(content, relative_path)
    
    def _extract_insert_statements(self, content: str, filepath: str):
        """Extrait les colonnes depuis INSERT INTO statements."""
        # Pattern: INSERT INTO table_name (col1, col2, col3)
        pattern = r'INSERT\s+INTO\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]+)\)'
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            table = match.group(1)
            columns_str = match.group(2)
            
            # Extract individual column names
            columns = [col.strip() for col in columns_str.split(',')]
            
            for col in columns:
                # Remove any whitespace and validate
                col = col.strip()
                if col:
                    self.add_table_column(table, col, filepath)
    
    def _extract_update_statements(self, content: str, filepath: str):
        """Extrait les colonnes depuis UPDATE statements."""
        # Pattern: UPDATE table_name SET col1=?, col2=?
        pattern = r'UPDATE\s+([A-Za-z_][A-Za-z0-9_]*)\s+SET\s+([^;]+?)(?:WHERE|;|$)'
        
        for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
            table = match.group(1)
            set_clause = match.group(2)
            
            # Extract column names from SET clause (before = sign)
            col_pattern = r'([A-Za-z_][A-Za-z0-9_]*)\s*='
            for col_match in re.finditer(col_pattern, set_clause):
                col = col_match.group(1)
                self.add_table_column(table, col, filepath)
    
    def _extract_select_statements(self, content: str, filepath: str):
        """Extrait les tables depuis SELECT statements (colonnes depuis liste explicite)."""
        # Pattern: SELECT col1, col2 FROM table_name
        # or SELECT * FROM table_name
        pattern = r'SELECT\s+([\w\s,.*()]+?)\s+FROM\s+([A-Za-z_][A-Za-z0-9_]*)'
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            columns_str = match.group(1).strip()
            table = match.group(2)
            
            # Register the table (even with SELECT *)
            self.table_columns[table]["files"].add(filepath)
            
            # If not SELECT *, try to extract column names
            if '*' not in columns_str:
                # Extract column names (simple identifier extraction)
                col_pattern = r'\b([A-Za-z_][A-Za-z0-9_]*)\b'
                for col_match in re.finditer(col_pattern, columns_str):
                    col = col_match.group(1)
                    # Skip SQL keywords that might appear
                    if col.upper() not in ('AS', 'FROM', 'SELECT', 'DISTINCT', 'COUNT', 'MAX', 'MIN', 'SUM', 'AVG'):
                        self.add_table_column(table, col, filepath)
    
    def _extract_create_table_statements(self, content: str, filepath: str):
        """Extrait les colonnes depuis CREATE TABLE statements."""
        # Pattern: CREATE TABLE [IF NOT EXISTS] table_name (columns...)
        pattern = r'CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^;]+)\)'
        
        for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
            table = match.group(1)
            columns_def = match.group(2)
            
            # Register table
            self.table_columns[table]["files"].add(filepath)
            
            # Parse column definitions
            # Split by comma, but be careful of constraints
            for line in columns_def.split(','):
                line = line.strip()
                if not line:
                    continue
                
                # Skip constraint definitions
                if line.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                    continue
                
                # Extract column name (first word) and type (second word)
                parts = line.split()
                if parts:
                    col_name = parts[0].strip()
                    
                    # Extract type if present
                    col_type = None
                    if len(parts) > 1:
                        type_str = parts[1].upper()
                        if 'INTEGER' in type_str or 'INT' in type_str:
                            col_type = 'INTEGER'
                        elif 'REAL' in type_str or 'FLOAT' in type_str or 'DOUBLE' in type_str:
                            col_type = 'REAL'
                        elif 'TEXT' in type_str or 'VARCHAR' in type_str or 'CHAR' in type_str:
                            col_type = 'TEXT'
                        elif 'DATE' in type_str or 'TIME' in type_str:
                            col_type = 'TEXT'  # SQLite stores dates as TEXT
                    
                    # Add column (validation happens in add_table_column)
                    if self.is_valid_sql_identifier(col_name):
                        self.add_table_column(table, col_name, filepath)
                        # Use explicit type from CREATE TABLE if available
                        if col_type:
                            self.table_columns[table]["column_types"][col_name] = col_type
    
    def scan_directories(self, dirs: List[str]):
        """Parcourt les répertoires et analyse tous les fichiers Python."""
        for directory in dirs:
            dir_path = self.repo_root / directory
            if not dir_path.exists():
                print(f"Warning: Directory {directory} does not exist")
                continue
            
            print(f"Scanning {directory}...")
            for py_file in dir_path.rglob("*.py"):
                self.analyze_file(py_file)
    
    def generate_yaml_manifest(self, output_file: Path):
        """Génère un manifest YAML simple avec colonnes et types inférés."""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Schema Hints for Database Migration\n")
            f.write("# Generated by analyze_modules_columns.py\n")
            f.write("#\n")
            f.write("# This file contains expected columns extracted from SQL queries in the code.\n")
            f.write("# You can manually add overrides or aliases in the 'manual_overrides' section.\n")
            f.write("#\n")
            f.write("# Format:\n")
            f.write("#   tables:\n")
            f.write("#     table_name:\n")
            f.write("#       expected_columns:\n")
            f.write("#         column_name:\n")
            f.write("#           type: TEXT|INTEGER|REAL|DATE\n")
            f.write("#           inferred: true|false\n")
            f.write("#\n")
            f.write("# Manual overrides example:\n")
            f.write("#   manual_overrides:\n")
            f.write("#     table_name:\n")
            f.write("#       column_aliases:\n")
            f.write("#         old_name: new_name\n")
            f.write("#       forced_types:\n")
            f.write("#         column_name: REAL\n")
            f.write("\n")
            
            f.write("schema_version: \"1.0\"\n")
            f.write("generated_by: \"analyze_modules_columns.py\"\n")
            f.write("\ntables:\n")
            
            # Write tables
            for table in sorted(self.table_columns.keys()):
                info = self.table_columns[table]
                
                if not info["columns"]:
                    continue
                
                f.write(f"  {table}:\n")
                f.write(f"    expected_columns:\n")
                
                # Write columns
                for col in sorted(info["columns"]):
                    col_type = info["column_types"].get(col, 'TEXT')
                    f.write(f"      {col}:\n")
                    f.write(f"        type: {col_type}\n")
                    f.write(f"        inferred: true\n")
            
            # Add placeholder for manual overrides
            f.write("\n# Manual overrides (edit this section to add custom mappings)\n")
            f.write("manual_overrides: {}\n")
        
        print(f"YAML manifest generated: {output_file}")
    
    def generate_report(self, output_file: Path):
        """Génère un rapport Markdown des tables et colonnes détectées."""
        
        sorted_tables = sorted(self.table_columns.keys())
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Analyse SQL - Tables et Colonnes Detectees\n\n")
            f.write("Ce rapport liste toutes les tables et colonnes referencees dans le code Python.\n")
            f.write("Il sert de reference pour les migrations et la maintenance du schema de base de donnees.\n\n")
            f.write(f"**Nombre total de tables detectees:** {len(sorted_tables)}\n\n")
            
            f.write("## Resume par Table\n\n")
            for table in sorted_tables:
                info = self.table_columns[table]
                col_count = len(info["columns"])
                file_count = len(info["files"])
                f.write(f"- **{table}**: {col_count} colonnes, referencee dans {file_count} fichier(s)\n")
            
            f.write("\n## Details des Tables et Colonnes\n\n")
            
            for table in sorted_tables:
                info = self.table_columns[table]
                f.write(f"### Table: `{table}`\n\n")
                
                if info["columns"]:
                    f.write("**Colonnes detectees:**\n\n")
                    sorted_cols = sorted(info["columns"])
                    for col in sorted_cols:
                        col_type = info["column_types"].get(col, 'TEXT')
                        f.write(f"- `{col}` (type infere: {col_type})\n")
                else:
                    f.write("*Aucune colonne specifique detectee (possiblement SELECT \\*)*\n")
                
                f.write(f"\n**Referencee dans les fichiers:**\n\n")
                sorted_files = sorted(info["files"])
                for filepath in sorted_files:
                    f.write(f"- `{filepath}`\n")
                
                f.write("\n---\n\n")
            
            # Add skipped identifiers section
            if self.skipped_identifiers:
                f.write("\n## Identifiants Invalides Ignores\n\n")
                f.write("Les identifiants suivants ont ete trouves dans le code mais ne correspondent pas\n")
                f.write("au pattern SQL valide (^[A-Za-z_][A-Za-z0-9_]*$) et ont ete ignores:\n\n")
                
                for filepath in sorted(self.skipped_identifiers.keys()):
                    skipped = self.skipped_identifiers[filepath]
                    if skipped:
                        f.write(f"**Fichier: `{filepath}`**\n\n")
                        for item in sorted(skipped):
                            f.write(f"- {item}\n")
                        f.write("\n")
        
        print(f"Report generated: {output_file}")


def main():
    """Point d'entrée principal du script."""
    # Détecter la racine du projet
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print("=" * 60)
    print("SQL Schema Analyzer - Strict SQL Identifier Extraction")
    print("=" * 60)
    print(f"Repository root: {repo_root}")
    print()
    
    # Créer l'analyseur
    analyzer = StrictSQLAnalyzer(repo_root)
    
    # Répertoires à scanner
    directories = ["modules", "ui", "scripts", "lib", "db"]
    
    # Scanner les répertoires
    analyzer.scan_directories(directories)
    
    print()
    print(f"Analysis complete. Found {len(analyzer.table_columns)} tables.")
    
    # Générer le rapport Markdown
    report_dir = repo_root / "reports"
    report_dir.mkdir(exist_ok=True)
    output_file = report_dir / "SQL_SCHEMA_HINTS.md"
    
    analyzer.generate_report(output_file)
    
    # Générer le manifest YAML
    db_dir = repo_root / "db"
    db_dir.mkdir(exist_ok=True)
    yaml_file = db_dir / "schema_hints.yaml"
    
    analyzer.generate_yaml_manifest(yaml_file)
    
    print()
    print("=" * 60)
    print(f"Report saved to: {output_file}")
    print(f"YAML manifest saved to: {yaml_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
