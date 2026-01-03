# 📋 Fonctionnalités par Mode - État Actuel

## ✅ ÉVÉNEMENTS (Events)

### Actions disponibles
- ✅ **Like** - `onAction('like', 'event', id)`
- ✅ **Participate** - `onAction('participate', 'event', id)` - Inscription à l'événement
- ✅ **Agenda** - `onAction('agenda', 'event', id)` - Ajouter à l'agenda
- ✅ **Route** - `onAction('route', 'event', id)` - Itinéraire vers l'événement
- ✅ **Share** - `onAction('share', 'event', id)` - Partager
- ✅ **Review** - `onAction('avis', 'event', id)` - Laisser un avis
- ✅ **Discussion** - `onAction('discussion', 'event', id)` - Contact/Discussion
- ✅ **Report** - `onAction('report', 'event', id)` - Signaler

### Statistiques affichées
- ✅ Likes count
- ✅ Comments count
- ✅ Participants count

### Spécificités
- ✅ Support des dates (startDate, endDate)
- ✅ Support du statut (OK, COMPLET, REPORTÉ, etc.)
- ✅ Support des boost levels (1.-, bronze, silver, gold, platinum)
- ✅ Support des images de catégories
- ✅ Support des overlays de statut

---

## ⚠️ BOOKINGS

### Actions disponibles
- ✅ **Like** - `onAction('like', 'booking', id)` (utilisé comme "Favoris")
- ❌ **Participate** - Non applicable (pas d'inscription pour un booking)
- ❌ **Agenda** - **MANQUE** - Pourrait être utile pour se rappeler d'un artiste
- ❌ **Route** - **MANQUE** - Utile pour se rendre chez l'artiste
- ✅ **Share** - `onAction('share', 'booking', id)`
- ✅ **Review** - `onAction('avis', 'booking', id)`
- ✅ **Discussion** - `onAction('discussion', 'booking', id)`
- ✅ **Report** - `onAction('report', 'booking', id)`
- ✅ **Achat Contact** - `onBuyContact('booking', id)` - Débloquer contact + sons

### Statistiques affichées
- ✅ Rating (étoiles)
- ✅ Likes count (comme "avis")

### Spécificités
- ✅ Support des soundLinks (pistes audio)
- ✅ Support du niveau (Débutant, Semi-pro, Pro, etc.)
- ✅ Support des boost levels
- ✅ Support des images de catégories
- ✅ Support AI indicator

---

## ⚠️ SERVICES

### Actions disponibles
- ✅ **Like** - `onAction('like', 'service', id)` (utilisé comme "Favoris")
- ❌ **Participate** - Non applicable
- ❌ **Agenda** - **MANQUE** - Pourrait être utile pour se rappeler d'un service
- ❌ **Route** - **MANQUE** - Utile pour se rendre chez le prestataire
- ✅ **Share** - `onAction('share', 'service', id)`
- ✅ **Review** - `onAction('avis', 'service', id)`
- ✅ **Discussion** - `onAction('discussion', 'service', id)`
- ✅ **Report** - `onAction('report', 'service', id)`
- ✅ **Achat Contact** - `onBuyContact('service', id)` - Débloquer contact

### Statistiques affichées
- ✅ Rating (étoiles)
- ✅ Likes count (comme "avis")

### Spécificités
- ✅ Support des boost levels
- ✅ Support des images de catégories
- ✅ Support AI indicator

---

## 🔍 Problèmes identifiés

### 1. Confusion Like vs Favoris
- **Problème** : Les boutons "Favoris" dans bookings/services utilisent `toggleLike()` au lieu de `toggleFavorite()`
- **Impact** : Les favoris ne sont pas séparés des likes
- **Solution** : Créer `toggleFavorite()` ou clarifier que "Favoris" = "Like"

### 2. Actions manquantes pour Bookings/Services
- **Agenda** : Pourrait être utile pour se rappeler d'un artiste/service
- **Route** : Utile pour se rendre chez l'artiste/prestataire

### 3. Système de favoris
- **Problème** : `currentUser.favorites` existe mais n'est pas utilisé dans les popups
- **Impact** : Les favoris ne sont pas vraiment séparés des likes
- **Note** : Le système d'alertes utilise `currentUser.favorites` pour détecter les nouveaux événements

---

## 💡 Recommandations

### Option 1 : Ajouter Agenda et Route pour Bookings/Services
```javascript
// Dans buildBookingPopup et buildServicePopup
<button onclick="onAction('agenda', 'booking', ${b.id})">📅 Agenda</button>
<button onclick="onAction('route', 'booking', ${b.id})">🗺️ Route</button>
```

### Option 2 : Clarifier Like vs Favoris
- Soit renommer "Favoris" en "Like" dans les popups
- Soit créer une vraie fonction `toggleFavorite()` séparée

### Option 3 : Unifier les actions
- Créer une fonction générique qui gère toutes les actions de manière cohérente
- S'assurer que toutes les actions fonctionnent pour tous les types quand c'est logique

---

## ✅ Ce qui fonctionne bien

1. **Système de signalements** - Fonctionne pour tous les types
2. **Système de likes** - Fonctionne pour tous les types
3. **Système de partage** - Fonctionne pour tous les types
4. **Système d'avis** - Fonctionne pour tous les types
5. **Système de discussion** - Fonctionne pour tous les types
6. **Achat de contact** - Spécifique et fonctionnel pour bookings/services

---

## 📝 Actions à faire (si nécessaire)

1. [ ] Ajouter bouton "Agenda" pour bookings/services
2. [ ] Ajouter bouton "Route" pour bookings/services
3. [ ] Clarifier ou séparer Like vs Favoris
4. [ ] Tester toutes les actions pour tous les types
5. [ ] Vérifier que le backend supporte toutes les actions pour tous les types



