# 📋 Fonctionnalités Complètes de MapEventAI

## 🎯 Résumé des Fonctionnalités Principales

### 1. 💬 **CANAL DE DISCUSSION** (`openDiscussionModal`)

**Localisation** : Ligne ~10293 dans `map_logic.js`

**Fonctionnalités** :
- **Style Facebook** : Interface similaire à Facebook avec posts, commentaires et réponses
- **Posts** : Les utilisateurs peuvent créer des posts dans la discussion d'un événement/booking/service
- **Commentaires** : Système de commentaires avec réponses imbriquées (niveaux multiples)
- **Likes** : Bouton "J'aime" pour chaque post et commentaire
- **Affichage progressif** : 
  - Affiche 3 réponses par défaut
  - Affiche 2 réponses imbriquées par défaut
  - Bouton "Voir X réponses supplémentaires" pour afficher le reste
- **Stockage** : Les posts sont stockés dans `localStorage` avec la clé `discussion_{type}_{id}`
- **Fonctions principales** :
  - `submitDiscussionComment(type, id)` : Publier un nouveau post
  - `submitReply(type, id, postId, replyPath)` : Répondre à un post ou commentaire
  - `togglePostLike(type, id, postId)` : Liker/unliker un post
  - `toggleReplyLike(type, id, postId, replyPath)` : Liker/unliker une réponse
  - `showReplyForm(postId, replyPath)` : Afficher/masquer le formulaire de réponse
  - `showAllReplies(postId, parentPath)` : Afficher toutes les réponses
  - `showAllNestedReplies(postId, parentPath)` : Afficher toutes les réponses imbriquées
- **Navigation** : Bouton retour pour revenir à la popup de l'événement
- **Interface** : Zone de texte en bas pour créer des posts, avec bouton "Publier"

**Boutons dans les popups** :
- Event : Bouton "💬 Discussion" (ligne ~3109)
- Booking : Bouton "💬 Contact" via `onAction('discussion', ...)` (ligne ~3369)
- Service : Bouton "💬 Contact" via `onAction('discussion', ...)` (ligne ~3486)

---

### 2. ➕ **INVITER DES PARTICIPANTS** (`inviteFriendsToEvent`)

**Localisation** : Ligne ~7295 dans `map_logic.js`

**Fonctionnalités** :
- **Modal d'invitation** : Affiche une liste de tous les amis de l'utilisateur
- **Recherche** : Barre de recherche pour filtrer les amis (`filterInviteFriends`)
- **Affichage** : 
  - Avatar de chaque ami
  - Nom de l'ami
  - Statut en ligne/hors ligne
  - Bouton "Inviter" pour chaque ami
- **Envoi d'invitation** : `sendInvitationToFriend(friendId, friendName, friendAvatar, type, id)`
  - Crée une alerte sociale pour l'ami invité
  - Stocke dans `window.userAlerts[friendId]`
  - Type d'alerte : `event_invitation`
- **Stockage des paramètres** : Le type et l'ID sont stockés dans `window.currentInviteType` et `window.currentInviteId` pour la recherche

**Boutons dans les popups** :
- Event : Bouton "➕ Inviter" (ligne ~3115)
- Booking : Bouton "➕ Inviter" (ligne ~3358)
- Service : Bouton "➕ Inviter" (ligne ~3475)

---

### 3. 👥 **VOIR LES PARTICIPANTS** (`viewEventAttendees`)

**Localisation** : Ligne ~14051 dans `map_logic.js`

**Fonctionnalités** :
- **Stub actuel** : Fonction non implémentée (affiche juste un message "Fonctionnalité en cours de développement")
- **Bouton dans popup Event** : Bouton "👥 Participants" (ligne ~3112)
- **À implémenter** : Doit afficher la liste des utilisateurs qui participent à l'événement

---

### 4. 👥 **SYSTÈME D'AMIS** (`openFriendsModal`)

**Localisation** : Ligne ~12793 dans `map_logic.js`

**Fonctionnalités complètes** :

#### 4.1 Modal des Amis
- **Demandes en attente** : Affiche les demandes d'amis reçues
  - Bouton ✓ pour accepter (`acceptFriendRequest`)
  - Bouton ✗ pour refuser (`declineFriendRequest`)
- **Recherche d'utilisateurs** : Barre de recherche (`searchUsers`)
  - Recherche par nom d'utilisateur
  - Affiche jusqu'à 5 résultats
  - Bouton "+ Ajouter" pour envoyer une demande
- **Liste des amis** :
  - Avatar avec indicateur en ligne/hors ligne
  - Nom et description de l'avatar
  - Bouton "💬 Chat" (`openChatWith`)
  - Bouton "🗑️" pour retirer l'ami (`removeFriend`)

