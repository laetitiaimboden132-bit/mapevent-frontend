# 📚 INFORMATIONS COMPLÉMENTAIRES POUR GEMINI

## 🏗️ STRUCTURE DU PROJET ACTUELLE

```
MapEventAI_NEW/
├── frontend/                          # Frontend (dossier actuel)
│   ├── public/
│   │   ├── mapevent.html             # Page principale (~2200 lignes)
│   │   ├── map_logic.js              # Logique JavaScript (~20000 lignes)
│   │   ├── trees/                    # Arbres de catégories JSON
│   │   │   ├── events_tree.json
│   │   │   ├── booking_tree.json
│   │   │   └── service_tree.json
│   │   └── assets/                   # Images, CSS, etc.
│   │
│   ├── lambda-package/               # Backend Lambda
│   │   ├── handler.py                # Handler Lambda principal
│   │   ├── lambda_function.py        # Point d'entrée Lambda
│   │   ├── deploy_backend.py         # Script de déploiement
│   │   ├── lambda.env                # Variables d'environnement (SECRET)
│   │   │
│   │   └── backend/
│   │       ├── main.py               # Application Flask (~2300 lignes)
│   │       ├── requirements.txt       # Dépendances Python
│   │       ├── services/             # Services (email, modération, etc.)
│   │       └── database/             # Scripts DB
│   │
│   └── [nombreux fichiers .md]       # Documentation
│
└── [autres dossiers backend/ si existent]
```

---

## 🛠️ STACK TECHNOLOGIQUE

### Frontend
- **HTML5** : Structure de la page
- **CSS3** : Styles inline et dans `<style>` tags
- **JavaScript (ES6+)** : Vanilla JS, pas de framework
- **Leaflet.js 1.9.4** : Bibliothèque de cartes
- **Stripe.js** : Paiements (intégré)
- **Pas de build tool** : Code directement dans le navigateur

### Backend
- **Python 3.12+** : Langage principal
- **Flask 3.0.0** : Framework web
- **Flask-CORS 4.0.0** : Gestion CORS
- **psycopg2-binary 2.9.9** : Client PostgreSQL
- **redis 5.0.1** : Client Redis
- **boto3 1.34.0** : SDK AWS
- **awsgi** : Adapter WSGI pour Lambda
- **stripe 7.8.0** : SDK Stripe
- **Pillow 10.2.0** : Traitement d'images
- **google-cloud-vision 3.4.5** : Modération d'images

### Infrastructure AWS
- **Lambda** : Runtime Python 3.12
- **API Gateway** : REST API
- **RDS PostgreSQL** : Base de données
- **ElastiCache Redis** : Cache
- **Cognito** : Authentification OAuth
- **CloudFront** : CDN
- **Route 53** : DNS
- **ACM** : Certificats SSL

---

## 📦 DÉPENDANCES BACKEND COMPLÈTES

Voir `lambda-package/backend/requirements.txt` :
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

---

## 🔄 WORKFLOW DE DÉVELOPPEMENT

### Déploiement Backend (Lambda)
1. Modifier le code dans `lambda-package/backend/`
2. Exécuter `python lambda-package/deploy_backend.py`
3. Le script crée un ZIP et le déploie sur Lambda
4. Les variables d'environnement sont dans `lambda-package/lambda.env`

### Déploiement Frontend
1. Modifier les fichiers dans `public/`
2. Les fichiers sont servis via CloudFront depuis S3 (probablement)
3. Ou via un serveur HTTP local pour le développement

### Tests Locaux
- **Frontend local :** `http://localhost:3000/mapevent.html`
- **Backend local :** (si Flask local) `http://localhost:5005`
- **Backend Lambda :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api`

---

## 🐛 PROBLÈME PRINCIPAL ACTUEL - DÉTAILS TECHNIQUES

### Problème : Sérialisation `"[dict - 17 items]"`

#### Code Backend (lambda-package/backend/main.py)
```python
# Route oauth_google() - Ligne ~1700
# Le code essaie de sérialiser user_data avec json.dumps()
user_data_json_str = json.dumps(user_data, ensure_ascii=False, default=str)
user_data_clean = json.loads(user_data_json_str)

# Puis utilise make_response()
response = make_response(response_json_str)
response.headers['Content-Type'] = 'application/json'
return response
```

#### Code Handler Lambda (lambda-package/handler.py)
```python
# Ligne ~180-320
# Détecte si body_json['user'] est une chaîne "[dict - X items]"
if isinstance(body_json['user'], str) and body_json['user'].startswith('[dict'):
    # Essaie de récupérer l'email depuis le body de la requête
    request_body = event.get('body', '')
    request_data = json.loads(request_body) if request_body else {}
    user_email = request_data.get('email', '')
    
    # Si email trouvé, récupère depuis DB
    if user_email:
        # Connexion PostgreSQL et récupération des données
        # Reconstruction de user_data_fixed
        body_json['user'] = user_data_fixed
