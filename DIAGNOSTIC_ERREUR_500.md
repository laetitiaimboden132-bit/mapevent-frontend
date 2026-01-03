# 🔍 Diagnostic : Erreur 500 sur `/api/user/oauth/google/complete`

## ❌ Problème Détecté

```
POST https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google/complete
[HTTP/2 500  1188ms]
```

Une erreur **500 (Internal Server Error)** se produit lors de la soumission du formulaire d'inscription après connexion Google.

---

## 🔍 Causes Possibles

### 1. **Colonnes Manquantes dans la Base de Données** (Le Plus Probable)

Le script SQL `CREER_COLONNES_USERS.sql` n'a peut-être pas été exécuté, ou certaines colonnes manquent.

**Vérification** :
- Les colonnes `first_name`, `last_name`, `username`, `password_hash`, `postal_address`, etc. doivent exister
- La colonne `avatar_emoji` doit être de type `TEXT` (pas `VARCHAR(10)`)

### 2. **Erreur de Connexion à la Base de Données**

Lambda ne peut pas se connecter à RDS.

**Vérification** :
- Lambda doit être dans le même VPC que RDS
- Security Groups doivent autoriser Lambda à accéder à RDS

### 3. **Erreur dans le Code Backend**

Une exception Python non gérée dans `oauth_google_complete`.

---

## 🔧 Solutions

### Solution 1 : Vérifier les Logs CloudWatch

1. **Allez dans AWS Console** : https://console.aws.amazon.com/
2. **CloudWatch** → **Log groups**
3. **Trouvez** : `/aws/lambda/mapevent-api` (ou nom similaire)
4. **Cliquez** sur le log group
5. **Ouvrez** le dernier log stream (le plus récent)
6. **Cherchez** les erreurs Python (lignes rouges ou avec "ERROR")

### Solution 2 : Vérifier que les Colonnes Existent

**Si vous avez pgAdmin** :
1. Connectez-vous à RDS
2. Exécutez cette requête SQL :
```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY column_name;
```
3. Vérifiez que toutes ces colonnes existent :
   - `first_name`
   - `last_name`
   - `username`
   - `email`
   - `password_hash`
   - `postal_address`
   - `avatar_emoji` (doit être `TEXT`, pas `VARCHAR(10)`)
   - `oauth_google_id`
   - `role`
   - `subscription`
   - `created_at`
   - `updated_at`

**Si des colonnes manquent** :
- Exécutez `CREER_COLONNES_USERS.sql` dans pgAdmin

### Solution 3 : Vérifier la Connexion Lambda → RDS

1. **AWS Console** → **Lambda**
2. **Trouvez** votre fonction Lambda (ex: `mapevent-api`)
3. **Vérifiez** :
   - Configuration → VPC : Lambda doit être dans le même VPC que RDS
   - Security Groups : Lambda doit avoir accès à RDS

---

## 📋 Checklist de Diagnostic

- [ ] Vérifier les logs CloudWatch pour l'erreur exacte
- [ ] Vérifier que toutes les colonnes existent dans la table `users`
- [ ] Vérifier que `avatar_emoji` est de type `TEXT`
- [ ] Vérifier que Lambda peut se connecter à RDS
- [ ] Vérifier que les variables d'environnement Lambda sont correctes (`RDS_HOST`, `RDS_PASSWORD`, etc.)

---

## 🚀 Action Immédiate

**La première chose à faire** : Regarder les logs CloudWatch pour voir l'erreur exacte.

Ensuite, selon l'erreur :
- Si c'est une colonne manquante → Exécuter le script SQL
- Si c'est une erreur de connexion → Vérifier VPC/Security Groups
- Si c'est une autre erreur → Corriger le code backend

---

## 📝 Note sur les Autres Warnings

Les warnings **Content-Security-Policy** et **cookies Stripe** sont **normaux** et ne bloquent pas le fonctionnement. Ce sont des avertissements de sécurité du navigateur, pas des erreurs.

**L'erreur importante** est la **500** sur `/api/user/oauth/google/complete`.


