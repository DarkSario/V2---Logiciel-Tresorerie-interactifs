# Analyse SQL - Tables et Colonnes Détectées

Ce rapport liste toutes les tables et colonnes référencées dans le code Python.
Il sert de référence pour les migrations et la maintenance du schéma de base de données.

**Nombre total de tables détectées:** 34

## Résumé par Table

- **buvette_achats**: 22 colonnes, référencée dans 3 fichier(s)
- **buvette_articles**: 14 colonnes, référencée dans 6 fichier(s)
- **buvette_inventaire_lignes**: 7 colonnes, référencée dans 5 fichier(s)
- **buvette_inventaires**: 10 colonnes, référencée dans 3 fichier(s)
- **buvette_mouvements**: 9 colonnes, référencée dans 2 fichier(s)
- **buvette_recettes**: 2 colonnes, référencée dans 2 fichier(s)
- **categories**: 28 colonnes, référencée dans 2 fichier(s)
- **colonnes_modeles**: 67 colonnes, référencée dans 3 fichier(s)
- **comptes**: 8 colonnes, référencée dans 1 fichier(s)
- **config**: 7 colonnes, référencée dans 3 fichier(s)
- **depenses_diverses**: 15 colonnes, référencée dans 1 fichier(s)
- **depenses_regulieres**: 15 colonnes, référencée dans 1 fichier(s)
- **depots_retraits_banque**: 21 colonnes, référencée dans 1 fichier(s)
- **dons_subventions**: 8 colonnes, référencée dans 2 fichier(s)
- **event_caisse_details**: 19 colonnes, référencée dans 1 fichier(s)
- **event_caisses**: 29 colonnes, référencée dans 3 fichier(s)
- **event_depenses**: 25 colonnes, référencée dans 3 fichier(s)
- **event_module_data**: 58 colonnes, référencée dans 3 fichier(s)
- **event_module_fields**: 18 colonnes, référencée dans 4 fichier(s)
- **event_modules**: 56 colonnes, référencée dans 4 fichier(s)
- **event_payments**: 23 colonnes, référencée dans 1 fichier(s)
- **event_recettes**: 22 colonnes, référencée dans 3 fichier(s)
- **events**: 63 colonnes, référencée dans 8 fichier(s)
- **fournisseurs**: 7 colonnes, référencée dans 3 fichier(s)
- **historique_clotures**: 5 colonnes, référencée dans 1 fichier(s)
- **inventaire_lignes**: 8 colonnes, référencée dans 2 fichier(s)
- **inventaires**: 6 colonnes, référencée dans 1 fichier(s)
- **membres**: 22 colonnes, référencée dans 3 fichier(s)
- **mouvements_stock**: 16 colonnes, référencée dans 1 fichier(s)
- **retrocessions_ecoles**: 95 colonnes, référencée dans 2 fichier(s)
- **sqlite_master**: 86 colonnes, référencée dans 4 fichier(s)
- **stock**: 30 colonnes, référencée dans 5 fichier(s)
- **tree**: 32 colonnes, référencée dans 0 fichier(s)
- **valeurs_modeles_colonnes**: 2 colonnes, référencée dans 3 fichier(s)

## Détails des Tables et Colonnes

### Table: `buvette_achats`

**Colonnes détectées:**

- `article_id` (type inféré: INTEGER)
- `bilan_txt` (type inféré: TEXT)
- `date_achat` (type inféré: DATE)
- `event_combo` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `events` (type inféré: TEXT)
- `evt_label` (type inféré: TEXT)
- `exercice` (type inféré: TEXT)
- `facture` (type inféré: TEXT)
- `fournisseur` (type inféré: TEXT)
- `frm_select` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `inv_apres` (type inféré: TEXT)
- `inv_avant` (type inféré: TEXT)
- `lignes_apres` (type inféré: TEXT)
- `lignes_avant` (type inféré: TEXT)
- `prix_unitaire` (type inféré: REAL)
- `qte` (type inféré: TEXT)
- `quantite` (type inféré: INTEGER)
- `recette` (type inféré: TEXT)
- `rows` (type inféré: TEXT)
- `total` (type inféré: REAL)

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_db.py`

---

### Table: `buvette_articles`

**Colonnes détectées:**

- `article` (type inféré: TEXT)
- `article_id` (type inféré: INTEGER)
- `categorie` (type inféré: TEXT)
- `columns` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `contenance` (type inféré: TEXT)
- `has_purchase_price` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `name` (type inféré: TEXT)
- `purchase_price` (type inféré: TEXT)
- `quantite` (type inféré: INTEGER)
- `rows` (type inféré: TEXT)
- `stock` (type inféré: INTEGER)
- `unite` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `lib/db_articles.py`
- `modules/buvette_db.py`
- `modules/buvette_inventaire_dialogs.py`
- `modules/buvette_mouvements_db.py`
- `scripts/migrate_add_purchase_price.py`
- `scripts/migration.py`

---

### Table: `buvette_inventaire_lignes`

**Colonnes détectées:**

- `article_id` (type inféré: INTEGER)
- `commentaire` (type inféré: TEXT)
- `cur` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `inventaire_id` (type inféré: INTEGER)
- `quantite` (type inféré: INTEGER)
- `rows` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_db.py`
- `modules/buvette_inventaire_db.py`
- `ui/inventory_lines_dialog.py`

