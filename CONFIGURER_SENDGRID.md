# 📧 Configuration SendGrid pour l'envoi d'emails

## ❌ Problème Actuel

Les emails de vérification ne sont pas envoyés car `SENDGRID_API_KEY` n'est pas configurée dans AWS Lambda.

## ✅ Solution : Configurer SendGrid

### 1. Obtenir une clé API SendGrid

1. Aller sur https://app.sendgrid.com/
2. Se connecter ou créer un compte
3. Aller dans **Settings** → **API Keys**
4. Cliquer sur **Create API Key**
5. Donner un nom (ex: "MapEvent Lambda")
6. Sélectionner **Full Access** ou **Restricted Access** avec permissions pour "Mail Send"
7. Copier la clé API (commence par `SG.`)

### 2. Configurer dans AWS Lambda

1. Aller dans **AWS Console** → **Lambda** → Fonction `mapevent-backend`
2. **Configuration** → **Environment variables** → **Edit**
3. Ajouter les variables suivantes :

#### Variables SendGrid

**Variable 1 :**
- **Key** : `SENDGRID_API_KEY`
- **Value** : `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (votre clé API complète)

**Variable 2 :**
- **Key** : `SENDGRID_FROM_EMAIL`
- **Value** : `noreply@mapevent.world` (ou votre email vérifié dans SendGrid)

**Variable 3 :**
- **Key** : `SENDGRID_FROM_NAME`
- **Value** : `MapEvent`

**Variable 4 :**
- **Key** : `FRONTEND_URL`
- **Value** : `https://mapevent.world`

4. Cliquer sur **Save**

### 3. Vérifier l'email expéditeur dans SendGrid

⚠️ **IMPORTANT** : L'email `noreply@mapevent.world` doit être vérifié dans SendGrid :

1. Aller dans **SendGrid** → **Settings** → **Sender Authentication**
2. Vérifier votre domaine `mapevent.world` OU ajouter un Single Sender Verification
3. Si vous utilisez un Single Sender, utilisez cet email dans `SENDGRID_FROM_EMAIL`

### 4. Tester

1. Créer un compte sur https://mapevent.world
2. Choisir "Vérification par email"
3. Vérifier que l'email arrive dans la boîte de réception (et les spams)

## 📋 Checklist

- [ ] Compte SendGrid créé
- [ ] Clé API SendGrid générée
- [ ] `SENDGRID_API_KEY` configurée dans Lambda
- [ ] `SENDGRID_FROM_EMAIL` configurée dans Lambda
- [ ] `SENDGRID_FROM_NAME` configurée dans Lambda
- [ ] `FRONTEND_URL` configurée dans Lambda
- [ ] Email expéditeur vérifié dans SendGrid
- [ ] Test d'envoi d'email réussi

## 🔍 Vérification dans les logs CloudWatch

Après configuration, vérifier les logs CloudWatch :

**Si SendGrid est bien configuré :**
```
✅ Email envoyé avec succès à user@example.com
✅ SendGrid message ID: xxxxxx
```

**Si SendGrid n'est pas configuré :**
```
❌ SENDGRID_API_KEY non configurée - Vérifiez les variables d'environnement Lambda
   SENDGRID_API_KEY vide: True
```

## 💡 Plan SendGrid Gratuit

SendGrid offre un plan gratuit avec :
- **100 emails/jour** (suffisant pour les tests)
- **40 000 emails/mois** (suffisant pour démarrer)

Pour plus d'emails, passer à un plan payant.
