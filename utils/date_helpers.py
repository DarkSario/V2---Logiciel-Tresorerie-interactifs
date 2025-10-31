from datetime import datetime

def parse_date(date_str, formats=None):
    """
    Tente de parser une chaîne de date dans plusieurs formats usuels.
    Retourne un objet datetime ou None si échec.
    """
    if not formats:
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d.%m.%Y",
        ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return None

def format_date(date_obj, fmt="%Y-%m-%d"):
    """
    Formate un objet date/datetime en chaîne selon le format fourni.
    """
    if not date_obj:
        return ""
    return date_obj.strftime(fmt)

def is_date_valid(date_str, formats=None):
    """
    Vérifie si la chaîne est une date valide dans au moins un format connu.
    """
    return parse_date(date_str, formats) is not None

def today(fmt="%Y-%m-%d"):
    """
    Retourne la date du jour au format spécifié.
    """
    return datetime.today().strftime(fmt)