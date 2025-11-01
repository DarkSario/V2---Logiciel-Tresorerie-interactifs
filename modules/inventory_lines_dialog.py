"""
Helper module for loading inventory lines safely.

This module provides robust functions for loading inventory data with proper
error handling and reporting. It ensures that sqlite3.Row objects are properly
converted to dictionaries before any .get() operations are performed.

Functions:
    load_inventory_lines: Load inventory lines with error handling and reporting
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.app_logger import get_logger
from modules.db_row_utils import _row_to_dict, _rows_to_dicts
from modules.buvette_inventaire_db import list_lignes_inventaire as _list_lignes_inventaire

logger = get_logger("inventory_lines_dialog")


def load_inventory_lines(inventaire_id: int) -> List[Dict[str, Any]]:
    """
    Load inventory lines with robust error handling and conversion.
    
    This function:
    1. Fetches inventory lines from the database
    2. Converts sqlite3.Row objects to dicts using _rows_to_dicts
    3. Handles errors gracefully with detailed reporting
    4. Writes error reports to reports/inventory_error_<timestamp>.txt on failure
    
    Args:
        inventaire_id: The ID of the inventory to load lines for
        
    Returns:
        List of dicts representing inventory lines, with keys:
        - id: line ID
        - inventaire_id: inventory ID
        - article_id: article ID
        - quantite: quantity counted
        - commentaire: optional comment
        - article_name: article name (from JOIN)
        
    Raises:
        Exception: Re-raises any exception after writing an error report
        
    Example:
        >>> try:
        >>>     lines = load_inventory_lines(inventory_id=42)
        >>>     for line in lines:
        >>>         article_id = line.get('article_id', 0)
        >>>         quantity = line.get('quantite', 0)
        >>> except Exception as e:
        >>>     logger.error(f"Failed to load inventory: {e}")
    """
    raw_rows = None  # Initialize for error reporting scope
    try:
        # Fetch raw rows from database
        logger.info(f"Loading inventory lines for inventaire_id={inventaire_id}")
        raw_rows = _list_lignes_inventaire(inventaire_id)
        
        if not raw_rows:
            logger.info(f"No lines found for inventaire_id={inventaire_id}")
            return []
        
        # Convert Row objects to dicts for safe .get() access
        lines_dicts = _rows_to_dicts(raw_rows)
        
        logger.info(f"Successfully loaded {len(lines_dicts)} inventory lines")
        return lines_dicts
        
    except Exception as e:
        # Log the error
        logger.error(f"Error loading inventory lines for inventaire_id={inventaire_id}: {e}", exc_info=True)
        
        # Write detailed error report
        _write_error_report(inventaire_id, e, raw_rows)
        
        # Re-raise the exception so callers can handle it
        raise


def _write_error_report(
    inventaire_id: int, 
    error: Exception, 
    raw_rows: Optional[List] = None
) -> None:
    """
    Write a detailed error report to reports/inventory_error_<timestamp>.txt.
    
    Args:
        inventaire_id: The inventory ID that failed to load
        error: The exception that occurred
        raw_rows: Optional raw rows data for debugging (if available)
    """
    try:
        # Ensure reports directory exists
        reports_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "reports"
        )
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate error report filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"inventory_error_{timestamp}.txt"
        report_path = os.path.join(reports_dir, report_filename)
        
        # Compile error report
        report_lines = [
            "=" * 80,
            "INVENTORY LOADING ERROR REPORT",
            "=" * 80,
            f"Timestamp: {datetime.now().isoformat()}",
            f"Inventaire ID: {inventaire_id}",
            "",
            "ERROR DETAILS:",
            f"Exception Type: {type(error).__name__}",
            f"Exception Message: {str(error)}",
            "",
        ]
        
        # Add raw rows information if available
        if raw_rows is not None:
            report_lines.extend([
                "RAW ROWS DATA:",
                f"Number of rows: {len(raw_rows)}",
                f"Row type: {type(raw_rows[0]).__name__ if raw_rows else 'N/A'}",
                "",
            ])
            
            # Try to show sample data (safely)
            if raw_rows:
                report_lines.append("First row sample (if accessible):")
                try:
                    first_row = raw_rows[0]
                    # Try to convert to dict
                    row_dict = _row_to_dict(first_row)
                    if row_dict:
                        for key, value in row_dict.items():
                            report_lines.append(f"  {key}: {value}")
                    else:
                        report_lines.append(f"  Could not convert row to dict: {first_row}")
                except Exception as row_error:
                    report_lines.append(f"  Error accessing row data: {row_error}")
                report_lines.append("")
        
        report_lines.extend([
            "RECOMMENDED ACTIONS:",
            "1. Check that the database connection is properly configured",
            "2. Verify that buvette_inventaire_lignes table exists and has expected columns",
            "3. Ensure sqlite3.Row factory is properly set on database connections",
            "4. Check for any database migration issues",
            "",
            "=" * 80,
        ])
        
        # Write report to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Error report written to: {report_path}")
        
    except Exception as report_error:
        # If we can't write the report, at least log it
        logger.error(f"Failed to write error report: {report_error}")
