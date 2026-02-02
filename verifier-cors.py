#!/usr/bin/env python3
"""
Script de vérification des en-têtes CORS
Vérifie que les valeurs respectent les exigences :
- Access-Control-Allow-Origin : doit être * ou https://mapevent.world
- Access-Control-Allow-Headers : doit contenir au minimum Content-Type,Authorization
- Access-Control-Allow-Methods : doit contenir GET,POST,PUT,DELETE,OPTIONS
"""

import re
import json
from pathlib import Path

# Exigences
REQUIRED_ORIGIN_VALUES = ["*", "https://mapevent.world"]
REQUIRED_HEADERS = ["Content-Type", "Authorization"]
REQUIRED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

def check_origin(value):
    """Vérifie que Access-Control-Allow-Origin est valide"""
    if not value:
        return False, "Valeur manquante"
    
    # Nettoyer la valeur (enlever les espaces)
    value = value.strip()
    
    # Vérifier si c'est une variable Python (comme cors_origin)
    if value.startswith("cors_origin") or value.startswith("allowed_origin"):
        return True, f"Variable dynamique: {value} (à vérifier à l'exécution)"
    
    # Vérifier les valeurs exactes (avec ou sans guillemets)
    value_clean = value.strip('"\'')
    if value_clean in REQUIRED_ORIGIN_VALUES:
        return True, f"[OK] Valeur valide: {value_clean}"
    
    # Vérifier si c'est une liste Python
    if "allowed_origins" in value or "[" in value:
        return True, f"Liste d'origines: {value} (à vérifier à l'exécution)"
    
    return False, f"[ERREUR] Valeur invalide: {value} (doit etre * ou https://mapevent.world)"

def check_headers(value):
    """Vérifie que Access-Control-Allow-Headers contient les en-têtes requis"""
    if not value:
        return False, "Valeur manquante"
    
    # Nettoyer la valeur
    value = value.strip()
    
    # Extraire les en-têtes (supprimer les guillemets si présents)
    headers_str = value.strip('"\'')
    
    # Si c'est une variable Python (pas de virgule et nom de variable), on ne peut pas vérifier statiquement
    if ',' not in headers_str and (headers_str.startswith('cors_') or headers_str.startswith('allowed_') or not any(c in headers_str for c in [',', '-', ' '])):
        return True, f"Variable dynamique: {value} (a verifier a l'execution)"
    
    # Parser les en-têtes
    headers_list = [h.strip() for h in headers_str.split(",")]
    
    # Vérifier que tous les en-têtes requis sont présents
    missing = []
    for required in REQUIRED_HEADERS:
        if not any(required.lower() == h.lower() for h in headers_list):
            missing.append(required)
    
    if missing:
        return False, f"[ERREUR] En-tetes manquants: {', '.join(missing)}"
    
    return True, f"[OK] Contient tous les en-tetes requis: {', '.join(REQUIRED_HEADERS)}"

def check_methods(value):
    """Vérifie que Access-Control-Allow-Methods contient les méthodes requises"""
    if not value:
        return False, "Valeur manquante"
    
    # Nettoyer la valeur
    value = value.strip()
    
    # Extraire les méthodes (supprimer les guillemets si présents)
    methods_str = value.strip('"\'')
    
    # Si c'est une variable Python (pas de virgule et nom de variable), on ne peut pas vérifier statiquement
    if ',' not in methods_str and (methods_str.startswith('cors_') or methods_str.startswith('allowed_') or not any(c in methods_str for c in [',', '-', ' '])):
        return True, f"Variable dynamique: {value} (a verifier a l'execution)"
    
    # Parser les méthodes
    methods_list = [m.strip().upper() for m in methods_str.split(",")]
    
    # Vérifier que toutes les méthodes requises sont présentes
    missing = []
    for required in REQUIRED_METHODS:
        if required not in methods_list:
            missing.append(required)
    
    if missing:
        return False, f"[ERREUR] Methodes manquantes: {', '.join(missing)}"
    
    return True, f"[OK] Contient toutes les methodes requises: {', '.join(REQUIRED_METHODS)}"

