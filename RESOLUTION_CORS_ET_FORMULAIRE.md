# 🔧 Résolution du problème CORS et affichage du formulaire

## 📋 Situation actuelle

- ✅ Connexion Google fonctionne (OAuth Cognito)
- ❌ L'API backend retourne une erreur CORS 403
- ❌ Le formulaire de complément de profil ne s'affiche pas après connexion Google

## 🎯 Solution : 2 options

### Option 1 : Corriger le CORS côté backend (RECOMMANDÉ)

Le backend Flask doit être déployé avec la nouvelle configuration CORS. Les modifications sont déjà dans `lambda-package/backend/main.py`.

**Actions à faire :**

1. **Déployer le backend mis à jour** :
   ```bash
   cd lambda-package
   # Créer le package ZIP avec les dépendances
   # Déployer sur AWS Lambda
   ```

2. **Vérifier la configuration API Gateway** :
   - Dans AWS Console → API Gateway
   - Trouver votre API
   - Vérifier que les méthodes OPTIONS sont configurées
   - Ajouter les headers CORS si nécessaire :
     - `Access-Control-Allow-Origin: *`
     - `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
     - `Access-Control-Allow-Headers: Content-Type, Authorization`

3. **Tester l'endpoint** :
   ```bash
   curl -X OPTIONS https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google \
     -H "Origin: https://mapevent.world" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```

### Option 2 : Le fallback fonctionne déjà (si le cache est vidé)

Le code frontend a été modifié pour afficher le formulaire même si l'API échoue. **MAIS** le navigateur utilise une version en cache.

**Actions à faire :**

1. **Vider le cache CloudFront** :
   - AWS Console → CloudFront
   - Trouver la distribution pour `mapevent.world`
   - Invalidation → Créer une invalidation
   - Chemin : `/map_logic.js` ou `/*`

2. **OU vider le cache local** :
   - Ouvrir les DevTools (F12)
   - Clic droit sur le bouton refresh → "Vider le cache et actualiser"
   - OU `Ctrl+Shift+R` (Windows) / `Cmd+Shift+R` (Mac)

## 🔍 Vérification

Après avoir vidé le cache, lors de la connexion Google, vous devriez voir dans la console :

```
🆕 ========================================
🆕 ERREUR API - FALLBACK ACTIVÉ
🆕 ========================================
📋 Raison de l'erreur: Erreur réseau/CORS: ...
🚀 Ouverture du formulaire de complément de profil Google...
✅ Formulaire ouvert avec succès !
```

## 📝 Fichiers modifiés

- ✅ `public/map_logic.js` : Gestion d'erreur améliorée + fallback
- ✅ `lambda-package/backend/main.py` : Configuration CORS améliorée

## 🚀 Pour demain

1. **Déployer le backend** avec la nouvelle config CORS
2. **OU** vider le cache CloudFront pour charger le nouveau `map_logic.js`
3. **Tester** la connexion Google → le formulaire devrait s'afficher automatiquement

## 💡 Note importante

Le problème CORS vient probablement d'API Gateway qui bloque les requêtes OPTIONS (preflight). La configuration Flask est correcte, mais API Gateway doit aussi être configuré pour autoriser CORS.










