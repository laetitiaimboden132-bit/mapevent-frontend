# 🔧 Configurer CORS sur S3 - Guide étape par étape

## 📋 Prérequis
- Avoir un compte AWS
- Être connecté à la console AWS
- Avoir les droits pour modifier le bucket `mapevent-avatars`

---

## 🎯 Méthode 1 : Via l'interface AWS Console (RECOMMANDÉ)

### Étape 1 : Ouvrir la console S3

1. **Allez sur** : https://console.aws.amazon.com/s3/
2. **Connectez-vous** avec vos identifiants AWS
3. **Sélectionnez la région** : `eu-west-1` (Europe - Irlande)
   - En haut à droite, vérifiez que la région est bien `eu-west-1`
   - Si ce n'est pas le cas, cliquez sur la région et sélectionnez `eu-west-1`

### Étape 2 : Trouver votre bucket

1. Dans la liste des buckets, **cherchez** : `mapevent-avatars`
2. **Cliquez sur le nom du bucket** (pas sur la case à cocher, mais sur le nom lui-même)

### Étape 3 : Accéder aux paramètres CORS

1. Une fois dans le bucket, vous verrez plusieurs **onglets** en haut :
   - Objets
   - Propriétés
   - Permissions
   - Métriques
   - etc.

2. **Cliquez sur l'onglet "Permissions"** (ou "Autorisations" si en français)

3. **Faites défiler vers le bas** jusqu'à la section **"Cross-origin resource sharing (CORS)"**

4. **Cliquez sur "Modifier"** (ou "Edit" en anglais)

### Étape 4 : Configurer CORS

1. Vous verrez un **éditeur de texte JSON**

2. **Supprimez tout le contenu** qui existe déjà (s'il y en a)

3. **Copiez-collez exactement ce code** :

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

4. **Vérifiez** que le code est bien collé (pas d'erreur de formatage)

5. **Cliquez sur "Enregistrer les modifications"** (ou "Save changes" en anglais)

### Étape 5 : Vérifier que ça a fonctionné

1. **Revenez** à la section CORS
2. Vous devriez voir votre configuration affichée
3. **C'est bon !** ✅

---

## 🎯 Méthode 2 : Via PowerShell (si vous préférez)

Si vous préférez utiliser PowerShell, j'ai créé un script automatique.

### Étape 1 : Ouvrir PowerShell

1. Appuyez sur `Windows + X`
2. Sélectionnez **"Windows PowerShell"** ou **"Terminal"**

### Étape 2 : Aller dans le bon dossier

```powershell
cd C:\MapEventAI_NEW\frontend\lambda-package
```

### Étape 3 : Exécuter le script

```powershell
.\configurer-cors-s3.ps1
```

Le script va :
- ✅ Créer la configuration CORS
- ✅ L'appliquer au bucket
- ✅ Vérifier que ça a fonctionné

---

## ✅ Vérification finale

### Test 1 : Vérifier dans la console AWS

1. Retournez dans la console S3
2. Allez dans votre bucket `mapevent-avatars`
3. Onglet **"Permissions"**
4. Section **"Cross-origin resource sharing (CORS)"**
5. Vous devriez voir votre configuration ✅

### Test 2 : Tester l'URL d'une image

1. **Ouvrez votre navigateur** (Safari, Chrome, etc.)
2. **Allez sur** cette URL (remplacez par votre ID utilisateur si différent) :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```

3. **L'image devrait s'afficher** dans le navigateur ✅

### Test 3 : Vérifier les headers CORS

1. **Ouvrez les DevTools** (F12 ou clic droit > Inspecter)
2. **Onglet "Network"** (Réseau)
3. **Rechargez la page** (F5)
4. **Cliquez sur la requête de l'image**
5. **Onglet "Headers"** (En-têtes)
6. **Cherchez dans "Response Headers"** :
   - `Access-Control-Allow-Origin: *` ✅
   - `Access-Control-Allow-Methods: GET, HEAD` ✅

---

## 🆘 Problèmes courants

### Problème 1 : "Vous n'avez pas les permissions"

**Solution** :
- Vérifiez que vous êtes connecté avec le bon compte AWS
- Vérifiez que vous avez les droits `s3:PutBucketCORS`

### Problème 2 : "Erreur de format JSON"

**Solution** :
- Vérifiez que vous avez bien copié tout le JSON
- Vérifiez qu'il n'y a pas d'espaces en trop
- Utilisez un validateur JSON en ligne si besoin

### Problème 3 : "Le bucket n'existe pas"

**Solution** :
- Vérifiez que vous êtes dans la bonne région (`eu-west-1`)
- Vérifiez l'orthographe : `mapevent-avatars` (avec un tiret)

### Problème 4 : "Les images ne se chargent toujours pas"

**Solutions** :
1. **Videz le cache du navigateur** :
   - Safari : `Cmd+Option+E` (Mac) ou `Ctrl+Shift+Delete` (Windows)
   - Chrome : `Ctrl+Shift+Delete` puis cochez "Images et fichiers en cache"

2. **Attendez quelques minutes** : Les changements CORS peuvent prendre 1-2 minutes à se propager

3. **Vérifiez que l'image existe** dans S3 :
   - Console S3 > Bucket `mapevent-avatars` > Dossier `avatars/`
   - Vous devriez voir votre fichier `.jpg`

---

## 📝 Résumé de la configuration CORS

Ce que vous avez configuré :

- ✅ **AllowedOrigins: *** : Autorise toutes les origines (domaines)
- ✅ **AllowedMethods: GET, HEAD** : Autorise la lecture des images
- ✅ **AllowedHeaders: *** : Autorise tous les headers
- ✅ **ExposeHeaders** : Expose les headers nécessaires au navigateur
- ✅ **MaxAgeSeconds: 3600** : Cache la réponse CORS pendant 1 heure

---

## 🎉 C'est terminé !

Une fois CORS configuré :

1. ✅ Videz le cache de votre navigateur
2. ✅ Reconnectez-vous avec Google OAuth
3. ✅ Vérifiez que l'avatar s'affiche correctement

Si vous avez des questions ou des problèmes, dites-moi à quelle étape vous êtes bloqué ! 😊




