"""
Script pour créer un Lambda Layer avec les dépendances
"""

import os
import zipfile
from pathlib import Path

def create_lambda_layer():
    """Crée un Lambda Layer avec les dépendances Python"""
    
    base_dir = Path(__file__).parent
    layer_dir = base_dir / "layer"
    zip_path = base_dir / "lambda-layer.zip"
    
    # Créer la structure du layer
    python_dir = layer_dir / "python" / "lib" / "python3.12" / "site-packages"
    python_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creation du Lambda Layer...")
    
    # Copier les dépendances si elles existent déjà
    deps_dir = base_dir / "python" / "lib" / "python3.12" / "site-packages"
    if deps_dir.exists():
        print("   Copie des dependances existantes...")
        import shutil
        for item in deps_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, python_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, python_dir / item.name)
    else:
        print("   Installation des dependances dans le layer...")
        import subprocess
        subprocess.run([
            "pip", "install", "-r", str(base_dir / "backend" / "requirements.txt"),
            "-t", str(python_dir),
            "--upgrade", "--quiet"
        ], check=True)
    
    # Créer le ZIP du layer
    if zip_path.exists():
        zip_path.unlink()
    
    print("   Creation du ZIP du layer...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(layer_dir):
            # Exclure les fichiers inutiles
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '*.dist-info', '*.egg-info']]
            
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    continue
                
                file_path = Path(root) / file
                # Garder la structure python/lib/python3.12/site-packages
                relative_path = file_path.relative_to(layer_dir)
                
                zipf.write(file_path, relative_path)
    
    # Afficher la taille
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nLambda Layer cree: {size_mb:.2f}MB")
    print(f"   Fichier: {zip_path}")
    
    if size_mb > 250:
        print("ATTENTION: Le layer depasse 250MB (limite Lambda)")
    elif size_mb > 50:
        print("ATTENTION: Le layer depasse 50MB (limite compresse)")
    else:
        print("Taille OK (< 50MB)")
    
    return zip_path

if __name__ == '__main__':
    create_lambda_layer()





