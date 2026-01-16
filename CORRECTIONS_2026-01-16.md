# Corrections du 16 janvier 2026

## Problème résolu : `ReferenceError: normalizedPhotoData is not defined`

### Symptôme
Erreur lors de la création de compte sans vérification :
```
ReferenceError: normalizedPhotoData is not defined
    connectUser https://mapevent.world/auth.js?v=...:3213
    createAccountWithoutVerification https://mapevent.world/auth.js?v=...:3789
```

### Cause
1. **Code** : `normalizedPhotoData` était bien défini dans `connectUser`, mais le cache CloudFront servait une ancienne version
2. **Script de déploiement** : Le script `deploy-frontend.ps1` n'invalidait pas `/auth.js*` dans CloudFront, donc les mises à jour de `auth.js` n'étaient pas propagées

### Solution appliquée

#### 1. Code corrigé (`public/auth.js`)
- `normalizedPhotoData` défini au début de `connectUser` (ligne 3186)
- Ajout de logs de version pour vérifier le chargement de la bonne version
- Version : `2026-01-16 11:26`

```javascript
function connectUser(user, tokens, rememberMe) {
  // ⚠️⚠️⚠️ VERSION 2026-01-16 11:26 - normalizedPhotoData défini au début
  console.log('[CONNECT] ✅✅✅ VERSION 2026-01-16 11:26 - connectUser avec normalizedPhotoData corrigé');
  
  // ⚠️ CRITIQUE : Normaliser photoData AU DÉBUT - DOIT être défini avant toute utilisation
  let normalizedPhotoData = user.photoData || null;
  if (normalizedPhotoData === 'null' || normalizedPhotoData === 'undefined' || normalizedPhotoData === '' || !normalizedPhotoData) {
    normalizedPhotoData = null;
  }
  // ... reste du code
}
```

#### 2. Script de déploiement corrigé (`deploy-frontend.ps1`)
- Ajout de `/auth.js*` à la liste des chemins invalidés dans CloudFront
- Maintenant invalide : `/map_logic.js*`, `/auth.js*`, `/mapevent.html*`, `/index.html*`

### Fichiers modifiés
- `public/auth.js` : Correction de `normalizedPhotoData`
- `public/mapevent.html` : Cache-busting mis à jour (`v=20260116-112600-FINAL-FIX`)
- `deploy-frontend.ps1` : Ajout de l'invalidation de `/auth.js*`

### Statut
✅ **RÉSOLU** - Testé et fonctionnel le 16 janvier 2026

### Notes importantes
- Toujours inclure `/auth.js*` dans les invalidations CloudFront lors des déploiements
- Le cache CloudFront peut prendre jusqu'à 20 secondes pour se propager
- Utiliser une fenêtre privée pour tester sans cache navigateur
