# Scripts de Maintenance et Migration

Ce répertoire contient des scripts utilitaires pour la maintenance et la migration de la base de données de l'application.

## Scripts Disponibles

### 1. `analyze_modules_columns.py`

Script d'analyse du code pour détecter les tables et colonnes SQL utilisées dans l'application.

**Fonctionnalités:**
- Parcourt automatiquement tous les fichiers Python dans `modules/`, `ui/`, `scripts/`, `lib/`, et `db/`
- Extrait les requêtes SQL (SELECT, INSERT, UPDATE, ALTER TABLE, CREATE TABLE)
- Identifie les références aux tables et colonnes
- Génère un rapport détaillé au format Markdown

**Usage:**
```bash
python scripts/analyze_modules_columns.py
```

**Sortie:**
- `reports/SQL_SCHEMA_HINTS.md` - Rapport complet avec :
  - Résumé par table (nombre de colonnes et fichiers)
  - Détails des colonnes détectées pour chaque table
  - Liste des fichiers où chaque table est référencée

**Cas d'usage:**
- Documentation du schéma de base de données
- Audit des dépendances SQL
- Préparation des migrations
- Détection des tables/colonnes non utilisées

---

### 2. `update_db_structure.py`

Script de migration sûre de la structure de base de données.

**Fonctionnalités:**
- Compare le schéma de référence avec le schéma actuel de la base
- Détecte automatiquement les colonnes manquantes
- Crée une sauvegarde timestampée avant toute modification
- Exécute les migrations dans une transaction
- Restaure automatiquement la sauvegarde en cas d'erreur
- Active le mode WAL pour de meilleures performances
- Optimise les paramètres PRAGMA
- Génère un rapport détaillé de migration

**Usage:**
```bash
# Migration de association.db (défaut)
python scripts/update_db_structure.py

# Migration d'une autre base
python scripts/update_db_structure.py --db-path chemin/vers/base.db
```

**Options:**
- `--db-path PATH` : Chemin vers la base de données à migrer (défaut: `association.db`)

**Sorties:**
- `[db-file].YYYYMMDD_HHMMSS.bak` - Sauvegarde timestampée de la base
- `scripts/migration_report_YYYYMMDD_HHMMSS.md` - Rapport détaillé de migration

**Format du rapport de migration:**
```markdown
# Database Migration Report

**Date:** 2025-11-01 10:30:46
**Database:** association.db
**Status:** SUCCESS
**Backup:** association.db.20251101_103046.bak

## Summary
- Tables requiring updates: 2
- Total columns added: 11

## Changes Applied
### Table: `config`
- Added column: `but_asso` (TEXT DEFAULT '')
- Added column: `cloture` (INTEGER DEFAULT 0)
...

## Migration Log
[Logs détaillés de toutes les opérations]
```

**Sécurité:**
- **Sauvegarde automatique** : Une copie de la base est créée avant toute modification
- **Transactions** : Toutes les modifications sont groupées dans une transaction
- **Rollback automatique** : En cas d'erreur, la transaction est annulée
- **Restauration** : La sauvegarde est restaurée automatiquement si la migration échoue
- **Pas de perte de données** : Les colonnes ajoutées ont des valeurs par défaut appropriées

**Schéma de référence:**
Le script contient un schéma de référence complet couvrant toutes les tables de l'application :
- `config`, `comptes`, `membres`
- `events`, `event_modules`, `event_module_fields`, `event_module_data`
- `event_payments`, `event_caisses`, `event_caisse_details`
- `event_recettes`, `event_depenses`
- `dons_subventions`, `depenses_regulieres`, `depenses_diverses`
- `categories`, `stock`, `inventaires`, `inventaire_lignes`, `mouvements_stock`
- `fournisseurs`, `colonnes_modeles`, `valeurs_modeles_colonnes`
- `depots_retraits_banque`, `historique_clotures`, `retrocessions_ecoles`
- `buvette_articles`, `buvette_achats`, `buvette_inventaires`
- `buvette_inventaire_lignes`, `buvette_mouvements`, `buvette_recettes`

**Types de colonnes et valeurs par défaut:**
- `TEXT` : Défaut `''` (chaîne vide)
- `INTEGER` : Défaut `0`
- `REAL` : Défaut `0.0`
- Colonnes optionnelles : Défaut `NULL` (None)

---

### 3. Autres scripts

#### `migration.py`
Script de migration basique (legacy). Utiliser `update_db_structure.py` pour les migrations modernes.

