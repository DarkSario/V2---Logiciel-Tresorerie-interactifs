# Guide de Migration et Maintenance de la Base de Données

## Vue d'ensemble

Ce document décrit le système de vérification automatique du schéma de base de données et la procédure de migration sûre pour maintenir la base de données à jour avec les besoins du code.

## Fonctionnalités

### 1. Analyseur SQL Strict

Le système utilise un analyseur strict qui :

- ✅ **Extrait UNIQUEMENT les identifiants SQL valides** via regex `^[A-Za-z_][A-Za-z0-9_]*$`
- ✅ **Détecte les patterns SQL** : INSERT INTO, UPDATE SET, SELECT FROM
- ✅ **Ignore les tokens de code** : appels de fonction, texte UI, mots-clés Python
- ✅ **Génère des fichiers UTF-8** : `reports/SQL_SCHEMA_HINTS.md` et `db/schema_hints.yaml`
- ✅ **Rapporte les identifiants invalides** : collecte et documente les noms ignorés

### 2. Vérification automatique au démarrage

À chaque démarrage de l'application, le système :

1. **Charge les hints du fichier** `db/schema_hints.yaml` (ou génère si absent)
2. **Compare avec la base réelle** via `PRAGMA table_info`
3. **Propose des mappings fuzzy** pour les colonnes similaires (matching >= 75%)
4. **Présente une fenêtre modale** avec les changements proposés
5. **Requiert approbation utilisateur** avant toute modification

### 3. Mise à jour sûre avec mapping intelligent

Lorsque des colonnes manquantes sont détectées, l'utilisateur peut déclencher une mise à jour automatique qui :

