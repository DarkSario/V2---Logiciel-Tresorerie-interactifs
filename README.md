# Gestion Association – Application Desktop

Un logiciel libre, multiplateforme, pour gérer la vie et la comptabilité d’une association scolaire ou équivalent.

## Fonctionnalités principales

- **Membres** : gestion des adhérents (contact, statut, cotisation)
- **Événements** : gestion des manifestations, modules dynamiques associés, recettes, dépenses, paiements, caisses
- **Finances** : suivi des dons, subventions, dépenses régulières/diverses, mouvements bancaires, journal général, clôture annuelle
- **Stock** : gestion des articles, seuils d’alerte, mouvements, inventaires, statistiques
- **Exports** : extraction de toutes les données en CSV, Excel, PDF ; création d’archives ZIP pour l’historique
- **Dashboard** : synthèse visuelle, graphiques, opérations récentes, solde global
- **Sauvegarde/Restauration** : manipulation aisée de la base SQLite, import/export

## Installation

1. Cloner ce dépôt
2. Installer les dépendances Python :
   ```sh
   pip install -r requirements.txt
   ```
3. (Optionnel) Pour l’export PDF :
   ```sh
   pip install reportlab
   ```
4. Lancer l’application :
   ```sh
   python main.py
   ```

## Structure du projet

| Dossier/fichier | Rôle |
|-----------------|------|
| `main.py` | Point d’entrée (UI principale) |
| `modules/` | Modules métiers (membres, événements, stock…) |
| `dialogs/` | Dialogues d’édition/saisie divers |
| `dashboard/` | Tableau de bord/statistiques |
| `exports/` | Fonctions d’export (CSV, Excel, PDF, ZIP) |
| `utils/` | Fonctions utilitaires (validation, logger, etc.) |
| `ui/` | Helpers d’UI génériques |
| `db/` | Accès et structure de la base SQLite |
| `tests/` | Tests unitaires |
| `docs/` | Documentation utilisateur |

## Sauvegarde et restauration

- Menu « Administration » : sauvegarde, restauration, ouverture d’une autre base
- Les données sont stockées localement dans un fichier SQLite (par défaut : `association.db`)

## Clôture d’exercice

- Permet d’exporter une archive ZIP de toutes les données, de générer un bilan PDF, puis de réinitialiser la base pour un nouvel exercice.

## Licence

MIT – projet libre, contributions bienvenues.

---

Pour plus de détails ou un guide utilisateur : voir [docs/UTILISATEUR.md](docs/UTILISATEUR.md)# Log-Interactif-treso-V2

Logiciel libre, multiplateforme, pour la gestion de la vie associative et la comptabilité d’une association scolaire ou équivalente.

---

## Fonctionnalités principales

- **Gestion des membres** : adhésions, contacts, cotisations, statuts, historiques
- **Événements** : gestion des manifestations, modules dynamiques, recettes/dépenses, paiements, caisses
- **Finances** : suivi des dons, subventions, dépenses régulières/diverses, mouvements bancaires, journal général, clôture annuelle
- **Stock** : gestion des articles et inventaires, seuils d’alerte, mouvements, statistiques
- **Exports** : extraction des données en CSV, Excel, PDF, ZIP de l’historique
- **Dashboard** : synthèse visuelle, graphiques, opérations récentes, solde global
- **Sauvegarde / Restauration** : manipulation facilitée de la base SQLite, import/export
- **Sécurité** : sauvegarde/restauration manuelle, changement de base, initialisation/effacement sécurisé

---

## Installation

### 1. Cloner le dépôt

```sh
git clone https://github.com/DarkSario/Log-Interactif-treso-V2.git
cd Log-Interactif-treso-V2
```

### 2. Installer les dépendances Python

**Python 3.9+ requis**

```sh
pip install -r requirements.txt
```

### 3. (Optionnel) Pour l’export PDF :

```sh
pip install reportlab
```

### 4. Lancer l’application

```sh
python main.py
```

---

## Structure du projet

| Dossier/fichier              | Rôle / Description                                           |
|------------------------------|-------------------------------------------------------------|
| `main.py`                    | Point d’entrée (UI principale)                              |
| `modules/`                   | Modules métier (membres, événements, stock, buvette…)       |
| `dialogs/`                   | Dialogues d’édition/saisie divers                           |
| `dashboard/dashboard.py`     | Tableau de bord, statistiques, synthèses visuelles          |
| `exports/`                   | Fonctions d’export (CSV, Excel, PDF, ZIP)                   |
| `utils/`                     | Fonctions utilitaires (logger, backup, helpers divers)      |
| `db/db.py`                   | Accès et structure de la base SQLite                        |
| `init_db.py`                 | (À fusionner/refactorer) Initiation de la base              |
| `tests/`                     | Tests unitaires et d’intégration                            |
| `docs/`                      | Documentation utilisateur et développeur                    |
| `arborescence.txt`           | Version textuelle de l’arbo du projet                       |
| `.env.example`               | Exemple de configuration (paramétrage avancé, chemins, etc.)|
| `requirements.txt`           | Dépendances Python du projet                                |
| `scripts/migration.py`       | (À créer) Script de migration de la base (MAJ structure)    |

---

## Démarrage rapide

1. **Premier lancement** : l’application crée et initialise automatiquement la base `association.db` si besoin.
2. **Navigation** : tous les modules sont accessibles via le menu principal ou la page d’accueil.
3. **Sauvegarde/Restauration** : menu « Administration » pour sauvegarder, restaurer, changer de base.
4. **Clôture d’exercice** : export ZIP complet + bilan PDF + réinitialisation guidée (optionnel).

---

## Contribution

- Respecter la structure de séparation logique métier / UI / DB / helpers
- Proposer un test unitaire pour chaque nouvelle fonctionnalité ou correction majeure
- Documenter toute nouvelle fonctionnalité ou module dans ce README et/ou dans `docs/`
- Merci de signaler tout bug ou suggestion via les issues GitHub

---

## Roadmap de refonte

Le projet est en cours de refonte : voir le fichier Excel `Plan_de_correction_Log-Interactif-treso-V2.xlsx` pour suivre l’avancement précis fichier par fichier.

---

## FAQ

**Q : Où sont stockées les données ?**  
R : Dans un fichier SQLite local (par défaut : `association.db`).

**Q : Puis-je changer de base de données ?**  
R : Oui, via le menu Administration.

**Q : La suppression ou la réinitialisation de la base est-elle risquée ?**  
R : Oui ! Toujours faire une sauvegarde via le menu avant une telle opération.

---

## Licence

Projet sous licence MIT.  
(C) 2025, Les Interactifs des Ecoles / DarkSario

---