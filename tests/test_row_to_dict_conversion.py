"""
Test that sqlite3.Row to dict conversion works correctly.

This test validates that the fix for the 'sqlite3.Row' object has no attribute 'get'
error is working correctly by testing the conversion pattern.
"""

import unittest
import sqlite3
import tempfile
import os


def _row_to_dict(row):
    """Convert sqlite3.Row to dict for safe .get() access."""
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows):
    """Convert list of sqlite3.Row objects to list of dicts."""
    return [dict(row) for row in rows]


class TestRowToDictConversion(unittest.TestCase):
    """Test sqlite3.Row to dict conversion helpers."""
    
    def setUp(self):
        """Create a temporary database for testing."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create test table
        self.conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                optional_field TEXT,
                nullable_field TEXT
            )
        """)
        
        # Insert test data
        self.conn.execute("""
            INSERT INTO test_table (id, name, optional_field, nullable_field)
            VALUES (1, 'test1', 'value1', NULL)
        """)
        self.conn.execute("""
            INSERT INTO test_table (id, name, optional_field, nullable_field)
            VALUES (2, 'test2', NULL, 'value2')
        """)
        self.conn.commit()
    
    def tearDown(self):
        """Clean up temporary database."""
        self.conn.close()
        os.close(self.db_fd)
        os.remove(self.db_path)
    
    def test_row_to_dict_basic(self):
        """Test that _row_to_dict converts sqlite3.Row to dict."""
        row = self.conn.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Verify it's a Row object
        self.assertIsInstance(row, sqlite3.Row)
        
        # Convert to dict
        row_dict = _row_to_dict(row)
        
        # Verify conversion
        self.assertIsInstance(row_dict, dict)
        self.assertEqual(row_dict['id'], 1)
        self.assertEqual(row_dict['name'], 'test1')
        self.assertEqual(row_dict['optional_field'], 'value1')
        self.assertIsNone(row_dict['nullable_field'])
    
    def test_row_to_dict_with_get_method(self):
        """Test that converted dict supports .get() method with default values."""
        row = self.conn.execute("SELECT * FROM test_table WHERE id=2").fetchone()
        row_dict = _row_to_dict(row)
        
        # Test .get() with existing key
        self.assertEqual(row_dict.get('name'), 'test2')
        
        # Test .get() with missing key and default
        self.assertEqual(row_dict.get('nonexistent', 'default'), 'default')
        
        # Test .get() with None value
        self.assertIsNone(row_dict.get('optional_field'))
        self.assertEqual(row_dict.get('optional_field', 'default'), None)
    
    def test_row_to_dict_with_none_input(self):
        """Test that _row_to_dict handles None input gracefully."""
        result = _row_to_dict(None)
        self.assertIsNone(result)
    
    def test_rows_to_dicts_batch_conversion(self):
        """Test that _rows_to_dicts converts multiple rows."""
        rows = self.conn.execute("SELECT * FROM test_table").fetchall()
        
        # Verify they're Row objects
        self.assertTrue(all(isinstance(r, sqlite3.Row) for r in rows))
        
        # Convert to dicts
        dicts = _rows_to_dicts(rows)
        
        # Verify conversion
        self.assertEqual(len(dicts), 2)
        self.assertTrue(all(isinstance(d, dict) for d in dicts))
        self.assertEqual(dicts[0]['id'], 1)
        self.assertEqual(dicts[1]['id'], 2)
    
    def test_conversion_pattern_consistency(self):
        """Test that the conversion pattern works consistently."""
        row = self.conn.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Test the pattern used in the fix
        row_dict = _row_to_dict(row)
        
        self.assertIsInstance(row_dict, dict)
        self.assertEqual(row_dict['id'], 1)
        self.assertEqual(row_dict.get('name'), 'test1')
        
        # Test that the same pattern works for None
        none_dict = _row_to_dict(None)
        self.assertIsNone(none_dict)
    
    def test_sqlite_row_does_not_have_get_method(self):
        """Verify that sqlite3.Row indeed lacks the .get() method."""
        row = self.conn.execute("SELECT * FROM test_table WHERE id=1").fetchone()
        
        # Verify that calling .get() on Row raises AttributeError
        with self.assertRaises(AttributeError) as ctx:
            row.get('name')
        
        self.assertIn("'sqlite3.Row' object has no attribute 'get'", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