- ✅ **Valide tous les identifiants** avec le pattern SQL strict
- ✅ **Ignore les noms invalides** et les documente dans le rapport
- ✅ **Matching fuzzy intelligent** : détecte les colonnes existantes similaires
- ✅ **Renommage sûr** : tente ALTER TABLE RENAME si supporté (SQLite 3.25+)
- ✅ **Fallback intelligent** : ADD + COPY si RENAME échoue
- ✅ **Crée une sauvegarde timestampée** (`association.db.YYYYMMDD_HHMMSS.bak`)
- ✅ **Exécute les migrations dans une transaction** (rollback en cas d'erreur)
- ✅ **Ajoute uniquement les colonnes manquantes** (pas de perte de données)
- ✅ **Active le mode WAL** pour de meilleures performances
- ✅ **Protection UTF-8 complète** : force l'encodage pour éviter les erreurs
- ✅ **Génère un rapport détaillé** dans `reports/` :
  - `migration_report_success_YYYYMMDD_HHMMSS.md` en cas de succès
  - `migration_report_failed_YYYYMMDD_HHMMSS.md` en cas d'échec
  - Inclut : environnement, opérations tentées, identifiants ignorés, traceback
- ✅ **Affiche automatiquement le rapport d'erreur** dans l'interface en cas d'échec
- ✅ **Restaure automatiquement la sauvegarde** en cas d'échec de migration
- ✅ **Est idempotent** (peut être exécuté plusieurs fois sans problème)

## Utilisation

### Workflow complet de migration

1. **Générer les hints** :
   ```bash
   python scripts/analyze_modules_columns.py
   ```
   Génère `reports/SQL_SCHEMA_HINTS.md` (lisible) et `db/schema_hints.yaml` (machine-readable).

2. **Réviser les hints** :
   Ouvrir `db/schema_hints.yaml` et vérifier que les colonnes détectées sont correctes.
   Supprimer manuellement les colonnes invalides si nécessaire.
   Ajouter des overrides manuels dans la section `manual_overrides` si besoin :
   ```yaml
   manual_overrides:
     table_name:
       column_aliases:
         old_name: new_name
       forced_types:
         column_name: REAL
   ```

3. **Tester sur une copie** :
   ```bash
   cp association.db association.db.test.bak
   python -u scripts/update_db_structure.py > reports/update_run.log 2>&1
   ```

4. **Inspecter les rapports** :
   - Vérifier `reports/migration_report_*.md`
   - Consulter la section "Skipped Invalid Identifiers"
   - Vérifier les "Column Mappings" pour les renommages/copies

5. **Appliquer en production** si les tests sont OK

### Vérification manuelle du schéma

Pour analyser le code et générer un rapport des tables/colonnes utilisées :

```bash
python scripts/analyze_modules_columns.py
```

Cela génère :
- `reports/SQL_SCHEMA_HINTS.md` - rapport lisible
- `db/schema_hints.yaml` - fichier de configuration pour les migrations

### Migration manuelle

Pour mettre à jour manuellement la structure de la base de données :

```bash
python scripts/update_db_structure.py --db-path association.db
```

**Note pour Windows et environnements non-UTF-8** : Si vous rencontrez des erreurs d'encodage (ex: `charmap codec can't encode character`), forcez l'encodage UTF-8 avant d'exécuter le script :

```powershell
# Windows PowerShell
$env:PYTHONIOENCODING = 'utf-8'
python -u scripts/update_db_structure.py --db-path association.db
```

```bash
# Linux/Mac (si nécessaire)
export PYTHONIOENCODING=utf-8
python -u scripts/update_db_structure.py --db-path association.db
```

Ou via le menu de l'application :
**Administration → Mettre à jour la structure de la base**

**Recommandation** : Utilisez Python 3.11+ qui offre une meilleure gestion des encodages sur toutes les plateformes.

### Vérification automatique au démarrage

La vérification est automatique et s'exécute à chaque lancement de l'application si le fichier `association.db` existe.

Si des colonnes manquent, une fenêtre s'affiche avec :
- 📋 Liste des tables et colonnes manquantes
- 🔄 Bouton "Mettre à jour maintenant" (recommandé)
- ⏭️ Bouton "Ignorer" (non recommandé)

## Procédure de Rollback

En cas de problème après une migration, vous pouvez restaurer la base de données depuis la sauvegarde automatique :

### Option 1 : Via l'interface

1. **Administration → Restaurer la base...**
2. Sélectionner le fichier de sauvegarde `.bak` approprié
3. Confirmer la restauration

### Option 2 : Manuellement

1. Fermer l'application
2. Localiser la sauvegarde : `association.db.YYYYMMDD_HHMMSS.bak`
3. Renommer ou supprimer `association.db`
4. Copier la sauvegarde et renommer en `association.db`
5. Redémarrer l'application

```bash
# Exemple sous Linux/Mac
cp association.db.20250101_143000.bak association.db

# Exemple sous Windows
copy association.db.20250101_143000.bak association.db
```

## Scripts et Modules

### `scripts/analyze_modules_columns.py`

**Rôle** : Analyseur SQL strict qui parcourt le code source et extrait UNIQUEMENT les identifiants SQL valides.

**Caractéristiques** :
- Utilise le pattern regex `^[A-Za-z_][A-Za-z0-9_]*$` pour valider les identifiants
- Extrait depuis INSERT INTO, UPDATE SET, SELECT FROM, CREATE TABLE
- Ignore les tokens de code, appels de fonction, texte UI
- Collecte les identifiants invalides dans une section dédiée du rapport

**Sortie** :
- `reports/SQL_SCHEMA_HINTS.md` - rapport lisible avec colonnes détectées et identifiants ignorés
- `db/schema_hints.yaml` - manifest YAML avec types inférés et section pour overrides manuels

**Utilisation** :
```bash
python scripts/analyze_modules_columns.py
```

### `scripts/compat_yaml.py`

**Rôle** : Loader de compatibilité pour `db/schema_hints.yaml`.

**Caractéristiques** :
- Tente d'utiliser PyYAML si disponible
- Sinon, utilise un parser simple pour le format produit par l'analyzeur
- Pas de dépendances externes requises (PyYAML optionnel)
- Expose `load_hints(path) -> dict`

**Utilisation** :
```python
from scripts.compat_yaml import load_hints
hints = load_hints('db/schema_hints.yaml')
```

### `scripts/update_db_structure.py`

**Rôle** : Script de migration sûre avec mapping fuzzy et validation stricte.

**Fonctionnalités** :
- Charge `db/schema_hints.yaml` via compat_yaml (ou génère si absent)
- Valide tous les noms de colonnes avec pattern SQL strict
- Ignore et rapporte les identifiants invalides
- Matching fuzzy (seuil >= 75%) pour détecter colonnes similaires
- Tente ALTER TABLE RENAME si supporté, sinon ADD + COPY
- Sauvegarde automatique avant modification
- Transaction avec rollback automatique en cas d'erreur
- Restauration automatique de la sauvegarde si échec
- Activation du mode WAL
- Génération de rapport détaillé dans `reports/`
- Affichage du chemin du rapport sur stdout pour intégration UI

**Utilisation** :
```bash
python scripts/update_db_structure.py [--db-path path/to/database.db]
```

**Code de sortie** :
- `0` : Succès (rapport dans `reports/migration_report_success_*.md`)
- `1` : Échec (rapport dans `reports/migration_report_failed_*.md`)

**Sortie** :
- Logs détaillés sur stdout/stderr
- Dernière ligne contient `REPORT_PATH:/chemin/vers/rapport.md`

### `ui/startup_schema_check.py`

**Rôle** : Module UI appelé au démarrage pour vérifier le schéma et proposer une mise à jour interactive.

**Fonctionnalités** :
- Compare schéma attendu vs réel
- Affiche une fenêtre modale en cas de différences
- Exécute `update_db_structure.py` si l'utilisateur accepte
- **Affiche automatiquement le rapport d'erreur** dans une fenêtre dédiée en cas d'échec
- **Affiche le rapport de succès** sur demande en cas de succès
- Permet d'ouvrir le fichier de rapport complet

**Intégration dans le code** :
```python
from ui import startup_schema_check

# Dans MainApp.__init__() ou au démarrage
startup_schema_check.run_check(root_window, "association.db")
```

**Fenêtre de rapport d'erreur** :
En cas d'échec de migration, une fenêtre `MigrationReportDialog` s'affiche automatiquement avec :
- ❌ Le contenu complet du rapport d'erreur
- 📋 Les détails des erreurs rencontrées
- 💡 Les actions recommandées
- 🔗 Un bouton pour ouvrir le fichier de rapport complet

## Schéma de Référence

Le schéma de référence est défini dans `scripts/update_db_structure.py` sous la forme d'un dictionnaire `REFERENCE_SCHEMA` :

```python
REFERENCE_SCHEMA = {
    "table_name": {
        "column_name": ("TYPE", "DEFAULT_VALUE"),
        ...
    },
    ...
}
```

Ce schéma est la source de vérité pour les migrations. Toute nouvelle colonne doit y être ajoutée.

## Bonnes Pratiques

### Pour les développeurs

1. **Toujours mettre à jour `REFERENCE_SCHEMA`** dans `update_db_structure.py` lors de l'ajout de nouvelles colonnes
2. **Tester les migrations** sur une copie de la base avant de les appliquer en production
3. **Documenter les changements** dans les rapports de migration
4. **Utiliser des valeurs par défaut appropriées** pour les nouvelles colonnes

### Pour les administrateurs

1. **Créer une sauvegarde manuelle** avant toute migration importante
2. **Vérifier les rapports de migration** après chaque mise à jour
3. **Conserver les sauvegardes automatiques** pendant au moins 30 jours
4. **Tester l'application** après une migration avant utilisation intensive

## Limitations

- Le système ne **crée pas de nouvelles tables** (seulement des colonnes)
- Le système ne **supprime pas de colonnes** (par sécurité)
- Le système ne **modifie pas les types de colonnes existantes**
- L'analyse du code est **heuristique** et peut manquer certaines références

## Dépannage

### La vérification automatique ne s'exécute pas

**Cause** : Le fichier `association.db` n'existe pas ou le module n'est pas importé.

**Solution** : Vérifier que le fichier existe et que `startup_schema_check` est importé dans `main.py`.

### La migration échoue

**Cause** : Base de données verrouillée, corruption, ou contrainte d'intégrité.

**Solution** :
1. Vérifier qu'aucune autre instance n'accède à la base
2. Consulter le rapport de migration pour les détails de l'erreur
3. Restaurer depuis la sauvegarde si nécessaire

### Colonnes détectées comme manquantes alors qu'elles existent

**Cause** : Décalage entre le schéma de référence et le code réel.

**Solution** :
1. Exécuter `analyze_modules_columns.py` pour générer un rapport à jour
2. Comparer avec `REFERENCE_SCHEMA` dans `update_db_structure.py`
3. Mettre à jour le schéma de référence si nécessaire

## Tests Manuels

### Test 1 : Migration réussie avec rapport

**Objectif** : Vérifier que la migration génère un rapport de succès dans `reports/`

**Procédure** :
1. Créer une base de données test avec des colonnes manquantes :
   ```bash
   sqlite3 test.db "CREATE TABLE config (id INTEGER, exercice TEXT);"
   ```
2. Exécuter la migration :
   ```bash
   python scripts/update_db_structure.py --db-path test.db
   ```
3. **Résultat attendu** :
   - Code de sortie : `0`
   - Fichier créé : `reports/migration_report_success_YYYYMMDD_HHMMSS.md`
   - Sortie contient : `REPORT_PATH:reports/migration_report_success_...`
   - Rapport contient : `**Status:** SUCCESS ✓`

### Test 2 : Migration échouée avec rapport d'erreur

**Objectif** : Vérifier que l'échec de migration génère un rapport d'erreur détaillé

**Procédure** :
1. Créer une base de données test avec des colonnes manquantes :
   ```bash
   sqlite3 test.db "CREATE TABLE config (id INTEGER, exercice TEXT);"
   ```
2. Rendre la base en lecture seule :
   ```bash
   chmod 444 test.db
   ```
3. Exécuter la migration :
   ```bash
   python scripts/update_db_structure.py --db-path test.db
   ```
4. **Résultat attendu** :
   - Code de sortie : `1`
   - Fichier créé : `reports/migration_report_failed_YYYYMMDD_HHMMSS.md`
   - Sortie contient : `REPORT_PATH:reports/migration_report_failed_...`
   - Rapport contient :
     - `**Status:** FAILED ✗`
     - `## Errors`
     - `## Recommended Actions`
     - Mention de la restauration de la sauvegarde

### Test 3 : Affichage automatique du rapport d'erreur dans l'UI

**Objectif** : Vérifier que l'interface affiche automatiquement le rapport en cas d'échec

**Procédure** :
1. Préparer une base avec colonnes manquantes comme Test 2
2. Lancer l'application :
   ```bash
   python main.py
   ```
3. Lorsque la fenêtre de vérification du schéma s'affiche, cliquer sur "Mettre à jour maintenant"
4. **Résultat attendu** :
   - Si l'échec se produit : une fenêtre `MigrationReportDialog` s'affiche automatiquement
   - En-tête rouge avec ❌
   - Contenu du rapport visible dans la zone de texte
   - Boutons "Ouvrir le fichier complet" et "Fermer"
   - Message indiquant que la base a été restaurée

### Test 4 : Affichage du rapport de succès dans l'UI

**Objectif** : Vérifier que l'utilisateur peut consulter le rapport de succès

**Procédure** :
1. Préparer une base avec colonnes manquantes (sans la rendre lecture seule)
2. Lancer l'application
3. Cliquer sur "Mettre à jour maintenant" dans la fenêtre de vérification
4. Lorsque le message de succès s'affiche, cliquer "Oui" pour consulter le rapport
5. **Résultat attendu** :
   - Fenêtre `MigrationReportDialog` s'affiche
   - En-tête vert avec ✅
   - Contenu du rapport de succès visible
   - Liste des colonnes ajoutées avec des ✓
   - Bouton pour ouvrir le fichier complet

### Test 5 : Idempotence - Exécution multiple

**Objectif** : Vérifier que la migration peut être exécutée plusieurs fois sans erreur

**Procédure** :
1. Créer une base test avec colonnes manquantes
2. Exécuter la migration une première fois (doit réussir)
3. Exécuter la migration une seconde fois sur la même base
4. **Résultat attendu** :
   - Les deux exécutions retournent code `0`
   - Deuxième rapport indique "No missing columns detected"
   - Aucune erreur levée sur les colonnes déjà existantes

## Test 6 : Buvette avec colonne manquante (Safe Access)

**Objectif** : Vérifier que le module buvette tolère les colonnes manquantes grâce au helper `_row_get_safe()`

**Procédure** :
1. Créer une base test avec table buvette_articles sans la colonne `purchase_price`:
   ```bash
   sqlite3 test.db "CREATE TABLE buvette_articles (id INTEGER PRIMARY KEY, name TEXT, categorie TEXT, unite TEXT, contenance TEXT, commentaire TEXT);"
   sqlite3 test.db "INSERT INTO buvette_articles (name, categorie) VALUES ('Test Article', 'Boissons');"
   ```
2. Lancer l'application et ouvrir le module Buvette
3. **Résultat attendu** :
   - La liste d'articles s'affiche correctement
   - Aucune erreur IndexError
   - Colonne "Prix achat/unité" reste vide pour les articles sans prix
   - Message d'erreur informatif si échec (avec suggestion de MAJ du schéma)

### Test 7 : Modification d'inventaire détaillé

**Objectif** : Vérifier que le bouton "Modifier" ouvre le dialogue détaillé en mode édition

**Procédure** :
1. Créer un inventaire détaillé avec plusieurs articles via "Nouvel inventaire détaillé"
2. Fermer le dialogue et sélectionner l'inventaire créé dans la liste
3. Cliquer sur le bouton "Modifier"
4. **Résultat attendu** :
   - Dialogue "Modifier inventaire détaillé" s'ouvre
   - Champs header (date, type, commentaire) sont pré-remplis
   - Liste d'articles est pré-chargée avec quantités actuelles
   - Modifications possibles : ajouter/supprimer articles, modifier quantités
   - Au clic sur "Enregistrer" : inventaire mis à jour (pas de duplication)
   - Message de confirmation : "Inventaire modifié avec succès!"

## Support

Pour toute question ou problème, consulter :
- Les rapports de migration dans `reports/migration_report_*.md`
- L'analyse du schéma dans `reports/SQL_SCHEMA_HINTS.md`
- Les logs de l'application

## Captures d'écran

### Interface de vérification au démarrage
Lorsque des colonnes manquantes sont détectées au démarrage, une fenêtre modale s'affiche :

![Fenêtre de vérification du schéma](../screenshots/schema_check_dialog.png)

### Fenêtre de rapport de migration
Après une migration, le rapport détaillé est accessible :

![Rapport de migration](../screenshots/migration_report_dialog.png)

### Interface d'inventaire détaillé
Le nouveau dialogue d'inventaire détaillé permet de créer/modifier des inventaires :

![Inventaire détaillé](../screenshots/detailed_inventory_dialog.png)

## Gestion de l'Encodage UTF-8

### Problématiques résolues

Les scripts de migration et d'analyse ont été conçus pour gérer correctement l'encodage UTF-8 :

1. **Forçage UTF-8 en Python** :
   ```python
   # Force UTF-8 encoding for stdout/stderr
   try:
       sys.stdout.reconfigure(encoding='utf-8')
       sys.stderr.reconfigure(encoding='utf-8')
   except Exception:
       pass
   ```

2. **Ouverture des fichiers** :
   Tous les fichiers sont ouverts avec `encoding='utf-8'` explicite :
   ```python
   with open(output_file, 'w', encoding='utf-8') as f:
       # ...
   ```

3. **Connexions SQLite** :
   Les connexions SQLite utilisent `sqlite3.Row` pour un accès sécurisé aux colonnes.

### Recommandations environnement

Pour éviter les problèmes d'encodage sur Windows ou dans des environnements non-UTF-8 :

**Windows PowerShell** :
```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -u scripts/analyze_modules_columns.py
python -u scripts/update_db_structure.py
```

**Linux/Mac (si nécessaire)** :
```bash
export PYTHONIOENCODING=utf-8
python -u scripts/analyze_modules_columns.py
python -u scripts/update_db_structure.py
```

**Python 3.11+** : Recommandé pour une meilleure gestion native de l'UTF-8 sur toutes les plateformes.

## Historique des Versions

### Version 2.2 (2025-11-01) - Smart Migration
- **Mapping intelligent** : fuzzy matching pour détecter les colonnes similaires (seuil 75%)
- **Renommage sûr** : ALTER TABLE RENAME COLUMN si SQLite 3.25+, sinon ADD + COPY
- **UI améliorée** : suppression du bouton "Ajouter" redondant dans inventaires
- **Row-to-dict conversion** : `_row_to_dict()` dans `inventory_lines_dialog.py` pour safe access
- **Documentation UTF-8** : instructions complètes pour gérer l'encodage
- **Fallback YAML** : `compat_yaml.py` fonctionne sans dépendance PyYAML

### Version 2.1 (2025-11-01)
- **Buvette safe access** : ajout du helper `_row_get_safe()` pour tolérer les colonnes manquantes
- **Inventaire edit mode** : bouton "Modifier" ouvre désormais le dialogue détaillé avec données pré-chargées
- **Support UPDATE inventaires** : `InventoryLinesDialog` supporte maintenant les modes INSERT et UPDATE
- **Gestion des lignes** : suppression des anciennes lignes et ré-insertion des nouvelles lors de la modification

### Version 2.0 (2025-01-02)
- **Rapports d'erreur détaillés** : génération systématique de rapports dans `reports/`
- **Affichage automatique des erreurs** : fenêtre dédiée pour les rapports d'erreur
- **Distinction succès/échec** : nommage des rapports selon le statut
- **Meilleure robustesse** : restauration automatique en cas d'échec
- **Tests améliorés** : 11 tests incluant les scénarios d'erreur

### Version 1.0 (2025-01-01)
- Implémentation initiale de la vérification automatique au démarrage
- Scripts d'analyse et de migration sûre
- Documentation complète
