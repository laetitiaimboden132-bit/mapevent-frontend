# 🔍 Déboguer l'avatar qui ne s'affiche pas sur le site

## ✅ Ce qui fonctionne

- ✅ L'image s'affiche directement avec l'URL → S3 est bien configuré
- ✅ CORS est configuré
- ✅ Bucket Policy est configurée

## ❌ Ce qui ne fonctionne pas

- ❌ L'avatar ne s'affiche pas dans le bloc compte sur le site

---

## 🔍 Diagnostic

### Étape 1 : Vérifier l'URL dans le code JavaScript

1. **Ouvrez votre site** : https://mapevent.world
2. **Ouvrez les DevTools** (F12 ou clic droit > Inspecter)
3. **Onglet "Console"**
4. **Tapez cette commande** :

```javascript
console.log('Profile Photo:', currentUser.profilePhoto);
console.log('Profile Photo URL:', currentUser.profile_photo_url);
console.log('Avatar:', currentUser.avatar);
```

5. **Appuyez sur Entrée**

6. **Regardez ce qui s'affiche** :
   - Est-ce que l'URL est présente ?
   - Est-ce que l'URL est correcte (commence par `https://mapevent-avatars.s3...`) ?

---

### Étape 2 : Vérifier les erreurs dans l'onglet Network

1. **Dans les DevTools**, allez dans l'onglet **"Network"** (Réseau)
2. **Rechargez la page** (F5)
3. **Filtrez par "jpg"** ou "avatar" ou "s3"
4. **Cherchez la requête vers l'image S3**
5. **Cliquez sur la requête**

6. **Vérifiez** :
   - **Status** : Doit être `200 OK` (pas `404` ou `403`)
   - **Headers** : Doit avoir `Access-Control-Allow-Origin: *`
   - **Preview** : L'image doit s'afficher

---

### Étape 3 : Vérifier le localStorage

1. **Dans la Console**, tapez :

```javascript
const user = JSON.parse(localStorage.getItem('currentUser'));
console.log('User from localStorage:', user);
console.log('Profile Photo:', user?.profilePhoto);
console.log('Profile Photo URL:', user?.profile_photo_url);
```

2. **Vérifiez** :
   - Est-ce que `profilePhoto` contient l'URL S3 ?
   - Est-ce que l'URL est correcte ?

---

## 🔧 Solutions possibles

### Solution 1 : Vider le cache et reconnecter

1. **Videz complètement le cache** :
   - Safari : `Cmd+Option+E` (Mac) ou `Ctrl+Shift+Delete` (Windows)
   - Chrome : `Ctrl+Shift+Delete` puis cochez "Images et fichiers en cache"

2. **Déconnectez-vous** du site
3. **Reconnectez-vous** avec Google OAuth
4. **Vérifiez** que l'avatar s'affiche

---

### Solution 2 : Vérifier que l'URL est bien sauvegardée

Si l'URL n'est pas dans `currentUser.profilePhoto`, il faut vérifier que le backend renvoie bien l'URL S3 après la connexion Google.

**Dans les DevTools > Network** :
1. **Cherchez la requête** vers `/api/user/oauth/google` ou `/api/user/oauth/google/complete`
2. **Cliquez dessus**
3. **Onglet "Response"** (Réponse)
4. **Vérifiez** que `profile_photo_url` contient l'URL S3 :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

---

### Solution 3 : Forcer la mise à jour de l'URL

Si l'URL n'est pas correcte, vous pouvez la forcer dans la console :

```javascript
// Vérifier l'URL actuelle
console.log('Current profilePhoto:', currentUser.profilePhoto);

// Forcer l'URL S3
currentUser.profilePhoto = 'https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg';
localStorage.setItem('currentUser', JSON.stringify(currentUser));

// Recharger l'affichage
showAccountModalTab('profil'); // ou le nom de votre onglet
```

---

## 📋 Checklist de diagnostic

- [ ] J'ai vérifié `currentUser.profilePhoto` dans la console
- [ ] J'ai vérifié les erreurs dans l'onglet Network
- [ ] J'ai vérifié le localStorage
- [ ] J'ai vidé le cache et reconnecté
- [ ] J'ai vérifié la réponse du backend

---

**Dites-moi ce que vous obtenez dans la console quand vous tapez `currentUser.profilePhoto` !** 😊




