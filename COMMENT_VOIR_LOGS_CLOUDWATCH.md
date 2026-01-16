# 📊 Comment voir les logs CloudWatch pour Lambda

## 🎯 Accès aux logs depuis la console AWS

### Méthode 1 : Depuis Lambda (le plus simple)

1. **Connectez-vous à la console AWS** : https://console.aws.amazon.com/
2. **Allez dans Lambda** :
   - Dans la barre de recherche en haut, tapez "Lambda"
   - Cliquez sur "Lambda" dans les résultats
3. **Sélectionnez votre fonction** :
   - Dans la liste des fonctions, cliquez sur **`mapevent-backend`**
4. **Accédez aux logs** :
   - Cliquez sur l'onglet **"Monitoring"** (en haut)
   - Cliquez sur **"View logs in CloudWatch"** (bouton bleu)
   - OU cliquez directement sur **"CloudWatch Logs"** dans le menu de gauche

### Méthode 2 : Depuis CloudWatch directement

1. **Connectez-vous à la console AWS** : https://console.aws.amazon.com/
2. **Allez dans CloudWatch** :
   - Dans la barre de recherche en haut, tapez "CloudWatch"
   - Cliquez sur "CloudWatch" dans les résultats
3. **Accédez aux logs** :
   - Dans le menu de gauche, cliquez sur **"Logs"** → **"Log groups"**
   - Cherchez et cliquez sur **`/aws/lambda/mapevent-backend`**
   - Cliquez sur le **stream de logs le plus récent** (celui avec la date/heure la plus récente)

## 🔍 Ce que vous verrez dans les logs

Les logs affichent :
- ✅ Les connexions réussies à la base de données
- ❌ Les erreurs avec le message complet
- 📝 Les requêtes SQL exécutées
- 🔍 Les détails de chaque étape du processus

## 🎯 Ce qu'il faut chercher

Quand vous testez la création de compte, cherchez :
1. **"Tentative de connexion à RDS"** - Vérifie que la connexion DB fonctionne
2. **"❌ ERREUR complétion profil Google"** - Affiche l'erreur exacte
3. **"Traceback complet"** - Montre la ligne exacte qui cause l'erreur
4. **"Type d'erreur"** - Indique le type d'erreur Python

## 📋 Exemple de ce que vous devriez voir

```
✅ Connexion RDS réussie
Recherche utilisateur: email=laetitiaimboden132@gmail.com, sub=e2451474-9031-703b-a62a-0a6b12243617
✅ Synchronisation backend réussie
```

OU en cas d'erreur :
```
❌ ERREUR complétion profil Google: ...
Traceback complet:
  File "...", line XXXX, in oauth_google_complete
    ...
Type d'erreur: ...
```

## 🚨 Si vous ne voyez pas de logs récents

1. **Vérifiez la région** : Assurez-vous d'être dans la région **eu-west-1** (Europe - Irlande)
2. **Actualisez la page** : Cliquez sur le bouton "Actualiser" dans CloudWatch
3. **Vérifiez les filtres** : Assurez-vous qu'aucun filtre de date n'est appliqué

## 💡 Astuce

Pour voir les logs en temps réel pendant que vous testez :
1. Ouvrez CloudWatch dans un onglet
2. Testez la création de compte dans un autre onglet
3. Revenez à CloudWatch et actualisez pour voir les nouveaux logs