def check_file(file_path):
    """Vérifie un fichier Python pour les en-têtes CORS"""
    print(f"\n{'='*80}")
    print(f"Vérification de: {file_path}")
    print(f"{'='*80}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {e}")
        return
    
    issues = []
    
    # Chercher tous les en-têtes CORS
    # Utiliser deux patterns : un pour les valeurs entre guillemets, un pour les variables
    for header_name in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Headers', 'Access-Control-Allow-Methods']:
        # Pattern 1: Valeur entre guillemets doubles
        pattern1 = rf'["\']{header_name}["\']\s*:\s*"([^"]+)"'
        for match in re.finditer(pattern1, content):
            line_num = content[:match.start()].count('\n') + 1
            value = match.group(1).strip()
            print(f"\n[Ligne {line_num}]: {header_name} = \"{value}\"")
            
            if header_name == 'Access-Control-Allow-Origin':
                is_valid, message = check_origin(value)
                print(f"   {message}")
                if not is_valid:
                    issues.append((line_num, header_name, value, message))
            elif header_name == 'Access-Control-Allow-Headers':
                is_valid, message = check_headers(value)
                print(f"   {message}")
                if not is_valid:
                    issues.append((line_num, header_name, value, message))
            elif header_name == 'Access-Control-Allow-Methods':
                is_valid, message = check_methods(value)
                print(f"   {message}")
                if not is_valid:
                    issues.append((line_num, header_name, value, message))
        
        # Pattern 2: Variable ou valeur sans guillemets
        pattern2 = rf'["\']{header_name}["\']\s*:\s*([^,\n}}]+)'
        for match in re.finditer(pattern2, content):
            line_num = content[:match.start()].count('\n') + 1
            value = match.group(1).strip()
            # Ignorer si c'était déjà capturé par pattern1 (contient des guillemets)
            if '"' in value or value.startswith("'") and value.endswith("'"):
                continue
            
            print(f"\n[Ligne {line_num}]: {header_name} = {value}")
            
            if header_name == 'Access-Control-Allow-Origin':
                is_valid, message = check_origin(value)
                print(f"   {message}")
                if not is_valid:
                    issues.append((line_num, header_name, value, message))
            elif header_name == 'Access-Control-Allow-Headers':
                is_valid, message = check_headers(value)
                print(f"   {message}")
                if not is_valid:
                    issues.append((line_num, header_name, value, message))
            elif header_name == 'Access-Control-Allow-Methods':
                is_valid, message = check_methods(value)
                print(f"   {message}")
                if not is_valid:
                    issues.append((line_num, header_name, value, message))
    
    # Chercher aussi dans les structures JSON
    json_pattern = r'\{[^}]*["\']Access-Control-Allow-[^}]*\}'
    json_matches = re.finditer(json_pattern, content, re.DOTALL)
    for match in json_matches:
        try:
            json_str = match.group(0)
            # Nettoyer pour JSON valide
            json_str = re.sub(r'(["\'])(\w+)\1\s*:', r'"\2":', json_str)
            data = json.loads(json_str)
            
            for key, value in data.items():
                if 'Access-Control-Allow-Origin' in key:
                    line_num = content[:match.start()].count('\n') + 1
                    print(f"\n[Ligne {line_num} (JSON)]: Access-Control-Allow-Origin = {value}")
                    is_valid, message = check_origin(str(value))
                    print(f"   {message}")
                    if not is_valid:
                        issues.append((line_num, 'Access-Control-Allow-Origin', str(value), message))
                
                elif 'Access-Control-Allow-Headers' in key:
                    line_num = content[:match.start()].count('\n') + 1
                    print(f"\n[Ligne {line_num} (JSON)]: Access-Control-Allow-Headers = {value}")
                    is_valid, message = check_headers(str(value))
                    print(f"   {message}")
                    if not is_valid:
                        issues.append((line_num, 'Access-Control-Allow-Headers', str(value), message))
                
                elif 'Access-Control-Allow-Methods' in key:
                    line_num = content[:match.start()].count('\n') + 1
                    print(f"\n[Ligne {line_num} (JSON)]: Access-Control-Allow-Methods = {value}")
                    is_valid, message = check_methods(str(value))
                    print(f"   {message}")
                    if not is_valid:
                        issues.append((line_num, 'Access-Control-Allow-Methods', str(value), message))
        except:
            pass
    
    return issues

