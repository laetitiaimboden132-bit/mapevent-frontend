# 📚 CONTEXTE COMPLET DU PROJET - MAP EVENT AI

**Date de création** : 2025-12-08  
**Version** : Pro  
**État** : Actif - Prêt pour développement  
**Domaine** : mapevent.world (configuré avec SendGrid)

---

## 📁 STRUCTURE COMPLÈTE DU PROJET

```
MapEventAI_NEW/
├── backend/                    # Backend Flask (Python)
│   ├── main.py                # Point d'entrée Flask (port 5005)
│   ├── api/                   # Blueprints Flask (APIs)
│   │   ├── events_api.py      # API événements
│   │   ├── booking_api.py    # API bookings
│   │   ├── services_api.py   # API services
│   │   └── map_api.py        # API carte
│   ├── ai_engine/            # Moteur de scraping AI
│   │   ├── extractor_api_official.py    # Extracteurs sources officielles
│   │   ├── extractor_ai.py              # Extracteur AI général
│   │   ├── extractor_ai_booking.py      # Extracteur AI bookings
│   │   ├── extractor_ai_services.py     # Extracteur AI services
│   │   ├── extractor_songkick.py        # API Songkick
│   │   ├── extractor_eventbrite.py      # Eventbrite
│   │   ├── extractor_ticketmaster.py    # Ticketmaster
│   │   ├── extractor_facebook_api.py    # Facebook API
│   │   ├── extractor_lastfm.py         # Last.fm
│   │   ├── event_validator.py           # Validation stricte événements
│   │   ├── auto_publisher.py            # Publication automatique
│   │   ├── category_engine.py           # Gestion catégories
│   │   ├── date_extractor.py            # Extraction dates
│   │   ├── location_extractor.py        # Extraction localisation
│   │   ├── description_extractor.py     # Extraction descriptions
│   │   └── event_status_detector.py     # Détection statuts
│   ├── core/                  # Modules core
│   │   ├── file_db.py         # Gestion fichiers JSON (thread-safe)
│   │   ├── geo_utils.py       # Utilitaires géographiques
│   │   └── ai_enricher.py     # Enrichissement AI
│   ├── sources/               # Extracteurs sources spécifiques
│   │   └── events/
│   │       ├── geneve_ch.py   # Site officiel Genève
│   │       ├── lausanne_ch.py # Site officiel Lausanne
│   │       ├── leprogramme_ch.py # Leprogramme.ch
│   │       └── myvaud.py      # MyVaud
│   ├── data/                  # Données (backend)
│   │   ├── events_status.json # Événements publiés
│   │   ├── events_status_fixed.json
│   │   └── geocode_cache.db  # Cache géocodage
│   └── logs/                  # Logs backend
│       └── backend.log
│
├── frontend/                  # Frontend (HTML/CSS/JS)
│   ├── public/
│   │   ├── mapevent.html     # Page principale (698 lignes)
│   │   ├── map_logic.js       # Logique principale (5808 lignes)
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── api.js         # Fonctions API
│   │   ├── trees/              # Arbres de catégories
│   │   │   ├── events_tree.json
│   │   │   ├── booking_tree.json
│   │   │   └── service_tree.json
│   │   └── assets/
│   │       ├── category_images/  # Images par catégorie
│   │       └── event_overlays/   # Overlays statuts
│   └── DEMARRER_SERVEUR.bat   # Script démarrage frontend
│
├── config/                    # Configuration
│   ├── settings.py            # Settings Python
│   ├── api_keys.json          # Clés API
│   ├── apis_official.json     # Sources officielles
│   ├── facebook_settings.json
│   ├── smtp_settings.json     # Configuration SendGrid
│   └── urls.json
│
├── data/                      # Données globales
│   ├── events_status.json     # Événements (copie)
│   ├── events.json
│   ├── booking_db.json
│   ├── services_db.json
│   ├── contacts_cache.json    # Cache contacts IA
│   └── urls_*.txt             # Listes URLs sources
│
├── logs/                      # Logs globaux
│   ├── auto_publisher.log
│   ├── backend.log
│   └── contacts_extractor.log
│
├── scraper/                   # Scrapers externes
│   └── python/
│       └── scraper_events_ch.py
│
├── DEMARRER_TOUT.bat          # Démarre frontend + backend
├── DEMARRER_BACKEND.bat       # Démarre backend uniquement
├── SAUVEGARDE_MANUELLE.bat    # Script sauvegarde
├── SAUVEGARDE_PROJET.md       # Guide sauvegarde
├── README.md                  # Documentation données
└── SOURCES_OFFICIELLES.md     # Documentation sources
```

