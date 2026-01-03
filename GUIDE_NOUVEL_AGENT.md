# 🚀 GUIDE POUR NOUVEL AGENT - MAP EVENT AI

**Date** : 2025-12-08  
**Projet** : MapEventAI - Plateforme événementielle avec carte interactive  
**État** : Actif - En développement

---

## 📋 RÉSUMÉ RAPIDE

**MapEventAI** est une plateforme web qui affiche des événements, bookings et services sur une carte interactive (Leaflet.js). Le projet comprend :
- **Backend Flask** (Python) : APIs et scraping AI
- **Frontend** (HTML/CSS/JS) : Carte interactive avec filtres et boosts
- **Système de scraping** : Extraction automatique depuis sources officielles

**URLs** :
- Frontend : `http://localhost:3000/mapevent.html`
- Backend : `http://localhost:5005`

---

## 🎯 TÂCHES PRINCIPALES À TRAVAILLER

### **1. FRONTEND - Améliorations UI/UX**
- ✅ Carte Leaflet fonctionnelle
- ✅ Système de boosts visuels
- ✅ Filtres par catégories et dates
- ⚠️ **À améliorer** : Tri dans la liste (catégories + distance)
- ⚠️ **À améliorer** : Système AI Live Assistant (interface prévue, pas connectée)

### **2. BACKEND - APIs et Scraping**
- ✅ APIs Flask fonctionnelles
- ✅ Extracteurs sources officielles
- ✅ Validation stricte (score 95%)
- ⚠️ **À améliorer** : Géocodage batch optimisé
- ⚠️ **À améliorer** : Système de notifications email

### **3. INTÉGRATION - Frontend ↔ Backend**
- ✅ Chargement données depuis API
- ✅ Filtrage automatique (dates, catégories)
- ⚠️ **À améliorer** : Gestion erreurs réseau
- ⚠️ **À améliorer** : Cache côté frontend

---

## 📁 STRUCTURE DU PROJET

```
MapEventAI_NEW/
├── backend/           # Backend Flask (Python)
│   ├── main.py       # Point d'entrée (port 5005)
│   ├── api/          # Blueprints Flask
│   ├── ai_engine/    # Extracteurs et scraping
│   └── core/         # Modules core
│
├── frontend/          # Frontend (HTML/CSS/JS)
│   └── public/
│       ├── mapevent.html    # Page principale
│       ├── map_logic.js     # Logique (5808 lignes)
│       └── trees/           # Arbres catégories
│
├── config/           # Configuration
├── data/             # Données JSON
└── logs/             # Logs
```

---

## 🔧 DÉMARRAGE RAPIDE

### **1. Installer les dépendances**
```bash
cd C:\MapEventAI_NEW\backend
pip install flask flask-cors requests beautifulsoup4 python-dateutil python-dotenv
```

### **2. Configurer .env (racine projet)**
Créer `.env` avec :
```env
SONGKICK_API_KEY=your_key
TICKETMASTER_API_KEY=your_key
GOOGLE_API_KEY=your_key
SENDGRID_API_KEY=your_key
MAPEVENT_BASE_URL=http://localhost:3000
```

### **3. Démarrer les serveurs**
```bash
# Option 1 : Script automatique
C:\MapEventAI_NEW\DEMARRER_TOUT.bat

# Option 2 : Manuel
# Terminal 1 - Backend
cd C:\MapEventAI_NEW\backend
python main.py

# Terminal 2 - Frontend
cd C:\MapEventAI_NEW\frontend\public
python -m http.server 3000
```

### **4. Ouvrir le site**
```
http://localhost:3000/mapevent.html
```

---

## 📖 DOCUMENTATION DÉTAILLÉE

### **Pour comprendre le FRONTEND**
Lire : `frontend/CONTEXTE_FRONTEND_COMPLET.md`
- Structure HTML/CSS/JS
- Variables globales
- Fonctions principales
- Système de boosts
- Thèmes UI

### **Pour comprendre le BACKEND**
Lire : `backend/RESUME_MODIFICATIONS.md` et `SOURCES_OFFICIELLES.md`
- Architecture Flask
- Extracteurs AI
- Validation stricte
- APIs disponibles

### **Pour comprendre TOUT LE PROJET**
Lire : `frontend/CONTEXTE_PROJET_COMPLET.md`
- Architecture complète
- Workflow de publication
- Configuration
- Système de données

---

## 🎨 FRONTEND - POINTS CLÉS

### **Fichiers Principaux**
- `public/mapevent.html` : Page principale (698 lignes)
- `public/map_logic.js` : Logique complète (5808 lignes)

### **Variables Globales Importantes**
```javascript
let currentMode = "event";        // "event" | "booking" | "service"
let eventsData = [];              // Données événements
let selectedCategories = [];      // Catégories sélectionnées (max 5)
let filteredData = null;         // null = tous, array = filtrés
let currentUser = {...};          // Utilisateur actuel
```

