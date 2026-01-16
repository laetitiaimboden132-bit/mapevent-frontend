# Solution pour le Problème de Cache

## Problème
Le navigateur charge toujours `map_logic.js?v=20260107-56` au lieu de `v=20260111-120000`.

## Solutions (essayez dans cet ordre)

### Solution 1 : Désactiver le cache dans DevTools (RECOMMANDÉ)
1. Ouvrez les DevTools (F12)
2. Allez dans l'onglet **Network**
3. Cochez **"Disable cache"** (en haut)
4. Gardez les DevTools ouverts
5. Rechargez la page (F5 ou Ctrl+R)

### Solution 2 : Mode Navigation Privée
1. Ouvrez une fenêtre de navigation privée (Ctrl+Shift+N)
2. Allez sur `mapevent.world`
3. Ouvrez la console (F12)
4. Vérifiez que les scripts chargés sont `v=20260111-120000`

### Solution 3 : Vider le cache Service Worker
1. Ouvrez les DevTools (F12)
2. Allez dans l'onglet **Application**
3. Dans le menu de gauche, cliquez sur **Service Workers**
4. Si un service worker est enregistré, cliquez sur **Unregister**
5. Rechargez la page

### Solution 4 : Vider complètement le cache
1. Appuyez sur **Ctrl+Shift+Delete**
2. Sélectionnez **"Tout le temps"** comme période
3. Cochez **"Images et fichiers en cache"**
4. Cliquez sur **"Effacer les données"**
5. Fermez **TOUS** les onglets du navigateur
6. Rouvrez le navigateur
7. Allez sur `mapevent.world`

### Solution 5 : Hard Refresh
1. Ouvrez la page
2. Appuyez sur **Ctrl+Shift+R** (ou **Ctrl+F5**)
3. Si ça ne marche pas, maintenez **Shift** et cliquez sur le bouton de rechargement

## Vérification
Après avoir appliqué une solution, vérifiez dans la console :
1. Ouvrez la console (F12)
2. Regardez les messages de chargement
3. Les messages `[AUTH] ✅ openAuthModal chargée depuis auth.js` doivent apparaître
4. Les messages `[AUTH] openAuthModal expose globalement` ne doivent **PAS** apparaître

## Si le problème persiste
Le serveur web pourrait avoir mis en cache les fichiers. Dans ce cas, contactez l'administrateur du serveur pour vider le cache du serveur/CDN.
