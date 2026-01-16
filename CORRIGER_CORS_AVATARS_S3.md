# 🔧 Corriger CORS pour les avatars S3

## ❌ Problème
Les images d'avatars depuis S3 sont bloquées :
- `NS_BINDING_ABORTED`
- `OpaqueResponseBlocking`
- La photo de profil ne s'affiche pas

## ✅ Solution : Configurer CORS sur le bucket S3

### Étape 1 : Aller dans S3
1. AWS Console → **S3**
2. Trouver le bucket : **`mapevent-avatars`**
3. Cliquer sur le bucket

### Étape 2 : Configurer CORS
1. Aller dans l'onglet **"Permissions"** (Autorisations)
2. Scroller jusqu'à **"Cross-origin resource sharing (CORS)"**
3. Cliquer sur **"Modifier"** (Edit)

### Étape 3 : Ajouter la configuration CORS
Coller cette configuration :

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

### Étape 4 : Sauvegarder
1. Cliquer sur **"Enregistrer les modifications"** (Save changes)
2. Attendre quelques secondes

### Étape 5 : Vérifier la politique du bucket
1. Toujours dans **"Permissions"**
2. **"Politique de bucket"** (Bucket policy)
3. Vérifier qu'elle contient :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mapevent-avatars/*"
        }
    ]
}
```

Si elle n'existe pas, l'ajouter.

### Étape 6 : Vérifier les paramètres de blocage d'accès public
1. Toujours dans **"Permissions"**
2. **"Paramètres de blocage d'accès public"** (Block public access settings)
3. Cliquer sur **"Modifier"**
4. **DÉSACTIVER** tous les blocages (ou au moins "Bloquer l'accès public et les objets ACL publics")
5. **Enregistrer**

## 🧪 Test
1. Rechargez votre site (Cmd+Shift+R)
2. Ouvrez la popup compte
3. La photo de profil devrait maintenant s'afficher

## 📋 Si ça ne fonctionne toujours pas

Vérifiez que l'URL de l'avatar est correcte :
- Dans la console (F12), onglet **Network**
- Cherchez les requêtes vers `mapevent-avatars.s3.eu-west-1.amazonaws.com`
- Vérifiez le code de réponse :
  - **200** = OK
  - **403** = Permissions manquantes
  - **404** = Fichier n'existe pas
  - **CORS error** = CORS mal configuré





