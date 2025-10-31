import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    lieu TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS event_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    nom_module TEXT NOT NULL,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_module_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    nom_champ TEXT NOT NULL,
    type_champ TEXT NOT NULL,
    FOREIGN KEY(module_id) REFERENCES event_modules(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_module_data (
    module_id INTEGER NOT NULL,
    row_index INTEGER NOT NULL,
    field_id INTEGER NOT NULL,
    valeur TEXT,
    PRIMARY KEY (module_id, row_index, field_id),
    FOREIGN KEY(module_id) REFERENCES event_modules(id) ON DELETE CASCADE,
    FOREIGN KEY(field_id) REFERENCES event_module_fields(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT,
    classe TEXT,
    cotisation REAL,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS dons_subventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donateur TEXT NOT NULL,
    montant REAL NOT NULL,
    date TEXT NOT NULL,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS depenses_regulieres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL,
    montant REAL NOT NULL,
    date TEXT NOT NULL,
    categorie TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS depenses_diverses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL,
    montant REAL NOT NULL,
    date TEXT NOT NULL,
    categorie TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    libelle TEXT NOT NULL,
    montant REAL NOT NULL,
    type TEXT NOT NULL,
    categorie TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER
);

CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    categorie_id INTEGER,
    quantite INTEGER NOT NULL,
    seuil_alerte INTEGER NOT NULL,
    date_peremption TEXT,
    lot TEXT,
    commentaire TEXT,
    FOREIGN KEY(categorie_id) REFERENCES categories(id)
);
"""

def main():
    conn = sqlite3.connect("association.db")
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    main()