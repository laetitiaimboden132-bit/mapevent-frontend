# 🧪 Test de la Solution S3 pour les Avatars

## ✅ Déploiement Terminé

Le code avec support S3 a été déployé dans Lambda.

## 🧪 Tests à Effectuer

### 1. Test de Connexion OAuth Google

1. Aller sur https://mapevent.world
2. Se connecter avec **OAuth Google**
3. Vérifier que la connexion fonctionne

### 2. Vérifier les Logs CloudWatch

1. **AWS Console > Lambda > `mapevent-backend`**
2. Onglet **"Monitor"** > **"View CloudWatch logs"**
3. Chercher dans les logs récents :
   - `✅ Avatar uploadé vers S3` (succès)
   - `⚠️ Erreur upload avatar vers S3` (erreur à corriger)

### 3. Vérifier dans S3

```bash
aws s3 ls s3://mapevent-avatars/avatars/
```

Vous devriez voir un fichier comme :
```
avatars/user_1234567890_abc123.jpg
```

### 4. Vérifier la Base de Données

L'URL S3 devrait être stockée dans `profile_photo_url` :
- Format attendu : `https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_xxx.jpg`
- **PAS** de base64 volumineuse

### 5. Vérifier l'Affichage

- L'avatar devrait s'afficher correctement dans l'interface
- Le bouton compte devrait montrer la photo de profil

## 🎯 Résultats Attendus

### ✅ Succès si vous voyez :

1. **Logs CloudWatch** :
   ```
   ✅ Avatar uploadé vers S3 et sauvegardé dans DB: https://mapevent-avatars.s3.eu-west-1.amazonaws.com/avatars/user_xxx.jpg
   ```

2. **S3** :
   ```
   avatars/user_xxx.jpg
   ```

3. **Réponse JSON** :
   - Taille < 10KB (au lieu de 11.78MB)
   - `profile_photo_url` contient une URL S3

4. **Interface** :
   - Avatar s'affiche correctement
   - Pas d'erreur dans la console

### ❌ Problèmes Possibles

1. **Erreur "Access Denied" dans les logs** :
   - Vérifier les permissions IAM Lambda pour S3

2. **Erreur "Bucket not found"** :
   - Vérifier que `S3_AVATARS_BUCKET=mapevent-avatars` est bien configuré

3. **Avatar ne s'affiche pas** :
   - Vérifier CORS dans S3
   - Vérifier que l'URL S3 est accessible publiquement

## 📊 Checklist de Test

- [ ] Connexion OAuth Google réussie
- [ ] Logs CloudWatch montrent l'upload S3
- [ ] Fichier présent dans S3
- [ ] URL S3 dans la base de données
- [ ] Réponse JSON < 10KB
- [ ] Avatar s'affiche dans l'interface

## 🆘 En Cas de Problème

Si vous voyez des erreurs, envoyez-moi :
1. Les logs CloudWatch (dernières 50 lignes)
2. Le résultat de `aws s3 ls s3://mapevent-avatars/avatars/`
3. La taille de la réponse JSON lors de la connexion