```

#### Code Frontend (public/map_logic.js)
```javascript
// Ligne ~526-548
// Détecte si syncData.user est "[dict - X items]"
if (typeof syncData.user === 'string') {
    if (syncData.user.startsWith('[dict') && syncData.user.includes('items]')) {
        console.error('❌ PROBLÈME SÉRIALISATION: syncData.user est "[dict - X items]"');
        backendUser = {}; // FORCER vide pour afficher le formulaire
    } else {
        backendUser = JSON.parse(syncData.user);
    }
}
```

### Pourquoi ça ne fonctionne pas ?
1. **Flask test client** transforme les dicts complexes en chaînes avant même que `json.dumps()` soit appelé
2. **Handler Lambda** ne peut pas toujours récupérer l'email (pas dans le body pour les callbacks OAuth)
3. **Frontend** détecte le problème mais la logique d'affichage du formulaire est complexe

---

## 🔍 POINTS D'ENTRÉE IMPORTANTS DU CODE

### Frontend - Authentification
- **Fichier :** `public/map_logic.js`
- **Fonction principale :** `handleCognitoCallbackIfPresent()` (ligne ~380)
- **Fonction connexion Google :** `startGoogleLogin()` (ligne ~2600)
- **Fonction formulaire :** `showProRegisterForm()` (ligne ~7000)
- **Fonction soumission :** `handleProRegisterSubmit()` (ligne ~8000)

### Backend - Authentification
- **Fichier :** `lambda-package/backend/main.py`
- **Route OAuth Google :** `@app.route('/api/user/oauth/google', methods=['POST'])` (ligne ~1328)
- **Route complétion profil :** `@app.route('/api/user/oauth/google/complete', methods=['POST'])` (ligne ~1809)

### Handler Lambda
- **Fichier :** `lambda-package/handler.py`
- **Fonction principale :** `lambda_handler(event, context)` (ligne ~40)
- **Détection sérialisation :** Ligne ~180-320

---

## 🧪 COMMENT TESTER

### Test Connexion Google
1. Ouvrir `https://mapevent.world`
2. Cliquer sur "Compte"
3. Cliquer sur "Connexion avec Google"
4. Se connecter avec Google
5. Vérifier si le formulaire d'inscription s'affiche

### Test API Backend Direct
```powershell
# Test endpoint OAuth Google
$body = @{
    email = "test@example.com"
    name = "Test User"
    sub = "test-sub-123"
    picture = ""
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Voir les Logs Lambda
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

---

## 📝 VARIABLES D'ENVIRONNEMENT LAMBDA

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
```

**Pour mettre à jour :**
```powershell
.\lambda-package\configure_lambda_env.ps1
```

---

## 🔐 COGNITO CONFIGURATION

**Dans le code frontend (`public/map_logic.js` ligne ~4) :**
```javascript
const COGNITO = {
  domain: "https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com",
  clientId: "...", // À récupérer depuis console AWS Cognito
  redirectUri: "https://mapevent.world/"
};
```

**Pour trouver le Client ID :**
1. Console AWS Cognito : https://eu-west-1.console.aws.amazon.com/cognito/
2. User Pools → Trouver le pool avec domaine `eu-west-19o9j6xsdr`
3. App clients → Copier le Client ID

---

## 🗄️ STRUCTURE BASE DE DONNÉES

### Table `users`
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

**Script de création :** `CREER_COLONNES_USERS.sql`

---

## 🚀 COMMANDES DE DÉPLOIEMENT

### Déployer Backend Lambda
```powershell
cd lambda-package
python deploy_backend.py
```

### Mettre à jour Variables d'Environnement
```powershell
cd lambda-package
.\configure_lambda_env.ps1
```

### Voir les Logs
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

### Tester Endpoint
```powershell
# Health check
Invoke-RestMethod -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/health"
```

---

## 🎯 OBJECTIFS PRIORITAIRES

### 1. URGENT - Corriger Sérialisation
**Problème :** `"[dict - 17 items]"` au lieu d'objet JSON

**Solutions à essayer :**
1. Dans `oauth_google()`, forcer la sérialisation AVANT de passer à Flask :
   ```python
   # Sérialiser chaque valeur individuellement
   user_data_serialized = {}
   for key, value in user_data.items():
       if isinstance(value, dict):
           user_data_serialized[key] = json.loads(json.dumps(value, default=str))
       else:
           user_data_serialized[key] = value
   ```

