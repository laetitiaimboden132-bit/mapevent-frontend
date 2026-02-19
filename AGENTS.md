# Guide pour les Agents AI - MapEventAI

## Structure du Projet

```
frontend/
├── public/                    # Frontend (HTML, JS, CSS)
│   ├── mapevent.html         # Page principale de la carte
│   ├── auth.js               # Authentification (OAuth Google, JWT)
│   └── map_logic.js          # Logique de la carte et UI
├── lambda-package/           # Backend Lambda (NE PAS MODIFIER SANS REDÉPLOYER)
│   ├── backend/
│   │   ├── main.py           # API Flask principale
│   │   ├── auth.py           # JWT + bcrypt
│   │   └── services/
│   │       └── email_sender.py  # Envoi emails SendGrid
│   ├── handler.py            # Handler Lambda
│   └── deploy-simple.ps1     # Script de déploiement
└── .gitignore                # Fichiers ignorés par Git
```

## Fichiers Importants à Connaitre

| Fichier | Description |
|---------|-------------|
| `public/auth.js` | Gestion OAuth Google, JWT tokens, connexion utilisateur |
| `public/map_logic.js` | Logique UI principale, formulaires, carte Leaflet |
| `lambda-package/backend/main.py` | Toutes les routes API Flask |
| `lambda-package/backend/auth.py` | Hashage bcrypt, génération JWT |
| `lambda-package/backend/services/email_sender.py` | Templates emails, envoi SendGrid |

## Commandes Utiles

### Déploiement Backend Lambda
```powershell
cd C:\MapEventAI_NEW\frontend\lambda-package
.\deploy-simple.ps1
```

### Vérifier les Logs Lambda (CloudWatch)
```powershell
aws logs tail /aws/lambda/mapevent-backend --since 10m --format short --region eu-west-1
```

### Configuration Lambda
- **Fonction**: `mapevent-backend`
- **Région**: `eu-west-1`
- **Runtime**: Python 3.12
- **Layers**: `psycopg2-py312-mapevent:1`, `bcrypt-layer:3`

## Points d'Attention

1. **Lambda Layers**: bcrypt et psycopg2 sont dans des Lambda Layers, PAS dans le package
2. **Cryptography**: Ne PAS inclure cryptography dans le package (incompatible Windows/Linux)
3. **Taille Package**: Max 50MB pour upload direct, sinon utilise S3
4. **Erreurs CSP (content.js)**: Ce sont des erreurs d'extensions navigateur, IGNORER

## RÈGLE N°1 : UNIQUEMENT OPEN DATA (OBLIGATOIRE)

**JAMAIS importer d'événements depuis des sources non open data.**
**TOUJOURS vérifier la licence AVANT d'importer.**

### Sources AUTORISÉES (licences vérifiées)

| Source | Licence | Type |
|--------|---------|------|
| OpenAgenda (openagenda.com) | Licence Ouverte v1.0 | Events |
| kulturdaten.berlin | CC0 | Events |
| Helsinki LinkedEvents (linkedevents.hel.fi) | CC BY 4.0 | Events |
| Montréal Open Data (donnees.montreal.ca) | CC BY 4.0 | Events |
| Paris Open Data (opendata.paris.fr) | ODbL | Events |
| Madrid Open Data (datos.madrid.es) | CC BY 4.0 | Events |
| Barcelona Open Data (opendata-ajuntament.barcelona.cat) | Open Data | Events |
| NYC Open Data (data.cityofnewyork.us) | Public Domain | Events |
| Toronto Open Data | Open Government License | Events |
| Nantes Métropole Open Data | Open Data | Events |
| Lisbonne Open Data (agendalx.pt via dados.cm-lisboa.pt) | CC BY | Events |
| OSM Calendar (osmcal.org) | Open Source | Events |
| Goabase (goabase.net/api) | API publique, backlink requis | Events électro |
| OpenStreetMap (Overpass API) | ODbL | POI/Lieux |
| opendata.swiss | Conditions d'utilisation ouvertes | Events CH |
| data.stad.gent | Open Data | Events Gand |

### Sources INTERDITES (ne JAMAIS utiliser)

- ❌ Resident Advisor (ra.co) - commercial, CGU interdisent le scraping
- ❌ Ticketmaster - commercial
- ❌ Eventbrite - commercial (sauf API officielle avec accord)
- ❌ Fever (feverup.com) - commercial
- ❌ Eventfrog - commercial
- ❌ UiTdatabank (uitdatabank.be) - propriétaire, accord écrit requis
- ❌ Tout site sans licence ouverte explicite

### Avant d'ajouter une NOUVELLE source
1. **Vérifier la licence** : CC0, CC BY, ODbL, Licence Ouverte, ou mention explicite "free to use"
2. **Documenter la licence** dans ce fichier (tableau ci-dessus)
3. **Si la licence n'est pas claire → NE PAS UTILISER**
4. En cas de doute, chercher les CGU/Terms du site
5. User-Agent transparent: "MapEventAI-Bot/1.0"

### Contenu
- Toujours citer la source originale (source_url = URL directe de l'event)
- **JAMAIS inventer d'URL** → si URL exacte non trouvée, ne pas publier l'event
- Vérifier l'existence réelle de chaque événement
- Descriptions: réécrire si scraping manuel, garder tel quel si open data

### Pointeurs (RUE + VILLE + PAYS) – CRITIQUE
- **Toujours vérifier** que le pointeur correspond à l'adresse : même rue, même ville, même pays
- Seuils : **5m** si adresse avec numéro de rue, **50m** si adresse vague
- Le backend (`event_validator.py`) auto-corrige les coords à l'insertion si le pointeur est trop loin
- Rejeter les résultats Nominatim qui pointent vers une autre ville/pays (ex: "Place du Marché" à Paris au lieu de Lausanne)

### source_url (PUBLICATION ORIGINALE) – CRITIQUE
- **source_url** = URL de la **page dédiée à cet event** uniquement
- Au clic sur "Voir la publication originale", l'utilisateur doit arriver sur **l'event lui-même**, pas sur :
  - ❌ Page d'accueil, page liste/agenda, page titre générique
- Si l'URL exacte de l'event n'est pas trouvée → **ne pas publier** l'event

## État Actuel (2026-02-13)

- ✅ Connexion email/mot de passe fonctionne
- ✅ OAuth Google fonctionne
- ✅ Emails de confirmation avec bouton HTML
- ✅ ~32 800 events sur la carte, TOUS open data
- ✅ Audit légal complet réalisé le 13/02/2026
- ✅ Events non-open-data supprimés (UiTdatabank, RA, Goabase ancien, Eventfrog)
- ✅ Sources : 12+ portails open data vérifiés
- ⚠️ Stripe à configurer (mode live)
- ⚠️ AWS SES : demande d'accès production en cours (Case ID 177071293300718)

## Prochaines Étapes

1. Configurer Stripe en mode live
2. Tester les paiements
3. Attendre approbation AWS SES pour envoi d'emails
4. Continuer à ajouter des sources OPEN DATA uniquement
