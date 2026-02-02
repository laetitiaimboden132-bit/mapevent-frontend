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

## État Actuel (2026-02-02)

- ✅ Connexion email/mot de passe fonctionne
- ✅ OAuth Google fonctionne
- ✅ Emails de confirmation avec bouton HTML
- ⚠️ Stripe à configurer (mode live)

## Prochaines Étapes

1. Configurer Stripe en mode live
2. Tester les paiements
