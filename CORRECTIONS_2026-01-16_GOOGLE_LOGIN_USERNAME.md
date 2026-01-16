# Corrections Google Login - Username et Photo du Formulaire

**Date :** 2026-01-16  
**Statut :** ✅ RÉSOLU

## Problème

Lors de la connexion Google, le username et la photo du formulaire d'inscription n'étaient pas correctement récupérés et affichés. Le système utilisait le username par défaut (partie email) au lieu du username saisi dans le formulaire.

## Corrections Apportées

### 1. Récupération du username depuis localStorage (`map_logic.js`)

**Fichier :** `public/map_logic.js`  
**Lignes :** ~804-850

**Modification :** Ajout de la récupération du username depuis `localStorage.getItem('pendingRegisterDataForGoogle')` AVANT la création du `slimUser` pour les comptes existants.

```javascript
// ⚠️⚠️⚠️ CRITIQUE : Récupérer le username depuis localStorage AVANT de créer slimUser
let savedUsernameFromForm = null;
let savedPhotoDataFromForm = null;
try {
  const savedFromStorage = localStorage.getItem('pendingRegisterDataForGoogle');
  if (savedFromStorage) {
    const savedPendingData = JSON.parse(savedFromStorage);
    savedUsernameFromForm = savedPendingData?.username || null;
    savedPhotoDataFromForm = savedPendingData?.photoData || null;
    console.log('[OAUTH] ✅✅✅ Données récupérées depuis localStorage:', {
      username: savedUsernameFromForm || 'MANQUANT',
      hasPhotoData: !!savedPhotoDataFromForm
    });
  }
} catch (e) {
  console.error('[OAUTH] ❌ Erreur récupération depuis localStorage:', e);
}

// ⚠️⚠️⚠️ VALIDATION STRICTE : Utiliser le username du formulaire s'il est valide
let finalUsername = savedUsernameFromForm || syncData.user.username || currentUser.email?.split('@')[0]?.substring(0, 20) || 'Utilisateur';
if (savedUsernameFromForm && savedUsernameFromForm !== 'null' && savedUsernameFromForm !== '' && !savedUsernameFromForm.includes('@')) {
  finalUsername = savedUsernameFromForm;
  console.log('[OAUTH] ✅✅✅✅✅ Username du FORMULAIRE utilisé:', finalUsername);
} else if (syncData.user.username && syncData.user.username !== 'null' && syncData.user.username !== '' && !syncData.user.username.includes('@')) {
  finalUsername = syncData.user.username;
  console.log('[OAUTH] ⚠️ Username du backend utilisé (formulaire invalide):', finalUsername);
} else {
  finalUsername = currentUser.email?.split('@')[0]?.substring(0, 20) || 'Utilisateur';
  console.log('[OAUTH] ❌ Aucun username valide, utilisation email part:', finalUsername);
}
```

### 2. Forçage du username dans currentUser (`map_logic.js`)

**Fichier :** `public/map_logic.js`  
**Lignes :** ~840-850

**Modification :** Forçage explicite du username et photoData dans `currentUser` AVANT l'appel à `updateAuthUI` pour éviter l'écrasement.

```javascript
// ⚠️⚠️⚠️ CRITIQUE : Forcer le username et photoData dans currentUser AVANT updateAuthUI
currentUser = { ...currentUser, ...slimUser, isLoggedIn: true };
if (finalUsername && finalUsername !== 'Utilisateur' && !finalUsername.includes('@')) {
  currentUser.username = finalUsername;
  console.log('[OAUTH] ✅✅✅✅✅ Username FORCÉ dans currentUser:', finalUsername);
}
if (savedPhotoDataFromForm && savedPhotoDataFromForm !== 'null' && savedPhotoDataFromForm !== '') {
  currentUser.photoData = savedPhotoDataFromForm;
  console.log('[OAUTH] ✅✅✅✅✅ photoData FORCÉ dans currentUser');
}
updateAuthUI(slimUser);
```

### 3. Validation stricte du username (`auth.js`)

**Fichier :** `public/auth.js`  
**Lignes :** ~2711-2727

