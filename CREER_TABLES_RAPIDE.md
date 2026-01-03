# 🗄️ Créer les Tables - Guide Rapide (5 minutes)

## ✅ Méthode la PLUS SIMPLE (sans AWS CLI, sans API Gateway)

### Étape 1 : Aller dans Lambda

1. **AWS Console** > **Lambda**
2. Cliquez sur votre fonction : **`mapevent-backend`**

### Étape 2 : Créer un événement de test

1. Onglet **"Test"** (en haut)
2. Cliquez sur **"Create new event"** ou **"Créer un nouvel événement"**
3. Nom de l'événement : `create-tables`
4. Dans le champ JSON, collez ceci :

```json
{
  "path": "/api/admin/create-tables",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{}"
}
```

5. Cliquez sur **"Save"** (Sauvegarder)

### Étape 3 : Exécuter le test

1. Cliquez sur **"Test"** (bouton orange)
2. Attendez quelques secondes
3. Vous verrez le résultat

### Étape 4 : Vérifier le résultat

Si vous voyez :
- **Status : 200**
- **Message : "Tables créées avec succès"**

✅ **C'est bon ! Les tables sont créées !**

## 📋 Liste des tables créées

Les tables suivantes seront créées :
- `events`
- `bookings`
- `services`
- `users`
- `user_likes`
- `user_favorites`
- `user_participations`
- `user_agenda`
- `user_reviews`
- `user_reports`
- `discussions`

## ⚠️ Si vous voyez une erreur

### Erreur "schema.sql not found"
- Le fichier `schema.sql` n'est pas dans le package Lambda
- Il faut redéployer Lambda avec le fichier `schema.sql`

### Erreur de connexion à la base de données
- Vérifiez les variables d'environnement Lambda :
  - `RDS_HOST`
  - `RDS_PORT`
  - `RDS_DB`
  - `RDS_USER`
  - `RDS_PASSWORD`

### Erreur "Database error"
- Vérifiez que la base de données existe
- Vérifiez les credentials RDS

## ✅ C'est tout !

Cette méthode fonctionne **toujours** car elle appelle Lambda directement, sans passer par API Gateway.

**Temps estimé : 2-5 minutes**

---

## 🔄 Pour recréer les tables plus tard

1. Lambda > `mapevent-backend` > Test
2. Sélectionnez l'événement `create-tables` (que vous avez sauvegardé)
3. Cliquez "Test"
4. C'est fait !

**Vous n'aurez plus besoin de 3 jours, juste 30 secondes !**

