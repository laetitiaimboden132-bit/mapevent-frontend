# CONTEXTE FRONTEND COMPLET - MAP EVENT

**Date de création** : 2025-12-08  
**Version** : Pro  
**État** : Actif - Prêt pour développement

---

## 📁 STRUCTURE DES FICHIERS

```
frontend/
├── public/
│   ├── mapevent.html          # Page principale (698 lignes)
│   ├── map_logic.js           # Logique principale (5808 lignes)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── api.js
│   ├── trees/
│   │   ├── events_tree.json   # Arbre de catégories Events
│   │   ├── booking_tree.json  # Arbre de catégories Booking
│   │   └── service_tree.json  # Arbre de catégories Service
│   └── assets/
│       ├── category_images/   # Images par catégorie (event, booking, service)
│       └── event_overlays/     # Overlays pour statuts (completed, canceled, etc.)
```

---

## 🎯 FONCTIONNALITÉS PRINCIPALES

### 1. **CARTE INTERACTIVE (Leaflet.js)**
- **Bibliothèque** : Leaflet 1.9.4
- **Thèmes de carte** : OSM Clair, Carto Dark Matter, Carto Light
- **Marqueurs dynamiques** : Icônes personnalisées selon boost/catégorie
- **Popups** : Popups complètes avec toutes les infos (titre, description, dates, adresse, etc.)

### 2. **MODES D'AFFICHAGE**
- **Event** : Événements (mode par défaut)
- **Booking** : Artistes/DJs/Performers
- **Service** : Prestataires (son, lumière, décoration, etc.)

### 3. **SYSTÈME DE FILTRES**

