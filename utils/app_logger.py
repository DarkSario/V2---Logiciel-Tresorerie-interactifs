import logging
import os

def get_logger(name="app", log_level="INFO", log_file="app.log"):
    """Crée et retourne un logger prêt à l'emploi pour tout le projet."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # File handler
        log_dir = "logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
            fh = logging.FileHandler(os.path.join(log_dir, log_file), encoding='utf-8')
            fh.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            pass  # Si le dossier logs n'est pas accessible, on garde la sortie console
    return logger