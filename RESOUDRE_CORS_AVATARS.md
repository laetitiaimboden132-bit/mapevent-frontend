# 🔧 Résoudre le problème CORS pour les avatars S3

## Problème
Les images d'avatar depuis S3 sont bloquées avec l'erreur `OpaqueResponseBlocking` dans la console du navigateur.

## Solution

### Étape 1: Vérifier la configuration actuelle

Exécutez le script de vérification :

```powershell
cd lambda-package
.\verifier-bucket-s3.ps1
```

Ce script va vérifier :
- ✅ Si le bucket existe
- ✅ La configuration CORS actuelle
- ✅ La politique du bucket
- ✅ Le Block Public Access
- ✅ L'accès à un fichier de test

### Étape 2: Configurer CORS

Exécutez le script de configuration CORS :

```powershell
cd lambda-package
.\configurer-cors-s3.ps1
```

Ce script va :
- ✅ Configurer CORS avec `AllowedOrigins: *`
- ✅ Autoriser les méthodes `GET` et `HEAD`
- ✅ Exposer les headers nécessaires (`ETag`, `Content-Length`, `Content-Type`)

### Étape 3: Vérifier la politique du bucket

Si le bucket n'a pas de politique permettant l'accès public en lecture, créez-en une :

```powershell
# Créer une politique permettant l'accès public en lecture
$POLICY = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Sid = "PublicReadGetObject"
            Effect = "Allow"
            Principal = "*"
            Action = "s3:GetObject"
            Resource = "arn:aws:s3:::mapevent-avatars/avatars/*"
        }
    )
} | ConvertTo-Json -Depth 10

$POLICY | Out-File -FilePath "bucket-policy.json" -Encoding UTF8

aws s3api put-bucket-policy --bucket mapevent-avatars --policy file://bucket-policy.json --region eu-west-1
```

### Étape 4: Vérifier Block Public Access

Assurez-vous que Block Public Access n'est pas activé pour les politiques publiques :

```powershell
# Vérifier la configuration actuelle
aws s3api get-public-access-block --bucket mapevent-avatars --region eu-west-1

# Si BlockPublicPolicy est activé, désactivez-le (si nécessaire)
aws s3api put-public-access-block `
    --bucket mapevent-avatars `
    --region eu-west-1 `
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

⚠️ **Attention**: Désactiver Block Public Access peut exposer votre bucket. Assurez-vous que seule la lecture publique est autorisée via la politique.

### Étape 5: Tester dans le navigateur

1. **Vider le cache du navigateur** :
   - Safari : `Cmd+Option+E` (Mac) ou `Ctrl+Shift+Delete` (Windows)
   - Chrome : `Ctrl+Shift+Delete` (Windows) ou `Cmd+Shift+Delete` (Mac)

2. **Tester l'URL directement** :
   ```
   https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```
   
   Cette URL devrait :
   - ✅ Charger l'image dans le navigateur
   - ✅ Afficher les headers CORS dans les DevTools (Network > Headers)

3. **Vérifier les headers CORS** :
   - Ouvrez les DevTools (F12)
   - Onglet Network
   - Rechargez la page
   - Cliquez sur la requête de l'image
   - Vérifiez les headers de réponse :
     - `Access-Control-Allow-Origin: *`
     - `Access-Control-Allow-Methods: GET, HEAD`
     - `Access-Control-Expose-Headers: ETag, Content-Length, Content-Type`

### Étape 6: Vérifier le code frontend

Le code frontend a été mis à jour pour :
- ✅ Ajouter `crossorigin="anonymous"` à toutes les images de profil
- ✅ Gérer les erreurs de chargement d'image avec fallback vers l'emoji avatar

## Dépannage

### Si CORS est configuré mais les images ne se chargent toujours pas

1. **Vérifier que l'image existe dans S3** :
   ```powershell
   aws s3 ls s3://mapevent-avatars/avatars/ --region eu-west-1
   ```

2. **Tester l'URL avec curl** :
   ```powershell
   curl -I https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg
   ```
   
   Vérifiez que les headers CORS sont présents dans la réponse.

3. **Vérifier les logs CloudWatch** :
   - Vérifiez si l'upload vers S3 a réussi
   - Vérifiez s'il y a des erreurs lors de l'upload

### Si l'image n'existe pas dans S3

1. **Vérifier les logs backend** :
   - L'upload a-t-il réussi ?
   - Y a-t-il des erreurs dans `s3_service.py` ?

2. **Tester l'upload manuellement** :
   - Connectez-vous avec Google OAuth
   - Vérifiez les logs CloudWatch pour voir si l'upload a lieu

## Résumé des changements

### Code modifié
- ✅ `public/map_logic.js` : Ajout de `crossorigin="anonymous"` à toutes les images de profil
- ✅ Gestion d'erreur améliorée avec fallback vers emoji avatar

### Scripts créés
- ✅ `lambda-package/configurer-cors-s3.ps1` : Configure CORS sur le bucket
- ✅ `lambda-package/verifier-bucket-s3.ps1` : Vérifie la configuration du bucket

## Prochaines étapes

1. Exécutez les scripts de configuration
2. Videz le cache du navigateur
3. Testez la connexion Google OAuth
4. Vérifiez que l'avatar s'affiche correctement