#### **Filtre Explorateur (Left Panel)**
- Sélection multiple de catégories (jusqu'à 5)
- Arbre hiérarchique de catégories chargé depuis JSON
- Filtres cumulatifs (catégories + dates)

#### **Filtres de Date (Mode Event uniquement)**
- Boutons rapides : Aujourd'hui, Demain, Ce week-end, Cette semaine, **Ce mois**
- Calendrier personnalisé : Sélection de plage (Du/Au)
- Filtres cumulatifs (plusieurs dates possibles)

### 4. **VUE LISTE (List View)**
- **État** : Activée (bouton "📋 Liste" visible)
- **Tri** : Boost uniquement (platinum > gold > silver > bronze > basic)
- **Limite** : 300 résultats maximum
- **Popup** : Clic sur élément ouvre popup complète dans modal
- **Position** : `position:absolute`, `z-index:40`

### 5. **SYSTÈME DE BOOSTS**

#### **Types de boosts**
- **AI** : Bordure noire 3px, fond #2a2a2a
- **Basic** : Bordure noire 3px, fond #2a2a2a (même que AI)
- **Bronze** : Bordure bronze #cd7f32
- **Silver** : Bordure argent #c0c0c0, +0.5mm plus grand
- **Gold** : Bordure jaune #ffd700, étoile jaune
- **Platinum** : Top 10 (enchères), bordure rouge

#### **Top 10 (Système d'enchères)**
- Top 1-10 : Bordures et halos spéciaux selon ranking
- Top 1-2 : Bordure et halo changent avec le thème
- Top 3-10 : Bordure rouge
- Top 4 : Cœur rouge au lieu de couronne
- Top 5 : Halo rouge
- Top 6-9 : Tailles progressives
- Top 8 : Petite couronne

### 6. **ABONNEMENTS**

#### **Plans disponibles**
1. **Free** : Gratuit (20 places agenda, 0 alertes)
2. **Events Explorer** : CHF 5/mois (100 places, 10 alertes)
3. **Events Alertes Pro** : CHF 10/mois (200 places, alertes illimitées)
4. **Service Pro** : CHF 12/mois (contacts illimités, badge pro)
5. **Service Ultra** : CHF 18/mois (API, stats, 10 events gratuits/mois)
6. **Full Premium** : CHF 25/mois (250 places, AI Live, tous points en OR)

#### **Full Premium - Fonctionnalités spéciales**
- **AI Live Assistant** : Assistant conversationnel en direct
- **Tous points en OR** : Tous les événements publiés sont automatiquement boostés en OR
- Agenda 250 places
- Alertes illimitées
- Contacts illimités
- Accès API complet
- Statistiques avancées
- Support 24/7

### 7. **SYSTÈME D'ALERTES**
- Alertes basées sur likes (organisateurs, bookings, services, catégories)
- Notifications si événement dans un rayon de 60km
- Limite selon abonnement (0, 10, ou illimité)

### 8. **THÈMES UI**
5 thèmes disponibles :
1. **Dark Neon** (par défaut)
2. **Light Pro**
3. **Purple Cyberpunk**
4. **Miami Sunset**
5. **Blue Ice**

Chaque thème définit :
- Couleurs de fond (body, topbar, card)
- Bordures et textes
- Boutons (main, alt)
- Logo et tagline

### 9. **LOGO ET BRANDING**
- **Logo** : Cible avec points événements (SVG animé)
- **Halo animé** : Double halo rouge qui change de couleur avec le thème
- **Tagline** : "Votre plateforme événementielle"
- **Couleur logo** : Gradient cyan-bleu (#00ffc3 → #3b82f6)

---

## 🔧 VARIABLES GLOBALES IMPORTANTES

```javascript
// État de la carte
let map;                    // Instance Leaflet
let tileLayer;              // Couche de tuiles
let markersLayer;           // Groupe de marqueurs
let markerMap = {};         // Map des marqueurs par clé

// Modes et données
let currentMode = "event";   // "event" | "booking" | "service"
let eventsData = [];         // Données événements
let bookingsData = [];       // Données bookings
let servicesData = [];       // Données services
let filteredData = null;     // null = tous les points, array = filtrés

// UI
let leftPanelOpen = false;   // Panel gauche (filtres)
let listViewOpen = false;    // Vue liste
let uiThemeIndex = 0;        // Index thème UI
let mapThemeIndex = 0;       // Index thème carte

// Filtres
let selectedCategories = []; // Catégories sélectionnées (max 5)
let selectedDates = [];      // Dates sélectionnées (cumulatif)
let timeFilter = null;       // Filtre temporel
let dateRangeStart = null;   // Date début (calendrier)
let dateRangeEnd = null;     // Date fin (calendrier)

// Utilisateur
let currentUser = {
  id: 1,
  name: "Utilisateur Test",
  email: "test@mapevent.ch",
  subscription: "free",
  agendaLimit: 20,
  alertLimit: 0,
  favorites: [],
  agenda: [],
  likes: [],
  alerts: []
};
```

---

## 📡 INTÉGRATION BACKEND

### **API Endpoints utilisés**
- `http://localhost:5005/api/events` - GET tous les événements
- `http://localhost:5005/api/bookings` - GET tous les bookings
- `http://localhost:5005/api/services` - GET tous les services

### **Chargement des données**
- Fonction `loadDataFromBackend(type)` dans `map_logic.js`
- Protection contre appels multiples (`isLoadingBackend` flag)
- Rate limiting (10 secondes minimum entre tentatives échouées)
- Filtrage automatique des événements passés et < 30 jours

---

## 🎨 SYSTÈME DE BOOSTS VISUELS

### **Fonctions clés**
- `getBoostColor(boost)` : Couleur de base selon boost
- `getTopRankingSize(ranking)` : Taille selon ranking (1-10)
- `getTopRankingBorderColor(ranking)` : Couleur bordure (thème pour 1-2, rouge pour 3-10)
- `getTopRankingHaloColor(ranking)` : Couleur halo (thème pour 1-2, rouge pour 3-5)
- `getTopRankingPointerVisuals(ranking)` : Couronnes/cœurs selon ranking
- `buildMarkerIcon(item)` : Construction de l'icône complète

### **Logique de tri dans la liste**
```javascript
// Tri actuel : Boost uniquement
const order = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
data.sort((a, b) => {
  const ra = order[a.boost || "basic"] || 99;
  const rb = order[b.boost || "basic"] || 99;
  return ra - rb;
});
```

---

## 🔄 FONCTIONS PRINCIPALES

### **Initialisation**
- `initMap()` : Initialise la carte Leaflet
- `initUI()` : Initialise l'interface
- `loadCategoryTrees()` : Charge les arbres de catégories depuis JSON
- `applyUITheme(index)` : Applique un thème UI
- `applyMapTheme(index)` : Applique un thème de carte

### **Gestion des données**
- `getCurrentData()` : Récupère les données du mode actuel
- `getActiveData()` : Récupère les données filtrées ou toutes
- `loadDataFromBackend(type)` : Charge depuis l'API backend
- `refreshMarkers()` : Rafraîchit les marqueurs sur la carte
- `refreshListView()` : Rafraîchit la vue liste

### **Filtres**
- `toggleCategory(cat)` : Ajoute/retire une catégorie (max 5)
- `applyExplorerFilter()` : Applique les filtres (catégories + dates)
- `toggleDateFilter(dateType)` : Ajoute/retire une date
- `eventMatchesTimeFilter(item)` : Vérifie si un événement correspond aux filtres de date

### **Popups**
- `buildEventPopup(ev)` : Construit la popup complète pour un événement
- `buildBookingPopup(b)` : Construit la popup pour un booking
- `buildServicePopup(s)` : Construit la popup pour un service
- `openPopupFromList(type, id)` : Ouvre popup depuis la liste

### **Modals**
- `openPublishModal()` : Modal de publication
- `openSubscriptionModal()` : Modal abonnements
- `openAccountModal()` : Modal compte utilisateur
- `openAgendaModal()` : Modal agenda
- `openCartModal()` : Modal panier
- `openAlertsModal()` : Modal alertes/abonnements

### **Boosts**
- `openBoostPaymentModal(itemId, itemType, city)` : Modal paiement boost
- `purchaseBoost(itemId, itemType, city)` : Achat de boost
- `updateCityRankings(city, itemType)` : Met à jour les rankings par ville

---

## 🗺️ VILLES SUISSES

Liste complète dans `SWISS_CITIES` avec coordonnées (lat/lng) :
- Zürich, Genève, Bâle, Lausanne, Berne, Winterthur, Lucerne, St-Gall, Lugano, Bienne, Thoune, Köniz, La Chaux-de-Fonds, Fribourg, Schaffhouse, Coire, Neuchâtel, Sion, Montreux, Yverdon, Aarau, Bellinzone, Zoug, Nyon, Martigny, Bulle, Morges, Vevey, Locarno, Soleure, **Sierre**

---

## 🎯 ÉTAT ACTUEL DES FONCTIONNALITÉS

### ✅ **Implémenté et fonctionnel**
- Carte Leaflet avec marqueurs dynamiques
- 3 modes (Event, Booking, Service)
- Filtres par catégories (multi-sélection, max 5)
- Filtres par dates (boutons rapides + calendrier)
- Vue liste avec tri par boost
- Système de boosts visuels (AI, Bronze, Silver, Gold, Platinum, Top 10)
- Popups complètes avec toutes les infos
- Thèmes UI (5 thèmes)
- Thèmes carte (3 thèmes)
- Abonnements (6 plans)
- Système d'alertes basé sur likes
- Logo animé avec halo
- Chargement depuis backend API
- Filtrage automatique (événements passés, < 30 jours)

### ⚠️ **À améliorer/Compléter**
- Tri dans la liste : Actuellement uniquement par boost, devrait inclure :
  - Tri par catégories (ordre de sélection)
  - Tri par distance depuis le centre de la map
  - Limite à 300 résultats (déjà implémenté mais pas visible dans le code actuel)
- Système AI Live Assistant : Interface prévue mais pas encore connectée à une API
- Système de paiement : Simulé (fonction `simulatePremiumPayment`)
- Système de notifications : Préparé mais pas encore connecté

---

## 🐛 PROBLÈMES CONNUS / NOTES

1. **Filtre de 30 jours** : Désactivé en phase test (minDays = 0), à réactiver en production
2. **Tri dans refreshMarkers** : Actuellement pas de tri par catégories (code simplifié)
3. **Tri dans refreshListView** : Actuellement uniquement par boost (code simplifié)
4. **Logo halo** : Change de couleur avec le thème (fonction `applyUITheme`)
5. **Bordures AI/Basic** : Noires 3px, visibles (corrigé récemment)

---

## 📝 NOTES DE DÉVELOPPEMENT

### **Pour ajouter une nouvelle fonctionnalité**
1. Vérifier les variables globales pertinentes
2. Utiliser les fonctions existantes (ex: `showNotification`, `closePublishModal`)
3. Respecter la structure des modals (backdrop + inner)
4. Utiliser les thèmes UI via CSS variables

### **Pour modifier le tri**
- `refreshMarkers()` : Tri pour l'affichage sur la carte
- `refreshListView()` : Tri pour l'affichage en liste
- Actuellement simplifié : tri uniquement par boost

### **Pour ajouter un nouveau boost**
1. Ajouter dans `getBoostColor()`
2. Ajouter dans `buildMarkerIcon()` (case)
3. Ajouter dans l'ordre de tri (`order` object)
4. Mettre à jour les prix dans `getBoostPrice()`

---

## 🔗 LIENS IMPORTANTS

- **Backend API** : `http://localhost:5005`
- **Frontend** : `http://localhost:3000/mapevent.html`
- **Arbres catégories** : `/trees/events_tree.json`, `/trees/booking_tree.json`, `/trees/service_tree.json`
- **Assets** : `/assets/category_images/`, `/assets/event_overlays/`

---

## 📊 STATISTIQUES DU CODE

- **mapevent.html** : ~698 lignes
- **map_logic.js** : ~5808 lignes
- **Fonctions** : ~662 fonctions/variables
- **Thèmes UI** : 5
- **Thèmes carte** : 3
- **Villes suisses** : 30+
- **Catégories** : Chargées dynamiquement depuis JSON

---

## 🚀 PROCHAINES ÉTAPES SUGGÉRÉES

1. **Améliorer le tri dans la liste** :
   - Ajouter tri par catégories (ordre de sélection)
   - Ajouter tri par distance depuis centre map
   - Afficher message si limite 300 atteinte

2. **Connecter l'AI Live Assistant** :
   - Intégrer API OpenAI/Claude
   - Créer interface chat complète
   - Gérer le contexte utilisateur

3. **Système de paiement réel** :
   - Intégrer Stripe/PayPal
   - Gérer les webhooks
   - Mettre à jour les abonnements

4. **Notifications push** :
   - Intégrer service de notifications
   - Gérer les permissions
   - Envoyer notifications pour alertes

---

**Document généré automatiquement - Ne pas modifier manuellement**  
**Pour toute modification, mettre à jour ce document**
































