# 🔍 VÉRIFICATION DES LOGS CLOUDWATCH

## ⏰ FUSEAU HORAIRE

**IMPORTANT :** CloudWatch utilise l'heure UTC (Coordinated Universal Time).

- **Votre heure locale :** 01h50
- **Heure UTC :** Probablement 00h50 (si vous êtes en UTC+1) ou 23h50 (si vous êtes en UTC+2)

**Les logs à 00h50 UTC correspondent donc à votre heure locale 01h50 ou 02h50.**

---

## 🔄 FORCER UNE NOUVELLE REQUÊTE

Pour générer de nouveaux logs, il faut faire une nouvelle requête au backend :

### Méthode 1 : Se connecter avec Google
1. Aller sur : https://mapevent.world
2. Cliquer sur "Compte"
3. Cliquer sur "Connexion avec Google"
4. Autoriser la connexion
5. **Cela générera de nouveaux logs dans CloudWatch**

### Méthode 2 : Rafraîchir la page après connexion
1. Si vous êtes déjà connecté, vous déconnecter
2. Vous reconnecter avec Google
3. **Cela générera de nouveaux logs**

---

## 📊 VÉRIFIER LES NOUVEAUX LOGS

1. Aller sur : https://eu-west-1.console.aws.amazon.com/cloudwatch/
2. Logs → Log groups → `/aws/lambda/mapevent-backend`
3. **Actualiser la page** (F5)
4. Chercher le log stream le plus récent
5. Vérifier l'heure UTC (les logs sont en UTC)

---

## 🎯 CE QU'IL FAUT CHERCHER

Dans les nouveaux logs, chercher :

### ✅ Logs positifs (si ça fonctionne) :
```
✅ JSON récupéré directement depuis response.get_json()
✅ user est un dict valide (keys: ...)
✅ Body JSON construit depuis response.get_json() (... caractères)
```

### ❌ Logs négatifs (si le problème persiste) :
```
⚠️ user est une chaîne '[dict - X items]'
⚠️ DÉTECTION: Body contient '[dict - X items]'
⚠️ ATTENTION: user est une chaîne '[dict - X items]' au lieu d'un objet JSON
```

---

## 🔍 SI LES LOGS NE SONT PAS À JOUR

1. **Vérifier que le déploiement a bien été effectué** :
   - Le dernier déploiement était à 00:54 UTC
   - Si vous êtes en UTC+1, c'était à 01:54 heure locale
   - Si vous êtes en UTC+2, c'était à 02:54 heure locale

2. **Attendre quelques secondes** :
   - CloudWatch peut avoir un délai de quelques secondes
   - Actualiser la page (F5)

3. **Vérifier le bon log group** :
   - `/aws/lambda/mapevent-backend`
   - Pas `/aws/lambda/mapevent-backend-old` ou autre

---

## 📝 RÉSUMÉ

1. **Faire une nouvelle connexion Google** pour générer de nouveaux logs
2. **Attendre 10-20 secondes** pour que les logs apparaissent
3. **Actualiser CloudWatch** (F5)
4. **Chercher les logs récents** (les plus récents en haut)
5. **Copier les lignes avec `[dict` ou `user`** et me les envoyer

---

**Les logs sont en UTC, pas en heure locale !**







