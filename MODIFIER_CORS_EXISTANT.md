# 🔧 Modifier la configuration CORS existante

## ✅ Vous avez trouvé CORS !
Vous êtes au bon endroit : **"Partage des ressources entre origines (CORS)"**

## 📋 Modifier la configuration

### 1. Cliquer sur "Modifier"
À côté de **"Partage des ressources entre origines (CORS)"**, cliquez sur **"Modifier"**

### 2. Remplacer la configuration actuelle
**SUPPRIMEZ** tout ce qui est dans la zone de texte et **COLLEZ** ceci :

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "ETag",
            "Content-Length",
            "Content-Type"
        ],
        "MaxAgeSeconds": 3600
    }
]
```

### 3. Sauvegarder
- Cliquez sur **"Enregistrer les modifications"** (en bas)

## ⚠️ Changements importants

**Avant :**
- `AllowedOrigins` : seulement `https://mapevent.world`, `localhost:8000`, `localhost:3000`
- `AllowedMethods` : `GET, PUT, POST, DELETE, HEAD` (trop permissif)

**Après :**
- `AllowedOrigins` : `*` (toutes les origines autorisées)
- `AllowedMethods` : seulement `GET, HEAD` (suffisant pour lire les images)

## 🧪 Test après modification

1. Attendez 10-20 secondes (propagation)
2. Rechargez votre site avec **Cmd+Shift+R**
3. Ouvrez la popup compte
4. La photo devrait maintenant s'afficher

## 📋 Si ça ne fonctionne toujours pas

Vérifiez aussi la **"Stratégie de compartiment"** (Bucket policy) :
- Elle doit permettre l'accès public en lecture
- Si elle est vide, ajoutez la politique du guide `CORRIGER_CORS_AVATARS_S3.md`