def check_json_config(file_path):
    """Vérifie un fichier JSON de configuration CORS"""
    print(f"\n{'='*80}")
    print(f"Vérification de: {file_path}")
    print(f"{'='*80}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {e}")
        return []
    
    issues = []
    
    # Vérifier AllowOrigins
    if 'AllowOrigins' in data:
        origins = data['AllowOrigins']
        print(f"\n[AllowOrigins] = {origins}")
        if isinstance(origins, list):
            has_star = "*" in origins
            has_mapevent = "https://mapevent.world" in origins
            if not (has_star or has_mapevent):
                issues.append((0, 'AllowOrigins', str(origins), 
                             "[ERREUR] Doit contenir * ou https://mapevent.world"))
                print("   [ERREUR] Doit contenir * ou https://mapevent.world")
            else:
                print("   [OK] Contient * ou https://mapevent.world")
        else:
            is_valid, message = check_origin(str(origins))
            print(f"   {message}")
            if not is_valid:
                issues.append((0, 'AllowOrigins', str(origins), message))
    
    # Vérifier AllowHeaders
    if 'AllowHeaders' in data:
        headers = data['AllowHeaders']
        print(f"\n[AllowHeaders] = {headers}")
        if isinstance(headers, list):
            headers_lower = [h.lower() for h in headers]
            missing = []
            for required in REQUIRED_HEADERS:
                if required.lower() not in headers_lower:
                    missing.append(required)
            if missing:
                issues.append((0, 'AllowHeaders', str(headers), 
                             f"[ERREUR] En-tetes manquants: {', '.join(missing)}"))
                print(f"   [ERREUR] En-tetes manquants: {', '.join(missing)}")
            else:
                print(f"   [OK] Contient tous les en-tetes requis: {', '.join(REQUIRED_HEADERS)}")
        else:
            is_valid, message = check_headers(str(headers))
            print(f"   {message}")
            if not is_valid:
                issues.append((0, 'AllowHeaders', str(headers), message))
    
    # Vérifier AllowMethods
    if 'AllowMethods' in data:
        methods = data['AllowMethods']
        print(f"\n[AllowMethods] = {methods}")
        if isinstance(methods, list):
            methods_upper = [m.upper() if isinstance(m, str) else str(m).upper() for m in methods]
            # Si "*" est présent, c'est OK
            if "*" in methods:
                    print("   [OK] Contient * (toutes les methodes autorisees)")
            else:
                missing = []
                for required in REQUIRED_METHODS:
                    if required not in methods_upper:
                        missing.append(required)
                if missing:
                    issues.append((0, 'AllowMethods', str(methods), 
                                 f"[ERREUR] Methodes manquantes: {', '.join(missing)}"))
                    print(f"   [ERREUR] Methodes manquantes: {', '.join(missing)}")
                else:
                    print(f"   [OK] Contient toutes les methodes requises: {', '.join(REQUIRED_METHODS)}")
        else:
            is_valid, message = check_methods(str(methods))
            print(f"   {message}")
            if not is_valid:
                issues.append((0, 'AllowMethods', str(methods), message))
    
    return issues

def main():
    """Fonction principale"""
    print("="*80)
    print("VÉRIFICATION DES EN-TÊTES CORS")
    print("="*80)
    print("\nExigences:")
    print(f"  - Access-Control-Allow-Origin: doit être * ou https://mapevent.world")
    print(f"  - Access-Control-Allow-Headers: doit contenir {', '.join(REQUIRED_HEADERS)}")
    print(f"  - Access-Control-Allow-Methods: doit contenir {', '.join(REQUIRED_METHODS)}")
    
    all_issues = []
    
    # Vérifier les fichiers Python
    python_files = [
        'lambda-package/handler.py',
        'lambda-package/backend/main.py',
    ]
    
    for file_path in python_files:
        if Path(file_path).exists():
            issues = check_file(file_path)
            if issues:
                all_issues.extend(issues)
        else:
            print(f"\n⚠️  Fichier non trouvé: {file_path}")
    
    # Vérifier les fichiers JSON
    json_files = [
        'lambda-package/cors-config.json',
    ]
    
    for file_path in json_files:
        if Path(file_path).exists():
            issues = check_json_config(file_path)
            if issues:
                all_issues.extend(issues)
        else:
            print(f"\n⚠️  Fichier non trouvé: {file_path}")
    
    # Résumé
    print(f"\n{'='*80}")
    print("RÉSUMÉ")
    print(f"{'='*80}")
    
    if all_issues:
        print(f"\n[ERREUR] {len(all_issues)} probleme(s) trouve(s):\n")
        for line_num, header, value, message in all_issues:
            print(f"  Ligne {line_num}: {header} = {value}")
            print(f"    {message}\n")
    else:
        print("\n[OK] Tous les en-tetes CORS respectent les exigences!")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
