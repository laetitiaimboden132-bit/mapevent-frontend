# 🚀 Guide de Déploiement MapEventAI Backend

## 📋 Prérequis

- AWS CLI installé et configuré
- Python 3.11+
- pip installé
- Permissions AWS pour Lambda et API Gateway

## 🔧 Déploiement Lambda

### Windows (PowerShell)

```powershell
cd lambda-package
.\deploy.ps1
```

### Linux/Mac

```bash
cd lambda-package
chmod +x deploy.sh
./deploy.sh
```

## 📝 Configuration des Variables d'Environnement

Après le déploiement, configurez les variables d'environnement:

```bash
aws lambda update-function-configuration \
    --function-name mapevent-backend \
    --environment Variables="{
        RDS_HOST=votre_host,
        RDS_PORT=5432,
        RDS_DB=mapevent,
        RDS_USER=votre_user,
        RDS_PASSWORD=votre_password,
        REDIS_HOST=votre_redis_host,
        REDIS_PORT=6379,
        GOOGLE_CLOUD_VISION_API_KEY=votre_cle_google,
        AWS_REGION=eu-west-1,
        STRIPE_SECRET_KEY=votre_cle_stripe
    }" \
    --region eu-west-1
```

## 🧪 Tests

### Tests unitaires

```bash
cd lambda-package
pip install pytest pytest-mock
python -m pytest backend/tests/ -v
```

### Test modération d'images

```bash
cd lambda-package
python test_moderation.py
```

## 📚 Documentation

- **WebSocket**: Voir `WEBSOCKET_SETUP.md`
- **Clés API**: Voir `API_KEYS_SETUP.md`
- **Tests**: Voir `backend/tests/test_social_endpoints.py`

## ✅ Checklist Post-Déploiement

- [ ] Lambda function déployée
- [ ] Variables d'environnement configurées
- [ ] Tests unitaires passés
- [ ] Test modération d'images réussi
- [ ] API Gateway configuré (si nécessaire)
- [ ] WebSocket configuré (voir WEBSOCKET_SETUP.md)
- [ ] Monitoring CloudWatch activé

## 🐛 Dépannage

**Erreur: "Module not found"**
- Vérifiez que toutes les dépendances sont dans `requirements.txt`
- Réinstallez les dépendances: `pip install -r backend/requirements.txt -t .`

**Erreur: "Timeout"**
- Augmentez le timeout Lambda (max 15 minutes)
- Vérifiez les connexions DB/Redis

**Erreur: "Memory limit"**
- Augmentez la mémoire allouée à Lambda (max 10GB)





