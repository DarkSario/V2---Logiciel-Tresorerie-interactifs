#!/usr/bin/env python3
"""
Script de vérification du module buvette.
Ce script exécute une série de vérifications automatisées pour identifier
les problèmes dans le code du module buvette avant d'appliquer les corrections.

Vérifications effectuées:
1. Exécution des tests unitaires (pytest)
2. Recherche de patterns problématiques dans le code
3. Vérification de la cohérence entre le schéma DB et le code

Créé dans le cadre de la PR de corrections du module buvette.
"""

import os
import sys
import re
import subprocess
from pathlib import Path

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}--- {text} ---{Colors.ENDC}")

def print_ok(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def run_tests():
    """Exécute les tests unitaires avec pytest."""
    print_section("Exécution des tests unitaires")
    
    # Vérifier si pytest est installé
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print_warning("pytest n'est pas installé. Installation en cours...")
            subprocess.run(["pip", "install", "-q", "pytest"], check=True)
    except Exception as e:
        print_error(f"Impossible de vérifier/installer pytest: {e}")
        return False
    
    # Exécuter les tests
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/test_buvette_inventaire.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print_ok("Tous les tests sont passés")
            return True
        else:
            print_error("Certains tests ont échoué")
            return False
    except subprocess.TimeoutExpired:
        print_error("Timeout lors de l'exécution des tests")
        return False
    except Exception as e:
        print_error(f"Erreur lors de l'exécution des tests: {e}")
        return False

def check_database_schema():
    """Vérifie le schéma de la base de données."""
    print_section("Vérification du schéma de base de données")
    
    db_file = Path("db/db.py")
    if not db_file.exists():
        print_error(f"Fichier {db_file} non trouvé")
        return []
    
    issues = []
    content = db_file.read_text()
    
    # Vérifier la définition de buvette_mouvements
    if 'date_mouvement DATE' in content:
        print_ok("Colonne 'date_mouvement' trouvée dans le schéma")
    else:
        issues.append("Colonne 'date_mouvement' non trouvée dans buvette_mouvements")
        print_error(issues[-1])
    
    if 'type_mouvement TEXT' in content:
        print_ok("Colonne 'type_mouvement' trouvée dans le schéma")
    else:
        issues.append("Colonne 'type_mouvement' non trouvée dans buvette_mouvements")
        print_error(issues[-1])
    
    if 'motif TEXT' in content:
        print_ok("Colonne 'motif' trouvée dans le schéma (pas 'commentaire')")
    
    return issues

def check_buvette_db_file():
    """Vérifie les patterns problématiques dans modules/buvette_db.py."""
    print_section("Vérification de modules/buvette_db.py")
    
    db_file = Path("modules/buvette_db.py")
    if not db_file.exists():
        print_error(f"Fichier {db_file} non trouvé")
        return []
    
    issues = []
    content = db_file.read_text()
    lines = content.split('\n')
    
    # Pattern 1: INSERT avec 'date' au lieu de 'date_mouvement'
    insert_pattern = re.compile(r'INSERT\s+INTO\s+buvette_mouvements\s*\([^)]*\bdate\b[^)]*\)', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if insert_pattern.search(line):
            issues.append(f"Ligne {i}: INSERT utilise 'date' au lieu de 'date_mouvement'")
            print_error(issues[-1])
    
    # Pattern 2: UPDATE avec 'date=' au lieu de 'date_mouvement='
    update_pattern = re.compile(r'UPDATE\s+buvette_mouvements\s+SET[^W]*\bdate\s*=', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if update_pattern.search(line):
            issues.append(f"Ligne {i}: UPDATE utilise 'date=' au lieu de 'date_mouvement='")
            print_error(issues[-1])
    
    # Pattern 3: UPDATE avec 'type=' au lieu de 'type_mouvement='
    update_type_pattern = re.compile(r'UPDATE\s+buvette_mouvements\s+SET[^W]*\btype\s*=', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if update_type_pattern.search(line):
            issues.append(f"Ligne {i}: UPDATE utilise 'type=' au lieu de 'type_mouvement='")
            print_error(issues[-1])
    
    # Pattern 4: SELECT sans alias AS date, AS type
    select_mouvements = re.compile(r'def\s+list_mouvements\(\):', re.IGNORECASE)
    found_list_mouvements = False
    for i, line in enumerate(lines, 1):
        if select_mouvements.search(line):
            found_list_mouvements = True
            # Vérifier les 20 lignes suivantes pour les alias
            check_lines = '\n'.join(lines[i:min(i+20, len(lines))])
            if 'AS date' not in check_lines or 'AS type' not in check_lines:
                issues.append(f"Fonction list_mouvements (ligne {i}): manque les alias AS date/AS type")
                print_error(issues[-1])
            else:
                print_ok("list_mouvements contient les alias AS date/AS type")
            break
    
    if not found_list_mouvements:
        issues.append("Fonction list_mouvements non trouvée")
        print_error(issues[-1])
    
    # Pattern 5: get_mouvement_by_id sans alias
    select_mouvement_by_id = re.compile(r'def\s+get_mouvement_by_id\(', re.IGNORECASE)
    found_get_mouvement = False
    for i, line in enumerate(lines, 1):
        if select_mouvement_by_id.search(line):
            found_get_mouvement = True
            check_lines = '\n'.join(lines[i:min(i+20, len(lines))])
            if 'AS date' not in check_lines or 'AS type' not in check_lines:
                issues.append(f"Fonction get_mouvement_by_id (ligne {i}): manque les alias AS date/AS type")
                print_error(issues[-1])
            else:
                print_ok("get_mouvement_by_id contient les alias AS date/AS type")
            break
    
    if not found_get_mouvement:
        issues.append("Fonction get_mouvement_by_id non trouvée")
        print_error(issues[-1])
    
    if not issues:
        print_ok("Aucun problème trouvé dans buvette_db.py")
    
    return issues

def check_buvette_ui_file():
    """Vérifie les patterns problématiques dans modules/buvette.py."""
    print_section("Vérification de modules/buvette.py")
    
    ui_file = Path("modules/buvette.py")
    if not ui_file.exists():
        print_error(f"Fichier {ui_file} non trouvé")
        return []
    
    issues = []
    content = ui_file.read_text()
    lines = content.split('\n')
    
    # Pattern 1: InventaireDialog sans columnconfigure
    inventaire_dialog_pattern = re.compile(r'class\s+InventaireDialog\(', re.IGNORECASE)
    found_inventaire = False
    for i, line in enumerate(lines, 1):
        if inventaire_dialog_pattern.search(line):
            found_inventaire = True
            # Vérifier les 50 lignes suivantes
            check_lines = '\n'.join(lines[i:min(i+50, len(lines))])
            if 'columnconfigure' not in check_lines:
                issues.append(f"InventaireDialog (ligne {i}): manque columnconfigure(1, weight=1)")
                print_error(issues[-1])
            else:
                print_ok("InventaireDialog contient columnconfigure")
            
            if 'sticky=' not in check_lines or 'sticky="ew"' not in check_lines:
                issues.append(f"InventaireDialog (ligne {i}): les Entry/Combobox devraient avoir sticky='ew'")
                print_warning(issues[-1])
            break
    
    # Pattern 2: LignesInventaireDialog affiche article_id au lieu de article_name
    lignes_refresh = re.compile(r'def\s+refresh_lignes\(self\):', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if lignes_refresh.search(line):
            check_lines = '\n'.join(lines[i:min(i+20, len(lines))])
            if 'article_id' in check_lines and 'values=' in check_lines:
                if 'article_name' not in check_lines:
                    issues.append(f"LignesInventaireDialog.refresh_lignes (ligne {i}): affiche article_id au lieu de article_name")
                    print_error(issues[-1])
                else:
                    print_ok("refresh_lignes utilise article_name")
            break
    
    # Pattern 3: LigneInventaireDialog utilise Entry pour article_id
    ligne_dialog = re.compile(r'class\s+LigneInventaireDialog\(', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if ligne_dialog.search(line):
            check_lines = '\n'.join(lines[i:min(i+50, len(lines))])
            if 'article_id_var' in check_lines and 'tk.Entry' in check_lines:
                if 'Combobox' not in check_lines or 'list_articles_names' not in check_lines:
                    issues.append(f"LigneInventaireDialog (ligne {i}): devrait utiliser Combobox au lieu de Entry pour article")
                    print_error(issues[-1])
                else:
                    print_ok("LigneInventaireDialog utilise Combobox")
            break
    
    # Pattern 4: MouvementDialog utilise Entry pour article_id
    mouvement_dialog = re.compile(r'class\s+MouvementDialog\(', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if mouvement_dialog.search(line):
            check_lines = '\n'.join(lines[i:min(i+50, len(lines))])
            if 'article_id_var' in check_lines and 'tk.Entry' in check_lines:
                if 'Combobox' not in check_lines or 'list_articles_names' not in check_lines:
                    issues.append(f"MouvementDialog (ligne {i}): devrait utiliser Combobox au lieu de Entry pour article")
                    print_error(issues[-1])
                else:
                    print_ok("MouvementDialog utilise Combobox")
            break
    
    # Pattern 5: refresh_bilan sans protection contre None
    bilan_pattern = re.compile(r'def\s+refresh_bilan\(self\):', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if bilan_pattern.search(line):
            check_lines = '\n'.join(lines[i:min(i+30, len(lines))])
            # Vérifier si sum() est protégé
            if 'sum(' in check_lines:
                if 'or 0' not in check_lines and 'if' not in check_lines:
                    issues.append(f"refresh_bilan (ligne {i}): sum() devrait être protégé contre None")
                    print_warning(issues[-1])
                else:
                    print_ok("refresh_bilan protège les agrégations")
            break
    
    if not issues:
        print_ok("Aucun problème trouvé dans buvette.py")
    
    return issues

def check_file_structure():
    """Vérifie la structure des fichiers du projet."""
    print_section("Vérification de la structure des fichiers")
    
    required_files = [
        "db/db.py",
        "modules/buvette_db.py",
        "modules/buvette.py",
        "modules/buvette_inventaire_db.py",
        "tests/test_buvette_inventaire.py"
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print_ok(f"Fichier trouvé: {file}")
        else:
            missing.append(file)
            print_error(f"Fichier manquant: {file}")
    
    return missing

def generate_summary(all_issues):
    """Génère un résumé des problèmes trouvés."""
    print_header("RÉSUMÉ DES VÉRIFICATIONS")
    
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    if total_issues == 0:
        print_ok("✓ Aucun problème détecté ! Le module buvette est conforme.")
    else:
        print_error(f"✗ {total_issues} problème(s) détecté(s) nécessitant une correction:")
        
        for category, issues in all_issues.items():
            if issues:
                print(f"\n{Colors.WARNING}{category}:{Colors.ENDC}")
                for issue in issues:
                    print(f"  - {issue}")
    
    return total_issues

def main():
    """Fonction principale du script de vérification."""
    print_header("SCRIPT DE VÉRIFICATION DU MODULE BUVETTE")
    print("Ce script identifie les incohérences et problèmes dans le module buvette")
    print("avant d'appliquer les corrections.\n")
    
    # Changer vers le répertoire racine du projet
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"Répertoire de travail: {os.getcwd()}\n")
    
    all_issues = {}
    
    # 1. Vérifier la structure des fichiers
    missing_files = check_file_structure()
    if missing_files:
        all_issues["Fichiers manquants"] = missing_files
    
    # 2. Vérifier le schéma de base de données
    schema_issues = check_database_schema()
    if schema_issues:
        all_issues["Schéma de base de données"] = schema_issues
    
    # 3. Vérifier buvette_db.py
    db_issues = check_buvette_db_file()
    if db_issues:
        all_issues["modules/buvette_db.py"] = db_issues
    
    # 4. Vérifier buvette.py
    ui_issues = check_buvette_ui_file()
    if ui_issues:
        all_issues["modules/buvette.py"] = ui_issues
    
    # 5. Exécuter les tests
    tests_passed = run_tests()
    if not tests_passed:
        all_issues["Tests unitaires"] = ["Certains tests ont échoué"]
    
    # 6. Générer le résumé
    total_issues = generate_summary(all_issues)
    
    # Retourner un code de sortie approprié
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
