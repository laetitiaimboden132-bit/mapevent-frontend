# 🔐 Corriger le Code de Sécurité Google au lieu de la Confirmation Smartphone

## ❌ Problème

Vous recevez maintenant un **code de sécurité** à entrer au lieu de la **confirmation sur smartphone** ("Oui, c'est moi").

## 🔍 Causes Possibles

### 1. **OAuth Consent Screen en mode "Testing"**
Si votre OAuth Consent Screen est en mode "Testing", Google peut demander des codes de sécurité pour les utilisateurs non ajoutés comme "Test users".

### 2. **Paramètres de Sécurité Google**
Votre compte Google peut avoir des paramètres de sécurité plus stricts qui nécessitent un code au lieu de la confirmation push.

### 3. **Changement de Configuration OAuth**
Un changement dans les scopes ou la configuration peut déclencher une authentification plus forte.

---

## ✅ Solution 1 : Vérifier OAuth Consent Screen

### Étape 1 : Aller dans Google Cloud Console

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Sélectionnez votre projet
3. Allez dans **APIs & Services** > **OAuth consent screen**

### Étape 2 : Vérifier le Statut

**Si le statut est "Testing" :**

1. **Option A : Ajouter votre email comme Test User**
   - Dans la section **Test users**, cliquez sur **"Add users"**
   - Ajoutez votre email : `laetitiaimboden132@gmail.com`
   - Cliquez sur **"Add"**
   - Attendez 5 minutes pour la propagation

2. **Option B : Passer en Production** (Recommandé pour un site public)
   - Cliquez sur **"PUBLISH APP"** en haut de la page
   - Remplissez les informations requises :
     - **App name** : MapEvent
     - **User support email** : Votre email
     - **Developer contact information** : Votre email
   - Acceptez les conditions
   - Cliquez sur **"PUBLISH"**
   - ⚠️ **ATTENTION** : Cela peut prendre jusqu'à 7 jours pour être approuvé par Google

---

## ✅ Solution 2 : Vérifier les Paramètres de Sécurité Google

### Étape 1 : Aller dans les Paramètres Google

1. Allez sur [Mon compte Google](https://myaccount.google.com/)
2. Allez dans **Sécurité**

### Étape 2 : Vérifier l'Authentification à Deux Facteurs

1. Cherchez **"Validation en deux étapes"**
2. Vérifiez que c'est activé
3. Cliquez dessus

### Étape 3 : Vérifier les Méthodes de Vérification

Dans **Méthodes de vérification**, vous devriez avoir :
- ✅ **Notifications Google** (confirmation push sur smartphone)
- ✅ **Messages texte** (SMS)
- ✅ **Appels téléphoniques**
- ✅ **Codes de sécurité**

**Si "Notifications Google" n'est pas activée :**
1. Cliquez sur **"Notifications Google"**
2. Suivez les instructions pour l'activer
3. Testez avec votre smartphone

---

## ✅ Solution 3 : Vérifier les Paramètres OAuth dans Cognito

### Étape 1 : Vérifier les Scopes

Dans AWS Cognito > **Federated identity providers** > **Google** :

Vérifiez que les **Scopes autorisés** sont :
```
openid email profile
```

**⚠️ IMPORTANT** : Ne pas ajouter de scopes supplémentaires qui pourraient déclencher une authentification plus forte.

### Étape 2 : Vérifier le Client ID et Secret

Assurez-vous que le **Client ID** et le **Secret** correspondent exactement à ceux dans Google Cloud Console.

---

## ✅ Solution 4 : Réinitialiser les Paramètres OAuth

Si rien ne fonctionne, essayez de réinitialiser :

### Dans Google Cloud Console :

1. **APIs & Services** > **Credentials**
2. Trouvez votre **OAuth 2.0 Client ID**
3. Cliquez sur **"Reset secret"** (si nécessaire)
4. **Copiez le nouveau secret**
5. **Mettez à jour dans Cognito** avec le nouveau secret

### Dans AWS Cognito :

1. **Federated identity providers** > **Google**
2. **Modifiez** le **Secret client**
3. **Collez le nouveau secret** depuis Google Cloud Console
4. **Sauvegardez**

---

## 🎯 Solution Recommandée (Rapide)

**Pour retrouver rapidement la confirmation push :**

1. **Ajoutez votre email comme Test User** dans OAuth Consent Screen (si en mode Testing)
2. **Vérifiez que "Notifications Google" est activée** dans vos paramètres de sécurité Google
3. **Attendez 5-10 minutes** pour la propagation
4. **Testez à nouveau**

---

## 📋 Checklist Complète

- [ ] OAuth Consent Screen : Statut vérifié (Testing ou Production)
- [ ] Test users : Votre email ajouté (si en mode Testing)
- [ ] Paramètres Google : "Notifications Google" activée
- [ ] Cognito : Scopes corrects (`openid email profile`)
- [ ] Cognito : Client ID et Secret à jour
- [ ] Attente : 5-10 minutes après modifications

---

## ⚠️ Note Importante

Si vous passez en **Production**, Google peut prendre jusqu'à **7 jours** pour approuver votre application. Pendant ce temps, seuls les **Test users** pourront se connecter.

Pour un site public, il est recommandé de :
1. **Rester en mode Testing** pour le développement
2. **Ajouter tous les emails de test** dans Test users
3. **Passer en Production** seulement quand le site est prêt