#### `enable_wal.py`
Active le mode WAL (Write-Ahead Logging) sur une base de données.

#### `migrate_add_purchase_price.py`
Migration spécifique pour ajouter la colonne `purchase_price` à `buvette_articles`.

#### `check_buvette.py`
Script de vérification de l'intégrité des données de la buvette.

#### `project_audit.py`
Audit général du projet et de sa structure.

---

## Intégration dans l'Application

La fonctionnalité de mise à jour de la structure est intégrée dans le menu **Administration** de l'application :

**Menu Administration > Mettre à jour la structure de la base**

Cette option :
1. Affiche une boîte de dialogue explicative
2. Demande confirmation à l'utilisateur
3. Exécute le script `update_db_structure.py`
4. Affiche un message de succès ou d'erreur
5. Indique l'emplacement du rapport de migration

---

## Workflow Recommandé

### Pour les développeurs

1. **Après avoir ajouté une nouvelle colonne dans le code:**
   ```bash
   # 1. Analyser l'utilisation SQL actuelle
   python scripts/analyze_modules_columns.py
   
   # 2. Ajouter la nouvelle colonne au REFERENCE_SCHEMA dans update_db_structure.py
   # 3. Tester la migration sur une copie de base
   python scripts/update_db_structure.py --db-path test_copy.db
   
   # 4. Vérifier le rapport de migration
   cat scripts/migration_report_*.md
   ```

2. **Avant un déploiement:**
   ```bash
   # Vérifier quelles colonnes seront ajoutées
   python scripts/update_db_structure.py --db-path production.db
   ```

### Pour les utilisateurs

1. **Via l'interface graphique** (recommandé) :
   - Ouvrir l'application
   - Menu Administration > Mettre à jour la structure de la base
   - Suivre les instructions à l'écran

2. **Via la ligne de commande** :
   ```bash
   python scripts/update_db_structure.py
   ```

---

## Tests

Des tests unitaires complets sont disponibles :

```bash
# Tester l'analyseur de modules
python tests/test_analyze_modules.py

# Tester le système de migration
python tests/test_database_migration.py

# Exécuter tous les tests
pytest tests/test_analyze_modules.py tests/test_database_migration.py
```

---

## Dépannage

### La migration échoue

1. **Vérifier les logs** : Consulter le rapport de migration dans `scripts/migration_report_*.md`
2. **Vérifier la sauvegarde** : Un fichier `.bak` a été créé automatiquement
3. **Restaurer manuellement** : Si nécessaire, copier le fichier `.bak` vers le fichier original

### Colonnes non détectées par l'analyseur

L'analyseur utilise des expressions régulières pour détecter les requêtes SQL. Si une colonne n'est pas détectée :
- Elle peut être référencée de manière dynamique (nom dans une variable)
- La syntaxe SQL peut être inhabituelle
- Ajouter manuellement la colonne au `REFERENCE_SCHEMA` si nécessaire

### Base de données verrouillée

Si vous obtenez une erreur "database is locked" :
1. Fermer toutes les instances de l'application
2. Vérifier qu'aucun autre processus n'accède à la base
3. Réessayer la migration

---

## Maintenance

### Ajouter une nouvelle table au schéma de référence

Éditer `scripts/update_db_structure.py` et ajouter la définition de la table dans `REFERENCE_SCHEMA` :

```python
REFERENCE_SCHEMA = {
    # ... tables existantes ...
    
    "nouvelle_table": {
        "id": ("INTEGER", None),
        "nom": ("TEXT", "''"),
        "valeur": ("REAL", "0.0"),
        # ... autres colonnes ...
    },
}
```

### Mettre à jour une colonne existante

**Important** : `update_db_structure.py` n'ajoute que des colonnes manquantes. Il ne modifie pas les colonnes existantes.

Pour modifier une colonne existante :
1. Créer un script de migration spécifique
2. Ou utiliser un outil externe (sqlite3, DB Browser for SQLite)

---

## Bonnes Pratiques

1. **Toujours faire une sauvegarde** avant une migration manuelle
2. **Tester sur une copie** avant de migrer la base de production
3. **Consulter les rapports** après chaque migration
4. **Garder les sauvegardes** pendant quelques jours après une migration réussie
5. **Documenter** les colonnes ajoutées dans le code

---

## Licence

Ces scripts font partie du projet "Gestion Association Les Interactifs des Ecoles".
