# Startup Schema Check - Visual Guide

This document provides a visual walkthrough of the startup schema check feature.

## Feature Overview

The startup schema check feature automatically validates the database schema when the application starts. If missing columns are detected, a user-friendly dialog appears offering to fix the issues automatically.

## User Experience Flow

### 1. Application Startup

When the user launches the application:

```
python main.py
```

The application:
1. Initializes the database if it doesn't exist
2. Checks if database file exists
3. **Automatically runs schema check** (new feature)
4. Continues to main window if no issues
5. **Shows alert dialog if columns are missing** (see below)

### 2. Schema Check Dialog (When Issues Found)

If the schema check detects missing columns, this modal dialog appears:

```
┌──────────────────────────────────────────────────────────────────┐
│  Vérification du schéma de base de données                    [X]│
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║  ⚠  Schéma de base de données incomplet                  ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                   │
│  Des colonnes attendues par le code sont absentes de la base    │
│  de données. Cela peut causer des erreurs lors de               │
│  l'utilisation de l'application.                                 │
│                                                                   │
│  Colonnes manquantes par table :                                 │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                          │▲   │
│  │  📋 Table: events                                        ││   │
│  │     • commentaire                                        ││   │
│  │     • description                                        ││   │
│  │     • lieu                                               ││   │
│  │                                                          ││   │
│  │  📋 Table: depenses_regulieres                          ││   │
│  │     • fournisseur                                        ││   │
│  │     • date_depense                                       ││   │
│  │     • paye_par                                           ││   │
│  │     • membre_id                                          ││   │
│  │     • statut_remboursement                               ││   │
│  │     • statut_reglement                                   ││   │
│  │     • moyen_paiement                                     ││   │
│  │     • numero_cheque                                      ││   │
│  │     • numero_facture                                     ││   │
│  │     • module_id                                          ││   │
│  │                                                          │▼   │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  💡 Recommandation : Il est fortement conseillé de mettre à     │
│  jour la base de données.                                        │
│  Une sauvegarde automatique sera créée avant toute              │
│  modification.                                                   │
│                                                                   │
│     ┌──────────────────────┐    ┌──────────────────────┐       │
│     │ Mettre à jour        │    │ Ignorer              │       │
│     │ maintenant          │    │ (non recommandé)     │       │
│     └──────────────────────┘    └──────────────────────┘       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Dialog Features:**
- ⚠️ Warning icon with clear title
- Scrollable list of tables and missing columns
- Recommendation message explaining the risk
- Two action buttons:
  - **"Mettre à jour maintenant"** (green) - Recommended action
  - **"Ignorer"** (gray) - Allows user to skip (not recommended)

### 3. User Clicks "Mettre à jour maintenant"

The dialog executes the migration process:

```
┌──────────────────────────────────────────────────────────────────┐
│  Mise à jour de la base de données...                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🔄 Exécution en cours...                                        │
│                                                                   │
│  ✓ Sauvegarde créée                                              │
│  ✓ Analyse du schéma                                             │
│  ✓ Ajout des colonnes manquantes                                 │
│  ✓ Optimisation de la base                                       │
│                                                                   │
│  Veuillez patienter...                                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 4. Success Dialog

After successful migration:

```
┌──────────────────────────────────────────────────────────────────┐
│  Succès                                                       [X]│
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ✅ Mise à jour de la base de données terminée avec succès !    │
│                                                                   │
│  Un rapport détaillé a été généré dans le répertoire scripts/.  │
│  Une sauvegarde de votre base a été créée automatiquement.      │
│                                                                   │
│  Voulez-vous ouvrir le rapport de migration ?                   │
│                                                                   │
│            ┌─────────┐            ┌─────────┐                   │
│            │   Oui   │            │   Non   │                   │
│            └─────────┘            └─────────┘                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

If user clicks "Oui", the migration report opens in the default text editor.

### 5. User Clicks "Ignorer"

If user chooses to ignore the missing columns:

```
┌──────────────────────────────────────────────────────────────────┐
│  Confirmation                                                 [X]│
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Êtes-vous sûr de vouloir ignorer cette mise à jour ?           │
│                                                                   │
│  Certaines fonctionnalités pourraient ne pas fonctionner        │
│  correctement.                                                   │
│                                                                   │
│            ┌─────────┐            ┌─────────┐                   │
│            │   Oui   │            │   Non   │                   │
│            └─────────┘            └─────────┘                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

