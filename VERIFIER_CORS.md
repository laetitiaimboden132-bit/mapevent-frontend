# Vérification des En-têtes CORS

## Description

Le script `verifier-cors.py` vérifie que les en-têtes CORS dans votre code respectent les exigences suivantes :

- **Access-Control-Allow-Origin** : doit être `*` ou `https://mapevent.world`
- **Access-Control-Allow-Headers** : doit contenir au minimum `Content-Type,Authorization`
- **Access-Control-Allow-Methods** : doit contenir `GET,POST,PUT,DELETE,OPTIONS`

## Utilisation

```bash
python verifier-cors.py
```

## Résultat

Le script analyse les fichiers suivants :
- `lambda-package/handler.py`
- `lambda-package/backend/main.py`
- `lambda-package/cors-config.json`

### Exemple de sortie

```
================================================================================
VÉRIFICATION DES EN-TÊTES CORS
================================================================================

Exigences:
  - Access-Control-Allow-Origin: doit être * ou https://mapevent.world
  - Access-Control-Allow-Headers: doit contenir Content-Type, Authorization
  - Access-Control-Allow-Methods: doit contenir GET, POST, PUT, DELETE, OPTIONS

[OK] Tous les en-têtes CORS respectent les exigences!
```

## Vérifications effectuées

### 1. Access-Control-Allow-Origin

Le script vérifie que la valeur est :
- `*` (toutes les origines)
- `https://mapevent.world` (origine spécifique)
- Une variable dynamique (comme `cors_origin`) qui sera vérifiée à l'exécution

### 2. Access-Control-Allow-Headers

Le script vérifie que la liste contient au minimum :
- `Content-Type`
- `Authorization`

Les autres en-têtes sont acceptés en plus.

### 3. Access-Control-Allow-Methods

Le script vérifie que la liste contient au minimum :
- `GET`
- `POST`
- `PUT`
- `DELETE`
- `OPTIONS`

Les autres méthodes sont acceptées en plus.

## Variables dynamiques

Si le script détecte une variable Python (comme `cors_origin`), il indique qu'elle doit être vérifiée à l'exécution. Assurez-vous que ces variables respectent les exigences lors de l'exécution du code.

## Fichiers vérifiés

### handler.py

Le script vérifie tous les endroits où les en-têtes CORS sont définis :
- Réponses `/health`
- Réponses `OPTIONS` (preflight)
- Réponses d'erreur
- Réponses normales

### cors-config.json

Le script vérifie la configuration JSON :
- `AllowOrigins` : doit contenir `*` ou `https://mapevent.world`
- `AllowHeaders` : doit contenir `Content-Type` et `Authorization`
- `AllowMethods` : doit contenir toutes les méthodes requises ou `*`

## Correction des problèmes

Si le script détecte des problèmes, il affiche :
- Le numéro de ligne
- Le nom de l'en-tête
- La valeur actuelle
- Le problème détecté

Corrigez les valeurs dans le code pour respecter les exigences.
