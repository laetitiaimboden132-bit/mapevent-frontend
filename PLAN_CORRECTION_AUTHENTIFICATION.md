# Plan de Correction - Authentification et Gestion de Profil MapEvent

## Objectif
Créer un système d'authentification et de gestion de profil professionnel, fiable et sans erreurs, comme un site leader top 1.

## Problèmes à Corriger

### 1. Problème de Sérialisation Backend `"[dict - 17 items]"`
**Symptôme** : Le backend renvoie parfois `"[dict - 17 items]"` au lieu d'un objet JSON valide.
**Cause** : Flask test client transforme les objets complexes en chaînes.
**Solution** : 
- Utiliser `make_response` avec `json.dumps` dans le backend
- Le handler Lambda récupère déjà les données depuis la DB si nécessaire
- Vérifier que la sérialisation est toujours correcte

### 2. Formulaire d'Inscription qui Réapparaît
**Symptôme** : Le formulaire d'inscription s'affiche même après avoir créé un compte.
**Cause** : `backendUser` est vide ou `profileComplete` n'est pas correctement détecté.
**Solution** :
- Vérifier `isBackendUserEmpty` AVANT toute autre vérification
- Si `backendUser` est vide, forcer l'affichage du formulaire
- Si `profileComplete === true` ET `backendUser` contient les données, connexion directe

### 3. Données Utilisateur Non Sauvegardées
**Symptôme** : Les données utilisateur (username, photo, adresse) ne sont pas sauvegardées.
**Cause** : Problème de sérialisation ou de sauvegarde dans la base de données.
**Solution** :
- Vérifier que `oauth_google_complete` sauvegarde correctement toutes les données
- S'assurer que les données sont bien récupérées depuis la DB lors de la reconnexion

### 4. Reconnexion Sans Formulaire
**Symptôme** : Le formulaire s'affiche à chaque reconnexion au lieu de se connecter directement.
**Cause** : `profileComplete` n'est pas correctement détecté ou `backendUser` est vide.
**Solution** :
- Vérifier `isBackendUserEmpty` en premier
- Si `profileComplete === true` ET `backendUser` contient les données, connexion directe
- Sinon, afficher le formulaire

### 5. Bouton "Modifier Profil" Non Fonctionnel
**Symptôme** : Le bouton "Modifier profil" ne fonctionne pas.
**Cause** : Fonction non exposée ou erreur dans le code.
**Solution** :
- Exposer `openEditProfileModal` globalement
- S'assurer que le formulaire s'affiche avec les données pré-remplies
- Permettre la modification et la sauvegarde

### 6. Déconnexion Non Complète
**Symptôme** : Le bouton "Compte" garde le nom/photo après déconnexion.
**Cause** : `currentUser` n'est pas complètement réinitialisé.
**Solution** :
- Réinitialiser `currentUser` complètement
- Supprimer les tokens Cognito
- Réinitialiser le bouton "Compte"

### 7. Fenêtre de Connexion - Champ Email Visible
**Symptôme** : Le champ email s'affiche directement au lieu des options Google/Facebook.
**Cause** : Structure HTML de la modal de connexion.
**Solution** :
- Afficher d'abord les options Google, Facebook, Mail
- Masquer le champ email par défaut
- Afficher le champ email seulement si l'utilisateur choisit "Mail"

## Corrections à Appliquer

### Backend (`lambda-package/backend/main.py`)
1. ✅ S'assurer que `oauth_google` renvoie toujours un objet JSON valide
2. ✅ Utiliser `make_response` avec `json.dumps` pour garantir la sérialisation
3. ✅ Vérifier que toutes les données utilisateur sont sauvegardées dans `oauth_google_complete`

### Handler Lambda (`lambda-package/handler.py`)
1. ✅ Vérifier que la récupération depuis la DB fonctionne correctement
2. ✅ Ajouter plus de logs pour le débogage

### Frontend (`public/map_logic.js`)
1. ✅ Vérifier `isBackendUserEmpty` AVANT toute autre vérification
2. ✅ Si `backendUser` est vide, forcer l'affichage du formulaire
3. ✅ Si `profileComplete === true` ET `backendUser` contient les données, connexion directe
4. ✅ Exposer `openEditProfileModal` globalement
5. ✅ Réinitialiser complètement `currentUser` lors de la déconnexion
6. ✅ Corriger la fenêtre de connexion pour afficher d'abord les options Google/Facebook

## Tests à Effectuer

1. **Première Connexion** :
   - Clic sur "Compte" → Fenêtre de connexion s'ouvre (Google, Facebook, Mail)
   - Clic sur Google → Formulaire d'inscription s'ouvre
   - Remplir le formulaire → Données sauvegardées
   - Nom et photo apparaissent dans le bloc compte

2. **Déconnexion** :
   - Clic sur "Déconnexion" → Bouton "Compte" redevient normal (sans nom/photo)

3. **Reconnexion** :
   - Clic sur "Compte" → Fenêtre de connexion s'ouvre
   - Clic sur Google → Connexion directe (PAS de formulaire)
   - Nom et photo apparaissent automatiquement

4. **Modification du Profil** :
   - Clic sur "Modifier profil" → Formulaire s'ouvre avec données pré-remplies
   - Modifier les données → Sauvegarder
   - Données mises à jour

## Notes Importantes

- Les données utilisateur (username, photo, adresse) sont **CRUCIALES** et ne doivent **JAMAIS** être perdues
- Le système doit fonctionner comme un site leader top 1, sans erreurs
- GitHub Desktop peut être utilisé pour versionner les modifications