---

## 🎯 ARCHITECTURE GÉNÉRALE

### **Stack Technologique**

#### **Backend**
- **Framework** : Flask (Python)
- **Port** : 5005
- **CORS** : Activé pour toutes les origines (`/api/*`)
- **Base de données** : Fichiers JSON (thread-safe avec `file_db.py`)
- **Logging** : Fichiers dans `logs/backend.log`

#### **Frontend**
- **Serveur** : Python HTTP Server (port 3000)
- **Bibliothèque carte** : Leaflet.js 1.9.4
- **Langages** : HTML5, CSS3, JavaScript (ES6+)
- **Pas de framework** : Vanilla JS pur

#### **Scraping AI**
- **Langage** : Python 3.x
- **Bibliothèques** : requests, beautifulsoup4, python-dateutil
- **Validation** : Système strict (score de fiabilité 95% minimum)
- **Sources** : Sites officiels, APIs (Songkick, Eventbrite, Ticketmaster)

---

## 🔧 BACKEND - DÉTAILS TECHNIQUES

### **1. Point d'Entrée : `main.py`**

```python
# Port : 5005
# Host : 0.0.0.0 (accessible réseau local)
# Debug : True (mode développement)
# CORS : Activé pour /api/*

# Blueprints enregistrés :
- events_bp (url_prefix="/api/events")
```

**Endpoints principaux** :
- `GET /` : Statut backend
- `GET /health` : Health check
- `GET /api/events` : Tous les événements
- `GET /api/events/categories` : Catégories
- `POST /api/events/filter` : Filtrage événements

### **2. API Événements : `api/events_api.py`**

**Fonctions principales** :
- `load_events()` : Charge depuis `data/events_status.json` (UTF-8)
- `load_events_tree()` : Charge l'arbre de catégories
- `flatten_tree_to_groups()` : Convertit arbre en format simple
- `parse_event_start()` : Parse dates avec dateutil
- `within_date_filter()` : Filtre par date (today, weekend, week, month, custom)
- `haversine_km()` : Calcul distance entre 2 points (formule Haversine)
- `within_radius()` : Filtre par rayon
- `event_matches_categories()` : Filtre par catégories

**Endpoints** :
- `GET /api/events/categories` : Retourne catégories formatées
- `POST /api/events/filter` : Filtre avec payload JSON
  ```json
  {
    "categories": ["Techno", "House"],
    "date_filter": "week",
    "radius_km": 50,
    "center": {"lat": 46.5197, "lon": 6.6323},
    "date_start": "2025-12-01",
    "date_end": "2025-12-31"
  }
  ```

### **3. Core : `core/file_db.py`**

**Fonctionnalités** :
- Thread-safe (verrouillage avec `threading.Lock`)
- Gestion automatique création fichiers
- UTF-8 avec `ensure_ascii=False`
- Format : `{"events": [...]}`

**Fonctions** :
- `load_events()` : Charge tous les événements
- `save_events(events)` : Sauvegarde tous les événements

### **4. AI Engine : Extracteurs**

#### **Extracteurs Sources Officielles**
- `extractor_api_official.py` : Orchestrateur principal
  - Intègre tous les extracteurs officiels
  - Validation automatique
  - Score de fiabilité 95% minimum

#### **Extracteurs Spécifiques**
- `extractor_songkick.py` : API Songkick (nécessite `SONGKICK_API_KEY`)
- `extractor_eventbrite.py` : Eventbrite
- `extractor_ticketmaster.py` : Ticketmaster (nécessite `TICKETMASTER_API_KEY`)
- `extractor_facebook_api.py` : Facebook Graph API
- `extractor_lastfm.py` : Last.fm

