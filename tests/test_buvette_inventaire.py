import unittest
import sqlite3
import os
import sys

# Mock tkinter before any imports that might use it
sys.modules['tkinter'] = type(sys)('tkinter')
sys.modules['tkinter.messagebox'] = type(sys)('messagebox')

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Simple database helper functions to avoid WAL mode issues
def get_test_connection(db_file):
    """Create a simple connection without WAL mode for testing."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


class TestBuvetteInventaire(unittest.TestCase):
    """Test suite for buvette inventaire database operations."""
    
    def setUp(self):
        """Set up a fresh test database before each test."""
        self.test_db = f"/tmp/test_buvette_inventaire_{id(self)}.db"
        
        # Create the tables
        conn = get_test_connection(self.test_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buvette_inventaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_inventaire DATE,
                event_id INTEGER,
                type_inventaire TEXT CHECK(type_inventaire IN ('avant', 'apres', 'hors_evenement')),
                commentaire TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buvette_inventaire_lignes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventaire_id INTEGER,
                article_id INTEGER,
                quantite INTEGER,
                commentaire TEXT,
                FOREIGN KEY (inventaire_id) REFERENCES buvette_inventaires(id),
                FOREIGN KEY (article_id) REFERENCES buvette_articles(id)
            )
        """)
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        # Clean up any WAL files
        for ext in ['-wal', '-shm']:
            wal_file = self.test_db + ext
            if os.path.exists(wal_file):
                try:
                    os.remove(wal_file)
                except:
                    pass
    
    def test_insert_inventaire_with_valid_type_hors_evenement(self):
        """Test inserting an inventory with type 'hors_evenement' does not raise IntegrityError."""
        conn = get_test_connection(self.test_db)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
            VALUES (?, ?, ?, ?)
        """, ('2025-01-15', None, 'hors_evenement', 'Test inventory'))
        inv_id = cur.lastrowid
        conn.commit()
        
        self.assertIsNotNone(inv_id)
        self.assertGreater(inv_id, 0)
        
        # Verify it was inserted correctly
        cur.execute("SELECT * FROM buvette_inventaires WHERE id=?", (inv_id,))
        inv = cur.fetchone()
        conn.close()
        
        self.assertIsNotNone(inv)
        self.assertEqual(inv['date_inventaire'], '2025-01-15')
        self.assertEqual(inv['type_inventaire'], 'hors_evenement')
        self.assertEqual(inv['commentaire'], 'Test inventory')
        self.assertIsNone(inv['event_id'])
    
    def test_insert_inventaire_with_valid_type_avant(self):
        """Test inserting an inventory with type 'avant'."""
        conn = get_test_connection(self.test_db)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
            VALUES (?, ?, ?, ?)
        """, ('2025-01-16', None, 'avant', 'Before event'))
        inv_id = cur.lastrowid
        conn.commit()
        
        cur.execute("SELECT * FROM buvette_inventaires WHERE id=?", (inv_id,))
        inv = cur.fetchone()
        conn.close()
        
        self.assertEqual(inv['type_inventaire'], 'avant')
    
    def test_insert_inventaire_with_valid_type_apres(self):
        """Test inserting an inventory with type 'apres'."""
        conn = get_test_connection(self.test_db)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
            VALUES (?, ?, ?, ?)
        """, ('2025-01-17', None, 'apres', 'After event'))
        inv_id = cur.lastrowid
        conn.commit()
        
        cur.execute("SELECT * FROM buvette_inventaires WHERE id=?", (inv_id,))
        inv = cur.fetchone()
        conn.close()
        
        self.assertEqual(inv['type_inventaire'], 'apres')
    
    def test_insert_inventaire_with_invalid_type_raises_error(self):
        """Test that inserting an inventory with invalid type raises IntegrityError."""
        conn = get_test_connection(self.test_db)
        with self.assertRaises(sqlite3.IntegrityError) as context:
            conn.execute("""
                INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
                VALUES (?, ?, ?, ?)
            """, ('2025-01-18', None, 'invalid_type', 'Should fail'))
            conn.commit()
        conn.close()
        
        self.assertIn('CHECK constraint', str(context.exception))
    
    def test_update_inventaire_with_valid_type(self):
        """Test updating an inventory with a valid type."""
        conn = get_test_connection(self.test_db)
        cur = conn.cursor()
        
        # First insert an inventory
        cur.execute("""
            INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
            VALUES (?, ?, ?, ?)
        """, ('2025-01-20', None, 'hors_evenement', 'Original'))
        inv_id = cur.lastrowid
        conn.commit()
        
        # Update it
        cur.execute("""
            UPDATE buvette_inventaires SET date_inventaire=?, event_id=?, type_inventaire=?, commentaire=?
            WHERE id=?
        """, ('2025-01-21', None, 'avant', 'Updated', inv_id))
        conn.commit()
        
        # Verify the update
        cur.execute("SELECT * FROM buvette_inventaires WHERE id=?", (inv_id,))
        inv = cur.fetchone()
        conn.close()
        
        self.assertEqual(inv['date_inventaire'], '2025-01-21')
        self.assertEqual(inv['type_inventaire'], 'avant')
        self.assertEqual(inv['commentaire'], 'Updated')
    
    def test_update_inventaire_with_invalid_type_raises_error(self):
        """Test that updating an inventory with invalid type raises IntegrityError."""
        conn = get_test_connection(self.test_db)
        cur = conn.cursor()
        
        # First insert an inventory
        cur.execute("""
            INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
            VALUES (?, ?, ?, ?)
        """, ('2025-01-22', None, 'hors_evenement', 'Original'))
        inv_id = cur.lastrowid
        conn.commit()
        
        # Try to update with invalid type
        with self.assertRaises(sqlite3.IntegrityError) as context:
            cur.execute("""
                UPDATE buvette_inventaires SET date_inventaire=?, event_id=?, type_inventaire=?, commentaire=?
                WHERE id=?
            """, ('2025-01-23', None, 'invalid_update', 'Should fail', inv_id))
            conn.commit()
        
        conn.close()
        self.assertIn('CHECK constraint', str(context.exception))
    
    def test_list_inventaires(self):
        """Test listing all inventories."""
        conn = get_test_connection(self.test_db)
        cur = conn.cursor()
        
        # Insert multiple inventories
        for date, type_inv, comment in [
            ('2025-01-24', 'hors_evenement', 'First'),
            ('2025-01-25', 'avant', 'Second'),
            ('2025-01-26', 'apres', 'Third')
        ]:
            cur.execute("""
                INSERT INTO buvette_inventaires (date_inventaire, event_id, type_inventaire, commentaire)
                VALUES (?, ?, ?, ?)
            """, (date, None, type_inv, comment))
        conn.commit()
        
        # List them
        cur.execute("SELECT * FROM buvette_inventaires ORDER BY date_inventaire DESC")
        inventaires = cur.fetchall()
        conn.close()
        
        self.assertEqual(len(inventaires), 3)


if __name__ == "__main__":
    unittest.main()
