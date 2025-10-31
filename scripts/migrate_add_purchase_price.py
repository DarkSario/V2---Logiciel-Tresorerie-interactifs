#!/usr/bin/env python3
"""
Migration script to add purchase_price column to buvette_articles table.
This script is idempotent - it can be run multiple times safely.

Features:
- Automatic database backup before migration
- Table existence detection with clear error messages
- Adds purchase_price column if missing
- Enables WAL mode for better concurrency
- Transaction-based operations with error handling
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

# Add parent directory to path to import db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db import get_db_file

def backup_database(db_path):
    """
    Create a backup of the database file.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        str: Path to the backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.{timestamp}.bak"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ Error creating backup: {e}")
        raise

def enable_wal_mode(conn):
    """
    Enable WAL (Write-Ahead Logging) mode for better concurrency.
    
    Args:
        conn: SQLite connection
    """
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        result = cursor.fetchone()
        print(f"✓ WAL mode enabled: {result[0]}")
        
        cursor.execute("PRAGMA synchronous=NORMAL;")
        print(f"✓ Synchronous mode set to NORMAL for better performance")
    except Exception as e:
        print(f"⚠ Warning: Could not enable WAL mode: {e}")

def migrate_add_purchase_price():
    """
    Add purchase_price column to buvette_articles if it doesn't exist.
    This is a non-destructive migration with automatic backup.
    """
    db_path = get_db_file()
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"✗ Error: Database file not found at {db_path}")
        print("  Please ensure the database has been initialized.")
        return False
    
    print(f"Database location: {db_path}")
    
    # Create backup
    try:
        backup_path = backup_database(db_path)
    except Exception as e:
        print(f"✗ Failed to create backup. Migration aborted for safety.")
        return False
    
    conn = None
    try:
        # Connect with a reasonable timeout
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # Check if buvette_articles table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='buvette_articles'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("✗ Error: Table 'buvette_articles' does not exist.")
            print("  Please initialize the database first using init_db.py")
            conn.rollback()
            conn.close()
            return False
        
        print("✓ Table 'buvette_articles' found")
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(buvette_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "purchase_price" in columns:
            print("✓ Column 'purchase_price' already exists in buvette_articles table.")
            conn.rollback()  # No changes needed
            conn.close()
            print("\n✓ No migration needed - database is already up to date")
            return True
        
        # Add the column
        print("→ Adding 'purchase_price' column to buvette_articles table...")
        cursor.execute("ALTER TABLE buvette_articles ADD COLUMN purchase_price REAL")
        
        # Commit the transaction
        conn.commit()
        print("✓ Successfully added 'purchase_price' column")
        
        # Enable WAL mode for better concurrency
        print("\n→ Optimizing database for better concurrency...")
        enable_wal_mode(conn)
        
        conn.close()
        
        print(f"\n✓ Migration completed successfully!")
        print(f"  Backup saved at: {backup_path}")
        print(f"  To rollback, restore from: {backup_path}")
        
        return True
        
    except sqlite3.OperationalError as e:
        error_msg = str(e).lower()
        if "database is locked" in error_msg:
            print(f"✗ Error: Database is currently locked by another process")
            print("  Please close all applications using the database and try again")
        elif "no such table" in error_msg:
            print(f"✗ Error: Table 'buvette_articles' does not exist")
            print("  Please initialize the database first")
        else:
            print(f"✗ SQLite error: {e}")
        
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error during migration: {e}")
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Database Migration: Add purchase_price column")
    print("=" * 70)
    print()
    
    success = migrate_add_purchase_price()
    
    print()
    print("=" * 70)
    if success:
        print("✓ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        sys.exit(0)
    else:
        print("✗ MIGRATION FAILED")
        print("=" * 70)
        sys.exit(1)
