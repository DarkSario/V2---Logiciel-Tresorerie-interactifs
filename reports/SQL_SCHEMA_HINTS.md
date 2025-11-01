# Analyse SQL - Tables et Colonnes Detectees

Ce rapport liste toutes les tables et colonnes referencees dans le code Python.
Il sert de reference pour les migrations et la maintenance du schema de base de donnees.

**Nombre total de tables detectees:** 34

## Resume par Table

- **buvette_achats**: 7 colonnes, referencee dans 3 fichier(s)
- **buvette_articles**: 9 colonnes, referencee dans 4 fichier(s)
- **buvette_inventaire_lignes**: 5 colonnes, referencee dans 5 fichier(s)
- **buvette_inventaires**: 4 colonnes, referencee dans 3 fichier(s)
- **buvette_mouvements**: 6 colonnes, referencee dans 2 fichier(s)
- **buvette_recettes**: 2 colonnes, referencee dans 2 fichier(s)
- **categories**: 6 colonnes, referencee dans 2 fichier(s)
- **colonnes_modeles**: 7 colonnes, referencee dans 3 fichier(s)
- **comptes**: 4 colonnes, referencee dans 1 fichier(s)
- **config**: 6 colonnes, referencee dans 3 fichier(s)
- **depenses_diverses**: 14 colonnes, referencee dans 1 fichier(s)
- **depenses_regulieres**: 14 colonnes, referencee dans 1 fichier(s)
- **depots_retraits_banque**: 7 colonnes, referencee dans 1 fichier(s)
- **dons_subventions**: 6 colonnes, referencee dans 2 fichier(s)
- **event_caisse_details**: 6 colonnes, referencee dans 1 fichier(s)
- **event_caisses**: 7 colonnes, referencee dans 3 fichier(s)
- **event_depenses**: 12 colonnes, referencee dans 3 fichier(s)
- **event_module_data**: 6 colonnes, referencee dans 3 fichier(s)
- **event_module_fields**: 6 colonnes, referencee dans 4 fichier(s)
- **event_modules**: 4 colonnes, referencee dans 4 fichier(s)
- **event_payments**: 8 colonnes, referencee dans 1 fichier(s)
- **event_recettes**: 7 colonnes, referencee dans 3 fichier(s)
- **events**: 5 colonnes, referencee dans 7 fichier(s)
- **fournisseurs**: 1 colonnes, referencee dans 3 fichier(s)
- **historique_clotures**: 2 colonnes, referencee dans 1 fichier(s)
- **inventaire_lignes**: 8 colonnes, referencee dans 2 fichier(s)
- **inventaires**: 3 colonnes, referencee dans 1 fichier(s)
- **membres**: 9 colonnes, referencee dans 3 fichier(s)
- **mouvements_stock**: 11 colonnes, referencee dans 1 fichier(s)
- **retrocessions_ecoles**: 80 colonnes, referencee dans 2 fichier(s)
- **sqlite_master**: 1 colonnes, referencee dans 5 fichier(s)
- **stock**: 14 colonnes, referencee dans 5 fichier(s)
- **table_name**: 4 colonnes, referencee dans 1 fichier(s)
- **valeurs_modeles_colonnes**: 2 colonnes, referencee dans 3 fichier(s)

## Details des Tables et Colonnes

### Table: `buvette_achats`

**Colonnes detectees:**

- `article_id` (type infere: INTEGER)
- `date_achat` (type infere: DATE)
- `exercice` (type infere: TEXT)
- `facture` (type infere: TEXT)
- `fournisseur` (type infere: TEXT)
- `prix_unitaire` (type infere: REAL)
- `quantite` (type infere: REAL)

