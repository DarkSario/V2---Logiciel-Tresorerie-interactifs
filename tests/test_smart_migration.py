"""
Tests for smart migration features: fuzzy matching, YAML hints, and column renaming.
"""

import os
import sys
import sqlite3
import tempfile
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_db_structure import DatabaseMigrator


def create_test_database_with_typo(db_path):
    """Create a test database with a column name typo (e.g., 'prnom' instead of 'prenom')."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            prnom TEXT,
            emial TEXT
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO membres (name, prnom, emial) VALUES (?, ?, ?)", 
                   ("Dupont", "Jean", "jean@example.com"))
    
    conn.commit()
    conn.close()


def create_yaml_hints(yaml_path):
    """Create a test YAML hints file."""
    hints = {
        "schema_version": "1.0",
        "generated_by": "test",
        "tables": {
            "membres": {
                "expected_columns": {
                    "id": {"type": "INTEGER", "inferred": False},
                    "name": {"type": "TEXT", "inferred": False},
                    "prenom": {"type": "TEXT", "inferred": True},
                    "email": {"type": "TEXT", "inferred": True},
                    "telephone": {"type": "TEXT", "inferred": True},
                }
            }
        }
    }
    
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(hints, f, default_flow_style=False, allow_unicode=True)


def test_fuzzy_column_matching():
    """Test fuzzy matching of column names."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database_with_typo(db_path)
        migrator = DatabaseMigrator(db_path, use_yaml_hints=False)
        
        # Test fuzzy match
        existing_cols = {"id", "name", "prnom", "emial"}
        
        # Should find "prnom" for "prenom"
        match = migrator.fuzzy_match_column("prenom", existing_cols)
        assert match == "prnom", f"Expected 'prnom', got {match}"
        
        # Should find "emial" for "email"
        match = migrator.fuzzy_match_column("email", existing_cols)
        assert match == "emial", f"Expected 'emial', got {match}"
        
        # Should not match unrelated columns
        match = migrator.fuzzy_match_column("telephone", existing_cols)
        assert match is None, f"Expected None, got {match}"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_case_insensitive_matching():
    """Test case-insensitive column matching."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_table (
                ID INTEGER PRIMARY KEY,
                Name TEXT,
                EMail TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        migrator = DatabaseMigrator(db_path, use_yaml_hints=False)
        existing_cols = {"ID", "Name", "EMail"}
        
        # Should find exact match (case-insensitive)
        match = migrator.fuzzy_match_column("id", existing_cols)
        assert match == "ID"
        
        match = migrator.fuzzy_match_column("name", existing_cols)
        assert match == "Name"
        
        match = migrator.fuzzy_match_column("email", existing_cols)
        assert match == "EMail"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_yaml_hints_loading():
    """Test loading schema hints from YAML."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode='w') as yaml_tmp:
        yaml_path = yaml_tmp.name
    
    try:
        create_test_database_with_typo(db_path)
        create_yaml_hints(yaml_path)
        
        migrator = DatabaseMigrator(db_path, use_yaml_hints=True)
        success = migrator.load_schema_hints(yaml_path)
        
        assert success is True
        assert migrator.schema_hints is not None
        assert "tables" in migrator.schema_hints
        assert "membres" in migrator.schema_hints["tables"]
        
        # Test getting column type from hints
        col_type = migrator.get_column_type_from_hints("membres", "email")
        assert col_type == "TEXT"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)