### **Fonctions Clés**
- `loadDataFromBackend(type)` : Charge depuis API (port 5005)
- `refreshMarkers()` : Rafraîchit marqueurs sur carte
- `refreshListView()` : Rafraîchit vue liste
- `applyExplorerFilter()` : Applique filtres
- `buildMarkerIcon(item)` : Construit icône avec boosts
- `buildEventPopup(ev)` : Construit popup complète

### **Système de Boosts**
- **AI/Basic** : Bordure noire 3px
- **Bronze** : Bordure bronze #cd7f32
- **Silver** : Bordure argent #c0c0c0 (+0.5mm)
- **Gold** : Bordure jaune #ffd700 + étoile
- **Platinum** : Top 10 (enchères), bordure rouge
- **Top 1-10** : Visuels spéciaux (couronnes, cœurs, halos)

### **Tri Actuel dans la Liste**
```javascript
// Actuellement : Boost uniquement
const order = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
data.sort((a, b) => order[a.boost] - order[b.boost]);
```

**À améliorer** : Ajouter tri par catégories (ordre sélection) + distance depuis centre map

---

## 🔌 BACKEND - POINTS CLÉS

### **Fichiers Principaux**
- `backend/main.py` : Point d'entrée Flask (port 5005)
- `backend/api/events_api.py` : API événements
- `backend/core/file_db.py` : Gestion fichiers JSON (thread-safe)
- `backend/ai_engine/extractor_api_official.py` : Orchestrateur scraping

### **Endpoints API**
- `GET /api/events` : Tous les événements
- `GET /api/events/categories` : Catégories
- `POST /api/events/filter` : Filtrage avec payload JSON

### **Extracteurs Disponibles**
- `sources/events/geneve_ch.py` : Site officiel Genève
- `sources/events/lausanne_ch.py` : Site officiel Lausanne
- `sources/events/leprogramme_ch.py` : Leprogramme.ch
- `ai_engine/extractor_songkick.py` : API Songkick
- `ai_engine/extractor_eventbrite.py` : Eventbrite
- `ai_engine/extractor_ticketmaster.py` : Ticketmaster

### **Validation Stricte**
- Score minimum : **95%**
- Critères : Source officielle, date valide, titre valide, localisation, pas de doublon
- Fichier : `backend/ai_engine/event_validator.py`

### **Données**
- Fichier principal : `data/events_status.json`
- Format : `{"events": [...]}`
- Thread-safe : Utilise `file_db.py` avec verrous

---

## 🐛 PROBLÈMES CONNUS

### **Frontend**
1. **Tri liste** : Actuellement uniquement par boost (code simplifié)
2. **Filtre 30 jours** : Désactivé en phase test (`minDays = 0`)
3. **AI Live Assistant** : Interface prévue mais pas connectée à API

### **Backend**
1. **Géocodage** : Pas de batch optimisé (appels individuels)
2. **Notifications email** : Préparé mais pas encore connecté
3. **Cache** : SQLite pour géocodage, mais pas pour événements

### **Intégration**
1. **Gestion erreurs** : Basique, à améliorer
2. **Rate limiting** : 10 secondes entre tentatives échouées
3. **UTF-8 BOM** : Géré avec `encoding="utf-8-sig"`

---

## ✅ TÂCHES PRIORITAIRES

### **1. Améliorer le tri dans la liste** (Frontend)
**Fichier** : `frontend/public/map_logic.js`  
**Fonction** : `refreshListView()`  
**Objectif** : Ajouter tri par catégories (ordre sélection) + distance depuis centre map

**Code actuel** :
```javascript
// Ligne ~1677
const order = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
const data = base.slice().sort((a, b) => {
  const ra = order[a.boost || "basic"] || 99;
  const rb = order[b.boost || "basic"] || 99;
  return ra - rb;
});
```

**À faire** :
1. Ajouter tri par catégories (ordre de sélection)
2. Ajouter tri par distance depuis centre map (`map.getCenter()`)
3. Garder tri par boost en dernier recours
4. Limiter à 300 résultats (déjà fait mais vérifier)

### **2. Connecter AI Live Assistant** (Frontend + Backend)
**Fichiers** :
- Frontend : `frontend/public/map_logic.js` (fonction `openAccountModal()`)
- Backend : À créer `backend/api/ai_chat_api.py`

**Objectif** : Interface chat fonctionnelle avec API OpenAI/Claude

**À faire** :
1. Créer endpoint backend `/api/ai/chat`
2. Intégrer API OpenAI ou Claude
3. Gérer contexte utilisateur (préférences, historique)
4. Connecter interface frontend existante

### **3. Optimiser géocodage batch** (Backend)
**Fichier** : `backend/core/geo_utils.py` ou nouveau fichier  
**Objectif** : Géocoder plusieurs adresses en une seule requête

