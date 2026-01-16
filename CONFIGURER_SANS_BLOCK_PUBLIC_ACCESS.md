# ✅ Configurer S3 sans modifier Block Public Access

## 🎯 Solution simple : Commencer par la Bucket Policy

Si le bouton "Modifier" est grisé pour Block Public Access, **commencez par configurer la Bucket Policy**.

---

## Étape 1 : Configurer la Bucket Policy

1. **Console AWS** → **S3** → **Bucket `mapevent-avatars`**
2. **Onglet "Autorisations"** (Permissions)
3. **Section "Politique du compartiment"** (Bucket policy)
4. **Cliquez sur "Modifier"** (Edit)

5. **Collez ce JSON** :

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

6. **Cliquez sur "Enregistrer les modifications"** (Save changes)

7. **Si AWS vous demande de confirmer** → Cliquez sur "Confirmer" (Confirm)

---

## Étape 2 : Configurer CORS

1. **Toujours dans le bucket** `mapevent-avatars`
2. **Onglet "Autorisations"**
3. **Section "Partage de ressources cross-origin (CORS)"** (Cross-origin resource sharing)
4. **Cliquez sur "Modifier"** (Edit)

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

6. **Cliquez sur "Enregistrer les modifications"** (Save changes)

---

## Étape 3 : Tester

### Test 1 : URL directe

1. **Copiez cette URL** :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

2. **Collez-la dans votre navigateur**

3. **Résultat** :
   - ✅ **L'image s'affiche** → Parfait ! Passez au test dans l'application
   - ❌ **Toujours "Access Denied"** → Il faut modifier Block Public Access (voir guide de dépannage)

---

## ⚠️ Si l'image ne s'affiche toujours pas

Cela signifie que **Block Public Access bloque les politiques publiques**.

**Solutions** :

1. **Demander à l'administrateur AWS** de modifier Block Public Access
2. **Utiliser AWS CLI** (si vous avez les permissions) :
   ```powershell
   aws s3api put-public-access-block `
       --bucket mapevent-avatars `
       --region eu-west-1 `
       --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
   ```

---

## ✅ Si l'image s'affiche

1. **Videz le cache du navigateur**
2. **Reconnectez-vous avec Google OAuth**
3. **Vérifiez que l'avatar s'affiche** dans l'application

---

Dites-moi ce que vous obtenez après avoir configuré la Bucket Policy ! 😊




