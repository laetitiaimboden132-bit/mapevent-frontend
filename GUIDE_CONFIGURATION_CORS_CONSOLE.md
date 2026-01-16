# Guide : Configuration CORS dans AWS API Gateway Console

Ce guide vous explique comment configurer CORS directement dans la console AWS pour résoudre les erreurs 500 sur les requêtes OPTIONS.

## 📋 Informations nécessaires

- **API Gateway ID** : `j33osy4bvj`
- **Stage** : `default`
- **Région** : `eu-west-1`
- **Endpoints à configurer** :
  - `/api/user/oauth/google` (Resource ID: `k70u2t`)
  - `/api/user/oauth/google/complete` (Resource ID: `rjh1m4`)
- **Origine autorisée** : `https://mapevent.world`

---

## 🚀 Étapes de configuration

### **Étape 1 : Accéder à API Gateway**

1. Connectez-vous à la [Console AWS](https://console.aws.amazon.com/)
2. Sélectionnez la région **eu-west-1** (Europe - Irlande)
3. Recherchez "API Gateway" dans la barre de recherche
4. Cliquez sur **API Gateway**
5. Dans la liste des APIs, trouvez votre API (elle devrait avoir l'ID `j33osy4bvj`)
6. Cliquez sur le nom de votre API

---

### **Étape 2 : Configurer `/api/user/oauth/google`**

#### **2.1 : Vérifier/Créer la méthode OPTIONS**

1. Dans le panneau de gauche, cliquez sur **Resources**
2. Trouvez et cliquez sur `/api/user/oauth/google`
3. Vérifiez si la méthode **OPTIONS** existe :
   - **Si OPTIONS existe** : Passez à l'étape 2.2
   - **Si OPTIONS n'existe pas** :
     - Cliquez sur **Actions** → **Create Method**
     - Sélectionnez **OPTIONS** dans le menu déroulant
     - Cliquez sur la coche ✓ à côté
     - Dans "Integration type", sélectionnez **Mock**
     - Cliquez sur **Save**

#### **2.2 : Configurer l'intégration Mock pour OPTIONS**

1. Cliquez sur la méthode **OPTIONS**
2. Cliquez sur **Integration Request**
3. Vérifiez que :
   - **Integration type** : `Mock`
   - **Integration HTTP method** : `POST`
4. Dans **Request Templates**, cliquez sur **Add mapping template**
5. Entrez `application/json` comme Content-Type
6. Dans le template, entrez :
   ```json
   {"statusCode": 200}
   ```
7. Cliquez sur **Save**

#### **2.3 : Configurer Method Response pour OPTIONS**

1. Cliquez sur **Method Response** (dans l'onglet OPTIONS)
2. Cliquez sur **200** (ou créez-le s'il n'existe pas)
3. Dans **Response Headers for 200**, cliquez sur **Add header**
4. Ajoutez ces 3 headers (un par un) :
   - `Access-Control-Allow-Headers` (type: String)
   - `Access-Control-Allow-Methods` (type: String)
   - `Access-Control-Allow-Origin` (type: String)
5. Cliquez sur **Save** après chaque ajout

#### **2.4 : Configurer Integration Response pour OPTIONS**

1. Cliquez sur **Integration Response** (dans l'onglet OPTIONS)
2. Cliquez sur **200** (ou créez-le s'il n'existe pas)
3. Dans **Header Mappings**, cliquez sur **Add header mapping**
4. Ajoutez ces 3 mappings (un par un) :

   **Mapping 1 :**
   - **Header name** : `Access-Control-Allow-Origin`
   - **Mapping** : `'https://mapevent.world'`
   - Cliquez sur ✓

   **Mapping 2 :**
   - **Header name** : `Access-Control-Allow-Methods`
   - **Mapping** : `'POST,OPTIONS'`
   - Cliquez sur ✓

   **Mapping 3 :**
   - **Header name** : `Access-Control-Allow-Headers`
   - **Mapping** : `'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'`
   - Cliquez sur ✓

5. Dans **Body Mapping Templates**, sélectionnez **When there are no templates defined**
6. Cliquez sur **Add mapping template**
7. Entrez `application/json` comme Content-Type
8. Dans le template, laissez vide ou entrez simplement :
   ```
   ""
   ```
9. Cliquez sur **Save**

#### **2.5 : Ajouter CORS headers à la méthode POST**

1. Revenez à la ressource `/api/user/oauth/google`
2. Cliquez sur la méthode **POST**
3. Cliquez sur **Method Response**
4. Pour chaque code de statut (200, 400, 500, etc.) :
   - Cliquez sur le code de statut
   - Dans **Response Headers**, ajoutez :
     - `Access-Control-Allow-Origin` (type: String)
   - Cliquez sur **Save**
5. Cliquez sur **Integration Response**
6. Pour chaque code de statut :
   - Cliquez sur le code de statut
   - Dans **Header Mappings**, ajoutez :
     - **Header name** : `Access-Control-Allow-Origin`
     - **Mapping** : `'https://mapevent.world'`
     - Cliquez sur ✓ puis **Save**

---

### **Étape 3 : Configurer `/api/user/oauth/google/complete`**

**Répétez exactement les mêmes étapes que pour `/api/user/oauth/google`** :

1. Trouvez `/api/user/oauth/google/complete` dans les Resources
2. Suivez les étapes 2.1 à 2.5 pour cet endpoint également

---

### **Étape 4 : Déployer l'API**

1. Une fois toutes les configurations terminées, cliquez sur **Actions** (en haut à droite)
2. Sélectionnez **Deploy API**
3. Dans **Deployment stage**, sélectionnez **default**
4. (Optionnel) Ajoutez une description : "Configuration CORS pour OAuth Google"
5. Cliquez sur **Deploy**

---

## ✅ Vérification

Après le déploiement, testez depuis votre navigateur :

1. Ouvrez la console développeur (F12)
2. Allez sur l'onglet **Network**
3. Cliquez sur "Connexion avec Google"
4. Vérifiez que la requête OPTIONS vers `/api/user/oauth/google` retourne :
   - **Status** : `200 OK`
   - **Headers** : 
     - `Access-Control-Allow-Origin: https://mapevent.world`
     - `Access-Control-Allow-Methods: POST,OPTIONS`
     - `Access-Control-Allow-Headers: Content-Type,Authorization,...`

---

## 🔧 Dépannage

### **Erreur : "Integration Response already exists"**
- Supprimez d'abord la réponse existante, puis recréez-la

### **Erreur : "Invalid mapping expression"**
- Assurez-vous d'utiliser des guillemets simples autour des valeurs :
  - ✅ Correct : `'https://mapevent.world'`
  - ❌ Incorrect : `https://mapevent.world` ou `"https://mapevent.world"`

### **Les headers ne s'affichent pas**
- Vérifiez que vous avez bien déployé l'API après les modifications
- Videz le cache de votre navigateur
- Vérifiez que les headers sont ajoutés à la fois dans **Method Response** ET **Integration Response**

---

## 📝 Notes importantes

- Les modifications ne sont actives qu'après le déploiement
- Vous devez configurer CORS pour **chaque méthode** (OPTIONS et POST)
- Les headers doivent être ajoutés dans **Method Response** (déclaration) ET **Integration Response** (valeur)

---

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :
1. Vérifiez les logs CloudWatch pour voir les erreurs exactes
2. Assurez-vous que tous les headers sont correctement mappés
3. Vérifiez que l'API a bien été déployée

Une fois terminé, les erreurs CORS 500 devraient être résolues ! 🎉









