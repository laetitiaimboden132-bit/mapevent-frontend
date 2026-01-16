# 📧 Comment Obtenir et Configurer la Clé SendGrid (SENDGRID_API_KEY)

## 🎯 À Quoi Sert SendGrid ?

SendGrid est utilisé pour **envoyer les emails de confirmation** aux nouveaux utilisateurs qui créent un compte via Google OAuth.

**Important** : Si vous ne configurez pas `SENDGRID_API_KEY`, les emails de confirmation ne seront **pas envoyés**, mais le système continuera de fonctionner. Les utilisateurs pourront quand même créer des comptes.

---

## 📋 Étape 1 : Créer un Compte SendGrid (GRATUIT)

### Option A : Compte Gratuit (100 emails/jour)

1. **Allez sur** : https://signup.sendgrid.com/
2. **Remplissez le formulaire** :
   - Email
   - Mot de passe
   - Nom de votre entreprise : `MapEvent`
   - Cliquez sur **"Create Account"**

3. **Vérifiez votre email** :
   - Vous recevrez un email de confirmation
   - Cliquez sur le lien pour activer votre compte

4. **Complétez votre profil** :
   - Renseignez vos informations
   - Acceptez les conditions d'utilisation

5. **Vérifiez votre identité** (obligatoire pour envoyer des emails) :
   - Option 1 : Vérification par email (rapide)
   - Option 2 : Vérification par téléphone
   - Suivez les instructions sur l'écran

---

## 🔑 Étape 2 : Créer une Clé API SendGrid

### 1. Connectez-vous à SendGrid

- Allez sur : https://app.sendgrid.com/
- Connectez-vous avec votre compte

### 2. Accédez aux API Keys

- Dans le menu de gauche, cliquez sur **"Settings"** (Paramètres)
- Cliquez sur **"API Keys"** (Clés API)

### 3. Créer une Nouvelle Clé API

1. Cliquez sur le bouton **"Create API Key"** (Créer une clé API)
2. Choisissez un **nom** pour votre clé :
   - Exemple : `MapEvent-Lambda-Email`
3. Choisissez les **permissions** :
   - **"Full Access"** (Accès complet) - **RECOMMANDÉ pour commencer**
   - OU **"Restricted Access"** (Accès restreint) :
     - Cochez uniquement **"Mail Send"** > **"Full Access"**
4. Cliquez sur **"Create & View"** (Créer et voir)

### 4. COPIER LA CLÉ API

⚠️ **IMPORTANT** : La clé API ne s'affichera **qu'une seule fois** !

1. **COPIEZ IMMÉDIATEMENT** la clé API (elle ressemble à : `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
2. **SAUVEGARDEZ-LA** dans un endroit sûr (fichier texte, gestionnaire de mots de passe, etc.)
3. **Si vous fermez cette page sans copier**, vous devrez créer une nouvelle clé !

Exemple de clé API :
```
SG.1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890
```

---

## ☁️ Étape 3 : Configurer dans AWS Lambda

### Méthode 1 : Via AWS Console (Recommandé - Plus Simple)

1. **Ouvrez AWS Console** :
   - Allez sur : https://console.aws.amazon.com/
   - Connectez-vous avec votre compte AWS

2. **Accédez à Lambda** :
   - Dans la barre de recherche en haut, tapez : `Lambda`
   - Cliquez sur **"Lambda"**

3. **Sélectionnez votre fonction** :
   - Cliquez sur **"mapevent-backend"**

4. **Accédez aux Variables d'environnement** :
   - Dans le menu de gauche, cliquez sur **"Configuration"** (Configuration)
   - Cliquez sur **"Environment variables"** (Variables d'environnement)

5. **Ajouter la clé SENDGRID_API_KEY** :
   - Cliquez sur le bouton **"Edit"** (Modifier)
   - Cliquez sur **"Add environment variable"** (Ajouter une variable d'environnement)
   - Dans le champ **"Key"** (Clé), tapez : `SENDGRID_API_KEY`
   - Dans le champ **"Value"** (Valeur), **COLLEZ** votre clé API SendGrid (celle que vous avez copiée à l'étape 2)
   - Cliquez sur **"Save"** (Sauvegarder)

6. **Vérification** :
   - Vous devriez voir dans la liste :
     ```
     SENDGRID_API_KEY = SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

### Méthode 2 : Via AWS CLI (Pour les utilisateurs avancés)

```powershell
# Remplacez VOTRE_CLE_SENDGRID par votre vraie clé API
$SENDGRID_KEY = "SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

aws lambda update-function-configuration `
    --function-name mapevent-backend `
    --region eu-west-1 `
    --environment "Variables={
        SENDGRID_API_KEY=$SENDGRID_KEY,
        RDS_HOST=mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com,
        RDS_PORT=5432,
        RDS_DB=mapevent,
        RDS_USER=postgres,
        RDS_PASSWORD=666666Laeti69!,
        REDIS_HOST=mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com,
        REDIS_PORT=6379,
        FLASK_ENV=production,
        JWT_SECRET=123ef56105a52cf1f84a551ff1bdbf195fe3025a5f8a6e13255ef146e3a002d4,
        S3_AVATARS_BUCKET=mapevent-avatars,
        GOOGLE_CLOUD_VISION_API_KEY=,
        STRIPE_SECRET_KEY=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,
        STRIPE_PUBLIC_KEY=pk_live_51Sfg8g2YO5zMBO7yRz2yRw9SZMJhYY8bfxLYT7v6VgQ77lFFwaUOGa5WYD1h7SDUgNkyABKnGFu3KN5p4PwT1Eqr00CisIZv67,
        STRIPE_WEBHOOK_SECRET=whsec_Mt6JWeZcpEAyH1fzl2D4ucOYUi8RlKYz
    }"