#### **Extracteurs Sites Officiels**
- `sources/events/geneve_ch.py` : Site officiel Genève
- `sources/events/lausanne_ch.py` : Site officiel Lausanne
- `sources/events/leprogramme_ch.py` : Leprogramme.ch
- `sources/events/myvaud.py` : MyVaud

#### **Extracteurs AI**
- `extractor_ai.py` : Extracteur AI général
- `extractor_ai_booking.py` : AI pour bookings
- `extractor_ai_services.py` : AI pour services
- `extractor_ai_pro.py` : AI Pro
- `extractor_ai_plus.py` : AI Plus

#### **Utilitaires**
- `event_validator.py` : Validation stricte (source, date, titre, localisation, doublons)
- `auto_publisher.py` : Publication automatique dans `events_status.json`
- `category_engine.py` : Gestion catégories et mapping
- `date_extractor.py` : Extraction dates (français supporté)
- `location_extractor.py` : Extraction adresses
- `description_extractor.py` : Extraction descriptions
- `event_status_detector.py` : Détection statuts (annulé, reporté, complet)

### **5. Validation Stricte**

**Critères de validation** (`event_validator.py`) :
1. ✅ **Source officielle** : URL dans liste blanche
2. ✅ **Date valide** : Date future (max 1 an)
3. ✅ **Titre valide** : Min 3 caractères, pas de mots-clés invalides
4. ✅ **Localisation valide** : Ville, adresse ou coordonnées
5. ✅ **Pas de doublon** : Détection automatique

**Score de fiabilité** :
- Sources officielles : 95% (minimum requis)
- APIs officielles : 95%
- Sources tierces : Variable selon validation

---

## 🎨 FRONTEND - DÉTAILS TECHNIQUES

### **1. Page Principale : `mapevent.html`**

**Structure** :
- Topbar fixe (64px de hauteur)
- Logo avec halo animé (SVG)
- Boutons modes (Events, Booking, Services)
- Bouton Liste
- Boutons utilitaires (ABO, Panier, Agenda, Alertes, Compte)
- Carte Leaflet (plein écran)
- Panel gauche (filtres) - masqué par défaut
- Vue liste - masquée par défaut
- Modals (backdrop + inner)

**Thèmes CSS** :
- Variables CSS pour thèmes dynamiques
- 5 thèmes UI configurables
- 3 thèmes carte configurables

### **2. Logique Principale : `map_logic.js`**

**Variables globales importantes** :
```javascript
// État carte
let map, tileLayer, markersLayer, markerMap = {};

// Modes et données
let currentMode = "event";
let eventsData = [], bookingsData = [], servicesData = [];
let filteredData = null; // null = tous, array = filtrés

// UI
let leftPanelOpen = false, listViewOpen = false;
let uiThemeIndex = 0, mapThemeIndex = 0;

// Filtres
let selectedCategories = []; // Max 5
let selectedDates = [];
let timeFilter = null;
let dateRangeStart = null, dateRangeEnd = null;

// Utilisateur
let currentUser = {
  subscription: "free",
  agendaLimit: 20,
  alertLimit: 0,
  favorites: [], agenda: [], likes: [], alerts: []
};
```

**Fonctions principales** :
- `initMap()` : Initialise Leaflet
- `loadDataFromBackend(type)` : Charge depuis API (port 5005)
- `refreshMarkers()` : Rafraîchit marqueurs sur carte
- `refreshListView()` : Rafraîchit vue liste (tri par boost)
- `applyExplorerFilter()` : Applique filtres (catégories + dates)
- `buildMarkerIcon(item)` : Construit icône avec boosts
- `buildEventPopup(ev)` : Construit popup complète
- `openPopupFromList(type, id)` : Ouvre popup depuis liste

**Système de boosts** :
- AI : Bordure noire 3px
- Basic : Bordure noire 3px
- Bronze : Bordure bronze #cd7f32
- Silver : Bordure argent #c0c0c0 (+0.5mm)
- Gold : Bordure jaune #ffd700 + étoile
- Platinum : Top 10 (enchères), bordure rouge
- Top 1-10 : Visuels spéciaux (couronnes, cœurs, halos)

