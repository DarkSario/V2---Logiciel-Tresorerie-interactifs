import zipfile
import os

def zip_directory(source_dir, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                arc_path = os.path.relpath(abs_path, start=source_dir)
                zipf.write(abs_path, arc_path)

def extract_zip(zip_path, dest_dir):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(dest_dir)