# 🚨 Système de Signalements - Documentation

## 📋 Vue d'ensemble

Le système de signalements permet aux utilisateurs de signaler **n'importe quelle action** sur la plateforme :
- Événements, Bookings, Services
- Messages dans les discussions
- Avis/Commentaires
- Utilisateurs
- Tout autre contenu

## 🎯 Fonctionnalités

### Types de signalements supportés

1. **Contenu inapproprié** - Contenu qui ne respecte pas les règles de la communauté
2. **Information fausse / Arnaque** - Fausses informations ou tentatives d'arnaque
3. **Image offensante / Contenu -16 ans** - Contenu inapproprié pour les mineurs
4. **Spam / Publicité** - Contenu publicitaire non autorisé
5. **Harcèlement / Intimidation** - Comportement abusif
6. **Autre** - Autre raison avec détails

### Structure des signalements

Chaque signalement contient :
- **Type d'élément** : `event`, `booking`, `service`, `message`, `discussion`, `review`, `user`, etc.
- **ID de l'élément** : Identifiant unique
- **Type parent** (optionnel) : Si c'est un message dans une discussion
- **ID parent** (optionnel) : ID du parent
- **Raison** : Une des raisons listées ci-dessus
- **Détails** : Description détaillée (optionnel)

## 🔧 Implémentation

### Frontend

**Fonction principale :**
```javascript
openReportModal(type, id, parentType = null, parentId = null)
```

**Exemples d'utilisation :**
```javascript
// Signaler un événement
openReportModal('event', 123);

// Signaler un message dans une discussion
openReportModal('message', 'msg_456', 'discussion', 'disc_789');

// Signaler un avis
openReportModal('review', 789);
```

**Soumission :**
```javascript
submitReport(type, id, parentType, parentId)
```
- Vérifie que l'utilisateur est connecté
- Envoie le signalement au backend
- Fallback sur localStorage si le backend échoue

### Backend

**Endpoint :**
```
POST /api/user/reports
```

**Body :**
```json
{
  "userId": "user_123",
  "itemType": "event",
  "itemId": "123",
  "parentType": null,
  "parentId": null,
  "reason": "inappropriate",
  "details": "Description détaillée..."
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Report submitted successfully"
}
```

### Base de données

**Table :** `user_reports`

**Champs :**
- `id` : ID unique
- `user_id` : Utilisateur qui signale
- `item_type` : Type d'élément signalé
- `item_id` : ID de l'élément (VARCHAR pour flexibilité)
- `parent_type` : Type parent (optionnel)
- `parent_id` : ID parent (optionnel)
- `reason` : Raison du signalement
- `details` : Détails supplémentaires
- `status` : `pending`, `reviewed`, `resolved`, `dismissed`
- `created_at` : Date de création
- `reviewed_at` : Date de révision (optionnel)

## 📍 Où ajouter des boutons de signalement

### Popups principales
- ✅ Événements (`buildEventPopup`)
- ✅ Bookings (`buildBookingPopup`)
- ✅ Services (`buildServicePopup`)

### À ajouter
- ⏳ Messages dans les discussions
- ⏳ Avis/Commentaires
- ⏳ Profils utilisateurs
- ⏳ Toute autre action interactive

### Exemple d'ajout dans une discussion

```javascript
// Dans openDiscussionModal ou buildMessage
<button onclick="openReportModal('message', messageId, 'discussion', discussionId)" 
        style="...">
  🚨 Signaler
</button>
```

## 🔄 Workflow de modération

1. **Signalement** → Utilisateur signale un contenu
2. **Enregistrement** → Sauvegardé en base avec status `pending`
3. **Révision** → Équipe de modération examine
4. **Décision** → Status changé en `reviewed`, `resolved`, ou `dismissed`

## 📊 Statistiques

Les signalements peuvent être récupérés via :
```
GET /api/user/reports?userId=X
```

Utile pour :
- Dashboard de modération
- Historique des signalements d'un utilisateur
- Statistiques de modération

## ⚠️ Notes importantes

1. **Tout peut être signalé** : Le système est conçu pour être flexible
2. **Pas de limite** : Les utilisateurs peuvent signaler autant de fois que nécessaire
3. **Anonymat** : Les signalements sont liés à l'utilisateur mais peuvent être anonymisés pour la modération
4. **Double signalement** : Un même utilisateur peut signaler plusieurs fois le même contenu (utile si le problème persiste)