```

⚠️ **ATTENTION** : Cette méthode remplace **TOUTES** les variables d'environnement ! Assurez-vous d'inclure toutes les variables existantes.

---

## ✅ Étape 4 : Vérifier que ça Fonctionne

### Vérifier dans AWS Lambda

1. Retournez dans **Lambda** > **mapevent-backend** > **Configuration** > **Environment variables**
2. Vérifiez que `SENDGRID_API_KEY` apparaît dans la liste
3. Vérifiez que la valeur commence par `SG.` et fait environ 69 caractères

### Tester l'envoi d'email

1. **Créez un nouveau compte** via Google OAuth sur votre site
2. **Vérifiez votre email** (celui utilisé lors de la création du compte)
3. **Vous devriez recevoir un email** avec le sujet : **"Votre code de vérification MapEventAI"**
4. **L'email contient** :
   - Un code à 6 chiffres
   - Les instructions pour confirmer votre adresse email

### Vérifier les logs Lambda

Si les emails ne sont pas envoyés, vérifiez les logs :

```powershell
# Afficher les logs récents
aws logs tail /aws/lambda/mapevent-backend --since 5m --region eu-west-1 --format short
```

Recherchez dans les logs :
- ✅ `Email envoyé avec succès à ...` = Ça fonctionne !
- ❌ `SENDGRID_API_KEY non configurée` = La clé n'est pas configurée
- ❌ `Erreur envoi email` = Problème avec SendGrid (vérifiez votre compte)

---

## 💰 Coûts SendGrid

### Plan Gratuit (Free)
- **100 emails/jour** (gratuit)
- **Infinite** (illimité) : À partir de 15€/mois
- **Essentials** : À partir de 20€/mois
- **Pro** : À partir de 90€/mois

**Pour commencer, le plan gratuit (100 emails/jour) est largement suffisant !**

---

## 🔒 Sécurité

### ⚠️ IMPORTANT : Protégez votre clé API

1. **Ne partagez JAMAIS** votre clé API SendGrid
2. **Ne commitez JAMAIS** la clé dans Git
3. **Ne la mettez JAMAIS** dans le code source
4. **Utilisez uniquement** les variables d'environnement Lambda

### Si votre clé API est compromise

1. **Allez sur SendGrid** > **Settings** > **API Keys**
2. **Supprimez l'ancienne clé** compromise
3. **Créez une nouvelle clé API**
4. **Mettez à jour** la variable d'environnement Lambda avec la nouvelle clé

---

## 🆘 Dépannage

### Problème 1 : "SENDGRID_API_KEY non configurée"

**Solution** :
- Vérifiez que la variable est bien ajoutée dans Lambda
- Vérifiez que le nom est exactement : `SENDGRID_API_KEY` (en majuscules)
- Attendez 1-2 minutes après la configuration (propagation)

### Problème 2 : "Erreur envoi email: 401 Unauthorized"

**Solution** :
- Vérifiez que votre clé API est correcte
- Vérifiez que votre compte SendGrid est vérifié
- Vérifiez que la clé API n'a pas été supprimée dans SendGrid

### Problème 3 : "Erreur envoi email: 403 Forbidden"

**Solution** :
- Vérifiez que votre compte SendGrid est vérifié (identité confirmée)
- Vérifiez que vous n'avez pas dépassé la limite d'emails (100/jour en gratuit)

### Problème 4 : Les emails partent dans les spams

**Solution** :
- Vérifiez votre domaine dans SendGrid
- Configurez SPF, DKIM et DMARC pour votre domaine
- Contactez le support SendGrid pour l'authentification du domaine

---

## 📚 Ressources Utiles

- **Documentation SendGrid** : https://docs.sendgrid.com/
- **Guide API Keys** : https://docs.sendgrid.com/ui/account-and-settings/api-keys
- **Limites SendGrid** : https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/api-keys

---

## ✅ Checklist Finale

- [ ] Compte SendGrid créé et vérifié
- [ ] Clé API SendGrid créée et copiée
- [ ] Variable `SENDGRID_API_KEY` ajoutée dans AWS Lambda
- [ ] Vérification dans Lambda Console que la clé est présente
- [ ] Test d'envoi d'email effectué
- [ ] Email de confirmation reçu
- [ ] Code de vérification fonctionnel

---

## 🎉 C'est Prêt !

Une fois configuré, tous les nouveaux utilisateurs qui créent un compte via Google OAuth recevront automatiquement un email de confirmation avec un code à 6 chiffres pour vérifier leur adresse email.