**Referencee dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_db.py`

---

### Table: `buvette_articles`

**Colonnes detectees:**

- `categorie` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `contenance` (type infere: REAL)
- `id` (type infere: INTEGER)
- `name` (type infere: TEXT)
- `purchase_price` (type infere: TEXT)
- `quantite` (type infere: REAL)
- `stock` (type infere: INTEGER)
- `unite` (type infere: TEXT)

**Referencee dans les fichiers:**

- `lib/db_articles.py`
- `modules/buvette_db.py`
- `modules/buvette_inventaire_dialogs.py`
- `modules/buvette_mouvements_db.py`

---

### Table: `buvette_inventaire_lignes`

**Colonnes detectees:**

- `article_id` (type infere: INTEGER)
- `commentaire` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `inventaire_id` (type infere: INTEGER)
- `quantite` (type infere: REAL)

**Referencee dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_db.py`
- `modules/buvette_inventaire_db.py`
- `ui/inventory_lines_dialog.py`

---

### Table: `buvette_inventaires`

**Colonnes detectees:**

- `commentaire` (type infere: TEXT)
- `date_inventaire` (type infere: DATE)
- `event_id` (type infere: INTEGER)
- `type_inventaire` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_inventaire_db.py`

---

### Table: `buvette_mouvements`

**Colonnes detectees:**

- `article_id` (type infere: INTEGER)
- `date_mouvement` (type infere: DATE)
- `event_id` (type infere: INTEGER)
- `motif` (type infere: TEXT)
- `quantite` (type infere: REAL)
- `type_mouvement` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/buvette_db.py`
- `modules/buvette_mouvements_db.py`

---

### Table: `buvette_recettes`

**Colonnes detectees:**

- `montant` (type infere: REAL)
- `recette` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`

---

### Table: `categories`

**Colonnes detectees:**

- `c` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `name` (type infere: TEXT)
- `p` (type infere: TEXT)
- `parent` (type infere: TEXT)
- `parent_id` (type infere: INTEGER)

**Referencee dans les fichiers:**

- `modules/categories.py`
- `modules/stock.py`

---

### Table: `colonnes_modeles`

**Colonnes detectees:**

- `id` (type infere: INTEGER)
- `master` (type infere: TEXT)
- `modele_id` (type infere: INTEGER)
- `name` (type infere: TEXT)
- `typ` (type infere: TEXT)
- `type_modele` (type infere: TEXT)
- `valeur` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/model_colonnes.py`

---

### Table: `comptes`

**Colonnes detectees:**

- `column` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `name` (type infere: TEXT)
- `solde` (type infere: REAL)

**Referencee dans les fichiers:**

- `db/db.py`

---

### Table: `config`

**Colonnes detectees:**

- `date` (type infere: DATE)
- `date_fin` (type infere: DATE)
- `disponible_banque` (type infere: REAL)
- `exercice` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `solde_report` (type infere: REAL)

**Referencee dans les fichiers:**

- `db/db.py`
- `modules/journal.py`
- `modules/solde_ouverture.py`

---

### Table: `depenses_diverses`

**Colonnes detectees:**

- `categorie` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `date_depense` (type infere: DATE)
- `fournisseur` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `membre_id` (type infere: INTEGER)
- `module_id` (type infere: INTEGER)
- `montant` (type infere: REAL)
- `moyen_paiement` (type infere: TEXT)
- `numero_cheque` (type infere: TEXT)
- `numero_facture` (type infere: TEXT)
- `paye_par` (type infere: TEXT)
- `statut_reglement` (type infere: TEXT)
- `statut_remboursement` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/depenses_diverses.py`

---

### Table: `depenses_regulieres`

**Colonnes detectees:**

- `categorie` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `date_depense` (type infere: DATE)
- `fournisseur` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `membre_id` (type infere: INTEGER)
- `module_id` (type infere: INTEGER)
- `montant` (type infere: REAL)
- `moyen_paiement` (type infere: TEXT)
- `numero_cheque` (type infere: TEXT)
- `numero_facture` (type infere: TEXT)
- `paye_par` (type infere: TEXT)
- `statut_reglement` (type infere: TEXT)
- `statut_remboursement` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/depenses_regulieres.py`

