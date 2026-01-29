# Configuration CORS pour Lambda Function URL

## Problème résolu
Le doublon `https://mapevent.world, https://mapevent.world` venait du fait que **deux endroits** envoyaient l'en-tête CORS.

## Solution actuelle (IMPORTANTE)

### 1. Code Lambda = N'ENVOIE PAS de headers CORS
Les fichiers `handler.py` et `lambda_function.py` ne doivent **PAS** ajouter d'en-têtes CORS.
C'est la **Function URL AWS** qui les ajoute automatiquement.

### 2. AWS Function URL = SEUL endroit qui envoie CORS

**Configuration dans AWS Console :**

1. **AWS Console** → **Lambda** → fonction **mapevent-backend**
2. **Configuration** → menu de gauche → **Function URL**
3. Clique sur **Edit**
4. Section **Configure cross-origin resource sharing (CORS)** :

| Paramètre | Valeur |
|-----------|--------|
| **Allow origin** | `https://mapevent.world` |
| **Allow methods** | `*` (ou GET, POST, PUT, DELETE, OPTIONS) |
| **Allow headers** | `*` (ou Content-Type, Authorization) |
| **Allow credentials** | **Désactivé** (décoché) |
| **Max age** | `3600` (optionnel) |

5. **Save**

### IMPORTANT : Une seule entrée dans Allow origin
- Mets **exactement** `https://mapevent.world` (pas de virgule, pas de doublon)
- NE PAS ajouter `http://localhost:8000` ici (pour le dev local, utiliser un autre mécanisme)

## Déploiement

Après avoir configuré AWS, déploie le backend :
```powershell
.\deploy-complet.ps1
```

Puis recharge le site : **Ctrl+Shift+R** sur https://mapevent.world

## Vérification
- Plus d'erreur `ne correspond pas à https://mapevent.world, https://mapevent.world`
- Les requêtes API passent avec le bon header CORS (une seule valeur)
