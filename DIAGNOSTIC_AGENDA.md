# 🔍 Diagnostic - Bouton Agenda

## ✅ Ce qui est vérifié

1. **Code modifié** : Ligne 16910-16911 dans `public/map_logic.js`
   - Le bouton appelle `openAgendaWindow()` 
   - La fonction existe à la ligne 14424

2. **Fonction définie** : `openAgendaWindow()` existe dans le code

## 🧪 Tests à faire dans la console (F12)

### Test 1 : Vérifier que la fonction existe
```javascript
typeof openAgendaWindow
```
**Résultat attendu** : `"function"`  
**Si `"undefined"`** : Le fichier n'est pas chargé ou le cache bloque

### Test 2 : Vérifier le bouton
```javascript
const btn = document.querySelector('button[onclick*="openAgendaWindow"]');
console.log(btn);
console.log(btn?.onclick);
```
**Résultat attendu** : Le bouton existe et a un onclick

### Test 3 : Tester manuellement
```javascript
openAgendaWindow()
```
**Résultat attendu** : Une fenêtre s'ouvre avec l'agenda

### Test 4 : Vérifier le cache
```javascript
// Vérifier la date de chargement du script
performance.getEntriesByType('resource').filter(r => r.name.includes('map_logic'))
```
**Résultat** : Vérifier la date de chargement

## 🔧 Solutions

### Solution 1 : Vider le cache COMPLÈTEMENT
1. **Chrome/Edge** :
   - `Ctrl+Shift+Delete`
   - Cochez "Images et fichiers en cache"
   - Période : "Toutes les périodes"
   - Cliquez "Effacer les données"
   - **Fermez TOUTES les fenêtres du navigateur**
   - Rouvrez le navigateur
   - Allez sur votre site

2. **Firefox** :
   - `Ctrl+Shift+Delete`
   - Cochez "Cache"
   - Cliquez "Effacer maintenant"
   - Fermez et rouvrez

### Solution 2 : Navigation privée
- `Ctrl+Shift+N` (Chrome) ou `Ctrl+Shift+P` (Firefox)
- Testez dans cette fenêtre

### Solution 3 : Rechargement forcé
- `Ctrl+Shift+R` (ou `Ctrl+F5`)
- Faites-le 3-4 fois

### Solution 4 : Vérifier le serveur
Si vous utilisez un serveur local, vérifiez que le fichier `map_logic.js` est bien servi :
- Ouvrez les DevTools (F12)
- Onglet "Network"
- Rechargez la page
- Cherchez `map_logic.js`
- Cliquez dessus
- Vérifiez l'onglet "Response" - le code doit contenir `openAgendaWindow` à la ligne 14424

## 📋 Informations à me donner

Si ça ne marche toujours pas, envoyez-moi :

1. **Résultat du Test 1** : `typeof openAgendaWindow`
2. **Résultat du Test 2** : Ce que `console.log(btn)` affiche
3. **Erreurs dans la console** : Toutes les erreurs en rouge
4. **Résultat du Test 3** : Est-ce que `openAgendaWindow()` fonctionne manuellement ?
5. **Version du navigateur** : Chrome/Edge/Firefox + version

## 🎯 Si la fonction existe mais le bouton ne fonctionne pas

Le problème peut venir de :
- Un autre script qui modifie le bouton après le chargement
- Un événement qui empêche le clic
- Un conflit avec d'autres fonctions

Dans ce cas, testez :
```javascript
// Forcer l'événement onclick
const btn = document.querySelector('button[onclick*="openAgendaWindow"]');
if (btn) {
  btn.onclick = openAgendaWindow;
  console.log('✅ Bouton forcé');
}
```





