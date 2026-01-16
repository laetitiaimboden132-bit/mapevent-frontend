# 🔍 Guide de Diagnostic - Bloc Compte

## 📋 Problème
Le bloc compte affiche "om/ε Laetibibi" au lieu de "Laetibibi" ou de l'avatar/photo.

## 🚀 Utilisation

### Méthode 1 : Page HTML interactive (Recommandée)

1. **Ouvrir la page de diagnostic** :
   ```
   https://mapevent.world/diagnostic-account.html
   ```
   Ou ouvrir le fichier local :
   ```
   file:///chemin/vers/frontend/public/diagnostic-account.html
   ```

2. **Cliquer sur les boutons** pour :
   - ✅ Vérifier les données dans localStorage
   - ✅ Vérifier l'état du DOM
   - ✅ Nettoyer les données corrompues
   - ✅ Lancer un diagnostic complet

### Méthode 2 : Script dans la console du navigateur

1. **Ouvrir la console** (F12 > Console)

2. **Copier-coller le script** depuis `public/diagnostic-account-block.js`

3. **Le script s'exécute automatiquement** et affiche :
   - Les données dans localStorage
   - L'état actuel du DOM
   - Les fonctions disponibles
   - Les recommandations

## 🔧 Actions de nettoyage

### Nettoyage automatique via la page HTML

1. Ouvrir `diagnostic-account.html`
2. Cliquer sur **"Nettoyer localStorage"**
3. Cliquer sur **"Recharger la page"**

### Nettoyage manuel dans la console

```javascript
// Fonction de nettoyage manuel
function nettoyerDonneesUtilisateur() {
  try {
    const currentUserStr = localStorage.getItem('currentUser');
    if (currentUserStr) {
      const currentUser = JSON.parse(currentUserStr);
      
      // Fonction de nettoyage
      const clean = (text) => {
        if (!text || typeof text !== 'string') return text;
        let cleaned = text.replace(/^om\/[^\s]*\s*/gi, '');
        cleaned = cleaned.replace(/om\/[^\s]*/gi, '');
        cleaned = cleaned.replace(/[αβεγδεζηθικλμνξοπρστυφχψω]/gi, '');
        cleaned = cleaned.replace(/[^\w\s\u00C0-\u017F\u00E0-\u00FF]/g, '');
        cleaned = cleaned.replace(/\/+/g, '');
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        return cleaned;
      };
      
      // Nettoyer les champs textuels
      if (currentUser.username) currentUser.username = clean(currentUser.username);
      if (currentUser.name) currentUser.name = clean(currentUser.name);
      if (currentUser.firstName) currentUser.firstName = clean(currentUser.firstName);
      if (currentUser.lastName) currentUser.lastName = clean(currentUser.lastName);
      
      // Sauvegarder
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
      console.log('✅ Données nettoyées:', currentUser);
      
      // Recharger la page
      location.reload();
    }
  } catch (e) {
    console.error('❌ Erreur:', e);
  }
}

// Exécuter la fonction
nettoyerDonneesUtilisateur();
```

### Nettoyage complet (supprimer et se reconnecter)

Si le problème persiste, supprimez complètement les données :

```javascript
// Supprimer les données utilisateur
localStorage.removeItem('currentUser');
localStorage.removeItem('cognito_tokens');

// Recharger la page
location.reload();
```

Puis reconnectez-vous avec Google.

## 📊 Interprétation des résultats

### ✅ Tout est OK
- Aucun "om/" ou "ε" dans localStorage
- Le DOM affiche correctement le nom/avatar
- Les fonctions de nettoyage fonctionnent

### ⚠️ Problème détecté
- "om/" ou "ε" trouvé dans localStorage → **Nettoyer localStorage**
- "om/" ou "ε" trouvé dans le DOM → **Recharger la page après nettoyage**
- Les fonctions de nettoyage ne fonctionnent pas → **Vérifier le code**

## 🔍 Vérifications supplémentaires

### Vérifier le backend

Les données peuvent aussi venir du backend. Vérifiez que la fonction `clean_user_text()` dans `lambda-package/backend/main.py` nettoie correctement les données avant de les sauvegarder.

### Vérifier les logs CloudWatch

1. Aller dans **CloudWatch** > **Logs** > **Log groups** > `/aws/lambda/mapevent-backend`
2. Chercher les logs récents de connexion Google OAuth
3. Vérifier si les données retournées contiennent "om/ε"

## 🆘 Si le problème persiste

1. **Vérifier que le code est à jour** :
   - Le fichier `map_logic.js` contient les fonctions `cleanAccountText`, `getUserAvatar`, `getUserDisplayName`
   - Le MutationObserver est actif

2. **Vérifier le CSS** :
   - Le fichier `mapevent.html` contient les styles pour `#account-topbar-btn`

3. **Vider complètement le cache** :
   - Ctrl+Shift+Delete (Chrome/Firefox)
   - Vider le cache et les cookies
   - Recharger la page

4. **Tester dans un navigateur privé** :
   - Ouvrir une fenêtre privée
   - Se connecter avec Google
   - Vérifier si le problème persiste

## 📝 Notes

- Le script de diagnostic ne modifie rien automatiquement
- Toutes les actions de nettoyage nécessitent une confirmation
- Après nettoyage, vous devrez vous reconnecter
- Les données sont sauvegardées sur le serveur, donc la reconnexion restaurera les données propres