---

### Table: `buvette_inventaires`

**Colonnes détectées:**

- `article_id` (type inféré: INTEGER)
- `commentaire` (type inféré: TEXT)
- `cur` (type inféré: TEXT)
- `date_inventaire` (type inféré: DATE)
- `event_id` (type inféré: INTEGER)
- `id` (type inféré: INTEGER)
- `inv_id` (type inféré: INTEGER)
- `inventaire_id` (type inféré: INTEGER)
- `rows` (type inféré: TEXT)
- `type_inventaire` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_inventaire_db.py`

---

### Table: `buvette_mouvements`

**Colonnes détectées:**

- `article_id` (type inféré: INTEGER)
- `date_mouvement` (type inféré: DATE)
- `event_id` (type inféré: INTEGER)
- `id` (type inféré: INTEGER)
- `inventaire_id` (type inféré: INTEGER)
- `motif` (type inféré: TEXT)
- `quantite` (type inféré: INTEGER)
- `rows` (type inféré: TEXT)
- `type_mouvement` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/buvette_db.py`
- `modules/buvette_mouvements_db.py`

---

### Table: `buvette_recettes`

**Colonnes détectées:**

- `SUM` (type inféré: TEXT)
- `recette` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`

---

### Table: `categories`

**Colonnes détectées:**

- `c.id` (type inféré: TEXT)
- `c.name` (type inféré: TEXT)
- `cat_id` (type inféré: INTEGER)
- `categorie_id` (type inféré: INTEGER)
- `commentaire` (type inféré: TEXT)
- `cur` (type inféré: TEXT)
- `date_peremption` (type inféré: DATE)
- `df_cat` (type inféré: TEXT)
- `form` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `item` (type inféré: TEXT)
- `lot` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `nb_children` (type inféré: TEXT)
- `nb_stock` (type inféré: INTEGER)
- `nom_entry` (type inféré: TEXT)
- `p.name` (type inféré: TEXT)
- `parent` (type inféré: TEXT)
- `parent_cb` (type inféré: TEXT)
- `parent_id` (type inféré: INTEGER)
- `parent_nom` (type inféré: TEXT)
- `parent_row` (type inféré: TEXT)
- `parent_var` (type inféré: TEXT)
- `quantite` (type inféré: INTEGER)
- `result` (type inféré: TEXT)
- `selected` (type inféré: TEXT)
- `seuil_alerte` (type inféré: INTEGER)
- `sticky` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/categories.py`
- `modules/stock.py`

---

### Table: `colonnes_modeles`

**Colonnes détectées:**

