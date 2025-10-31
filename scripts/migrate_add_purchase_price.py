#!/usr/bin/env python3
"""
Migration script to add purchase_price column to buvette_articles table.
This script is idempotent - it can be run multiple times safely.
"""

import sqlite3
import os
import sys

# Add parent directory to path to import db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db import get_connection, get_db_file
from utils.app_logger import get_logger

logger = get_logger("migration_purchase_price")

def migrate_add_purchase_price():
    """
    Add purchase_price column to buvette_articles if it doesn't exist.
    This is a non-destructive migration.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(buvette_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "purchase_price" in columns:
            logger.info("Column 'purchase_price' already exists in buvette_articles table.")
            print("✓ Column 'purchase_price' already exists in buvette_articles table.")
            conn.close()
            return True
        
        # Add the column
        logger.info("Adding 'purchase_price' column to buvette_articles table...")
        print("Adding 'purchase_price' column to buvette_articles table...")
        cursor.execute("ALTER TABLE buvette_articles ADD COLUMN purchase_price REAL")
        conn.commit()
        
        logger.info("Successfully added 'purchase_price' column to buvette_articles table.")
        print("✓ Successfully added 'purchase_price' column to buvette_articles table.")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            logger.error(f"Table buvette_articles does not exist: {e}")
            print(f"✗ Error: Table buvette_articles does not exist. Please initialize the database first.")
            return False
        else:
            logger.error(f"SQLite error during migration: {e}")
            print(f"✗ SQLite error: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print(f"Running migration on database: {get_db_file()}")
    print("-" * 60)
    
    success = migrate_add_purchase_price()
    
    print("-" * 60)
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed. Please check the logs.")
        sys.exit(1)
