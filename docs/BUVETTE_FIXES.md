# Corrections du Module Buvette

## Vue d'ensemble

Ce document décrit les corrections automatiques appliquées au module buvette dans la PR `copilot/auto-fix-buvette`. Les modifications visent à résoudre les incohérences entre la structure de la base de données et le code, et à améliorer l'ergonomie des interfaces utilisateur.

## Problèmes identifiés et résolus

### 1. Gestion du stock des articles

**Problème**: Le module buvette n'avait pas de système pour suivre les quantités en stock de chaque article après les inventaires.

**Solution**:
- Ajout d'une colonne `stock` (INTEGER DEFAULT 0) à la table `buvette_articles`
- Création de fonctions utilitaires pour gérer le stock:
  - `ensure_stock_column()`: migration non destructive
  - `set_article_stock(article_id, stock)`: mise à jour du stock
  - `get_article_stock(article_id)`: récupération du stock actuel
- Mise à jour automatique du stock lors de l'enregistrement d'une ligne d'inventaire

### 2. Interface utilisateur du formulaire d'inventaire

**Problème**: Le champ "Type inventaire" utilisait un Entry libre, permettant des valeurs invalides et rendant la saisie peu ergonomique.

**Solution**:
- Remplacement du champ Entry par un Combobox avec les valeurs autorisées: `avant`, `apres`, `hors_evenement`
- Validation stricte du type d'inventaire lors de l'enregistrement
- Meilleur layout avec `columnconfigure` et `sticky='ew'` pour des champs extensibles

### 3. Cohérence des données

**Problème**: Les noms de colonnes dans le code ne correspondaient pas au schéma de la base de données (ex: `date` vs `date_mouvement`).

**Solution**:
- Les INSERT et UPDATE utilisent maintenant les noms corrects: `date_mouvement`, `type_mouvement`, `motif`
- Les SELECT ajoutent des alias (AS date, AS type, AS commentaire) pour maintenir la compatibilité avec l'UI existante

## Fichiers modifiés

### `db/db.py`
- Ajout de la colonne `stock` au schéma de `buvette_articles`
- Migration automatique dans `upgrade_db_structure()` pour les bases existantes
- Ajout de la colonne `commentaire` à `buvette_inventaire_lignes` si absente

### `modules/buvette_db.py`
- Fonction `ensure_stock_column()`: vérification et ajout de la colonne stock
- Fonction `set_article_stock(article_id, stock)`: mise à jour du stock d'un article
- Fonction `get_article_stock(article_id)`: récupération du stock actuel

### `modules/buvette.py`
- `InventaireDialog`: Combobox pour le type inventaire
- `InventaireDialog.save`: validation stricte du type
- `LigneInventaireDialog.save`: appel automatique de `set_article_stock()` après enregistrement
- `BuvetteModule.__init__`: appel de `ensure_stock_column()` au démarrage

### Tests
- `tests/test_buvette_stock.py`: 5 nouveaux tests pour la fonctionnalité de stock

## Tests

### Tests d'inventaire (7 tests)
- Insertion avec type valide (avant, apres, hors_evenement)
- Insertion avec type invalide (doit échouer)
- Mise à jour avec type valide
- Mise à jour avec type invalide (doit échouer)
- Liste des inventaires

### Tests de stock (5 tests)
- Création de la colonne stock dans une nouvelle table
- Insertion d'articles avec stock par défaut (0)
- Insertion d'articles avec stock explicite
- Mise à jour du stock
- Migration de la colonne sur une table existante

**Résultat**: ✅ 12/12 tests passent

## Rapport de vérification

Le script `scripts/check_buvette.py` effectue une analyse complète du module et confirme:
- ✅ Structure des fichiers correcte
- ✅ Schéma de base de données conforme
- ✅ Fonctions buvette_db.py correctes avec alias
- ✅ Interface utilisateur conforme
- ✅ Tous les tests unitaires passent

Voir `scripts/check_buvette_report.json` pour le rapport détaillé.

## Sécurité

✅ **Aucune vulnérabilité détectée** par CodeQL

## Migration

La migration est **non destructive**:
- Les données existantes sont préservées
- La colonne `stock` est ajoutée avec la valeur par défaut 0
- La colonne `unite` existante n'est pas supprimée
- La migration s'effectue automatiquement au démarrage du module buvette

## Validation manuelle recommandée

Bien que tous les tests automatisés passent, il est recommandé de valider manuellement:

1. **Ouverture du module buvette**
   - Vérifier que `ensure_stock_column()` s'exécute sans erreur
   - Vérifier qu'aucun message d'erreur n'apparaît

2. **Création d'un inventaire**
   - Ouvrir le dialog "Ajouter un inventaire"
   - Vérifier que le champ "Type inventaire" est un Combobox
   - Vérifier que les options sont: avant, apres, hors_evenement
   - Créer un inventaire de test

3. **Ajout d'une ligne d'inventaire**
   - Cliquer sur "Voir lignes" pour un inventaire
   - Ajouter une ligne avec un article existant
   - Saisir une quantité (ex: 50)
   - Vérifier que l'enregistrement réussit

4. **Vérification du stock**
   - Vérifier dans la base de données que la colonne `stock` existe
   - Vérifier que le stock de l'article a été mis à jour avec la quantité saisie

## Compatibilité

- ✅ Compatible avec les bases de données existantes (migration automatique)
- ✅ Compatible avec le code existant (aliases dans les SELECT)
- ✅ Pas de perte de données
- ✅ Pas de modification des interfaces existantes (sauf amélioration du Combobox)

## Notes de développement

### Comment utiliser la gestion du stock

```python
from modules.buvette_db import set_article_stock, get_article_stock, ensure_stock_column

# S'assurer que la colonne stock existe
ensure_stock_column()

# Mettre à jour le stock d'un article
set_article_stock(article_id=1, stock=50)

# Récupérer le stock actuel
stock = get_article_stock(article_id=1)
print(f"Stock actuel: {stock}")
```

### Structure de la table buvette_articles

```sql
CREATE TABLE buvette_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    categorie TEXT,
    unite TEXT,
    contenance TEXT,
    commentaire TEXT,
    stock INTEGER DEFAULT 0  -- NOUVELLE COLONNE
);
```

## Références

- Script de vérification: `scripts/check_buvette.py`
- Rapport JSON: `scripts/check_buvette_report.json`
- Tests: `tests/test_buvette_inventaire.py`, `tests/test_buvette_stock.py`
