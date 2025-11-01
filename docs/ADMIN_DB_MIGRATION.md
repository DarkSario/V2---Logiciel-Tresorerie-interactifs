# Guide de Migration et Maintenance de la Base de Données

## Vue d'ensemble

Ce document décrit le système de vérification automatique du schéma de base de données et la procédure de migration sûre pour maintenir la base de données à jour avec les besoins du code.

## Fonctionnalités

### 1. Vérification automatique au démarrage

À chaque démarrage de l'application, le système :

1. **Analyse le code** pour identifier toutes les tables et colonnes utilisées
2. **Compare avec la base réelle** via `PRAGMA table_info`
3. **Alerte l'utilisateur** si des colonnes manquent
4. **Propose une mise à jour sûre** ou de continuer sans modification

### 2. Mise à jour sûre de la structure

Lorsque des colonnes manquantes sont détectées, l'utilisateur peut déclencher une mise à jour automatique qui :

- ✅ **Crée une sauvegarde timestampée** (`association.db.YYYYMMDD_HHMMSS.bak`)
- ✅ **Exécute les migrations dans une transaction** (rollback en cas d'erreur)
- ✅ **Ajoute uniquement les colonnes manquantes** (pas de perte de données)
- ✅ **Active le mode WAL** pour de meilleures performances
- ✅ **Génère un rapport détaillé** (`scripts/migration_report_YYYYMMDD_HHMMSS.md`)
- ✅ **Est idempotent** (peut être exécuté plusieurs fois sans problème)

## Utilisation

### Vérification manuelle du schéma

Pour analyser le code et générer un rapport des tables/colonnes utilisées :

```bash
python scripts/analyze_modules_columns.py
```

Cela génère un rapport dans `reports/SQL_SCHEMA_HINTS.md`.

### Migration manuelle

Pour mettre à jour manuellement la structure de la base de données :

```bash
python scripts/update_db_structure.py --db-path association.db
```

Ou via le menu de l'application :
**Administration → Mettre à jour la structure de la base**

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

**Rôle** : Parcourt le code source (modules/, ui/, scripts/, lib/, db/) et extrait toutes les références aux tables et colonnes SQL via analyse regex.

**Sortie** : `reports/SQL_SCHEMA_HINTS.md` - rapport détaillé des tables et colonnes détectées.

**Utilisation** :
```bash
python scripts/analyze_modules_columns.py
```

### `scripts/update_db_structure.py`

**Rôle** : Script de migration sûre qui compare le schéma de référence (hardcodé dans le script) avec la base réelle et ajoute les colonnes manquantes.

**Fonctionnalités** :
- Sauvegarde automatique avant modification
- Transaction avec rollback automatique en cas d'erreur
- Restauration automatique de la sauvegarde si échec
- Activation du mode WAL
- Génération de rapport détaillé

**Utilisation** :
```bash
python scripts/update_db_structure.py [--db-path path/to/database.db]
```

**Code de sortie** :
- `0` : Succès
- `1` : Échec

### `ui/startup_schema_check.py`

**Rôle** : Module UI appelé au démarrage pour vérifier le schéma et proposer une mise à jour interactive.

**Fonctionnalités** :
- Compare schéma attendu vs réel
- Affiche une fenêtre modale en cas de différences
- Exécute `update_db_structure.py` si l'utilisateur accepte
- Propose d'ouvrir le rapport de migration

**Intégration dans le code** :
```python
from ui import startup_schema_check

# Dans MainApp.__init__() ou au démarrage
startup_schema_check.run_check(root_window, "association.db")
```

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

## Support

Pour toute question ou problème, consulter :
- Les rapports de migration dans `scripts/migration_report_*.md`
- L'analyse du schéma dans `reports/SQL_SCHEMA_HINTS.md`
- Les logs de l'application

## Historique des Versions

### Version 1.0 (2025-01-01)
- Implémentation initiale de la vérification automatique au démarrage
- Scripts d'analyse et de migration sûre
- Documentation complète