**Tri dans la liste** :
- Actuellement : Boost uniquement (platinum > gold > silver > bronze > basic)
- Limite : 300 résultats maximum
- À améliorer : Ajouter tri par catégories + distance depuis centre map

### **3. Arbres de Catégories**

**Fichiers** :
- `trees/events_tree.json` : Arbre hiérarchique Events
- `trees/booking_tree.json` : Arbre hiérarchique Booking
- `trees/service_tree.json` : Arbre hiérarchique Service

**Structure** :
```json
{
  "Events": {
    "Music": {
      "Electronic": {
        "Techno": [],
        "House": [],
        "Disco": []
      }
    }
  }
}
```

**Chargement** :
- Chargé au démarrage via `loadCategoryTrees()`
- Utilisé pour filtres et images de catégories

### **4. Assets**

**Images catégories** :
- `assets/category_images/event/` : Images pour événements
- `assets/category_images/booking/` : Images pour bookings
- `assets/category_images/service/` : Images pour services

**Overlays statuts** :
- `assets/event_overlays/eventdefault.jpg` : Par défaut
- `assets/event_overlays/completed.jpeg` : Terminé
- `assets/event_overlays/Event canceled.jpeg` : Annulé
- `assets/event_overlays/postponed.jpeg` : Reporté

---

## 🔐 CONFIGURATION ET VARIABLES D'ENVIRONNEMENT

### **Fichier `.env` (Racine du projet)**

**Variables requises** :
```env
# APIs Officielles
SONGKICK_API_KEY=your_key_here
TICKETMASTER_API_KEY=your_key_here
TICKETMASTER_COUNTRY=CH

# Géocodage
GOOGLE_API_KEY=your_key_here

# Facebook
FACEBOOK_ACCESS_TOKEN=your_token_here

# Ticketswap
TICKETSWAP_API_KEY=your_key_here

# SendGrid (Email)
SENDGRID_API_KEY=your_key_here
MAPEVENT_BASE_URL=http://localhost:3000

# Pays par défaut
OFFICIAL_API_COUNTRY=CH
```

### **Fichiers de Configuration**

**`config/settings.py`** :
- Charge `.env` depuis racine projet
- Classe `Settings` avec toutes les clés API

**`config/apis_official.json`** :
- Liste des sources officielles
- Scores de fiabilité

**`config/smtp_settings.json`** :
- Configuration SendGrid
- Domaine : mapevent.world

---

## 📡 INTÉGRATION FRONTEND-BACKEND

### **Endpoints API Utilisés**

**Frontend → Backend** :
- `GET http://localhost:5005/api/events` : Tous les événements
- `GET http://localhost:5005/api/bookings` : Tous les bookings
- `GET http://localhost:5005/api/services` : Tous les services

**Protection** :
- Flag `isLoadingBackend` : Évite appels multiples
- Rate limiting : 10 secondes minimum entre tentatives échouées
- Gestion UTF-8 BOM : `encoding="utf-8-sig"` pour fichiers JSON

**Filtrage automatique frontend** :
- Événements passés : Exclus automatiquement
- Événements < 30 jours : Exclus (désactivé en phase test, `minDays = 0`)

---

## 🚀 SCRIPTS DE DÉMARRAGE

### **`DEMARRER_TOUT.bat`**
Démarre frontend + backend dans fenêtres séparées :
```batch
# Backend : Port 5005
# Frontend : Port 3000
# URLs affichées automatiquement
```

### **`DEMARRER_BACKEND.bat`**
Démarre uniquement le backend Flask.

### **`frontend/DEMARRER_SERVEUR.bat`**
Démarre uniquement le frontend HTTP.

### **Scripts de Test**
- `run_events_only.bat` : Test scraping événements
- `run_booking_only.bat` : Test scraping bookings
- `run_services_only.bat` : Test scraping services
- `run_auto_publisher.bat` : Publication automatique

---

## 💾 SYSTÈME DE DONNÉES

### **Fichiers de Données Principaux**