- `"INTEGER"` (type inféré: TEXT)
- `"REAL"]).pack(fill="x"` (type inféré: TEXT)
- `"Supprimer` (type inféré: TEXT)
- `"bold")).pack(anchor="w"` (type inféré: TEXT)
- `"bold")).pack(pady=8)` (type inféré: TEXT)
- `(modele_id` (type inféré: INTEGER)
- `(name` (type inféré: TEXT)
- `))` (type inféré: TEXT)
- `)).fetchall()` (type inféré: TEXT)
- `)).fetchone()["id"]` (type inféré: TEXT)
- `10` (type inféré: TEXT)
- `200)` (type inféré: TEXT)
- `6))` (type inféré: TEXT)
- `600)` (type inféré: TEXT)
- `?)"` (type inféré: TEXT)
- `anchor="w")` (type inféré: TEXT)
- `anchor="w").pack(side="left")` (type inféré: TEXT)
- `callback=None):` (type inféré: TEXT)
- `callback=self.refresh_list)` (type inféré: TEXT)
- `command=lambda` (type inféré: TEXT)
- `command=self.ajouter).pack(side="left"` (type inféré: TEXT)
- `command=self.destroy).pack(side="right"` (type inféré: TEXT)
- `command=top.destroy).pack(pady=8)` (type inféré: TEXT)
- `expand=True` (type inféré: TEXT)
- `font=("Arial"` (type inféré: TEXT)
- `height=15` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `master` (type inféré: TEXT)
- `master):` (type inféré: TEXT)
- `modele_id` (type inféré: INTEGER)
- `modele_id):` (type inféré: TEXT)
- `modele_id=None` (type inféré: TEXT)
- `modele_id=modele_id` (type inféré: INTEGER)
- `name` (type inféré: TEXT)
- `padx=10` (type inféré: TEXT)
- `padx=2)` (type inféré: TEXT)
- `padx=4)` (type inféré: TEXT)
- `padx=5` (type inféré: TEXT)
- `padx=8` (type inféré: TEXT)
- `padx=8)` (type inféré: TEXT)
- `pady=(0` (type inféré: TEXT)
- `pady=10)` (type inféré: TEXT)
- `pady=2` (type inféré: TEXT)
- `pady=8)` (type inféré: TEXT)
- `text="Ajouter` (type inféré: TEXT)
- `text="Fermer"` (type inféré: TEXT)
- `text="Modifier"` (type inféré: TEXT)
- `text="Modèles` (type inféré: TEXT)
- `text="Name` (type inféré: TEXT)
- `text="Supprimer"` (type inféré: TEXT)
- `text="Type` (type inféré: TEXT)
- `text="Valeurs` (type inféré: TEXT)
- `text="Voir` (type inféré: TEXT)
- `text=f"{c['name']}` (type inféré: TEXT)
- `textvariable=self.nom_var).pack(fill="x"` (type inféré: TEXT)
- `textvariable=self.type_var` (type inféré: TEXT)
- `txt)` (type inféré: TEXT)
- `typ` (type inféré: TEXT)
- `typ))` (type inféré: TEXT)
- `type_modele` (type inféré: TEXT)
- `type_modele)` (type inféré: TEXT)
- `v))` (type inféré: TEXT)
- `valeur` (type inféré: TEXT)
- `valeur)` (type inféré: TEXT)
- `valeurs):` (type inféré: TEXT)
- `values=["TEXT"` (type inféré: TEXT)
- `width=40)` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/model_colonnes.py`

---

### Table: `comptes`

**Colonnes détectées:**

- `("Banque` (type inféré: TEXT)
- `?)"` (type inféré: TEXT)
- `definition):` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `name` (type inféré: TEXT)
- `row["solde_report"]))` (type inféré: TEXT)
- `solde` (type inféré: REAL)
- `solde)` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `db/db.py`

---

### Table: `config`

**Colonnes détectées:**

- `MAX` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `date_fin` (type inféré: DATE)
- `disponible_banque` (type inféré: REAL)
- `exercice` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `solde_report` (type inféré: REAL)

**Référencée dans les fichiers:**

- `db/db.py`
- `modules/journal.py`
- `modules/solde_ouverture.py`

---

### Table: `depenses_diverses`

**Colonnes détectées:**

- `categorie` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `date_depense` (type inféré: DATE)
- `fournisseur` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `items` (type inféré: TEXT)
- `membre_id` (type inféré: INTEGER)
- `module_id` (type inféré: INTEGER)
- `montant` (type inféré: REAL)
- `moyen_paiement` (type inféré: TEXT)
- `numero_cheque` (type inféré: TEXT)
- `numero_facture` (type inféré: TEXT)
- `paye_par` (type inféré: TEXT)
- `statut_reglement` (type inféré: TEXT)
- `statut_remboursement` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`

---

### Table: `depenses_regulieres`

**Colonnes détectées:**

- `categorie` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `date_depense` (type inféré: DATE)
- `fournisseur` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `items` (type inféré: TEXT)
- `membre_id` (type inféré: INTEGER)
- `module_id` (type inféré: INTEGER)
- `montant` (type inféré: REAL)
- `moyen_paiement` (type inféré: TEXT)
- `numero_cheque` (type inféré: TEXT)
- `numero_facture` (type inféré: TEXT)
- `paye_par` (type inféré: TEXT)
- `statut_reglement` (type inféré: TEXT)
- `statut_remboursement` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/depenses_regulieres.py`

---

### Table: `depots_retraits_banque`

**Colonnes détectées:**

- `DISTINCT` (type inféré: TEXT)
- `banque` (type inféré: TEXT)
- `banques` (type inféré: TEXT)
- `c` (type inféré: TEXT)
- `cmb_type` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `ent_date` (type inféré: DATE)
- `ent_montant` (type inféré: REAL)
- `id` (type inféré: INTEGER)
- `id_` (type inféré: TEXT)
- `iid` (type inféré: TEXT)
- `index` (type inféré: TEXT)
- `item` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `new_val` (type inféré: TEXT)
- `pointe` (type inféré: TEXT)
- `reference` (type inféré: TEXT)
- `sticky` (type inféré: TEXT)
- `type` (type inféré: TEXT)
- `win` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/depots_retraits_banque.py`

---

### Table: `dons_subventions`

**Colonnes détectées:**

- `date` (type inféré: DATE)
- `id` (type inféré: INTEGER)
- `items` (type inféré: TEXT)
- `justificatif` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `row_factory` (type inféré: TEXT)
- `source` (type inféré: TEXT)
- `type` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/dons_subventions.py`
- `modules/exports.py`

---

### Table: `event_caisse_details`

**Colonnes détectées:**

- `caisse_id` (type inféré: INTEGER)
- `date` (type inféré: DATE)
- `date_var` (type inféré: DATE)
- `desc` (type inféré: TEXT)
- `desc_var` (type inféré: TEXT)
- `description` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `justif` (type inféré: TEXT)
- `justif_var` (type inféré: TEXT)
- `justificatif` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `montant_float` (type inféré: REAL)
- `montant_var` (type inféré: REAL)
- `op` (type inféré: TEXT)
- `operation_id` (type inféré: INTEGER)
- `typ` (type inféré: TEXT)
- `type_op` (type inféré: TEXT)
- `type_ops` (type inféré: TEXT)
- `type_var` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_caisse_details.py`

---

### Table: `event_caisses`

**Colonnes détectées:**

- `btn_frame` (type inféré: TEXT)
- `caisse` (type inféré: TEXT)
- `caisse_id` (type inféré: INTEGER)
- `cid` (type inféré: TEXT)
- `columns` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `exist` (type inféré: TEXT)
- `fond_debut` (type inféré: TEXT)
- `fond_fin` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `moment` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `nom` (type inféré: TEXT)
- `nom_caisse` (type inféré: TEXT)
- `nom_var` (type inféré: TEXT)
- `r` (type inféré: TEXT)
- `recettes` (type inféré: TEXT)
- `resp` (type inféré: TEXT)
- `resp_var` (type inféré: TEXT)
- `responsable` (type inféré: TEXT)
- `show` (type inféré: TEXT)
- `solde` (type inféré: REAL)
- `solde_float` (type inféré: REAL)
- `solde_initial` (type inféré: REAL)
- `solde_var` (type inféré: REAL)
- `source` (type inféré: TEXT)
- `tree` (type inféré: TEXT)
- `type` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_caisses.py`
- `modules/event_recettes.py`
- `modules/exports.py`

---

### Table: `event_depenses`

**Colonnes détectées:**

- `0` (type inféré: TEXT)
- `COALESCE` (type inféré: TEXT)
- `categorie` (type inféré: TEXT)
- `categorie_var` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `date_depense` (type inféré: DATE)
- `date_var` (type inféré: DATE)
- `dep` (type inféré: TEXT)
- `depense_id` (type inféré: INTEGER)
- `desc` (type inféré: TEXT)
- `desc_var` (type inféré: TEXT)
- `description` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `fournisseur` (type inféré: TEXT)
- `fournisseur_var` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `justif` (type inféré: TEXT)
- `justif_var` (type inféré: TEXT)
- `justificatif` (type inféré: TEXT)
- `membre_id` (type inféré: INTEGER)
- `montant` (type inféré: REAL)
- `montant_float` (type inféré: REAL)
- `montant_var` (type inféré: REAL)
- `paye_par` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_depenses.py`
- `modules/events.py`
- `modules/exports.py`

---

### Table: `event_module_data`

**Colonnes détectées:**

- `FocusOut` (type inféré: TEXT)
- `MAX` (type inféré: TEXT)
- `Return` (type inféré: TEXT)
- `ch` (type inféré: TEXT)
- `choix` (type inféré: TEXT)
- `col` (type inféré: TEXT)
- `col_idx` (type inféré: TEXT)
- `columns` (type inféré: TEXT)
- `dlg` (type inféré: TEXT)
- `dlg_prix` (type inféré: REAL)
- `e` (type inféré: TEXT)
- `editing_entry` (type inféré: TEXT)
- `entry` (type inféré: TEXT)
- `field` (type inféré: TEXT)
- `field_id` (type inféré: INTEGER)
- `fields` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `id_col` (type inféré: INTEGER)
- `id_col_total` (type inféré: REAL)
- `idx` (type inféré: TEXT)
- `iid` (type inféré: TEXT)
- `implémentée` (type inféré: TEXT)
- `initialvalue` (type inféré: TEXT)
- `modele_colonne` (type inféré: TEXT)
- `modele_id` (type inféré: INTEGER)
- `module_id` (type inféré: INTEGER)
- `name` (type inféré: TEXT)
- `new_price` (type inféré: TEXT)
- `new_value` (type inféré: TEXT)
- `next_idx` (type inféré: TEXT)
- `next_row` (type inféré: TEXT)
- `old_price` (type inféré: TEXT)
- `parent` (type inféré: TEXT)
- `parent_dir` (type inféré: TEXT)
- `prix` (type inféré: REAL)
- `prix_unitaire` (type inféré: REAL)
- `qte` (type inféré: TEXT)
- `region` (type inféré: TEXT)
- `res` (type inféré: TEXT)
- `res_total` (type inféré: REAL)
- `row_idx` (type inféré: TEXT)
- `row_index` (type inféré: TEXT)
- `row_values` (type inféré: TEXT)
- `rowid` (type inféré: TEXT)
- `rowidx` (type inféré: TEXT)
- `rows` (type inféré: TEXT)
- `sel` (type inféré: TEXT)
- `selected_field` (type inféré: TEXT)
- `total` (type inféré: REAL)
- `typ` (type inféré: TEXT)
- `val` (type inféré: TEXT)
- `val_prix` (type inféré: REAL)
- `val_row` (type inféré: TEXT)
- `valeur` (type inféré: REAL)
- `value` (type inféré: TEXT)
- `with_modele_colonne` (type inféré: TEXT)
- `x` (type inféré: TEXT)
- `y` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_module_fields`

**Colonnes détectées:**

- `btn_frame` (type inféré: TEXT)
- `champ` (type inféré: TEXT)
- `cols` (type inféré: TEXT)
- `columns` (type inféré: TEXT)
- `fid` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `index` (type inféré: TEXT)
- `initialvalue` (type inféré: TEXT)
- `modele_colonne` (type inféré: TEXT)
- `module_id` (type inféré: INTEGER)
- `new_price` (type inféré: TEXT)
- `nom_champ` (type inféré: TEXT)
- `old_price` (type inféré: TEXT)
- `prix_unitaire` (type inféré: REAL)
- `selectmode` (type inféré: TEXT)
- `show` (type inféré: TEXT)
- `tree` (type inféré: TEXT)
- `type_champ` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_module_fields.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_modules`

**Colonnes détectées:**

- `1` (type inféré: TEXT)
- `ComboboxSelected` (type inféré: TEXT)
- `btnf` (type inféré: TEXT)
- `colonne_frame` (type inféré: TEXT)
- `colonne_idx` (type inféré: TEXT)
- `colonne_label` (type inféré: TEXT)
- `colonne_menu` (type inféré: TEXT)
- `colonne_var` (type inféré: TEXT)
- `colonnes_choices` (type inféré: TEXT)
- `columns` (type inféré: TEXT)
- `columnspan` (type inféré: TEXT)
- `comment` (type inféré: TEXT)
- `comment_var` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `editing_entry` (type inféré: TEXT)
- `event` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `field_id` (type inféré: INTEGER)
- `fields` (type inféré: TEXT)
- `font` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `id_col_total` (type inféré: REAL)
- `idx` (type inféré: TEXT)
- `mem` (type inféré: TEXT)
- `membre_nom` (type inféré: TEXT)
- `mid` (type inféré: TEXT)
- `mods` (type inféré: TEXT)
- `module_choices` (type inféré: TEXT)
- `module_id` (type inféré: INTEGER)
- `module_idx` (type inféré: TEXT)
- `module_menu` (type inféré: TEXT)
- `module_name` (type inféré: TEXT)
- `module_var` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `montant_entry` (type inféré: REAL)
- `montant_var` (type inféré: REAL)
- `name` (type inféré: TEXT)
- `nom_module` (type inféré: TEXT)
- `prix_var` (type inféré: REAL)
- `r` (type inféré: TEXT)
- `recette_id` (type inféré: INTEGER)
- `result` (type inféré: TEXT)
- `rid` (type inféré: TEXT)
- `rows` (type inféré: TEXT)
- `sel` (type inféré: TEXT)
- `selectmode` (type inféré: TEXT)
- `show` (type inféré: TEXT)
- `somme` (type inféré: TEXT)
- `source` (type inféré: TEXT)
- `source_var` (type inféré: TEXT)
- `sticky` (type inféré: TEXT)
- `tree` (type inféré: TEXT)
- `type_var` (type inféré: TEXT)
- `types` (type inféré: TEXT)
- `value` (type inféré: TEXT)
- `variable` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_payments`

**Colonnes détectées:**

- `banque` (type inféré: TEXT)
- `banque_var` (type inféré: TEXT)
- `classe` (type inféré: TEXT)
- `classe_var` (type inféré: TEXT)
- `comment` (type inféré: TEXT)
- `comment_var` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `d` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `id` (type inféré: INTEGER)
- `mode` (type inféré: TEXT)
- `mode_paiement` (type inféré: TEXT)
- `mode_var` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `montant_var` (type inféré: REAL)
- `name` (type inféré: TEXT)
- `nom_payeuse` (type inféré: TEXT)
- `nom_var` (type inféré: TEXT)
- `numero` (type inféré: TEXT)
- `numero_cheque` (type inféré: TEXT)
- `numero_var` (type inféré: TEXT)
- `p` (type inféré: TEXT)
- `payment_id` (type inféré: INTEGER)

**Référencée dans les fichiers:**

- `modules/event_payments.py`

---

### Table: `event_recettes`

**Colonnes détectées:**

- `0` (type inféré: TEXT)
- `COALESCE` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `date_var` (type inféré: DATE)
- `depenses` (type inféré: TEXT)
- `desc` (type inféré: TEXT)
- `desc_var` (type inféré: TEXT)
- `description` (type inféré: TEXT)
- `eid` (type inféré: TEXT)
- `ev` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `gain` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `lieu` (type inféré: TEXT)
- `lieu_var` (type inféré: TEXT)
- `module_id` (type inféré: INTEGER)
- `montant` (type inféré: REAL)
- `name` (type inféré: TEXT)
- `name_var` (type inféré: TEXT)
- `sel` (type inféré: TEXT)
- `source` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/event_recettes.py`
- `modules/events.py`
- `modules/exports.py`

---

### Table: `events`

**Colonnes détectées:**

- `Caisses` (type inféré: TEXT)
- `Dépenses` (type inféré: TEXT)
- `LOT` (type inféré: TEXT)
- `Recettes` (type inféré: TEXT)
- `SUBVENTIONS` (type inféré: TEXT)
- `alignment` (type inféré: TEXT)
- `b` (type inféré: TEXT)
- `bottomMargin` (type inféré: TEXT)
- `caisse_id` (type inféré: INTEGER)
- `caisses` (type inféré: TEXT)
- `caisses_data` (type inféré: TEXT)
- `caisses_details` (type inféré: TEXT)
- `caisses_details_df` (type inféré: TEXT)
- `cid` (type inféré: TEXT)
- `colWidths` (type inféré: TEXT)
- `data` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `debut` (type inféré: TEXT)
- `depenses` (type inféré: TEXT)
- `depenses_data` (type inféré: TEXT)
- `description` (type inféré: TEXT)
- `doc` (type inféré: TEXT)
- `dons` (type inféré: TEXT)
- `dossier` (type inféré: TEXT)
- `dépenses` (type inféré: TEXT)
- `elements` (type inféré: TEXT)
- `encoding` (type inféré: TEXT)
- `enregistré` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `events` (type inféré: TEXT)
- `evt_id` (type inféré: INTEGER)
- `ext` (type inféré: TEXT)
- `filename` (type inféré: TEXT)
- `fin` (type inféré: TEXT)
- `format` (type inféré: TEXT)
- `gain` (type inféré: TEXT)
- `hAlign` (type inféré: TEXT)
- `i` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `index` (type inféré: TEXT)
- `initialfile` (type inféré: TEXT)
- `inv_id` (type inféré: INTEGER)
- `leftMargin` (type inféré: TEXT)
- `lieu` (type inféré: TEXT)
- `moment` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `pagesize` (type inféré: TEXT)
- `qte_constatee` (type inféré: TEXT)
- `recettes` (type inféré: TEXT)
- `recettes_data` (type inféré: TEXT)
- `rightMargin` (type inféré: TEXT)
- `sheet_name` (type inféré: TEXT)
- `stock_id` (type inféré: INTEGER)
- `styles` (type inféré: TEXT)
- `subventions` (type inféré: TEXT)
- `synth_data` (type inféré: TEXT)
- `synth_table` (type inféré: TEXT)
- `t` (type inféré: TEXT)
- `topMargin` (type inféré: TEXT)
- `total_depenses` (type inféré: REAL)
- `total_recettes` (type inféré: REAL)
- `type` (type inféré: TEXT)
- `vals` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_inventaire_db.py`
- `modules/buvette_mouvements_db.py`
- `modules/events.py`
- `modules/exports.py`
- `modules/inventaire.py`
- `scripts/migration.py`

---

### Table: `fournisseurs`

**Colonnes détectées:**

- `confirm` (type inféré: TEXT)
- `fid` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `initialvalue` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `new_nom` (type inféré: TEXT)
- `parent` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/fournisseurs.py`

---

### Table: `historique_clotures`

**Colonnes détectées:**

- `cid` (type inféré: TEXT)
- `date_cloture` (type inféré: DATE)
- `id` (type inféré: INTEGER)
- `initialvalue` (type inféré: TEXT)
- `new_date` (type inféré: DATE)

**Référencée dans les fichiers:**

- `modules/historique_clotures.py`

---

### Table: `inventaire_lignes`

**Colonnes détectées:**

- `c.name` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `inventaire_id` (type inféré: INTEGER)
- `l.quantite_constatee` (type inféré: INTEGER)
- `l.stock_id` (type inféré: INTEGER)
- `quantite_constatee` (type inféré: INTEGER)
- `s.name` (type inféré: TEXT)
- `stock_id` (type inféré: INTEGER)

**Référencée dans les fichiers:**

- `modules/historique_inventaire.py`
- `modules/inventaire.py`

---

### Table: `inventaires`

**Colonnes détectées:**

- `commentaire` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `date_inventaire` (type inféré: DATE)
- `evenement` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `id` (type inféré: INTEGER)

**Référencée dans les fichiers:**

- `modules/inventaire.py`

---

### Table: `membres`

**Colonnes détectées:**

- `commentaire` (type inféré: TEXT)
- `commentaire_var` (type inféré: TEXT)
- `cotisation` (type inféré: TEXT)
- `cotisation_menu` (type inféré: TEXT)
- `cotisation_var` (type inféré: TEXT)
- `date_adh` (type inféré: DATE)
- `date_adhesion` (type inféré: DATE)
- `date_var` (type inféré: DATE)
- `email` (type inféré: TEXT)
- `email_var` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `member_id` (type inféré: INTEGER)
- `name` (type inféré: TEXT)
- `nom_var` (type inféré: TEXT)
- `prenom` (type inféré: TEXT)
- `prenom_var` (type inféré: TEXT)
- `statut` (type inféré: TEXT)
- `statut_menu` (type inféré: TEXT)
- `statut_var` (type inféré: TEXT)
- `tel` (type inféré: TEXT)
- `tel_var` (type inféré: TEXT)
- `telephone` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/members.py`

---

### Table: `mouvements_stock`

**Colonnes détectées:**

- `date` (type inféré: DATE)
- `id` (type inféré: INTEGER)
- `m.commentaire` (type inféré: TEXT)
- `m.date` (type inféré: DATE)
- `m.date_peremption` (type inféré: DATE)
- `m.id` (type inféré: TEXT)
- `m.prix_achat_total` (type inféré: REAL)
- `m.prix_unitaire` (type inféré: REAL)
- `m.quantite` (type inféré: INTEGER)
- `m.type` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `prix_achat_total` (type inféré: REAL)
- `prix_unitaire` (type inféré: REAL)
- `quantite` (type inféré: INTEGER)
- `s.name` (type inféré: TEXT)
- `type` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `modules/mouvements_stock.py`

---

### Table: `retrocessions_ecoles`

**Colonnes détectées:**

- `"""` (type inféré: TEXT)
- `"Erreur` (type inféré: TEXT)
- `"La` (type inféré: TEXT)
- `'apres'` (type inféré: TEXT)
- `'hors_evenement'))` (type inféré: TEXT)
- `article_id` (type inféré: INTEGER)
- `banque` (type inféré: TEXT)
- `but_asso` (type inféré: TEXT)
- `caisse_id` (type inféré: INTEGER)
- `categorie` (type inféré: TEXT)
- `categorie_id` (type inféré: INTEGER)
- `cid` (type inféré: TEXT)
- `classe` (type inféré: TEXT)
- `cloture` (type inféré: INTEGER)
- `comm_var` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `contenance` (type inféré: TEXT)
- `cotisation` (type inféré: TEXT)
- `data` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `date_achat` (type inféré: TEXT)
- `date_adhesion` (type inféré: TEXT)
- `date_cloture` (type inféré: TEXT)
- `date_depense` (type inféré: TEXT)
- `date_fin` (type inféré: TEXT)
- `date_inventaire` (type inféré: TEXT)
- `date_mouvement` (type inféré: TEXT)
- `date_peremption` (type inféré: TEXT)
- `date_recette` (type inféré: TEXT)
- `date_var` (type inféré: DATE)
- `description` (type inféré: TEXT)
- `disponible_banque` (type inféré: REAL)
- `ecole` (type inféré: TEXT)
- `ecole_var` (type inféré: TEXT)
- `email` (type inféré: TEXT)
- `event_id` (type inféré: INTEGER)
- `exercice` (type inféré: TEXT)
- `f"Erreur` (type inféré: TEXT)
- `facture` (type inféré: TEXT)
- `field_id` (type inféré: INTEGER)
- `fournisseur` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `id_col_total` (type inféré: INTEGER)
- `inventaire_id` (type inféré: INTEGER)
- `justificatif` (type inféré: TEXT)
- `lieu` (type inféré: TEXT)
- `lot` (type inféré: TEXT)
- `membre_id` (type inféré: INTEGER)
- `mode_paiement` (type inféré: TEXT)
- `modele_colonne` (type inféré: TEXT)
- `modele_id` (type inféré: INTEGER)
- `module_id` (type inféré: INTEGER)
- `moment` (type inféré: TEXT)
- `montant` (type inféré: REAL)
- `montant_float` (type inféré: REAL)
- `montant_var` (type inféré: REAL)
- `motif` (type inféré: TEXT)
- `moyen_paiement` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `nom_caisse` (type inféré: TEXT)
- `nom_champ` (type inféré: TEXT)
- `nom_module` (type inféré: TEXT)
- `nom_payeuse` (type inféré: TEXT)
- `numero_cheque` (type inféré: TEXT)
- `numero_facture` (type inféré: TEXT)
- `parent_id` (type inféré: INTEGER)
- `paye_par` (type inféré: TEXT)
- `pointe` (type inféré: INTEGER)
- `prenom` (type inféré: TEXT)
- `prix_achat_total` (type inféré: REAL)
- `prix_unitaire` (type inféré: REAL)
- `purchase_price` (type inféré: REAL)
- `quantite` (type inféré: INTEGER)
- `quantite_constatee` (type inféré: INTEGER)
- `reference` (type inféré: TEXT)
- `row_index` (type inféré: INTEGER)
- `seuil_alerte` (type inféré: INTEGER)
- `solde` (type inféré: REAL)
- `solde_report` (type inféré: REAL)
- `source` (type inféré: TEXT)
- `statut` (type inféré: TEXT)
- `statut_reglement` (type inféré: TEXT)
- `statut_remboursement` (type inféré: TEXT)
- `stock` (type inféré: INTEGER)
- `stock_id` (type inféré: INTEGER)
- `telephone` (type inféré: TEXT)
- `type` (type inféré: TEXT)
- `type_champ` (type inféré: TEXT)
- `type_inventaire` (type inféré: TEXT)
- `type_modele` (type inféré: TEXT)
- `type_mouvement` (type inféré: TEXT)
- `unite` (type inféré: TEXT)
- `valeur` (type inféré: TEXT)
- `value` (type inféré: TEXT)
- `win` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `db/db.py`
- `modules/retrocessions_ecoles.py`

---

### Table: `sqlite_master`

**Colonnes détectées:**

- `__name__` (type inféré: TEXT)
- `anchor` (type inféré: TEXT)
- `bg` (type inféré: TEXT)
- `bool` (type inféré: TEXT)
- `button_frame` (type inféré: TEXT)
- `capture_output` (type inféré: TEXT)
- `check` (type inféré: TEXT)
- `close_button` (type inféré: TEXT)
- `col_type` (type inféré: TEXT)
- `columns` (type inféré: TEXT)
- `confirm` (type inféré: TEXT)
- `content` (type inféré: TEXT)
- `cwd` (type inféré: TEXT)
- `date` (type inféré: DATE)
- `db_path` (type inféré: TEXT)
- `default_value` (type inféré: TEXT)
- `dialog` (type inféré: TEXT)
- `encoding` (type inféré: TEXT)
- `error_msg` (type inféré: TEXT)
- `existing_cols` (type inféré: TEXT)
- `expected_schema` (type inféré: TEXT)
- `fg` (type inféré: TEXT)
- `font` (type inféré: TEXT)
- `foreground` (type inféré: TEXT)
- `fuzzy_match` (type inféré: TEXT)
- `header_color` (type inféré: TEXT)
- `header_frame` (type inféré: TEXT)
- `header_label` (type inféré: TEXT)
- `icon` (type inféré: TEXT)
- `ignore_button` (type inféré: TEXT)
- `info_label` (type inféré: TEXT)
- `info_text` (type inféré: TEXT)
- `is_error` (type inféré: TEXT)
- `justify` (type inféré: TEXT)
- `key` (type inféré: TEXT)
- `latest_report` (type inféré: TEXT)
- `major` (type inféré: TEXT)
- `message` (type inféré: TEXT)
- `minor` (type inféré: TEXT)
- `missing` (type inféré: TEXT)
- `missing_cols` (type inféré: TEXT)
- `missing_columns` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `open_button` (type inféré: TEXT)
- `parent` (type inféré: TEXT)
- `parent_window` (type inféré: TEXT)
- `patch` (type inféré: TEXT)
- `platform` (type inféré: TEXT)
- `real_cols` (type inféré: TEXT)
- `real_schema` (type inféré: TEXT)
- `recommendation_label` (type inféré: TEXT)
- `recommendation_text` (type inféré: TEXT)
- `report_path` (type inféré: TEXT)
- `reports` (type inféré: TEXT)
- `reports_dir` (type inféré: TEXT)
- `result` (type inféré: TEXT)
- `returncode` (type inféré: TEXT)
- `root` (type inféré: TEXT)
- `script_path` (type inféré: TEXT)
- `scrollbar` (type inféré: TEXT)
- `show_report` (type inféré: TEXT)
- `str` (type inféré: TEXT)
- `succes` (type inféré: TEXT)
- `success` (type inféré: TEXT)
- `success_msg` (type inféré: TEXT)
- `successfully` (type inféré: TEXT)
- `supports_rename` (type inféré: TEXT)
- `table_exists` (type inféré: TEXT)
- `table_missing` (type inféré: TEXT)
- `tables` (type inféré: TEXT)
- `text_color` (type inféré: TEXT)
- `text_frame` (type inféré: TEXT)
- `text_widget` (type inféré: TEXT)
- `threshold` (type inféré: TEXT)
- `timeout` (type inféré: TEXT)
- `title_text` (type inféré: TEXT)
- `type` (type inféré: TEXT)
- `update_button` (type inféré: DATE)
- `user_choice` (type inféré: TEXT)
- `version` (type inféré: TEXT)
- `warning_label` (type inféré: TEXT)
- `wrap` (type inféré: TEXT)
- `wraplength` (type inféré: TEXT)
- `x` (type inféré: TEXT)
- `y` (type inféré: TEXT)
- `yscrollcommand` (type inféré: TEXT)

**Référencée dans les fichiers:**

- `db/db.py`
- `scripts/migrate_add_purchase_price.py`
- `scripts/update_db_structure.py`
- `ui/startup_schema_check.py`

---

### Table: `stock`

**Colonnes détectées:**

- `COUNT` (type inféré: INTEGER)
- `SUM` (type inféré: TEXT)
- `c.name` (type inféré: TEXT)
- `cat_cb` (type inféré: TEXT)
- `cat_var` (type inféré: TEXT)
- `categorie` (type inféré: TEXT)
- `categorie_id` (type inféré: INTEGER)
- `cats` (type inféré: TEXT)
- `comment_var` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `date_peremp_var` (type inféré: DATE)
- `date_peremption` (type inféré: DATE)
- `id` (type inféré: INTEGER)
- `lot` (type inféré: TEXT)
- `lot_var` (type inféré: TEXT)
- `name` (type inféré: TEXT)
- `nom_var` (type inféré: TEXT)
- `qte_var` (type inféré: TEXT)
- `quantite` (type inféré: INTEGER)
- `s.commentaire` (type inféré: TEXT)
- `s.date_peremption` (type inféré: DATE)
- `s.id` (type inféré: TEXT)
- `s.lot` (type inféré: TEXT)
- `s.name` (type inféré: TEXT)
- `s.quantite` (type inféré: INTEGER)
- `s.seuil_alerte` (type inféré: INTEGER)
- `seuil_alerte` (type inféré: INTEGER)
- `seuil_var` (type inféré: INTEGER)
- `stock` (type inféré: INTEGER)
- `stock_id` (type inféré: INTEGER)

**Référencée dans les fichiers:**

- `modules/categories.py`
- `modules/inventaire.py`
- `modules/stock.py`
- `modules/stock_inventaire.py`
- `modules/stock_stats.py`

---

### Table: `tree`

**Colonnes détectées:**

- `article` (type inféré: TEXT)
- `article_combo` (type inféré: TEXT)
- `article_id` (type inféré: INTEGER)
- `article_str` (type inféré: TEXT)
- `article_var` (type inféré: TEXT)
- `articles` (type inféré: TEXT)
- `btn_frame` (type inféré: TEXT)
- `callback` (type inféré: TEXT)
- `categorie` (type inféré: TEXT)
- `categorie_entry` (type inféré: TEXT)
- `categorie_label` (type inféré: TEXT)
- `columnspan` (type inféré: TEXT)
- `commentaire` (type inféré: TEXT)
- `contenance` (type inféré: TEXT)
- `contenance_entry` (type inféré: TEXT)
- `contenance_label` (type inféré: TEXT)
- `create_new_var` (type inféré: TEXT)
- `frame` (type inféré: TEXT)
- `id` (type inféré: INTEGER)
- `name` (type inféré: TEXT)
- `name_entry` (type inféré: TEXT)
- `name_label` (type inféré: TEXT)
- `new_categorie_var` (type inféré: TEXT)
- `new_contenance_var` (type inféré: TEXT)
- `new_name_var` (type inféré: TEXT)
- `quantite` (type inféré: INTEGER)
- `quantite_var` (type inféré: INTEGER)
- `select_label` (type inféré: TEXT)
- `sticky` (type inféré: TEXT)
- `unite` (type inféré: TEXT)
- `value` (type inféré: TEXT)
- `variable` (type inféré: TEXT)

**Référencée dans les fichiers:**


---

### Table: `valeurs_modeles_colonnes`

**Colonnes détectées:**

- `modele_id` (type inféré: INTEGER)
- `valeur` (type inféré: REAL)

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/model_colonnes.py`

---