---

### Table: `depots_retraits_banque`

**Colonnes detectees:**

- `banque` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `date` (type infere: DATE)
- `montant` (type infere: REAL)
- `pointe` (type infere: TEXT)
- `reference` (type infere: TEXT)
- `type` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/depots_retraits_banque.py`

---

### Table: `dons_subventions`

**Colonnes detectees:**

- `date` (type infere: DATE)
- `id` (type infere: INTEGER)
- `justificatif` (type infere: TEXT)
- `montant` (type infere: REAL)
- `source` (type infere: TEXT)
- `type` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/dons_subventions.py`
- `modules/exports.py`

---

### Table: `event_caisse_details`

**Colonnes detectees:**

- `caisse_id` (type infere: INTEGER)
- `date` (type infere: DATE)
- `description` (type infere: TEXT)
- `justificatif` (type infere: TEXT)
- `montant` (type infere: REAL)
- `type_op` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/event_caisse_details.py`

---

### Table: `event_caisses`

**Colonnes detectees:**

- `commentaire` (type infere: TEXT)
- `event_id` (type infere: INTEGER)
- `id` (type infere: INTEGER)
- `nom` (type infere: TEXT)
- `nom_caisse` (type infere: TEXT)
- `responsable` (type infere: TEXT)
- `solde_initial` (type infere: REAL)

**Referencee dans les fichiers:**

- `modules/event_caisses.py`
- `modules/event_recettes.py`
- `modules/exports.py`

---

### Table: `event_depenses`

**Colonnes detectees:**

- `COALESCE` (type infere: TEXT)
- `categorie` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `date` (type infere: DATE)
- `date_depense` (type infere: DATE)
- `description` (type infere: TEXT)
- `event_id` (type infere: INTEGER)
- `fournisseur` (type infere: TEXT)
- `justificatif` (type infere: TEXT)
- `membre_id` (type infere: INTEGER)
- `montant` (type infere: REAL)
- `paye_par` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/event_depenses.py`
- `modules/events.py`
- `modules/exports.py`

---

### Table: `event_module_data`

**Colonnes detectees:**

- `field_id` (type infere: INTEGER)
- `id` (type infere: INTEGER)
- `module_id` (type infere: INTEGER)
- `mx` (type infere: TEXT)
- `row_index` (type infere: TEXT)
- `valeur` (type infere: REAL)

**Referencee dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_module_fields`

**Colonnes detectees:**

- `id` (type infere: INTEGER)
- `modele_colonne` (type infere: TEXT)
- `module_id` (type infere: INTEGER)
- `nom_champ` (type infere: TEXT)
- `prix_unitaire` (type infere: REAL)
- `type_champ` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_module_fields.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_modules`

**Colonnes detectees:**

- `event_id` (type infere: INTEGER)
- `id` (type infere: INTEGER)
- `id_col_total` (type infere: REAL)
- `nom_module` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_payments`

**Colonnes detectees:**

- `banque` (type infere: TEXT)
- `classe` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `event_id` (type infere: INTEGER)
- `mode_paiement` (type infere: TEXT)
- `montant` (type infere: REAL)
- `nom_payeuse` (type infere: TEXT)
- `numero_cheque` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/event_payments.py`

---

### Table: `event_recettes`

**Colonnes detectees:**

- `COALESCE` (type infere: TEXT)
- `commentaire` (type infere: TEXT)
- `event_id` (type infere: INTEGER)
- `id` (type infere: INTEGER)
- `module_id` (type infere: INTEGER)
- `montant` (type infere: REAL)
- `source` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/event_recettes.py`
- `modules/events.py`
- `modules/exports.py`

---

### Table: `events`

**Colonnes detectees:**

- `date` (type infere: DATE)
- `description` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `lieu` (type infere: TEXT)
- `name` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_inventaire_db.py`
- `modules/buvette_mouvements_db.py`
- `modules/events.py`
- `modules/exports.py`
- `modules/inventaire.py`

