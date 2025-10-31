# Documentation Log-Interactif-treso

## Présentation

**Log-Interactif-treso** est une application de gestion de trésorerie associative, conçue pour faciliter le suivi des recettes, dépenses, membres, événements et la génération de bilans argumentés.

---

## Table des matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Structure du code](#structure-du-code)
- [Tests](#tests)
- [Scripts et outils](#scripts-et-outils)
- [Export et rapports](#export-et-rapports)
- [Développement et contribution](#développement-et-contribution)

---

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/DarkSario/Log-Interactif-treso-V2.git
   cd Log-Interactif-treso-V2
   ```

2. **Créer un environnement virtuel (optionnel mais recommandé)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate sous Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer l’application via `.env` (voir `.env.example`)**
   - Adapter le chemin de la base (`DB_PATH`) et les variables de configuration si besoin.

---

## Lancement

```bash
python main.py
```

L’interface graphique s’ouvre, permettant la gestion des membres, recettes, dépenses, événements, etc.

---

## Fonctionnalités principales

- Gestion des membres (ajout, modification, cotisations, export)
- Saisie et édition d’événements, modules et lignes associées
- Saisie ultra-paramétrable des recettes/dépenses (y compris par module)
- Synthèse, tableau de bord graphique et exports multiples (Excel, PDF, Word)
- Génération de bilans argumentés automatisés et personnalisables
- Outils d’administration : clôture d’exercice, migration DB, scripts d’export en masse

---

## Structure du code

- `main.py` : point d’entrée de l’application
- `dialogs/` : boîtes de dialogue (saisie, édition, confirmation…)
- `dashboard/` : tableau de bord et synthèse visuelle
- `exports/` : scripts d’export (bilan, données brutes…)
- `db/` : accès et helpers base de données
- `utils/` : fonctions utilitaires (validation, erreurs…)
- `scripts/` : outils de migration, batchs, etc.
- `tests/` : tests unitaires

---

## Tests

- Les scripts de test sont dans le dossier `tests/`.
- Lancer tous les tests :
   ```bash
   python -m unittest discover tests
   ```

---

## Scripts et outils

- **Migration DB** : `python scripts/migration.py`
- **Export bilan argumenté** : depuis l’interface ou via `exports/export_bilan_argumene.py`
- **Autres exports** : voir `exports/exports.py`

---

## Export et rapports

- Export Excel/PDF/CSV des bilans, dépenses, subventions, etc.
- Génération d’un rapport PDF/Word argumenté pour chaque exercice.
- Export en lot de tous les bilans événements possible.

---

## Développement et contribution

- Forkez le projet et proposez vos améliorations via pull request.
- Respectez la structure existante et documentez vos ajouts.
- Pour toute question ou suggestion, ouvrez une issue sur le dépôt GitHub.

---

## Auteurs & Licence

Développé par [DarkSario](https://github.com/DarkSario)

Licence : MIT

---

## Pour aller plus loin

- Consultez les fichiers sources et commentaires pour comprendre la logique.
- Ajoutez vos propres modules ou scripts via la structure proposée.
- Personnalisez les exports (mises en page, tableaux…) selon vos besoins.

---

**Bon usage de Log-Interactif-treso !**