**Modification :** Validation stricte pour utiliser le username du formulaire uniquement s'il est valide (pas un email, pas "null", etc.).

```javascript
// ⚠️⚠️⚠️ VALIDATION STRICTE : Si le username du formulaire existe et est valide, l'utiliser
if (savedUsernameFromForm && savedUsernameFromForm !== 'null' && savedUsernameFromForm !== '' && !savedUsernameFromForm.includes('@')) {
  finalUsername = savedUsernameFromForm;
  console.log('[OAUTH] ✅✅✅✅✅ Username du FORMULAIRE VALIDÉ et utilisé:', finalUsername);
} else if (syncData.user.username && syncData.user.username !== 'null' && syncData.user.username !== '' && !syncData.user.username.includes('@')) {
  // Si le username du backend est valide, l'utiliser
  finalUsername = syncData.user.username;
  console.log('[OAUTH] ⚠️ Username du backend utilisé (formulaire invalide):', finalUsername);
} else {
  // Si les deux sont invalides, utiliser "Utilisateur"
  finalUsername = 'Utilisateur';
  console.log('[OAUTH] ❌ Aucun username valide, utilisation "Utilisateur"');
}
```

### 4. Protection du formulaire de modification (`map_logic.js`)

**Fichier :** `public/map_logic.js`  
**Lignes :** ~21447-21460

**Modification :** Ajout d'un délai pour empêcher la fermeture prématurée du modal pendant l'injection du HTML.

```javascript
console.log('[EDIT PROFILE] ✅ Formulaire de modification affiché');

// ⚠️⚠️⚠️ CRITIQUE : Empêcher la fermeture du modal pendant l'injection
// Attendre un peu pour que le HTML soit complètement injecté
setTimeout(() => {
  // Réattacher les event listeners après l'injection
  const closeBtn = modal.querySelector('.modal-close-btn, [onclick*="closePublishModal"]');
  if (closeBtn) {
    closeBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      closePublishModal(e);
    });
  }
}, 100);
```

## Flux de Données

1. **Inscription** : L'utilisateur remplit le formulaire avec username et photo
2. **Sauvegarde localStorage** : Les données sont sauvegardées dans `localStorage.setItem('pendingRegisterDataForGoogle', ...)` avant la redirection Google
3. **Redirection Google** : L'utilisateur est redirigé vers Google pour OAuth
4. **Callback** : Après retour de Google, `handleCognitoCallbackIfPresent` est appelé
5. **Récupération** : Le code récupère `pendingRegisterDataForGoogle` depuis localStorage
6. **Validation** : Le username est validé (pas email, pas "null", etc.)
7. **Création slimUser** : Le `slimUser` est créé avec le username du formulaire
8. **Forçage currentUser** : Le username est forcé dans `currentUser` avant `updateAuthUI`
9. **Affichage** : L'UI affiche le username et la photo du formulaire

## Logs de Débogage

Les logs suivants permettent de vérifier le bon fonctionnement :

- `[OAUTH] ✅✅✅ Données récupérées depuis localStorage:` - Confirme la récupération
- `[OAUTH] ✅✅✅✅✅ Username du FORMULAIRE utilisé:` - Confirme l'utilisation du username du formulaire
- `[OAUTH] ✅✅✅✅✅ Username FORCÉ dans currentUser:` - Confirme le forçage dans currentUser
- `[OAUTH] ✅✅✅✅✅ photoData FORCÉ dans currentUser` - Confirme le forçage de la photo

## Tests

✅ Connexion Google avec username du formulaire  
✅ Affichage correct du username et de la photo  
✅ Formulaire de modification s'ouvre correctement  
✅ Pas de fermeture prématurée du modal

## Notes

- Le username est sauvegardé dans localStorage AVANT la redirection Google
- Le username est récupéré depuis localStorage APRÈS le retour de Google
- Le username est validé pour éviter les valeurs invalides (email, "null", etc.)
- Le username est forcé dans `currentUser` pour éviter l'écrasement par `updateAuthUI`
- La photo est également récupérée et forcée de la même manière

## Fichiers Modifiés

- `public/auth.js` - Validation stricte du username
- `public/map_logic.js` - Récupération et forçage du username et photoData
