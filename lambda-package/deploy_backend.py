"""
Script Python pour déployer le backend Lambda avec la nouvelle configuration CORS
"""

import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path

def clean_old_files():
    """Nettoie les anciens fichiers"""
    print("[1/4] Nettoyage...")
    base_dir = Path(__file__).parent
    
    # Supprimer les anciens ZIP
    for zip_file in base_dir.glob("lambda-deploy*.zip"):
        zip_file.unlink()
        print(f"   Supprimé: {zip_file.name}")
    
    # Supprimer __pycache__
    for pycache in base_dir.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    
    # Supprimer les .pyc
    for pyc in base_dir.rglob("*.pyc"):
        pyc.unlink()

def install_dependencies():
    """Installe les dépendances Python"""
    print("[2/4] Installation des dependances...")
    base_dir = Path(__file__).parent
    requirements_file = base_dir / "backend" / "requirements.txt"
    
    # Créer un dossier pour les dépendances
    deps_dir = base_dir / "dependencies"
    if deps_dir.exists():
        shutil.rmtree(deps_dir)
    deps_dir.mkdir()
    
    # Installer les dépendances (sans uvloop qui ne fonctionne pas sur Windows)
    # On va installer directement dans le dossier de base pour Lambda
    try:
        # Lire requirements.txt et filtrer uvloop si présent
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        # Installer dans le dossier courant (pour Lambda)
        cmd = [
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_file),
            "-t", str(base_dir),
            "--upgrade",
            "--quiet",
            "--platform", "linux_x86_64",  # Pour Lambda Linux
            "--only-binary", ":all:",  # Utiliser seulement les binaires
            "--no-deps"  # Ne pas installer les dépendances (pour éviter uvloop)
        ]
        
        # Essayer d'abord sans --no-deps
        print("   Installation des dépendances principales...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_file),
            "-t", str(base_dir),
            "--upgrade",
            "--quiet"
        ], check=False, capture_output=True, text=True)  # Ne pas échouer si certaines dépendances échouent
        
        # Vérifier que typing_extensions est bien installé (peut être un fichier .py ou un dossier)
        typing_ext_path = base_dir / "typing_extensions"
        typing_ext_py = base_dir / "typing_extensions.py"
        if not typing_ext_path.exists() and not typing_ext_py.exists():
            print("   [WARNING] typing_extensions non trouve apres installation, installation explicite...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install",
                "typing-extensions>=4.14.1",
                "-t", str(base_dir),
                "--upgrade",
                "--quiet"
            ], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   [ERROR] Echec installation typing-extensions: {result.stderr}")
            else:
                print("   [OK] typing-extensions installe")
        
        # Vérifier à nouveau après installation
        if typing_ext_path.exists():
            print(f"   [OK] typing_extensions trouve (dossier): {typing_ext_path}")
        elif typing_ext_py.exists():
            print(f"   [OK] typing_extensions trouve (fichier): {typing_ext_py}")
        else:
            print("   [CRITICAL] typing_extensions toujours absent apres installation!")
        
    except Exception as e:
        print(f"   ATTENTION: Erreur lors de l'installation: {e}")
        print("   Continuons quand même...")

