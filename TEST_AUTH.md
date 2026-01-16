# Test des Fonctions AUTH

## Instructions

1. Ouvrez votre application dans le navigateur
2. Ouvrez la console développeur (F12)
3. Copiez-collez le contenu du fichier `test_auth_functions.js` dans la console
4. Appuyez sur Entrée

## Ce que le test vérifie

✅ **Fonctions exposées globalement** : Vérifie que toutes les fonctions AUTH sont accessibles via `window.*`

✅ **Variables globales** : Vérifie que les variables AUTH (`registerStep`, `registerData`, etc.) existent

✅ **Chargement des scripts** : Vérifie que `auth.js` et `map_logic.js` sont bien chargés

✅ **Ordre de chargement** : Vérifie que `auth.js` est chargé **AVANT** `map_logic.js` (important !)

✅ **Tests fonctionnels** : Teste quelques fonctions basiques sans déclencher d'actions

## Résultat attendu

Si tout est correct, vous devriez voir :
```
✅ TOUS LES TESTS SONT PASSÉS !
Les fonctions AUTH sont correctement extraites et exposées.
```

## Si des tests échouent

1. **Fonctions manquantes** : Vérifiez que `auth.js` est bien chargé dans `mapevent.html`
2. **Ordre incorrect** : Assurez-vous que `<script src="auth.js">` est **AVANT** `<script src="map_logic.js">`
3. **Erreurs JavaScript** : Vérifiez la console pour d'autres erreurs qui pourraient bloquer le chargement

## Test manuel rapide

Vous pouvez aussi tester manuellement dans la console :

```javascript
// Vérifier que les fonctions existent
typeof window.openAuthModal === 'function'  // doit retourner "function"
typeof window.performLogin === 'function'   // doit retourner "function"
typeof window.logout === 'function'         // doit retourner "function"

// Vérifier l'ordre de chargement
Array.from(document.querySelectorAll('script[src]')).map(s => s.src)
// auth.js doit apparaître avant map_logic.js
```
