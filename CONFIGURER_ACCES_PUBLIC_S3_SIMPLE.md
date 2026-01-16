# 🔓 Configurer l'accès public S3 - Guide simple

## ⚠️ Important : Ne pas utiliser les ACLs

Les ACLs (Access Control Lists) sont désactivées sur votre bucket. **C'est normal !** On va utiliser la **Bucket Policy** à la place.

---

## ✅ Solution en 3 étapes

### Étape 1 : Configurer Block Public Access

1. **Dans le bucket** `mapevent-avatars`
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Block public access (bucket settings)"** (Bloquer l'accès public)
4. **Cliquez sur "Edit"** (Modifier)

5. **Décochez UNIQUEMENT les 2 premières cases** :
   - ❌ **Block public access to buckets and objects granted through new access control lists (ACLs)**
   - ❌ **Block public access to buckets and objects granted through any access control lists (ACLs)**

6. **Laissez COCHÉES les 2 dernières cases** :
   - ✅ **Block public access to buckets and objects granted through new public bucket or access point policies**
   - ✅ **Block public and cross-account access to buckets and objects through any public bucket or access point policies**

7. **Cliquez sur "Save changes"** (Enregistrer)
8. **Tapez "confirm"** dans la case de confirmation
9. **Cliquez sur "Confirm"** (Confirmer)

---

### Étape 2 : Configurer la Bucket Policy

1. **Toujours dans le bucket** `mapevent-avatars`
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Bucket policy"** (Politique du compartiment) - **PAS les ACLs !**
4. **Cliquez sur "Edit"** (Modifier)

5. **Si la politique est vide**, collez ce JSON :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mapevent-avatars/avatars/*"
        }
    ]
}
```

6. **Cliquez sur "Save changes"** (Enregistrer)

7. **AWS peut vous demander de confirmer** - Cliquez sur "Confirm" (Confirmer)

---

### Étape 3 : Configurer CORS

1. **Toujours dans le bucket** `mapevent-avatars`
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Cross-origin resource sharing (CORS)"** (Partage de ressources cross-origin)
4. **Cliquez sur "Edit"** (Modifier)

5. **Collez ce JSON** :

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
        "MaxAgeSeconds": 3600
    }
]
```

6. **Cliquez sur "Save changes"** (Enregistrer)

---

## ✅ Test

### Test 1 : Tester l'URL directement

1. **Copiez cette URL** :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

2. **Collez-la dans votre navigateur**

3. **L'image devrait maintenant s'afficher** ✅

### Test 2 : Dans l'application

1. **Videz le cache du navigateur** :
   - Safari : `Cmd+Option+E` (Mac) ou `Ctrl+Shift+Delete` (Windows)
   - Chrome : `Ctrl+Shift+Delete` puis cochez "Images et fichiers en cache"

2. **Reconnectez-vous avec Google OAuth**

3. **Vérifiez que l'avatar s'affiche** dans le bloc compte

---

## 📋 Résumé : Ce qu'il faut faire

| Étape | Section dans AWS | Action |
|-------|------------------|--------|
| 1 | **Block public access** | Décocher les 2 premières cases |
| 2 | **Bucket policy** | Ajouter le JSON de politique |
| 3 | **CORS** | Ajouter le JSON CORS |

**⚠️ Ne touchez PAS aux ACLs** - Elles sont désactivées, c'est normal !

---

## 🆘 Si ça ne fonctionne toujours pas

### Vérifications :

1. **Vérifiez que vous avez bien enregistré** les 3 configurations
2. **Attendez 1-2 minutes** - Les changements peuvent prendre du temps
3. **Vérifiez la région** : `eu-west-1` (en haut à droite de la console AWS)
4. **Vérifiez l'orthographe** : `mapevent-avatars` (avec un tiret)

### Si l'image s'affiche directement mais pas dans l'application :

- → Problème CORS (vérifiez l'étape 3)
- → Cache du navigateur (videz-le)

---

Dites-moi quand vous avez fait les 3 étapes, et on teste ensemble ! 😊




