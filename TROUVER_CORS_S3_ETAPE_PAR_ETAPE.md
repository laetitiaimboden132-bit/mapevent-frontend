# 📍 Trouver CORS dans S3 - Guide Visuel

## ✅ Vous êtes dans le bon bucket
Vous êtes dans : **`mapevent-avatars`** (ou similaire) ✅

## 📋 Étape par étape

### 1. Vérifier que vous êtes dans le bon bucket
- En haut de la page, vous devriez voir : **"mapevent-avatars"** (ou nom similaire)
- Si ce n'est pas le bon, cliquez sur le nom du bucket en haut à gauche

### 2. Trouver l'onglet "Permissions"
En haut de la page, vous voyez plusieurs onglets :
- **Vue d'ensemble** (Overview)
- **Objets** (Objects)
- **Propriétés** (Properties)
- **Permissions** ← **CLIQUEZ ICI** ✅
- **Gestion** (Management)
- **Métriques** (Metrics)

### 3. Dans "Permissions", scroller vers le bas
Vous verrez plusieurs sections :
- **"Paramètres de blocage d'accès public"** (Block public access settings)
- **"Politique de bucket"** (Bucket policy)
- **"Liste de contrôle d'accès (ACL)"** (Access control list)
- **"Cross-origin resource sharing (CORS)"** ← **VOUS ÊTES ICI** ✅

### 4. Cliquer sur "Modifier" (Edit)
À côté de **"Cross-origin resource sharing (CORS)"**, il y a un bouton **"Modifier"** (Edit)
- Cliquez dessus

### 5. Coller la configuration
Dans la zone de texte, collez :

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

### 6. Sauvegarder
- Cliquez sur **"Enregistrer les modifications"** (Save changes) en bas

## 🔍 Si vous ne voyez pas "CORS"

### Option A : Vérifier la région
- En haut à droite, vérifiez que vous êtes dans la bonne région (ex: `eu-west-1`)

### Option B : Vérifier les permissions
- Vous devez avoir les permissions `s3:PutBucketCORS` sur ce bucket

### Option C : Chercher dans "Propriétés"
Parfois CORS peut être dans :
- **Propriétés** (Properties) → **"Hébergement de site web statique"** (Static website hosting)

## 📸 À quoi ça ressemble

```
┌─────────────────────────────────────┐
│ mapevent-avatars                    │
├─────────────────────────────────────┤
│ Vue d'ensemble | Objets | Propriétés│
│ Permissions | Gestion | Métriques   │
├─────────────────────────────────────┤
│                                     │
│ Permissions                         │
│                                     │
│ Paramètres de blocage...           │
│ [Modifier]                          │
│                                     │
│ Politique de bucket                 │
│ [Modifier]                          │
│                                     │
│ Cross-origin resource sharing (CORS)│
│ [Modifier]  ← CLIQUEZ ICI           │
│                                     │
└─────────────────────────────────────┘
```

## 🆘 Si toujours rien

Dites-moi :
1. **Quels onglets** voyez-vous en haut ? (Vue d'ensemble, Objets, etc.)
2. **Dans "Permissions"**, quelles sections voyez-vous ?
3. **Une capture d'écran** serait idéale





