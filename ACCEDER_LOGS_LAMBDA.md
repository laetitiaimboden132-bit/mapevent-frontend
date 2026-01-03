# 📋 Accéder aux logs Lambda - Guide étape par étape

## 🗺️ Navigation complète

### Étape 1 : Aller dans CloudWatch

1. **AWS Console** (console.aws.amazon.com)
2. Dans la barre de recherche en haut, tapez : **"CloudWatch"**
3. Cliquez sur **"CloudWatch"**

### Étape 2 : Aller dans Logs

1. Dans le menu de gauche, cherchez **"Logs"**
2. Cliquez sur **"Logs"** (ou "Log groups")

### Étape 3 : Trouver le log group de Lambda

1. Vous verrez une liste de **"Log groups"**
2. Cherchez un nom qui contient :
   - `/aws/lambda/mapevent-backend`
   - Ou `/aws/lambda/mapevent-backend-xxx`
   - Ou juste le nom de votre fonction Lambda

3. **Cliquez sur ce log group**

### Étape 4 : Voir les log streams

1. Après avoir cliqué sur le log group, vous verrez une nouvelle page
2. En haut, il y a un onglet **"Log streams"** (ou "Flux de logs")
3. Vous verrez une liste de **log streams** (flux de logs)
4. Ce sont des fichiers de logs individuels

### Étape 5 : Ouvrir un log stream

1. Dans la liste des log streams, cliquez sur le **plus récent** (en haut de la liste)
2. Ou celui avec la date/heure la plus récente
3. Les logs s'afficheront

## 🔍 Si vous ne voyez pas de log streams

### Option 1 : Utiliser le filtre de recherche

1. En haut de la page, il y a un champ de recherche
2. Tapez le nom de votre fonction Lambda
3. Les log groups correspondants apparaîtront

### Option 2 : Aller directement depuis Lambda

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Monitoring"**
3. Cliquez sur **"View logs in CloudWatch"**
4. Cela vous amène directement aux logs !

## 💡 Méthode la plus simple

**Depuis Lambda directement :**

1. **Lambda** (dans AWS Console)
2. Cliquez sur votre fonction : **`mapevent-backend`**
3. Onglet **"Monitoring"** (en haut)
4. Cliquez sur **"View logs in CloudWatch"** (bouton bleu)
5. Vous êtes directement dans les logs !

C'est la méthode la plus rapide !

## 📍 Où vous êtes maintenant ?

Dites-moi où vous êtes :
- Dans CloudWatch mais pas de log groups ?
- Dans un log group mais pas de log streams ?
- Autre chose ?

Je vous guiderai depuis là !

