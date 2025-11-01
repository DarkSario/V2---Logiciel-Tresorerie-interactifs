#!/usr/bin/env python3
"""
Script d'analyse des modules pour détecter les tables et colonnes utilisées.

Ce script parcourt le code Python du projet (modules/, ui/, scripts/, lib/)
et extrait toutes les requêtes SQL et références aux tables/colonnes pour
produire un rapport détaillé des schémas attendus par le code.

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
import yaml


class SQLAnalyzer:
    """Analyseur de code Python pour extraire les références SQL."""
    
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.table_columns = defaultdict(lambda: {"columns": set(), "files": set(), "column_types": {}})
        
        # Patterns pour extraire les requêtes SQL
        self.sql_patterns = [
            # SELECT queries
            r'SELECT\s+(?:\*|[\w,.\s*()]+)\s+FROM\s+(\w+)',
            # INSERT INTO
            r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)',
            # UPDATE queries
            r'UPDATE\s+(\w+)\s+SET\s+([^;]+)',
            # ALTER TABLE
            r'ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)',
            # CREATE TABLE
            r'CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+(\w+)\s*\(([^;]+)\)',
            # PRAGMA table_info
            r'PRAGMA\s+table_info\s*\(\s*(\w+)\s*\)',
        ]
        
        # Pattern pour les références de colonnes dans WHERE, SET, etc.
        self.column_ref_pattern = r'\b(\w+)\s*=\s*[?:]'
        
        # Common false positives to filter out (Python/Tkinter keywords, UI elements, etc.)
        self.false_positive_columns = {
            'padx', 'pady', 'row', 'column', 'text', 'values', 'state', 'side', 'fill', 
            'expand', 'width', 'height', 'command', 'textvariable', 'title', 'header',
            'filetypes', 'defaultextension', 'filepath', 'conn', 'cursor', 'df', 'params',
            'table', 'before', 'after', 'table_matches', 'var', 'on_save', 'CREATE',
        }
        
        # Patterns pour inférer les types de colonnes
        self.type_patterns = {
            'REAL': [
                r'(prix|montant|solde|total|cout|tarif|taux)(_\w+)?$',
                r'(disponible|valeur)(_\w+)?$',
            ],
            'INTEGER': [
                r'(quantite|stock|nombre|count|seuil)(_\w+)?$',
                r'^id(_\w+)?$',
                r'(_id|_count)$',
            ],
            'TEXT': [
                r'(nom|name|prenom|email|adresse|ville|pays)(_\w+)?$',
                r'(commentaire|description|libelle|categorie)(_\w+)?$',
                r'(type|statut|mode|reference|numero)(_\w+)?$',
            ],
            'DATE': [
                r'date(_\w+)?$',
            ],
        }
        
    def infer_column_type(self, column_name):
        """Infère le type SQL d'une colonne basé sur son nom."""
        column_lower = column_name.lower()
        
        # Test patterns for each type
        for sql_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, column_lower, re.IGNORECASE):
                    return sql_type
        
        # Default to TEXT if no pattern matches
        return 'TEXT'
    
    def analyze_file(self, filepath):
        """Analyse un fichier Python pour extraire les références SQL."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return
        
        relative_path = str(filepath.relative_to(self.repo_root))
        
        # Recherche de requêtes SQL (souvent dans des chaînes multi-lignes ou simples)
        # On cherche les patterns SQL dans le contenu
        self._extract_sql_references(content, relative_path)
        
        # Recherche de références dictionary-style (row["column"], row.get("column"))
        self._extract_dict_references(content, relative_path)
    
    def _add_column_to_table(self, table, column, infer_type=True):
        """Ajoute une colonne à une table et infère son type si nécessaire."""
        # Filter out false positives
        if column and column.lower() not in self.false_positive_columns and column not in self.table_columns[table]["columns"]:
            self.table_columns[table]["columns"].add(column)
            if infer_type and column not in self.table_columns[table]["column_types"]:
                self.table_columns[table]["column_types"][column] = self.infer_column_type(column)
    
    def _extract_dict_references(self, content, filepath):
        """Extrait les références dictionary-style (row["column"], row.get("column"))."""
        
        # Pattern pour row["column"] ou row['column']
        for match in re.finditer(r'row\s*\[\s*["\'](\w+)["\']\s*\]', content, re.IGNORECASE):
            column = match.group(1)
            # Essayer de trouver la table associée dans le contexte
            before = content[max(0, match.start()-500):match.start()]
            table_matches = list(re.finditer(r'FROM\s+(\w+)', before, re.IGNORECASE))
            if table_matches:
                table = table_matches[-1].group(1)
                self._add_column_to_table(table, column)
        
        # Pattern pour row.get("column") ou row.get('column')
        for match in re.finditer(r'row\.get\s*\(\s*["\'](\w+)["\']\s*[,\)]', content, re.IGNORECASE):
            column = match.group(1)
            before = content[max(0, match.start()-500):match.start()]
            table_matches = list(re.finditer(r'FROM\s+(\w+)', before, re.IGNORECASE))
            if table_matches:
                table = table_matches[-1].group(1)
                self._add_column_to_table(table, column)
    
    def _extract_sql_references(self, content, filepath):
        """Extrait les références SQL du contenu du fichier."""
        
        # SELECT FROM
        for match in re.finditer(r'SELECT\s+(?:\*|[\w,.\s*()]+)\s+FROM\s+(\w+)', content, re.IGNORECASE):
            table = match.group(1)
            self.table_columns[table]["files"].add(filepath)
            # Essayer d'extraire les colonnes du SELECT
            select_part = content[match.start():match.end()]
            if '*' not in select_part:
                cols = re.findall(r'SELECT\s+([\w,.\s*()]+)\s+FROM', select_part, re.IGNORECASE)
                if cols:
                    for col in cols[0].split(','):
                        col = col.strip().split()[0].split('(')[0].split(')')[0]
                        if col and col != '*' and not col.upper() in ('AS', 'FROM', 'SELECT'):
                            self._add_column_to_table(table, col)
        
        # INSERT INTO
        for match in re.finditer(r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)', content, re.IGNORECASE):
            table = match.group(1)
            columns = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            for col in columns.split(','):
                col = col.strip()
                if col:
                    self._add_column_to_table(table, col)
        
        # UPDATE SET
        for match in re.finditer(r'UPDATE\s+(\w+)\s+SET\s+([^;]+?)(?:WHERE|;|$)', content, re.IGNORECASE | re.DOTALL):
            table = match.group(1)
            set_clause = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            # Extraire les colonnes du SET
            for col_match in re.finditer(r'(\w+)\s*=', set_clause):
                col = col_match.group(1)
                self._add_column_to_table(table, col)
        
        # ALTER TABLE ADD COLUMN
        for match in re.finditer(r'ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)', content, re.IGNORECASE):
            table = match.group(1)
            column = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            self._add_column_to_table(table, column)
        
        # CREATE TABLE
        for match in re.finditer(r'CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+(\w+)\s*\(([^;]+)\)', content, re.IGNORECASE | re.DOTALL):
            table = match.group(1)
            columns_def = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            # Extraire les noms de colonnes (première partie avant le type)
            for line in columns_def.split(','):
                line = line.strip()
                if line and not line.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                    parts = line.split()
                    if parts:
                        col_name = parts[0].strip()
                        # Extract type if present (second part typically)
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
                        
                        if col_name:
                            self._add_column_to_table(table, col_name, infer_type=False)
                            # Use explicit type from CREATE TABLE if available
                            if col_type and col_name not in self.table_columns[table]["column_types"]:
                                self.table_columns[table]["column_types"][col_name] = col_type
                            elif col_name not in self.table_columns[table]["column_types"]:
                                # Infer if not explicitly defined
                                self.table_columns[table]["column_types"][col_name] = self.infer_column_type(col_name)
        
        # PRAGMA table_info
        for match in re.finditer(r'PRAGMA\s+table_info\s*\(\s*["\']?(\w+)["\']?\s*\)', content, re.IGNORECASE):
            table = match.group(1)
            self.table_columns[table]["files"].add(filepath)
        
        # Références de colonnes dans WHERE et autres clauses
        for match in re.finditer(r'WHERE\s+([^;]+?)(?:ORDER|GROUP|LIMIT|$)', content, re.IGNORECASE):
            where_clause = match.group(1)
            # Chercher les tables mentionnées avant ce WHERE
            before = content[:match.start()]
            table_matches = list(re.finditer(r'FROM\s+(\w+)', before, re.IGNORECASE))
            if table_matches:
                table = table_matches[-1].group(1)
                for col_match in re.finditer(r'(\w+)\s*[=<>!]', where_clause):
                    col = col_match.group(1)
                    if col and not col.upper() in ('AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'LIKE'):
                        self._add_column_to_table(table, col)
    
    def scan_directories(self, dirs):
        """Parcourt les répertoires et analyse tous les fichiers Python."""
        for directory in dirs:
            dir_path = self.repo_root / directory
            if not dir_path.exists():
                print(f"Warning: Directory {directory} does not exist")
                continue
            
            print(f"Scanning {directory}...")
            for py_file in dir_path.rglob("*.py"):
                self.analyze_file(py_file)
    
    def generate_yaml_manifest(self, output_file):
        """Génère un manifest YAML machine-readable avec colonnes et types inférés."""
        
        # Filter out false positive table names
        false_positive_tables = {'CREATE', 'for', 'tree', 'sqlite_master'}
        
        # Préparer les données pour YAML
        manifest = {
            "schema_version": "1.0",
            "generated_by": "analyze_modules_columns.py",
            "tables": {}
        }
        
        for table, info in self.table_columns.items():
            # Skip false positive tables
            if table in false_positive_tables:
                continue
                
            if not info["columns"]:
                continue
            
            # Only include tables with at least some reasonable columns (not all false positives)
            valid_columns = [col for col in info["columns"] if col.lower() not in self.false_positive_columns]
            
            if not valid_columns:
                continue
                
            manifest["tables"][table] = {
                "expected_columns": {}
            }
            
            # Ajouter chaque colonne avec son type inféré
            for col in sorted(info["columns"]):
                col_type = info["column_types"].get(col, 'TEXT')
                manifest["tables"][table]["expected_columns"][col] = {
                    "type": col_type,
                    "inferred": col not in info.get("explicit_types", set())
                }
        
        # Écrire le fichier YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
        
        print(f"YAML manifest generated: {output_file}")
    
    def generate_report(self, output_file):
        """Génère un rapport Markdown des tables et colonnes détectées."""
        
        # Trier les tables par ordre alphabétique
        sorted_tables = sorted(self.table_columns.keys())
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Analyse SQL - Tables et Colonnes Détectées\n\n")
            f.write("Ce rapport liste toutes les tables et colonnes référencées dans le code Python.\n")
            f.write("Il sert de référence pour les migrations et la maintenance du schéma de base de données.\n\n")
            f.write(f"**Nombre total de tables détectées:** {len(sorted_tables)}\n\n")
            
            f.write("## Résumé par Table\n\n")
            for table in sorted_tables:
                info = self.table_columns[table]
                col_count = len(info["columns"])
                file_count = len(info["files"])
                f.write(f"- **{table}**: {col_count} colonnes, référencée dans {file_count} fichier(s)\n")
            
            f.write("\n## Détails des Tables et Colonnes\n\n")
            
            for table in sorted_tables:
                info = self.table_columns[table]
                f.write(f"### Table: `{table}`\n\n")
                
                if info["columns"]:
                    f.write("**Colonnes détectées:**\n\n")
                    sorted_cols = sorted(info["columns"])
                    for col in sorted_cols:
                        col_type = info["column_types"].get(col, 'TEXT')
                        f.write(f"- `{col}` (type inféré: {col_type})\n")
                else:
                    f.write("*Aucune colonne spécifique détectée (possiblement SELECT \\*)*\n")
                
                f.write(f"\n**Référencée dans les fichiers:**\n\n")
                sorted_files = sorted(info["files"])
                for filepath in sorted_files:
                    f.write(f"- `{filepath}`\n")
                
                f.write("\n---\n\n")
        
        print(f"Report generated: {output_file}")


def main():
    """Point d'entrée principal du script."""
    # Détecter la racine du projet
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print("=" * 60)
    print("SQL Schema Analyzer - Module Column Detection")
    print("=" * 60)
    print(f"Repository root: {repo_root}")
    print()
    
    # Créer l'analyseur
    analyzer = SQLAnalyzer(repo_root)
    
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