def create_zip_package():
    """Crée le package ZIP pour Lambda"""
    print("[3/4] Creation du package ZIP...")
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
        'create_*.py',
        'lambda-deploy*.zip',
        '.pytest_cache',
        '*.log',
        'dependencies',
        'layer',
        '*.dist-info',
        '*.egg-info',
        'bin',
        'include',
        'lib64',
        'share'
    ]
    
    # Supprimer l'ancien ZIP
    if zip_path.exists():
        zip_path.unlink()
    
    # Créer le nouveau ZIP
    files_added = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter handler.py et lambda_function.py à la racine
        handler_file = base_dir / "handler.py"
        if handler_file.exists():
            zipf.write(handler_file, "handler.py")
            files_added += 1
            print(f"   + handler.py")
        
        # Ajouter lambda_function.py (point d'entrée Lambda)
        lambda_function_file = base_dir / "lambda_function.py"
        if lambda_function_file.exists():
            zipf.write(lambda_function_file, "lambda_function.py")
            files_added += 1
            print(f"   + lambda_function.py")
        
        # Ajouter le dossier backend
        backend_dir = base_dir / "backend"
        if backend_dir.exists():
            for root, dirs, files in os.walk(backend_dir):
                # Exclure les dossiers
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', 'tests']]
                
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(base_dir)
                    
                    # Vérifier les exclusions
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if pattern in str(relative_path) or relative_path.match(pattern):
                            should_exclude = True
                            break
                    
                    if not should_exclude and file.endswith(('.py', '.txt', '.sql')):
                        zipf.write(file_path, relative_path)
                        files_added += 1
        
        # Ajouter typing_extensions.py si c'est un fichier (package namespace)
        typing_ext_py = base_dir / "typing_extensions.py"
        if typing_ext_py.exists():
            zipf.write(typing_ext_py, "typing_extensions.py")
            files_added += 1
            print(f"   + typing_extensions.py")
        
        # Ajouter les dépendances Python installées
        for item in base_dir.iterdir():
            if item.is_dir() and item.name not in ['backend', 'layer', 'dependencies', '__pycache__', '.git']:
                # Vérifier si c'est une dépendance Python (contient des fichiers .py ou des packages)
                has_python_files = any(item.rglob("*.py")) or any(item.rglob("*.so"))
                if has_python_files or item.name.endswith(('.dist-info', '.egg-info')):
                    # IMPORTANT: S'assurer que typing_extensions est inclus
                    if item.name == 'typing_extensions':
                        print(f"   [OK] Ajout de typing_extensions (dossier) au package...")
                    
                    for root, dirs, files in os.walk(item):
                        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'tests', 'test']]
                        
                        for file in files:
                            file_path = Path(root) / file
                            relative_path = file_path.relative_to(base_dir)
                            
                            # Exclure certains fichiers
                            if file.endswith(('.pyc', '.pyo', '.log')):
                                continue
                            
                            zipf.write(file_path, relative_path)
                            files_added += 1
        
        # Ajouter les fichiers .py isolés qui sont des packages namespace
        for py_file in base_dir.glob("*.py"):
            if py_file.name not in ['handler.py', 'lambda_function.py', 'deploy_backend.py']:
                # Vérifier si c'est déjà inclus (dans un dossier)
                already_included = False
                for name in zipf.namelist():
                    if name == py_file.name:
                        already_included = True
                        break
                if not already_included:
                    zipf.write(py_file, py_file.name)
                    files_added += 1
                    print(f"   + {py_file.name}")
    
    # Vérifier que typing_extensions est dans le ZIP (après fermeture du ZIP)
    try:
        with zipfile.ZipFile(zip_path, 'r') as check_zip:
            zip_names = check_zip.namelist()
            typing_ext_in_zip = any('typing_extensions' in name for name in zip_names)
            if typing_ext_in_zip:
                print(f"   [OK] typing_extensions verifie dans le ZIP")
            else:
                print(f"   [WARNING] typing_extensions NON trouve dans le ZIP!")
                print(f"   [INFO] Fichiers dans ZIP: {len(zip_names)} fichiers")
                print(f"   [INFO] Exemples: {zip_names[:10]}")
    except Exception as zip_check_err:
        print(f"   [WARNING] Impossible de verifier le ZIP: {zip_check_err}")
    
    # Afficher la taille
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nPackage cree: {size_mb:.2f}MB ({files_added} fichiers)")
    print(f"   Fichier: {zip_path}")
    
    if size_mb > 250:
        print("ATTENTION: Le package depasse 250MB (limite Lambda decompresse)")
    elif size_mb > 50:
        print("ATTENTION: Le package depasse 50MB (limite Lambda compresse)")
        print("   Considerer l'utilisation d'un Lambda Layer")
    else:
        print("Taille OK (< 50MB)")
    
    return zip_path

def deploy_to_lambda(zip_path):
    """Déploie le package sur AWS Lambda"""
    print("\n[4/4] Deploiement sur AWS Lambda...")
    
    function_name = "mapevent-backend"
    region = "eu-west-1"
    
    try:
        # Mettre à jour le code de la fonction
        cmd = [
            "aws", "lambda", "update-function-code",
            "--function-name", function_name,
            "--zip-file", f"fileb://{zip_path}",
            "--region", region
        ]
        
        print(f"   Commande: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("   Code mis a jour avec succes")
        
        # Attendre un peu
        import time
        print("   Attente de la mise a jour...")
        time.sleep(5)
        
        # Afficher les informations de la fonction
        print("\nInformations de la fonction:")
        cmd_info = [
            "aws", "lambda", "get-function",
            "--function-name", function_name,
            "--region", region,
            "--query", "Configuration.[FunctionName,Runtime,LastModified,CodeSize]",
            "--output", "table"
        ]
        subprocess.run(cmd_info, check=False)
        
        print("\nDeploiement termine avec succes!")
        print(f"   Fonction: {function_name}")
        print(f"   Region: {region}")
        print(f"   La nouvelle configuration CORS est maintenant active!")
        
    except subprocess.CalledProcessError as e:
        print(f"ERREUR lors du deploiement: {e}")
        print(f"   Sortie: {e.stdout}")
        print(f"   Erreur: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("ERREUR: AWS CLI n'est pas installe ou pas dans le PATH")
        print("   Installez AWS CLI: https://aws.amazon.com/cli/")
        sys.exit(1)

def main():
    """Fonction principale"""
    print("Deploiement Lambda MapEventAI Backend avec nouvelle config CORS")
    print("=" * 60)
    
    try:
        clean_old_files()
        install_dependencies()
        zip_path = create_zip_package()
        deploy_to_lambda(zip_path)
        
        print("\n" + "=" * 60)
        print("Deploiement reussi!")
        print("\nProchaines etapes:")
        print("   1. Tester la connexion Google sur https://mapevent.world")
        print("   2. Verifier que le formulaire de profil s'affiche")
        print("   3. Verifier les logs CloudWatch si necessaire")
        
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


