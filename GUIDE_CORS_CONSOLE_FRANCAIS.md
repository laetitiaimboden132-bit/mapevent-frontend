# Guide : Configuration CORS dans AWS API Gateway (Interface française)

## 📋 Informations nécessaires

- **API Gateway ID** : `j33osy4bvj`
- **Étape de déploiement** : `default`
- **Région** : `eu-west-1` (Europe - Irlande)
- **Endpoints à configurer** :
  - `/api/user/oauth/google`
  - `/api/user/oauth/google/complete`
- **Origine autorisée** : `https://mapevent.world`

---

## 🚀 Étapes de configuration

### **Étape 1 : Accéder à API Gateway**

1. Connectez-vous à la [Console AWS](https://console.aws.amazon.com/)
2. En haut à droite, sélectionnez la région **eu-west-1** (Europe - Irlande)
3. Dans la barre de recherche en haut, tapez **"API Gateway"**
4. Cliquez sur **API Gateway**
5. Dans la liste des APIs, trouvez votre API (ID : `j33osy4bvj`)
6. Cliquez sur le nom de votre API

---

### **Étape 2 : Configurer `/api/user/oauth/google`**

#### **2.1 : Accéder à la ressource**

1. Dans le panneau de gauche, cliquez sur **Ressources** (Resources)
2. Déroulez l'arborescence pour trouver `/api/user/oauth/google`
3. Cliquez sur `/api/user/oauth/google`

#### **2.2 : Utiliser l'action "Activer CORS"**

1. En haut à droite, cliquez sur **Actions** (Actions)
2. Dans le menu déroulant, sélectionnez **Activer CORS** (Enable CORS)
   
   ⚠️ **Si vous ne voyez pas "Activer CORS"** :
   - Vérifiez que vous avez bien sélectionné la ressource (pas la méthode)
   - Cherchez dans le menu "Actions" → peut-être "Activer CORS" ou "CORS"
   - Sinon, passez à la méthode manuelle ci-dessous

3. Dans la fenêtre qui s'ouvre, configurez :
   
   **Origines autorisées (Access-Control-Allow-Origin)** :
   - Entrez : `https://mapevent.world`
   
   **En-têtes autorisés (Access-Control-Allow-Headers)** :
   - Entrez : `Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token`
   
   **Méthodes autorisées (Access-Control-Allow-Methods)** :
   - Cochez : `POST` et `OPTIONS`
   
   **Exposer les en-têtes** :
   - Laissez vide ou ajoutez : `Content-Length,X-Amzn-RequestId`
   
   **Durée de mise en cache (Access-Control-Max-Age)** :
   - Laissez `600` (10 minutes) ou changez selon vos besoins

4. **IMPORTANT** : Cochez la case **Remplacer les en-têtes CORS existants** (Replace existing CORS headers)

5. Cliquez sur **Activer CORS et remplacer les valeurs existantes** (Enable CORS and replace existing CORS headers)

6. Dans la fenêtre de confirmation, cliquez sur **Oui, remplacer les valeurs existantes** (Yes, replace existing values)

#### **2.3 : Méthode manuelle (si "Activer CORS" n'existe pas)**

Si vous ne trouvez pas l'option "Activer CORS", configurez manuellement :

**A. Méthode OPTIONS :**

1. Cliquez sur la méthode **OPTIONS** (ou créez-la si elle n'existe pas)
2. Cliquez sur **Réponse de méthode** (Method Response)
3. Cliquez sur **200**
4. Dans **En-têtes de réponse pour 200**, cliquez sur **Ajouter un en-tête**
5. Ajoutez ces 3 en-têtes (un par un) :
   - `Access-Control-Allow-Headers` (Type: Chaîne)
   - `Access-Control-Allow-Methods` (Type: Chaîne)
   - `Access-Control-Allow-Origin` (Type: Chaîne)
6. Cliquez sur **Enregistrer** après chaque ajout

7. Cliquez sur **Réponse d'intégration** (Integration Response)
8. Cliquez sur **200**
9. Dans **Mappages d'en-têtes** (Header Mappings), cliquez sur **Ajouter un mappage d'en-tête**
10. Ajoutez ces 3 mappings (un par un) :
    
    **Mapping 1 :**
    - **Nom de l'en-tête** : `Access-Control-Allow-Origin`
    - **Mappage** : `'https://mapevent.world'` ⚠️ **Guillemets simples obligatoires**
    - Cliquez sur ✓
    
    **Mapping 2 :**
    - **Nom de l'en-tête** : `Access-Control-Allow-Methods`
    - **Mappage** : `'POST,OPTIONS'` ⚠️ **Guillemets simples obligatoires**
    - Cliquez sur ✓
    
    **Mapping 3 :**
    - **Nom de l'en-tête** : `Access-Control-Allow-Headers`
    - **Mappage** : `'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'`
    - Cliquez sur ✓

11. Cliquez sur **Enregistrer**

**B. Méthode POST :**

1. Revenez à la ressource `/api/user/oauth/google`
2. Cliquez sur la méthode **POST**
3. Cliquez sur **Réponse de méthode** (Method Response)
4. Pour chaque code de statut (200, 400, 500, etc.) :
   - Cliquez sur le code de statut
   - Dans **En-têtes de réponse**, cliquez sur **Ajouter un en-tête**
   - Entrez : `Access-Control-Allow-Origin` (Type: Chaîne)
   - Cliquez sur **Enregistrer**

5. Cliquez sur **Réponse d'intégration** (Integration Response)
6. Pour chaque code de statut :
   - Cliquez sur le code de statut
   - Dans **Mappages d'en-têtes**, cliquez sur **Ajouter un mappage d'en-tête**
   - **Nom de l'en-tête** : `Access-Control-Allow-Origin`
   - **Mappage** : `'https://mapevent.world'` ⚠️ **Guillemets simples obligatoires**
   - Cliquez sur ✓ puis **Enregistrer**

---

### **Étape 3 : Configurer `/api/user/oauth/google/complete`**

**Répétez exactement les mêmes étapes que pour `/api/user/oauth/google`** :

1. Trouvez `/api/user/oauth/google/complete` dans les Ressources
2. Suivez les étapes 2.2 ou 2.3 pour cet endpoint également

---

### **Étape 4 : Déployer l'API**

1. Une fois toutes les configurations terminées, cliquez sur **Actions** (en haut à droite)
2. Sélectionnez **Déployer l'API** (Deploy API)
3. Dans **Étape de déploiement** (Deployment stage), sélectionnez **default**
4. (Optionnel) Ajoutez une description : "Configuration CORS pour OAuth Google"
5. Cliquez sur **Déployer** (Deploy)

---

## ✅ Vérification

Après le déploiement, testez depuis votre navigateur :

1. Ouvrez la console développeur (F12)
2. Allez sur l'onglet **Réseau** (Network)
3. Cliquez sur "Connexion avec Google"
4. Vérifiez que la requête OPTIONS vers `/api/user/oauth/google` retourne :
   - **Statut** : `200 OK`
   - **En-têtes** : 
     - `Access-Control-Allow-Origin: https://mapevent.world`
     - `Access-Control-Allow-Methods: POST,OPTIONS`
     - `Access-Control-Allow-Headers: Content-Type,Authorization,...`

---

## 🔧 Dépannage

### **Je ne trouve pas "Activer CORS" dans le menu Actions**

**Solutions :**
1. Vérifiez que vous avez sélectionné la **ressource** (pas une méthode individuelle)
2. Cherchez dans le menu : peut-être "CORS" ou "Configurer CORS"
3. Utilisez la méthode manuelle décrite dans la section 2.3

### **Erreur : "Expression de mappage non valide"**

- Assurez-vous d'utiliser des **guillemets simples** autour des valeurs :
  - ✅ Correct : `'https://mapevent.world'`
  - ❌ Incorrect : `https://mapevent.world` ou `"https://mapevent.world"`

### **Les en-têtes ne s'affichent pas**

- Vérifiez que vous avez bien **déployé l'API** après les modifications
- Videz le cache de votre navigateur (Ctrl+Shift+Delete)
- Vérifiez que les en-têtes sont ajoutés à la fois dans **Réponse de méthode** ET **Réponse d'intégration**

---

## 📝 Notes importantes

- Les modifications ne sont actives qu'**après le déploiement**
- Vous devez configurer CORS pour **chaque méthode** (OPTIONS et POST)
- Les en-têtes doivent être ajoutés dans **Réponse de méthode** (déclaration) ET **Réponse d'intégration** (valeur)

---

## 🆘 Termes français dans AWS Console

Si vous ne trouvez pas certains termes, voici les traductions possibles :

- **Actions** = Actions (ou "Actions" en français)
- **Ressources** = Resources (ou "Ressources")
- **Réponse de méthode** = Method Response
- **Réponse d'intégration** = Integration Response
- **Mappages d'en-têtes** = Header Mappings
- **Déployer l'API** = Deploy API
- **Étape de déploiement** = Deployment stage

Une fois terminé, les erreurs CORS 500 devraient être résolues ! 🎉


