import csv
import os

def write_csv(filepath, data, header=None, delimiter=",", encoding="utf-8"):
    """
    Écrit des données dans un fichier CSV.
    - filepath : chemin du fichier à écrire
    - data : liste de listes (lignes)
    - header : liste des noms de colonnes (optionnel)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline='', encoding=encoding) as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter)
        if header:
            writer.writerow(header)
        writer.writerows(data)

def read_csv(filepath, delimiter=",", encoding="utf-8"):
    """
    Lit un fichier CSV et retourne une liste de lignes (chacune est une liste).
    """
    with open(filepath, "r", newline='', encoding=encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        return [row for row in reader]

def write_dicts_csv(filepath, dict_list, fieldnames, delimiter=",", encoding="utf-8"):
    """
    Écrit une liste de dictionnaires dans un CSV avec les en-têtes fournis.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline='', encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(dict_list)

def read_dicts_csv(filepath, delimiter=",", encoding="utf-8"):
    """
    Lit un CSV et retourne une liste de dictionnaires.
    """
    with open(filepath, "r", newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        return [row for row in reader]