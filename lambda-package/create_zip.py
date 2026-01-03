"""
Script Python pour créer le package ZIP Lambda
"""

import os
import zipfile
from pathlib import Path

def create_lambda_package():
    """Crée le package ZIP pour Lambda"""
    
    # Répertoire de base
    base_dir = Path(__file__).parent
    zip_path = base_dir / "lambda-deploy.zip"
    
    # Exclusions
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.git',
        '*.md',
        'deploy.*',
        'test_*.py',
        'create_zip.py',
        'lambda-deploy.zip',
        '.pytest_cache',
        '*.log'
    ]
    
    print("Creation du package Lambda...")
    
    # Supprimer l'ancien ZIP
    if zip_path.exists():
        zip_path.unlink()
        print("   Ancien ZIP supprime")
    
    # Créer le nouveau ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter tous les fichiers nécessaires
        for root, dirs, files in os.walk(base_dir):
            # Exclure les dossiers à ignorer
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(base_dir)
                
                # Vérifier les exclusions
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(relative_path) or relative_path.match(pattern):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    zipf.write(file_path, relative_path)
                    print(f"   Ajoute: {relative_path}")
    
    # Afficher la taille
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nPackage cree: {size_mb:.2f}MB")
    print(f"   Fichier: {zip_path}")
    
    if size_mb > 50:
        print("ATTENTION: Le package depasse 50MB (limite Lambda)")
    else:
        print("Taille OK (< 50MB)")

if __name__ == '__main__':
    create_lambda_package()

