# 🧪 Comment Tester l'Envoi d'Emails SendGrid

## 🎯 Test Manuel (Recommandé - Le Plus Simple)

### Étape 1 : Créer un Nouveau Compte via Google OAuth

1. **Ouvrez votre site** :
   - Allez sur : https://mapevent.world (ou votre URL de production)
   - Ou ouvrez en local si vous testez en développement

2. **Déconnectez-vous** (si vous êtes déjà connecté) :
   - Cliquez sur votre bloc compte
   - Cliquez sur "Se déconnecter"

3. **Créez un nouveau compte** :
   - Cliquez sur "Compte" (ou le bouton de connexion)
   - Cliquez sur "Connexion avec Google"
   - **Utilisez un email de test** que vous pouvez vérifier facilement
   - Suivez les étapes de connexion Google

4. **Si le profil n'est pas complet** :
   - Vous devriez voir un formulaire (photo manquante, etc.)
   - **OU** vous devriez voir le modal de vérification email directement

### Étape 2 : Vérifier l'Email de Confirmation

1. **Ouvrez votre boîte email** (celui utilisé pour créer le compte)
2. **Cherchez un email** avec :
   - **Expéditeur** : `noreply@mapevent.world` ou `MapEvent`
   - **Sujet** : `Votre code de vérification MapEventAI`
3. **Dans l'email, vous devriez voir** :
   - Un code à 6 chiffres (ex: `123456`)
   - Le texte : "Ce code est valide pendant 15 minutes"
   - Les instructions pour confirmer votre email

### Étape 3 : Vérifier les Logs Lambda

Si l'email n'arrive pas, vérifiez les logs :

```powershell
# Afficher les logs récents (5 dernières minutes)
aws logs tail /aws/lambda/mapevent-backend --since 5m --region eu-west-1 --format short

# Chercher spécifiquement les logs d'email
aws logs tail /aws/lambda/mapevent-backend --since 10m --region eu-west-1 --format short | Select-String -Pattern "email|Email|SENDGRID|verification|confirmation"
```

**Ce que vous devriez voir dans les logs** :
- ✅ `Email envoyé avec succès à ...` = **Ça fonctionne !**
- ❌ `SENDGRID_API_KEY non configurée` = Problème de configuration
- ❌ `Erreur envoi email: 401` = Clé API invalide
- ❌ `Erreur envoi email: 403` = Compte SendGrid non vérifié

---

## 🧪 Test Automatique (Avancé)

Si vous voulez tester directement l'envoi d'email sans créer un compte, vous pouvez utiliser ce script :

### Script PowerShell de Test

```powershell
# test-email-sendgrid.ps1
# Remplacez VOTRE_EMAIL par votre email de test
$EMAIL_TEST = "votre-email@example.com"

Write-Host "Envoi d'un email de test..." -ForegroundColor Cyan

$body = @{
    email = $EMAIL_TEST
    name = "Test User"
    sub = "test-sub-$(Get-Random)"
} | ConvertTo-Json

# Appeler l'endpoint OAuth Google (cela créera un compte et enverra un email)
$response = Invoke-RestMethod -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

Write-Host "Réponse:" -ForegroundColor Green
$response | ConvertTo-Json -Depth 10

Write-Host "`nVérifiez votre email: $EMAIL_TEST" -ForegroundColor Yellow
```

**⚠️ ATTENTION** : Ce script créera un compte dans votre base de données ! Utilisez-le seulement pour des tests.

---

## 🔍 Vérifier que SendGrid Fonctionne

### Vérifier dans SendGrid Dashboard

1. **Connectez-vous à SendGrid** : https://app.sendgrid.com/
2. **Allez dans** : **Activity** (Activité) dans le menu de gauche
3. **Vous devriez voir** :
   - Les emails envoyés (si l'envoi fonctionne)
   - Les emails en attente
   - Les emails échoués (si erreur)

### Vérifier les Statistiques SendGrid

1. **Dans SendGrid**, allez dans **Stats** (Statistiques)
2. **Vous devriez voir** :
   - Nombre d'emails envoyés aujourd'hui
   - Nombre d'emails délivrés
   - Taux de rebond

---

## ❌ Dépannage

### Problème 1 : Email non reçu

**Solutions** :
1. Vérifiez les **spams** (emails de test vont souvent dans les spams)
2. Vérifiez les **logs Lambda** (voir ci-dessus)
3. Vérifiez que **SendGrid est bien configuré** dans Lambda
4. Vérifiez que votre **compte SendGrid est vérifié** (identité confirmée)

### Problème 2 : "SENDGRID_API_KEY non configurée" dans les logs

**Solution** :
1. Vérifiez dans AWS Lambda Console que `SENDGRID_API_KEY` est bien présente
2. Vérifiez qu'il n'y a pas d'espaces avant/après la clé
3. Attendez 1-2 minutes après modification (propagation)

### Problème 3 : "Erreur envoi email: 401 Unauthorized"

**Solution** :
1. Vérifiez que votre clé API SendGrid est correcte
2. Vérifiez que la clé API n'a pas été supprimée dans SendGrid
3. Créez une nouvelle clé API si nécessaire

### Problème 4 : "Erreur envoi email: 403 Forbidden"

**Solution** :
1. Vérifiez que votre compte SendGrid est **vérifié** (identité confirmée)
2. Vérifiez que vous n'avez pas dépassé la limite d'emails (100/jour en gratuit)
3. Vérifiez que votre domaine est vérifié (pour les emails avec votre domaine)

### Problème 5 : Email reçu mais dans les spams

**Solution** :
1. C'est **normal** pour les emails de test
2. Ajoutez `noreply@mapevent.world` à vos contacts
3. Pour la production, configurez SPF, DKIM et DMARC pour votre domaine

---

## ✅ Checklist de Test

- [ ] Compte SendGrid créé et vérifié
- [ ] Clé API SendGrid configurée dans Lambda (sans espaces)
- [ ] Nouveau compte créé via Google OAuth
- [ ] Email de confirmation reçu
- [ ] Code à 6 chiffres visible dans l'email
- [ ] Logs Lambda montrent "Email envoyé avec succès"
- [ ] Activity SendGrid montre l'email envoyé

---

## 🎉 C'est Prêt !

Une fois que vous recevez l'email de confirmation, c'est que tout fonctionne correctement ! 🎊
