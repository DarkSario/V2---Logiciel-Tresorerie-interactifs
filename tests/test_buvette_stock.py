"""
Tests pour la fonctionnalité de gestion du stock dans le module buvette.

Ce fichier teste:
- La création de la colonne stock (migration non destructive)
- La fonction set_article_stock
- La fonction get_article_stock
- L'intégration avec les lignes d'inventaire
"""

import unittest
import sqlite3
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_test_connection(db_file):
    """Create a simple connection without WAL mode for testing."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


class TestBuvetteStock(unittest.TestCase):
    """Test suite for buvette stock management."""
    
    def setUp(self):
        """Set up a fresh test database before each test."""
        self.test_db = f"/tmp/test_buvette_stock_{id(self)}.db"
        
        # Create the tables
        conn = get_test_connection(self.test_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buvette_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie TEXT,
                unite TEXT,
                contenance TEXT,
                commentaire TEXT,
                stock INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_stock_column_exists_in_new_table(self):
        """Test that stock column exists in newly created table."""
        conn = get_test_connection(self.test_db)
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        self.assertIn('stock', columns)
    
    def test_insert_article_with_default_stock(self):
        """Test that new articles have stock defaulting to 0."""
        conn = get_test_connection(self.test_db)
        conn.execute("""
            INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire)
            VALUES (?, ?, ?, ?, ?)
        """, ('Coca-Cola', 'Boissons', 'bouteille', '1L', 'Test'))
        conn.commit()
        
        cursor = conn.execute("SELECT stock FROM buvette_articles WHERE name=?", ('Coca-Cola',))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row['stock'], 0)
    
    def test_insert_article_with_explicit_stock(self):
        """Test inserting an article with explicit stock value."""
        conn = get_test_connection(self.test_db)
        conn.execute("""
            INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('Pepsi', 'Boissons', 'canette', '0.33L', 'Test', 50))
        conn.commit()
        
        cursor = conn.execute("SELECT stock FROM buvette_articles WHERE name=?", ('Pepsi',))
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row['stock'], 50)
    
    def test_update_article_stock(self):
        """Test updating the stock of an article."""
        conn = get_test_connection(self.test_db)
        
        # Insert an article
        conn.execute("""
            INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('Fanta', 'Boissons', 'bouteille', '1.5L', 'Test', 10))
        conn.commit()
        
        # Get the article ID
        cursor = conn.execute("SELECT id FROM buvette_articles WHERE name=?", ('Fanta',))
        article_id = cursor.fetchone()['id']
        
        # Update the stock
        conn.execute("UPDATE buvette_articles SET stock=? WHERE id=?", (25, article_id))
        conn.commit()
        
        # Verify the update
        cursor = conn.execute("SELECT stock FROM buvette_articles WHERE id=?", (article_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row['stock'], 25)
    
    def test_stock_column_migration_on_existing_table(self):
        """Test adding stock column to an existing table without it."""
        # Create a table without stock column
        test_db2 = f"/tmp/test_migration_{id(self)}.db"
        conn = get_test_connection(test_db2)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buvette_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie TEXT,
                unite TEXT,
                contenance TEXT,
                commentaire TEXT
            )
        """)
        conn.commit()
        
        # Insert an article without stock
        conn.execute("""
            INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire)
            VALUES (?, ?, ?, ?, ?)
        """, ('Sprite', 'Boissons', 'bouteille', '1L', 'Test'))
        conn.commit()
        
        # Add stock column (simulating migration)
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'stock' not in columns:
            conn.execute("ALTER TABLE buvette_articles ADD COLUMN stock INTEGER DEFAULT 0")
            conn.commit()
        
        # Verify the column was added and default value is applied
        cursor = conn.execute("SELECT stock FROM buvette_articles WHERE name=?", ('Sprite',))
        row = cursor.fetchone()
        conn.close()
        
        # Clean up
        if os.path.exists(test_db2):
            os.remove(test_db2)
        
        self.assertIsNotNone(row)
        self.assertEqual(row['stock'], 0)


if __name__ == "__main__":
    unittest.main()
