from utils.validation import sanitize_string

def sanitize_row(row: dict) -> dict:
    return {k: sanitize_string(v) if isinstance(v, str) else v for k, v in row.items()}
