"""
Database helper module for articles management (buvette_articles).

This module provides database operations for managing articles in the buvette system.
Features:
- Short-lived connections with timeout for each operation
- Retry/backoff wrapper for "database is locked" errors
- Backward compatibility with databases lacking purchase_price column
- Exponential backoff for locked database scenarios

Functions include:
- get_all_articles: Retrieve all articles
- get_article_by_id: Get a specific article by ID
- get_article_by_name: Get a specific article by name
- create_article: Create a new article
- update_article_stock: Update the stock quantity of an article
- update_article_purchase_price: Update the purchase price of an article
"""

import sqlite3
import time
from functools import wraps
from db.db import get_db_file

# Configuration for retry logic
DEFAULT_TIMEOUT = 30.0  # seconds
MAX_RETRIES = 5
INITIAL_BACKOFF = 0.1  # seconds

def with_retry(func):
    """
    Decorator to retry database operations on lock errors with exponential backoff.
    
    Args:
        func: Function to wrap with retry logic
        
    Returns:
        Wrapped function with retry capability
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        backoff = INITIAL_BACKOFF
        
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                error_msg = str(e).lower()
                if "database is locked" in error_msg or "locked" in error_msg:
                    retries += 1
                    if retries >= MAX_RETRIES:
                        print(f"✗ Database locked after {MAX_RETRIES} retries: {e}")
                        raise
                    
                    wait_time = backoff * (2 ** (retries - 1))
                    print(f"⚠ Database locked, retrying in {wait_time:.2f}s (attempt {retries}/{MAX_RETRIES})...")
                    time.sleep(wait_time)
                else:
                    # Other operational errors should be raised immediately
                    raise
            except Exception as e:
                # Non-lock errors should be raised immediately
                raise
        
        # Should not reach here, but just in case
        raise sqlite3.OperationalError(f"Failed after {MAX_RETRIES} retries")
    
    return wrapper

def get_connection_with_timeout():
    """
    Get a short-lived database connection with proper timeout settings.
    
    Returns:
        sqlite3.Connection: Database connection with Row factory
    """
    db_path = get_db_file()
    conn = sqlite3.connect(db_path, timeout=DEFAULT_TIMEOUT)
    conn.row_factory = sqlite3.Row
    return conn

def column_exists(cursor, table, column):
    """
    Check if a column exists in a table.
    
    Args:
        cursor: Database cursor
        table: Table name
        column: Column name
        
    Returns:
        bool: True if column exists, False otherwise
    """
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

@with_retry
def get_all_articles():
    """
    Retrieve all articles from buvette_articles table.
    Uses short-lived connection with retry logic.
    
    Returns:
        list: List of article rows as sqlite3.Row objects
    """
    conn = None
    try:
        conn = get_connection_with_timeout()
        cursor = conn.cursor()
        
        # Check if purchase_price column exists for backward compatibility
        has_purchase_price = column_exists(cursor, "buvette_articles", "purchase_price")
        
        if has_purchase_price:
            cursor.execute("""
                SELECT id, name, categorie, unite, contenance, commentaire, stock, purchase_price
                FROM buvette_articles
                ORDER BY name
            """)
        else:
            # Fallback for old database schema
            cursor.execute("""
                SELECT id, name, categorie, unite, contenance, commentaire, stock
                FROM buvette_articles
                ORDER BY name
            """)
        
        articles = cursor.fetchall()
        return articles
    finally:
        if conn:
            conn.close()

@with_retry
def get_article_by_id(article_id):
    """
    Get a specific article by its ID.
    Uses short-lived connection with retry logic.
    
    Args:
        article_id (int): The ID of the article
        
    Returns:
        sqlite3.Row or None: The article row if found, None otherwise
    """
    conn = None
    try:
        conn = get_connection_with_timeout()
        cursor = conn.cursor()
        
        # Check if purchase_price column exists for backward compatibility
        has_purchase_price = column_exists(cursor, "buvette_articles", "purchase_price")
        
        if has_purchase_price:
            cursor.execute("""
                SELECT id, name, categorie, unite, contenance, commentaire, stock, purchase_price
                FROM buvette_articles
                WHERE id = ?
            """, (article_id,))
        else:
            # Fallback for old database schema
            cursor.execute("""
                SELECT id, name, categorie, unite, contenance, commentaire, stock
                FROM buvette_articles
                WHERE id = ?
            """, (article_id,))
        
        article = cursor.fetchone()
        return article
    finally:
        if conn:
            conn.close()

@with_retry
def get_article_by_name(name):
    """
    Get a specific article by its name.
    Uses short-lived connection with retry logic.
    
    Args:
        name (str): The name of the article
        
    Returns:
        sqlite3.Row or None: The article row if found, None otherwise
    """
    conn = None
    try:
        conn = get_connection_with_timeout()
        cursor = conn.cursor()
        
        # Check if purchase_price column exists for backward compatibility
        has_purchase_price = column_exists(cursor, "buvette_articles", "purchase_price")
        
        if has_purchase_price:
            cursor.execute("""
                SELECT id, name, categorie, unite, contenance, commentaire, stock, purchase_price
                FROM buvette_articles
                WHERE name = ?
            """, (name,))
        else:
            # Fallback for old database schema
            cursor.execute("""
                SELECT id, name, categorie, unite, contenance, commentaire, stock
                FROM buvette_articles
                WHERE name = ?
            """, (name,))
        
        article = cursor.fetchone()
        return article
    finally:
        if conn:
            conn.close()

@with_retry
def create_article(name, categorie, unite=None, contenance=None, commentaire=None, stock=0, purchase_price=None):
    """
    Create a new article in the database.
    Uses short-lived connection with retry logic.
    
    Args:
        name (str): Name of the article (required)
        categorie (str): Category of the article
        unite (str, optional): Unit type (e.g., "canette", "bouteille")
        contenance (str, optional): Capacity (e.g., "0.33L", "0.5L")
        commentaire (str, optional): Additional comments
        stock (int, optional): Initial stock quantity (default: 0)
        purchase_price (float, optional): Purchase price per unit
        
    Returns:
        int: The ID of the newly created article
    """
    conn = None
    try:
        conn = get_connection_with_timeout()
        cursor = conn.cursor()
        
        # Check if purchase_price column exists for backward compatibility
        has_purchase_price = column_exists(cursor, "buvette_articles", "purchase_price")
        
        if has_purchase_price:
            cursor.execute("""
                INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire, stock, purchase_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, categorie, unite, contenance, commentaire, stock, purchase_price))
        else:
            # Fallback for old database schema (ignore purchase_price)
            cursor.execute("""
                INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, categorie, unite, contenance, commentaire, stock))
        
        article_id = cursor.lastrowid
        conn.commit()
        print(f"✓ Created article '{name}' with id {article_id}")
        return article_id
    finally:
        if conn:
            conn.close()

@with_retry
def update_article_stock(article_id, stock):
    """
    Update the stock quantity of an article.
    Uses short-lived connection with retry logic.
    
    Args:
        article_id (int): The ID of the article
        stock (int): The new stock quantity
        
    Returns:
        bool: True if successful
    """
    conn = None
    try:
        conn = get_connection_with_timeout()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE buvette_articles
            SET stock = ?
            WHERE id = ?
        """, (stock, article_id))
        conn.commit()
        print(f"✓ Updated stock for article id {article_id} to {stock}")
        return True
    finally:
        if conn:
            conn.close()

@with_retry
def update_article_purchase_price(article_id, purchase_price):
    """
    Update the purchase price of an article.
    Uses short-lived connection with retry logic.
    Handles backward compatibility gracefully.
    
    Args:
        article_id (int): The ID of the article
        purchase_price (float): The new purchase price per unit
        
    Returns:
        bool: True if successful
    """
    conn = None
    try:
        conn = get_connection_with_timeout()
        cursor = conn.cursor()
        
        # Check if purchase_price column exists for backward compatibility
        has_purchase_price = column_exists(cursor, "buvette_articles", "purchase_price")
        
        if not has_purchase_price:
            print(f"⚠ Warning: Column 'purchase_price' does not exist. Please run migration script.")
            print(f"  Migration can be run with: python scripts/migrate_add_purchase_price.py")
            return False
        
        cursor.execute("""
            UPDATE buvette_articles
            SET purchase_price = ?
            WHERE id = ?
        """, (purchase_price, article_id))
        conn.commit()
        print(f"✓ Updated purchase_price for article id {article_id} to {purchase_price}")
        return True
    finally:
        if conn:
            conn.close()
