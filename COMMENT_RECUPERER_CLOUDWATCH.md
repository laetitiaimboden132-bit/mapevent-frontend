# 📊 COMMENT RÉCUPÉRER LES LOGS CLOUDWATCH

## 🔍 MÉTHODE 1 : CONSOLE AWS (RECOMMANDÉ)

### Étape 1 : Aller sur CloudWatch
1. Ouvrir : https://eu-west-1.console.aws.amazon.com/cloudwatch/
2. Se connecter avec vos identifiants AWS

### Étape 2 : Trouver les logs Lambda
1. Dans le menu de gauche, cliquer sur **"Logs"**
2. Cliquer sur **"Log groups"**
3. Chercher : `/aws/lambda/mapevent-backend`
4. Cliquer dessus

### Étape 3 : Voir les logs récents
1. Vous verrez une liste de "Log streams" (fichiers de logs)
2. Cliquer sur le plus récent (en haut de la liste)
3. Les logs s'affichent avec l'heure et le message

### Étape 4 : Filtrer les logs
Dans la barre de recherche en haut, taper :
- `[dict` pour trouver les erreurs de sérialisation
- `user` pour trouver les logs liés aux utilisateurs
- `oauth_google` pour trouver les logs de connexion Google

---

## 🔍 MÉTHODE 2 : AWS CLI (POUR MOI)

Si vous avez AWS CLI installé, je peux récupérer les logs avec :

```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

Mais pour l'instant, la méthode 1 (Console) est plus simple.

---

## 📋 CE QU'IL FAUT CHERCHER DANS LES LOGS

### Logs importants à copier :

1. **Erreurs de sérialisation :**
   ```
   ⚠️ ATTENTION: user est une chaîne '[dict - 17 items]'
   ```

2. **Logs de la fonction oauth_google :**
   ```
   🔍 Recherche utilisateur: email=...
   ✅ Utilisateur trouvé: ...
   ```

3. **Logs de sérialisation :**
   ```
   ✅ user_data_clean sérialisable (... caractères)
   ✅ Réponse complète sérialisée (... caractères)
   ```

4. **Erreurs Python :**
   ```
   ❌ Erreur: ...
   Traceback: ...
   ```

---

## 🎯 CE QUE JE DOIS VOIR

Copiez-moi les lignes qui contiennent :
- `[dict`
- `user est une chaîne`
- `oauth_google`
- `sérialisable`
- `Erreur` ou `❌`

Cela m'aidera à comprendre exactement où le problème se produit.

---

## ⚡ MÉTHODE RAPIDE

1. Aller sur : https://eu-west-1.console.aws.amazon.com/cloudwatch/
2. Logs → Log groups → `/aws/lambda/mapevent-backend`
3. Cliquer sur le log stream le plus récent
4. Dans la barre de recherche, taper : `[dict`
5. Copier les lignes qui apparaissent
6. Me les envoyer

---

**C'est tout ! 🚀**







