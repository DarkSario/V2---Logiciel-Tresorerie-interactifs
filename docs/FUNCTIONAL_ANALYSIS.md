# Analyse Fonctionnelle Complète — Audit par Fonctionnalité

**Projet :** V2 - Logiciel Trésorerie Interactifs  
**Date :** 31 octobre 2025  
**Type :** Application desktop de gestion associative (Python + Tkinter + SQLite)

---

## 📋 Sommaire des Fonctionnalités

1. [Initialisation et Base de Données](#1-initialisation-et-base-de-données)
2. [Interface Principale et Point d'Entrée](#2-interface-principale-et-point-dentrée)
3. [Gestion des Membres](#3-gestion-des-membres)
4. [Gestion des Événements](#4-gestion-des-événements)
5. [Gestion du Stock](#5-gestion-du-stock)
6. [Module Buvette](#6-module-buvette)
7. [Gestion Financière](#7-gestion-financière)
8. [Journal Général et Comptabilité](#8-journal-général-et-comptabilité)
9. [Exports et Rapports](#9-exports-et-rapports)
10. [Dashboard et Tableaux de Bord](#10-dashboard-et-tableaux-de-bord)
11. [Clôture d'Exercice](#11-clôture-dexercice)
12. [Sauvegarde et Restauration](#12-sauvegarde-et-restauration)
13. [Utilitaires et Helpers](#13-utilitaires-et-helpers)
14. [Dialogues et UI](#14-dialogues-et-ui)
15. [Tests Unitaires](#15-tests-unitaires)
16. [Scripts et Migration](#16-scripts-et-migration)
17. [Workflows GitHub Actions](#17-workflows-github-actions)

---

## 1. Initialisation et Base de Données

### Description
Gestion de la base de données SQLite (`association.db`) incluant création de schéma, migrations et connexions.

### Points d'entrée
- **Fichiers principaux :**
  - `db/db.py` : module central de gestion DB
  - `init_db.py` : script d'initialisation (potentiellement redondant)
  - `main.py` (lignes 30-33) : détection et initialisation automatique au lancement

### Vérifications à effectuer
- ✅ Vérifier que `association.db` n'est **pas versionné** dans Git (risque de conflit/données sensibles)
- ✅ Confirmer que `.gitignore` contient `*.db`, `*.sqlite*`, `association.db`
- ✅ Vérifier la présence de `PRAGMA journal_mode=WAL` pour performances (ligne 38 de `db/db.py`)
- ✅ Contrôler la gestion des erreurs de connexion (try/except présent ligne 34-44)
- ✅ Vérifier que `timeout=10` est suffisant pour éviter les locks
- ✅ S'assurer que toutes les tables sont créées via `init_db()` au premier lancement
- ✅ Tester la fonction `upgrade_db_structure()` pour migrations non destructives
- ✅ Valider que `drop_tables()` affiche un avertissement clair avant suppression

### Risques potentiels
- 🔴 **CRITIQUE** : Fichiers `.db` potentiellement présents dans le repository (voir arborescence.txt lignes 3-5 : `association.db`, `association.db-shm`, `association.db-wal`)
- 🟠 **IMPORTANT** : Redondance entre `init_db.py` et `db/db.py` → risque de désynchronisation du schéma
- 🟡 **MOYEN** : Pas de vérification d'intégrité référentielle explicite dans toutes les tables
- 🟡 **MOYEN** : Logs de migration non sauvegardés pour audit

### Recommandations

#### 🔴 PRIORITÉ CRITIQUE
```bash
# Retirer les fichiers DB du repository
git rm --cached association.db association.db-shm association.db-wal

# Vérifier .gitignore (déjà présent mais confirmer)
cat .gitignore | grep -E '(\.db|association\.db)'

# Commit
git commit -m "Remove database files from version control"
```

#### 🟠 PRIORITÉ IMPORTANTE
- **Fusionner** `init_db.py` dans `db/db.py` ou clarifier leur rôle respectif
- Ajouter un fichier `docs/DATABASE_SCHEMA.md` documentant toutes les tables et colonnes
- Implémenter un système de versioning de schéma (ex: table `schema_version`)

#### 🟡 PRIORITÉ OPTIONNELLE
- Ajouter des contraintes `FOREIGN KEY ON DELETE CASCADE` explicites partout
- Logger toutes les migrations dans `logs/migrations.log`

---

## 2. Interface Principale et Point d'Entrée

### Description
Application Tkinter principale avec menu, barre de statut et navigation vers tous les modules.

### Points d'entrée
- **`main.py`** : classe `MainApp` (ligne 60)
  - Initialisation de l'UI (ligne 62-74)
  - Création du menu (méthode `create_menu`)
  - Gestion du statut de la DB (ligne 76-79)

### Vérifications à effectuer
- ✅ Vérifier que le titre de la fenêtre indique le fichier DB actif
- ✅ Contrôler l'affichage du dialogue `init_first_launch()` au premier démarrage
- ✅ Tester le changement dynamique de base de données via menu Administration
- ✅ Valider la fermeture propre de l'application (libération connexions DB)
- ✅ Vérifier la gestion des exceptions au niveau racine (decorateur `@handle_errors` ?)

### Risques potentiels
- 🟡 **MOYEN** : Pas de gestion explicite de `on_closing()` pour fermer proprement les connexions
- 🟡 **MOYEN** : Si plusieurs fenêtres `Toplevel` sont ouvertes, risque de fuites mémoire
- 🟢 **FAIBLE** : Taille de fenêtre non sauvegardée entre sessions

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
```python
# Ajouter dans MainApp.__init__()
self.protocol("WM_DELETE_WINDOW", self.on_closing)

def on_closing(self):
    """Fermeture propre : libérer connexions, logs."""
    try:
        conn = get_connection()
        conn.close()
    except:
        pass
    self.destroy()
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Sauvegarder taille/position fenêtre dans un fichier `config.json`
- Ajouter un système de thèmes (clair/sombre)

---

## 3. Gestion des Membres

### Description
Module de gestion des adhérents de l'association : contacts, cotisations, statuts.

### Points d'entrée
- **`modules/members.py`** : classe `MembersModule`
- **`dialogs/edit_member_dialog.py`** : dialogue d'édition

### Vérifications à effectuer
- ✅ Valider les champs email avec regex (`utils/validation.py`)
- ✅ Vérifier que les montants de cotisation sont positifs
- ✅ Contrôler les suppressions avec confirmation
- ✅ Tester l'export CSV des membres
- ✅ Valider l'unicité des emails (ou non selon règles métier)

### Risques potentiels
- 🟡 **MOYEN** : Pas de validation stricte du format email dans le dialogue
- 🟢 **FAIBLE** : Données sensibles (emails) non chiffrées en DB (acceptable pour SQLite local)

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Ajouter validation email obligatoire dans `edit_member_dialog.py` :
```python
from utils.validation import is_email
if email and not is_email(email):
    messagebox.showerror("Erreur", "Format d'email invalide")
    return
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Ajouter un champ "Date d'adhésion" pour historique
- Implémenter recherche/filtrage par nom/prénom/classe

---

## 4. Gestion des Événements

### Description
Module central pour organiser les manifestations avec modules dynamiques, recettes, dépenses, paiements et caisses.

### Points d'entrée
- **`modules/events.py`** : fenêtre principale des événements
- **`modules/event_modules.py`** : gestion des modules dynamiques associés
- **`modules/event_module_fields.py`** : définition des champs personnalisés
- **`modules/event_module_data.py`** : données des modules
- **`modules/event_recettes.py`** : recettes par événement
- **`modules/event_depenses.py`** : dépenses par événement
- **`modules/event_payments.py`** : paiements des participants
- **`modules/event_caisses.py`** + **`event_caisse_details.py`** : gestion multi-caisses

### Vérifications à effectuer
- ✅ Vérifier les clés étrangères `FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE`
- ✅ Contrôler que la suppression d'un événement supprime bien modules/recettes/dépenses associés
- ✅ Valider les montants positifs pour recettes et négatifs/positifs pour dépenses
- ✅ Tester l'intégrité des données avec modules dynamiques (table `event_module_data`)
- ✅ Vérifier la cohérence des caisses (solde = recettes - dépenses)

### Risques potentiels
- 🟠 **IMPORTANT** : Complexité élevée avec 8 tables liées → risque d'incohérences
- 🟡 **MOYEN** : Pas de transactions explicites pour opérations multi-tables
- 🟡 **MOYEN** : Possibilité de "double-comptage" entre event_recettes et event_caisses

### Recommandations

#### 🔴 PRIORITÉ CRITIQUE
- **Envelopper les opérations multi-tables dans des transactions :**
```python
conn = get_connection()
try:
    conn.execute("BEGIN TRANSACTION")
    # ... insertions/updates multiples ...
    conn.commit()
except Exception as e:
    conn.rollback()
    raise
```

#### 🟠 PRIORITÉ IMPORTANTE
- Créer une vue SQL `v_event_summary` calculant automatiquement solde par événement
- Ajouter des tests d'intégrité dans `tests/test_events.py`

#### 🟡 PRIORITÉ OPTIONNELLE
- Implémenter un système de "validation" d'événement (statut: brouillon/validé/clôturé)

---

## 5. Gestion du Stock

### Description
Suivi des articles, seuils d'alerte, mouvements, inventaires physiques.

### Points d'entrée
- **`modules/stock.py`** : module principal
- **`modules/mouvements_stock.py`** : entrées/sorties
- **`modules/inventaire.py`** + **`stock_inventaire.py`** : inventaires
- **`modules/stock_stats.py`** : statistiques
- **`modules/historique_inventaire.py`** : historique
- **`dialogs/edit_stock_dialog.py`**, **`inventaire_dialog.py`**

### Vérifications à effectuer
- ✅ Valider que les quantités en stock ne deviennent pas négatives
- ✅ Vérifier les seuils d'alerte et notifications
- ✅ Contrôler que les mouvements (entrées/sorties) mettent bien à jour le stock
- ✅ Tester la cohérence entre inventaire physique et stock théorique
- ✅ Valider les calculs de valorisation du stock (prix × quantité)

### Risques potentiels
- 🟠 **IMPORTANT** : Pas de gestion de transactions → risque de stock incohérent en cas d'erreur
- 🟡 **MOYEN** : Pas de traçabilité fine (qui a fait le mouvement, quand exactement)
- 🟢 **FAIBLE** : Pas de gestion de lots/péremption (selon besoin métier)

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Ajouter une contrainte `CHECK(quantite >= 0)` sur la table `stock`
- Implémenter un trigger SQLite pour empêcher stock négatif :
```sql
CREATE TRIGGER prevent_negative_stock
BEFORE UPDATE ON stock
FOR EACH ROW
WHEN NEW.quantite < 0
BEGIN
    SELECT RAISE(ABORT, 'Stock cannot be negative');
END;
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Ajouter colonnes `created_by`, `updated_by`, `updated_at` pour audit
- Implémenter notifications visuelles (badge rouge) pour articles sous seuil

---

## 6. Module Buvette

### Description
Gestion spécifique pour la buvette : articles, achats, inventaires, mouvements, recettes et bilans.

### Points d'entrée
- **`modules/buvette.py`** : module principal
- **`modules/buvette_db.py`**, **`buvette_inventaire_db.py`**, **`buvette_mouvements_db.py`** : accès DB
- **`modules/buvette_dialogs.py`**, **`buvette_inventaire_dialogs.py`**, **`buvette_mouvements_dialogs.py`** : UI
- **`modules/buvette_bilan_db.py`**, **`buvette_bilan_dialogs.py`** : bilans

### Vérifications à effectuer
- ✅ Vérifier que la colonne `stock` a bien été ajoutée (voir `db/db.py` ligne 6)
- ✅ Contrôler la cohérence entre achats, inventaires et stock disponible
- ✅ Valider les calculs de marge (prix vente - prix achat)
- ✅ Tester les mouvements de stock (approvisionnement, vente, casse)
- ✅ Vérifier l'export des bilans buvette

### Risques potentiels
- 🟠 **IMPORTANT** : Redondance avec module Stock général → risque de confusion
- 🟡 **MOYEN** : Migration de la colonne `stock` a été faite mais nécessite test sur DB existantes
- 🟡 **MOYEN** : Commentaires manquants dans certains inventaires (ajouté dans migration)

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- **Clarifier la relation Stock général vs Buvette** : documenter dans `docs/ARCHITECTURE.md`
- Tester la migration sur une copie de DB de production :
```bash
cp association.db association_test.db
python -c "from db.db import upgrade_db_structure; upgrade_db_structure()"
sqlite3 association_test.db "PRAGMA table_info(buvette_articles);"
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Fusionner modules Buvette et Stock si règles métier similaires
- Ajouter un dashboard spécifique buvette avec graphiques ventes

---

## 7. Gestion Financière

### Description
Suivi des finances de l'association : dons, subventions, dépenses régulières/diverses, dépôts/retraits bancaires, rétrocessions.

### Points d'entrée
- **`modules/dons_subventions.py`** : dons et subventions
- **`modules/depenses_regulieres.py`** : dépenses récurrentes
- **`modules/depenses_diverses.py`** : dépenses ponctuelles
- **`modules/depots_retraits_banque.py`** : mouvements bancaires
- **`modules/retrocessions_ecoles.py`** : redistribution aux écoles
- **`modules/solde_ouverture.py`** : solde initial exercice
- **`modules/fournisseurs.py`** : gestion fournisseurs
- **`dialogs/depense_dialog.py`**, **`edit_don_dialog.py`**

### Vérifications à effectuer
- ✅ Vérifier que tous les montants sont en `REAL` et positifs (sauf dépenses)
- ✅ Contrôler la somme des opérations = solde disponible
- ✅ Valider les dates au format ISO (YYYY-MM-DD)
- ✅ Tester les catégories de dépenses (table `categories`)
- ✅ Vérifier les exports comptables vers Excel/PDF

### Risques potentiels
- 🟡 **MOYEN** : Pas de rapprochement bancaire automatisé
- 🟡 **MOYEN** : Pas de calcul automatique du solde global (doit être recalculé)
- 🟢 **FAIBLE** : Pas de gestion multi-comptes bancaires (selon besoin)

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Créer une vue SQL calculant le solde global en temps réel :
```sql
CREATE VIEW v_solde_global AS
SELECT 
    (SELECT COALESCE(SUM(montant), 0) FROM dons_subventions)
    + (SELECT COALESCE(SUM(montant), 0) FROM event_recettes)
    - (SELECT COALESCE(SUM(montant), 0) FROM depenses_diverses)
    - (SELECT COALESCE(SUM(montant), 0) FROM depenses_regulieres)
    AS solde_calcule;
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Ajouter un module de rapprochement bancaire (import relevés CSV)
- Implémenter des alertes si solde < seuil défini

---

## 8. Journal Général et Comptabilité

### Description
Tenue du journal comptable général avec écritures, édition et consultation.

### Points d'entrée
- **`modules/journal.py`** : module principal du journal
- **`dialogs/edit_journal_dialog.py`** : édition d'écriture

### Vérifications à effectuer
- ✅ Vérifier que les écritures ont date, libellé, montant, type (débit/crédit)
- ✅ Contrôler l'équilibre débit = crédit pour écritures double
- ✅ Valider l'ordre chronologique des écritures
- ✅ Tester l'export du journal en CSV/PDF
- ✅ Vérifier la non-modification des écritures clôturées

### Risques potentiels
- 🟠 **IMPORTANT** : Pas de validation stricte débit=crédit pour comptabilité en partie double
- 🟡 **MOYEN** : Pas de numérotation automatique des écritures
- 🟡 **MOYEN** : Possibilité de modifier/supprimer écritures après clôture

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Ajouter une colonne `cloture` (BOOLEAN) dans table `journal`
- Bloquer modification si `cloture = 1` :
```python
if row["cloture"]:
    messagebox.showerror("Erreur", "Écriture clôturée, modification impossible")
    return
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Implémenter numérotation auto : `ECRITURE-2025-0001`
- Ajouter validation partie double (débit = crédit) avant enregistrement

---

## 9. Exports et Rapports

### Description
Extraction des données en CSV, Excel, PDF, archives ZIP pour audit et archivage.

### Points d'entrée
- **`modules/exports.py`** : fenêtre d'export principal
- **`exports/exports.py`** : fonctions export CSV/Excel/PDF
- **`exports/export_bilan_argumente.py`** : bilans argumentés
- **`utils/csv_helpers.py`**, **`utils/pdf_helpers.py`**, **`utils/zip_helpers.py`**

### Vérifications à effectuer
- ✅ Tester tous les formats d'export (CSV, Excel, PDF, ZIP)
- ✅ Vérifier l'encodage UTF-8 pour éviter problèmes d'accents
- ✅ Contrôler que les fichiers générés s'ouvrent correctement
- ✅ Valider les permissions de lecture/écriture sur dossier `exports/`
- ✅ Tester avec tables vides et tables volumineuses

### Risques potentiels
- 🟡 **MOYEN** : Dépendance optionnelle `reportlab` peut échouer silencieusement
- 🟡 **MOYEN** : Pas de nettoyage des anciens exports (accumulation fichiers)
- 🟢 **FAIBLE** : Noms de fichiers peuvent contenir espaces/caractères spéciaux

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
```python
# Vérifier reportlab au démarrage et afficher warning clair
try:
    import reportlab
except ImportError:
    logger.warning("reportlab non installé, exports PDF désactivés")
    messagebox.showwarning("Export PDF", "Installez reportlab: pip install reportlab")
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Implémenter nettoyage automatique des exports > 30 jours
- Sanitizer les noms de fichiers : remplacer espaces par `_`, supprimer caractères spéciaux

---

## 10. Dashboard et Tableaux de Bord

### Description
Synthèse visuelle avec graphiques, statistiques, opérations récentes, solde global.

### Points d'entrée
- **`dashboard/dashboard.py`** : module principal avec onglets (Résumé, Événements, Finances, Graphiques)

### Vérifications à effectuer
- ✅ Vérifier la présence de `matplotlib` (import ligne 5-11)
- ✅ Tester l'affichage sur différentes résolutions d'écran
- ✅ Valider les calculs de totaux (recettes, dépenses, solde)
- ✅ Contrôler les performances avec nombreuses données
- ✅ Tester le rafraîchissement après modification de données

### Risques potentiels
- 🟠 **IMPORTANT** : Dépendance `matplotlib` peut manquer (message d'erreur ligne 8-11)
- 🟡 **MOYEN** : Pas de cache des données → requêtes SQL à chaque ouverture
- �� **FAIBLE** : Graphiques peuvent être illisibles avec trop de données

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Vérifier `matplotlib` au démarrage de l'app (pas seulement au clic Dashboard)
- Ajouter bouton "Rafraîchir" visible dans chaque onglet

#### 🟡 PRIORITÉ OPTIONNELLE
- Implémenter mise en cache des données dashboard (TTL 5 min)
- Ajouter filtres par période (mois/trimestre/année)

---

## 11. Clôture d'Exercice

### Description
Processus de fin d'année : export complet, bilan PDF/Word, réinitialisation optionnelle de la base.

### Points d'entrée
- **`modules/cloture_exercice.py`** : module principal
- **`modules/historique_clotures.py`** : historique des clôtures
- **`dialogs/cloture_confirm_dialog.py`** : dialogue de confirmation
- **`utils/cloture_exercice.py`** : utilitaires clôture

### Vérifications à effectuer
- ✅ Vérifier le dialogue d'avertissement (opération IRRÉVERSIBLE, ligne 34)
- ✅ Tester l'export ZIP de toutes les tables
- ✅ Valider la génération des bilans PDF/Word
- ✅ Contrôler la sauvegarde historique avant réinitialisation
- ✅ Vérifier que l'utilisateur confirme explicitement

### Risques potentiels
- 🔴 **CRITIQUE** : Réinitialisation de la base sans sauvegarde préalable obligatoire
- 🟠 **IMPORTANT** : Pas de test de restauration automatique des sauvegardes
- 🟡 **MOYEN** : Historique des clôtures peut devenir volumineux

### Recommandations

#### 🔴 PRIORITÉ CRITIQUE
```python
# Forcer sauvegarde avant réinitialisation
def cloture_confirm(self):
    if not os.path.exists(f"backups/cloture_{datetime.now().strftime('%Y%m%d')}.bak"):
        messagebox.showerror("Erreur", "Créez d'abord une sauvegarde via 'Exporter en ZIP'")
        return
    # ... suite du processus
```

#### 🟠 PRIORITÉ IMPORTANTE
- Ajouter un test automatisé `test_cloture_restore.py` vérifiant la restauration
- Stocker hash SHA256 des sauvegardes pour vérifier intégrité

#### 🟡 PRIORITÉ OPTIONNELLE
- Implémenter archivage automatique des clôtures vers cloud (Google Drive, Dropbox)

---

## 12. Sauvegarde et Restauration

### Description
Mécanisme de backup/restore manuel de la base SQLite.

### Points d'entrée
- **`utils/backup_restore.py`** : fonctions principales
  - `backup_database()` : création `.bak` dans dossier `backups/`
  - `restore_database()` : restauration depuis `.bak`
  - `open_database()` : changement de base active

### Vérifications à effectuer
- ✅ Vérifier la création du dossier `backups/` si absent
- ✅ Tester la restauration complète d'une sauvegarde
- ✅ Contrôler les permissions fichiers (lecture/écriture)
- ✅ Valider la gestion des erreurs (fichier corrompu, espace disque)
- ✅ Vérifier que `.bak` n'est pas versionné (`.gitignore`)

### Risques potentiels
- 🟡 **MOYEN** : Pas de compression des sauvegardes (gzip)
- 🟡 **MOYEN** : Pas de rotation automatique (garder N dernières sauvegardes)
- 🟢 **FAIBLE** : Nom de fichier backup peut être écrasé si plusieurs backups le même jour

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Ajouter horodatage précis dans nom de fichier :
```python
backup_name = f"{base_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Compresser les backups avec gzip : `shutil.make_archive()`
- Implémenter rotation : garder 10 derniers backups, supprimer les plus anciens

---

## 13. Utilitaires et Helpers

### Description
Fonctions transverses : validation, logging, gestion erreurs, dates, notifications.

### Points d'entrée
- **`utils/validation.py`** : `is_email()`, `is_number()`, `is_integer()`, `is_required()`
- **`utils/app_logger.py`** : `get_logger()` → logs console + fichier `logs/app.log`
- **`utils/error_handler.py`** : `handle_exception()`, décorateur `@handle_errors`
- **`utils/date_helpers.py`** : manipulation dates
- **`utils/notify.py`** : notifications système
- **`utils/csv_helpers.py`**, **`pdf_helpers.py`**, **`zip_helpers.py`**

### Vérifications à effectuer
- ✅ Tester toutes les fonctions de validation avec cas limites
- ✅ Vérifier que les logs sont bien écrits dans `logs/app.log`
- ✅ Contrôler la rotation des logs (taille maximale)
- ✅ Valider le format des dates (ISO 8601)
- ✅ Tester les exports CSV avec caractères spéciaux (accents, guillemets)

### Risques potentiels
- 🟡 **MOYEN** : Pas de rotation automatique des logs → fichier peut grossir indéfiniment
- 🟡 **MOYEN** : Regex email simpliste dans `is_email()` (ligne 6 de test)
- 🟢 **FAIBLE** : Dossier `logs/` peut ne pas être créé automatiquement

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
```python
# Ajouter rotation logs dans app_logger.py
from logging.handlers import RotatingFileHandler
fh = RotatingFileHandler(
    os.path.join(log_dir, log_file),
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Améliorer regex email : `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Ajouter validation téléphone français : `is_phone_fr()`

---

## 14. Dialogues et UI

### Description
Dialogues réutilisables pour édition, saisie, confirmation.

### Points d'entrée
- **`dialogs/`** : 12 fichiers de dialogues
  - `edit_member_dialog.py`, `edit_event_dialog.py`, `edit_stock_dialog.py`
  - `edit_don_dialog.py`, `edit_journal_dialog.py`, `edit_module_dialog.py`
  - `depense_dialog.py`, `inventaire_dialog.py`, `cloture_confirm_dialog.py`
  - `add_row_dialog.py`, `edit_field_dialog.py`, `edit_module_data_dialog.py`
- **`ui/ui_utils.py`** : helpers UI génériques

### Vérifications à effectuer
- ✅ Vérifier que tous les dialogues appellent `transient(parent)` pour modalité
- ✅ Tester la validation des champs avant enregistrement
- ✅ Contrôler les messages d'erreur explicites
- ✅ Valider la fermeture avec touche Escape
- ✅ Vérifier l'accessibilité (focus clavier, tabulation)

### Risques potentiels
- 🟡 **MOYEN** : Code dupliqué entre dialogues (validation, layout)
- 🟢 **FAIBLE** : Pas de gestion de thèmes/styles centralisés

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
- Créer une classe `BaseDialog` factorisant le code commun :
```python
class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.bind("<Escape>", lambda e: self.destroy())
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Implémenter tooltips sur tous les champs de saisie
- Ajouter validation en temps réel (champs rouge si invalide)

---

## 15. Tests Unitaires

### Description
Tests pour validation des fonctionnalités critiques.

### Points d'entrée
- **`tests/test_utils.py`** : tests de validation (email, nombre, requis)
- **`tests/test_buvette_stock.py`** : tests module buvette stock
- **`tests/test_buvette_inventaire.py`** : tests inventaire buvette

### Vérifications à effectuer
- ✅ Exécuter tous les tests : `pytest tests/`
- ✅ Vérifier la couverture de code : `pytest --cov=modules --cov=utils`
- ✅ Tester les cas limites et erreurs
- ✅ Valider les mocks pour éviter modifications DB réelle
- ✅ S'assurer que les tests sont documentés

### Risques potentiels
- 🟠 **IMPORTANT** : Couverture de tests très faible (<20% estimé)
- 🟠 **IMPORTANT** : Pas de tests pour modules critiques (finances, clôture)
- 🟡 **MOYEN** : Tests buvette utilisent-ils une DB de test ou la vraie ?

### Recommandations

#### 🔴 PRIORITÉ CRITIQUE
```bash
# Créer tests critiques manquants
tests/
  test_finances.py       # Tests dons, dépenses, solde
  test_cloture.py        # Tests clôture et restauration
  test_events.py         # Tests événements et modules
  test_db_integrity.py   # Tests intégrité référentielle
```

#### 🟠 PRIORITÉ IMPORTANTE
- Configurer CI/CD GitHub Actions pour exécuter tests automatiquement
- Ajouter badge de couverture dans README.md

#### 🟡 PRIORITÉ OPTIONNELLE
- Utiliser `pytest-django` ou équivalent pour fixtures DB
- Implémenter tests de charge (1000+ événements)

---

## 16. Scripts et Migration

### Description
Scripts utilitaires pour maintenance et migration de schéma.

### Points d'entrée
- **`scripts/migration.py`** : système de migration de schéma
- **`lister_arborescence.py`** : génération de `arborescence.txt`

### Vérifications à effectuer
- ✅ Tester le script de migration sur DB vide et DB existante
- ✅ Vérifier que les migrations sont idempotentes (relançables)
- ✅ Contrôler les messages d'erreur si migration échoue
- ✅ Valider que `lister_arborescence.py` exclut `__pycache__`, `.git`

### Risques potentiels
- 🟡 **MOYEN** : Chemin DB hardcodé dans `migration.py` (ligne 14)
- 🟡 **MOYEN** : Pas de rollback automatique si migration échoue
- 🟢 **FAIBLE** : Script `lister_arborescence.py` inclut potentiellement fichiers sensibles

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
```python
# Utiliser variable d'environnement ou argument CLI
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--db", default=os.getenv("DB_PATH", "./association.db"))
args = parser.parse_args()
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Ajouter une table `migrations_applied` pour tracker migrations exécutées
- Implémenter commande `migration.py rollback` pour annuler dernière migration

---

## 17. Workflows GitHub Actions

### Description
Automatisation CI/CD pour création de PRs via patches ou branches existantes.

### Points d'entrée
- **`.github/workflows/Auto-Create-PR.yml`** : workflow manuel (`workflow_dispatch`)

### Vérifications à effectuer
- ✅ Tester les deux modes : `apply_patch` et `create_pr_from_branch`
- ✅ Vérifier que les permissions sont correctes (ligne 39-41)
- ✅ Contrôler la gestion d'erreurs (patch non trouvé, branche inexistante)
- ✅ Valider l'authentification GitHub Actions
- ✅ Tester avec des patches contenant des conflits

### Risques potentiels
- 🟡 **MOYEN** : Pas de validation du format du patch avant application
- 🟡 **MOYEN** : Erreur silencieuse si `git apply` échoue partiellement
- 🟡 **MOYEN** : Pas de CI/CD pour tests automatiques (build, lint, test)

### Recommandations

#### 🟠 PRIORITÉ IMPORTANTE
```yaml
# Ajouter workflow de tests automatiques
.github/workflows/tests.yml:
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov
```

#### 🟡 PRIORITÉ OPTIONNELLE
- Ajouter workflow de linting : `flake8`, `black --check`
- Implémenter workflow de release automatique avec tags

---

## 🎯 Plan d'Actions Proposé

### PR A : Sécurité et Gestion des Données (CRITIQUE)

**Priorité :** 🔴 CRITIQUE  
**Estimation :** 2-3 heures  
**Objectif :** Retirer données sensibles et sécuriser le repository

#### Commandes à exécuter

```bash
# 1. Retirer fichiers DB du repository
git rm --cached association.db association.db-shm association.db-wal 2>/dev/null || true
git add .gitignore

# 2. Vérifier .gitignore (normalement déjà correct)
echo "# Fichiers base de données" >> .gitignore
echo "*.db" >> .gitignore
echo "*.db-shm" >> .gitignore
echo "*.db-wal" >> .gitignore
echo "*.sqlite*" >> .gitignore
echo "association.db" >> .gitignore

# 3. Ajouter exemples de sauvegardes à ignorer
echo "" >> .gitignore
echo "# Sauvegardes et exports" >> .gitignore
echo "backups/" >> .gitignore
echo "*.bak" >> .gitignore
echo "exports/*.csv" >> .gitignore
echo "exports/*.xlsx" >> .gitignore
echo "exports/*.pdf" >> .gitignore
echo "exports/*.zip" >> .gitignore

# 4. Commit
git commit -m "security: Remove database files from version control

- Remove association.db and SQLite temporary files
- Update .gitignore to exclude database files
- Add backups/ and exports/ to .gitignore"
```

#### Fichiers à modifier

**`README.md`** : Ajouter section sécurité
```markdown
## ⚠️ Sécurité et Données

- **Ne jamais versionner** les fichiers `.db`, `.bak`, ou exports contenant des données personnelles
- Créer des sauvegardes régulières via le menu Administration
- Stocker les sauvegardes en lieu sûr (disque externe, cloud chiffré)
```

---

### PR B : Tests et Qualité du Code (IMPORTANT)

**Priorité :** 🟠 IMPORTANT  
**Estimation :** 4-6 heures  
**Objectif :** Améliorer couverture de tests et ajouter CI/CD

#### Fichiers à créer

**`.github/workflows/tests.yml`**
```yaml
name: Tests et Linting

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 black
      
      - name: Linting avec flake8
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      
      - name: Check formatting avec black
        run: black --check --diff .
      
      - name: Tests unitaires
        run: pytest tests/ -v --cov=modules --cov=utils --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**`tests/test_finances.py`** (nouveau)
```python
import unittest
from unittest.mock import Mock, patch
from modules.dons_subventions import DonsSubventionsModule

class TestFinances(unittest.TestCase):
    @patch('modules.dons_subventions.get_connection')
    def test_montant_positif(self, mock_conn):
        # Test que les montants négatifs sont rejetés
        mock_cur = Mock()
        mock_conn.return_value.cursor.return_value = mock_cur
        
        # TODO: implémenter test
        pass

if __name__ == "__main__":
    unittest.main()
```

**`tests/test_db_integrity.py`** (nouveau)
```python
import unittest
import sqlite3
from db.db import get_connection, init_db

class TestDatabaseIntegrity(unittest.TestCase):
    def setUp(self):
        # Utiliser DB de test
        self.test_db = "test_association.db"
        
    def test_foreign_keys_enabled(self):
        conn = get_connection()
        result = conn.execute("PRAGMA foreign_keys;").fetchone()
        self.assertEqual(result[0], 1, "Foreign keys should be enabled")
        conn.close()
    
    def test_cascade_delete_events(self):
        # Test que la suppression d'un event supprime ses modules
        pass

if __name__ == "__main__":
    unittest.main()
```

#### Améliorations code existant

**`db/db.py`** : Activer les contraintes FK
```python
def get_connection():
    try:
        conn = sqlite3.connect(_db_file, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")  # ← AJOUTER CETTE LIGNE
        return conn
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base: {e}")
        raise
```

**`utils/app_logger.py`** : Ajouter rotation logs
```python
from logging.handlers import RotatingFileHandler

def get_logger(name="app", log_level="INFO", log_file="app.log"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler avec rotation
        log_dir = "logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
            fh = RotatingFileHandler(
                os.path.join(log_dir, log_file),
                maxBytes=5*1024*1024,  # 5 MB
                backupCount=5,
                encoding='utf-8'
            )
            fh.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            pass
    return logger
```

---

### PR C : Documentation et Architecture (OPTIONNEL)

**Priorité :** 🟡 OPTIONNEL  
**Estimation :** 3-4 heures  
**Objectif :** Améliorer documentation technique et utilisateur

#### Fichiers à créer

**`docs/ARCHITECTURE.md`**
```markdown
# Architecture du Projet

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                     main.py (UI Tkinter)                 │
├─────────────────────────────────────────────────────────┤
│  Modules Métier                                          │
│  - members      - events        - stock                  │
│  - buvette      - finances      - journal                │
│  - exports      - dashboard     - cloture                │
├─────────────────────────────────────────────────────────┤
│  Dialogues UI (dialogs/)                                 │
├─────────────────────────────────────────────────────────┤
│  Utilitaires (utils/)                                    │
│  - validation   - logging       - backup/restore         │
│  - csv/pdf/zip helpers                                   │
├─────────────────────────────────────────────────────────┤
│  Accès Données (db/db.py)                                │
│  - Connexion SQLite    - Migrations    - Transactions    │
├─────────────────────────────────────────────────────────┤
│              association.db (SQLite)                      │
└─────────────────────────────────────────────────────────┘
```

## Principes

1. **Séparation UI / Métier / Données**
2. **Modules autonomes** : chaque module peut fonctionner indépendamment
3. **Validation centralisée** dans `utils/validation.py`
4. **Logging unifié** via `utils/app_logger.py`
5. **Base SQLite locale** : pas de serveur, portabilité maximale

## Schéma de Données

Voir `docs/DATABASE_SCHEMA.md` pour le détail des tables.

### Relations principales

- `events` ← `event_modules` ← `event_module_data`
- `events` ← `event_recettes`, `event_depenses`, `event_caisses`
- `stock` ← `mouvements_stock` ← `inventaires`
- `buvette_articles` (séparé du stock général)
```

**`docs/DATABASE_SCHEMA.md`**
```markdown
# Schéma de la Base de Données

## Table: events
Gestion des événements organisés par l'association.

| Colonne      | Type    | Contraintes       | Description                 |
|--------------|---------|-------------------|-----------------------------|
| id           | INTEGER | PRIMARY KEY AUTO  | Identifiant unique          |
| name         | TEXT    | NOT NULL          | Nom de l'événement          |
| date         | TEXT    | NOT NULL          | Date (format YYYY-MM-DD)    |
| lieu         | TEXT    |                   | Lieu de l'événement         |
| commentaire  | TEXT    |                   | Remarques                   |

## Table: members
Gestion des adhérents.

| Colonne      | Type    | Contraintes       | Description                 |
|--------------|---------|-------------------|-----------------------------|
| id           | INTEGER | PRIMARY KEY AUTO  | Identifiant unique          |
| name         | TEXT    | NOT NULL          | Nom                         |
| prenom       | TEXT    | NOT NULL          | Prénom                      |
| email        | TEXT    |                   | Email de contact            |
| classe       | TEXT    |                   | Classe/groupe               |
| cotisation   | REAL    |                   | Montant cotisation          |
| commentaire  | TEXT    |                   | Remarques                   |

## Table: stock
Gestion des articles en stock.

[... continuer pour toutes les tables principales ...]
```

**`docs/CONTRIBUTING.md`**
```markdown
# Guide de Contribution

## Prérequis

- Python 3.9+
- Git
- Éditeur avec support Python (VS Code, PyCharm)

## Installation environnement de développement

```bash
# Cloner le repo
git clone https://github.com/DarkSario/V2---Logiciel-Tresorerie-interactifs.git
cd V2---Logiciel-Tresorerie-interactifs

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
pip install pytest black flake8  # Outils dev

# Lancer l'application
python main.py
```

## Workflow de contribution

1. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
2. Coder et tester : `pytest tests/`
3. Formatter : `black .`
4. Linter : `flake8 .`
5. Commit : `git commit -m "feat: ajouter fonctionnalité X"`
6. Push : `git push origin feature/ma-fonctionnalite`
7. Ouvrir une PR sur GitHub

## Conventions

- **Noms de branches** : `feature/`, `fix/`, `docs/`, `refactor/`
- **Messages de commit** : `type: description` (feat, fix, docs, refactor, test)
- **Code** : PEP8, français pour commentaires/UI, anglais pour noms de variables
- **Tests** : ajouter test pour chaque nouvelle fonctionnalité

## Tests

```bash
# Tous les tests
pytest tests/

# Avec couverture
pytest tests/ --cov=modules --cov=utils

# Un fichier spécifique
pytest tests/test_utils.py -v
```
```

**`README.md`** : Ajouter badges
```markdown
# Gestion Association – Application Desktop

[![Tests](https://github.com/DarkSario/V2---Logiciel-Tresorerie-interactifs/actions/workflows/tests.yml/badge.svg)](https://github.com/DarkSario/V2---Logiciel-Tresorerie-interactifs/actions/workflows/tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[... reste du README existant ...]
```

---

## 📸 Annexes : Captures d'écran de contexte

Les captures suivantes illustrent les problématiques identifiées lors de l'audit :

### Capture 3 : Structure du projet et fichiers sensibles
![Capture 3](https://example.com/capture3.png)

**Observations :**
- Présence de fichiers `.db` dans l'arborescence
- Fichiers WAL (Write-Ahead Logging) SQLite également présents
- Risque de versioning de données sensibles

### Capture 2 : Configuration workflow GitHub Actions
![Capture 2](https://example.com/capture2.png)

**Observations :**
- Workflow manuel `Auto-Create-PR.yml` fonctionnel
- Permissions correctement définies
- Besoin d'ajouter workflow automatique pour tests

### Capture 1 : Vue globale du repository
![Capture 1](https://example.com/capture1.png)

**Observations :**
- Structure modulaire bien organisée
- Documentation existante mais incomplète
- Nécessité de clarifier certains modules (buvette vs stock)

---

## 🔍 Conclusion et Prochaines Étapes

### Points forts du projet

✅ **Architecture modulaire** bien séparée (UI / Métier / Données)  
✅ **Documentation utilisateur** présente (`docs/UTILISATEUR.md`)  
✅ **Système de logging** centralisé et fonctionnel  
✅ **Exports multiformats** (CSV, Excel, PDF, ZIP)  
✅ **Sauvegarde/restauration** implémentée  
✅ **Tests unitaires** de base présents  

### Axes d'amélioration prioritaires

🔴 **CRITIQUE** : Retirer fichiers base de données du repository (PR A)  
🟠 **IMPORTANT** : Améliorer couverture de tests et ajouter CI/CD (PR B)  
🟠 **IMPORTANT** : Activer contraintes FK et transactions (PR B)  
🟡 **OPTIONNEL** : Compléter documentation architecture (PR C)  
🟡 **OPTIONNEL** : Fusionner modules redondants (buvette/stock) (futur)  

### Validation et Suivi

Ce rapport doit être **relu et validé** par l'auteur du repository avant d'implémenter les PRs proposées.

**Checklist de validation :**

- [ ] Lire l'analyse complète et confirmer la compréhension
- [ ] Prioriser les PRs selon les besoins réels du projet
- [ ] Créer les issues GitHub correspondantes pour suivi
- [ ] Implémenter PR A (sécurité) en priorité
- [ ] Reviewer et merger les PRs une par une
- [ ] Mettre à jour cette analyse après chaque PR mergée

---

**Document généré le :** 31 octobre 2025  
**Auteur :** Agent d'analyse fonctionnelle automatisé  
**Version :** 1.0  
**Statut :** En attente de validation
