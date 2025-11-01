"""
Tests for the startup_schema_check module.
"""

import os
import sys
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock tkinter before importing startup_schema_check
sys.modules['tkinter'] = MagicMock()

from ui.startup_schema_check import (
    get_expected_schema,
    get_real_schema,
    detect_missing_columns
)


def test_get_expected_schema():
    """Test that expected schema is loaded from REFERENCE_SCHEMA."""
    expected = get_expected_schema()
    
    # Should contain tables from REFERENCE_SCHEMA
    assert isinstance(expected, dict)
    assert len(expected) > 0
    
    # Check some known tables exist
    if "events" in expected:
        assert isinstance(expected["events"], set)
        assert "id" in expected["events"]
        assert "name" in expected["events"]


def test_get_real_schema_with_database():
    """Test reading real schema from a database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create a test database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Get the schema
        schema = get_real_schema(db_path)
        
        assert "test_table" in schema
        assert "id" in schema["test_table"]
        assert "name" in schema["test_table"]
        assert "email" in schema["test_table"]
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_get_real_schema_nonexistent_database():
    """Test that get_real_schema handles nonexistent databases."""
    schema = get_real_schema("/nonexistent/database.db")
    assert schema == {}


def test_detect_missing_columns_no_missing():
    """Test when no columns are missing."""
    expected = {
        "users": {"id", "name", "email"}
    }
    real = {
        "users": {"id", "name", "email", "created_at"}
    }
    
    missing = detect_missing_columns(expected, real)
    
    # No missing columns (real has all expected columns and more)
    assert "users" not in missing or len(missing["users"]) == 0


def test_detect_missing_columns_with_missing():
    """Test when columns are missing."""
    expected = {
        "users": {"id", "name", "email", "phone"}
    }
    real = {
        "users": {"id", "name"}
    }
    
    missing = detect_missing_columns(expected, real)
    
    assert "users" in missing
    assert "email" in missing["users"]
    assert "phone" in missing["users"]


def test_detect_missing_columns_table_not_exists():
    """Test when entire table doesn't exist in real schema."""
    expected = {
        "users": {"id", "name"},
        "products": {"id", "title"}
    }
    real = {
        "users": {"id", "name"}
    }
    
    missing = detect_missing_columns(expected, real)
    
    # products table doesn't exist, so should not be in missing
    # (update_db_structure doesn't create tables)
    assert "products" not in missing


def test_detect_missing_columns_complex():
    """Test with multiple tables and various missing columns."""
    expected = {
        "config": {"id", "exercice", "date", "but_asso"},
        "membres": {"id", "name", "email", "phone"},
        "events": {"id", "name", "date"}
    }
    real = {
        "config": {"id", "exercice"},  # Missing: date, but_asso
        "membres": {"id", "name"},     # Missing: email, phone
        "events": {"id", "name", "date"}  # Complete
    }
    
    missing = detect_missing_columns(expected, real)
    
    assert "config" in missing
    assert set(missing["config"]) == {"date", "but_asso"}
    
    assert "membres" in missing
    assert set(missing["membres"]) == {"email", "phone"}
    
    # events is complete
    assert "events" not in missing or len(missing["events"]) == 0


def test_integration_with_test_database():
    """Integration test with a real test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create a test database with missing columns
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY,
                name TEXT,
                date TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Get expected schema (will include 'description' for events)
        expected = get_expected_schema()
        
        # Get real schema
        real = get_real_schema(db_path)
        
        # Detect missing columns
        missing = detect_missing_columns(expected, real)
        
        # Should detect that 'description' is missing if it's in REFERENCE_SCHEMA
        if "events" in expected and "description" in expected["events"]:
            assert "events" in missing
            assert "description" in missing["events"]
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    # Run tests
    test_get_expected_schema()
    print("✓ test_get_expected_schema")
    
    test_get_real_schema_with_database()
    print("✓ test_get_real_schema_with_database")
    
    test_get_real_schema_nonexistent_database()
    print("✓ test_get_real_schema_nonexistent_database")
    
    test_detect_missing_columns_no_missing()
    print("✓ test_detect_missing_columns_no_missing")
    
    test_detect_missing_columns_with_missing()
    print("✓ test_detect_missing_columns_with_missing")
    
    test_detect_missing_columns_table_not_exists()
    print("✓ test_detect_missing_columns_table_not_exists")
    
    test_detect_missing_columns_complex()
    print("✓ test_detect_missing_columns_complex")
    
    test_integration_with_test_database()
    print("✓ test_integration_with_test_database")
    
    print("\nAll tests passed!")
