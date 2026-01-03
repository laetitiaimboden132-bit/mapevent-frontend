# 🆕 Créer un nouvel événement de test

## ❌ Problème
L'événement s'appelle "test - health" et contient `/api/health` au lieu de `/api/admin/create-tables`.

## ✅ Solution : Créer un nouvel événement

### Étape 1 : Créer un nouvel événement

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Test"**
3. En haut, à côté de "Test", vous verrez un menu déroulant ou un bouton
4. Cherchez **"Configure test events"** ou **"Configurer les événements de test"**
5. Cliquez dessus

### Étape 2 : Créer un nouvel événement

1. Vous verrez une liste d'événements (peut-être juste "test - health")
2. Cliquez sur **"Create new event"** ou **"Créer un nouvel événement"**
3. Ou cherchez un bouton **"+"** ou **"Add"**

### Étape 3 : Configurer le nouvel événement

1. **Event name** (Nom de l'événement) : `create-tables`
2. Dans le champ JSON, **effacez tout** et **collez exactement ceci** :

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

3. Cliquez sur **"Save"** (Sauvegarder)

### Étape 4 : Sélectionner le nouvel événement

1. Dans le menu déroulant en haut (à côté de "Test")
2. Sélectionnez **"create-tables"** (au lieu de "test - health")
3. Cliquez sur **"Test"**

### Étape 5 : Vérifier le résultat

Vous devriez voir :
```json
{
  "statusCode": 200,
  "body": "{\"status\":\"success\",\"message\":\"Tables créées avec succès\",\"tables\":[...]}"
}
```

## 🔄 Alternative : Modifier l'événement existant

Si vous ne trouvez pas comment créer un nouvel événement :

1. **Sélectionnez "test - health"** dans le menu déroulant
2. **Modifiez le JSON** :
   - Changez `"path": "/api/health"` en `"path": "/api/admin/create-tables"`
   - Changez `"httpMethod": "GET"` en `"httpMethod": "POST"`
   - Ajoutez `"body": "{}"`
3. **Sauvegardez**
4. **Testez**

## ✅ Action immédiate

1. **Créez un nouvel événement** appelé `create-tables`
2. **Ou modifiez "test - health"** pour changer le path
3. **Testez**

Dites-moi si vous arrivez à créer un nouvel événement ou si vous préférez modifier celui existant !

