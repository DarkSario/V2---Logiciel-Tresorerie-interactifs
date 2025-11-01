"""
Tests for the database migration script.
"""

import os
import sys
import sqlite3
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_db_structure import DatabaseMigrator, REFERENCE_SCHEMA


def create_test_database(db_path, missing_columns=True):
    """Create a test database with or without missing columns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if missing_columns:
        # Create tables with some columns missing
        cursor.execute("""
            CREATE TABLE config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercice TEXT,
                date TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE membres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                prenom TEXT
            )
        """)
    else:
        # Create complete tables
        cursor.execute("""
            CREATE TABLE config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercice TEXT,
                date TEXT,
                but_asso TEXT DEFAULT '',
                cloture INTEGER DEFAULT 0,
                solde_report REAL DEFAULT 0.0,
                disponible_banque REAL DEFAULT 0.0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE membres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                prenom TEXT,
                email TEXT DEFAULT '',
                classe TEXT DEFAULT '',
                cotisation TEXT DEFAULT '',
                commentaire TEXT DEFAULT '',
                telephone TEXT DEFAULT '',
                statut TEXT DEFAULT '',
                date_adhesion TEXT DEFAULT ''
            )
        """)
    
    conn.commit()
    conn.close()


def test_database_migrator_initialization():
    """Test DatabaseMigrator initialization."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path)
        migrator = DatabaseMigrator(db_path)
        
        assert migrator.db_path == db_path
        assert migrator.backup_path is None
        assert len(migrator.migration_log) == 0
        assert len(migrator.errors) == 0
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_create_backup():
    """Test backup creation."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path)
        migrator = DatabaseMigrator(db_path)
        
        result = migrator.create_backup()
        
        assert result is True
        assert migrator.backup_path is not None
        assert os.path.exists(migrator.backup_path)
        assert migrator.backup_path.endswith(".bak")
        
        # Clean up backup
        if migrator.backup_path and os.path.exists(migrator.backup_path):
            os.unlink(migrator.backup_path)
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_get_existing_schema():
    """Test schema retrieval."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path)
        migrator = DatabaseMigrator(db_path)
        
        conn = sqlite3.connect(db_path)
        schema = migrator.get_existing_schema(conn)
        conn.close()
        
        assert "config" in schema
        assert "membres" in schema
        assert "id" in schema["config"]
        assert "exercice" in schema["config"]
        assert "date" in schema["config"]
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_detect_missing_columns():
    """Test detection of missing columns."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path, missing_columns=True)
        migrator = DatabaseMigrator(db_path)
        
        conn = sqlite3.connect(db_path)
        existing_schema = migrator.get_existing_schema(conn)
        conn.close()
        
        missing = migrator.detect_missing_columns(existing_schema)
        
        assert "config" in missing
        assert "membres" in missing
        
        # Check that we detected the missing columns in config
        config_missing_cols = [col[0] for col in missing["config"]]
        assert "but_asso" in config_missing_cols
        assert "cloture" in config_missing_cols
        assert "solde_report" in config_missing_cols
        assert "disponible_banque" in config_missing_cols
        
        # Check that we detected the missing columns in membres
        membres_missing_cols = [col[0] for col in missing["membres"]]
        assert "email" in membres_missing_cols
        assert "classe" in membres_missing_cols
        assert "cotisation" in membres_missing_cols
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_apply_migrations():
    """Test applying migrations."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path, missing_columns=True)
        migrator = DatabaseMigrator(db_path)
        
        conn = sqlite3.connect(db_path)
        existing_schema = migrator.get_existing_schema(conn)
        missing = migrator.detect_missing_columns(existing_schema)
        
        result = migrator.apply_migrations(conn, missing)
        
        assert result is True
        
        # Verify columns were added
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(config)")
        config_cols = {row[1] for row in cursor.fetchall()}
        
        assert "but_asso" in config_cols
        assert "cloture" in config_cols
        assert "solde_report" in config_cols
        assert "disponible_banque" in config_cols
        
        cursor.execute("PRAGMA table_info(membres)")
        membres_cols = {row[1] for row in cursor.fetchall()}
        
        assert "email" in membres_cols
        assert "classe" in membres_cols
        assert "cotisation" in membres_cols
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_migration_with_data_preservation():
    """Test that migration preserves existing data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path, missing_columns=True)
        
        # Insert some test data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO config (exercice, date) VALUES (?, ?)", ("2024-2025", "2024-09-01"))
        cursor.execute("INSERT INTO membres (name, prenom) VALUES (?, ?)", ("Dupont", "Jean"))
        cursor.execute("INSERT INTO membres (name, prenom) VALUES (?, ?)", ("Martin", "Marie"))
        conn.commit()
        conn.close()
        
        # Run migration
        migrator = DatabaseMigrator(db_path)
        migrator.create_backup()
        
        conn = sqlite3.connect(db_path)
        existing_schema = migrator.get_existing_schema(conn)
        missing = migrator.detect_missing_columns(existing_schema)
        migrator.apply_migrations(conn, missing)
        
        # Verify data is still there
        cursor = conn.cursor()
        cursor.execute("SELECT exercice, date, but_asso FROM config")
        row = cursor.fetchone()
        assert row[0] == "2024-2025"
        assert row[1] == "2024-09-01"
        # New column should have default value
        assert row[2] == ""
        
        cursor.execute("SELECT name, prenom, email FROM membres")
        rows = cursor.fetchall()
        assert len(rows) == 2
        assert rows[0][0] == "Dupont"
        assert rows[0][1] == "Jean"
        assert rows[0][2] == ""  # Default value for new column
        
        conn.close()
        
        # Clean up backup
        if migrator.backup_path and os.path.exists(migrator.backup_path):
            os.unlink(migrator.backup_path)
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_no_migration_needed():
    """Test when no migration is needed."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path, missing_columns=False)
        migrator = DatabaseMigrator(db_path)
        
        conn = sqlite3.connect(db_path)
        existing_schema = migrator.get_existing_schema(conn)
        missing = migrator.detect_missing_columns(existing_schema)
        
        # Should find no missing columns for these two tables
        if "config" in missing:
            assert len(missing["config"]) == 0
        if "membres" in missing:
            assert len(missing["membres"]) == 0
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_generate_report():
    """Test report generation."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database(db_path, missing_columns=True)
        migrator = DatabaseMigrator(db_path)
        
        conn = sqlite3.connect(db_path)
        existing_schema = migrator.get_existing_schema(conn)
        missing = migrator.detect_missing_columns(existing_schema)
        conn.close()
        
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as report_tmp:
            report_path = report_tmp.name
        
        migrator.generate_report(report_path, missing, True)
        
        assert os.path.exists(report_path)
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        assert "# Database Migration Report" in content
        assert "SUCCESS" in content
        assert "config" in content
        assert "membres" in content
        
        os.unlink(report_path)
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    # Run tests
    test_database_migrator_initialization()
    print("✓ test_database_migrator_initialization")
    
    test_create_backup()
    print("✓ test_create_backup")
    
    test_get_existing_schema()
    print("✓ test_get_existing_schema")
    
    test_detect_missing_columns()
    print("✓ test_detect_missing_columns")
    
    test_apply_migrations()
    print("✓ test_apply_migrations")
    
    test_migration_with_data_preservation()
    print("✓ test_migration_with_data_preservation")
    
    test_no_migration_needed()
    print("✓ test_no_migration_needed")
    
    test_generate_report()
    print("✓ test_generate_report")
    
    print("\nAll tests passed!")
