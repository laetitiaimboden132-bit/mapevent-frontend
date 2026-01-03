# 🔧 Corriger l'erreur CORS 403

## ❌ Erreur actuelle
```
Access-Control-Allow-Origin manquant
Code d'état : 403
```

## ✅ Solution étape par étape

### 1. Ouvrir API Gateway
- AWS Console > API Gateway
- Sélectionnez votre API

### 2. Naviguer vers la méthode
- Ressources > `/api` > `/payments` > `/create-checkout-session`
- **Sélectionnez la MÉTHODE POST** (pas OPTIONS, pas la ressource)

### 3. Activer CORS
- Cliquez sur **"Actions"** (en haut à droite)
- Sélectionnez **"Activer CORS"**

### 4. Configurer CORS
Dans le formulaire qui s'ouvre :

**Origines autorisées :**
```
*
```
(ou `https://mapevent.world` pour la production)

**Méthodes autorisées :**
```
POST, OPTIONS
```

**Headers autorisés :**
```
Content-Type, Origin
```

**Headers exposés :** (laissez vide ou ajoutez)
```
*
```

### 5. Valider
- Cochez **"Activer CORS et remplacer les valeurs CORS existantes"**
- Cliquez **"Activer CORS et remplacer les valeurs CORS existantes"**

### 6. Vérifier OPTIONS
- API Gateway devrait avoir créé automatiquement la méthode **OPTIONS**
- Vérifiez dans les ressources que **OPTIONS** existe sous `/create-checkout-session`
- Si OPTIONS n'existe pas, créez-la manuellement :
  - Cliquez sur `/create-checkout-session`
  - "Actions" > "Créer une méthode" > OPTIONS
  - Lier à la même intégration Lambda que POST

### 7. DÉPLOYER (CRITIQUE !)
- Cliquez sur **"Actions"** (en haut)
- Sélectionnez **"Déployer l'API"**
- **Stage :** `default` (ou votre stage)
- **Description :** "Activation CORS paiement"
- Cliquez **"Déployer"**

### 8. Attendre
- Attendez **30 secondes** après le déploiement
- Les changements prennent quelques secondes à se propager

### 9. Retester
- Relancez le test dans `test-api.html`
- Vérifiez la console (F12) > Network
- La requête OPTIONS devrait retourner 200 avec les headers CORS

## 🔍 Vérifications

### Dans la console du navigateur (F12 > Network)
1. Cherchez la requête **OPTIONS** (preflight)
2. Elle doit retourner **Status 200**
3. Headers de réponse doivent contenir :
   - `Access-Control-Allow-Origin: *` (ou votre domaine)
   - `Access-Control-Allow-Methods: POST, OPTIONS`
   - `Access-Control-Allow-Headers: Content-Type, Origin`

### Si OPTIONS retourne 403
- La méthode OPTIONS n'existe pas ou n'est pas configurée
- Créez-la manuellement et liez-la à Lambda

### Si OPTIONS retourne 200 mais POST échoue
- Vérifiez que les headers CORS sont identiques sur POST et OPTIONS
- Vérifiez que l'API a bien été déployée

## ⚠️ Erreurs courantes

❌ **Oublier de déployer** → Les changements ne sont pas actifs
❌ **Activer CORS sur /payments** → Il faut l'activer sur /create-checkout-session
❌ **Activer CORS sur OPTIONS** → Il faut l'activer sur POST (OPTIONS sera créé automatiquement)
❌ **Ne pas attendre** → Les changements prennent 10-30 secondes

## ✅ Checklist

- [ ] CORS activé sur la méthode **POST** de `/create-checkout-session`
- [ ] Méthode **OPTIONS** existe (créée automatiquement ou manuellement)
- [ ] Origines autorisées : `*` ou votre domaine
- [ ] Méthodes autorisées : `POST, OPTIONS`
- [ ] Headers autorisés : `Content-Type, Origin`
- [ ] API **DÉPLOYÉE** sur le stage `default`
- [ ] Attendu 30 secondes après le déploiement
- [ ] Testé à nouveau
