# 🔒 Sécurité Stripe - Protection de vos Clés

## ⚠️ RISQUE : Envoyer des Clés par Mail

### ❌ NE JAMAIS Envoyer par Mail

**Les clés secrètes Stripe (`sk_live_...` ou `sk_test_...`) sont TRÈS SENSIBLES !**

Si quelqu'un pirate votre mail et récupère votre clé secrète :
- ✅ Il peut créer des paiements à votre place
- ✅ Il peut accéder à tous vos paiements
- ✅ Il peut voler vos données clients
- ✅ Il peut faire des remboursements frauduleux
- ❌ **C'est TRÈS DANGEREUX !**

## ✅ Solutions SÉCURISÉES

### Option 1 : AWS Systems Manager Parameter Store (RECOMMANDÉ)

**Le plus sécurisé** - Stockage chiffré dans AWS :

1. **Dans AWS Console** :
   - Allez dans **Systems Manager** → **Parameter Store**
   - Créez un paramètre :
     - Nom : `/mapevent/stripe/secret-key`
     - Type : **SecureString** (chiffré)
     - Valeur : `sk_live_VOTRE_CLE`

2. **Dans Lambda** :
   - Utilisez le SDK AWS pour récupérer la valeur
   - Pas besoin de variable d'environnement

**Avantages** :
- ✅ Chiffré automatiquement
- ✅ Accès contrôlé par IAM
- ✅ Historique des changements
- ✅ Pas dans le code

### Option 2 : Variables d'Environnement Lambda (Actuel)

**Déjà configuré** - Mais attention :

✅ **Bien** :
- Pas dans le code source
- Accessible seulement depuis Lambda

⚠️ **Risques** :
- Visible dans la console AWS (si quelqu'un a accès)
- Pas chiffré par défaut

**Recommandation** : Utiliser **Parameter Store** à la place

### Option 3 : Gestionnaire de Mots de Passe

Pour **sauvegarder** vos clés (pas pour les utiliser) :

- ✅ **1Password**
- ✅ **LastPass**
- ✅ **Bitwarden**
- ✅ **KeePass** (gratuit, local)

**Stockez** :
- Clé secrète : `sk_live_...`
- Clé publique : `pk_live_...`
- Identifiants Stripe Dashboard

### Option 4 : Notes Chiffrées

Pour **sauvegarder** localement :

- ✅ **Fichier texte chiffré** (avec 7-Zip ou WinRAR)
- ✅ **Document Word avec mot de passe**
- ✅ **Fichier dans un dossier chiffré**

## 🚫 À NE JAMAIS FAIRE

### ❌ Envoyer par Mail
- Risque de piratage
- Pas chiffré
- Traces permanentes

### ❌ Mettre dans Git
- Visible par tous si repo public
- Historique permanent
- Risque de fuite

### ❌ Partager sur Slack/Teams/Discord
- Pas sécurisé
- Traces permanentes
- Accès non contrôlé

### ❌ Stocker en clair dans un fichier
- Accessible si ordinateur compromis
- Pas de protection

## ✅ Bonnes Pratiques

### 1. Rotation des Clés

Si vous pensez qu'une clé est compromise :
1. **Stripe Dashboard** → **Developers** → **API keys**
2. **Révoquer** l'ancienne clé
3. **Créer** une nouvelle clé
4. **Mettre à jour** dans Lambda/Parameter Store

### 2. Accès Limité

- ✅ **IAM** : Donner accès seulement aux personnes nécessaires
- ✅ **Stripe Dashboard** : Activer 2FA (authentification à 2 facteurs)
- ✅ **Logs** : Surveiller les accès suspects

### 3. Clés de Test vs Production

- ✅ **Test** : Moins critique, mais quand même sensible
- ⚠️ **Production** : TRÈS CRITIQUE, protéger absolument

### 4. Sauvegarde Sécurisée

Pour **sauvegarder** (pas pour utiliser) :
- ✅ Gestionnaire de mots de passe
- ✅ Fichier chiffré local
- ✅ **PAS** dans le cloud non chiffré

## 📋 Checklist Sécurité

- [ ] Clés stockées dans AWS Parameter Store (ou Lambda variables)
- [ ] Clés **JAMAIS** dans le code source
- [ ] Clés **JAMAIS** dans Git
- [ ] Clés **JAMAIS** envoyées par mail
- [ ] Stripe Dashboard avec **2FA activé**
- [ ] Accès IAM limité aux personnes nécessaires
- [ ] Sauvegarde sécurisée dans gestionnaire de mots de passe
- [ ] Rotation des clés si compromission suspectée

## 🔐 Si Votre Mail est Piraté

### Actions Immédiates

1. **Changer le mot de passe** du mail
2. **Activer 2FA** sur le mail
3. **Vérifier Stripe Dashboard** :
   - Voir les dernières activités
   - Vérifier les paiements suspects
4. **Révoquer les clés Stripe** si nécessaire
5. **Créer de nouvelles clés**
6. **Mettre à jour** dans Lambda/Parameter Store

## 💡 Recommandation Finale

### Pour Utiliser (Production)
✅ **AWS Systems Manager Parameter Store** avec SecureString

### Pour Sauvegarder (Backup)
✅ **Gestionnaire de mots de passe** (1Password, LastPass, etc.)

### Pour Partager (Si nécessaire)
✅ **AWS Systems Manager** avec accès IAM contrôlé
❌ **JAMAIS par mail**

---

**En résumé : Ne JAMAIS envoyer les clés secrètes par mail. Utilisez AWS Parameter Store pour la production et un gestionnaire de mots de passe pour la sauvegarde ! 🔒**

