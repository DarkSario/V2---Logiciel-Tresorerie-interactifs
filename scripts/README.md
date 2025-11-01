# Scripts de Maintenance et Migration

Ce répertoire contient des scripts utilitaires pour la maintenance et la migration de la base de données de l'application.

## Smart Migrations System

Le système de migrations intelligentes fournit une gestion de schéma de base de données sûre et automatisée.

### 1. `analyze_modules_columns.py` - Analyseur SQL Strict

Script d'analyse stricte du code pour détecter les tables et colonnes SQL utilisées dans l'application.

**Fonctionnalités clés:**
- **Validation stricte** : Utilise le pattern regex `^[A-Za-z_][A-Za-z0-9_]*$` pour valider les identifiants SQL
- **Extraction précise** : N'extrait QUE depuis les patterns SQL (INSERT INTO, UPDATE SET, SELECT FROM, CREATE TABLE)
- **Évite les faux positifs** : Ignore les tokens de code, appels de fonction, et texte UI
- **Inférence de types** : Détecte automatiquement les types de colonnes (TEXT, INTEGER, REAL, DATE) basés sur les noms
- **Rapporte les invalides** : Collecte et rapporte les identifiants invalides trouvés

**Usage:**
```bash
python scripts/analyze_modules_columns.py
```

**Sorties:**
- `reports/SQL_SCHEMA_HINTS.md` - Rapport lisible en markdown avec :
  - Résumé par table (nombre de colonnes et fichiers)
  - Détails des colonnes détectées avec types inférés
  - Liste des fichiers où chaque table est référencée
  - Section des identifiants invalides ignorés

- `db/schema_hints.yaml` - Manifest machine-readable au format simple :
  ```yaml
  schema_version: "1.0"
  tables:
    table_name:
      expected_columns:
        column_name:
          type: TEXT|INTEGER|REAL|DATE
          inferred: true
  manual_overrides: {}
  ```

**Cas d'usage:**
- Documentation du schéma de base de données
- Génération de hints pour la migration
- Détection des colonnes manquantes
- Audit des dépendances SQL

---

### 2. `update_db_structure.py` - Migrateur Intelligent de Base de Données

Script de migration robuste avec matching fuzzy et renommage intelligent de colonnes.

**Fonctionnalités intelligentes:**
- **Chargement de hints YAML** : Charge `db/schema_hints.yaml` ou exécute l'analyseur en fallback
- **Validation stricte** : Valide tous les noms de colonnes attendus (ignore et rapporte les invalides)
- **Fuzzy matching** : Détecte les colonnes similaires (ex: `prnom` → `prenom`) avec seuil configurable (0.75 par défaut)
- **Matching insensible à la casse** : Trouve `email` même si la colonne s'appelle `EMail`
- **Renommage intelligent** : Utilise `ALTER TABLE RENAME COLUMN` si supporté (SQLite 3.25+)
- **Fallback ADD+COPY** : Pour versions anciennes ou échec de rename, ajoute colonne et copie les données
- **Sauvegardes timestampées** : Crée toujours `{database}.YYYYMMDD_HHMMSS.bak`
- **Transactions sûres** : Rollback automatique en cas d'erreur
- **Optimisation** : Active WAL mode et optimise les pragmas SQLite

**Usage:**
```bash
# Migration de association.db (défaut)
python scripts/update_db_structure.py

# Migration d'une autre base
python scripts/update_db_structure.py --db-path chemin/vers/base.db

# Désactiver les hints YAML (utiliser seulement REFERENCE_SCHEMA)
python scripts/update_db_structure.py --no-yaml-hints
```

**Options:**
- `--db-path PATH` : Chemin vers la base de données à migrer (défaut: `association.db`)
- `--no-yaml-hints` : Désactiver le chargement des hints YAML

**Sorties:**
- `[db-file].YYYYMMDD_HHMMSS.bak` - Sauvegarde timestampée de la base
- `reports/migration_report_{success|failed}_YYYYMMDD_HHMMSS.md` - Rapport détaillé de migration

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
### Table: `membres`
- [OK] Column: `prenom` (TEXT DEFAULT '') - Mapped from `prnom` (membres.prnom)
- [OK] Column: `email` (TEXT DEFAULT '') - Mapped from `emial` (membres.emial)

### Table: `config`
- [OK] Column: `but_asso` (TEXT DEFAULT '')
- [OK] Column: `cloture` (INTEGER DEFAULT 0)

## Column Mappings
- `membres.prnom` → `membres.prenom`
- `membres.emial` → `membres.email`

## Skipped Invalid Identifiers
- `table_name.invalid-column` (does not match SQL identifier pattern)

## Migration Log
[Logs détaillés de toutes les opérations]
```

**Mécanismes de sécurité:**
- **Sauvegarde automatique** : Une copie timestampée de la base est créée avant toute modification
- **Validation stricte** : Seuls les identifiants SQL valides (`^[A-Za-z_][A-Za-z0-9_]*$`) sont traités
- **Transactions** : Toutes les modifications sont groupées dans une transaction avec BEGIN/COMMIT
- **Rollback automatique** : En cas d'erreur, la transaction est annulée automatiquement
- **Restauration** : La sauvegarde est restaurée automatiquement si la migration échoue
- **Préservation des données** : Le fuzzy matching et RENAME/COPY préservent les données existantes
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

## Exemples de Migration

### Exemple 1: Renommage de colonne avec fuzzy matching

**Scénario:** Le code attend `prenom`, mais la base contient `prnom`

**Action (SQLite 3.25+):**
```sql
ALTER TABLE membres RENAME COLUMN prnom TO prenom
```

**Résultat:** Colonne renommée, données préservées, pas de duplication

### Exemple 2: Ajout avec copie de données

**Scénario:** Colonne `email` attendue, colonne similaire `emial` existe, mais RENAME pas supporté

**Action:**
```sql
ALTER TABLE membres ADD COLUMN email TEXT DEFAULT '';
UPDATE membres SET email = emial;
```

**Résultat:** Nouvelle colonne ajoutée, données copiées de la colonne similaire

### Exemple 3: Ajout simple

**Scénario:** Colonne `description` attendue, aucune colonne similaire n'existe

**Action:**
```sql
ALTER TABLE events ADD COLUMN description TEXT DEFAULT '';
```

**Résultat:** Nouvelle colonne ajoutée avec type inféré et valeur par défaut

---

## Tests

Des tests unitaires complets sont disponibles :

```bash
# Tester l'analyseur de modules (extraction SQL stricte)
python tests/test_analyze_modules.py

# Tester le système de migration intelligente (fuzzy matching, renommage)
python tests/test_smart_migration.py

# Tester les migrations de base (legacy)
python tests/test_database_migration.py

# Exécuter tous les tests
pytest tests/test_analyze_modules.py tests/test_smart_migration.py tests/test_database_migration.py
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
