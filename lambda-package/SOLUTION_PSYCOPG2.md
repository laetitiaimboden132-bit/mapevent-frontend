# Solution pour psycopg2 sur Lambda

## Problème
`psycopg2-binary` nécessite des binaires Linux compilés, mais l'installation sur Windows produit des binaires Windows qui ne fonctionnent pas sur Lambda.

## Solutions

### Solution 1 : Utiliser Docker (RECOMMANDÉ)
Le script `deploy-lambda.ps1` a été mis à jour pour utiliser Docker automatiquement.

**Prérequis** : Docker Desktop installé et démarré

**Commande** :
```powershell
cd lambda-package
.\deploy-lambda.ps1
```

### Solution 2 : Utiliser une couche Lambda précompilée
Si Docker n'est pas disponible, utilisez une couche Lambda publique pour psycopg2.

**Étapes** :
1. Allez sur AWS Console → Lambda → Fonction `mapevent-backend`
2. Onglet "Layers" → "Add a layer"
3. Choisir "Specify an ARN"
4. Utiliser cette ARN (pour Python 3.12, région eu-west-1) :
   ```
   arn:aws:lambda:eu-west-1:898466741470:layer:psycopg2-py312:1
   ```
   (Si cette ARN ne fonctionne pas, cherchez "psycopg2 lambda layer python 3.12" sur GitHub)

5. Retirer `psycopg2-binary` de `requirements.txt` temporairement
6. Redéployer le code

### Solution 3 : Utiliser un conteneur Lambda
Migrer vers un conteneur Lambda au lieu d'un ZIP (plus complexe mais plus flexible).

## Vérification
Après déploiement, vérifiez les logs CloudWatch :
```bash
aws logs tail /aws/lambda/mapevent-backend --since 5m --region eu-west-1
```

Vous ne devriez plus voir : `No module named 'psycopg2._psycopg'`

## Test rapide
```powershell
# Vérifier si Docker est disponible
docker --version

# Si oui, déployer avec Docker
cd lambda-package
.\deploy-lambda.ps1

# Si non, utiliser la Solution 2 (couche Lambda)
```





