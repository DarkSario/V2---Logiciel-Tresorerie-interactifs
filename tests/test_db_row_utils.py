"""
Tests for modules/db_row_utils.py

This test suite validates the _row_to_dict and _rows_to_dicts utility functions.
"""

import unittest
import sqlite3
import tempfile
import os
from modules.db_row_utils import _row_to_dict, _rows_to_dicts


class TestDbRowUtils(unittest.TestCase):
    """Test suite for db_row_utils module."""
    
    def setUp(self):
        """Set up a temporary test database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create test table
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                optional_field TEXT,
                number_field INTEGER
            )
        """)
        
        # Insert test data
        cursor.execute(
            "INSERT INTO test_table (name, optional_field, number_field) VALUES (?, ?, ?)",
            ("Test Item 1", "Optional Value", 42)
        )
        cursor.execute(
            "INSERT INTO test_table (name, optional_field, number_field) VALUES (?, ?, ?)",
            ("Test Item 2", None, 100)
        )
        cursor.execute(
            "INSERT INTO test_table (name, number_field) VALUES (?, ?)",
            ("Test Item 3", 200)
        )
        
        self.conn.commit()
    
    def tearDown(self):
        """Clean up the test database."""
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_row_to_dict_basic(self):
        """Test basic conversion of sqlite3.Row to dict."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Convert to dict
        result = _row_to_dict(row)
        
        # Verify it's a dict
        self.assertIsInstance(result, dict)
        
        # Verify keys and values
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test Item 1")
        self.assertEqual(result["optional_field"], "Optional Value")
        self.assertEqual(result["number_field"], 42)
    
    def test_row_to_dict_with_get_method(self):
        """Test that converted dict supports .get() method."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM test_table WHERE id=2").fetchone()
        
        # Convert to dict
        result = _row_to_dict(row)
        
        # Test .get() with default value
        self.assertEqual(result.get("name"), "Test Item 2")
        # When a field is explicitly NULL in DB, .get() returns None (not the default)
        # because the key exists in the dict, just with None value
        self.assertIsNone(result.get("optional_field"))
        self.assertIsNone(result.get("optional_field", "default"))  # Key exists, value is None
        # For truly nonexistent keys, default is returned
        self.assertEqual(result.get("nonexistent_field", "default"), "default")
    
    def test_row_to_dict_with_none_input(self):
        """Test that _row_to_dict returns None when input is None."""
        result = _row_to_dict(None)
        self.assertIsNone(result)
    
    def test_row_to_dict_with_dict_input(self):
        """Test that _row_to_dict handles dict input (idempotent)."""
        input_dict = {"id": 1, "name": "Test", "value": 42}
        result = _row_to_dict(input_dict)
        
        # Should return the same dict
        self.assertEqual(result, input_dict)
    
    def test_rows_to_dicts_batch_conversion(self):
        """Test batch conversion of multiple rows."""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM test_table ORDER BY id").fetchall()
        
        # Convert all rows
        results = _rows_to_dicts(rows)
        
        # Verify count
        self.assertEqual(len(results), 3)
        
        # Verify all are dicts
        for result in results:
            self.assertIsInstance(result, dict)
        
        # Verify data
        self.assertEqual(results[0]["name"], "Test Item 1")
        self.assertEqual(results[1]["name"], "Test Item 2")
        self.assertEqual(results[2]["name"], "Test Item 3")
        
        # Test .get() on converted dicts
        self.assertEqual(results[0].get("optional_field"), "Optional Value")
        # When field is NULL in DB, .get() returns None (not default) because key exists
        self.assertIsNone(results[1].get("optional_field", "N/A"))
        # Use "or" operator for NULL-coalescing behavior
        self.assertEqual(results[1].get("optional_field") or "N/A", "N/A")
    
    def test_rows_to_dicts_empty_list(self):
        """Test _rows_to_dicts with empty list."""
        result = _rows_to_dicts([])
        self.assertEqual(result, [])
    
    def test_rows_to_dicts_filters_none(self):
        """Test that _rows_to_dicts filters out None values."""
        cursor = self.conn.cursor()
        row1 = cursor.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        row2 = cursor.execute("SELECT * FROM test_table WHERE id=2").fetchone()
        
        # Mix in a None value
        mixed_rows = [row1, None, row2]
        
        # Convert - should filter out None
        results = _rows_to_dicts(mixed_rows)
        
        # Should only have 2 results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[1]["id"], 2)
    
    def test_sqlite_row_bracket_access_still_works(self):
        """Test that original sqlite3.Row bracket access still works before conversion."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Before conversion, bracket access should work
        self.assertEqual(row["name"], "Test Item 1")
        self.assertEqual(row["id"], 1)
    
    def test_sqlite_row_lacks_get_method(self):
        """Verify that sqlite3.Row does not have .get() method."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Confirm Row doesn't have .get() method
        self.assertFalse(hasattr(row, "get") or callable(getattr(row, "get", None)))
    
    def test_conversion_enables_get_method(self):
        """Verify that conversion enables .get() method that was missing."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Convert to dict
        row_dict = _row_to_dict(row)
        
        # Now .get() should work
        self.assertTrue(hasattr(row_dict, "get"))
        self.assertTrue(callable(row_dict.get))
        
        # And it should work as expected
        self.assertEqual(row_dict.get("name"), "Test Item 1")
        self.assertEqual(row_dict.get("nonexistent", "default"), "default")


if __name__ == "__main__":
    unittest.main()