---

### Table: `fournisseurs`

**Colonnes detectees:**

- `name` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/fournisseurs.py`

---

### Table: `historique_clotures`

**Colonnes detectees:**

- `date_cloture` (type infere: DATE)
- `id` (type infere: INTEGER)

**Referencee dans les fichiers:**

- `modules/historique_clotures.py`

---

### Table: `inventaire_lignes`

**Colonnes detectees:**

- `c` (type infere: TEXT)
- `categorie` (type infere: TEXT)
- `inventaire_id` (type infere: INTEGER)
- `l` (type infere: TEXT)
- `name` (type infere: TEXT)
- `quantite_constatee` (type infere: REAL)
- `s` (type infere: TEXT)
- `stock_id` (type infere: INTEGER)

**Referencee dans les fichiers:**

- `modules/historique_inventaire.py`
- `modules/inventaire.py`

---

### Table: `inventaires`

**Colonnes detectees:**

- `commentaire` (type infere: TEXT)
- `date_inventaire` (type infere: DATE)
- `event_id` (type infere: INTEGER)

**Referencee dans les fichiers:**

- `modules/inventaire.py`

---

### Table: `membres`

**Colonnes detectees:**

- `commentaire` (type infere: TEXT)
- `cotisation` (type infere: TEXT)
- `date_adhesion` (type infere: DATE)
- `email` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `name` (type infere: TEXT)
- `prenom` (type infere: TEXT)
- `statut` (type infere: TEXT)
- `telephone` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/members.py`

---

### Table: `mouvements_stock`

**Colonnes detectees:**

- `commentaire` (type infere: TEXT)
- `date` (type infere: DATE)
- `date_peremption` (type infere: DATE)
- `id` (type infere: INTEGER)
- `m` (type infere: TEXT)
- `name` (type infere: TEXT)
- `prix_achat_total` (type infere: REAL)
- `prix_unitaire` (type infere: REAL)
- `quantite` (type infere: REAL)
- `s` (type infere: TEXT)
- `type` (type infere: TEXT)

**Referencee dans les fichiers:**

- `modules/mouvements_stock.py`

---

### Table: `retrocessions_ecoles`

**Colonnes detectees:**