This confirmation ensures the user understands the risk of ignoring the update.

### 6. Error Handling

If the migration fails:

```
┌──────────────────────────────────────────────────────────────────┐
│  Erreur                                                       [X]│
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ❌ La mise à jour a échoué.                                    │
│                                                                   │
│  Détails :                                                       │
│  [Error message truncated to 500 characters]                    │
│                                                                   │
│  Votre base de données a été restaurée depuis la sauvegarde     │
│  automatique. Aucune donnée n'a été perdue.                     │
│                                                                   │
│                        ┌──────┐                                  │
│                        │  OK  │                                  │
│                        └──────┘                                  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

Key features:
- Clear error message (truncated for security)
- Reassurance that backup was restored
- No data loss

## Manual Access via Menu

Users can also trigger the schema check manually:

```
Main Application Window
┌────────────────────────────────────────────────────────────────┐
│  Gestion Association Les Interactifs des Ecoles [association.db]│
├────────────────────────────────────────────────────────────────┤
│  Modules  Exports  Tableau de Bord  Journal  Administration ▼ │
│                                                        Quitter  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│        Les Interactifs des Ecoles                              │
│        Exercice en cours : 2024-2025 (Début : 2024-09-01)     │
│                                                                 │
│     ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│     │Événements│  │ Stock   │  │ Buvette │                     │
│     └─────────┘  └─────────┘  └─────────┘                     │
│     ...                                                         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

Administration Menu:
  ├─ Éditer exercice
  ├─ Solde d'ouverture bancaire
  ├─ Gestion des clôtures
  ├─ Sauvegarder la base...
  ├─ Restaurer la base...
  ├─ Ouvrir une autre base...
  ├─────────────────────────
  ├─ Réinitialiser les données
  └─ Mettre à jour la structure de la base  ← New feature
```

Clicking "Mettre à jour la structure de la base" shows:

```
┌──────────────────────────────────────────────────────────────────┐
│  Mise à jour                                                  [X]│
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Voulez-vous mettre à jour/adapter la structure de la base de   │
│  données ?                                                        │
│                                                                   │
│  Cette opération va :                                            │
│  - Créer une sauvegarde automatique timestampée                 │
│  - Ajouter les colonnes manquantes sans perte de données        │
│  - Optimiser la base de données (WAL mode)                      │
│  - Générer un rapport détaillé                                   │
│                                                                   │
│  Souhaitez-vous continuer ?                                      │
│                                                                   │
│            ┌─────────┐            ┌─────────┐                   │
│            │   Oui   │            │   Non   │                   │
│            └─────────┘            └─────────┘                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Generated Reports

### Migration Report (`scripts/migration_report_YYYYMMDD_HHMMSS.md`)

```markdown
# Database Migration Report

**Date:** 2025-11-01 11:23:37
**Database:** association.db
**Status:** SUCCESS
**Backup:** association.db.20251101_112337.bak

## Summary

- Tables requiring updates: 5
- Total columns added: 24

## Changes Applied

### Table: `events`

- Added column: `description` (TEXT DEFAULT '')

### Table: `event_modules`

- Added column: `id_col_total` (INTEGER)

...

## Migration Log

```
[2025-11-01 11:23:37] INFO: ============================================================
[2025-11-01 11:23:37] INFO: Database Structure Update - Safe Migration
[2025-11-01 11:23:37] INFO: ============================================================
[2025-11-01 11:23:37] INFO: Database: association.db
[2025-11-01 11:23:37] INFO: Creating backup: association.db.20251101_112337.bak
[2025-11-01 11:23:37] INFO: Backup created successfully
[2025-11-01 11:23:37] INFO: Processing table 'events': 1 column(s) to add
[2025-11-01 11:23:37] INFO:   ✓ Successfully added column 'description'
...
```
```

### Schema Analysis Report (`reports/SQL_SCHEMA_HINTS.md`)