**À faire** :
1. Utiliser API batch si disponible (Google, Mapbox)
2. Implémenter cache intelligent
3. Réduire coûts API

### **4. Système notifications email** (Backend)
**Fichier** : `backend/ai_engine/email_notification_system.py` (à créer ou améliorer)  
**Objectif** : Envoyer emails via SendGrid

**Configuration** :
- Domaine : mapevent.world
- SendGrid API Key : Dans `.env`

**À faire** :
1. Configurer SendGrid avec domaine
2. Créer templates emails
3. Intégrer dans workflow publication

---

## 🔍 COMMENT NAVIGUER DANS LE CODE

### **Frontend - Trouver une fonction**
```bash
# Rechercher dans map_logic.js
grep "function nomFonction" frontend/public/map_logic.js
```

### **Backend - Trouver un endpoint**
```bash
# Rechercher dans api/
grep "@.*\.route" backend/api/*.py
```

### **Backend - Trouver un extracteur**
```bash
# Lister tous les extracteurs
ls backend/ai_engine/extractor_*.py
ls backend/sources/events/*.py
```

### **Vérifier les logs**
```bash
# Backend
cat logs/backend.log

# Scraping
cat backend/ai_engine/logs/smart_scraper.log
```

---

## 📝 CONVENTIONS DE CODE

### **Frontend**
- **Variables globales** : `let` ou `const`
- **Fonctions** : `function nomFonction() {}`
- **Callbacks** : Arrow functions `() => {}`
- **Console logs** : Utiliser emojis pour faciliter debug (📊, ✅, ⚠️, ❌)

### **Backend**
- **Imports** : Standard library d'abord, puis third-party
- **Logging** : Utiliser `logging.getLogger(__name__)`
- **Exceptions** : Toujours logger avec `logger.exception()`
- **Type hints** : Optionnels mais recommandés

### **Fichiers JSON**
- **Encoding** : UTF-8 avec `ensure_ascii=False`
- **Format** : Indentation 2 espaces
- **BOM** : Gérer avec `encoding="utf-8-sig"` si nécessaire

---

## 🚨 ERREURS FRÉQUENTES

### **"Port déjà utilisé"**
```bash
# Trouver le processus
netstat -ano | findstr ":5005"
netstat -ano | findstr ":3000"

# Tuer le processus
taskkill /F /PID <PID>
```

### **"Module not found"**
```bash
# Installer dépendances
pip install -r requirements.txt
# Ou manuellement
pip install flask flask-cors requests beautifulsoup4
```

### **"404 sur /api/events"**
- Vérifier que backend tourne sur port 5005
- Vérifier CORS activé
- Vérifier URL dans frontend : `http://localhost:5005/api/events`

### **"Aucune donnée disponible"**
- Vérifier que `data/events_status.json` existe et contient des données
- Vérifier encoding UTF-8
- Vérifier format JSON valide

---

## 📞 RESSOURCES UTILES

### **Documentation Externe**
- **Leaflet.js** : https://leafletjs.com/
- **Flask** : https://flask.palletsprojects.com/
- **SendGrid** : https://docs.sendgrid.com/

### **Fichiers de Documentation Projet**
- `frontend/CONTEXTE_PROJET_COMPLET.md` : Vue d'ensemble complète
- `frontend/CONTEXTE_FRONTEND_COMPLET.md` : Détails frontend
- `backend/RESUME_MODIFICATIONS.md` : Historique backend
- `SOURCES_OFFICIELLES.md` : Sources et validation
- `SAUVEGARDE_PROJET.md` : Guide sauvegarde

### **Scripts Utiles**
- `DEMARRER_TOUT.bat` : Démarre tout
- `SAUVEGARDE_MANUELLE.bat` : Sauvegarde manuelle
- `run_events_only.bat` : Test scraping événements

---

## ✅ CHECKLIST AVANT DE COMMENCER

- [ ] Lire ce guide complet
- [ ] Lire `frontend/CONTEXTE_PROJET_COMPLET.md` pour vue d'ensemble
- [ ] Installer dépendances backend
- [ ] Configurer `.env` avec clés API
- [ ] Démarrer serveurs (backend + frontend)
- [ ] Vérifier que le site fonctionne
- [ ] Vérifier console navigateur (F12) pour erreurs
- [ ] Comprendre la structure des données (`data/events_status.json`)

---

## 🎯 OBJECTIFS DU PROJET

### **Court Terme**
- Améliorer tri dans la liste
- Connecter AI Live Assistant
- Optimiser géocodage
- Système notifications email

### **Moyen Terme**
- Base de données (PostgreSQL)
- Cache intelligent (Redis)
- Monitoring et statistiques
- Notifications push

### **Long Terme**
- Microservices
- CDN pour assets
- CI/CD
- Scaling horizontal

---

**Bonne chance avec le projet ! 🚀**  
**En cas de question, référez-vous aux documents de contexte complets.**
