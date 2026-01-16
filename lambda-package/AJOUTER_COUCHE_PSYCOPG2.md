# Ajouter une couche Lambda pour psycopg2

## Problème
`psycopg2-binary` nécessite des binaires Linux compilés. L'installation sur Windows produit des binaires Windows qui ne fonctionnent pas sur Lambda.

## Solution : Couche Lambda précompilée

### Option 1 : Via AWS Console (RECOMMANDÉ)

1. **Allez sur AWS Console** → Lambda → Fonction `mapevent-backend`
2. **Onglet "Layers"** → Cliquez sur "Add a layer"
3. **Choisir "Specify an ARN"**
4. **Utiliser cette ARN** (pour Python 3.12, région eu-west-1) :
   ```
   arn:aws:lambda:eu-west-1:898466741470:layer:psycopg2-py312:1
   ```
   **OU** cherchez une autre couche sur :
   - https://github.com/jetbridge/psycopg2-lambda-layer
   - https://github.com/AbhimanyuHK/aws-psycopg2-lambda

5. **Cliquez sur "Add"**

### Option 2 : Via AWS CLI

```powershell
aws lambda update-function-configuration `
    --function-name mapevent-backend `
    --layers arn:aws:lambda:eu-west-1:898466741470:layer:psycopg2-py312:1 `
    --region eu-west-1
```

### Option 3 : Créer votre propre couche

Si les couches publiques ne fonctionnent pas, créez votre propre couche :

```powershell
# 1. Créer un dossier pour la couche
mkdir psycopg2-layer
cd psycopg2-layer
mkdir python\lib\python3.12\site-packages

# 2. Installer psycopg2-binary dans ce dossier (avec Docker ou WSL)
# Dans WSL ou Docker :
pip install psycopg2-binary==2.9.9 -t python/lib/python3.12/site-packages

# 3. Créer le ZIP
zip -r psycopg2-layer.zip python

# 4. Publier la couche
aws lambda publish-layer-version `
    --layer-name psycopg2-py312 `
    --zip-file fileb://psycopg2-layer.zip `
    --compatible-runtimes python3.12 `
    --region eu-west-1
```

## Après avoir ajouté la couche

1. **Retirer `psycopg2-binary` de `requirements.txt`** (optionnel, mais recommandé pour réduire la taille)
2. **Redéployer le code** :
   ```powershell
   cd lambda-package
   .\deploy-lambda.ps1
   ```
3. **Tester** : Les logs ne devraient plus montrer `No module named 'psycopg2._psycopg'`

## Vérification

```bash
aws logs tail /aws/lambda/mapevent-backend --since 5m --region eu-west-1
```

Vous ne devriez plus voir l'erreur `psycopg2._psycopg`.





