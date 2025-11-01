# Guide de Migration de Base de Données

Ce guide explique comment utiliser les nouveaux outils de migration et d'analyse de la base de données.

## Vue d'ensemble

L'application dispose maintenant de deux outils puissants pour gérer la structure de la base de données :

1. **Analyseur de schéma** : Détecte automatiquement les tables et colonnes utilisées dans le code
2. **Migrateur sûr** : Ajoute les colonnes manquantes sans perte de données

## Pour les utilisateurs finaux

### Mettre à jour la structure de la base via l'interface

1. Ouvrez l'application
2. Menu **Administration** > **Mettre à jour la structure de la base**
3. Lisez la boîte de dialogue qui explique l'opération
4. Cliquez sur **Oui** pour confirmer
5. Un message vous informera du succès ou de l'échec
6. Un rapport détaillé sera généré dans le dossier `scripts/`

**Important** :
- Une sauvegarde automatique est créée avant toute modification
- Vos données ne seront jamais perdues
- L'opération peut prendre quelques secondes
- Vous pouvez exécuter cette opération plusieurs fois sans risque

### En cas de problème

Si la migration échoue :
1. L'application restaure automatiquement la sauvegarde
2. Consultez le rapport dans `scripts/migration_report_*.md`
3. Contactez le support technique avec ce rapport

## Pour les développeurs

### Analyser le schéma SQL

Pour obtenir un rapport de toutes les tables et colonnes utilisées dans le code :

```bash
python scripts/analyze_modules_columns.py
```

Résultat : `reports/SQL_SCHEMA_HINTS.md` avec la liste complète des tables et colonnes.

### Effectuer une migration

#### Via l'interface (recommandé)
Menu Administration > Mettre à jour la structure de la base

#### Via la ligne de commande
```bash
# Base par défaut (association.db)
python scripts/update_db_structure.py

# Autre base
python scripts/update_db_structure.py --db-path /chemin/vers/base.db
```

### Ajouter une nouvelle colonne au schéma

Lorsque vous ajoutez une nouvelle colonne dans le code :

1. **Modifiez `scripts/update_db_structure.py`** :

```python
REFERENCE_SCHEMA = {
    # ... tables existantes ...
    
    "ma_table": {
        # ... colonnes existantes ...
        "nouvelle_colonne": ("TEXT", "''"),  # Type et valeur par défaut
    },
}
```

2. **Types de colonnes supportés** :
   - `TEXT` : Texte, défaut recommandé `''`
   - `INTEGER` : Entier, défaut recommandé `0`
   - `REAL` : Nombre décimal, défaut recommandé `0.0`
   - Pour colonnes optionnelles : défaut `None`

3. **Testez la migration** :
```bash
# Créer une copie de test
cp association.db test.db

# Tester la migration
python scripts/update_db_structure.py --db-path test.db

# Vérifier le rapport
cat scripts/migration_report_*.md
```

4. **Déployez** :
   - Commitez les modifications
   - Les utilisateurs utiliseront le menu Administration pour migrer

### Workflow de développement

```bash
# 1. Développer la fonctionnalité avec nouvelle colonne
# 2. Ajouter la colonne au REFERENCE_SCHEMA
# 3. Analyser l'usage SQL
python scripts/analyze_modules_columns.py

# 4. Tester la migration
cp association.db test_migration.db
python scripts/update_db_structure.py --db-path test_migration.db

# 5. Vérifier que les tests passent
pytest tests/test_database_migration.py

# 6. Committer les modifications
git add scripts/update_db_structure.py
git commit -m "Add nouvelle_colonne to ma_table"
```

## Architecture technique

### Sauvegarde et sécurité

1. **Sauvegarde automatique** :
   - Format : `[db-file].YYYYMMDD_HHMMSS.bak`
   - Créée avant toute modification
   - Conserve l'intégrité complète de la base

2. **Transactions** :
   - Toutes les modifications sont groupées
   - Rollback automatique en cas d'erreur
   - Garantit la cohérence de la base

3. **Restauration automatique** :
   - Si la migration échoue, la sauvegarde est restaurée
   - Aucune intervention manuelle nécessaire

### Détection des colonnes manquantes

Le script compare :
- **Schéma de référence** : Défini dans `REFERENCE_SCHEMA`
- **Schéma actuel** : Obtenu via `PRAGMA table_info()`

Les colonnes présentes dans le schéma de référence mais absentes de la base sont ajoutées.

### Optimisations appliquées

Après une migration réussie :
1. **WAL mode** : `PRAGMA journal_mode=WAL`
   - Améliore la concurrence
   - Réduit les blocages

2. **Synchronous NORMAL** : `PRAGMA synchronous=NORMAL`
   - Équilibre entre performance et sécurité
   - Recommandé pour la plupart des usages

3. **ANALYZE** : `ANALYZE`
   - Optimise les requêtes
   - Met à jour les statistiques

## Exemples de rapports

### Rapport d'analyse SQL

```markdown
# Analyse SQL - Tables et Colonnes Détectées

**Nombre total de tables détectées:** 35

## Résumé par Table
- **membres**: 40 colonnes, référencée dans 3 fichier(s)
- **events**: 68 colonnes, référencée dans 8 fichier(s)
...

## Détails des Tables et Colonnes
### Table: `membres`
**Colonnes détectées:**
- `id`
- `name`
- `prenom`
- `email`
...
```

### Rapport de migration

```markdown
# Database Migration Report

**Date:** 2025-11-01 10:35:10
**Database:** association.db
**Status:** SUCCESS
**Backup:** association.db.20251101_103510.bak

## Summary
- Tables requiring updates: 5
- Total columns added: 24

## Changes Applied
### Table: `events`
- Added column: `description` (TEXT DEFAULT '')
...
```

## Dépannage avancé

### Restaurer manuellement une sauvegarde

```bash
# Identifier la sauvegarde
ls -lt *.bak | head -1

# Restaurer
cp association.db.20251101_103510.bak association.db
```

### Forcer la réanalyse de la base

```bash
sqlite3 association.db "ANALYZE;"
```

### Vérifier l'intégrité de la base

```bash
sqlite3 association.db "PRAGMA integrity_check;"
```

### Inspecter les colonnes d'une table

```bash
sqlite3 association.db "PRAGMA table_info(membres);"
```

## Limites connues

1. **Pas de modification de colonnes existantes** :
   - Le script ne modifie pas les colonnes existantes
   - Pour changer un type ou renommer : script de migration spécifique

2. **Pas de création de tables** :
   - Le script ajoute uniquement des colonnes
   - Les nouvelles tables doivent être créées manuellement ou via `init_db.py`

3. **Détection basée sur regex** :
   - L'analyseur peut manquer des références SQL complexes
   - Les requêtes dynamiques ne sont pas toujours détectées

## Support

Pour toute question ou problème :
1. Consultez les rapports générés
2. Vérifiez les logs dans le rapport de migration
3. Contactez l'équipe de développement avec :
   - Le rapport de migration
   - Le message d'erreur complet
   - La version de l'application

## Changelog

### Version 1.0 (2025-11-01)
- Première version des outils de migration
- Analyseur de schéma SQL
- Migrateur sûr avec sauvegarde automatique
- 16 tests unitaires
- Documentation complète
