# Debug Erreur 500 - Création de compte

## Problème
Erreur 500 persistante lors de la création de compte avec Google OAuth.

## Corrections appliquées aujourd'hui
1. ✅ Correction import `create_app` dans `handler.py`
2. ✅ Gestion erreurs S3 améliorée (ne bloque plus la création de compte)
3. ✅ Gestion PIL/Pillow avec fallback
4. ✅ Scripts de déploiement automatique créés

## À vérifier demain

### 1. Vérifier les logs CloudWatch
```bash
aws logs tail /aws/lambda/mapevent-backend --since 10m --region eu-west-1 --format short
```

### 2. Points à vérifier dans le code
- **handler.py ligne 99** : Vérifier que `create_app()` est bien appelé
- **backend/main.py ligne 26** : Vérifier que `create_app()` est bien défini
- **Import paths** : Vérifier que les imports fonctionnent dans l'environnement Lambda

### 3. Test local possible
```python
# Tester l'import dans un environnement similaire à Lambda
from backend.main import create_app
app = create_app()
```

### 4. Solution de contournement si nécessaire
Si l'import continue à échouer, créer directement l'app dans `handler.py` :
```python
# Dans handler.py, remplacer l'import par :
from backend.main import app as flask_app
app = flask_app
```

## Commandes utiles pour demain
```powershell
# Voir les logs en temps réel
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1

# Redéployer rapidement
cd lambda-package
.\deploy-lambda.ps1
```

## Fichiers modifiés aujourd'hui
- `lambda-package/handler.py` : Correction import create_app
- `lambda-package/backend/main.py` : Gestion erreurs S3 améliorée
- `lambda-package/backend/services/s3_service.py` : Gestion PIL/Pillow






