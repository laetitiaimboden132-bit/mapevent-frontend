# 🔧 Corriger l'événement de test

## ❌ Problème
Vous voyez `"status":"ok"` au lieu de `"Tables créées avec succès"`.

Cela signifie que Lambda a appelé la route `/api/health` au lieu de `/api/admin/create-tables`.

## ✅ Solution : Vérifier le path dans l'événement

### Étape 1 : Vérifier l'événement de test

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Test"**
3. Regardez l'événement que vous avez créé
4. Vérifiez le champ **"path"** dans le JSON

**Il doit être exactement :**
```json
"path": "/api/admin/create-tables"
```

**Pas :**
- `"/api/health"` ❌
- `"/api/admin/create-tables/"` ❌ (pas de slash à la fin)
- `"api/admin/create-tables"` ❌ (pas de slash au début)

### Étape 2 : Corriger l'événement

1. Dans l'éditeur JSON de l'événement
2. **Effacez tout**
3. **Collez exactement ceci :**

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

4. **Cliquez sur "Save"** (Sauvegarder)

### Étape 3 : Retester

1. Cliquez sur **"Test"** (bouton orange)
2. Attendez 5 secondes
3. Regardez le résultat

### Étape 4 : Vérifier le résultat

**Si ça fonctionne, vous verrez :**
```json
{
  "statusCode": 200,
  "body": "{\"status\":\"success\",\"message\":\"Tables créées avec succès\",\"tables\":[...]}"
}
```

**Avec dans le body :**
- `"status":"success"`
- `"message":"Tables créées avec succès"`
- `"tables":["events","bookings","services",...]`

## ⚠️ Points importants

1. **Le path doit être EXACTEMENT** : `/api/admin/create-tables`
2. **Pas d'espace** avant ou après
3. **Pas de slash à la fin**
4. **httpMethod doit être** : `POST` (en majuscules)

## ✅ Action immédiate

1. **Vérifiez l'événement de test**
2. **Corrigez le path** si nécessaire
3. **Sauvegardez**
4. **Retestez**
5. **Dites-moi ce que vous voyez**

