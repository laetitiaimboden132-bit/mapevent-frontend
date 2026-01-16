# 📋 INDEX DES FICHIERS POUR GEMINI

## 🎯 FICHIERS PRINCIPAUX À LIRE EN PRIORITÉ

### 1. README_GEMINI_COMPLET.md ⭐⭐⭐
**À LIRE EN PREMIER** - Guide complet depuis le début
- Vue d'ensemble du projet
- Architecture technique complète
- Infrastructure AWS
- Problème principal détaillé
- Solutions à implémenter
- Checklist complète

### 2. RESUME_ETAT_PROJET.md ⭐⭐
État actuel du projet
- Ce qui fonctionne
- Problèmes critiques en cours
- Solutions tentées
- Bugs connus
- Prochaines étapes recommandées

### 3. RESUME_CHEMINS_AWS.md ⭐⭐
Tous les chemins et configurations AWS
- API Gateway (ID, endpoints, Resource IDs)
- Lambda Function (nom, handler, logs)
- RDS PostgreSQL (endpoint, credentials)
- Redis ElastiCache (endpoint)
- Cognito (domain, configuration)
- CloudFront, Route 53, ACM
- Commandes AWS CLI utiles

### 4. INFORMATIONS_COMPLEMENTAIRES_GEMINI.md ⭐
Détails techniques complémentaires
- Structure du code
- Points d'entrée des fonctions
- Workflow de développement
- Tests et debugging
- Exemples de code

---

## 📚 FICHIERS DE DOCUMENTATION SUPPLÉMENTAIRES

### Configuration AWS
- **GUIDE_CONFIGURATION_CORS_CONSOLE.md** : Configuration CORS dans API Gateway
- **GUIDE_COGNITO_FRANCAIS.md** : Configuration Cognito détaillée
- **lambda-package/README_DEPLOIEMENT.md** : Guide de déploiement Lambda

### Problèmes spécifiques
- **PLAN_CORRECTION_AUTHENTIFICATION.md** : Plan de correction détaillé
- **DEBUG_FORMULAIRE.md** : Debug du formulaire d'inscription

---

## 📁 FICHIERS DE CODE IMPORTANTS

### Frontend
- `public/mapevent.html` : Page principale
- `public/map_logic.js` : Logique JavaScript complète

### Backend
- `lambda-package/handler.py` : Handler Lambda
- `lambda-package/lambda_function.py` : Point d'entrée Lambda
- `lambda-package/backend/main.py` : Application Flask

### Configuration
- `lambda-package/lambda.env` : Variables d'environnement (⚠️ SECRET)
- `lambda-package/backend/requirements.txt` : Dépendances Python

---

## 🚀 ORDRE DE LECTURE RECOMMANDÉ POUR GEMINI

1. **README_GEMINI_COMPLET.md** (ce fichier résume tout)
2. **RESUME_ETAT_PROJET.md** (comprendre les problèmes actuels)
3. **RESUME_CHEMINS_AWS.md** (connaître l'infrastructure)
4. **INFORMATIONS_COMPLEMENTAIRES_GEMINI.md** (détails techniques)
5. Lire le code dans l'ordre :
   - `lambda-package/backend/main.py` (route `oauth_google`)
   - `lambda-package/handler.py` (détection sérialisation)
   - `public/map_logic.js` (fonction `handleCognitoCallbackIfPresent`)

---

## ✅ CHECKLIST POUR GEMINI

Avant de commencer :
- [ ] Lire `README_GEMINI_COMPLET.md` en entier
- [ ] Lire `RESUME_ETAT_PROJET.md`
- [ ] Lire `RESUME_CHEMINS_AWS.md`
- [ ] Comprendre le problème de sérialisation `"[dict - 17 items]"`
- [ ] Vérifier l'accès aux logs CloudWatch

Pour corriger :
- [ ] Modifier `lambda-package/backend/main.py` (route `oauth_google`)
- [ ] Tester la réponse API
- [ ] Simplifier `public/map_logic.js` (logique formulaire)
- [ ] Tester le flow complet

Pour déployer :
- [ ] Exécuter `python lambda-package/deploy_backend.py`
- [ ] Vérifier les logs CloudWatch
- [ ] Tester sur `https://mapevent.world`

---

**Dernière mise à jour :** 31 décembre 2024







