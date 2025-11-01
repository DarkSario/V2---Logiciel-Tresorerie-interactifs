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
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path


class SQLAnalyzer:
    """Analyseur de code Python pour extraire les références SQL."""
    
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.table_columns = defaultdict(lambda: {"columns": set(), "files": set()})
        
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
                            self.table_columns[table]["columns"].add(col)
        
        # INSERT INTO
        for match in re.finditer(r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)', content, re.IGNORECASE):
            table = match.group(1)
            columns = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            for col in columns.split(','):
                col = col.strip()
                if col:
                    self.table_columns[table]["columns"].add(col)
        
        # UPDATE SET
        for match in re.finditer(r'UPDATE\s+(\w+)\s+SET\s+([^W][^;]+?)(?:WHERE|$)', content, re.IGNORECASE | re.DOTALL):
            table = match.group(1)
            set_clause = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            # Extraire les colonnes du SET
            for col_match in re.finditer(r'(\w+)\s*=', set_clause):
                col = col_match.group(1)
                self.table_columns[table]["columns"].add(col)
        
        # ALTER TABLE ADD COLUMN
        for match in re.finditer(r'ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)', content, re.IGNORECASE):
            table = match.group(1)
            column = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            self.table_columns[table]["columns"].add(column)
        
        # CREATE TABLE
        for match in re.finditer(r'CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+(\w+)\s*\(([^;]+)\)', content, re.IGNORECASE | re.DOTALL):
            table = match.group(1)
            columns_def = match.group(2)
            self.table_columns[table]["files"].add(filepath)
            # Extraire les noms de colonnes (première partie avant le type)
            for line in columns_def.split(','):
                line = line.strip()
                if line and not line.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                    col_name = line.split()[0].strip()
                    if col_name:
                        self.table_columns[table]["columns"].add(col_name)
        
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
                        self.table_columns[table]["columns"].add(col)
    
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
                        f.write(f"- `{col}`\n")
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
    
    # Générer le rapport
    report_dir = repo_root / "reports"
    report_dir.mkdir(exist_ok=True)
    output_file = report_dir / "SQL_SCHEMA_HINTS.md"
    
    analyzer.generate_report(output_file)
    
    print()
    print("=" * 60)
    print(f"Report saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
