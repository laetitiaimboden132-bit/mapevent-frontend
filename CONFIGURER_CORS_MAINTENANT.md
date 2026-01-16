# ✅ Configurer CORS - Vous y êtes !

## 🎯 Vous êtes dans la bonne section

Vous êtes dans **"Partage des ressources entre origines (CORS)"** - parfait !

---

## 📋 Étapes pour configurer CORS

### Étape 1 : Cliquer sur "Modifier"

1. **Vous devriez voir un bouton "Modifier"** (ou "Edit" en anglais)
2. **Cliquez dessus**

### Étape 2 : Coller le JSON

1. **Supprimez tout le contenu** qui est déjà dans la zone de texte (s'il y en a)

2. **Copiez-collez exactement ce code** :

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

3. **Vérifiez** que le code est bien collé (pas d'erreur de formatage)

### Étape 3 : Enregistrer

1. **Cliquez sur "Enregistrer les modifications"** (ou "Save changes" en anglais)
2. **Si AWS vous demande de confirmer** → Cliquez sur "Confirmer" (Confirm)

---

## ✅ C'est fait !

Une fois que vous avez enregistré, CORS est configuré !

---

## 📋 Prochaine étape : Configurer la Bucket Policy

Maintenant, il faut aussi configurer la **"Politique du compartiment"** (Bucket Policy) pour permettre l'accès public.

### Comment faire :

1. **Restez dans l'onglet "Autorisations"**
2. **Descendez un peu** jusqu'à la section **"Politique du compartiment"** (Bucket policy)
3. **Cliquez sur "Modifier"**
4. **Collez ce JSON** :

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

5. **Cliquez sur "Enregistrer les modifications"**

---

## 🧪 Test après configuration

Une fois que vous avez configuré **CORS** ET **Bucket Policy** :

1. **Testez cette URL** dans votre navigateur :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

2. **L'image devrait s'afficher** ✅

---

Dites-moi quand vous avez enregistré CORS, et on configure la Bucket Policy ensuite ! 😊




