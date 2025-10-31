# Guide utilisateur – Gestion Association

## Prise en main

- **Lancement** : double-cliquez sur `main.py` ou utilisez `python main.py`
- **Initialisation** : au premier lancement, renseignez la période d’exercice et la trésorerie initiale
- **Accueil** : choisissez le module souhaité (Membres, Événements, Stock, etc.)

## Modules

### Membres

- Ajout, édition, suppression de membres
- Suivi des cotisations, statuts (président, trésorier, etc.)
- Export des listes

### Événements

- Création et gestion d’événements (nom, date, lieu, description)
- Modules personnalisés pour chaque événement (tableaux dynamiques)
- Recettes et dépenses propres à chaque événement
- Suivi des paiements, gestion des caisses

### Gestion du Stock

- Suivi des articles, seuils d’alerte, gestion des lots
- Mouvements de stock (entrées, sorties, inventaires)
- Statistiques par catégorie

### Finances

- Suivi des dons, subventions, dépenses régulières et diverses
- Historique des mouvements bancaires
- Journal général consultable et exportable

### Clôture d’exercice

- Export des données en archive ZIP
- Génération d’un bilan PDF
- Réinitialisation de la base pour un nouvel exercice

## Exports et sauvegardes

- Exports CSV, Excel, PDF accessibles depuis chaque module ou via le menu « Exports »
- Sauvegarde et restauration de la base via le menu « Administration »

## Conseils

- Effectuez régulièrement des sauvegardes de la base
- Utilisez l’export ZIP en fin d’exercice pour l’archivage
- Vous pouvez ouvrir une base différente via le menu « Administration »

## Questions fréquentes

- **Où sont stockées les données ?**  
  Localement dans le fichier `association.db` (ou un autre fichier SQLite si souhaité)
- **Peut-on utiliser l’appli sur plusieurs PC ?**  
  Oui, en copiant le fichier `.db` et en l’ouvrant via le menu dédié.
- **Comment restaurer un backup ?**  
  Menu « Administration » > Restaurer la base

---

Pour toute demande d’évolution, bug, ou aide : [ouvrir une issue GitHub](https://github.com/ton-repo/issues)