**`data/events_status.json`** :
```json
{
  "events": [
    {
      "id": 1,
      "type": "event",
      "title": "...",
      "startDate": "2025-12-15T20:00:00Z",
      "endDate": "2025-12-16T02:00:00Z",
      "city": "Lausanne",
      "address": "Rue de la Gare 12, Lausanne",
      "lat": 46.5197,
      "lng": 6.6323,
      "categories": ["Techno"],
      "boost": "gold",
      "sourceUrl": "https://...",
      "isAI": true,
      "reliabilityScore": 95
    }
  ]
}
```

**`data/contacts_cache.json`** :
- Cache contacts trouvés par IA
- Champ `verified: true` après confirmation

**`data/booking_db.json`** : Bookings
**`data/services_db.json`** : Services

### **Cache Géocodage**

**`backend/data/geocode_cache.db`** :
- Cache SQLite pour géocodage
- Évite appels API répétés

---

## 🔄 WORKFLOW DE PUBLICATION

### **1. Scraping**
- Extracteurs récupèrent événements depuis sources
- Validation automatique (score 95% minimum)
- Filtrage dates (30 jours minimum en production)

### **2. Validation**
- `event_validator.py` vérifie tous les critères
- Rejet si score < 95%
- Rejet si doublon détecté

### **3. Publication**
- `auto_publisher.py` écrit dans `events_status.json`
- Format : `{"events": [...]}`
- Thread-safe avec `file_db.py`

### **4. Affichage Frontend**
- `loadDataFromBackend()` charge depuis API
- Filtrage automatique (passés, < 30 jours)
- Affichage sur carte avec marqueurs

---

## 📧 SYSTÈME EMAIL (SendGrid)

### **Configuration**
- **Domaine** : mapevent.world
- **Numéro domaine** : 188694213
- **Statut** : Actif (24-48h après achat)
- **Clé API** : À configurer dans `.env`

### **Fonctionnalités**
- Envoi emails confirmation
- Notifications organisateurs
- Liens personnalisés (domaine mapevent.world)

---

## 🎯 FONCTIONNALITÉS PRINCIPALES

### **1. Carte Interactive**
- Leaflet.js avec marqueurs dynamiques
- Popups complètes avec toutes les infos
- Filtres par catégories (multi-sélection, max 5)
- Filtres par dates (boutons rapides + calendrier)
- Thèmes UI (5) et carte (3)

### **2. Système de Boosts**
- 6 types : AI, Basic, Bronze, Silver, Gold, Platinum
- Top 10 : Système d'enchères par ville
- Visuels spéciaux : Couronnes, cœurs, halos selon ranking
- Top 1-2 : Couleurs changent avec thème

### **3. Abonnements**
- 6 plans : Free, Events Explorer, Events Alertes Pro, Service Pro, Service Ultra, Full Premium
- Full Premium : AI Live Assistant + Tous points en OR
- Limites : Agenda (20-250), Alertes (0-illimité)

### **4. Système d'Alertes**
- Basé sur likes (organisateurs, bookings, services, catégories)
- Notifications si événement dans 60km
- Limite selon abonnement

### **5. Vue Liste**
- Tri par boost (platinum > gold > silver > bronze > basic)
- Limite 300 résultats
- Popup complète au clic
- À améliorer : Tri par catégories + distance

---

## 🐛 PROBLÈMES CONNUS / NOTES

### **Backend**
1. **Filtre 30 jours** : Désactivé en phase test, à réactiver en production
2. **Validation stricte** : Score 95% minimum requis
3. **Géocodage** : Cache SQLite pour optimiser
4. **Thread-safety** : `file_db.py` utilise verrous

### **Frontend**
1. **Tri liste** : Actuellement uniquement par boost (code simplifié)
2. **Filtre 30 jours** : Désactivé en phase test (`minDays = 0`)
3. **Bordures AI/Basic** : Noires 3px, visibles (corrigé)
4. **Logo halo** : Change de couleur avec thème

### **Intégration**
1. **CORS** : Activé pour toutes origines (`/api/*`)
2. **UTF-8 BOM** : Géré avec `encoding="utf-8-sig"`
3. **Rate limiting** : 10 secondes entre tentatives échouées
4. **Protection appels multiples** : Flag `isLoadingBackend`