2. Utiliser `Response` directement avec `json.dumps()` :
   ```python
   from flask import Response
   return Response(
       json.dumps({'user': user_data_serialized, ...}, default=str),
       mimetype='application/json'
   )
   ```

3. Dans le handler Lambda, extraire l'email depuis le token Cognito au lieu du body

### 2. URGENT - Afficher Formulaire
**Problème :** Formulaire ne s'affiche pas quand profil incomplet

**Solution :** Simplifier la logique :
```javascript
// Si backendUser est vide OU profileComplete === false → Afficher formulaire
if (isBackendUserEmpty || !profileComplete || isNewUser) {
    showProRegisterForm();
    return;
}
```

### 3. IMPORTANT - Récupérer Données Utilisateur
**Problème :** Données perdues après reconnexion

**Solution :** S'assurer que le handler Lambda récupère bien depuis la DB quand `"[dict - X items]"` est détecté

---

## 📚 FICHIERS DE DOCUMENTATION IMPORTANTS

1. **RESUME_ETAT_PROJET.md** : État actuel du projet, problèmes, solutions tentées
2. **RESUME_CHEMINS_AWS.md** : Tous les chemins AWS, endpoints, credentials
3. **GUIDE_CONFIGURATION_CORS_CONSOLE.md** : Configuration CORS dans API Gateway
4. **PLAN_CORRECTION_AUTHENTIFICATION.md** : Plan de correction détaillé

---

## 🔧 OUTILS DE DÉVELOPPEMENT

### AWS CLI
- **Installation :** https://aws.amazon.com/cli/
- **Configuration :** `aws configure`
- **Région par défaut :** `eu-west-1`

### Python
- **Version :** 3.12+
- **Installation :** https://www.python.org/downloads/
- **Dépendances :** `pip install -r lambda-package/backend/requirements.txt`

### Git (optionnel)
- **Installation :** Voir `INSTALLATION_GIT_WINDOWS.md`
- **Configuration :** Voir `GIT_COMMANDES_ESSENTIELLES.md`

---

## 🎨 FRONTEND - POINTS CLÉS

### Variables Globales Importantes
```javascript
let currentUser = {};              // Utilisateur actuel
let currentMode = "event";         // Mode: "event" | "booking" | "service"
let eventsData = [];              // Données événements
let selectedCategories = [];      // Catégories sélectionnées
```

### Fonctions Principales
- `updateAccountButton()` : Met à jour le bouton compte dans la topbar
- `openLoginModal()` : Ouvre la modal de connexion
- `showProRegisterForm()` : Affiche le formulaire d'inscription
- `handleCognitoCallbackIfPresent()` : Traite le callback OAuth Google

### localStorage
- **Clés importantes :** `currentUser`, `cognito_tokens`
- **Gestion quota :** Fonction `safeSetItem()` avec nettoyage automatique
- **Nettoyage :** Fonction `cleanLocalStorage()` appelée périodiquement

---

## 🐛 BUGS CONNUS ET SOLUTIONS

### Bug 1 : `"[dict - 17 items]"` dans la réponse
- **Détecté :** Frontend ligne ~534, Handler Lambda ligne ~182
- **Solution partielle :** Handler Lambda récupère depuis DB si email disponible
- **À améliorer :** Extraire email depuis token Cognito

### Bug 2 : Formulaire ne s'affiche pas
- **Détecté :** Frontend ligne ~759
- **Solution partielle :** Vérification `isBackendUserEmpty`
- **À améliorer :** Simplifier la logique conditionnelle

### Bug 3 : Données utilisateur perdues
- **Détecté :** Après reconnexion, username/photo/adresse manquants
- **Solution partielle :** Handler Lambda récupère depuis DB
- **À améliorer :** S'assurer que toutes les données sont récupérées

---

## 📞 SUPPORT ET LOGS

### Logs CloudWatch
- **Log Group :** `/aws/lambda/mapevent-backend`
- **Région :** `eu-west-1`
- **URL Console :** https://eu-west-1.console.aws.amazon.com/cloudwatch/

### Logs Frontend
- **Console navigateur :** F12 → Console
- **Préfixes de logs :** 
  - `✅` : Succès
  - `⚠️` : Avertissement
  - `❌` : Erreur
  - `🔍` : Debug

---

## 🎯 PROCHAINES ÉTAPES RECOMMANDÉES

1. **Corriger la sérialisation** dans `oauth_google()` pour garantir un JSON valide
2. **Simplifier la logique frontend** pour l'affichage du formulaire
3. **Améliorer le handler Lambda** pour extraire l'email depuis le token Cognito
4. **Tester le flow complet** : Connexion → Formulaire → Sauvegarde → Reconnexion
5. **Ajouter des tests** pour éviter les régressions

---

**Dernière mise à jour :** 31 décembre 2024
**Version :** 1.0







