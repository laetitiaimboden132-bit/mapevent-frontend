"""
Script pour créer le package Lambda complet avec dépendances
"""

import os
import zipfile
from pathlib import Path

def create_full_lambda_package():
    """Crée le package ZIP complet pour Lambda avec dépendances"""
    
    base_dir = Path(__file__).parent
    zip_path = base_dir / "lambda-deploy-full.zip"
    
    # Exclusions
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.git',
        '*.md',
        'deploy.*',
        'test_*.py',
        'create_*.py',
        'lambda-deploy*.zip',
        '.pytest_cache',
        '*.log',
        '*.dist-info',
        '*.egg-info'
    ]
    
    print("Creation du package Lambda complet...")
    
    # Supprimer l'ancien ZIP
    if zip_path.exists():
        zip_path.unlink()
        print("   Ancien ZIP supprime")
    
    # Créer le nouveau ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter tous les fichiers du projet
        for root, dirs, files in os.walk(base_dir):
            # Exclure les dossiers à ignorer
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', 'python']]
            
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
                    if 'backend' in str(relative_path) or 'handler' in str(relative_path):
                        print(f"   Ajoute: {relative_path}")
        
        # Ajouter les dépendances Python si elles existent
        python_dir = base_dir / "python"
        if python_dir.exists():
            print("   Ajout des dependances Python...")
            for root, dirs, files in os.walk(python_dir):
                # Exclure les fichiers inutiles
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '*.dist-info', '*.egg-info']]
                
                for file in files:
                    if file.endswith(('.pyc', '.pyo')):
                        continue
                    
                    file_path = Path(root) / file
                    # Garder la structure python/lib/python3.12/site-packages
                    relative_path = file_path.relative_to(base_dir)
                    
                    zipf.write(file_path, relative_path)
    
    # Afficher la taille
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nPackage complet cree: {size_mb:.2f}MB")
    print(f"   Fichier: {zip_path}")
    
    if size_mb > 250:
        print("ATTENTION: Le package depasse 250MB (limite Lambda decompresse)")
    elif size_mb > 50:
        print("ATTENTION: Le package depasse 50MB (limite Lambda compresse)")
        print("   Considerer l'utilisation d'un Lambda Layer")
    else:
        print("Taille OK (< 50MB)")

if __name__ == '__main__':
    create_full_lambda_package()





