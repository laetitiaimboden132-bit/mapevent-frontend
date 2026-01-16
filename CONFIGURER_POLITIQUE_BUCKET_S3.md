# 🔓 Configurer la politique du bucket S3 pour l'accès public

## ❌ Problème actuel

Vous obtenez `Access Denied` car le bucket n'autorise pas l'accès public en lecture.

## ✅ Solution : Configurer la politique du bucket

### Étape 1 : Aller dans les permissions du bucket

1. **Console AWS** → **S3** → **Bucket `mapevent-avatars`**
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Bucket policy"** (Politique du compartiment)
4. **Cliquez sur "Edit"** (Modifier)

### Étape 2 : Ajouter la politique

1. **Si la politique est vide** : Collez directement le code ci-dessous
2. **Si une politique existe déjà** : Ajoutez le "Statement" dans le tableau "Statement" existant

### Code à copier-coller :

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

### Étape 3 : Enregistrer

1. **Cliquez sur "Save changes"** (Enregistrer les modifications)
2. **Confirmez** si AWS vous demande de confirmer

---

## ⚠️ Important : Vérifier Block Public Access

Avant que la politique fonctionne, il faut vérifier Block Public Access :

### Étape 1 : Aller dans Block Public Access

1. **Dans le bucket** `mapevent-avatars`
2. **Onglet "Permissions"**
3. **Section "Block public access (bucket settings)"** (Bloquer l'accès public)
4. **Cliquez sur "Edit"** (Modifier)

### Étape 2 : Configuration recommandée

**Décochez** (uncheck) les deux premières cases :

- ❌ **Block public access to buckets and objects granted through new access control lists (ACLs)**
- ❌ **Block public access to buckets and objects granted through any access control lists (ACLs)**

**Laissez cochées** (check) les deux dernières :

- ✅ **Block public access to buckets and objects granted through new public bucket or access point policies**
- ✅ **Block public and cross-account access to buckets and objects through any public bucket or access point policies**

**En résumé** :
- Les deux premières : **DÉCOCHÉES** ❌
- Les deux dernières : **COCHÉES** ✅

### Étape 3 : Enregistrer

1. **Cliquez sur "Save changes"** (Enregistrer)
2. **Tapez "confirm"** dans la case de confirmation
3. **Cliquez sur "Confirm"** (Confirmer)

---

## ✅ Vérification

### Test 1 : Tester l'URL directement

1. **Copiez cette URL** :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

2. **Collez-la dans votre navigateur**

3. **L'image devrait maintenant s'afficher** ✅

### Test 2 : Vérifier CORS (si pas encore fait)

1. **Dans le bucket** → **Onglet "Permissions"**
2. **Section "Cross-origin resource sharing (CORS)"**
3. **Cliquez sur "Edit"**
4. **Collez ce JSON** :

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

5. **Cliquez sur "Save changes"**

---

## 🎯 Ordre des opérations

1. ✅ **Configurer Block Public Access** (décocher les 2 premières cases)
2. ✅ **Configurer la politique du bucket** (ajouter le JSON)
3. ✅ **Configurer CORS** (ajouter le JSON)
4. ✅ **Tester l'URL** dans le navigateur
5. ✅ **Vider le cache** du navigateur
6. ✅ **Tester dans l'application**

---

## 🆘 Si ça ne fonctionne toujours pas

### Vérifications supplémentaires :

1. **Vérifiez que vous êtes dans la bonne région** : `eu-west-1` (en haut à droite de la console AWS)

2. **Vérifiez l'orthographe du bucket** : `mapevent-avatars` (avec un tiret)

3. **Attendez 1-2 minutes** : Les changements peuvent prendre un peu de temps à se propager

4. **Vérifiez les logs** : Si l'image ne s'affiche toujours pas, vérifiez les logs CloudWatch pour voir s'il y a des erreurs

---

## 📝 Résumé de la configuration

### Politique du bucket :
- ✅ Autorise l'accès public en lecture (`s3:GetObject`)
- ✅ Uniquement pour le dossier `avatars/*`
- ✅ Pour tous les utilisateurs (`Principal: "*"`)

### Block Public Access :
- ✅ Les ACLs sont autorisées (2 premières cases décochées)
- ✅ Les politiques publiques sont contrôlées (2 dernières cases cochées)

### CORS :
- ✅ Autorise toutes les origines (`*`)
- ✅ Autorise GET et HEAD
- ✅ Expose les headers nécessaires

---

Dites-moi une fois que vous avez fait ces étapes, et on testera ensemble ! 😊




