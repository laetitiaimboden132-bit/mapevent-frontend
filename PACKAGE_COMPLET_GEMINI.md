# 📦 PACKAGE COMPLET POUR GEMINI - MAPEVENT PROJECT

**Date :** 31 décembre 2024  
**Projet :** MapEvent - Authentification Google OAuth + Gestion Profil  
**État :** Problème critique de sérialisation backend à résoudre

---

## 🎯 FICHIERS À DONNER À GEMINI (DANS L'ORDRE)

### ⭐ FICHIERS PRINCIPAUX (À LIRE EN PREMIER)

1. **README_GEMINI_COMPLET.md** ⭐⭐⭐
   - Guide complet depuis le début
   - Vue d'ensemble, architecture, infrastructure AWS
   - Problème principal détaillé avec solutions
   - **À LIRE EN PREMIER**

2. **DEMARRAGE_RAPIDE_GEMINI.md** ⭐⭐
   - Correction rapide du problème (15 minutes)
   - Code à modifier directement
   - **À LIRE EN SECOND**

3. **RESUME_ETAT_PROJET.md** ⭐⭐
   - État actuel du projet
   - Ce qui fonctionne / ne fonctionne pas
   - Solutions tentées
   - Bugs connus

4. **RESUME_CHEMINS_AWS.md** ⭐⭐
   - Tous les chemins AWS
   - Endpoints, credentials, IDs
   - Commandes AWS CLI

5. **INFORMATIONS_COMPLEMENTAIRES_GEMINI.md** ⭐
   - Détails techniques
   - Structure du code
   - Points d'entrée des fonctions

6. **INDEX_FICHIERS_GEMINI.md**
   - Index de tous les fichiers
   - Ordre de lecture recommandé

---

## 📋 RÉSUMÉ EXÉCUTIF (POUR GEMINI)

### Le Projet
MapEvent est une plateforme web qui affiche des événements sur une carte interactive. Le système d'authentification permet aux utilisateurs de se connecter avec Google OAuth et de compléter leur profil (username, photo, adresse) une seule fois.

### Le Problème
Le backend Flask (déployé sur AWS Lambda) renvoie `{"user": "[dict - 17 items]"}` au lieu d'un objet JSON valide. Cela empêche le frontend de récupérer les données utilisateur et d'afficher le formulaire d'inscription.

### La Cause
Flask test client (utilisé par Lambda) transforme les dictionnaires Python complexes en chaînes de caractères avant la sérialisation JSON.

### La Solution
1. Forcer la sérialisation de chaque valeur individuellement dans `oauth_google()`
2. Utiliser `Response` directement avec `json.dumps()` au lieu de `make_response()`
3. Simplifier la logique frontend d'affichage du formulaire

### Infrastructure AWS
- **Région :** eu-west-1
- **API Gateway ID :** j33osy4bvj
- **Lambda Function :** mapevent-backend
- **RDS :** mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com
- **Redis :** mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com
- **Cognito Domain :** eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
- **Site :** https://mapevent.world

---

## 🔧 FICHIERS DE CODE À MODIFIER

### Backend
1. **lambda-package/backend/main.py**
   - Fonction : `oauth_google()` (ligne ~1328)
   - Modifier : Sérialisation de `user_data`

2. **lambda-package/handler.py**
   - Fonction : `lambda_handler()` (ligne ~180-320)
   - Modifier : Extraction email depuis token Cognito

### Frontend
3. **public/map_logic.js**
   - Fonction : `handleCognitoCallbackIfPresent()` (ligne ~380)
   - Modifier : Simplifier la logique d'affichage du formulaire

---

## 📊 STRUCTURE DU PROJET

```
MapEventAI_NEW/frontend/
├── public/
│   ├── mapevent.html          # Page principale
│   ├── map_logic.js           # Logique JavaScript (~20000 lignes)
│   └── trees/                 # Arbres de catégories JSON
│
├── lambda-package/
│   ├── handler.py             # Handler Lambda
│   ├── lambda_function.py     # Point d'entrée Lambda
│   ├── deploy_backend.py      # Script de déploiement
│   ├── lambda.env             # Variables d'environnement (SECRET)
│   └── backend/
│       ├── main.py            # Application Flask (~2300 lignes)
│       └── requirements.txt   # Dépendances Python
│
└── [fichiers .md]             # Documentation
```

---

## 🚀 WORKFLOW DE CORRECTION

### 1. Modifier le Backend
```python
# Dans lambda-package/backend/main.py, fonction oauth_google()
# Forcer la sérialisation de chaque valeur
user_data_forced = {}
for key, value in user_data_clean.items():
    if isinstance(value, dict):
        user_data_forced[key] = json.loads(json.dumps(value, default=str))
    else:
        user_data_forced[key] = value

# Utiliser Response directement
from flask import Response
return Response(
    json.dumps({'user': user_data_forced, ...}, default=str),
    mimetype='application/json'
)
```

### 2. Déployer
```powershell
cd lambda-package
python deploy_backend.py
```

### 3. Tester
- Ouvrir https://mapevent.world
- Se connecter avec Google
- Vérifier que le formulaire s'affiche
- Vérifier les logs CloudWatch

---

## 🔍 COMMANDES ESSENTIELLES

### Voir les logs
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

### Déployer
```powershell
cd lambda-package
python deploy_backend.py
```

### Tester l'API
```powershell
$body = @{
    email = "test@example.com"
    name = "Test User"
    sub = "test-sub-123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

---

## 📚 DOCUMENTATION COMPLÈTE

### Fichiers à lire (dans l'ordre)
1. README_GEMINI_COMPLET.md
2. DEMARRAGE_RAPIDE_GEMINI.md
3. RESUME_ETAT_PROJET.md
4. RESUME_CHEMINS_AWS.md
5. INFORMATIONS_COMPLEMENTAIRES_GEMINI.md

### Fichiers de référence
- GUIDE_CONFIGURATION_CORS_CONSOLE.md
- GUIDE_COGNITO_FRANCAIS.md
- PLAN_CORRECTION_AUTHENTIFICATION.md

---

## ✅ CHECKLIST FINALE

- [ ] Tous les fichiers de documentation sont présents
- [ ] Les chemins AWS sont documentés
- [ ] Le problème est clairement expliqué
- [ ] Les solutions sont proposées
- [ ] Les commandes de déploiement sont fournies
- [ ] Les logs sont accessibles

---

**PRÊT POUR GEMINI :** ✅ OUI  
**Fichiers à copier :** Tous les fichiers .md listés ci-dessus  
**Ordre de lecture :** Suivre l'ordre dans INDEX_FICHIERS_GEMINI.md