#### 4.2 Fonctions associées
- `searchUsers(query)` : Recherche d'utilisateurs (ligne ~12967)
- `sendFriendRequest(userId, userName, userAvatar)` : Envoyer une demande (ligne ~13002)
- `acceptFriendRequest(fromUserId)` : Accepter une demande (ligne ~13038)
- `declineFriendRequest(fromUserId)` : Refuser une demande (ligne ~13058)
- `removeFriend(friendId)` : Retirer un ami (ligne ~13069)
- `openChatWith(friendId)` : Ouvrir le chat (à implémenter)

#### 4.3 Données utilisateurs
- `initDemoUsers()` : Initialise 15 utilisateurs de démo (ligne ~12769)
- Stockage dans `allUsers[]`
- Chaque utilisateur a : id, name, avatar, avatarId, avatarDescription, isOnline, lastSeen

**Accès** : Depuis le menu "Compte" → "Amis"

---

### 5. 👥 **SYSTÈME DE GROUPES** (`openGroupsModal`)

**Localisation** : Ligne ~12879 dans `map_logic.js`

**Fonctionnalités** :

#### 5.1 Canaux par Pays
- Section "🌍 Par Pays" avec le pays enregistré de l'utilisateur
- Fonction `changeGroupCountry()` pour changer de pays

#### 5.2 Canaux par Catégorie
- **Events** : Canal de discussion pour les événements
- **Booking** : Canal de discussion pour les bookings
- **Services** : Canal de discussion pour les services
- Fonction `openGroupChannel(type, channelId)` pour ouvrir un canal

#### 5.3 Groupes Personnalisés
- Liste des groupes créés par l'utilisateur
- Chaque groupe affiche : emoji, nom, nombre de membres
- Fonction `createGroup()` pour créer un nouveau groupe

**Fonctions associées** :
- `openGroupChannel(type, channelId)` : Ouvrir un canal de groupe
- `createGroup()` : Créer un nouveau groupe
- `changeGroupCountry()` : Changer le pays pour les canaux
- `sendGroupMessage()` : Envoyer un message dans un groupe (stub)

**Accès** : Depuis le menu "Compte" → "Groupes"

---

### 6. 📝 **FORMULAIRE DE PUBLICATION** (`buildPublishFormHtml` / `openPublishModal`)

**Localisation** : Ligne ~5949 dans `map_logic.js`

**Fonctionnalités complètes** :

#### 6.1 Champs du Formulaire
- **Titre/Nom** * (obligatoire)
- **Catégorie principale** * (obligatoire)
- **Dates** (uniquement pour Events) :
  - Date de début *
  - Date de fin *
- **Adresse complète** * (obligatoire)
- **Téléphone** (optionnel)
- **Email** * (obligatoire)
- **Description complète** * (obligatoire)
- **Photo principale** * (obligatoire, type file)
- **Billetterie** (uniquement Events) : Lien vers les billets
- **Liens sociaux** : Facebook, Instagram, etc.
- **Liens vidéo** : YouTube, Vimeo, etc.
- **Liens audio** (uniquement Booking) : SoundCloud, etc.
- **Niveau** (uniquement Booking) : Niveau de l'artiste
- **Estimation de prix** (uniquement Booking) : Prix estimé

#### 6.2 Options de Visibilité
- **Point standard** : Publication gratuite
- **Bronze Boost** : Boost de visibilité
- **Silver Boost** : Boost supérieur
- **Platinum Boost** : Boost maximum

#### 6.3 Recommandation d'Abonnement
- Bloc avec informations sur les abonnements
- Bouton "Voir abonnements" (`openSubscriptionModal`)
- Prix affichés selon le mode (Event vs Booking/Service)

#### 6.4 Soumission
- Fonction `onSubmitPublishForm(e)` (ligne ~6145)
- Vérifie que l'utilisateur est connecté
- Récupère toutes les données du formulaire
- Envoie au backend via API
- Affiche notification de succès/erreur

**Accès** : Bouton "Publier" dans la topbar

---

### 7. 🔍 **FILTRE EXPLORATEUR** (`toggleExplorer`)

**Localisation** : Ligne ~4968 dans `map_logic.js`

**Fonctionnalités** :
- **Panel de filtres** : Panneau latéral avec filtres avancés
- **Filtres par catégorie** : Sélection multiple de catégories
- **Filtres par date** :
  - Filtre par date exacte
  - Filtre par plage de dates (dateRangeStart, dateRangeEnd)
  - Affichage de la plage sélectionnée
- **Filtres par ville** : Recherche et sélection de ville
- **Application des filtres** : `applyExplorerFilter()` met à jour les marqueurs et la liste
- **État** : Variable `explorerOpen` pour gérer l'ouverture/fermeture

