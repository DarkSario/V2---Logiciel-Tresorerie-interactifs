"""
Tests for modules/inventory_lines_dialog.py

This test suite validates the load_inventory_lines function and error reporting.
"""

import unittest
import sqlite3
import tempfile
import os
import glob
from modules.inventory_lines_dialog import load_inventory_lines, _write_error_report


class TestInventoryLinesLoader(unittest.TestCase):
    """Test suite for inventory_lines_dialog module."""
    
    def setUp(self):
        """Set up a temporary test database with inventory structure."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.conn.cursor()
        
        # Create buvette_inventaires table
        cursor.execute("""
            CREATE TABLE buvette_inventaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_inventaire TEXT NOT NULL,
                event_id INTEGER,
                type_inventaire TEXT NOT NULL,
                commentaire TEXT
            )
        """)
        
        # Create buvette_inventaire_lignes table
        cursor.execute("""
            CREATE TABLE buvette_inventaire_lignes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventaire_id INTEGER NOT NULL,
                article_id INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                commentaire TEXT,
                FOREIGN KEY (inventaire_id) REFERENCES buvette_inventaires(id)
            )
        """)
        
        # Create buvette_articles table for JOIN
        cursor.execute("""
            CREATE TABLE buvette_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie TEXT,
                stock INTEGER DEFAULT 0
            )
        """)
        
        # Insert test data
        cursor.execute(
            "INSERT INTO buvette_inventaires (date_inventaire, type_inventaire, commentaire) VALUES (?, ?, ?)",
            ("2024-01-15", "hors_evenement", "Test inventory")
        )
        inventaire_id = cursor.lastrowid
        self.test_inventaire_id = inventaire_id
        
        # Insert articles
        cursor.execute("INSERT INTO buvette_articles (name, categorie, stock) VALUES (?, ?, ?)", ("Coca", "Boisson", 10))
        article1_id = cursor.lastrowid
        cursor.execute("INSERT INTO buvette_articles (name, categorie, stock) VALUES (?, ?, ?)", ("Sprite", "Boisson", 5))
        article2_id = cursor.lastrowid
        
        # Insert inventory lines
        cursor.execute(
            "INSERT INTO buvette_inventaire_lignes (inventaire_id, article_id, quantite) VALUES (?, ?, ?)",
            (inventaire_id, article1_id, 8)
        )
        cursor.execute(
            "INSERT INTO buvette_inventaire_lignes (inventaire_id, article_id, quantite) VALUES (?, ?, ?)",
            (inventaire_id, article2_id, 3)
        )
        
        self.conn.commit()
        
        # Store original DB path for mocking
        self.original_db_path = None
    
    def tearDown(self):
        """Clean up the test database."""
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
        # Clean up any error reports generated during tests
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        if os.path.exists(reports_dir):
            error_reports = glob.glob(os.path.join(reports_dir, "inventory_error_*.txt"))
            for report in error_reports:
                try:
                    os.unlink(report)
                except (OSError, IOError) as e:
                    # Log but don't fail test if cleanup fails
                    print(f"Warning: Could not remove test report {report}: {e}")
    
    def test_load_inventory_lines_returns_dicts(self):
        """Test that load_inventory_lines returns a list of dicts."""
        # Temporarily patch the db module to use our test database
        import modules.buvette_inventaire_db as db_module
        original_get_conn = db_module.get_conn
        
        def mock_get_conn():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        
        try:
            db_module.get_conn = mock_get_conn
            
            # Load inventory lines
            lines = load_inventory_lines(self.test_inventaire_id)
            
            # Verify results
            self.assertIsInstance(lines, list)
            self.assertEqual(len(lines), 2)
            
            # Verify all items are dicts
            for line in lines:
                self.assertIsInstance(line, dict)
                
            # Verify .get() method works
            self.assertEqual(lines[0].get("article_id"), 1)
            self.assertEqual(lines[0].get("quantite"), 8)
            self.assertEqual(lines[1].get("article_id"), 2)
            self.assertEqual(lines[1].get("quantite"), 3)
            
        finally:
            db_module.get_conn = original_get_conn
    
    def test_load_inventory_lines_empty(self):
        """Test loading inventory with no lines."""
        import modules.buvette_inventaire_db as db_module
        original_get_conn = db_module.get_conn
        
        def mock_get_conn():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        
        try:
            db_module.get_conn = mock_get_conn
            
            # Create empty inventory
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO buvette_inventaires (date_inventaire, type_inventaire) VALUES (?, ?)",
                ("2024-01-20", "hors_evenement")
            )
            empty_inv_id = cursor.lastrowid
            self.conn.commit()
            
            # Load empty inventory
            lines = load_inventory_lines(empty_inv_id)
            
            # Should return empty list
            self.assertEqual(lines, [])
            
        finally:
            db_module.get_conn = original_get_conn
    
    def test_write_error_report(self):
        """Test that error reports are written correctly."""
        # Create a test error
        test_error = ValueError("Test error for reporting")
        
        # Write error report
        _write_error_report(inventaire_id=999, error=test_error, raw_rows=None)
        
        # Check that report was created
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        self.assertTrue(os.path.exists(reports_dir))
        
        # Find the most recent error report
        error_reports = sorted(glob.glob(os.path.join(reports_dir, "inventory_error_*.txt")))
        self.assertGreater(len(error_reports), 0, "Error report should have been created")
        
        # Read the report
        latest_report = error_reports[-1]
        with open(latest_report, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify content
        self.assertIn("INVENTORY LOADING ERROR REPORT", content)
        self.assertIn("Inventaire ID: 999", content)
        self.assertIn("ValueError", content)
        self.assertIn("Test error for reporting", content)
        self.assertIn("RECOMMENDED ACTIONS", content)
    
    def test_load_inventory_lines_handles_errors(self):
        """Test that load_inventory_lines properly handles and reports errors."""
        import modules.buvette_inventaire_db as db_module
        original_get_conn = db_module.get_conn
        
        def mock_get_conn_error():
            raise sqlite3.OperationalError("Database is locked")
        
        try:
            db_module.get_conn = mock_get_conn_error
            
            # Attempt to load - should raise error
            with self.assertRaises(sqlite3.OperationalError):
                load_inventory_lines(self.test_inventaire_id)
            
            # Check that error report was created
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
            error_reports = glob.glob(os.path.join(reports_dir, "inventory_error_*.txt"))
            self.assertGreater(len(error_reports), 0, "Error report should have been created on failure")
            
        finally:
            db_module.get_conn = original_get_conn


if __name__ == "__main__":
    unittest.main()
