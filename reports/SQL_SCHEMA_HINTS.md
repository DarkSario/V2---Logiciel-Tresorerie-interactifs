# Analyse SQL - Tables et Colonnes Détectées

Ce rapport liste toutes les tables et colonnes référencées dans le code Python.
Il sert de référence pour les migrations et la maintenance du schéma de base de données.

**Nombre total de tables détectées:** 35

## Résumé par Table

- **buvette_achats**: 33 colonnes, référencée dans 3 fichier(s)
- **buvette_articles**: 17 colonnes, référencée dans 6 fichier(s)
- **buvette_inventaire_lignes**: 9 colonnes, référencée dans 5 fichier(s)
- **buvette_inventaires**: 11 colonnes, référencée dans 3 fichier(s)
- **buvette_mouvements**: 10 colonnes, référencée dans 2 fichier(s)
- **buvette_recettes**: 1 colonnes, référencée dans 2 fichier(s)
- **categories**: 38 colonnes, référencée dans 2 fichier(s)
- **colonnes_modeles**: 67 colonnes, référencée dans 3 fichier(s)
- **comptes**: 9 colonnes, référencée dans 1 fichier(s)
- **config**: 7 colonnes, référencée dans 3 fichier(s)
- **depenses_diverses**: 16 colonnes, référencée dans 1 fichier(s)
- **depenses_regulieres**: 16 colonnes, référencée dans 1 fichier(s)
- **depots_retraits_banque**: 29 colonnes, référencée dans 1 fichier(s)
- **dons_subventions**: 9 colonnes, référencée dans 2 fichier(s)
- **event_caisse_details**: 30 colonnes, référencée dans 1 fichier(s)
- **event_caisses**: 40 colonnes, référencée dans 3 fichier(s)
- **event_depenses**: 34 colonnes, référencée dans 3 fichier(s)
- **event_module_data**: 66 colonnes, référencée dans 3 fichier(s)
- **event_module_fields**: 29 colonnes, référencée dans 4 fichier(s)
- **event_modules**: 71 colonnes, référencée dans 4 fichier(s)
- **event_payments**: 32 colonnes, référencée dans 1 fichier(s)
- **event_recettes**: 32 colonnes, référencée dans 3 fichier(s)
- **events**: 68 colonnes, référencée dans 8 fichier(s)
- **for**: 3 colonnes, référencée dans 0 fichier(s)
- **fournisseurs**: 8 colonnes, référencée dans 3 fichier(s)
- **historique_clotures**: 6 colonnes, référencée dans 1 fichier(s)
- **inventaire_lignes**: 8 colonnes, référencée dans 2 fichier(s)
- **inventaires**: 3 colonnes, référencée dans 1 fichier(s)
- **membres**: 40 colonnes, référencée dans 3 fichier(s)
- **mouvements_stock**: 9 colonnes, référencée dans 1 fichier(s)
- **retrocessions_ecoles**: 100 colonnes, référencée dans 2 fichier(s)
- **sqlite_master**: 75 colonnes, référencée dans 4 fichier(s)
- **stock**: 38 colonnes, référencée dans 5 fichier(s)
- **tree**: 44 colonnes, référencée dans 0 fichier(s)
- **valeurs_modeles_colonnes**: 2 colonnes, référencée dans 3 fichier(s)

## Détails des Tables et Colonnes

### Table: `buvette_achats`

**Colonnes détectées:**

- `article_id`
- `bilan_txt`
- `command`
- `conn`
- `date_achat`
- `event_combo`
- `event_id`
- `events`
- `evt_label`
- `exercice`
- `expand`
- `facture`
- `fill`
- `fournisseur`
- `frm_select`
- `height`
- `id`
- `inv_apres`
- `inv_avant`
- `lignes_apres`
- `lignes_avant`
- `padx`
- `pady`
- `params`
- `prix_unitaire`
- `quantite`
- `recette`
- `row`
- `rows`
- `side`
- `state`
- `text`
- `width`

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_db.py`

---

### Table: `buvette_articles`

**Colonnes détectées:**

- `article`
- `article_id`
- `categorie`
- `columns`
- `commentaire`
- `conn`
- `contenance`
- `cursor`
- `has_purchase_price`
- `id`
- `name`
- `purchase_price`
- `quantite`
- `row`
- `rows`
- `stock`
- `unite`

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

- `article_id`
- `commentaire`
- `conn`
- `cur`
- `id`
- `inventaire_id`
- `quantite`
- `row`
- `rows`

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_db.py`
- `modules/buvette_inventaire_db.py`
- `ui/inventory_lines_dialog.py`