---

## 📊 STATISTIQUES DU CODE

### **Backend**
- **Fichiers Python** : ~27 dans `ai_engine/`
- **APIs** : 4 blueprints (events, booking, services, map)
- **Extracteurs** : ~15 extracteurs différents
- **Lignes de code** : ~5000+ (estimation)

### **Frontend**
- **mapevent.html** : ~698 lignes
- **map_logic.js** : ~5808 lignes
- **Fonctions** : ~662 fonctions/variables
- **Thèmes UI** : 5
- **Thèmes carte** : 3

### **Données**
- **Villes suisses** : 30+ avec coordonnées
- **Catégories** : Chargées dynamiquement depuis JSON
- **Images catégories** : ~100+ images

---

## 🚀 PROCHAINES ÉTAPES SUGGÉRÉES

### **Court Terme**
1. **Améliorer tri liste** : Catégories + distance depuis centre map
2. **Réactiver filtre 30 jours** : En production
3. **Connecter AI Live Assistant** : Intégrer API OpenAI/Claude
4. **Système paiement réel** : Stripe/PayPal

### **Moyen Terme**
1. **Notifications push** : Service de notifications
2. **Géocodage optimisé** : Batch processing
3. **Cache intelligent** : Redis pour performances
4. **Monitoring** : Dashboard statistiques

### **Long Terme**
1. **Base de données** : Migration vers PostgreSQL
2. **Microservices** : Séparation scraping/API/frontend
3. **CDN** : Assets statiques
4. **CI/CD** : Déploiement automatique

---

## 📝 NOTES IMPORTANTES

### **Sauvegarde**
- Script : `SAUVEGARDE_MANUELLE.bat`
- Guide : `SAUVEGARDE_PROJET.md`
- Recommandation : Git + Cloud (OneDrive/Google Drive)

### **Dépendances Backend**
```bash
pip install flask flask-cors requests beautifulsoup4 python-dateutil python-dotenv
```

### **Ports Utilisés**
- **Frontend** : 3000 (HTTP Server)
- **Backend** : 5005 (Flask)
- **Firefox** : Utiliser `127.0.0.1` si problème proxy

### **Domaine**
- **Nom** : mapevent.world
- **Registrar** : Configuré
- **SendGrid** : Domain authenticated
- **DNS** : À configurer selon SendGrid

---

## 🔗 LIENS ET RESSOURCES

### **URLs Locales**
- Frontend : `http://localhost:3000/mapevent.html`
- Backend : `http://localhost:5005`
- Health : `http://localhost:5005/health`
- API Events : `http://localhost:5005/api/events`

### **Documentation**
- `SOURCES_OFFICIELLES.md` : Sources et validation
- `backend/RESUME_MODIFICATIONS.md` : Historique modifications
- `backend/INSTALL_DEPENDENCIES.md` : Installation
- `frontend/README_SERVEURS.md` : Guide serveurs

### **Fichiers de Configuration**
- `.env` : Variables d'environnement (racine projet)
- `config/settings.py` : Settings Python
- `config/apis_official.json` : Sources officielles
- `config/smtp_settings.json` : SendGrid

---

## ✅ CHECKLIST DÉMARRAGE

### **Avant de commencer**
- [ ] Vérifier Python installé (`python --version`)
- [ ] Installer dépendances (`pip install ...`)
- [ ] Configurer `.env` avec clés API
- [ ] Vérifier ports 3000 et 5005 libres

### **Démarrage**
- [ ] Lancer `DEMARRER_TOUT.bat` ou scripts séparés
- [ ] Vérifier backend : `http://localhost:5005/health`
- [ ] Vérifier frontend : `http://localhost:3000/mapevent.html`
- [ ] Vérifier console navigateur (F12) pour erreurs

### **Test**
- [ ] Carte s'affiche correctement
- [ ] Marqueurs apparaissent
- [ ] Popups s'ouvrent
- [ ] Filtres fonctionnent
- [ ] Vue liste fonctionne

---

**Document généré automatiquement - Ne pas modifier manuellement**  
**Pour toute modification, mettre à jour ce document**  
**Dernière mise à jour : 2025-12-08**
































