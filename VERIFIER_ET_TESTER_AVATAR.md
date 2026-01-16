# ✅ Vérifier et tester l'avatar S3

## 📋 Informations de votre image

- **URL** : `https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg`
- **Taille** : 2.9 Mo
- **Type** : jpg
- **Région** : eu-west-1 ✅

L'image existe bien dans S3 ! Maintenant, vérifions qu'elle est accessible.

---

## 🔍 Étape 1 : Tester l'URL directement

### Test simple dans le navigateur

1. **Copiez cette URL** :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

2. **Collez-la dans la barre d'adresse** de votre navigateur (Safari, Chrome, etc.)

3. **Appuyez sur Entrée**

### Résultats possibles :

- ✅ **L'image s'affiche** → L'image est accessible publiquement, mais il faut vérifier CORS
- ❌ **Erreur "Access Denied"** → Il faut configurer la politique du bucket (voir ci-dessous)
- ❌ **Erreur 404** → L'image n'existe pas (mais vous venez de la voir, donc ce n'est pas ça)

---

## 🔍 Étape 2 : Vérifier CORS

### Dans la console AWS S3 :

1. **Retournez dans votre bucket** `mapevent-avatars`
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Cross-origin resource sharing (CORS)"**
4. **Cliquez dessus** pour voir la configuration

### Ce que vous devriez voir :

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

### Si CORS n'est pas configuré :

- **Cliquez sur "Edit"** (Modifier)
- **Collez le JSON ci-dessus**
- **Cliquez sur "Save changes"** (Enregistrer)

---

## 🔍 Étape 3 : Vérifier la politique du bucket

### Si l'image ne s'affiche pas (Access Denied) :

1. **Dans le bucket** `mapevent-avatars`
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Bucket policy"** (Politique du compartiment)
4. **Cliquez sur "Edit"** (Modifier)

### Si la politique est vide, ajoutez ceci :

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

5. **Cliquez sur "Save changes"** (Enregistrer)

---

## 🔍 Étape 4 : Vérifier Block Public Access

### Important : Vérifier que Block Public Access n'est pas trop restrictif

1. **Dans le bucket** `mapevent-avatars`
2. **Onglet "Permissions"** (Autorisations)
3. **Section "Block public access (bucket settings)"** (Bloquer l'accès public)
4. **Cliquez sur "Edit"** (Modifier)

### Configuration recommandée :

- ✅ **Block all public access** : **DÉSACTIVÉ** (décocher)
- ✅ **Block public access to buckets and objects granted through new access control lists (ACLs)** : **DÉSACTIVÉ**
- ✅ **Block public access to buckets and objects granted through any access control lists (ACLs)** : **DÉSACTIVÉ**
- ⚠️ **Block public access to buckets and objects granted through new public bucket or access point policies** : **ACTIVÉ** (cocher) - OK, car on utilise une politique
- ⚠️ **Block public and cross-account access to buckets and objects through any public bucket or access point policies** : **ACTIVÉ** (cocher) - OK, car on utilise une politique

**En résumé** : Les deux premières cases doivent être **DÉCOCHÉES**, les deux dernières peuvent rester **COCHÉES**.

5. **Cliquez sur "Save changes"** (Enregistrer)

---

## 🧪 Étape 5 : Tester avec les DevTools

### Pour vérifier que CORS fonctionne :

1. **Ouvrez votre site** : https://mapevent.world
2. **Ouvrez les DevTools** (F12 ou clic droit > Inspecter)
3. **Onglet "Network"** (Réseau)
4. **Rechargez la page** (F5)
5. **Cherchez la requête** vers l'image (filtrez par "jpg" ou "avatar")
6. **Cliquez sur la requête**
7. **Onglet "Headers"** (En-têtes)

### Headers à vérifier dans "Response Headers" :

- ✅ `Access-Control-Allow-Origin: *`
- ✅ `Access-Control-Allow-Methods: GET, HEAD`
- ✅ `Access-Control-Expose-Headers: ETag, Content-Length, Content-Type`

### Si ces headers sont absents :

- CORS n'est pas configuré correctement
- Revenez à l'Étape 2

---

## ✅ Checklist finale

Avant de tester dans votre application :

- [ ] L'image s'affiche directement dans le navigateur (URL copiée-collée)
- [ ] CORS est configuré dans le bucket
- [ ] La politique du bucket permet l'accès public en lecture (si nécessaire)
- [ ] Block Public Access est configuré correctement
- [ ] Les headers CORS apparaissent dans les DevTools

---

## 🎯 Test final dans l'application

1. **Videz le cache du navigateur** :
   - Safari : `Cmd+Option+E` (Mac) ou `Ctrl+Shift+Delete` (Windows)
   - Chrome : `Ctrl+Shift+Delete` puis cochez "Images et fichiers en cache"

2. **Reconnectez-vous avec Google OAuth**

3. **Vérifiez que l'avatar s'affiche** dans le bloc compte

---

## 🆘 Si ça ne fonctionne toujours pas

### Vérifications supplémentaires :

1. **Vérifiez l'URL dans le code** :
   - L'URL doit être exactement : `https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg`
   - Vérifiez qu'il n'y a pas d'espaces ou de caractères bizarres

2. **Vérifiez les logs CloudWatch** :
   - L'upload a-t-il réussi ?
   - Y a-t-il des erreurs ?

3. **Testez avec curl** (si vous avez PowerShell) :
   ```powershell
   curl -I https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```
   - Vous devriez voir `HTTP/1.1 200 OK`
   - Et les headers CORS

---

Dites-moi ce que vous obtenez à chaque étape ! 😊




