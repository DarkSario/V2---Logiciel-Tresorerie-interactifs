"""
Database helper module for articles management (buvette_articles).

This module provides database operations for managing articles in the buvette system.
Functions include:
- get_all_articles: Retrieve all articles
- get_article_by_id: Get a specific article by ID
- get_article_by_name: Get a specific article by name
- create_article: Create a new article
- update_article_stock: Update the stock quantity of an article
- update_article_purchase_price: Update the purchase price of an article
"""

import sqlite3
from db.db import get_connection
from utils.app_logger import get_logger

logger = get_logger("db_articles")

def get_conn():
    """Get a database connection with Row factory."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

def get_all_articles():
    """
    Retrieve all articles from buvette_articles table.
    
    Returns:
        list: List of article rows as sqlite3.Row objects
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, categorie, unite, contenance, commentaire, stock, purchase_price
            FROM buvette_articles
            ORDER BY name
        """)
        articles = cursor.fetchall()
        conn.close()
        return articles
    except Exception as e:
        logger.error(f"Error fetching all articles: {e}")
        raise

def get_article_by_id(article_id):
    """
    Get a specific article by its ID.
    
    Args:
        article_id (int): The ID of the article
        
    Returns:
        sqlite3.Row or None: The article row if found, None otherwise
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, categorie, unite, contenance, commentaire, stock, purchase_price
            FROM buvette_articles
            WHERE id = ?
        """, (article_id,))
        article = cursor.fetchone()
        conn.close()
        return article
    except Exception as e:
        logger.error(f"Error fetching article by id {article_id}: {e}")
        raise

def get_article_by_name(name):
    """
    Get a specific article by its name.
    
    Args:
        name (str): The name of the article
        
    Returns:
        sqlite3.Row or None: The article row if found, None otherwise
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, categorie, unite, contenance, commentaire, stock, purchase_price
            FROM buvette_articles
            WHERE name = ?
        """, (name,))
        article = cursor.fetchone()
        conn.close()
        return article
    except Exception as e:
        logger.error(f"Error fetching article by name '{name}': {e}")
        raise

def create_article(name, categorie, unite=None, contenance=None, commentaire=None, stock=0, purchase_price=None):
    """
    Create a new article in the database.
    
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
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO buvette_articles (name, categorie, unite, contenance, commentaire, stock, purchase_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, categorie, unite, contenance, commentaire, stock, purchase_price))
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Created article '{name}' with id {article_id}")
        return article_id
    except Exception as e:
        logger.error(f"Error creating article '{name}': {e}")
        raise

def update_article_stock(article_id, stock):
    """
    Update the stock quantity of an article.
    
    Args:
        article_id (int): The ID of the article
        stock (int): The new stock quantity
        
    Returns:
        bool: True if successful
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE buvette_articles
            SET stock = ?
            WHERE id = ?
        """, (stock, article_id))
        conn.commit()
        conn.close()
        logger.info(f"Updated stock for article id {article_id} to {stock}")
        return True
    except Exception as e:
        logger.error(f"Error updating stock for article id {article_id}: {e}")
        raise

def update_article_purchase_price(article_id, purchase_price):
    """
    Update the purchase price of an article.
    
    Args:
        article_id (int): The ID of the article
        purchase_price (float): The new purchase price per unit
        
    Returns:
        bool: True if successful
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE buvette_articles
            SET purchase_price = ?
            WHERE id = ?
        """, (purchase_price, article_id))
        conn.commit()
        conn.close()
        logger.info(f"Updated purchase_price for article id {article_id} to {purchase_price}")
        return True
    except Exception as e:
        logger.error(f"Error updating purchase_price for article id {article_id}: {e}")
        raise
