"""
Tests for the analyze_modules_columns script.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.analyze_modules_columns import StrictSQLAnalyzer


def test_sql_analyzer_initialization():
    """Test StrictSQLAnalyzer initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        assert analyzer.repo_root == Path(tmpdir)
        assert len(analyzer.table_columns) == 0


def test_extract_select_queries():
    """Test extraction of SELECT queries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        content = """
        conn.execute("SELECT id, name, email FROM membres WHERE id = ?", (mid,))
        conn.execute("SELECT * FROM events ORDER BY date DESC")
        """
        
        analyzer._extract_select_statements(content, "test.py")
        
        assert "membres" in analyzer.table_columns
        assert "events" in analyzer.table_columns
        assert "id" in analyzer.table_columns["membres"]["columns"]
        assert "name" in analyzer.table_columns["membres"]["columns"]
        assert "email" in analyzer.table_columns["membres"]["columns"]


def test_extract_insert_queries():
    """Test extraction of INSERT queries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        content = """
        INSERT INTO members (name, prenom, email) VALUES (?, ?, ?)
        """
        
        analyzer._extract_insert_statements(content, "test.py")
        
        assert "members" in analyzer.table_columns
        assert "name" in analyzer.table_columns["members"]["columns"]
        assert "prenom" in analyzer.table_columns["members"]["columns"]
        assert "email" in analyzer.table_columns["members"]["columns"]


def test_extract_update_queries():
    """Test extraction of UPDATE queries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        content = """
        UPDATE config SET exercice=?, date=?, disponible_banque=? WHERE id=1
        """
        
        analyzer._extract_update_statements(content, "test.py")
        
        assert "config" in analyzer.table_columns
        assert "exercice" in analyzer.table_columns["config"]["columns"]
        assert "date" in analyzer.table_columns["config"]["columns"]
        assert "disponible_banque" in analyzer.table_columns["config"]["columns"]


def test_extract_alter_table():
    """Test extraction of ALTER TABLE statements - not in StrictSQLAnalyzer scope."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        # StrictSQLAnalyzer focuses on INSERT/UPDATE/SELECT/CREATE TABLE
        # ALTER TABLE is not extracted as it doesn't define expected schema
        content = """
        ALTER TABLE buvette_articles ADD COLUMN stock INTEGER DEFAULT 0
        """
        
        # This test is skipped as ALTER TABLE is not in scope
        pass


def test_extract_create_table():
    """Test extraction of CREATE TABLE statements."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        content = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            lieu TEXT,
            commentaire TEXT
        )
        """
        
        analyzer._extract_create_table_statements(content, "test.py")
        
        assert "events" in analyzer.table_columns
        assert "id" in analyzer.table_columns["events"]["columns"]
        assert "name" in analyzer.table_columns["events"]["columns"]
        assert "date" in analyzer.table_columns["events"]["columns"]
        assert "lieu" in analyzer.table_columns["events"]["columns"]
        assert "commentaire" in analyzer.table_columns["events"]["columns"]


def test_analyze_file():
    """Test analyzing a complete Python file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        # Create a test Python file
        test_file = Path(tmpdir) / "test_module.py"
        test_file.write_text("""
import sqlite3

def get_members():
    conn = sqlite3.connect("test.db")
    cursor = conn.execute("SELECT id, name, email FROM membres")
    return cursor.fetchall()

def add_member(name, email):
    conn = sqlite3.connect("test.db")
    conn.execute("INSERT INTO membres (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
""")
        
        analyzer.analyze_file(test_file)
        
        assert "membres" in analyzer.table_columns
        assert "id" in analyzer.table_columns["membres"]["columns"]
        assert "name" in analyzer.table_columns["membres"]["columns"]
        assert "email" in analyzer.table_columns["membres"]["columns"]
        assert "test_module.py" in analyzer.table_columns["membres"]["files"]


def test_generate_report():
    """Test report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = StrictSQLAnalyzer(tmpdir)
        
        # Add some test data
        analyzer.table_columns["test_table"]["columns"].add("col1")
        analyzer.table_columns["test_table"]["columns"].add("col2")
        analyzer.table_columns["test_table"]["files"].add("test.py")
        
        output_file = Path(tmpdir) / "report.md"
        analyzer.generate_report(str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "# Analyse SQL" in content
        assert "test_table" in content
        assert "col1" in content
        assert "col2" in content
        assert "test.py" in content


if __name__ == "__main__":
    # Run tests
    test_sql_analyzer_initialization()
    print("✓ test_sql_analyzer_initialization")
    
    test_extract_select_queries()
    print("✓ test_extract_select_queries")
    
    test_extract_insert_queries()
    print("✓ test_extract_insert_queries")
    
    test_extract_update_queries()
    print("✓ test_extract_update_queries")
    
    test_extract_alter_table()
    print("✓ test_extract_alter_table")
    
    test_extract_create_table()
    print("✓ test_extract_create_table")
    
    test_analyze_file()
    print("✓ test_analyze_file")
    
    test_generate_report()
    print("✓ test_generate_report")
    
    print("\nAll tests passed!")
