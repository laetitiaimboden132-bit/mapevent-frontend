# 🚀 Guide de Démarrage Rapide - MapEventAI Backend

## 📋 Prérequis

- AWS CLI installé et configuré
- Python 3.12+
- Accès AWS avec permissions Lambda, RDS, Redis

## ⚡ Déploiement en 3 étapes

### Étape 1: Configurer les variables d'environnement

1. Copiez le fichier template:
   ```powershell
   Copy-Item lambda.env.example lambda.env
   ```

2. Éditez `lambda.env` et remplissez les valeurs:
   - RDS_HOST, RDS_USER, RDS_PASSWORD
   - REDIS_HOST
   - GOOGLE_CLOUD_VISION_API_KEY (optionnel)
   - STRIPE_SECRET_KEY (optionnel)

3. Exécutez le script de configuration:
   ```powershell
   .\configure_lambda_env.ps1
   ```

### Étape 2: Configurer les clés API (optionnel)

Pour la modération d'images, suivez `setup_api_keys.md`:
- Google Cloud Vision API (recommandé)
- Ou AWS Rekognition (fallback)

### Étape 3: Tester les endpoints

```powershell
.\test_all_endpoints.ps1
```

## 📚 Documentation complète

- **Déploiement**: `README_DEPLOIEMENT.md`
- **WebSocket**: `WEBSOCKET_SETUP.md`
- **Clés API**: `setup_api_keys.md`
- **Tests**: `test_all_endpoints.ps1`

## ✅ Checklist

- [ ] Variables d'environnement configurées
- [ ] Clés API modération configurées (optionnel)
- [ ] Tests des endpoints réussis
- [ ] Base de données PostgreSQL accessible
- [ ] Redis accessible
- [ ] Lambda function déployée

## 🐛 Dépannage

**Erreur 502/503**: Vérifiez les variables d'environnement et la connexion DB/Redis

**Erreur "Module not found"**: Vérifiez que les Lambda Layers sont attachés

**Erreur de modération**: Vérifiez que les clés API sont configurées

## 📞 Support

Consultez les logs CloudWatch pour plus de détails:
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```





