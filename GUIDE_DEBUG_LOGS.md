# 🔍 Guide de débogage - Logs et console

## 📊 Deux endroits pour voir les logs

### 1. Console du navigateur (F12) - RECOMMANDÉ pour commencer

**Comment ouvrir :**
- Appuyez sur `F12` ou `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
- Ou clic droit → "Inspecter" / "Inspecter l'élément"

**Onglets importants :**

#### 📝 Console (Console)
- **Affiche tous les logs JavaScript** du frontend
- Cherchez les messages avec ces préfixes :
  - `🆕` = Fallback activé (erreur API)
  - `📋` = Informations de débogage
  - `✅` = Succès
  - `❌` = Erreur
  - `⚠️` = Avertissement

**Exemple de logs à chercher :**
```
🆕 ========================================
🆕 ERREUR API - FALLBACK ACTIVÉ
🆕 ========================================
📋 Raison de l'erreur: Erreur réseau/CORS: ...
🚀 Tentative d'ouverture du formulaire de complément de profil Google...
✅ Formulaire ouvert avec succès !
```

#### 🌐 Réseau (Network)
- **Affiche toutes les requêtes HTTP** (API, images, etc.)
- Filtrez par "Fetch/XHR" pour voir les appels API
- Cliquez sur une requête pour voir :
  - **Headers** : En-têtes envoyés/reçus
  - **Response** : Réponse du serveur
  - **Status** : Code HTTP (200 = OK, 403 = CORS, 500 = Erreur serveur)

**Requêtes importantes à vérifier :**
- `/api/user/oauth/google` → Doit retourner 200 ou 201
- Si vous voyez `(failed)` ou `CORS error` → Problème CORS

**Comment filtrer :**
1. Ouvrez l'onglet Network
2. Cliquez sur le filtre "Fetch/XHR" (ou tapez "api" dans la barre de recherche)
3. Rechargez la page ou testez la connexion Google
4. Regardez les requêtes vers `/api/user/oauth/google`

---

### 2. AWS CloudWatch - Pour les logs backend

**Comment accéder :**
1. AWS Console → CloudWatch
2. Dans le menu de gauche : **Logs** → **Log groups**
3. Cherchez : `/aws/lambda/mapevent-backend`
4. Cliquez dessus → **Log streams** → Choisissez le plus récent

**Ou directement :**
1. AWS Console → Lambda
2. Fonction : `mapevent-backend`
3. Onglet **Monitor** → **View CloudWatch logs**

**Ce que vous verrez :**
- Logs Python du backend Flask
- Erreurs de code
- Requêtes reçues
- Réponses envoyées

**Exemple de logs :**
```
🔍 Path reçu: /api/user/oauth/google
🔍 Méthode: POST
✅ Requête OPTIONS détectée pour /api/user/oauth/google
🔍 Réponse Flask: 200
```

---

## 🎯 Scénarios de débogage

### Scénario 1 : Le formulaire ne s'affiche pas

**Dans la console F12 (Console) :**
1. Cherchez les messages `🆕 ERREUR API - FALLBACK ACTIVÉ`
2. Si vous ne voyez rien → Le code n'est peut-être pas chargé (cache)
3. Si vous voyez `⚠️ Éléments DOM non prêts` → Problème de timing

**Dans la console F12 (Network) :**
1. Cherchez la requête `/api/user/oauth/google`
2. Si Status = `(failed)` ou `CORS error` → Problème CORS backend
3. Si Status = `403` → Problème CORS
4. Si Status = `500` → Erreur serveur (voir CloudWatch)

**Dans CloudWatch :**
1. Vérifiez si la requête arrive au backend
2. Si oui → Voir les erreurs Python
3. Si non → Problème API Gateway ou CORS

---

### Scénario 2 : Erreur CORS

**Dans la console F12 (Network) :**
- La requête apparaît en rouge
- Message : `CORS policy: No 'Access-Control-Allow-Origin' header`
- Status : `(failed)` ou `403`

**Solution :**
- Vérifier CloudWatch pour voir si OPTIONS est géré
- Vérifier que le backend est bien déployé avec la nouvelle config

---

### Scénario 3 : Le formulaire s'affiche mais ne fonctionne pas

**Dans la console F12 (Console) :**
- Cherchez les erreurs JavaScript
- Vérifiez les messages lors du clic sur "Créer le compte"

**Dans la console F12 (Network) :**
- Vérifiez la requête `/api/user/oauth/google/complete`
- Status doit être `200` ou `201`

---

## 🛠️ Commandes utiles dans la console F12

**Vider le cache et recharger :**
```javascript
location.reload(true)
```

**Vérifier si currentUser existe :**
```javascript
console.log(JSON.parse(localStorage.getItem('currentUser')))
```

**Vérifier si le formulaire existe :**
```javascript
document.getElementById('google-profile-completion-modal')
```

**Forcer l'ouverture du formulaire :**
```javascript
if (typeof openGoogleProfileCompletionModal === 'function') {
    openGoogleProfileCompletionModal();
}
```

---

## 📋 Checklist de débogage

- [ ] Console F12 ouverte (F12)
- [ ] Onglet Console vérifié pour les erreurs JavaScript
- [ ] Onglet Network vérifié pour les requêtes API
- [ ] CloudWatch vérifié pour les logs backend
- [ ] Cache vidé (Ctrl+Shift+R)
- [ ] Logs recherchés avec les préfixes 🆕 📋 ✅ ❌ ⚠️

---

## 💡 Astuce

**Commencez toujours par F12 (Console)** car :
- C'est plus rapide
- Vous voyez les erreurs frontend immédiatement
- Les requêtes réseau montrent les problèmes CORS

**Utilisez CloudWatch seulement si :**
- La requête arrive au backend mais échoue
- Vous avez besoin de voir les logs Python détaillés
- Vous suspectez un problème côté serveur









