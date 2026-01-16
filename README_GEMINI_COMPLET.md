# 🚀 GUIDE COMPLET POUR GEMINI - MAPEVENT PROJECT

**Date :** 31 décembre 2024  
**Projet :** MapEvent - Plateforme événementielle avec authentification Google OAuth  
**État :** En développement - Problème critique de sérialisation backend

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble du projet](#vue-densemble)
2. [Architecture technique](#architecture)
3. [Infrastructure AWS complète](#infrastructure-aws)
4. [Problème principal actuel](#probleme-principal)
5. [Structure du code](#structure-code)
6. [Workflow de développement](#workflow)
7. [Configuration et credentials](#configuration)
8. [Tests et debugging](#tests)
9. [Solutions à implémenter](#solutions)

---

## 🎯 VUE D'ENSEMBLE DU PROJET

### Objectif
Créer un système d'authentification et de gestion de profil utilisateur pour MapEvent, permettant aux utilisateurs de :
1. Se connecter avec Google OAuth
2. Compléter leur profil (username, photo, adresse postale) **UNE SEULE FOIS**
3. Se reconnecter sans refaire le formulaire d'inscription
4. Modifier leur profil ultérieurement

### Contexte
- **Domaine :** https://mapevent.world
- **Type :** Application web statique (frontend) + Backend serverless (AWS Lambda)
- **Région AWS :** eu-west-1 (Europe - Irlande)
- **Base de données :** PostgreSQL (RDS)
- **Cache :** Redis (ElastiCache)

---

## 🏗️ ARCHITECTURE TECHNIQUE

### Frontend
- **Technologies :** HTML5, CSS3, JavaScript (ES6+), Vanilla JS (pas de framework)
- **Bibliothèques :**
  - Leaflet.js 1.9.4 (cartes)
  - Stripe.js (paiements)
- **Fichiers principaux :**
  - `public/mapevent.html` (~2200 lignes)
  - `public/map_logic.js` (~20000 lignes)
- **Hébergement :** CloudFront + S3 (probablement)

### Backend
- **Runtime :** Python 3.12+
- **Framework :** Flask 3.0.0
- **Déploiement :** AWS Lambda
- **Fichiers principaux :**
  - `lambda-package/handler.py` (Handler Lambda)
  - `lambda-package/lambda_function.py` (Point d'entrée)
  - `lambda-package/backend/main.py` (~2300 lignes, Application Flask)

### Base de données
- **Type :** PostgreSQL
- **Host :** `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port :** 5432
- **Database :** `mapevent`
- **User :** `postgres`

### Cache
- **Type :** Redis (ElastiCache)
- **Host :** `mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com`
- **Port :** 6379

### Authentification
- **Service :** AWS Cognito
- **Provider :** Google OAuth
- **Domain :** `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- **Flow :** PKCE (Proof Key for Code Exchange) pour SPA

---

## ☁️ INFRASTRUCTURE AWS COMPLÈTE

### API Gateway
- **API ID :** `j33osy4bvj`
- **Stage :** `default`
- **Région :** `eu-west-1`
- **URL Base :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default`
- **URL API :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api`

**Endpoints principaux :**
- `/api/user/oauth/google` (POST) - Resource ID: `k70u2t`
- `/api/user/oauth/google/complete` (POST) - Resource ID: `rjh1m4`

### Lambda Function
- **Nom :** `mapevent-backend`
- **Région :** `eu-west-1`
- **Handler :** `lambda_function.lambda_handler`
- **Runtime :** Python 3.12
- **Timeout :** 15 minutes (max)
- **Log Group :** `/aws/lambda/mapevent-backend`

### RDS PostgreSQL
- **Endpoint :** `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port :** `5432`
- **Database :** `mapevent`
- **User :** `postgres`
- **Instance ID :** `mapevent-db`

### ElastiCache Redis
- **Endpoint :** `mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com`
- **Port :** `6379`
- **Cluster ID :** `mapevent-cache`

### AWS Cognito
- **Domain :** `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- **URL complète :** `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- **Redirect URI :** `https://mapevent.world/`
- **Provider :** Google OAuth

### CloudFront
- **Domain :** `mapevent.world`
- **Distribution :** (ID à récupérer depuis console)

### Route 53
- **Domain :** `mapevent.world`
- **Hosted Zone :** (ID à récupérer depuis console)

### ACM (Certificats SSL)
- **Domain :** `mapevent.world`
- **Région :** `us-east-1` (pour CloudFront) ou `eu-west-1` (pour API Gateway)

---

## 🐛 PROBLÈME PRINCIPAL ACTUEL

### Symptôme
Le backend Flask renvoie `{"user": "[dict - 17 items]"}` au lieu d'un objet JSON valide contenant les données utilisateur (username, photo, adresse, etc.).

### Cause
Flask test client (utilisé par Lambda pour simuler les requêtes HTTP) transforme les dictionnaires Python complexes en chaînes de caractères lors de la sérialisation, avant même que `json.dumps()` soit appelé.

### Impact
1. Le frontend ne peut pas extraire les données utilisateur
2. Le formulaire d'inscription ne s'affiche pas alors qu'il devrait
3. L'utilisateur ne peut pas se connecter correctement
4. Les données (username, photo, adresse) sont perdues après reconnexion

### Solutions tentées (sans succès complet)
1. ✅ Sérialisation explicite avec `json.dumps()` dans le backend
2. ✅ Utilisation de `make_response()` au lieu de `jsonify()`
3. ✅ Handler Lambda qui détecte `"[dict - X items]"` et récupère les données depuis la DB
4. ✅ Frontend qui détecte `"[dict - X items]"` et force l'affichage du formulaire

### État actuel
Le problème persiste. Le handler Lambda essaie de récupérer l'email depuis le body de la requête, mais dans le cas d'un callback OAuth, l'email n'est pas toujours disponible dans le body.

---

## 📁 STRUCTURE DU CODE

### Frontend - Fichiers clés

#### `public/map_logic.js` (~20000 lignes)
**Fonctions principales :**
- `handleCognitoCallbackIfPresent()` (ligne ~380) : Traite le callback OAuth Google
- `startGoogleLogin()` (ligne ~2600) : Démarre la connexion Google
- `showProRegisterForm()` (ligne ~7000) : Affiche le formulaire d'inscription
- `handleProRegisterSubmit()` (ligne ~8000) : Soumet le formulaire
- `openLoginModal()` (ligne ~9700) : Ouvre la modal de connexion
- `performLogin()` (ligne ~9900) : Connexion par email/mot de passe
- `updateAccountButton()` : Met à jour le bouton compte dans la topbar

**Variables globales importantes :**
```javascript
let currentUser = {};              // Utilisateur actuel
let currentMode = "event";         // Mode: "event" | "booking" | "service"
let eventsData = [];              // Données événements
let selectedCategories = [];      // Catégories sélectionnées
```

**Configuration Cognito :**
```javascript
const COGNITO = {
  domain: "https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com",
  clientId: "...", // À récupérer depuis console AWS Cognito
  redirectUri: "https://mapevent.world/"
};
```

**URL API :**
```javascript
const API_BASE_URL = "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api";
```

#### `public/mapevent.html` (~2200 lignes)
- Page principale HTML
- Styles CSS inline
- Structure de la carte Leaflet
- Modals (connexion, inscription, profil)

### Backend - Fichiers clés

#### `lambda-package/backend/main.py` (~2300 lignes)
**Routes principales :**
- `@app.route('/api/user/oauth/google', methods=['POST'])` (ligne ~1328)
  - Récupère/crée l'utilisateur après authentification Google
  - Retourne `{"user": {...}, "isNewUser": bool, "profileComplete": bool}`
  
- `@app.route('/api/user/oauth/google/complete', methods=['POST'])` (ligne ~1809)
  - Complète le profil utilisateur (username, password, photo, adresse)
  - Sauvegarde dans PostgreSQL

**Problème de sérialisation :**
Le code essaie de sérialiser `user_data` avec `json.dumps()` puis utilise `make_response()`, mais Flask test client transforme quand même l'objet en chaîne.

#### `lambda-package/handler.py`
**Fonction principale :**
- `lambda_handler(event, context)` (ligne ~40)
  - Point d'entrée Lambda
  - Utilise Flask test client pour simuler les requêtes HTTP
  - Gère CORS
  - Détecte `"[dict - X items]"` et essaie de corriger (ligne ~180-320)

**Détection et correction :**
```python
if isinstance(body_json['user'], str) and body_json['user'].startswith('[dict'):
    # Essaie de récupérer l'email depuis le body
    user_email = request_data.get('email', '')
    # Si email trouvé, récupère depuis DB et reconstruit user_data
```

#### `lambda-package/lambda_function.py`
- Point d'entrée Lambda standard
- Importe `lambda_handler` depuis `handler.py`

### Base de données

#### Table `users`
Colonnes principales :
- `id` (VARCHAR PRIMARY KEY)
- `email` (VARCHAR UNIQUE)
- `username` (VARCHAR)
- `first_name` (VARCHAR)
- `last_name` (VARCHAR)
- `password_hash` (VARCHAR)
- `profile_photo_url` (TEXT)
- `postal_address` (TEXT)
- `postal_city` (TEXT)
- `postal_zip` (TEXT)
- `postal_country` (VARCHAR DEFAULT 'CH')
- `avatar_emoji` (TEXT)
- `avatar_description` (TEXT)
- `subscription` (VARCHAR DEFAULT 'free')
- `role` (VARCHAR DEFAULT 'user')
- `oauth_google_id` (VARCHAR)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

---

## 🔄 WORKFLOW DE DÉVELOPPEMENT

### Déploiement Backend (Lambda)
```powershell
cd lambda-package
python deploy_backend.py
```
Le script :
1. Nettoie les anciens fichiers
2. Installe les dépendances
3. Crée un package ZIP
4. Déploie sur Lambda via AWS CLI

### Mise à jour Variables d'Environnement
```powershell
cd lambda-package
.\configure_lambda_env.ps1
```

### Voir les Logs Lambda
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

### Test Local Frontend
- Ouvrir : `http://localhost:3000/mapevent.html`
- (Si serveur local configuré)

### Test API Direct
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

## 🔐 CONFIGURATION ET CREDENTIALS

### Variables d'Environnement Lambda
**Fichier :** `lambda-package/lambda.env` (⚠️ NE PAS COMMITER)

```env
RDS_HOST=mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB=mapevent
RDS_USER=postgres
RDS_PASSWORD=666666Laeti69!

REDIS_HOST=mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com
REDIS_PORT=6379

AWS_REGION=eu-west-1
FLASK_ENV=production

# Optionnel
GOOGLE_CLOUD_VISION_API_KEY=
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Dépendances Backend
**Fichier :** `lambda-package/backend/requirements.txt`
```
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
redis==5.0.1
boto3==1.34.0
sendgrid==6.11.0
requests==2.31.0
python-dateutil==2.8.2
awsgi
stripe==7.8.0
Pillow==10.2.0
google-cloud-vision==3.4.5
```

### Cognito Client ID
**À récupérer depuis :**
1. Console AWS Cognito : https://eu-west-1.console.aws.amazon.com/cognito/
2. User Pools → Trouver le pool avec domaine `eu-west-19o9j6xsdr`
3. App clients → Copier le Client ID
4. Mettre à jour dans `public/map_logic.js` ligne ~6

---

## 🧪 TESTS ET DEBUGGING

### Test Flow Complet
1. Ouvrir `https://mapevent.world`
2. Cliquer sur "Compte"
3. Cliquer sur "Connexion avec Google"
4. Se connecter avec Google
5. **Vérifier :** Le formulaire d'inscription doit s'afficher
6. Remplir le formulaire (username, password, photo, adresse)
7. Soumettre
8. **Vérifier :** L'utilisateur est connecté, le nom et la photo apparaissent
9. Se déconnecter
10. Se reconnecter avec Google
11. **Vérifier :** Le formulaire NE doit PAS s'afficher, les données doivent être restaurées

### Logs Frontend (Console Navigateur)
- Ouvrir F12 → Console
- Chercher les préfixes :
  - `✅` : Succès
  - `⚠️` : Avertissement
  - `❌` : Erreur
  - `🔍` : Debug

### Logs Backend (CloudWatch)
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

**URL Console :** https://eu-west-1.console.aws.amazon.com/cloudwatch/

### Vérifier la Réponse API
```powershell
# Après connexion Google, vérifier la réponse
# Dans les logs CloudWatch, chercher :
# "🔍 Body brut récupéré" ou "⚠️ ATTENTION: user est une chaîne"
```

---

## 💡 SOLUTIONS À IMPLÉMENTER

### Solution 1 : Corriger la sérialisation à la source (RECOMMANDÉ)

**Fichier :** `lambda-package/backend/main.py`  
**Fonction :** `oauth_google()` (ligne ~1328)

**Modification :**
```python
# Après avoir construit user_data (ligne ~1635)
# FORCER la sérialisation de chaque valeur individuellement
user_data_serialized = {}
for key, value in user_data.items():
    if isinstance(value, dict):
        # Sérialiser chaque dict individuellement
        user_data_serialized[key] = json.loads(json.dumps(value, default=str))
    elif isinstance(value, (list, tuple)):
        # Sérialiser les listes
        user_data_serialized[key] = json.loads(json.dumps(value, default=str))
    else:
        # Valeurs simples
        user_data_serialized[key] = value

# Utiliser user_data_serialized au lieu de user_data
response_data = {
    'user': user_data_serialized,  # ← Utiliser la version sérialisée
    'isNewUser': is_new_user,
    'profileComplete': profile_complete
}

# Sérialiser la réponse complète
response_json_str = json.dumps(response_data, ensure_ascii=False, default=str)

# Utiliser Response directement
from flask import Response
return Response(
    response_json_str,
    mimetype='application/json',
    status=200
)
```

### Solution 2 : Extraire l'email depuis le token Cognito

**Fichier :** `lambda-package/handler.py`  
**Fonction :** `lambda_handler()` (ligne ~180-320)

**Modification :**
```python
# Au lieu de chercher l'email dans le body, extraire depuis le token Cognito
if isinstance(body_json['user'], str) and body_json['user'].startswith('[dict'):
    # Essayer d'extraire l'email depuis les headers (si token Cognito présent)
    auth_header = headers_lower.get('authorization', '')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        try:
            # Décoder le token JWT (sans vérification pour extraction rapide)
            import base64
            import json as json_lib
            parts = token.split('.')
            if len(parts) >= 2:
                payload = json_lib.loads(base64.urlsafe_b64decode(parts[1] + '=='))
                user_email = payload.get('email', '')
                print(f"🔍 Email extrait depuis token Cognito: {user_email}")
        except:
            pass
    
    # Si toujours pas d'email, essayer depuis le body
    if not user_email:
        request_body = event.get('body', '')
        # ... (code existant)
```

### Solution 3 : Simplifier la logique frontend

**Fichier :** `public/map_logic.js`  
**Fonction :** `handleCognitoCallbackIfPresent()` (ligne ~380)

**Modification :**
```javascript
// Simplifier la logique d'affichage du formulaire
const shouldShowForm = 
    isNewUser ||                           // Nouvel utilisateur
    !profileComplete ||                    // Profil incomplet (backend)
    isBackendUserEmpty ||                  // Données manquantes (sérialisation)
    !hasUsername ||                        // Pas de username
    !hasProfilePhoto;                      // Pas de photo

if (shouldShowForm) {
    // Afficher le formulaire IMMÉDIATEMENT
    console.log('📝 Affichage formulaire d\'inscription', {
        reason: isNewUser ? 'nouvel utilisateur' : 
                !profileComplete ? 'profil incomplet' : 
                isBackendUserEmpty ? 'données manquantes' : 
                !hasUsername ? 'pas de username' : 
                'pas de photo'
    });
    
    currentUser.isLoggedIn = false;
    currentUser.profileComplete = false;
    
    // Pré-remplir avec données Google
    registerData.email = currentUser.email || user.email || '';
    registerData.firstName = currentUser.firstName || user.firstName || '';
    registerData.lastName = currentUser.lastName || user.lastName || '';
    registerData.profilePhoto = currentUser.profile_photo_url || user.profile_photo_url || user.picture || '';
    
    // Afficher le formulaire
    if (typeof window.showProRegisterForm === 'function') {
        window.showProRegisterForm();
    }
    
    updateAccountButton();
    updateUserUI();
    
    // Nettoyer l'URL
    if (window.history && window.history.replaceState) {
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    return; // SORTIR ICI
}
```

---

## 📚 FICHIERS DE DOCUMENTATION

### Fichiers principaux à lire
1. **README_GEMINI_COMPLET.md** (ce fichier) : Vue d'ensemble complète
2. **RESUME_ETAT_PROJET.md** : État actuel, problèmes, solutions tentées
3. **RESUME_CHEMINS_AWS.md** : Tous les chemins AWS, endpoints, credentials
4. **INFORMATIONS_COMPLEMENTAIRES_GEMINI.md** : Détails techniques, structure code

### Fichiers de configuration AWS
- **GUIDE_CONFIGURATION_CORS_CONSOLE.md** : Configuration CORS dans API Gateway
- **GUIDE_COGNITO_FRANCAIS.md** : Configuration Cognito
- **lambda-package/README_DEPLOIEMENT.md** : Guide de déploiement Lambda

---

## 🎯 CHECKLIST POUR GEMINI

### Avant de commencer
- [ ] Lire ce document en entier
- [ ] Lire `RESUME_ETAT_PROJET.md`
- [ ] Lire `RESUME_CHEMINS_AWS.md`
- [ ] Comprendre le problème de sérialisation
- [ ] Vérifier l'accès aux logs CloudWatch

### Pour corriger le problème
- [ ] Modifier `oauth_google()` pour forcer la sérialisation
- [ ] Tester la réponse API avec `curl` ou PowerShell
- [ ] Vérifier que `user` est un objet JSON valide
- [ ] Simplifier la logique frontend d'affichage du formulaire
- [ ] Tester le flow complet (connexion → formulaire → reconnexion)

### Pour déployer
- [ ] Modifier le code
- [ ] Exécuter `python lambda-package/deploy_backend.py`
- [ ] Vérifier les logs CloudWatch
- [ ] Tester sur `https://mapevent.world`

---

## 🔗 LIENS UTILES

### Console AWS (eu-west-1)
- **Lambda :** https://eu-west-1.console.aws.amazon.com/lambda/
- **API Gateway :** https://eu-west-1.console.aws.amazon.com/apigateway/
- **RDS :** https://eu-west-1.console.aws.amazon.com/rds/
- **Cognito :** https://eu-west-1.console.aws.amazon.com/cognito/
- **CloudWatch :** https://eu-west-1.console.aws.amazon.com/cloudwatch/
- **ElastiCache :** https://eu-west-1.console.aws.amazon.com/elasticache/

### Production
- **Site :** https://mapevent.world
- **API :** https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api

---

## 📞 COMMANDES AWS CLI ESSENTIELLES

```powershell
# Voir les logs Lambda
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1

# Mettre à jour les variables d'environnement
aws lambda update-function-configuration `
    --function-name mapevent-backend `
    --environment Variables="{RDS_HOST=...,RDS_PORT=5432,...}" `
    --region eu-west-1

# Voir les détails de la fonction Lambda
aws lambda get-function --function-name mapevent-backend --region eu-west-1

# Lister les APIs Gateway
aws apigateway get-rest-apis --region eu-west-1

# Voir les ressources d'une API
aws apigateway get-resources --rest-api-id j33osy4bvj --region eu-west-1
```

---

## ⚠️ NOTES IMPORTANTES

1. **Ne jamais commiter `lambda.env`** : Contient les mots de passe
2. **Toujours tester en production** : Le problème se produit uniquement avec Flask test client (Lambda)
3. **Vérifier les logs CloudWatch** : Les erreurs sont visibles là-bas
4. **Le problème est dans la sérialisation** : Pas dans la logique métier
5. **Le frontend détecte le problème** : Mais la logique d'affichage est complexe

---

**Dernière mise à jour :** 31 décembre 2024, 23:50  
**Version :** 1.0  
**Prêt pour Gemini :** ✅ OUI







