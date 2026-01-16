# 🍎 Instructions pour Safari

## 📱 Ouvrir la console sur Safari

### Méthode 1 : Menu Safari
1. Cliquez sur **Safari** (en haut à gauche)
2. Cliquez sur **Paramètres** (ou **Préférences**)
3. Allez dans l'onglet **Avancé**
4. Cochez **"Afficher le menu Développement dans la barre de menus"**
5. Fermez les paramètres
6. Maintenant, cliquez sur **Développement** (nouveau menu en haut)
7. Cliquez sur **Afficher le console JavaScript** (ou **Show JavaScript Console**)

### Méthode 2 : Raccourci clavier
1. Activez d'abord le menu Développement (voir Méthode 1)
2. Appuyez sur **Cmd+Option+C** (⌘⌥C)

## 🧪 Tests à faire dans la console

### Test 1 : Vérifier que la fonction existe
Tapez dans la console :
```javascript
typeof openAgendaWindow
```
**Résultat attendu** : `"function"`  
**Si `"undefined"`** : Le fichier n'est pas chargé ou le cache bloque

### Test 2 : Tester manuellement
Tapez dans la console :
```javascript
openAgendaWindow()
```
**Résultat attendu** : Une fenêtre s'ouvre avec votre agenda

### Test 3 : Vérifier le bouton
Tapez dans la console :
```javascript
const btn = document.querySelector('button[onclick*="openAgendaWindow"]');
console.log(btn);
```
**Résultat attendu** : Le bouton existe

## 🔧 Vider le cache sur Safari

1. Cliquez sur **Safari** → **Paramètres** (ou **Préférences**)
2. Allez dans l'onglet **Avancé**
3. Cliquez sur **"Vider les caches"** (ou **"Empty Caches"**)
4. OU utilisez le raccourci : **Cmd+Option+E** (⌘⌥E)

## 🔄 Rechargement forcé sur Safari

- **Cmd+Shift+R** (⌘⇧R) : Recharger en ignorant le cache
- OU **Cmd+Option+R** (⌘⌥R)

## 📋 Informations à me donner

1. **Résultat du Test 1** : `typeof openAgendaWindow` → ?
2. **Résultat du Test 2** : Est-ce que `openAgendaWindow()` fonctionne ?
3. **Erreurs dans la console** : Y a-t-il des messages en rouge ?
4. **Version de Safari** : Safari → À propos de Safari

## 🎯 Si la console ne s'ouvre pas

1. Vérifiez que le menu **Développement** est activé (Paramètres → Avancé)
2. Si vous ne voyez pas "Développement", activez-le d'abord
3. Essayez le raccourci **Cmd+Option+C**