- `article_id` (type infere: INTEGER)
- `banque` (type infere: TEXT)
- `but_asso` (type infere: TEXT)
- `caisse_id` (type infere: INTEGER)
- `categorie` (type infere: TEXT)
- `categorie_id` (type infere: INTEGER)
- `classe` (type infere: TEXT)
- `cloture` (type infere: INTEGER)
- `commentaire` (type infere: TEXT)
- `contenance` (type infere: TEXT)
- `cotisation` (type infere: TEXT)
- `date` (type infere: TEXT)
- `date_achat` (type infere: TEXT)
- `date_adhesion` (type infere: TEXT)
- `date_cloture` (type infere: TEXT)
- `date_depense` (type infere: TEXT)
- `date_fin` (type infere: TEXT)
- `date_inventaire` (type infere: TEXT)
- `date_mouvement` (type infere: TEXT)
- `date_peremption` (type infere: TEXT)
- `date_recette` (type infere: TEXT)
- `description` (type infere: TEXT)
- `disponible_banque` (type infere: REAL)
- `ecole` (type infere: TEXT)
- `email` (type infere: TEXT)
- `event_id` (type infere: INTEGER)
- `exercice` (type infere: TEXT)
- `facture` (type infere: TEXT)
- `field_id` (type infere: INTEGER)
- `fournisseur` (type infere: TEXT)
- `id` (type infere: INTEGER)
- `id_col_total` (type infere: INTEGER)
- `inventaire_id` (type infere: INTEGER)
- `justificatif` (type infere: TEXT)
- `lieu` (type infere: TEXT)
- `lot` (type infere: TEXT)
- `membre_id` (type infere: INTEGER)
- `mode_paiement` (type infere: TEXT)
- `modele_colonne` (type infere: TEXT)
- `modele_id` (type infere: INTEGER)
- `module_id` (type infere: INTEGER)
- `moment` (type infere: TEXT)
- `montant` (type infere: REAL)
- `motif` (type infere: TEXT)
- `moyen_paiement` (type infere: TEXT)
- `name` (type infere: TEXT)
- `nom_caisse` (type infere: TEXT)
- `nom_champ` (type infere: TEXT)
- `nom_module` (type infere: TEXT)
- `nom_payeuse` (type infere: TEXT)
- `numero_cheque` (type infere: TEXT)
- `numero_facture` (type infere: TEXT)
- `parent_id` (type infere: INTEGER)
- `paye_par` (type infere: TEXT)
- `pointe` (type infere: INTEGER)
- `prenom` (type infere: TEXT)
- `prix_achat_total` (type infere: REAL)
- `prix_unitaire` (type infere: REAL)
- `purchase_price` (type infere: REAL)
- `quantite` (type infere: INTEGER)
- `quantite_constatee` (type infere: INTEGER)
- `reference` (type infere: TEXT)
- `row_index` (type infere: INTEGER)
- `seuil_alerte` (type infere: INTEGER)
- `solde` (type infere: REAL)
- `solde_report` (type infere: REAL)
- `source` (type infere: TEXT)
- `statut` (type infere: TEXT)
- `statut_reglement` (type infere: TEXT)
- `statut_remboursement` (type infere: TEXT)
- `stock` (type infere: INTEGER)
- `stock_id` (type infere: INTEGER)
- `telephone` (type infere: TEXT)
- `type` (type infere: TEXT)
- `type_champ` (type infere: TEXT)
- `type_inventaire` (type infere: TEXT)
- `type_modele` (type infere: TEXT)
- `type_mouvement` (type infere: TEXT)
- `unite` (type infere: TEXT)
- `valeur` (type infere: REAL)

**Referencee dans les fichiers:**

- `db/db.py`
- `modules/retrocessions_ecoles.py`

---

### Table: `sqlite_master`

**Colonnes detectees:**

- `name` (type infere: TEXT)

**Referencee dans les fichiers:**

- `db/db.py`
- `scripts/migrate_add_purchase_price.py`
- `scripts/update_db_structure.py`
- `scripts/update_db_structure_old.py`
- `ui/startup_schema_check.py`

---

### Table: `stock`

**Colonnes detectees:**

- `c` (type infere: TEXT)
- `categorie` (type infere: TEXT)
- `categorie_id` (type infere: INTEGER)
- `commentaire` (type infere: TEXT)
- `date_peremption` (type infere: DATE)
- `id` (type infere: INTEGER)
- `lot` (type infere: TEXT)
- `name` (type infere: TEXT)
- `nb_articles` (type infere: TEXT)
- `quantite` (type infere: REAL)
- `s` (type infere: TEXT)
- `seuil_alerte` (type infere: TEXT)
- `stock_id` (type infere: INTEGER)
- `total_qte` (type infere: REAL)

**Referencee dans les fichiers:**

- `modules/categories.py`
- `modules/inventaire.py`
- `modules/stock.py`
- `modules/stock_inventaire.py`
- `modules/stock_stats.py`

---

### Table: `table_name`

**Colonnes detectees:**

- `col1` (type infere: TEXT)
- `col2` (type infere: TEXT)
- `col3` (type infere: TEXT)
- `pattern` (type infere: TEXT)

**Referencee dans les fichiers:**

- `scripts/analyze_modules_columns.py`

---

### Table: `valeurs_modeles_colonnes`

**Colonnes detectees:**

- `modele_id` (type infere: INTEGER)
- `valeur` (type infere: REAL)

**Referencee dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/model_colonnes.py`

---

