# 🔍 DIAGNOSTIC : ERREUR 500 LORS DE LA CONNEXION

## ❌ PROBLÈME

Lors de la tentative de connexion, vous obtenez une erreur **500 (Erreur interne du serveur)**.

---

## 🔍 CAUSES POSSIBLES

### 1. **Problème avec l'endpoint `/api/auth/login`**

L'endpoint peut avoir un problème. Vérifiez :
- Que l'endpoint existe bien
- Que la base de données est accessible
- Que les variables d'environnement sont correctement configurées

### 2. **Problème avec la base de données**

- La connexion à RDS peut échouer
- La table `users` ou `user_passwords` peut ne pas exister
- Les colonnes nécessaires peuvent manquer

### 3. **Problème avec bcrypt**

- bcrypt peut ne pas être installé dans Lambda
- L'import peut échouer

### 4. **Problème avec les identifiants**

- Vous avez utilisé les valeurs d'exemple au lieu de vos vrais identifiants
- Votre compte peut ne pas exister

---

## ✅ SOLUTIONS

### Solution 1 : Tester la connexion d'abord

Utilisez le script de test pour diagnostiquer :

```powershell
.\test-connexion-api.ps1 -Email "votre-vrai-email@example.com" -Password "votre-vrai-mot-de-passe"
```

**⚠️ IMPORTANT :** Remplacez par vos **vrais identifiants**, pas les valeurs d'exemple !

### Solution 2 : Vérifier que votre compte existe

Si vous n'avez pas encore de compte administrateur, vous devez d'abord en créer un avec le rôle "director" ou "admin".

### Solution 3 : Utiliser l'endpoint directement

Si le script ne fonctionne pas, vous pouvez tester l'endpoint directement :

```powershell
$body = @{
    email = "votre-vrai-email@example.com"
    password = "votre-vrai-mot-de-passe"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## 🆘 SI VOUS N'AVEZ PAS DE COMPTE ADMINISTRATEUR

Si vous n'avez pas encore de compte avec le rôle "director" ou "admin", vous devez :

1. **Créer un compte normal** via l'interface web
2. **Modifier le rôle dans la base de données** pour le mettre à "director" ou "admin"

Ou utiliser l'endpoint admin pour créer un compte administrateur directement.

---

## 📋 CHECKLIST

- [ ] J'ai utilisé mes **vrais identifiants** (pas les valeurs d'exemple)
- [ ] Mon compte existe dans la base de données
- [ ] Mon compte a le rôle "director" ou "admin"
- [ ] L'API est accessible
- [ ] La base de données RDS est accessible
- [ ] bcrypt est installé dans Lambda

---

## 🎯 PROCHAINE ÉTAPE

1. **Testez d'abord** avec le script de diagnostic :
   ```powershell
   .\test-connexion-api.ps1 -Email "votre-vrai-email@example.com" -Password "votre-vrai-mot-de-passe"
   ```

2. **Si ça fonctionne**, utilisez le token obtenu :
   ```powershell
   .\supprimer-tous-comptes.ps1 -JwtToken "token-obtenu" -Confirm "OUI"
   ```

3. **Si ça ne fonctionne pas**, vérifiez les logs Lambda dans CloudWatch pour voir l'erreur exacte.