---

### Table: `buvette_inventaires`

**Colonnes détectées:**

- `article_id`
- `commentaire`
- `conn`
- `cur`
- `date_inventaire`
- `event_id`
- `id`
- `inv_id`
- `inventaire_id`
- `rows`
- `type_inventaire`

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`
- `modules/buvette_inventaire_db.py`

---

### Table: `buvette_mouvements`

**Colonnes détectées:**

- `article_id`
- `conn`
- `date_mouvement`
- `event_id`
- `id`
- `inventaire_id`
- `motif`
- `quantite`
- `rows`
- `type_mouvement`

**Référencée dans les fichiers:**

- `modules/buvette_db.py`
- `modules/buvette_mouvements_db.py`

---

### Table: `buvette_recettes`

**Colonnes détectées:**

- `SUM`

**Référencée dans les fichiers:**

- `modules/buvette_bilan_db.py`
- `modules/buvette_bilan_dialogs.py`

---

### Table: `categories`

**Colonnes détectées:**

- `c.id`
- `c.name`
- `cat_id`
- `categorie_id`
- `column`
- `command`
- `commentaire`
- `conn`
- `cur`
- `date_peremption`
- `df_cat`
- `form`
- `id`
- `item`
- `lot`
- `name`
- `nb_children`
- `nb_stock`
- `nom_entry`
- `p.name`
- `padx`
- `pady`
- `parent_cb`
- `parent_id`
- `parent_nom`
- `parent_row`
- `parent_var`
- `quantite`
- `result`
- `row`
- `selected`
- `seuil_alerte`
- `state`
- `sticky`
- `text`
- `textvariable`
- `values`
- `width`

**Référencée dans les fichiers:**

- `modules/categories.py`
- `modules/stock.py`

---

### Table: `colonnes_modeles`

**Colonnes détectées:**

- `"INTEGER"`
- `"REAL"]).pack(fill="x"`
- `"Supprimer`
- `"bold")).pack(anchor="w"`
- `"bold")).pack(pady=8)`
- `(modele_id`
- `(name`
- `))`
- `)).fetchall()`
- `)).fetchone()["id"]`
- `10`
- `200)`
- `6))`
- `600)`
- `?)"`
- `anchor="w")`
- `anchor="w").pack(side="left")`
- `callback=None):`
- `callback=self.refresh_list)`
- `command=lambda`
- `command=self.ajouter).pack(side="left"`
- `command=self.destroy).pack(side="right"`
- `command=top.destroy).pack(pady=8)`
- `expand=True`
- `font=("Arial"`
- `height=15`
- `id`
- `master`
- `master):`
- `modele_id`
- `modele_id):`
- `modele_id=None`
- `modele_id=modele_id`
- `name`
- `padx=10`
- `padx=2)`
- `padx=4)`
- `padx=5`
- `padx=8`
- `padx=8)`
- `pady=(0`
- `pady=10)`
- `pady=2`
- `pady=8)`
- `text="Ajouter`
- `text="Fermer"`
- `text="Modifier"`
- `text="Modèles`
- `text="Name`
- `text="Supprimer"`
- `text="Type`
- `text="Valeurs`
- `text="Voir`
- `text=f"{c['name']}`
- `textvariable=self.nom_var).pack(fill="x"`
- `textvariable=self.type_var`
- `txt)`
- `typ`
- `typ))`
- `type_modele`
- `type_modele)`
- `v))`
- `valeur`
- `valeur)`
- `valeurs):`
- `values=["TEXT"`
- `width=40)`

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/model_colonnes.py`

---

### Table: `comptes`

**Colonnes détectées:**

- `("Banque`
- `?)"`
- `column`
- `definition):`
- `id`
- `name`
- `row["solde_report"]))`
- `solde`
- `solde)`

**Référencée dans les fichiers:**

- `db/db.py`

---

### Table: `config`

**Colonnes détectées:**

- `MAX`
- `date`
- `date_fin`
- `disponible_banque`
- `exercice`
- `id`
- `solde_report`

**Référencée dans les fichiers:**

- `db/db.py`
- `modules/journal.py`
- `modules/solde_ouverture.py`

---

### Table: `depenses_diverses`

**Colonnes détectées:**

- `categorie`
- `commentaire`
- `conn`
- `date_depense`
- `fournisseur`
- `id`
- `items`
- `membre_id`
- `module_id`
- `montant`
- `moyen_paiement`
- `numero_cheque`
- `numero_facture`
- `paye_par`
- `statut_reglement`
- `statut_remboursement`

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`

---

### Table: `depenses_regulieres`

**Colonnes détectées:**

- `categorie`
- `commentaire`
- `conn`
- `date_depense`
- `fournisseur`
- `id`
- `items`
- `membre_id`
- `module_id`
- `montant`
- `moyen_paiement`
- `numero_cheque`
- `numero_facture`
- `paye_par`
- `statut_reglement`
- `statut_remboursement`

**Référencée dans les fichiers:**

- `modules/depenses_regulieres.py`

---

### Table: `depots_retraits_banque`

**Colonnes détectées:**

- `DISTINCT`
- `banque`
- `banques`
- `c`
- `cmb_type`
- `column`
- `commentaire`
- `conn`
- `date`
- `df`
- `ent_date`
- `ent_montant`
- `id`
- `id_`
- `iid`
- `index`
- `item`
- `montant`
- `new_val`
- `params`
- `pointe`
- `reference`
- `row`
- `state`
- `sticky`
- `text`
- `type`
- `values`
- `win`

**Référencée dans les fichiers:**

- `modules/depots_retraits_banque.py`

---

### Table: `dons_subventions`

**Colonnes détectées:**

- `conn`
- `date`
- `id`
- `items`
- `justificatif`
- `montant`
- `row_factory`
- `source`
- `type`

**Référencée dans les fichiers:**

- `modules/dons_subventions.py`
- `modules/exports.py`

---

### Table: `event_caisse_details`

**Colonnes détectées:**

- `caisse_id`
- `command`
- `conn`
- `date`
- `date_var`
- `desc`
- `desc_var`
- `description`
- `id`
- `justif`
- `justif_var`
- `justificatif`
- `montant`
- `montant_float`
- `montant_var`
- `on_save`
- `op`
- `operation_id`
- `padx`
- `pady`
- `side`
- `state`
- `text`
- `textvariable`
- `typ`
- `type_op`
- `type_ops`
- `type_var`
- `values`
- `width`

**Référencée dans les fichiers:**

- `modules/event_caisse_details.py`

---

### Table: `event_caisses`

**Colonnes détectées:**

- `btn_frame`
- `caisse`
- `caisse_id`
- `cid`
- `columns`
- `command`
- `commentaire`
- `conn`
- `event_id`
- `exist`
- `expand`
- `fill`
- `fond_debut`
- `fond_fin`
- `id`
- `moment`
- `montant`
- `nom`
- `nom_caisse`
- `nom_var`
- `on_save`
- `padx`
- `pady`
- `r`
- `recettes`
- `resp`
- `resp_var`
- `responsable`
- `show`
- `side`
- `solde`
- `solde_float`
- `solde_initial`
- `solde_var`
- `source`
- `text`
- `textvariable`
- `tree`
- `type`
- `width`

**Référencée dans les fichiers:**

- `modules/event_caisses.py`
- `modules/event_recettes.py`
- `modules/exports.py`

---

### Table: `event_depenses`

**Colonnes détectées:**

- `0`
- `COALESCE`
- `categorie`
- `categorie_var`
- `command`
- `commentaire`
- `conn`
- `date`
- `date_depense`
- `date_var`
- `dep`
- `depense_id`
- `desc`
- `desc_var`
- `description`
- `event_id`
- `fournisseur`
- `fournisseur_var`
- `id`
- `justif`
- `justif_var`
- `justificatif`
- `membre_id`
- `montant`
- `montant_float`
- `montant_var`
- `on_save`
- `padx`
- `pady`
- `paye_par`
- `side`
- `text`
- `textvariable`
- `width`

**Référencée dans les fichiers:**

- `modules/event_depenses.py`
- `modules/events.py`
- `modules/exports.py`

---

### Table: `event_module_data`

**Colonnes détectées:**

- `FocusOut`
- `MAX`
- `Return`
- `ch`
- `choix`
- `col`
- `col_idx`
- `columns`
- `conn`
- `df`
- `dlg`
- `dlg_prix`
- `e`
- `editing_entry`
- `entry`
- `field`
- `field_id`
- `fields`
- `height`
- `id`
- `id_col`
- `id_col_total`
- `idx`
- `iid`
- `implémentée`
- `initialvalue`
- `modele_colonne`
- `modele_id`
- `module_id`
- `name`
- `new_price`
- `new_value`
- `next_idx`
- `next_row`
- `old_price`
- `on_save`
- `parent`
- `parent_dir`
- `prix`
- `prix_unitaire`
- `qte`
- `region`
- `res`
- `res_total`
- `row`
- `row_idx`
- `row_index`
- `row_values`
- `rowid`
- `rowidx`
- `rows`
- `sel`
- `selected_field`
- `title`
- `total`
- `typ`
- `val`
- `val_prix`
- `val_row`
- `valeur`
- `value`
- `values`
- `width`
- `with_modele_colonne`
- `x`
- `y`

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_module_fields`

**Colonnes détectées:**

- `btn_frame`
- `champ`
- `cols`
- `columns`
- `command`
- `conn`
- `df`
- `expand`
- `fid`
- `fill`
- `id`
- `index`
- `initialvalue`
- `modele_colonne`
- `module_id`
- `new_price`
- `nom_champ`
- `old_price`
- `padx`
- `pady`
- `params`
- `prix_unitaire`
- `selectmode`
- `show`
- `side`
- `text`
- `tree`
- `type_champ`
- `width`

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_module_fields.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_modules`

**Colonnes détectées:**

- `1`
- `ComboboxSelected`
- `btnf`
- `colonne_frame`
- `colonne_idx`
- `colonne_label`
- `colonne_menu`
- `colonne_var`
- `colonnes_choices`
- `column`
- `columns`
- `columnspan`
- `command`
- `comment`
- `comment_var`
- `commentaire`
- `conn`
- `editing_entry`
- `event`
- `event_id`
- `expand`
- `field_id`
- `fields`
- `fill`
- `font`
- `id`
- `id_col_total`
- `idx`
- `mem`
- `membre_nom`
- `mid`
- `mods`
- `module_choices`
- `module_id`
- `module_idx`
- `module_menu`
- `module_name`
- `module_var`
- `montant`
- `montant_entry`
- `montant_var`
- `name`
- `nom_module`
- `on_save`
- `padx`
- `pady`
- `prix_var`
- `r`
- `recette_id`
- `result`
- `rid`
- `row`
- `rows`
- `sel`
- `selectmode`
- `show`
- `side`
- `somme`
- `source`
- `source_var`
- `state`
- `sticky`
- `text`
- `textvariable`
- `tree`
- `type_var`
- `types`
- `value`
- `values`
- `variable`
- `width`

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/event_modules.py`
- `modules/event_recettes.py`

---

### Table: `event_payments`

**Colonnes détectées:**

- `banque`
- `banque_var`
- `classe`
- `classe_var`
- `command`
- `comment`
- `comment_var`
- `commentaire`
- `conn`
- `d`
- `event_id`
- `id`
- `mode`
- `mode_paiement`
- `mode_var`
- `montant`
- `montant_var`
- `name`
- `nom_payeuse`
- `nom_var`
- `numero`
- `numero_cheque`
- `numero_var`
- `on_save`
- `p`
- `padx`
- `pady`
- `payment_id`
- `side`
- `text`
- `textvariable`
- `width`

**Référencée dans les fichiers:**

- `modules/event_payments.py`

---

### Table: `event_recettes`

**Colonnes détectées:**

- `0`
- `COALESCE`
- `command`
- `commentaire`
- `conn`
- `date`
- `date_var`
- `depenses`
- `desc`
- `desc_var`
- `description`
- `eid`
- `ev`
- `event_id`
- `gain`
- `id`
- `lieu`
- `lieu_var`
- `module_id`
- `montant`
- `name`
- `name_var`
- `on_save`
- `padx`
- `pady`
- `sel`
- `side`
- `source`
- `text`
- `textvariable`
- `values`
- `width`

**Référencée dans les fichiers:**

- `modules/event_recettes.py`
- `modules/events.py`
- `modules/exports.py`

---

### Table: `events`

**Colonnes détectées:**

- `Caisses`
- `Dépenses`
- `LOT`
- `Recettes`
- `SUBVENTIONS`
- `alignment`
- `b`
- `bottomMargin`
- `caisse_id`
- `caisses`
- `caisses_data`
- `caisses_details`
- `caisses_details_df`
- `cid`
- `colWidths`
- `conn`
- `data`
- `date`
- `debut`
- `defaultextension`
- `depenses`
- `depenses_data`
- `description`
- `doc`
- `dons`
- `dossier`
- `dépenses`
- `elements`
- `encoding`
- `enregistré`
- `event_id`
- `events`
- `evt_id`
- `ext`
- `filename`
- `filetypes`
- `fin`
- `format`
- `gain`
- `hAlign`
- `i`
- `id`
- `index`
- `initialfile`
- `inv_id`
- `leftMargin`
- `lieu`
- `moment`
- `name`
- `pagesize`
- `params`
- `qte_constatee`
- `recettes`
- `recettes_data`
- `rightMargin`
- `sheet_name`
- `stock_id`
- `styles`
- `subventions`
- `synth_data`
- `synth_table`
- `t`
- `title`
- `topMargin`
- `total_depenses`
- `total_recettes`
- `type`
- `vals`

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

### Table: `for`

**Colonnes détectées:**

- `before`
- `table`
- `table_matches`

**Référencée dans les fichiers:**


---

### Table: `fournisseurs`

**Colonnes détectées:**

- `confirm`
- `conn`
- `fid`
- `id`
- `initialvalue`
- `name`
- `new_nom`
- `parent`

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/fournisseurs.py`

---

### Table: `historique_clotures`

**Colonnes détectées:**

- `cid`
- `conn`
- `date_cloture`
- `id`
- `initialvalue`
- `new_date`

**Référencée dans les fichiers:**

- `modules/historique_clotures.py`

---

### Table: `inventaire_lignes`

**Colonnes détectées:**

- `c.name`
- `event_id`
- `inventaire_id`
- `l.quantite_constatee`
- `l.stock_id`
- `quantite_constatee`
- `s.name`
- `stock_id`

**Référencée dans les fichiers:**

- `modules/historique_inventaire.py`
- `modules/inventaire.py`

---

### Table: `inventaires`

**Colonnes détectées:**

- `commentaire`
- `date_inventaire`
- `event_id`

**Référencée dans les fichiers:**

- `modules/inventaire.py`

---

### Table: `membres`

**Colonnes détectées:**

- `command`
- `commentaire`
- `commentaire_var`
- `conn`
- `cotisation`
- `cotisation_menu`
- `cotisation_var`
- `date_adh`
- `date_adhesion`
- `date_var`
- `defaultextension`
- `df`
- `email`
- `email_var`
- `filepath`
- `filetypes`
- `header`
- `id`
- `member_id`
- `name`
- `nom_var`
- `on_save`
- `padx`
- `pady`
- `prenom`
- `prenom_var`
- `row`
- `side`
- `state`
- `statut`
- `statut_menu`
- `statut_var`
- `tel`
- `tel_var`
- `telephone`
- `text`
- `textvariable`
- `title`
- `values`
- `width`

**Référencée dans les fichiers:**

- `modules/depenses_diverses.py`
- `modules/depenses_regulieres.py`
- `modules/members.py`

---

### Table: `mouvements_stock`

**Colonnes détectées:**

- `m.commentaire`
- `m.date`
- `m.date_peremption`
- `m.id`
- `m.prix_achat_total`
- `m.prix_unitaire`
- `m.quantite`
- `m.type`
- `s.name`

**Référencée dans les fichiers:**

- `modules/mouvements_stock.py`

---

### Table: `retrocessions_ecoles`

**Colonnes détectées:**

- `"""`
- `"Erreur`
- `"La`
- `'apres'`
- `'hors_evenement'))`
- `article_id`
- `banque`
- `but_asso`
- `caisse_id`
- `categorie`
- `categorie_id`
- `cid`
- `classe`
- `cloture`
- `comm_var`
- `command`
- `commentaire`
- `conn`
- `contenance`
- `cotisation`
- `data`
- `date`
- `date_achat`
- `date_adhesion`
- `date_cloture`
- `date_depense`
- `date_fin`
- `date_inventaire`
- `date_mouvement`
- `date_peremption`
- `date_recette`
- `date_var`
- `description`
- `disponible_banque`
- `ecole`
- `ecole_var`
- `email`
- `event_id`
- `exercice`
- `f"Erreur`
- `facture`
- `field_id`
- `fournisseur`
- `id`
- `id_col_total`
- `inventaire_id`
- `justificatif`
- `lieu`
- `lot`
- `membre_id`
- `mode_paiement`
- `modele_colonne`
- `modele_id`
- `module_id`
- `moment`
- `montant`
- `montant_float`
- `montant_var`
- `motif`
- `moyen_paiement`
- `name`
- `nom_caisse`
- `nom_champ`
- `nom_module`
- `nom_payeuse`
- `numero_cheque`
- `numero_facture`
- `pady`
- `parent_id`
- `paye_par`
- `pointe`
- `prenom`
- `prix_achat_total`
- `prix_unitaire`
- `purchase_price`
- `quantite`
- `quantite_constatee`
- `reference`
- `row_index`
- `seuil_alerte`
- `solde`
- `solde_report`
- `source`
- `statut`
- `statut_reglement`
- `statut_remboursement`
- `stock`
- `stock_id`
- `telephone`
- `text`
- `textvariable`
- `type`
- `type_champ`
- `type_inventaire`
- `type_modele`
- `type_mouvement`
- `unite`
- `valeur`
- `value`
- `win`

**Référencée dans les fichiers:**

- `db/db.py`
- `modules/retrocessions_ecoles.py`

---

### Table: `sqlite_master`

**Colonnes détectées:**

- `__name__`
- `anchor`
- `bg`
- `button_frame`
- `capture_output`
- `columns`
- `command`
- `confirm`
- `cursor`
- `cwd`
- `date`
- `db_path`
- `dialog`
- `error_msg`
- `existing_cols`
- `expand`
- `expected_schema`
- `fg`
- `fill`
- `font`
- `foreground`
- `header_frame`
- `height`
- `icon`
- `ignore_button`
- `info_label`
- `info_text`
- `justify`
- `key`
- `latest_report`
- `message`
- `missing`
- `missing_cols`
- `missing_columns`
- `name`
- `padx`
- `pady`
- `parent`
- `parent_window`
- `platform`
- `real_cols`
- `real_schema`
- `recommendation_label`
- `recommendation_text`
- `reports`
- `result`
- `returncode`
- `root`
- `script_path`
- `scripts_dir`
- `scrollbar`
- `show_report`
- `side`
- `state`
- `str`
- `success`
- `success_msg`
- `successfully`
- `succès`
- `table_exists`
- `table_missing`
- `tables`
- `text`
- `text_frame`
- `text_widget`
- `type`
- `update_button`
- `user_choice`
- `warning_label`
- `width`
- `wrap`
- `wraplength`
- `x`
- `y`
- `yscrollcommand`

**Référencée dans les fichiers:**

- `db/db.py`
- `scripts/migrate_add_purchase_price.py`
- `scripts/update_db_structure.py`
- `ui/startup_schema_check.py`

---

### Table: `stock`

**Colonnes détectées:**

- `COUNT`
- `SUM`
- `c.name`
- `cat_cb`
- `cat_var`
- `categorie_id`
- `cats`
- `command`
- `comment_var`
- `commentaire`
- `conn`
- `date_peremp_var`
- `date_peremption`
- `id`
- `lot`
- `lot_var`
- `name`
- `nom_var`
- `on_save`
- `padx`
- `pady`
- `qte_var`
- `quantite`
- `s.commentaire`
- `s.date_peremption`
- `s.id`
- `s.lot`
- `s.name`
- `s.quantite`
- `s.seuil_alerte`
- `seuil_alerte`
- `seuil_var`
- `side`
- `state`
- `stock`
- `text`
- `textvariable`
- `width`

**Référencée dans les fichiers:**

- `modules/categories.py`
- `modules/inventaire.py`
- `modules/stock.py`
- `modules/stock_inventaire.py`
- `modules/stock_stats.py`

---

### Table: `tree`

**Colonnes détectées:**

- `article`
- `article_combo`
- `article_id`
- `article_str`
- `article_var`
- `articles`
- `btn_frame`
- `callback`
- `categorie`
- `categorie_entry`
- `categorie_label`
- `column`
- `columnspan`
- `command`
- `commentaire`
- `contenance`
- `contenance_entry`
- `contenance_label`
- `create_new_var`
- `expand`
- `fill`
- `frame`
- `id`
- `name`
- `name_entry`
- `name_label`
- `new_categorie_var`
- `new_contenance_var`
- `new_name_var`
- `padx`
- `pady`
- `quantite`
- `quantite_var`
- `row`
- `select_label`
- `side`
- `state`
- `sticky`
- `text`
- `textvariable`
- `unite`
- `value`
- `variable`
- `width`

**Référencée dans les fichiers:**


---

### Table: `valeurs_modeles_colonnes`

**Colonnes détectées:**

- `modele_id`
- `valeur`

**Référencée dans les fichiers:**

- `modules/event_module_data.py`
- `modules/event_modules.py`
- `modules/model_colonnes.py`

---