```markdown
# Analyse SQL - Tables et Colonnes Détectées

Ce rapport liste toutes les tables et colonnes référencées dans le code Python.

**Nombre total de tables détectées:** 35

## Résumé par Table

- **events**: 68 colonnes, référencée dans 8 fichier(s)
- **depenses_regulieres**: 16 colonnes, référencée dans 1 fichier(s)
...

## Détails des Tables et Colonnes

### Table: `events`

**Colonnes détectées:**

- `id`
- `name`
- `date`
- `lieu`
- `commentaire`
- `description`

**Référencée dans les fichiers:**

- `modules/events.py`
- `db/db.py`
...
```

## Command Line Usage

For administrators who prefer the command line:

```bash
# Generate schema analysis
$ python scripts/analyze_modules_columns.py
============================================================
SQL Schema Analyzer - Module Column Detection
============================================================
Repository root: /path/to/project

Scanning modules...
Scanning ui...
Scanning scripts...
Scanning lib...
Scanning db...

Analysis complete. Found 35 tables.
Report generated: reports/SQL_SCHEMA_HINTS.md
============================================================

# Run migration manually
$ python scripts/update_db_structure.py --db-path association.db
[2025-11-01 11:23:37] INFO: ============================================================
[2025-11-01 11:23:37] INFO: Database Structure Update - Safe Migration
[2025-11-01 11:23:37] INFO: ============================================================
[2025-11-01 11:23:37] INFO: Database: association.db
[2025-11-01 11:23:37] INFO: Creating backup: association.db.20251101_112337.bak
[2025-11-01 11:23:37] INFO: Backup created successfully
...
[2025-11-01 11:23:37] INFO: Migration completed successfully!
[2025-11-01 11:23:37] INFO: ============================================================
```

## Safety Features Visualized

### Backup Creation

Before:
```
.
├── association.db (56KB)
└── reports/
```

After migration:
```
.
├── association.db (60KB) ← Updated
├── association.db.20251101_112337.bak (56KB) ← Backup
├── reports/
└── scripts/
    └── migration_report_20251101_112337.md ← Report
```

### Transaction Safety

```
Migration Flow:
┌────────────────────────────────────────┐
│ 1. Create Backup                       │
│    ✓ association.db.20251101.bak      │
└─────────────┬──────────────────────────┘
              │
┌─────────────▼──────────────────────────┐
│ 2. Begin Transaction                   │
│    BEGIN TRANSACTION;                  │
└─────────────┬──────────────────────────┘
              │
┌─────────────▼──────────────────────────┐
│ 3. Add Columns                         │
│    ALTER TABLE ... ADD COLUMN ...      │
│    ✓ events.description                │
│    ✓ events.lieu                       │
│    ✓ events.commentaire                │
└─────────────┬──────────────────────────┘
              │
         ┌────▼────┐
         │Success? │
         └────┬────┘
              │
        ┌─────┴─────┐
        │           │
    ┌───▼──┐    ┌───▼──┐
    │ Yes  │    │  No  │
    └───┬──┘    └───┬──┘
        │           │
┌───────▼──┐    ┌───▼────────┐
│ COMMIT;  │    │ ROLLBACK;  │
│          │    │ Restore    │
│ Optimize │    │ Backup     │
└──────────┘    └────────────┘
```

## User Benefits

1. **Automatic Detection**: No manual schema tracking needed
2. **One-Click Fix**: Simple UI to resolve issues
3. **Safe Operations**: Automatic backups before changes
4. **No Data Loss**: Rollback on error with backup restoration
5. **Detailed Reports**: Full audit trail of changes
6. **Idempotent**: Can run multiple times safely
7. **Zero Downtime**: WAL mode keeps app responsive

## Developer Benefits

1. **Schema Documentation**: Auto-generated from code
2. **Safe Migrations**: Tested rollback mechanism
3. **Audit Trail**: Detailed migration reports
4. **Easy Maintenance**: Update REFERENCE_SCHEMA to add columns
5. **Testing**: Comprehensive test suite included
6. **Security**: Multiple layers of validation

## Summary

The startup schema check feature provides a comprehensive, safe, and user-friendly way to keep the database schema in sync with the application code. It combines:

- **Automatic detection** at startup
- **Interactive UI** for user control
- **Safe migrations** with backups and rollback
- **Comprehensive reporting** for audit trails
- **Security controls** to prevent vulnerabilities

This ensures that users always have a working application with minimal manual intervention required.
