"""
Tests pour la fonctionnalité du prix d'achat dans le module buvette.

Ce fichier teste:
- La création de la colonne purchase_price (migration)
- L'insertion d'articles avec purchase_price
- La mise à jour d'articles avec purchase_price
- La récupération d'articles avec purchase_price
"""

import unittest
import sqlite3
import os


def get_test_connection(db_file):
    """Create a simple connection without WAL mode for testing."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


class TestBuvettePurchasePrice(unittest.TestCase):
    """Test suite for buvette purchase price management."""
    
    def setUp(self):
        """Set up a fresh test database before each test."""
        self.test_db = f"/tmp/test_buvette_purchase_price_{id(self)}.db"
        
        # Create the tables with purchase_price column
        conn = get_test_connection(self.test_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buvette_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                categorie TEXT,
                unite TEXT,
                contenance TEXT,
                commentaire TEXT,
                stock INTEGER DEFAULT 0,
                purchase_price REAL
            )
        """)
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_table_has_purchase_price_column(self):
        """Test that buvette_articles table has purchase_price column."""
        conn = get_test_connection(self.test_db)
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        self.assertIn('purchase_price', columns, "purchase_price column should exist")
    
    def test_insert_article_with_purchase_price(self):
        """Test inserting an article with a purchase price."""
        conn = get_test_connection(self.test_db)
        conn.execute("""
            INSERT INTO buvette_articles 
            (name, categorie, unite, commentaire, contenance, purchase_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Coca-Cola", "Boisson", "canette", "Test", "0.33L", 1.50))
        conn.commit()
        
        # Retrieve the article
        cursor = conn.execute("SELECT * FROM buvette_articles WHERE name = ?", ("Coca-Cola",))
        article = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(article, "Article should be inserted")
        self.assertEqual(article['purchase_price'], 1.50, "Purchase price should be 1.50")
    
    def test_insert_article_without_purchase_price(self):
        """Test inserting an article without a purchase price (NULL)."""
        conn = get_test_connection(self.test_db)
        conn.execute("""
            INSERT INTO buvette_articles 
            (name, categorie, unite, commentaire, contenance)
            VALUES (?, ?, ?, ?, ?)
        """, ("Fanta", "Boisson", "canette", "Test", "0.33L"))
        conn.commit()
        
        # Retrieve the article
        cursor = conn.execute("SELECT * FROM buvette_articles WHERE name = ?", ("Fanta",))
        article = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(article, "Article should be inserted")
        self.assertIsNone(article['purchase_price'], "Purchase price should be NULL")
    
    def test_update_article_purchase_price(self):
        """Test updating an article's purchase price."""
        conn = get_test_connection(self.test_db)
        
        # Insert article
        conn.execute("""
            INSERT INTO buvette_articles 
            (name, categorie, unite, commentaire, contenance, purchase_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Sprite", "Boisson", "canette", "Test", "0.33L", 1.25))
        conn.commit()
        
        # Get the article ID
        cursor = conn.execute("SELECT id FROM buvette_articles WHERE name = ?", ("Sprite",))
        article_id = cursor.fetchone()['id']
        
        # Update purchase price
        conn.execute("""
            UPDATE buvette_articles 
            SET purchase_price = ? 
            WHERE id = ?
        """, (1.75, article_id))
        conn.commit()
        
        # Verify update
        cursor = conn.execute("SELECT purchase_price FROM buvette_articles WHERE id = ?", (article_id,))
        updated_price = cursor.fetchone()['purchase_price']
        conn.close()
        
        self.assertEqual(updated_price, 1.75, "Purchase price should be updated to 1.75")
    
    def test_migration_adds_purchase_price_column(self):
        """Test that migration adds purchase_price column to existing table."""
        # Create a database with old schema (without purchase_price)
        old_db = f"/tmp/test_migration_{id(self)}.db"
        conn = get_test_connection(old_db)
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
        
        # Insert test data
        conn.execute("""
            INSERT INTO buvette_articles 
            (name, categorie, unite, commentaire, contenance, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Pepsi", "Boisson", "canette", "Old data", "0.33L", 5))
        conn.commit()
        
        # Verify purchase_price column doesn't exist
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns_before = [row[1] for row in cursor.fetchall()]
        self.assertNotIn('purchase_price', columns_before, "purchase_price should not exist before migration")
        
        # Run migration
        conn.execute("ALTER TABLE buvette_articles ADD COLUMN purchase_price REAL")
        conn.commit()
        
        # Verify purchase_price column exists
        cursor = conn.execute("PRAGMA table_info(buvette_articles)")
        columns_after = [row[1] for row in cursor.fetchall()]
        self.assertIn('purchase_price', columns_after, "purchase_price should exist after migration")
        
        # Verify old data is preserved
        cursor = conn.execute("SELECT name, stock, purchase_price FROM buvette_articles WHERE name = ?", ("Pepsi",))
        article = cursor.fetchone()
        conn.close()
        
        self.assertEqual(article['name'], "Pepsi", "Article name should be preserved")
        self.assertEqual(article['stock'], 5, "Article stock should be preserved")
        self.assertIsNone(article['purchase_price'], "Purchase price should be NULL for old data")
        
        # Cleanup
        os.remove(old_db)


if __name__ == '__main__':
    unittest.main()
