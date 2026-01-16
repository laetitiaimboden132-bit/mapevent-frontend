# Vérification de la couche Lambda psycopg2

## Problème
L'erreur `No module named 'psycopg2._psycopg'` persiste même après avoir ajouté la couche.

## Vérifications à faire

### 1. Vérifier que la couche est attachée
```powershell
aws lambda get-function --function-name mapevent-backend --region eu-west-1 --query 'Configuration.Layers'
```

### 2. Vérifier le contenu de la couche
La couche doit avoir cette structure :
```
python/
  lib/
    python3.12/
      site-packages/
        psycopg2/
          __init__.py
          _psycopg.so (ou _psycopg.cpython-312-x86_64-linux-gnu.so)
          ...
```

### 3. Vérifier les logs Lambda
Après avoir fait une requête, vérifiez les logs CloudWatch. Le code de debug devrait afficher :
- Si `/opt/python` existe
- Les packages dans `/opt/python/lib/python3.12/site-packages`
- Si `psycopg2` est présent

### 4. Problème possible : Structure de la couche incorrecte

Si la couche a été créée avec la mauvaise structure, il faut la recréer.

**Structure correcte pour une couche Lambda Python 3.12** :
```
python/
  lib/
    python3.12/
      site-packages/
        [packages ici]
```

**Structure incorrecte** (ne fonctionnera pas) :
```
lib/
  python3.12/
    site-packages/
      [packages ici]
```

## Solution : Recréer la couche avec la bonne structure

Si la structure est incorrecte, recréer la couche :

```powershell
cd lambda-package
.\creer-couche-auto.ps1
```

Ou manuellement avec Docker :
```powershell
# Créer la structure
mkdir psycopg2-layer-temp\python\lib\python3.12\site-packages

# Installer psycopg2 dans Docker
docker run --rm -v "${PWD}:/workspace" -w /workspace/psycopg2-layer-temp python:3.12-slim pip install --no-cache-dir psycopg2-binary==2.9.9 -t python/lib/python3.12/site-packages

# Créer le ZIP (depuis psycopg2-layer-temp)
cd psycopg2-layer-temp
Compress-Archive -Path python -DestinationPath ..\psycopg2-layer.zip
cd ..

# Publier la nouvelle version
aws lambda publish-layer-version --layer-name psycopg2-py312-mapevent --zip-file fileb://psycopg2-layer.zip --compatible-runtimes python3.12 --region eu-west-1
```

## Vérification finale

Après avoir recréé la couche, testez à nouveau. Les logs devraient montrer :
- ✅ `psycopg2 trouvé dans /opt!`
- ✅ `Application Flask créée`