def test_column_rename_support_check():
    """Test checking SQLite RENAME COLUMN support."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        create_test_database_with_typo(db_path)
        migrator = DatabaseMigrator(db_path, use_yaml_hints=False)
        
        conn = sqlite3.connect(db_path)
        supports_rename = migrator.check_rename_column_support(conn)
        conn.close()
        
        # Modern SQLite should support RENAME COLUMN
        assert isinstance(supports_rename, bool)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_migration_with_fuzzy_match_and_rename():
    """Test migration with fuzzy matching and column renaming."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode='w') as yaml_tmp:
        yaml_path = yaml_tmp.name
    
    try:
        create_test_database_with_typo(db_path)
        create_yaml_hints(yaml_path)
        
        migrator = DatabaseMigrator(db_path, use_yaml_hints=True)
        migrator.load_schema_hints(yaml_path)
        migrator.create_backup()
        
        conn = sqlite3.connect(db_path)
        
        # Check SQLite version for RENAME support
        supports_rename = migrator.check_rename_column_support(conn)
        
        existing_schema = migrator.get_existing_schema(conn)
        missing = migrator.detect_missing_columns(existing_schema)
        
        # Should detect missing columns with fuzzy matches
        assert "membres" in missing
        
        # Find the entries for prenom and email
        membres_missing = missing["membres"]
        prenom_entry = next((e for e in membres_missing if e[0] == "prenom"), None)
        email_entry = next((e for e in membres_missing if e[0] == "email"), None)
        
        assert prenom_entry is not None, "prenom should be detected as missing"
        assert prenom_entry[3] == "prnom", "Should find 'prnom' as fuzzy match for 'prenom'"
        
        assert email_entry is not None, "email should be detected as missing"
        assert email_entry[3] == "emial", "Should find 'emial' as fuzzy match for 'email'"
        
        # Apply migrations
        success = migrator.apply_migrations(conn, missing)
        assert success is True
        
        # Verify the result
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(membres)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Should have correct column names now
        assert "prenom" in columns or "prnom" in columns
        assert "email" in columns or "emial" in columns
        
        # If rename was supported, old names should be gone
        if supports_rename:
            assert "prenom" in columns, "prenom should exist after rename"
            assert "email" in columns, "email should exist after rename"
        
        # Verify data preservation
        cursor.execute("SELECT name FROM membres WHERE id = 1")
        row = cursor.fetchone()
        assert row[0] == "Dupont", "Data should be preserved"
        
        conn.close()
        
        # Clean up backup
        if migrator.backup_path and os.path.exists(migrator.backup_path):
            os.unlink(migrator.backup_path)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)


def test_migration_without_yaml_hints():
    """Test that migration still works without YAML hints (using only REFERENCE_SCHEMA)."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercice TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Run migration without YAML hints
        migrator = DatabaseMigrator(db_path, use_yaml_hints=False)
        success = migrator.run_migration()
        
        # Should still work using REFERENCE_SCHEMA
        assert success is True
        
        # Verify columns were added
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(config)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        
        # Should have added missing columns from REFERENCE_SCHEMA
        assert "date" in columns
        assert "but_asso" in columns
        
        # Clean up
        if migrator.backup_path and os.path.exists(migrator.backup_path):
            os.unlink(migrator.backup_path)
        if migrator.report_path and os.path.exists(migrator.report_path):
            os.unlink(migrator.report_path)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_type_inference():
    """Test that column types are correctly inferred from YAML hints."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode='w') as yaml_tmp:
        yaml_path = yaml_tmp.name
    
    try:
        # Create a minimal database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
        
        # Create YAML with various types
        hints = {
            "schema_version": "1.0",
            "tables": {
                "test_table": {
                    "expected_columns": {
                        "id": {"type": "INTEGER", "inferred": False},
                        "montant": {"type": "REAL", "inferred": True},
                        "quantite": {"type": "INTEGER", "inferred": True},
                        "description": {"type": "TEXT", "inferred": True},
                    }
                }
            }
        }
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(hints, f)
        
        migrator = DatabaseMigrator(db_path, use_yaml_hints=True)
        migrator.load_schema_hints(yaml_path)
        
        # Check type retrieval
        assert migrator.get_column_type_from_hints("test_table", "montant") == "REAL"
        assert migrator.get_column_type_from_hints("test_table", "quantite") == "INTEGER"
        assert migrator.get_column_type_from_hints("test_table", "description") == "TEXT"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)


if __name__ == "__main__":
    # Run tests
    test_fuzzy_column_matching()
    print("✓ test_fuzzy_column_matching")
    
    test_case_insensitive_matching()
    print("✓ test_case_insensitive_matching")
    
    test_yaml_hints_loading()
    print("✓ test_yaml_hints_loading")
    
    test_column_rename_support_check()
    print("✓ test_column_rename_support_check")
    
    test_migration_with_fuzzy_match_and_rename()
    print("✓ test_migration_with_fuzzy_match_and_rename")
    
    test_migration_without_yaml_hints()
    print("✓ test_migration_without_yaml_hints")
    
    test_type_inference()
    print("✓ test_type_inference")
    
    print("\nAll smart migration tests passed!")