**Fonctions associées** :
- `toggleExplorer()` : Ouvrir/fermer le panneau
- `applyExplorerFilter()` : Appliquer les filtres
- `setupDateRangePicker()` : Configurer le sélecteur de dates
- `updateDateRangeDisplay()` : Mettre à jour l'affichage de la plage
- `renderSelectedTags()` : Afficher les catégories sélectionnées
- `removeSelectedCategory(cat)` : Retirer une catégorie

**Accès** : Bouton "Filtre" dans la topbar

---

### 8. 📊 **AUTRES FONCTIONNALITÉS IMPORTANTES**

#### 8.1 Système de Reviews/Avis
- `openReviewModal(type, id)` : Ouvrir la modal des avis
- `submitReview(type, id)` : Soumettre un avis avec note (1-5 étoiles)
- `submitReply(reviewId, type, id)` : Répondre à un avis
- Stockage dans `localStorage` avec clé `reviews_{type}_{id}`

#### 8.2 Système de Participation
- `toggleParticipation(type, id)` : Participer/se désinscrire d'un événement
- Met à jour le compteur de participants
- Stockage dans `currentUser.participating[]`

#### 8.3 Système de Favoris
- `toggleFavorite(type, id)` : Ajouter/retirer des favoris
- Stockage dans `currentUser.favorites[]`

#### 8.4 Système d'Agenda
- `onAction('agenda', type, id)` : Ajouter/retirer de l'agenda
- Stockage dans `currentUser.agenda[]`
- Limites selon l'abonnement

#### 8.5 Partage
- `sharePopup(type, id)` : Partager un événement/booking/service
- Partage vers groupes, amis, ou réseaux sociaux

---

## 🔗 **LIENS ENTRE FONCTIONNALITÉS**

### Dans les Popups d'Événements :
1. **💬 Discussion** → `openDiscussionModal('event', id)`
2. **👥 Participants** → `viewEventAttendees('event', id)` (stub)
3. **➕ Inviter** → `inviteFriendsToEvent('event', id)`

### Dans le Menu Compte :
1. **👥 Amis** → `openFriendsModal()`
2. **👥 Groupes** → `openGroupsModal()`
3. **📝 Publier** → `openPublishModal()`

### Dans le Filtre Explorateur :
- Filtres par catégorie, date, ville
- Application automatique sur la carte et la liste

---

## ⚠️ **FONCTIONS À IMPLÉMENTER (STUBS)**

1. `viewEventAttendees(type, id)` : Afficher la liste des participants
2. `openChatWith(friendId)` : Ouvrir le chat avec un ami
3. `openGroupChannel(type, channelId)` : Ouvrir un canal de groupe
4. `createGroup()` : Créer un nouveau groupe
5. `sendGroupMessage()` : Envoyer un message dans un groupe

---

## 📦 **STOCKAGE DES DONNÉES**

### localStorage :
- `discussion_{type}_{id}` : Posts de discussion
- `reviews_{type}_{id}` : Avis et reviews
- `currentUser` : Données utilisateur
- `cognito_tokens` : Tokens d'authentification Cognito

### sessionStorage :
- `showAllReplies_{type}_{id}_{postId}_{parentPath}` : État d'affichage des réponses
- `showAllNestedReplies_{type}_{id}_{postId}_{replyPath}` : État d'affichage des réponses imbriquées
- `pkce_verifier` : PKCE verifier pour OAuth
- `oauth_state` : State OAuth pour sécurité

---

## 🎨 **INTERFACE UTILISATEUR**

### Style Facebook pour Discussion :
- Fond sombre (#18191a, #242526)
- Avatars avec dégradés
- Bulles de texte arrondies
- Boutons "J'aime" et "Commenter"
- Formulaire de réponse en bas

### Style Moderne pour Autres Modals :
- Fond sombre avec transparence
- Dégradés de couleurs (cyan, bleu, violet)
- Bordures arrondies
- Animations au survol

---

## ✅ **RÉSUMÉ DES BOUTONS DANS LES POPUPS**

### Popup Event :
- 💬 Discussion → `openDiscussionModal('event', id)`
- 👥 Participants → `viewEventAttendees('event', id)`
- ➕ Inviter → `inviteFriendsToEvent('event', id)`
- 🎟️ Participer → `toggleParticipation('event', id)`
- 📅 Agenda → `onAction('agenda', 'event', id)`
- ⭐ Avis → `openReviewModal('event', id)`
- 🗺️ Y aller → `onAction('route', 'event', id)`

### Popup Booking :
- 💬 Contact → `onAction('discussion', 'booking', id)`
- ➕ Inviter → `inviteFriendsToEvent('booking', id)`
- ⭐ Avis → `onAction('avis', 'booking', id)`

### Popup Service :
- 💬 Contact → `onAction('discussion', 'service', id)`
- ➕ Inviter → `inviteFriendsToEvent('service', id)`
- ⭐ Avis → `onAction('avis', 'service', id)`

---

**Document créé le** : 2024-12-31
**Version du code analysé** : map_logic.js (lignes 1-17642)




