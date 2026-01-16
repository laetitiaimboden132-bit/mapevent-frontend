# Résolution définitive : Erreur psycopg2._psycopg

## Problème actuel
```
❌ Import error: No module named 'psycopg2._psycopg'
```

**Cause** : `psycopg2-binary` nécessite des binaires Linux compilés, mais l'installation sur Windows produit des binaires Windows qui ne fonctionnent pas sur Lambda.

## Solutions disponibles

### ✅ Solution 1 : Démarrer Docker Desktop (RECOMMANDÉ)

1. **Démarrer Docker Desktop** (attendre qu'il soit complètement démarré)
2. **Exécuter** :
   ```powershell
   cd lambda-package
   .\creer-couche-psycopg2.ps1
   ```
3. Le script va automatiquement :
   - Installer psycopg2-binary dans Docker (Linux)
   - Créer une couche Lambda
   - La publier et l'ajouter à votre fonction

### ✅ Solution 2 : Via AWS Console (PLUS RAPIDE)

1. **Allez sur** : https://console.aws.amazon.com/lambda/home?region=eu-west-1#/functions/mapevent-backend
2. **Onglet "Layers"** → **"Add a layer"**
3. **Choisir "Browse layers"** ou chercher une couche publique
4. **Rechercher** : `psycopg2` ou `postgresql`
5. **Sélectionner** une couche compatible Python 3.12
6. **Cliquer "Add"**

**Couches publiques recommandées** :
- Cherchez sur GitHub : `psycopg2 lambda layer python 3.12`
- Ou utilisez cette ARN (si accessible) : `arn:aws:lambda:eu-west-1:898466741470:layer:psycopg2-py312:1`

### ✅ Solution 3 : Créer la couche manuellement avec WSL

1. **Ouvrir WSL** (Ubuntu)
2. **Installer Python/pip** si nécessaire :
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
3. **Dans WSL, naviguer vers le projet** :
   ```bash
   cd /mnt/c/MapEventAI_NEW/frontend/lambda-package
   ```
4. **Créer la structure** :
   ```bash
   mkdir -p psycopg2-layer/python/lib/python3.12/site-packages
   ```
5. **Installer psycopg2** :
   ```bash
   pip3 install psycopg2-binary==2.9.9 -t psycopg2-layer/python/lib/python3.12/site-packages
   ```
6. **Créer le ZIP** :
   ```bash
   cd psycopg2-layer
   zip -r ../psycopg2-layer.zip python
   cd ..
   ```
7. **Publier la couche** (depuis PowerShell Windows) :
   ```powershell
   aws lambda publish-layer-version `
       --layer-name psycopg2-py312-mapevent `
       --zip-file fileb://psycopg2-layer.zip `
       --compatible-runtimes python3.12 `
       --region eu-west-1
   ```
8. **Ajouter à la fonction** :
   ```powershell
   # Récupérer l'ARN de la couche depuis la sortie précédente
   aws lambda update-function-configuration `
       --function-name mapevent-backend `
       --layers <ARN_DE_LA_COUCHE> `
       --region eu-west-1
   ```

## Après avoir ajouté la couche

1. **Optionnel** : Retirer `psycopg2-binary` de `requirements.txt` pour réduire la taille
2. **Redéployer le code** :
   ```powershell
   cd lambda-package
   .\deploy-lambda.ps1
   ```
3. **Tester** : Les logs ne devraient plus montrer l'erreur `psycopg2._psycopg`

## Vérification

```bash
aws logs tail /aws/lambda/mapevent-backend --since 5m --region eu-west-1
```

Vous devriez voir :
- ✅ `Application Flask créée` au lieu de `No module named 'psycopg2._psycopg'`

## Recommandation

**Utilisez la Solution 2 (AWS Console)** - C'est la plus rapide et la plus fiable. Les couches Lambda publiques sont déjà testées et optimisées.





